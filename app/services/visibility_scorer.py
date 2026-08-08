"""
Deterministic visibility scorer.

Consumes the structured JSON returned by GeminiProvider.query_structured()
and computes all metrics without trusting Gemini-supplied scores.

Gemini is an evidence source. Scores are calculated here.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("app.services.visibility_scorer")

# ── Schema constants ───────────────────────────────────────────────────────────
EXPECTED_QUERIES = 8          # standardized evaluation dimensions
MIN_RESPONSE_LEN = 20         # minimum chars for a non-empty response


class VisibilityQueryResult:
    """Parsed result for a single evaluation query dimension."""

    def __init__(self, raw: Dict[str, Any]):
        self.query_id: str = str(raw.get("query_id", "unknown"))
        self.category: str = str(raw.get("category", "unknown"))
        self.query: str = str(raw.get("query", ""))
        self.response: str = str(raw.get("response", ""))
        self.brand_mentioned: bool = bool(raw.get("brand_mentioned", False))
        self.brand_position: Optional[int] = _safe_int(raw.get("brand_position"))
        self.competitors_listed: List[str] = _safe_list(raw.get("competitors_listed", []))
        self.recommendation_strength: int = _clamp(int(raw.get("recommendation_strength", 0)), 0, 5)
        self.evidence_snippet: str = str(raw.get("evidence_snippet", ""))[:500]


class VisibilityScorecard:
    """
    Deterministic scorecard calculated from structured Gemini evidence.

    Formula (documented):
      mention_rate         = mentioned_queries / total_queries
      recommendation_rate  = sum(recommendation_strength > 0) / total_queries
      avg_position_score   = 1 - (mean_brand_position - 1) / 10   [0–1, only when positioned]
      visibility_score     = 0.50 * mention_rate
                           + 0.35 * recommendation_rate
                           + 0.15 * avg_position_score
      (all clamped to [0.0, 1.0])
    """

    def __init__(
        self,
        brand: str,
        domain: str,
        queries: List[VisibilityQueryResult],
        raw_json: str,
    ):
        self.brand = brand
        self.domain = domain
        self.queries = queries
        self.raw_json = raw_json
        self.total_queries = len(queries)

        # ── Core metrics ─────────────────────────────────────────────────────
        self.mentioned_count = sum(1 for q in queries if q.brand_mentioned)
        self.mention_rate = round(
            self.mentioned_count / self.total_queries, 4
        ) if self.total_queries > 0 else 0.0

        self.recommended_count = sum(1 for q in queries if q.recommendation_strength > 0)
        self.recommendation_rate = round(
            self.recommended_count / self.total_queries, 4
        ) if self.total_queries > 0 else 0.0

        positioned = [q.brand_position for q in queries if q.brand_position is not None and q.brand_position >= 1]
        if positioned:
            mean_pos = sum(positioned) / len(positioned)
            self.avg_position_score = round(max(0.0, 1.0 - (mean_pos - 1) / 10.0), 4)
        else:
            self.avg_position_score = 0.0

        # ── Composite visibility score ────────────────────────────────────────
        raw_score = (
            0.50 * self.mention_rate
            + 0.35 * self.recommendation_rate
            + 0.15 * self.avg_position_score
        )
        self.visibility_score = round(min(1.0, max(0.0, raw_score)), 4)

        # ── Evidence aggregation ──────────────────────────────────────────────
        self.all_competitors: List[str] = sorted(set(
            c for q in queries for c in q.competitors_listed if c
        ))

        # Snippets: evidence where brand IS mentioned
        self.brand_evidence_snippets: List[str] = [
            q.evidence_snippet
            for q in queries
            if q.brand_mentioned and q.evidence_snippet
        ][:10]

        # Categories tested
        self.categories_tested: List[str] = sorted(set(q.category for q in queries if q.category))

        logger.info(
            "event=scorecard_calculated domain=%s total_queries=%d mentioned=%d "
            "mention_rate=%.2f recommendation_rate=%.2f visibility_score=%.2f",
            domain, self.total_queries, self.mentioned_count,
            self.mention_rate, self.recommendation_rate, self.visibility_score,
        )

    def summary_text(self) -> str:
        """Returns a human-readable summary of the scorecard for storage as raw_response."""
        lines = [
            f"AI Visibility Scorecard — {self.brand} ({self.domain})",
            f"",
            f"Visibility Score:      {self.visibility_score * 100:.1f}%",
            f"Mention Rate:          {self.mention_rate * 100:.1f}% ({self.mentioned_count}/{self.total_queries} queries)",
            f"Recommendation Rate:   {self.recommendation_rate * 100:.1f}% ({self.recommended_count}/{self.total_queries} queries)",
            f"Avg Position Score:    {self.avg_position_score * 100:.1f}%",
            f"",
            f"Categories tested: {', '.join(self.categories_tested) if self.categories_tested else 'n/a'}",
            f"Competitors identified: {', '.join(self.all_competitors[:8]) if self.all_competitors else 'none'}",
            f"",
            f"Evidence (queries where brand was mentioned):",
        ]
        for i, snip in enumerate(self.brand_evidence_snippets[:5], 1):
            lines.append(f"  [{i}] {snip[:200]}")
        if not self.brand_evidence_snippets:
            lines.append("  (brand not mentioned in any response)")
        return "\n".join(lines)


# ── Public parse function ──────────────────────────────────────────────────────

def parse_structured_response(raw_json: str, domain: str) -> VisibilityScorecard:
    """
    Parses the raw JSON string returned by Gemini and returns a VisibilityScorecard.

    Raises ValueError if the JSON cannot be parsed or has no valid queries.
    Never trusts Gemini-supplied numeric scores — all metrics are recalculated.
    """
    # Strip markdown code fences if Gemini wraps JSON in ```json ... ```
    cleaned = raw_json.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        # Try to extract JSON object from surrounding text
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                raise ValueError(f"Gemini response is not valid JSON: {exc}") from exc
        else:
            raise ValueError(f"Gemini response contains no JSON object: {exc}") from exc

    brand = str(data.get("brand", domain.split(".")[0].title()))
    raw_queries = data.get("queries", [])

    if not isinstance(raw_queries, list) or len(raw_queries) == 0:
        raise ValueError("Gemini structured response contains no 'queries' array.")

    parsed_queries = []
    for raw_q in raw_queries:
        if not isinstance(raw_q, dict):
            continue
        q = VisibilityQueryResult(raw_q)
        # Only count queries that have a meaningful response
        if len(q.response) >= MIN_RESPONSE_LEN:
            parsed_queries.append(q)

    if not parsed_queries:
        raise ValueError("No valid query results found in Gemini response.")

    return VisibilityScorecard(
        brand=brand,
        domain=domain,
        queries=parsed_queries,
        raw_json=raw_json,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _safe_int(val: Any) -> Optional[int]:
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _safe_list(val: Any) -> List[str]:
    if isinstance(val, list):
        return [str(x) for x in val if x]
    return []


def _clamp(val: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, val))
