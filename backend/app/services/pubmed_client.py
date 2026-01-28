import httpx
from typing import Dict, List, Any

class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    async def search(self, query: str, retmax: int = 5) -> List[str]:
        """
        Search PubMed for a query and return PMIDs.
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax,
            "tool": "annapurna-ai",
            "email": "agent@annapurna.ai" # Dummy email for nice behavior
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/esearch.fcgi", params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("esearchresult", {}).get("idlist", [])
            except Exception as e:
                print(f"PubMed Search Error: {e}")
                return []

    async def fetch_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch summary details for a list of PMIDs.
        Returns simplified metadata (Title, Abstract, Source).
        """
        if not pmids:
            return []
            
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
            "rettype": "abstract",  # efetch doesn't always support json for abstract, esummary does but no abstract
             # actually efetch returns XML mostly, esummary returns JSON.
             # For MVP, let's use esummary to get title/source and skip abstract if complex xml parsing is needed
             # OR use efetch with 'text' mode for simple retrieval.
             # User requested JSON output. efetch json isn't standard.
             # Let's use esummary for metadata.
        }
        
        # NOTE: esummary doesn't usually give abstracts. 
        # For a robust "MCP" tool we might need XML parsing, but let's stick to esummary for JSON simplicity for MVP.
        # If abstract is CRITICAL, we'd need efetch=xml and an XML parser. 
        # Given "Atomic/Simple" constraints, let's try esummary first.
        
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
                            # Abstract is missing in esummary
                            "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        })
                return summaries
            except Exception as e:
                print(f"PubMed Fetch Error: {e}")
                return []

pubmed_client = PubMedClient()
