"""
Shared utilities for Thesis Master.

Text cleaning, formatting helpers, rate limiting, and common functions.
"""

import re
import time
import unicodedata
from typing import Optional, List
from functools import wraps


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove control characters except newlines
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_doi(text: str) -> Optional[str]:
    """Extract DOI from text."""
    pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_isbn(text: str) -> Optional[str]:
    """Extract ISBN-10 or ISBN-13 from text."""
    # Remove hyphens and spaces
    cleaned = re.sub(r'[-\s]', '', text)
    # ISBN-13
    match = re.search(r'97[89]\d{10}', cleaned)
    if match:
        return match.group(0)
    # ISBN-10
    match = re.search(r'\d{9}[\dXx]', cleaned)
    if match:
        return match.group(0)
    return None


def format_authors(authors: str, max_authors: int = 3) -> str:
    """Format author string for display."""
    if not authors:
        return "Unknown"
    author_list = [a.strip() for a in re.split(r'[;,]', authors) if a.strip()]
    if len(author_list) <= max_authors:
        return ", ".join(author_list)
    return f"{', '.join(author_list[:max_authors])} et al."


def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def word_count_to_target(current: int, target: int) -> str:
    """Return progress string towards word count target."""
    if target <= 0:
        return "No target set"
    percentage = min(100, int(current / target * 100))
    bar_length = 20
    filled = int(bar_length * percentage / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    return f"{bar} {current}/{target} words ({percentage}%)"


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe filesystem use."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('._')
    return filename[:200] if filename else "untitled"


def format_date(date_str: Optional[str], fmt: str = "%Y-%m-%d") -> str:
    """Format a date string for display."""
    if not date_str:
        return "N/A"
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime(fmt)
    except (ValueError, AttributeError):
        return date_str


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

    def __call__(self, func):
        """Use as decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


def safe_request(func):
    """Decorator for safe HTTP requests with error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    return wrapper


def parse_bibtex_entry(bibtex_str: str) -> dict:
    """Parse a single BibTeX entry into a dictionary."""
    result = {}
    # Extract entry type
    type_match = re.match(r'@(\w+)\{', bibtex_str)
    if type_match:
        result['entry_type'] = type_match.group(1).lower()

    # Extract key
    key_match = re.match(r'@\w+\{(\w+)', bibtex_str)
    if key_match:
        result['cite_key'] = key_match.group(1)

    # Extract fields
    field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'
    for match in re.finditer(field_pattern, bibtex_str):
        key = match.group(1).lower()
        value = match.group(2).strip()
        result[key] = value

    return result


def generate_cite_key(authors: str, year: int, title: str) -> str:
    """Generate a BibTeX cite key."""
    first_author = "Unknown"
    if authors:
        first_author = re.split(r'[;,]', authors)[0].strip()
        # Get last name
        parts = first_author.split()
        first_author = parts[-1] if parts else "Unknown"

    first_author = re.sub(r'[^a-zA-Z]', '', first_author).lower()
    year_str = str(year) if year else "0000"
    # First word of title
    title_word = re.sub(r'[^a-zA-Z\s]', '', title).split()[0].lower() if title else "untitled"

    return f"{first_author}{year_str}{title_word}"
