"""Offline invariant checks for the deterministic planning path."""

import json
import re
from pathlib import Path

from app.domain.planning.constraints import ConstraintEngine
from app.domain.planning.fallback import FallbackPlanner
from app.domain.planning.scorer import PlanScorer
from app.domain.planning.validator import PlanValidator
from app.models.schemas import PlanRequest

SCENARIOS = Path(__file__).parent / "scenarios" / "planning_invariants.json"


def contains_term(text: str, term: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", text) is not None


def evaluate(scenario: dict) -> dict:
    request = PlanRequest.model_validate(scenario["request"])
    engine = ConstraintEngine()
    constraints = engine.compile(request)
    preferences = engine.compile_preferences(request)
    candidate = FallbackPlanner().build("offline_eval", [], constraints)
    plan = PlanValidator().validate(candidate, constraints)
    serialized = json.dumps(plan, sort_keys=True).casefold()
    violations = [
        term
        for term in scenario["expected"].get("forbiddenTerms", [])
        if contains_term(serialized, term)
    ]
    expected_spice = scenario["expected"].get("spiceLevel")
    if expected_spice and preferences.spiceLevel != expected_spice:
        raise AssertionError(
            f"expected spice level {expected_spice!r}, got {preferences.spiceLevel!r}"
        )
    if violations:
        raise AssertionError(f"forbidden terms present: {', '.join(violations)}")
    score = PlanScorer().score(plan, preferences, request.pantryInventory)
    return {"scenario": scenario["name"], "days": len(plan), "score": score.total}


def main() -> None:
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    failures: list[str] = []
    for scenario in scenarios:
        try:
            result = evaluate(scenario)
            print(f"PASS {result['scenario']}: {result['days']} days, score={result['score']}")
        except (AssertionError, ValueError) as exc:
            failures.append(f"{scenario['name']}: {exc}")
            print(f"FAIL {scenario['name']}: {exc}")
    if failures:
        raise SystemExit(f"{len(failures)} evaluation scenario(s) failed")
    print(f"All {len(scenarios)} offline planning scenarios passed")


if __name__ == "__main__":
    main()
