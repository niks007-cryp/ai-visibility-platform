import re
from typing import List


class SnippetExtractor:
    """Stateless pure extractor for verbatim sentence quotes referencing target domain."""

    @staticmethod
    def extract(text: str, target_domain: str) -> List[str]:
        """Tokenizes text into sentences and extracts verbatim quotes referencing target_domain."""
        if not text or not target_domain:
            return []

        clean_domain = target_domain.lower().removeprefix("www.")
        domain_name = clean_domain.split(".")[0] if "." in clean_domain else clean_domain

        search_terms = {clean_domain, domain_name}
        if len(domain_name) >= 4:
            search_terms.add(domain_name[:4])

        # Tokenize into sentences (split by . ! ? \n)
        sentences = re.split(r'(?<=[.!?\n])\s+', text)
        matched_quotes = []

        for sentence in sentences:
            s_stripped = sentence.strip()
            if not s_stripped:
                continue
                
            s_lower = s_stripped.lower()
            if any(term in s_lower for term in search_terms if len(term) >= 3):
                matched_quotes.append(s_stripped)

        return matched_quotes


snippet_extractor = SnippetExtractor()
