from typing import Literal

from pydantic import BaseModel, Field, field_validator

# --- C. Curated Evidence Models ---


class EvidenceCitation(BaseModel):
    source: str = Field(..., description="Name of the source (e.g., 'ICMR-NIN Dietary Guidelines')")
    year: int = Field(..., description="Year of publication")
    identifier: str = Field(..., description="Section, page number, or specific ID")


class EvidenceClaim(BaseModel):
    id: str
    topic: str = Field(..., description="General topic (e.g., 'iron', 'pregnancy', 'protein')")
    claim: str = Field(..., description="The specific verified claim")
    evidence_type: Literal["guideline", "systematic-review", "meta-analysis", "research-abstract"]
    population: str = Field(..., description="Target population (e.g., 'Adult Indians', 'Children 1-3y')")
    limitations: str = Field(..., description="Any constraints or confidence limits")
    citation: EvidenceCitation

# --- MCP Tool Models ---


class NutrientProfile(BaseModel):
    energy_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    micronutrients: dict[str, float] = Field(default_factory=dict, description="Key-value pairs of micronutrients")


class FoodItem(BaseModel):
    id: str
    name: str
    source: Literal["IFCT", "USDA"]
    nutrients: NutrientProfile

# --- Plan Models ---


TeluguAndhraConstraint = Literal[
    "vegetarian",
    "no_egg",
    "andhra_telugu_style",
    "rice_based_lunch",
    "pappu_or_dal_daily",
    "fermented_breakfasts_ok",
    "mild_for_children",
    "festival_no_onion_garlic",
]


class FamilyProfile(BaseModel):
    label: str = Field(
        default="Family member",
        max_length=60,
        description="Privacy-preserving role label. Avoid full legal names.",
    )
    ageGroup: Literal["adult", "senior", "teen", "child"] = "adult"
    appetite: Literal["light", "regular", "hearty"] = "regular"
    dietaryTags: list[str] = Field(default_factory=list, max_length=12)
    privacyScope: Literal["local_device_only", "meal_planning_only"] = "local_device_only"

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str) -> str:
        cleaned = " ".join(value.split())[:60]
        if not cleaned:
            return "Family member"
        return cleaned

    @field_validator("dietaryTags")
    @classmethod
    def validate_dietary_tags(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in value:
            tag = " ".join(item.split())[:80]
            key = tag.casefold()
            if tag and key not in seen:
                cleaned.append(tag)
                seen.add(key)
        return cleaned


class PantryItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    quantity: str = Field(default="", max_length=40)
    category: Literal["grains", "dals", "vegetables", "spices", "dairy", "other"] = "other"
    expiresWithinDays: int | None = Field(default=None, ge=0, le=365)

    @field_validator("name", "quantity")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return " ".join(value.split())


class PlanRequest(BaseModel):
    householdSize: str = Field(default="2", max_length=16)
    spiceLevel: str = Field(default="medium", max_length=32)
    dietary: str = Field(default="vegetarian", max_length=1000)
    allergies: list[str] = Field(default_factory=list, max_length=20)
    familyProfiles: list[FamilyProfile] = Field(default_factory=list, max_length=12)
    pantryInventory: list[PantryItem] = Field(default_factory=list, max_length=80)
    teluguAndhraConstraints: list[TeluguAndhraConstraint] = Field(
        default_factory=lambda: [
            "vegetarian",
            "andhra_telugu_style",
            "rice_based_lunch",
            "pappu_or_dal_daily",
        ],
        max_length=12,
    )

    @field_validator("householdSize")
    @classmethod
    def validate_household_size(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned.endswith("+"):
            cleaned = cleaned[:-1]
        if not cleaned.isdigit():
            raise ValueError("householdSize must be a positive number")
        size = int(cleaned)
        if size < 1 or size > 12:
            raise ValueError("householdSize must be between 1 and 12")
        return str(size)

    @field_validator("spiceLevel")
    @classmethod
    def validate_spice_level(cls, value: str) -> str:
        cleaned = value.strip().lower()
        allowed = {"mild", "medium", "spicy"}
        if cleaned not in allowed:
            raise ValueError("spiceLevel must be mild, medium, or spicy")
        return cleaned

    @field_validator("dietary")
    @classmethod
    def validate_dietary_text(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("dietary preferences cannot be empty")
        return cleaned

    @field_validator("allergies")
    @classmethod
    def validate_allergies(cls, value: list[str]) -> list[str]:
        return [" ".join(item.split())[:80] for item in value if item and item.strip()]

    @field_validator("teluguAndhraConstraints")
    @classmethod
    def validate_telugu_andhra_constraints(
        cls,
        value: list[TeluguAndhraConstraint],
    ) -> list[TeluguAndhraConstraint]:
        if not value:
            return ["vegetarian", "andhra_telugu_style"]
        cleaned: list[TeluguAndhraConstraint] = []
        for item in value:
            if item not in cleaned:
                cleaned.append(item)
        if "andhra_telugu_style" not in cleaned:
            cleaned.append("andhra_telugu_style")
        return cleaned


class NutritionEstimate(BaseModel):
    calories_kcal: float | None = Field(default=None, ge=0, le=2000)
    protein_g: float | None = Field(default=None, ge=0, le=200)
    carbs_g: float | None = Field(default=None, ge=0, le=300)
    fat_g: float | None = Field(default=None, ge=0, le=200)
    fiber_g: float | None = Field(default=None, ge=0, le=100)


class PlanMeal(BaseModel):
    title: str = Field(..., min_length=1, max_length=140, description="Meal name")
    description: str = Field(..., min_length=1, max_length=700)
    ingredients: list[str] = Field(..., min_length=1, max_length=30)
    time: str = Field(default="8:00 AM", max_length=32)
    nutrition: NutritionEstimate = Field(default_factory=NutritionEstimate)
    confidence: Literal["low", "medium", "high"] = "low"
    source_status: str = Field(default="llm_unverified", max_length=80)
    disclaimer: str = (
        "Nutrition estimates are approximate and for general wellness planning only."
    )

    @field_validator("ingredients")
    @classmethod
    def clean_ingredients(cls, value: list[str]) -> list[str]:
        cleaned = [" ".join(item.split())[:120] for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("at least one ingredient is required")
        return cleaned


class DayMeals(BaseModel):
    breakfast: PlanMeal
    lunch: PlanMeal
    dinner: PlanMeal


class DayPlan(BaseModel):
    day: str = Field(..., min_length=1, max_length=16)
    date: str = Field(..., min_length=1, max_length=32)
    meals: DayMeals
    confidence: Literal["low", "medium", "high"] = "low"
    source_status: str = Field(default="llm_unverified", max_length=80)
    disclaimer: str = (
        "General wellness only. Nutrition estimates are approximate and not medical advice."
    )
    safety_notes: list[str] = Field(default_factory=list)

# --- API Response Models ---


class EvidenceResponse(BaseModel):
    topic: str
    claims: list[EvidenceClaim] = Field(default_factory=list)
    disclaimer: str = (
        "This information is for general wellness and educational purposes only. It is not medical advice."
    )
