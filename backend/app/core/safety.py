import re
from dataclasses import dataclass

WELLNESS_DISCLAIMER = (
    "Annapurna-AI provides general wellness meal-planning ideas only. It does not "
    "provide medical advice, diagnosis, treatment, or personalized clinical nutrition."
)

NUTRITION_ESTIMATE_DISCLAIMER = (
    "Nutrition values are approximate estimates for planning and should be verified "
    "against labels, recipes, or a qualified professional when precision matters."
)

CLINICIAN_GUIDANCE = (
    "For medical conditions, pregnancy, pediatric diets, eating disorders, severe "
    "allergies, medication interactions, or aggressive weight-loss goals, consult a "
    "qualified clinician or registered dietitian."
)


@dataclass(frozen=True)
class SafetyConcern:
    code: str
    label: str
    guidance: str


SAFETY_PATTERNS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "diabetes",
        "Diabetes or blood glucose concern",
        ("diabetes", "diabetic", "blood sugar", "glucose", "insulin", "a1c"),
    ),
    (
        "pregnancy",
        "Pregnancy or lactation",
        ("pregnancy", "pregnant", "lactation", "breastfeeding", "postpartum"),
    ),
    (
        "kidney_disease",
        "Kidney disease",
        ("kidney disease", "renal", "ckd", "dialysis", "creatinine"),
    ),
    (
        "eating_disorder",
        "Eating disorder or extreme restriction",
        (
            "eating disorder",
            "anorexia",
            "bulimia",
            "binge eating",
            "starve",
            "800 calories",
            "under 1000 calories",
            "extreme weight loss",
            "lose weight fast",
            "crash diet",
        ),
    ),
    (
        "severe_allergy",
        "Severe allergy",
        ("allergy", "allergic", "anaphylaxis", "severe allergy", "life-threatening allergy", "epipen"),
    ),
    (
        "epilepsy_medication",
        "Epilepsy medication interaction",
        ("epilepsy", "seizure medication", "anti-seizure", "antiepileptic"),
    ),
    (
        "pediatric_diet",
        "Pediatric diet",
        ("child diet", "kid diet", "toddler", "infant", "baby food", "pediatric"),
    ),
)

COMMON_ALLERGENS: tuple[str, ...] = (
    "peanut",
    "peanuts",
    "tree nut",
    "almond",
    "cashew",
    "walnut",
    "milk",
    "dairy",
    "curd",
    "yogurt",
    "ghee",
    "egg",
    "eggs",
    "soy",
    "wheat",
    "gluten",
    "sesame",
    "shellfish",
    "fish",
)


def detect_safety_concerns(*texts: str | None) -> list[SafetyConcern]:
    combined = " ".join(text or "" for text in texts).lower()
    concerns: list[SafetyConcern] = []

    for code, label, keywords in SAFETY_PATTERNS:
        if any(keyword in combined for keyword in keywords):
            concerns.append(
                SafetyConcern(
                    code=code,
                    label=label,
                    guidance=(
                        f"{label}: keep guidance general and review choices with a qualified clinician "
                        "or registered dietitian."
                    ),
                )
            )

    return concerns


def build_safety_notes(concerns: list[SafetyConcern]) -> list[str]:
    if not concerns:
        return [WELLNESS_DISCLAIMER, NUTRITION_ESTIMATE_DISCLAIMER]
    notes = [WELLNESS_DISCLAIMER, CLINICIAN_GUIDANCE, NUTRITION_ESTIMATE_DISCLAIMER]
    notes.extend(concern.guidance for concern in concerns)
    return notes


def extract_allergens(*texts: str | None, explicit_allergies: list[str] | None = None) -> list[str]:
    found: set[str] = set()
    combined = " ".join(text or "" for text in texts).lower()

    for allergen in COMMON_ALLERGENS:
        if allergen in combined:
            found.add(_canonical_allergen(allergen))

    for allergy in explicit_allergies or []:
        cleaned = re.sub(r"[^a-zA-Z0-9\s-]", " ", allergy).strip().lower()
        if cleaned:
            found.add(_canonical_allergen(cleaned))

    return sorted(found)


def contains_allergen(text: str, allergens: list[str]) -> bool:
    haystack = text.lower()
    return any(allergen in haystack for allergen in allergens)


def _canonical_allergen(value: str) -> str:
    if value in {"peanuts"}:
        return "peanut"
    if value in {"curd", "yogurt", "ghee", "milk"}:
        return "dairy"
    if value in {"eggs"}:
        return "egg"
    return value
