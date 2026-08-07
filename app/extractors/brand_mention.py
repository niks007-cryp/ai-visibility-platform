import re
from typing import List, Tuple


class BrandMentionExtractor:
    """Stateless pure extractor for target brand presence and cited brand tokens."""

    @staticmethod
    def extract(text: str, target_domain: str) -> Tuple[bool, List[str]]:
        """Evaluates whether target_domain is mentioned and extracts brand name tokens.
        
        Returns:
            Tuple[mentioned: bool, extracted_brands: List[str]]
        """
        if not text or not target_domain:
            return False, []

        clean_text = text.lower()
        clean_domain = target_domain.lower().removeprefix("www.")
        domain_name = clean_domain.split(".")[0] if "." in clean_domain else clean_domain

        # Search for exact domain, domain_name, or root sub-tokens (e.g. "acme" from "acmesoftware")
        search_terms = {clean_domain, domain_name}
        # Add root prefix tokens if domain_name contains compound words (e.g., "acmesoftware" -> "acme")
        if len(domain_name) >= 4:
            search_terms.add(domain_name[:4])

        is_mentioned = any(term in clean_text for term in search_terms if len(term) >= 3)

        # Extract cited capitalized brand/domain tokens
        found_brands = set()
        words = re.findall(r'\b[A-Z][a-zA-Z0-9\.\-]{2,}\b', text)
        for w in words:
            w_clean = w.strip(".,;:()[]")
            if w_clean.lower() not in {"the", "and", "for", "with", "this", "that", "from", "best", "top", "status", "query", "simulated"}:
                found_brands.add(w_clean)

        return is_mentioned, sorted(list(found_brands))


brand_mention_extractor = BrandMentionExtractor()
