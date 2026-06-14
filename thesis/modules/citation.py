"""
Citation generator module.

Generate formatted citations in multiple academic styles:
APA 7th, IEEE, Chicago, Harvard, Vancouver, GB/T 7714.
"""

import re
from typing import Optional, Dict, List

import requests

from thesis.database import Database
from thesis.utils import format_authors, extract_doi


class CitationGenerator:
    """Generate citations in multiple formats."""

    def generate_from_doi(self, doi: str, fmt: str = "apa7") -> str:
        """Generate citation from DOI using CrossRef API."""
        try:
            url = f"https://api.crossref.org/works/{doi}"
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                return f"Error: Could not retrieve metadata for DOI {doi}"
            item = resp.json().get("message", {})
            return self._format_from_crossref(item, fmt)
        except Exception as e:
            return f"Error: {e}"

    def generate_from_isbn(self, isbn: str, fmt: str = "apa7") -> str:
        """Generate citation from ISBN using Open Library API."""
        try:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                return f"Error: Could not retrieve metadata for ISBN {isbn}"
            data = resp.json()
            key = f"ISBN:{isbn}"
            if key not in data:
                return f"Error: ISBN {isbn} not found"
            book = data[key]
            return self._format_from_openlibrary(book, isbn, fmt)
        except Exception as e:
            return f"Error: {e}"

    def generate_from_reference(self, ref_id: int, fmt: str = "apa7") -> str:
        """Generate citation from a stored reference."""
        with Database() as db:
            ref = db.fetch_one("SELECT * FROM references_table WHERE id = ?", (ref_id,))
        if not ref:
            return f"Error: Reference {ref_id} not found"
        return self._format_from_dict(ref, fmt)

    def generate_manual(self, data: dict, fmt: str = "apa7") -> str:
        """Generate citation from manually provided data."""
        return self._format_from_dict(data, fmt)

    def _format_from_crossref(self, item: dict, fmt: str) -> str:
        """Format CrossRef data into citation string."""
        title_parts = item.get("title", [])
        title = title_parts[0] if title_parts else "Untitled"
        authors_list = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            authors_list.append({"given": given, "family": family})
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
        volume = item.get("volume", "")
        issue = item.get("issue", "")
        pages = item.get("page", "")
        doi = item.get("DOI", "")
        url = item.get("URL", "")
        publisher = item.get("publisher", "")

        return self._format_citation(
            title=title, authors=authors_list, year=year, journal=journal,
            volume=volume, issue=issue, pages=pages, doi=doi, url=url,
            publisher=publisher, fmt=fmt
        )

    def _format_from_openlibrary(self, book: dict, isbn: str, fmt: str) -> str:
        """Format Open Library data into citation string."""
        title = book.get("title", "Untitled")
        authors_list = []
        for author in book.get("authors", []):
            name = author.get("name", "")
            parts = name.split()
            if len(parts) >= 2:
                authors_list.append({"given": " ".join(parts[:-1]), "family": parts[-1]})
            else:
                authors_list.append({"given": name, "family": ""})
        publishers = book.get("publishers", [])
        publisher = publishers[0].get("name", "") if publishers else ""
        publish_date = book.get("publish_date", "")
        year = None
        year_match = re.search(r'\d{4}', publish_date)
        if year_match:
            year = int(year_match.group())

        return self._format_citation(
            title=title, authors=authors_list, year=year,
            publisher=publisher, isbn=isbn, fmt=fmt
        )

    def _format_from_dict(self, data: dict, fmt: str) -> str:
        """Format reference dictionary into citation string."""
        authors_str = data.get("authors", "")
        authors_list = []
        for author in re.split(r'[;,]', authors_str):
            author = author.strip()
            if not author:
                continue
            parts = author.split()
            if len(parts) >= 2:
                authors_list.append({"given": " ".join(parts[:-1]), "family": parts[-1]})
            else:
                authors_list.append({"given": "", "family": author})

        return self._format_citation(
            title=data.get("title", "Untitled"),
            authors=authors_list,
            year=data.get("year"),
            journal=data.get("journal", ""),
            volume=data.get("volume", ""),
            issue=data.get("issue", ""),
            pages=data.get("pages", ""),
            doi=data.get("doi", ""),
            url=data.get("url", ""),
            publisher=data.get("publisher", ""),
            isbn=data.get("isbn", ""),
            edition=data.get("edition", ""),
            city=data.get("city", ""),
            fmt=fmt,
        )

    def _format_citation(self, title: str, authors: list, year: int = None,
                         journal: str = "", volume: str = "", issue: str = "",
                         pages: str = "", doi: str = "", url: str = "",
                         publisher: str = "", isbn: str = "", edition: str = "",
                         city: str = "", fmt: str = "apa7") -> str:
        """Format a citation in the specified style."""
        formatters = {
            "apa7": self._format_apa7,
            "apa": self._format_apa7,
            "ieee": self._format_ieee,
            "chicago": self._format_chicago,
            "harvard": self._format_harvard,
            "vancouver": self._format_vancouver,
            "gbt7714": self._format_gbt7714,
        }
        formatter = formatters.get(fmt.lower(), self._format_apa7)
        return formatter(
            title=title, authors=authors, year=year, journal=journal,
            volume=volume, issue=issue, pages=pages, doi=doi, url=url,
            publisher=publisher, isbn=isbn, edition=edition, city=city
        )

    def _format_authors_apa(self, authors: list) -> str:
        """Format authors for APA style."""
        if not authors:
            return ""
        formatted = []
        for a in authors:
            family = a.get("family", "")
            given = a.get("given", "")
            if family and given:
                initials = "".join([n[0] + ". " for n in given.split() if n]).strip()
                formatted.append(f"{family}, {initials}")
            elif family:
                formatted.append(family)
        if len(formatted) == 1:
            return formatted[0]
        elif len(formatted) == 2:
            return f"{formatted[0]}, & {formatted[1]}"
        elif len(formatted) <= 20:
            return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
        else:
            first_19 = ", ".join(formatted[:19])
            return f"{first_19}, . . . {formatted[-1]}"

    def _format_authors_last_first(self, authors: list) -> str:
        """Format authors as Last, F. I."""
        return self._format_authors_apa(authors)

    def _format_authors_first_last(self, authors: list) -> str:
        """Format authors as F. I. Last."""
        if not authors:
            return ""
        formatted = []
        for a in authors:
            family = a.get("family", "")
            given = a.get("given", "")
            if family and given:
                initials = "".join([n[0].upper() + ". " for n in given.split() if n]).strip()
                formatted.append(f"{initials} {family}")
            elif family:
                formatted.append(family)
        if len(formatted) <= 6:
            return ", ".join(formatted[:-1]) + f", & {formatted[-1]}" if len(formatted) > 1 else formatted[0]
        else:
            return ", ".join(formatted[:6]) + ", et al."

    def _format_apa7(self, **kw) -> str:
        """APA 7th Edition format."""
        authors = self._format_authors_apa(kw["authors"])
        year_str = f"({kw['year']})" if kw.get("year") else "(n.d.)"
        title = kw.get("title", "Untitled")
        journal = kw.get("journal", "")
        doi = kw.get("doi", "")
        url = kw.get("url", "")

        if journal:
            parts = f"{authors} {year_str}. {title}. *{journal}*"
            if kw.get("volume"):
                parts += f", *{kw['volume']}*"
            if kw.get("issue"):
                parts += f"({kw['issue']})"
            if kw.get("pages"):
                parts += f", {kw['pages']}"
            parts += "."
            if doi:
                parts += f" https://doi.org/{doi}"
            elif url:
                parts += f" {url}"
            return parts
        else:
            publisher = kw.get("publisher", "")
            parts = f"{authors} {year_str}. *{title}*."
            if publisher:
                parts += f" {publisher}."
            if doi:
                parts += f" https://doi.org/{doi}"
            elif url:
                parts += f" {url}"
            return parts

    def _format_ieee(self, **kw) -> str:
        """IEEE format."""
        authors = self._format_authors_first_last(kw["authors"])
        title = kw.get("title", "Untitled")
        journal = kw.get("journal", "")
        year = kw.get("year", "n.d.")

        if journal:
            parts = f'{authors}, "{title},"'
            parts += f" *{journal}*"
            if kw.get("volume"):
                parts += f", vol. {kw['volume']}"
            if kw.get("issue"):
                parts += f", no. {kw['issue']}"
            if kw.get("pages"):
                parts += f", pp. {kw['pages']}"
            parts += f", {year}."
            if kw.get("doi"):
                parts += f" doi: {kw['doi']}"
            return parts
        else:
            return f'{authors}, *{title}*. {kw.get("publisher", "")}, {year}.'

    def _format_chicago(self, **kw) -> str:
        """Chicago Author-Date format."""
        authors = self._format_authors_apa(kw["authors"])
        year_str = kw.get("year", "n.d.")
        title = kw.get("title", "Untitled")
        journal = kw.get("journal", "")

        if journal:
            parts = f'{authors}. {year_str}. "{title}." *{journal}*'
            if kw.get("volume"):
                parts += f" {kw['volume']}"
            if kw.get("issue"):
                parts += f", no. {kw['issue']}"
            if kw.get("pages"):
                parts += f": {kw['pages']}"
            parts += "."
            if kw.get("doi"):
                parts += f" https://doi.org/{kw['doi']}."
            return parts
        else:
            return f'{authors}. {year_str}. *{title}*. {kw.get("publisher", "")}.'

    def _format_harvard(self, **kw) -> str:
        """Harvard format."""
        authors = self._format_authors_apa(kw["authors"])
        year_str = kw.get("year", "n.d.")
        title = kw.get("title", "Untitled")
        journal = kw.get("journal", "")

        if journal:
            parts = f"{authors} ({year_str}) '{title}', *{journal}*"
            if kw.get("volume"):
                parts += f", {kw['volume']}"
            if kw.get("issue"):
                parts += f"({kw['issue']})"
            if kw.get("pages"):
                parts += f", pp. {kw['pages']}"
            parts += "."
            if kw.get("doi"):
                parts += f" doi: {kw['doi']}."
            return parts
        else:
            return f"{authors} ({year_str}) *{title}*. {kw.get('publisher', '')}."

    def _format_vancouver(self, **kw) -> str:
        """Vancouver format."""
        authors = self._format_authors_first_last(kw["authors"])
        title = kw.get("title", "Untitled")
        journal = kw.get("journal", "")
        year = kw.get("year", "")

        if journal:
            parts = f"{authors}. {title}. {journal}. {year}"
            if kw.get("volume"):
                parts += f";{kw['volume']}"
            if kw.get("issue"):
                parts += f"({kw['issue']})"
            if kw.get("pages"):
                parts += f":{kw['pages']}"
            parts += "."
            return parts
        else:
            return f"{authors}. {title}. {kw.get('publisher', '')}; {year}."

    def _format_gbt7714(self, **kw) -> str:
        """GB/T 7714 format (Chinese national standard)."""
        authors = self._format_authors_first_last(kw["authors"])
        title = kw.get("title", "Untitled")
        journal = kw.get("journal", "")
        year = kw.get("year", "")

        if journal:
            parts = f"{authors}. {title}[J]. {journal}, {year}"
            if kw.get("volume"):
                parts += f", {kw['volume']}"
            if kw.get("issue"):
                parts += f"({kw['issue']})"
            if kw.get("pages"):
                parts += f": {kw['pages']}"
            parts += "."
            return parts
        else:
            return f"{authors}. {title}[M]. {kw.get('publisher', '')}, {year}."


def generate_citation(identifier: str, fmt: str = "apa7") -> str:
    """Convenience function to generate citation from DOI or ISBN."""
    generator = CitationGenerator()
    doi = extract_doi(identifier)
    if doi:
        return generator.generate_from_doi(doi, fmt)
    # Try ISBN
    cleaned = re.sub(r'[-\s]', '', identifier)
    if re.match(r'^\d{10}(\d{3})?$', cleaned):
        return generator.generate_from_isbn(identifier, fmt)
    return "Error: Could not identify DOI or ISBN in the provided identifier."
