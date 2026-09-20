import json
import re
from typing import Any

from app.domain.planning.models import PlanningPreferences
from app.models.schemas import PlanRequest
from app.prompts.planner_v1 import build_planner_prompts
from app.services.llm_service import LLMService


class CandidatePlanner:
    def __init__(self, llm: LLMService):
        self.llm = llm

    async def generate_candidates(
        self,
        request: PlanRequest,
        preferences: PlanningPreferences,
        user_id: str,
    ) -> list[Any] | None:
        system_prompt, user_prompt = build_planner_prompts(request, preferences)
        response = await self.llm.generate_response(
            system_prompt,
            user_prompt,
            json_mode=True,
            user_id=user_id,
        )
        if response is None:
            return None
        return self._extract_candidates(response)

    def _extract_candidates(self, response: str) -> list[Any]:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response was not valid JSON") from exc

        if isinstance(payload, dict) and "candidates" in payload:
            raw_candidates = payload["candidates"]
            if not isinstance(raw_candidates, list) or not raw_candidates:
                raise ValueError("LLM response candidates must be a non-empty list")
            return [candidate.get("plan") if isinstance(candidate, dict) else candidate for candidate in raw_candidates]
        if isinstance(payload, dict) and "plan" in payload:
            return [payload["plan"]]
        if isinstance(payload, list):
            return [payload]
        raise ValueError("LLM response did not contain a plan candidate")
