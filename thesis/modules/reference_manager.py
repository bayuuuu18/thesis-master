"""
Reference management module.

Store, organize, tag, and search references in SQLite.
Import from BibTeX, RIS, DOI. Export to BibTeX, RIS.
"""

import re
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

import requests

from thesis.database import Database
from thesis.utils import clean_text, parse_bibtex_entry, generate_cite_key


class ReferenceManager:
    """Manage academic references with SQLite backend."""

    def __init__(self):
        pass

    def add_reference(self, title: str, authors: str = "", year: int = None,
                      journal: str = "", volume: str = "", issue: str = "",
                      pages: str = "", doi: str = "", isbn: str = "",
                      url: str = "", abstract: str = "", bibtex: str = "",
                      tags: List[str] = None, notes: str = "",
                      pdf_path: str = "", source: str = "") -> int:
        """Add a new reference and return its ID."""
        data = {
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "doi": doi,
            "isbn": isbn,
            "url": url,
            "abstract": abstract,
            "bibtex": bibtex,
            "tags": json.dumps(tags or []),
            "notes": notes,
            "pdf_path": pdf_path,
            "source": source,
        }
        with Database() as db:
            return db.insert("references_table", data)

    def get_reference(self, ref_id: int) -> Optional[Dict]:
        """Get a reference by ID."""
        with Database() as db:
            ref = db.fetch_one("SELECT * FROM references_table WHERE id = ?", (ref_id,))
            if ref and ref.get("tags"):
                try:
                    ref["tags"] = json.loads(ref["tags"])
                except (json.JSONDecodeError, TypeError):
                    ref["tags"] = []
            return ref

    def update_reference(self, ref_id: int, **kwargs) -> int:
        """Update a reference by ID."""
        if "tags" in kwargs and isinstance(kwargs["tags"], list):
            kwargs["tags"] = json.dumps(kwargs["tags"])
        with Database() as db:
            return db.update("references_table", kwargs, "id = ?", (ref_id,))

    def delete_reference(self, ref_id: int) -> int:
        """Delete a reference by ID."""
        with Database() as db:
            return db.delete("references_table", "id = ?", (ref_id,))

    def list_references(self, search: str = "", tag: str = "",
                        year_from: int = None, year_to: int = None,
                        sort_by: str = "created_at", order: str = "DESC",
                        limit: int = 100, offset: int = 0) -> List[Dict]:
        """List references with optional filtering."""
        conditions = []
        params = []

        if search:
            conditions.append("(title LIKE ? OR authors LIKE ? OR abstract LIKE ?)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        if tag:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")

        if year_from:
            conditions.append("year >= ?")
            params.append(year_from)

        if year_to:
            conditions.append("year <= ?")
            params.append(year_to)

        where = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM references_table WHERE {where} ORDER BY {sort_by} {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with Database() as db:
            refs = db.fetch_all(query, tuple(params))
            for ref in refs:
                if ref.get("tags"):
                    try:
                        ref["tags"] = json.loads(ref["tags"])
                    except (json.JSONDecodeError, TypeError):
                        ref["tags"] = []
                else:
                    ref["tags"] = []
            return refs

    def count_references(self, search: str = "", tag: str = "") -> int:
        """Count references with optional filtering."""
        conditions = []
        params = []
        if search:
            conditions.append("(title LIKE ? OR authors LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")
        where = " AND ".join(conditions) if conditions else "1=1"
        with Database() as db:
            result = db.fetch_one(f"SELECT COUNT(*) as cnt FROM references_table WHERE {where}", tuple(params))
            return result["cnt"] if result else 0

    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        with Database() as db:
            refs = db.fetch_all("SELECT tags FROM references_table WHERE tags IS NOT NULL AND tags != '[]'")
            all_tags = set()
            for ref in refs:
                try:
                    tags = json.loads(ref["tags"])
                    all_tags.update(tags)
                except (json.JSONDecodeError, TypeError):
                    pass
            return sorted(all_tags)

    def import_from_bibtex(self, bibtex_content: str) -> List[int]:
        """Import references from BibTeX content. Returns list of inserted IDs."""
        ids = []
        # Split into individual entries
        entries = re.split(r'\n(?=@)', bibtex_content)
        for entry in entries:
            entry = entry.strip()
            if not entry or not entry.startswith('@'):
                continue
            parsed = parse_bibtex_entry(entry)
            if not parsed.get("title"):
                continue
            ref_id = self.add_reference(
                title=parsed.get("title", ""),
                authors=parsed.get("author", ""),
                year=int(parsed["year"]) if parsed.get("year") and parsed["year"].isdigit() else None,
                journal=parsed.get("journal", ""),
                volume=parsed.get("volume", ""),
                issue=parsed.get("number", ""),
                pages=parsed.get("pages", ""),
                doi=parsed.get("doi", ""),
                isbn=parsed.get("isbn", ""),
                url=parsed.get("url", ""),
                abstract=parsed.get("abstract", ""),
                bibtex=entry,
                source="bibtex_import",
            )
            ids.append(ref_id)
        return ids

    def import_from_ris(self, ris_content: str) -> List[int]:
        """Import references from RIS content. Returns list of inserted IDs."""
        ids = []
        entries = ris_content.split("\nER  -\n")
        for entry in entries:
            if not entry.strip():
                continue
            data = {}
            current_key = None
            for line in entry.split("\n"):
                if len(line) >= 2 and line[2:4] == "- ":
                    key = line[:2].strip()
                    value = line[4:].strip()
                    if key == "TI":
                        data["title"] = value
                    elif key == "AU":
                        data.setdefault("authors", []).append(value)
                    elif key == "PY":
                        try:
                            data["year"] = int(value[:4])
                        except (ValueError, IndexError):
                            pass
                    elif key == "JO":
                        data["journal"] = value
                    elif key == "VL":
                        data["volume"] = value
                    elif key == "IS":
                        data["issue"] = value
                    elif key == "SP":
                        data["pages"] = value
                    elif key == "DO":
                        data["doi"] = value
                    elif key == "UR":
                        data["url"] = value
                    elif key == "AB":
                        data["abstract"] = value

            if data.get("title"):
                ref_id = self.add_reference(
                    title=data.get("title", ""),
                    authors=", ".join(data.get("authors", [])),
                    year=data.get("year"),
                    journal=data.get("journal", ""),
                    volume=data.get("volume", ""),
                    issue=data.get("issue", ""),
                    pages=data.get("pages", ""),
                    doi=data.get("doi", ""),
                    url=data.get("url", ""),
                    abstract=data.get("abstract", ""),
                    source="ris_import",
                )
                ids.append(ref_id)
        return ids

    def import_from_doi(self, doi: str) -> Optional[int]:
        """Import a reference from DOI using CrossRef API."""
        try:
            url = f"https://api.crossref.org/works/{doi}"
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                return None
            item = resp.json().get("message", {})
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
            year = None
            date_parts = item.get("published-print", {}).get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]
            container = item.get("container-title", [])
            journal = container[0] if container else ""

            return self.add_reference(
                title=title,
                authors=", ".join(authors_list),
                year=year,
                journal=journal,
                volume=item.get("volume", ""),
                issue=item.get("issue", ""),
                pages=item.get("page", ""),
                doi=doi,
                url=item.get("URL", ""),
                source="doi_import",
            )
        except Exception as e:
            print(f"DOI import error: {e}")
            return None

    def export_bibtex(self, ref_ids: List[int] = None) -> str:
        """Export references to BibTeX format."""
        refs = []
        if ref_ids:
            for rid in ref_ids:
                ref = self.get_reference(rid)
                if ref:
                    refs.append(ref)
        else:
            refs = self.list_references(limit=10000)

        entries = []
        for ref in refs:
            if ref.get("bibtex"):
                entries.append(ref["bibtex"])
                continue
            cite_key = generate_cite_key(ref.get("authors", ""), ref.get("year", 0), ref.get("title", ""))
            entry = f"@article{{{cite_key},\n"
            entry += f'  title = {{{ref.get("title", "")}}},\n'
            entry += f'  author = {{{ref.get("authors", "")}}},\n'
            if ref.get("year"):
                entry += f'  year = {{{ref["year"]}}},\n'
            if ref.get("journal"):
                entry += f'  journal = {{{ref["journal"]}}},\n'
            if ref.get("volume"):
                entry += f'  volume = {{{ref["volume"]}}},\n'
            if ref.get("issue"):
                entry += f'  number = {{{ref["issue"]}}},\n'
            if ref.get("pages"):
                entry += f'  pages = {{{ref["pages"]}}},\n'
            if ref.get("doi"):
                entry += f'  doi = {{{ref["doi"]}}},\n'
            if ref.get("url"):
                entry += f'  url = {{{ref["url"]}}},\n'
            entry = entry.rstrip(",\n") + "\n}"
            entries.append(entry)
        return "\n\n".join(entries)

    def export_ris(self, ref_ids: List[int] = None) -> str:
        """Export references to RIS format."""
        refs = []
        if ref_ids:
            for rid in ref_ids:
                ref = self.get_reference(rid)
                if ref:
                    refs.append(ref)
        else:
            refs = self.list_references(limit=10000)

        entries = []
        for ref in refs:
            lines = ["TY  - JOUR"]
            lines.append(f"TI  - {ref.get('title', '')}")
            for author in ref.get("authors", "").split(","):
                author = author.strip()
                if author:
                    lines.append(f"AU  - {author}")
            if ref.get("year"):
                lines.append(f"PY  - {ref['year']}")
            if ref.get("journal"):
                lines.append(f"JO  - {ref['journal']}")
            if ref.get("volume"):
                lines.append(f"VL  - {ref['volume']}")
            if ref.get("issue"):
                lines.append(f"IS  - {ref['issue']}")
            if ref.get("pages"):
                lines.append(f"SP  - {ref['pages']}")
            if ref.get("doi"):
                lines.append(f"DO  - {ref['doi']}")
            if ref.get("url"):
                lines.append(f"UR  - {ref['url']}")
            if ref.get("abstract"):
                lines.append(f"AB  - {ref['abstract']}")
            lines.append("ER  -\n")
            entries.append("\n".join(lines))
        return "\n".join(entries)
