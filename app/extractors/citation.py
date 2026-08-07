import re
from typing import List


class CitationExtractor:
    """Stateless pure extractor for HTTP/HTTPS URL citations present in raw text."""

    @staticmethod
    def extract(text: str) -> List[str]:
        """Extracts unique HTTP/HTTPS URL strings from text."""
        if not text:
            return []

        url_pattern = r'https?://[^\s()<>]+'
        matches = re.findall(url_pattern, text)
        
        # Clean trailing punctuation from URLs
        cleaned_urls = set()
        for url in matches:
            clean_url = url.rstrip(".,;:!)]}>")
            if clean_url:
                cleaned_urls.add(clean_url)

        return sorted(list(cleaned_urls))


citation_extractor = CitationExtractor()
