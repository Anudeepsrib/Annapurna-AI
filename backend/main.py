from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from mock_data import mock_week_plan, grocery_categories

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserPreferences(BaseModel):
    householdSize: str
    spiceLevel: str
    dietary: str
    expertise: Optional[str] = "intermediate"

# Simple in-memory store for the generated plan (per session roughly, since it's global variable)
# In a real app, this would be in a database or keyed by user session.
current_plan = mock_week_plan
current_grocery_list = grocery_categories

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/generate-plan")
def generate_plan(prefs: UserPreferences):
    # In a real app, we would use LLM here to generate based on prefs.
    # For MVP, we just return the mock plan, maybe logging the prefs.
    print(f"Generating plan for preferences: {prefs}")
    
    # We could slightly customize the mock data here if we wanted to prove dynamic generation
    # But returning standard mock data is fine for step 1 of integration.
    return {"status": "success", "message": "Plan generated successfully"}

@app.get("/api/plan")
def get_plan():
    return current_plan

@app.get("/api/grocery-list")
def get_grocery_list():
    return current_grocery_list
