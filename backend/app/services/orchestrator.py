from app.core.config import settings
from app.core.safety import CLINICIAN_GUIDANCE, WELLNESS_DISCLAIMER, detect_safety_concerns
from app.models.schemas import EvidenceClaim, EvidenceResponse
from app.services.evidence_service import evidence_service
from app.services.pubmed_client import pubmed_client


class EvidenceOrchestrator:
    def _is_safe_query(self, query: str) -> bool:
        """Check for blocked medical/disease keywords."""
        return not detect_safety_concerns(query)

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
                disclaimer=f"{WELLNESS_DISCLAIMER} {CLINICIAN_GUIDANCE}",
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

        if not summaries:
            disclaimer = "Curated local evidence was not found for this topic."
            if not settings.ENABLE_EXTERNAL_NETWORK or not settings.ENABLE_PUBMED:
                disclaimer += " PubMed lookup is disabled by default for local-first privacy."
            return EvidenceResponse(topic=topic, claims=[], disclaimer=disclaimer)

        # Convert PubMed summaries to "Claims" structure for consistency
        # PubMed results are abstracts, not verified app claims.
        research_claims = []
        for s in summaries:
            research_claims.append(
                EvidenceClaim(
                    id=f"PUBMED-{s.get('pmid')}",
                    topic=topic,
                    claim=f"Research abstract title: {s.get('title')}",
                    evidence_type="research-abstract",
                    population="Unknown",
                    limitations="Unverified PubMed abstract. Do not treat as clinical guidance.",
                    citation={
                        "source": s.get("source", "PubMed"),
                        "year": 2024,
                        "identifier": f"PMID:{s.get('pmid')}",
                    },
                )
            )

        return EvidenceResponse(
            topic=topic,
            claims=research_claims,
            disclaimer=(
                "NOTICE: Curated local evidence was not found. Showing PubMed abstracts only; "
                "verify with a qualified professional."
            ),
        )


orchestrator = EvidenceOrchestrator()
