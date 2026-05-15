from typing import Any, Dict, List

import httpx

from app.core.config import settings


class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    async def search(self, query: str, retmax: int = 5) -> List[str]:
        """
        Search PubMed for a query and return PMIDs (if enabled).
        Returns empty list if PubMed is disabled.
        """
        if not settings.ENABLE_EXTERNAL_NETWORK or not settings.ENABLE_PUBMED:
            return []

        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax,
            "tool": "annapurna-ai",
            "email": settings.PUBMED_EMAIL,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/esearch.fcgi", params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("esearchresult", {}).get("idlist", [])
            except Exception:
                return []

    async def fetch_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch summary details for a list of PMIDs.
        Returns empty list if PubMed is disabled.
        """
        if not settings.ENABLE_EXTERNAL_NETWORK or not settings.ENABLE_PUBMED:
            return []

        if not pmids:
            return []

        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/esummary.fcgi", params=params)
                response.raise_for_status()
                data = response.json()
                result = data.get("result", {})

                summaries = []
                for pmid in pmids:
                    if pmid in result:
                        item = result[pmid]
                        summaries.append({
                            "pmid": pmid,
                            "title": item.get("title", ""),
                            "source": item.get("source", ""),
                            "pubdate": item.get("pubdate", ""),
                            "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        })
                return summaries
            except Exception:
                return []


pubmed_client = PubMedClient()
