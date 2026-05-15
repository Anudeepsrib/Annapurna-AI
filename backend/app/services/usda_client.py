from typing import Any, Dict

import httpx

from app.core.config import settings


class USDAClient:
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"

    async def search_foods(self, query: str) -> Dict[str, Any]:
        """
        Search USDA database (if enabled).
        Returns empty dict if USDA is disabled or no API key.
        """
        # Check if USDA lookups are enabled
        if not settings.ENABLE_EXTERNAL_NETWORK or not settings.ENABLE_USDA:
            return {}

        # Use API key from settings
        api_key = settings.USDA_API_KEY
        if not api_key:
            return {}

        params = {
            "query": query,
            "api_key": api_key,
            "pageSize": 5,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/foods/search", params=params)
                response.raise_for_status()
                return response.json()
            except Exception:
                return {}


usda_client = USDAClient()
