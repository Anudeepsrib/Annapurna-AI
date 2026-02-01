import json
import os
from typing import List
from app.models.schemas import EvidenceClaim, FoodItem

class EvidenceService:
    def __init__(self, data_dir: str = "../data/evidence"):
        # Adjust path relative to where app is run. Assuming run from backend/ dir.
        self.data_dir = data_dir
        self.guidelines = self._load_guidelines()
        self.food_composition = self._load_food_composition()

    def _load_guidelines(self) -> List[EvidenceClaim]:
        path = os.path.join(self.data_dir, "guidelines", "icmr_2024.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [EvidenceClaim(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not load guidelines from {path}")
            return []

    def _load_food_composition(self) -> List[FoodItem]:
        path = os.path.join(self.data_dir, "food_composition", "ifct_2017.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [FoodItem(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not load IFCT data from {path}")
            return []

    def get_guidelines(self, topic: str) -> List[EvidenceClaim]:
        """Filter guidelines by topic (case-insensitive substring match)."""
        search_term = topic.lower()
        return [
            g for g in self.guidelines 
            if search_term in g.topic.lower() or search_term in g.claim.lower()
        ]

    def get_ifct_food(self, query: str) -> List[FoodItem]:
        """Search IFCT foods by name."""
        search_term = query.lower()
        return [
            f for f in self.food_composition 
            if search_term in f.name.lower()
        ]

# Singleton instance
evidence_service = EvidenceService(data_dir="data/evidence")
