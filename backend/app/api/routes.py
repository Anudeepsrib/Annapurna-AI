from fastapi import APIRouter, HTTPException, Depends
from app.services.evidence_service import evidence_service
from app.services.orchestrator import orchestrator
from app.services.usda_client import usda_client
from app.models.schemas import EvidenceResponse, FoodItem
from pydantic import BaseModel

router = APIRouter()

# --- Evidence Routes ---

@router.get("/evidence/{topic}", response_model=EvidenceResponse)
async def get_evidence(topic: str):
    """
    Get evidence for a topic. 
    Prioritizes curated guidelines, falls back to PubMed.
    """
    return await orchestrator.get_evidence(topic)

@router.get("/mcp/ifct/search")
async def search_ifct(query: str):
    """
    Search local IFCT database.
    """
    results = evidence_service.get_ifct_food(query)
    return {"results": results}

@router.get("/mcp/usda/search")
async def search_usda(query: str):
    """
    Search USDA FoodData Central.
    """
    results = await usda_client.search_foods(query)
    return results

# --- Plan Generation Routes ---

class PlanRequest(BaseModel):
    householdSize: str
    spiceLevel: str
    dietary: str

# Mock Data Store for MVP (In-memory)
generated_plan_store = []

@router.post("/generate-plan")
async def generate_plan(request: PlanRequest):
    """
    Generate a weekly meal plan (Mock implementation for MVP).
    """
    # In a real system, this would use LLM + Evidence to generate.
    # For MVP, we return a static curated Andhra plan.
    
    global generated_plan_store
    
    mock_plan = [
        {
            "day": "Monday",
            "date": "Jan 29",
            "meals": {
                "breakfast": {"title": "Pesarattu", "description": "Green gram dosa with ginger chutney", "ingredients": ["Green gram", "Ginger", "Chili"], "time": "8:00 AM"},
                "lunch": {"title": "Andhra Pappu & Rice", "description": "Tangy tomato dal with steamed rice", "ingredients": ["Toor dal", "Tomato", "Ghee"], "time": "1:00 PM"},
                "dinner": {"title": "Phulka & Bendakaya Fry", "description": "Soft rotis with crispy okra fry", "ingredients": ["Okra", "Whole wheat flour"], "time": "7:30 PM"}
            }
        },
        {
            "day": "Tuesday",
            "date": "Jan 30",
            "meals": {
                "breakfast": {"title": "Idli Sambar", "description": "Steamed rice cakes with lentil stew", "ingredients": ["Rice batter", "Lentils", "Vegetables"], "time": "8:00 AM"},
                "lunch": {"title": "Gutti Vankaya Curry", "description": "Stuffed eggplant curry with rice", "ingredients": ["Eggplant", "Peanuts", "Spices"], "time": "1:00 PM"},
                "dinner": {"title": "Vegetable Pulao", "description": "Mildly spiced rice with mixed veggies", "ingredients": ["Basmati rice", "Carrots", "Beans"], "time": "7:30 PM"}
            }
        },
        {
            "day": "Wednesday",
            "date": "Jan 31",
            "meals": {
                "breakfast": {"title": "Upma", "description": "Savory semolina porridge with veggies", "ingredients": ["Semolina", "Onion", "Cashews"], "time": "8:00 AM"},
                "lunch": {"title": "Rasam & Potato Fry", "description": "Pepper tamarind soup with aloo fry", "ingredients": ["Tamarind", "Potatoes", "Black pepper"], "time": "1:00 PM"},
                "dinner": {"title": "Dosa & Chutney", "description": "Crispy crepe with coconut chutney", "ingredients": ["Rice batter", "Coconut"], "time": "7:30 PM"}
            }
        },
        {
            "day": "Thursday",
            "date": "Feb 01",
            "meals": {
                "breakfast": {"title": "Pongal", "description": "Peppercorn seasoned rice and lentil porridge", "ingredients": ["Rice", "Moong dal", "Ghee"], "time": "8:00 AM"},
                "lunch": {"title": "Sambar Rice", "description": "Rice cooked in flavorful lentil stew", "ingredients": ["Rice", "Vegetables", "Sambar powder"], "time": "1:00 PM"},
                "dinner": {"title": "Chapati & Paneer Curry", "description": "Flatbread with cottage cheese curry", "ingredients": ["Paneer", "Wheat flour", "Tomato"], "time": "7:30 PM"}
            }
        },
        {
            "day": "Friday",
            "date": "Feb 02",
            "meals": {
                "breakfast": {"title": "Dosa", "description": "Crispy dosa with spicy ginger pickle", "ingredients": ["Rice batter", "Ginger pickle"], "time": "8:00 AM"},
                "lunch": {"title": "Lemon Rice", "description": "Tangy lemon flavored rice with peanuts", "ingredients": ["Rice", "Lemon", "Peanuts"], "time": "1:00 PM"},
                "dinner": {"title": "Semiya Upma", "description": "Vermicelli savory breakfast for dinner", "ingredients": ["Vermicelli", "Vegetables"], "time": "7:30 PM"}
            }
        },
        {
            "day": "Saturday",
            "date": "Feb 03",
            "meals": {
                "breakfast": {"title": "Poori Bhaji", "description": "Fried bread with potato curry", "ingredients": ["Wheat flour", "Potatoes"], "time": "9:00 AM"},
                "lunch": {"title": "Full Meals", "description": "Rice, Dal, Fry, Sambar, Curd", "ingredients": ["Rice", "Dal", "Vegetables"], "time": "1:00 PM"},
                "dinner": {"title": "Rava Dosa", "description": "Crispy semolina crepe", "ingredients": ["Semolina", "Rice flour"], "time": "8:00 PM"}
            }
        },
        {
            "day": "Sunday",
            "date": "Feb 04",
            "meals": {
                "breakfast": {"title": "Mysore Bonda", "description": "Fluffy fried fritters", "ingredients": ["Flour", "Yogurt", "Cumin"], "time": "9:00 AM"},
                "lunch": {"title": "Veg Biryani", "description": "Aromatic rice with spices", "ingredients": ["Basmati rice", "Spices", "Ghee"], "time": "1:00 PM"},
                "dinner": {"title": "Light Curd Rice", "description": "Yogurt rice with pomegranate", "ingredients": ["Rice", "Yogurt", "Pomegranate"], "time": "7:30 PM"}
            }
        }
    ]
    
    generated_plan_store = mock_plan
    return {"status": "success", "message": "Plan generated"}

@router.get("/plan")
async def get_plan():
    """
    Retrieve the current meal plan.
    """
    global generated_plan_store
    if not generated_plan_store:
         # Return a default if nothing generated yet (or could trigger generation)
         # For this demo, calling generate implicitly if empty is fine
         await generate_plan(PlanRequest(householdSize="2", spiceLevel="medium", dietary="vegetarian"))
         
    return generated_plan_store
