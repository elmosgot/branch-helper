import re
import unicodedata


def slugify(text: str) -> str:
    """Convert issue title text into a git-safe branch name segment."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", ascii_text)
    slug = re.sub(r"[-.]{2,}", "-", slug)
    return slug.strip("-.").lower()
