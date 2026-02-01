from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import json

class MealPlan(SQLModel, table=True):
    """
    Database model for storing generated meal plans.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Store the JSON blob of the plan directly
    # In a larger app, we might normalize meals into separate tables,
    # but for this MVP, storing the complex JSON structure is efficient.
    plan_json: str # JSON stringified content

    @property
    def plan_data(self):
        return json.loads(self.plan_json)

    @plan_data.setter
    def plan_data(self, value):
        self.plan_json = json.dumps(value)
