import uuid
from typing import List
from app.models.extracted_evidence import ExtractedEvidence
from app.schemas.recommendation import (
    Recommendation,
    PriorityLevel,
    EffortLevel,
    ImpactLevel,
)


class RecommendationRuleEngine:
    """Pure deterministic rule engine mapping ExtractedEvidence facts to actionable remediation recommendations."""

    @staticmethod
    def generate_recommendations(evidence: ExtractedEvidence) -> List[Recommendation]:
        """Evaluates factual evidence against deterministic business rules.
        
        Returns:
            List[Recommendation] ordered by priority (P0 -> P1 -> P2).
        """
        recommendations: List[Recommendation] = []

        # Rule 1: Entity Recognition (P0 Critical)
        if not evidence.mentioned:
            recommendations.append(
                Recommendation(
                    id=uuid.uuid5(uuid.NAMESPACE_DNS, f"rec-p0-entity-{evidence.id}"),
                    title="Improve Entity Recognition Across Authoritative Sources",
                    description=(
                        f"Target domain '{evidence.target_domain}' was not cited or recommended in AI provider output. "
                        "Publish a dedicated category landing page and update listings on top third-party review directories "
                        "(G2, Capterra, Trustpilot) to anchor brand entity recognition."
                    ),
                    category="Entity Optimization",
                    priority=PriorityLevel.P0,
                    effort=EffortLevel.MEDIUM,
                    expected_impact=ImpactLevel.HIGH,
                    trigger="mentioned == False",
                    evidence_reference=f"ExtractedEvidence ID: {evidence.id} (mentioned=False)",
                    verification_method="Re-audit AI visibility 14 days post-publication to verify brand mention."
                )
            )

        # Rule 2: Structured Citation Ingress (P1 High)
        if len(evidence.raw_citations) == 0:
            recommendations.append(
                Recommendation(
                    id=uuid.uuid5(uuid.NAMESPACE_DNS, f"rec-p1-citation-{evidence.id}"),
                    title="Add Schema.org Organization Markup & Canonical Links",
                    description=(
                        f"Brand '{evidence.target_domain}' was processed without direct HTTP/HTTPS URL links in AI output. "
                        "Implement Schema.org Organization JSON-LD markup and embed canonical website links in high-authority directory profiles."
                    ),
                    category="Technical SEO",
                    priority=PriorityLevel.P1,
                    effort=EffortLevel.LOW,
                    expected_impact=ImpactLevel.HIGH,
                    trigger="raw_citations is empty",
                    evidence_reference=f"ExtractedEvidence ID: {evidence.id} (raw_citations=[])",
                    verification_method="Verify HTTP citation URL presence in subsequent AI audit responses."
                )
            )

        # Rule 3: AI Retrieval Content Optimization (P1 High)
        if len(evidence.matched_snippets) == 0:
            recommendations.append(
                Recommendation(
                    id=uuid.uuid5(uuid.NAMESPACE_DNS, f"rec-p1-snippet-{evidence.id}"),
                    title="Publish FAQ & Category Comparison Content Targeting AI Retrieval",
                    description=(
                        f"No verbatim recommendation sentence quotes were generated for '{evidence.target_domain}'. "
                        "Publish structured Q&A and FAQ content targeting direct category search queries."
                    ),
                    category="Content Strategy",
                    priority=PriorityLevel.P1,
                    effort=EffortLevel.MEDIUM,
                    expected_impact=ImpactLevel.HIGH,
                    trigger="matched_snippets is empty",
                    evidence_reference=f"ExtractedEvidence ID: {evidence.id} (matched_snippets=[])",
                    verification_method="Check for verbatim sentence quote extraction in AI audit report."
                )
            )

        # Rule 4: Competitor Positioning (P2 Medium)
        competitor_count = len(evidence.extracted_brand_mentions)
        if competitor_count > 3:
            recommendations.append(
                Recommendation(
                    id=uuid.uuid5(uuid.NAMESPACE_DNS, f"rec-p2-competitor-{evidence.id}"),
                    title="Create Versus & Competitor Alternative Comparison Pages",
                    description=(
                        f"High competitor density detected ({competitor_count} competing brands cited in AI output). "
                        "Create explicit '/vs/<competitor>' comparison pages highlighting feature matrix differentiators."
                    ),
                    category="Competitive Positioning",
                    priority=PriorityLevel.P2,
                    effort=EffortLevel.HIGH,
                    expected_impact=ImpactLevel.MEDIUM,
                    trigger=f"competitor_count > 3 ({competitor_count} brands cited)",
                    evidence_reference=f"ExtractedEvidence ID: {evidence.id} (extracted_brand_mentions={competitor_count})",
                    verification_method="Verify target brand inclusion in comparative category queries."
                )
            )

        return recommendations


recommendation_rule_engine = RecommendationRuleEngine()
