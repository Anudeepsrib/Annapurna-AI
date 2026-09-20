import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    GroceryCompilationError,
    IdempotencyConflictError,
    PlanConflictError,
    PlanGenerationError,
)
from app.core.safety import WELLNESS_DISCLAIMER, build_safety_notes, detect_safety_concerns
from app.domain.grocery import GROCERY_COMPILER_VERSION, GroceryCompiler
from app.domain.pantry import PantryService
from app.domain.planning.constraints import ConstraintEngine
from app.domain.planning.fallback import FALLBACK_PLANNER_VERSION, FallbackPlanner
from app.domain.planning.models import CompiledConstraints, PlanningPreferences
from app.domain.planning.planner import CandidatePlanner
from app.domain.planning.scorer import PlanScorer
from app.domain.planning.validator import VALIDATOR_VERSION, PlanValidator
from app.models.schemas import GenerationMetadata, ManualShoppingItem, PantryItem, PlanRequest
from app.prompts.planner_v1 import PROMPT_VERSION
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.plan_repository import PlanRepository
from app.services.llm_service import llm_service

logger = structlog.get_logger()
PLANNER_VERSION = "candidate_planner_v2"


class PlanService:
    def __init__(self, session: AsyncSession):
        self.repository = PlanRepository(session)
        self.feedback_repository = FeedbackRepository(session)
        self.pantry_service = PantryService(session)
        self.constraint_engine = ConstraintEngine()
        self.plan_validator = PlanValidator()
        self.plan_scorer = PlanScorer()
        self.candidate_planner = CandidatePlanner(llm_service)
        self.fallback_planner = FallbackPlanner()
        self.grocery_compiler = GroceryCompiler()

    async def generate_plan(
        self,
        request: PlanRequest,
        user_id: str,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        request_hash = self._request_hash(request)
        if idempotency_key is not None:
            idempotency_key = idempotency_key.strip()
            if not idempotency_key or len(idempotency_key) > 128:
                raise PlanGenerationError("Idempotency-Key must contain between 1 and 128 characters")
            prior = await self.repository.get_generation_request(user_id, idempotency_key)
            if prior:
                if prior.request_hash != request_hash:
                    raise IdempotencyConflictError(
                        "Idempotency-Key was already used with a different plan request"
                    )
                return json.loads(prior.response_json)

        request = await self.pantry_service.prepare_plan_request(user_id, request)
        previous = await self.repository.get_latest(user_id)
        previous_payload = previous.plan_data if previous else {}
        constraints = self.constraint_engine.compile(request)
        preferences = self.constraint_engine.compile_preferences(request)
        feedback_weights = await self.feedback_repository.preference_weights(user_id)
        safety_concerns = detect_safety_concerns(request.dietary, " ".join(request.allergies))
        safety_notes = build_safety_notes(safety_concerns)

        if safety_concerns:
            source_status = "safety_guardrail"
            logger.info("Using safety guardrail plan", concerns=[concern.code for concern in safety_concerns])
            plan = self._fallback_plan(source_status, safety_notes, constraints)
        else:
            plan, source_status = await self._select_plan(
                request,
                preferences,
                constraints,
                user_id,
                safety_notes,
                feedback_weights,
            )

        plan = self._restore_locked_meals(plan, previous_payload, constraints)
        plan = self._apply_household_overrides(plan, previous_payload)
        grocery = self._compile_grocery(
            plan,
            request.pantryInventory,
            request.manualShoppingItems,
            previous_payload,
        )
        metadata = self._generation_metadata(source_status)
        await self._save_plan(
            user_id,
            plan,
            request,
            grocery,
            metadata,
            constraints,
            preferences,
            previous_payload,
        )
        result = {
            "plan": plan,
            "source_status": source_status,
            "disclaimer": WELLNESS_DISCLAIMER,
            "safety_notes": safety_notes,
            "grocery_optimization": grocery,
            "generation_metadata": metadata.model_dump(mode="json"),
        }
        if idempotency_key is not None:
            await self.repository.save_generation_request(
                user_id,
                idempotency_key,
                request_hash,
                result,
            )
        return result

    async def _select_plan(
        self,
        request: PlanRequest,
        preferences: PlanningPreferences,
        constraints: CompiledConstraints,
        user_id: str,
        safety_notes: list[str],
        feedback_weights: dict[str, float],
    ) -> tuple[list[dict[str, Any]], str]:
        try:
            candidates = await self.candidate_planner.generate_candidates(request, preferences, user_id)
        except ValueError as exc:
            logger.warning("LLM candidate parsing failed; using deterministic fallback", error=str(exc))
            candidates = []

        if candidates is None:
            source_status = (
                "fallback_llm_timeout"
                if self.candidate_planner.last_error_code == "LLM_TIMEOUT"
                else "fallback_llm_unavailable"
            )
            logger.warning("LLM unavailable; using deterministic fallback")
            return self._fallback_plan(source_status, safety_notes, constraints), source_status

        valid_candidates = []
        for candidate in candidates:
            try:
                valid_candidates.append(self.plan_validator.validate(candidate, constraints))
            except ValueError as exc:
                logger.warning("Discarding invalid plan candidate", error=str(exc))

        if not valid_candidates:
            source_status = "fallback_invalid_llm_json"
            return self._fallback_plan(source_status, safety_notes, constraints), source_status

        selected = self.plan_scorer.select_best(
            valid_candidates,
            preferences,
            request.pantryInventory,
            feedback_weights,
        )
        return selected, "llm_schema_validated"

    def _fallback_plan(
        self,
        source_status: str,
        safety_notes: list[str],
        constraints: CompiledConstraints,
    ) -> list[dict[str, Any]]:
        candidate = self.fallback_planner.build(source_status, safety_notes, constraints)
        return self.plan_validator.validate(candidate, constraints)

    async def get_latest_plan(self, user_id: str) -> list[dict[str, Any]] | None:
        saved = await self.repository.get_latest(user_id)
        if saved:
            plan, _context = self._unpack_saved_payload(saved.plan_data)
            return plan
        return None

    async def generate_grocery_list(self, user_id: str) -> list[dict[str, Any]]:
        payload = await self._get_latest_payload(user_id)
        if payload is None:
            return []
        plan, context = self._unpack_saved_payload(payload)
        if not plan:
            return []

        pantry = await self.pantry_service.current_legacy_items(user_id)
        if not pantry:
            pantry = [
                PantryItem.model_validate(item)
                for item in context.get("pantry_inventory", [])
                if isinstance(item, dict)
            ]
        manual_items = [
            ManualShoppingItem.model_validate(item)
            for item in context.get("manual_shopping_items", [])
            if isinstance(item, dict)
        ]
        return self._compile_grocery(plan, pantry, manual_items, context)

    async def _get_latest_payload(self, user_id: str) -> Any | None:
        saved = await self.repository.get_latest(user_id)
        return saved.plan_data if saved else None

    async def _save_plan(
        self,
        user_id: str,
        plan: list[dict[str, Any]],
        request: PlanRequest,
        grocery: list[dict[str, Any]],
        metadata: GenerationMetadata,
        constraints: CompiledConstraints,
        preferences: PlanningPreferences,
        previous_payload: Any,
    ) -> None:
        payload = {
            "schema_version": 5,
            "plan": plan,
            "privacy_model": self._privacy_model_for(request),
            "pantry_inventory": [item.model_dump(mode="json") for item in request.pantryInventory],
            "telugu_andhra_constraints": request.teluguAndhraConstraints,
            "compiled_constraints": constraints.model_dump(mode="json"),
            "planning_preferences": preferences.model_dump(mode="json"),
            "household_size": request.householdSize,
            "manual_shopping_items": [item.model_dump(mode="json") for item in request.manualShoppingItems],
            "shopping_exclusions": self._context_list(previous_payload, "shopping_exclusions"),
            "use_soon_requests": self._context_list(previous_payload, "use_soon_requests"),
            "household_overrides": (
                previous_payload.get("household_overrides", {}) if isinstance(previous_payload, dict) else {}
            ),
            "pipeline_versions": {
                "fallback": FALLBACK_PLANNER_VERSION,
                "grocery_compiler": GROCERY_COMPILER_VERSION,
            },
            "grocery_optimization": grocery,
        }
        saved = await self.repository.save(user_id, payload, metadata)
        logger.info("Plan saved to DB", id=saved.id)

    def _generation_metadata(self, source_status: str) -> GenerationMetadata:
        error_code = {
            "fallback_llm_timeout": "LLM_TIMEOUT",
            "fallback_llm_unavailable": "LLM_UNAVAILABLE",
            "fallback_invalid_llm_json": "LLM_INVALID_RESPONSE",
        }.get(source_status)
        return GenerationMetadata(
            generation_id=str(uuid4()),
            generated_at=datetime.now(UTC),
            provider=settings.LLM_PROVIDER,
            model=settings.LLM_MODEL,
            prompt_version=PROMPT_VERSION,
            planner_version=PLANNER_VERSION,
            validator_version=VALIDATOR_VERSION,
            source_status=source_status,
            fallback_used=source_status != "llm_schema_validated",
            error_code=error_code,
        )

    def _unpack_saved_payload(self, payload: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if isinstance(payload, list):
            return payload, {}
        if isinstance(payload, dict):
            plan = payload.get("plan", [])
            if isinstance(plan, list):
                return plan, {
                    "privacy_model": payload.get("privacy_model", {}),
                    "pantry_inventory": payload.get("pantry_inventory", []),
                    "telugu_andhra_constraints": payload.get("telugu_andhra_constraints", []),
                    "compiled_constraints": payload.get("compiled_constraints", {}),
                    "planning_preferences": payload.get("planning_preferences", {}),
                    "grocery_optimization": payload.get("grocery_optimization", []),
                    "manual_shopping_items": payload.get("manual_shopping_items", []),
                    "shopping_exclusions": payload.get("shopping_exclusions", []),
                    "use_soon_requests": payload.get("use_soon_requests", []),
                }
        return [], {}

    def _privacy_model_for(self, request: PlanRequest) -> dict[str, Any]:
        return {
            "mode": "local_first_family_profile",
            "data_minimization": [
                "Use role labels instead of real names.",
                "Store age groups and appetite bands instead of exact ages or weights.",
                "Keep profile, pantry, and generated plan data in local SQLite by default.",
            ],
            "family_profiles": [profile.model_dump() for profile in request.familyProfiles],
            "cloud_boundary": (
                "Profile and pantry details should be sent to a cloud model only after the "
                "operator intentionally enables non-local model access."
            ),
        }

    def _request_hash(self, request: PlanRequest) -> str:
        serialized = json.dumps(
            request.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _restore_locked_meals(
        self,
        plan: list[dict[str, Any]],
        previous_payload: Any,
        constraints: CompiledConstraints,
    ) -> list[dict[str, Any]]:
        if not isinstance(previous_payload, dict):
            return plan
        previous_plan = previous_payload.get("plan", [])
        locked = {
            (day.get("day"), meal_type): meal
            for day in previous_plan
            for meal_type, meal in day.get("meals", {}).items()
            if isinstance(meal, dict) and meal.get("locked")
        }
        if not locked:
            return plan
        merged = deepcopy(plan)
        for day in merged:
            for meal_type in day.get("meals", {}):
                existing = locked.get((day.get("day"), meal_type))
                if existing:
                    day["meals"][meal_type] = deepcopy(existing)
        try:
            return self.plan_validator.validate(merged, constraints)
        except ValueError as exc:
            raise PlanConflictError(
                "A locked meal conflicts with the updated hard constraints; unlock it before regenerating"
            ) from exc

    def _compile_grocery(
        self,
        plan: list[dict[str, Any]],
        pantry: list[PantryItem],
        manual_items: list[ManualShoppingItem],
        context: Any,
    ) -> list[dict[str, Any]]:
        payload = context if isinstance(context, dict) else {}
        try:
            return self.grocery_compiler.compile(
                plan,
                pantry,
                manual_items,
                self._context_list(payload, "shopping_exclusions"),
                self._context_list(payload, "use_soon_requests"),
            )
        except (TypeError, ValueError) as exc:
            raise GroceryCompilationError("Could not reconcile plan ingredients with pantry stock") from exc

    def _apply_household_overrides(
        self,
        plan: list[dict[str, Any]],
        previous_payload: Any,
    ) -> list[dict[str, Any]]:
        overrides = previous_payload.get("household_overrides", {}) if isinstance(previous_payload, dict) else {}
        for day in plan:
            override = overrides.get(day.get("day"), {})
            if isinstance(override, dict) and override.get("guestCount"):
                day["guestCount"] = override["guestCount"]
        return plan

    def _context_list(self, payload: Any, key: str) -> list[str]:
        values = payload.get(key, []) if isinstance(payload, dict) else []
        return [str(value) for value in values if str(value).strip()]
