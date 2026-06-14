"""
Multi-source paper search module.

Search papers from arXiv, Semantic Scholar, CrossRef, and Google Scholar.
"""

import re
import time
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

import requests

from thesis.config import get_semantic_scholar_key, SEARCH_TIMEOUT, SEARCH_DEFAULT_LIMIT
from thesis.utils import RateLimiter


@dataclass
class Paper:
    """Represents a paper/metadata from any source."""
    title: str
    authors: str
    year: Optional[int] = None
    abstract: str = ""
    doi: str = ""
    url: str = ""
    pdf_url: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    source: str = ""
    citation_count: int = 0
    bibtex: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_reference_dict(self) -> dict:
        """Convert to format suitable for reference_manager."""
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "doi": self.doi,
            "url": self.url,
            "abstract": self.abstract,
            "bibtex": self.bibtex,
            "source": self.source,
        }


class PaperSearcher:
    """Search papers from multiple academic databases."""

    def __init__(self):
        self.rate_limiter = RateLimiter(calls_per_second=2.0)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ThesisMaster/1.0 (https://github.com/bayuuuu18/thesis-master)"
        })

    def search(self, query: str, source: str = "all", limit: int = 20,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               authors: Optional[str] = None) -> List[Paper]:
        """
        Search papers from specified source(s).

        Args:
            query: Search query
            source: Source to search ("arxiv", "semantic_scholar", "crossref", "all")
            limit: Maximum results
            year_from: Start year filter
            year_to: End year filter
            authors: Author name filter

        Returns:
            List of Paper objects
        """
        results = []
        limit = min(limit, SEARCH_DEFAULT_LIMIT)

        source_map = {
            "arxiv": self._search_arxiv,
            "semantic_scholar": self._search_semantic_scholar,
            "crossref": self._search_crossref,
            "google_scholar": self._search_google_scholar,
            "garuda": self._search_garuda,
        }

        if source == "all":
            per_source = max(5, limit // 3)
            for name, func in source_map.items():
                try:
                    self.rate_limiter.wait()
                    papers = func(query, limit=per_source, year_from=year_from,
                                  year_to=year_to, authors=authors)
                    results.extend(papers)
                except Exception as e:
                    print(f"Warning: {name} search failed: {e}")
        elif source in source_map:
            results = source_map[source](query, limit=limit, year_from=year_from,
                                          year_to=year_to, authors=authors)
        else:
            raise ValueError(f"Unknown source: {source}. Use: arxiv, semantic_scholar, crossref, google_scholar, garuda, all")

        # Deduplicate by title similarity
        results = self._deduplicate(results)
        return results[:limit]

    def _search_arxiv(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search arXiv API."""
        papers = []
        try:
            import arxiv
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.Relevance,
            )
            for result in search.results():
                year = result.published.year if result.published else None
                authors_str = ", ".join([a.name for a in result.authors[:10]])
                pdf_url = result.pdf_url if hasattr(result, 'pdf_url') else ""
                papers.append(Paper(
                    title=result.title.replace('\n', ' '),
                    authors=authors_str,
                    year=year,
                    abstract=result.summary.replace('\n', ' '),
                    doi=result.doi or "",
                    url=result.entry_id,
                    pdf_url=pdf_url,
                    journal="arXiv",
                    source="arxiv",
                ))
        except ImportError:
            # Fallback: use requests
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": limit,
                "sortBy": "relevance",
            }
            resp = self.session.get(url, params=params, timeout=SEARCH_TIMEOUT)
            if resp.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns).text or ""
                    summary = entry.find("atom:summary", ns).text or ""
                    published = entry.find("atom:published", ns).text or ""
                    year = int(published[:4]) if published else None
                    authors_list = entry.findall("atom:author/atom:name", ns)
                    authors_str = ", ".join([a.text for a in authors_list if a.text])
                    links = entry.findall("atom:link", ns)
                    pdf_url = ""
                    url = ""
                    for link in links:
                        if link.get("title") == "pdf":
                            pdf_url = link.get("href", "")
                        elif link.get("rel") == "alternate":
                            url = link.get("href", "")
                    doi_elem = entry.find("{http://arxiv.org/schemas/atom}doi")
                    doi = doi_elem.text if doi_elem is not None else ""
                    papers.append(Paper(
                        title=title.strip().replace('\n', ' '),
                        authors=authors_str,
                        year=year,
                        abstract=summary.strip().replace('\n', ' '),
                        doi=doi,
                        url=url,
                        pdf_url=pdf_url,
                        journal="arXiv",
                        source="arxiv",
                    ))
        except Exception as e:
            print(f"arXiv search error: {e}")
        return papers

    def _search_semantic_scholar(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search Semantic Scholar API."""
        papers = []
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": "title,authors,year,abstract,externalIds,url,citationCount,journal,publicationTypes",
        }
        api_key = get_semantic_scholar_key()
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key

        try:
            resp = self.session.get(url, params=params, headers=headers, timeout=SEARCH_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", []):
                    authors_list = [a.get("name", "") for a in item.get("authors", [])]
                    authors_str = ", ".join(authors_list[:10])
                    ext_ids = item.get("externalIds", {}) or {}
                    journal_info = item.get("journal", {}) or {}
                    papers.append(Paper(
                        title=item.get("title", ""),
                        authors=authors_str,
                        year=item.get("year"),
                        abstract=item.get("abstract", "") or "",
                        doi=ext_ids.get("DOI", ""),
                        url=item.get("url", ""),
                        journal=journal_info.get("name", ""),
                        volume=journal_info.get("volume", ""),
                        pages=journal_info.get("pages", ""),
                        citation_count=item.get("citationCount", 0),
                        source="semantic_scholar",
                    ))
        except Exception as e:
            print(f"Semantic Scholar search error: {e}")
        return papers

    def _search_crossref(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search CrossRef API."""
        papers = []
        url = "https://api.crossref.org/works"
        params = {
            "query": query,
            "rows": min(limit, 100),
            "sort": "relevance",
        }
        try:
            resp = self.session.get(url, params=params, timeout=SEARCH_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("message", {}).get("items", []):
                    title_parts = item.get("title", [])
                    title = title_parts[0] if title_parts else ""
                    authors_list = []
                    for author in item.get("author", []):
                        name_parts = []
                        if author.get("given"):
                            name_parts.append(author["given"])
                        if author.get("family"):
                            name_parts.append(author["family"])
                        if name_parts:
                            authors_list.append(" ".join(name_parts))
                    authors_str = ", ".join(authors_list[:10])
                    year = None
                    date_parts = item.get("published-print", {}).get("date-parts", [[]])
                    if date_parts and date_parts[0]:
                        year = date_parts[0][0]
                    if not year:
                        date_parts = item.get("created", {}).get("date-parts", [[]])
                        if date_parts and date_parts[0]:
                            year = date_parts[0][0]
                    container = item.get("container-title", [])
                    journal = container[0] if container else ""
                    papers.append(Paper(
                        title=title,
                        authors=authors_str,
                        year=year,
                        doi=item.get("DOI", ""),
                        url=item.get("URL", ""),
                        journal=journal,
                        volume=item.get("volume", ""),
                        issue=item.get("issue", ""),
                        pages=item.get("page", ""),
                        citation_count=item.get("is-referenced-by-count", 0),
                        source="crossref",
                    ))
        except Exception as e:
            print(f"CrossRef search error: {e}")
        return papers

    def _search_google_scholar(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search Google Scholar using scholarly library."""
        papers = []
        try:
            from scholarly import scholarly
            search_results = scholarly.search_pubs(query)
            count = 0
            for result in search_results:
                if count >= limit:
                    break
                try:
                    bib = result.get('bib', {})
                    title = bib.get('title', '')
                    authors = ', '.join(bib.get('author', []))
                    year = bib.get('pub_year')
                    if year:
                        year = int(year)
                    abstract = bib.get('abstract', '')
                    journal = bib.get('journal', '') or bib.get('venue', '')
                    volume = bib.get('volume', '')
                    pages = bib.get('pages', '')
                    url = result.get('pub_url', '') or result.get('eprint_url', '')
                    citation_count = result.get('num_citations', 0)

                    papers.append(Paper(
                        title=title,
                        authors=authors,
                        year=year,
                        abstract=abstract,
                        url=url,
                        journal=journal,
                        volume=volume,
                        pages=pages,
                        citation_count=citation_count,
                        source="google_scholar",
                    ))
                    count += 1
                except Exception:
                    continue
        except ImportError:
            print("Warning: scholarly not installed. Install with: pip install scholarly")
        except Exception as e:
            print(f"Google Scholar search error: {e}")
        return papers

    def _search_garuda(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search Indonesian academic papers via Google Scholar (Indonesian journals focus)."""
        papers = []
        try:
            from scholarly import scholarly
            # Add site filter for Indonesian journals
            indo_query = f'{query} site:garuda.kemdikbud.go.id OR site:jurnal.uns.ac.id OR site:jurnal.ugm.ac.id OR site:jurnal.ui.ac.id OR "jurnal indonesia"'
            search_results = scholarly.search_pubs(indo_query)
            count = 0
            for result in search_results:
                if count >= limit:
                    break
                try:
                    bib = result.get('bib', {})
                    title = bib.get('title', '')
                    authors = ', '.join(bib.get('author', []))
                    year = bib.get('pub_year')
                    if year:
                        year = int(year)
                    abstract = bib.get('abstract', '')
                    journal = bib.get('journal', '') or bib.get('venue', '')
                    volume = bib.get('volume', '')
                    pages = bib.get('pages', '')
                    url = result.get('pub_url', '') or result.get('eprint_url', '')
                    citation_count = result.get('num_citations', 0)

                    papers.append(Paper(
                        title=title,
                        authors=authors,
                        year=year,
                        abstract=abstract,
                        url=url,
                        journal=journal,
                        volume=volume,
                        pages=pages,
                        citation_count=citation_count,
                        source="garuda",
                    ))
                    count += 1
                except Exception:
                    continue
        except ImportError:
            print("Warning: scholarly not installed. Install with: pip install scholarly")
        except Exception as e:
            print(f"Garuda search error: {e}")
        return papers

    def _deduplicate(self, papers: List[Paper]) -> List[Paper]:
        """Remove duplicate papers based on title similarity."""
        seen_titles = set()
        unique = []
        for paper in papers:
            normalized = re.sub(r'[^a-z0-9]', '', paper.title.lower())
            if normalized and normalized not in seen_titles:
                seen_titles.add(normalized)
                unique.append(paper)
        return unique


def search_papers(query: str, source: str = "all", limit: int = 20,
                  year_from: Optional[int] = None, year_to: Optional[int] = None,
                  authors: Optional[str] = None) -> List[Paper]:
    """Convenience function for paper search."""
    searcher = PaperSearcher()
    return searcher.search(query, source=source, limit=limit,
                          year_from=year_from, year_to=year_to, authors=authors)
