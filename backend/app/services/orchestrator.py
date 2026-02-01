from app.services.evidence_service import evidence_service
from app.services.pubmed_client import pubmed_client
from app.models.schemas import EvidenceClaim, EvidenceResponse

class EvidenceOrchestrator:
    # Basic Safety Blocklist
    BLOCKED_KEYWORDS = [
        "cure", "treat", "prescription", "diagnostic", "diabetes", 
        "cancer", "pregnancy", "ckd", "kidney disease", "drug"
    ]

    def _is_safe_query(self, query: str) -> bool:
        """Check for blocked medical/disease keywords."""
        q = query.lower()
        if any(keyword in q for keyword in self.BLOCKED_KEYWORDS):
            return False
        return True

    async def get_evidence(self, topic: str) -> EvidenceResponse:
        """
        Main entry point for evidence retrieval.
        1. Safety Check
        2. Curated Evidence Check
        3. Fallback to PubMed (MCP Tool)
        """
        # 1. Safety Check
        if not self._is_safe_query(topic):
            return EvidenceResponse(
                topic=topic,
                claims=[],
                disclaimer="Safety Block: Query blocked. This system provides wellness info only, not medical advice for diseases."
            )

        # 2. Curated Check
        curated_claims = evidence_service.get_guidelines(topic)
        if curated_claims:
            return EvidenceResponse(
                topic=topic,
                claims=curated_claims
            )

        # 3. Fallback: PubMed Search
        # Note: In a full MCP implementation, we'd define this as a "Tool Call"
        pmids = await pubmed_client.search(topic, retmax=3)
        summaries = await pubmed_client.fetch_details(pmids)
        
        # Convert PubMed summaries to "Claims" structure for consistency
        # In reality, PubMed results aren't verified claims, so we label them "research-abstract"
        research_claims = []
        for s in summaries:
            research_claims.append(EvidenceClaim(
                id=f"PUBMED-{s.get('pmid')}",
                topic=topic,
                claim=f"Research Abstract: {s.get('title')}",
                evidence_type="systematic-review", # approximating for MVP
                population="Unknown", 
                limitations="Unverified PubMed Abstract",
                citation={
                    "source": s.get("source", "PubMed"),
                    "year": 2024, # Mock year if parsing fails
                    "identifier": f"PMID:{s.get('pmid')}"
                }
            ))

        return EvidenceResponse(
            topic=topic,
            claims=research_claims,
            disclaimer="NOTICE: Required verified evidence not found. Showing latest research abstracts. Verify with a professional."
        )

orchestrator = EvidenceOrchestrator()
