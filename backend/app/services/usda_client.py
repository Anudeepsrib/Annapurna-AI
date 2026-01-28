import httpx
from typing import Dict, Any, Optional

class USDAClient:
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    # In a real app, API_KEY would come from env vars.
    # We will assume a DEMO_KEY for this MVP or expect an env var.
    API_KEY = "DEMO_KEY" 

    async def search_foods(self, query: str) -> Dict[str, Any]:
        """Search USDA database."""
        params = {
            "query": query,
            "api_key": self.API_KEY,
            "pageSize": 5
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/foods/search", params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"USDA Search Error: {e}")
                return {}

usda_client = USDAClient()
