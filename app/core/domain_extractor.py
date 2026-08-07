from urllib.parse import urlparse


class DomainExtractor:
    """Utility extracting and normalizing clean target domains from raw URL strings."""

    @staticmethod
    def extract_domain(url: str) -> str:
        """Normalizes URL string to lower-case domain name (e.g. 'https://www.Acme.io/test' -> 'acme.io')."""
        if not url:
            return ""

        url_str = url.strip().lower()
        if not url_str.startswith(("http://", "https://")):
            url_str = f"https://{url_str}"

        parsed = urlparse(url_str)
        netloc = parsed.netloc or parsed.path

        # Strip port if present
        if ":" in netloc:
            netloc = netloc.split(":")[0]

        # Strip www. prefix
        if netloc.startswith("www."):
            netloc = netloc[4:]

        return netloc
