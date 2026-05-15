import json
import os

import structlog

from app.models.schemas import EvidenceClaim, FoodItem

logger = structlog.get_logger()


class EvidenceService:
    def __init__(self, data_dir: str = None):
        # Always use absolute path to gracefully resolve from any run directory
        if data_dir is None:
            self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "evidence"))
        else:
            self.data_dir = data_dir
            
        self.guidelines = self._load_guidelines()
        self.food_composition = self._load_food_composition()

    def _load_guidelines(self) -> list[EvidenceClaim]:
        path = os.path.join(self.data_dir, "guidelines", "icmr_2024.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [EvidenceClaim(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("Could not load local guidelines", path=path)
            return []

    def _load_food_composition(self) -> list[FoodItem]:
        path = os.path.join(self.data_dir, "food_composition", "ifct_2017.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [FoodItem(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("Could not load local food composition data", path=path)
            return []

    def get_guidelines(self, topic: str) -> list[EvidenceClaim]:
        """Filter guidelines by topic (case-insensitive substring match)."""
        search_term = topic.lower()
        return [
            g for g in self.guidelines
            if search_term in g.topic.lower() or search_term in g.claim.lower()
        ]

    def get_ifct_food(self, query: str) -> list[FoodItem]:
        """Search IFCT foods by name."""
        search_term = query.lower()
        return [
            f for f in self.food_composition
            if search_term in f.name.lower()
        ]


# Singleton instance
evidence_service = EvidenceService()
