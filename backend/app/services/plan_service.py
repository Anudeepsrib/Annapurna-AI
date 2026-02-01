from sqlmodel import Session, select
from app.models.db import MealPlan
from app.services.llm_service import llm_service
from app.models.schemas import PlanRequest
import json
import os
import structlog

logger = structlog.get_logger()

class PlanService:
    def __init__(self, session: Session):
        self.session = session

    async def generate_plan(self, request: PlanRequest, user_id: str):
        """
        Generates a plan using LLM (or mock), saves to DB, and returns it.
        """
        plan_data = None
        
        # 1. Attempt LLM Generation
        if os.getenv("OPENAI_API_KEY"):
            try:
                plan_data = await self._generate_with_llm(request, user_id)
            except Exception as e:
                logger.error("LLM Generation Failed", error=str(e))
        
        # 2. Fallback to Mock if LLM failed or not configured
        if not plan_data:
            logger.info("Using Mock Generation")
            plan_data = self._get_mock_plan()

        # 3. Save to Database
        self._save_plan(user_id, plan_data)
        
        return plan_data

    async def get_latest_plan(self, user_id: str):
        """
        Retrieves the most recent plan for the user.
        """
        statement = select(MealPlan).where(MealPlan.user_id == user_id).order_by(MealPlan.created_at.desc())
        result = self.session.exec(statement).first()
        
        if result:
            return result.plan_data
        return None

    def _save_plan(self, user_id: str, plan_data: list):
        # json.dumps ensures we store it as a string
        json_content = json.dumps(plan_data)
        db_plan = MealPlan(user_id=user_id, plan_json=json_content)
        self.session.add(db_plan)
        self.session.commit()
        self.session.refresh(db_plan)
        logger.info("Plan saved to DB", id=db_plan.id)

    async def _generate_with_llm(self, request: PlanRequest, user_id: str):
        system_prompt = "You are an expert nutritionist specialized in Indian cuisine." \
                        "Return ONLY a JSON object with the structure: " \
                        "[{day: 'Monday', date: '...', meals: {breakfast: {title, description, ingredients:[], time}, lunch: {...}, dinner: {...}}}, ...]"
        
        user_prompt = f"Create a 7-day meal plan for {request.householdSize} people, {request.dietary}, spice level {request.spiceLevel}. Use Andhra style recipes."
        
        llm_response = await llm_service.generate_response(
            system_prompt, 
            user_prompt, 
            json_mode=True, 
            user_id=user_id
        )
        
        if llm_response:
            return json.loads(llm_response)
        return None

    def _get_mock_plan(self):
        # Return the static mock data (Same as before)
        return [
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
                    "breakfast": {"title": "Idli Sambar", "description": "Steamed rice cakes", "ingredients": ["Rice", "Lentils"], "time": "8:00 AM"},
                    "lunch": {"title": "Gutti Vankaya", "description": "Stuffed Brinjal", "ingredients": ["Brinjal", "Peanuts"], "time": "1:00 PM"},
                    "dinner": {"title": "Veg Pulao", "description": "Mixed Veg Price", "ingredients": ["Rice", "Veggies"], "time": "8:00 PM"}
                }
            }
        ]

    async def generate_grocery_list(self, user_id: str):
        """
        Generates a grocery list based on the user's latest plan.
        """
        plan_data = await self.get_latest_plan(user_id)
        if not plan_data:
            return []
            
        # Aggregate ingredients
        ingredients_map = {}
        
        for day in plan_data:
            meals = day.get("meals", {})
            for meal_type, meal_info in meals.items():
                meal_title = meal_info.get("title")
                ingredients = meal_info.get("ingredients", [])
                
                for ing in ingredients:
                    # Normalize ingredient name
                    ing_name = ing.strip()
                    if ing_name not in ingredients_map:
                        ingredients_map[ing_name] = {
                            "id": ing_name.lower().replace(" ", "-"),
                            "name": ing_name,
                            "count": 0,
                            "meals": set()
                        }
                    ingredients_map[ing_name]["count"] += 1
                    ingredients_map[ing_name]["meals"].add(meal_title)

        # Convert to list
        items = []
        for ing_name, data in ingredients_map.items():
            items.append({
                "id": data["id"],
                "name": data["name"],
                "quantity": f"{data['count']} unit(s)", # Placeholder quantity logic
                "meals": list(data["meals"])
            })
            
        # Simple categorization (Can be improved with LLM or Dictionary)
        # For now, put everything in "Weekly Essentials"
        return [{
            "name": "Weekly Essentials",
            "items": items
        }]
