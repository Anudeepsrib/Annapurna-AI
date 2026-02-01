from pydantic import BaseModel, Field
from typing import Literal, Dict, List

# --- C. Curated Evidence Models ---

class EvidenceCitation(BaseModel):
    source: str = Field(..., description="Name of the source (e.g., 'ICMR-NIN Dietary Guidelines')")
    year: int = Field(..., description="Year of publication")
    identifier: str = Field(..., description="Section, page number, or specific ID")

class EvidenceClaim(BaseModel):
    id: str
    topic: str = Field(..., description="General topic (e.g., 'iron', 'pregnancy', 'protein')")
    claim: str = Field(..., description="The specific verified claim")
    evidence_type: Literal["guideline", "systematic-review", "meta-analysis"]
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
    micronutrients: Dict[str, float] = Field(default_factory=dict, description="Key-value pairs of micronutrients")

class FoodItem(BaseModel):
    id: str
    name: str
    source: Literal["IFCT", "USDA"]
    nutrients: NutrientProfile

# --- Plan Models ---

class PlanRequest(BaseModel):
    householdSize: str
    spiceLevel: str
    dietary: str

# --- API Response Models ---

class EvidenceResponse(BaseModel):
    topic: str
    claims: List[EvidenceClaim] = []
    disclaimer: str = "This information is for general wellness and educational purposes only. It is not medical advice."
