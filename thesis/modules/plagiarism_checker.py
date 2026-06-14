"""
Plagiarism checker module.

Basic text similarity checker using online search APIs.
Note: This is a basic self-check tool, not a replacement for Turnitin.
"""

import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

import requests

from thesis.utils import clean_text


class PlagiarismChecker:
    """Check text against online sources for potential plagiarism."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (ThesisMaster/1.0; Educational)"
        })

    def check_text(self, text: str, chunk_size: int = 50) -> Dict:
        """
        Check text for potential plagiarism.

        Args:
            text: Text to check
            chunk_size: Number of words per chunk for checking

        Returns:
            Dictionary with results: {score, matches, report}
        """
        text = clean_text(text)
        if not text:
            return {"score": 0, "matches": [], "report": "No text to check."}

        words = text.split()
        if len(words) < 5:
            return {"score": 0, "matches": [], "report": "Text too short to check."}

        # Split into chunks
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append((i, chunk))

        matches = []
        total_checked = 0

        for start_idx, chunk in chunks[:10]:  # Limit to 10 chunks
            total_checked += 1
            # Search for the chunk
            search_results = self._search_web(chunk)
            for result in search_results:
                similarity = self._calculate_similarity(chunk, result.get("snippet", ""))
                if similarity > 0.3:  # 30% threshold
                    matches.append({
                        "original_text": chunk,
                        "source_url": result.get("url", ""),
                        "source_title": result.get("title", ""),
                        "matched_text": result.get("snippet", ""),
                        "similarity": round(similarity * 100, 1),
                        "word_position": start_idx,
                    })

        # Calculate overall score
        if matches:
            avg_similarity = sum(m["similarity"] for m in matches) / len(matches)
            score = min(100, avg_similarity * (len(matches) / max(total_checked, 1)))
        else:
            score = 0

        report = self._generate_report(text, matches, score)

        return {
            "score": round(score, 1),
            "matches": matches,
            "report": report,
            "chunks_checked": total_checked,
            "total_words": len(words),
        }

    def check_chunks(self, text: str, num_chunks: int = 5) -> List[Dict]:
        """Check specific chunks of text."""
        words = text.split()
        chunk_size = max(10, len(words) // num_chunks)
        results = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.split()) < 5:
                continue
            search_results = self._search_web(chunk)
            chunk_matches = []
            for result in search_results:
                similarity = self._calculate_similarity(chunk, result.get("snippet", ""))
                if similarity > 0.3:
                    chunk_matches.append({
                        "source_url": result.get("url", ""),
                        "source_title": result.get("title", ""),
                        "similarity": round(similarity * 100, 1),
                    })
            results.append({
                "chunk": chunk[:100] + "..." if len(chunk) > 100 else chunk,
                "matches": chunk_matches,
                "max_similarity": max([m["similarity"] for m in chunk_matches], default=0),
            })

        return results

    def _search_web(self, query: str) -> List[Dict]:
        """Search web for matching text using DuckDuckGo."""
        results = []
        try:
            # Use DuckDuckGo Instant Answer API
            truncated = " ".join(query.split()[:15])  # Limit query length
            url = "https://api.duckduckgo.com/"
            params = {
                "q": truncated,
                "format": "json",
                "no_redirect": 1,
                "no_html": 1,
            }
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Get related topics
                for topic in data.get("RelatedTopics", [])[:5]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:100],
                            "snippet": topic.get("Text", ""),
                            "url": topic.get("FirstURL", ""),
                        })
                # Get abstract
                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", ""),
                        "snippet": data["Abstract"],
                        "url": data.get("AbstractURL", ""),
                    })
        except Exception:
            pass

        # Fallback: Wikipedia search
        if not results:
            try:
                truncated = " ".join(query.split()[:10])
                url = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": truncated,
                    "format": "json",
                    "srlimit": 3,
                }
                resp = self.session.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("query", {}).get("search", []):
                        snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": snippet,
                            "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                        })
            except Exception:
                pass

        return results

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts."""
        if not text1 or not text2:
            return 0.0
        # Normalize
        t1 = re.sub(r'\s+', ' ', text1.lower().strip())
        t2 = re.sub(r'\s+', ' ', text2.lower().strip())
        # Use SequenceMatcher
        return SequenceMatcher(None, t1, t2).ratio()

    def _generate_report(self, text: str, matches: List[Dict], score: float) -> str:
        """Generate a human-readable plagiarism report."""
        lines = []
        lines.append("=" * 60)
        lines.append("           PLAGIARISM CHECK REPORT")
        lines.append("=" * 60)
        lines.append(f"")
        lines.append(f"  Overall Similarity Score: {score:.1f}%")
        lines.append(f"  Text Length: {len(text.split())} words")
        lines.append(f"  Matches Found: {len(matches)}")
        lines.append("")

        if score < 15:
            lines.append("  ✅ LOW similarity - Text appears mostly original")
        elif score < 40:
            lines.append("  ⚠️  MODERATE similarity - Review flagged sections")
        else:
            lines.append("  ❌ HIGH similarity - Significant rewriting recommended")

        lines.append("")
        lines.append("-" * 60)

        if matches:
            lines.append("  MATCHED SECTIONS:")
            lines.append("")
            for i, match in enumerate(matches[:10], 1):
                lines.append(f"  [{i}] Similarity: {match['similarity']}%")
                lines.append(f"      Source: {match['source_title'][:60]}")
                lines.append(f"      URL: {match['source_url']}")
                lines.append(f"      Text: \"{match['original_text'][:80]}...\"")
                lines.append("")
        else:
            lines.append("  No significant matches found.")
            lines.append("")

        lines.append("-" * 60)
        lines.append("  NOTE: This is a basic similarity check for self-review.")
        lines.append("  For official plagiarism detection, use Turnitin or similar.")
        lines.append("=" * 60)

        return "\n".join(lines)


def check_plagiarism(text: str) -> Dict:
    """Convenience function for plagiarism checking."""
    checker = PlagiarismChecker()
    return checker.check_text(text)
