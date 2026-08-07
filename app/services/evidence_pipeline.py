from typing import Dict, Any
from app.extractors.brand_mention import brand_mention_extractor, BrandMentionExtractor
from app.extractors.citation import citation_extractor, CitationExtractor
from app.extractors.snippet import snippet_extractor, SnippetExtractor


class EvidencePipeline:
    """Orchestrates pure stateless extractors to transform raw AI text into factual evidence."""

    def __init__(
        self,
        brand_extractor: BrandMentionExtractor = brand_mention_extractor,
        citation_ext: CitationExtractor = citation_extractor,
        snippet_ext: SnippetExtractor = snippet_extractor
    ):
        self.brand_extractor = brand_extractor
        self.citation_ext = citation_ext
        self.snippet_ext = snippet_ext

    def process(self, raw_text: str, target_domain: str) -> Dict[str, Any]:
        """Runs extraction pipeline deterministically on raw_text for target_domain."""
        mentioned, brand_mentions = self.brand_extractor.extract(raw_text, target_domain)
        citations = self.citation_ext.extract(raw_text)
        snippets = self.snippet_ext.extract(raw_text, target_domain)

        return {
            "mentioned": mentioned,
            "raw_citations": citations,
            "matched_snippets": snippets,
            "extracted_brand_mentions": brand_mentions
        }


evidence_pipeline = EvidencePipeline()
