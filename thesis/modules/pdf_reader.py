"""
PDF reader module.

Download PDFs from DOI/URL, extract text, parse sections using PyMuPDF.
"""

import os
import re
from typing import Optional, Dict, List, Tuple
from pathlib import Path

import requests

from thesis.config import PDF_DIR
from thesis.utils import clean_text


class PDFReader:
    """Read and extract text from PDF documents."""

    def __init__(self):
        self.pdf_dir = Path(PDF_DIR)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

    def download_pdf(self, url: str, filename: str = "") -> Optional[str]:
        """
        Download a PDF from URL.

        Args:
            url: URL to download PDF from
            filename: Local filename (auto-generated if empty)

        Returns:
            Local file path or None on failure
        """
        if not url:
            return None
        if not filename:
            filename = url.split("/")[-1][:100] or "paper.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        # Clean filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filepath = self.pdf_dir / filename

        if filepath.exists():
            return str(filepath)

        try:
            headers = {"User-Agent": "Mozilla/5.0 (ThesisMaster/1.0)"}
            resp = requests.get(url, headers=headers, timeout=30, stream=True)
            if resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                return str(filepath)
        except Exception as e:
            print(f"PDF download error: {e}")
        return None

    def extract_text(self, pdf_path: str, pages: List[int] = None) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to PDF file
            pages: Specific page numbers to extract (0-indexed). None for all.

        Returns:
            Extracted text as string
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            text_parts = []
            for i, page in enumerate(doc):
                if pages and i not in pages:
                    continue
                text = page.get_text()
                if text:
                    text_parts.append(text)
            doc.close()
            return "\n\n".join(text_parts)
        except ImportError:
            return self._extract_text_fallback(pdf_path)
        except Exception as e:
            return f"Error extracting text: {e}"

    def _extract_text_fallback(self, pdf_path: str) -> str:
        """Fallback text extraction using basic method."""
        try:
            with open(pdf_path, 'rb') as f:
                content = f.read()
            # Very basic text extraction - looks for text streams
            text_chunks = re.findall(rb'\(([^)]+)\)', content)
            text = b" ".join(text_chunks).decode('latin-1', errors='ignore')
            return clean_text(text)
        except Exception:
            return "Error: Could not extract text. Install PyMuPDF: pip install pymupdf"

    def parse_sections(self, pdf_path: str) -> Dict[str, str]:
        """
        Parse a PDF into common academic paper sections.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with section names as keys and content as values
        """
        text = self.extract_text(pdf_path)
        if not text or text.startswith("Error"):
            return {"full_text": text}

        sections = {
            "abstract": "",
            "introduction": "",
            "methods": "",
            "results": "",
            "discussion": "",
            "conclusion": "",
            "references": "",
            "full_text": text,
        }

        # Common section headers (case insensitive)
        section_patterns = [
            (r'(?i)\b(?:abstract)\b', "abstract"),
            (r'(?i)\b(?:1\.?\s*)?introduction\b', "introduction"),
            (r'(?i)\b(?:2\.?\s*)(?:methodology|methods|materials\s+and\s+methods)\b', "methods"),
            (r'(?i)\b(?:3\.?\s*)(?:results|findings)\b', "results"),
            (r'(?i)\b(?:4\.?\s*)(?:discussion)\b', "discussion"),
            (r'(?i)\b(?:5\.?\s*)?(?:conclusion|conclusions|concluding\s+remarks)\b', "conclusion"),
            (r'(?i)\b(?:references|bibliography|works?\s+cited)\b', "references"),
        ]

        # Find positions of each section header
        found_sections = []
        for pattern, name in section_patterns:
            match = re.search(pattern, text)
            if match:
                found_sections.append((match.start(), name))

        # Sort by position
        found_sections.sort()

        # Extract text between sections
        for i, (start, name) in enumerate(found_sections):
            if i + 1 < len(found_sections):
                end = found_sections[i + 1][0]
            else:
                end = len(text)
            content = text[start:end]
            # Remove the header itself
            content = re.sub(r'^[^\n]*\n', '', content, count=1)
            sections[name] = clean_text(content)

        # If no sections found, try to extract abstract from beginning
        if not sections["abstract"]:
            abstract_match = re.search(r'(?i)abstract[:\s]*(.*?)(?=\n\s*\n|\n\s*(?:1\.?\s*)?introduction)',
                                       text, re.DOTALL)
            if abstract_match:
                sections["abstract"] = clean_text(abstract_match.group(1))

        return sections

    def get_metadata(self, pdf_path: str) -> Dict[str, str]:
        """Extract PDF metadata."""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            meta = doc.metadata or {}
            doc.close()
            return {
                "title": meta.get("title", ""),
                "author": meta.get("author", ""),
                "subject": meta.get("subject", ""),
                "creator": meta.get("creator", ""),
                "producer": meta.get("producer", ""),
                "creationDate": meta.get("creationDate", ""),
                "page_count": str(doc.page_count if hasattr(doc, 'page_count') else 0),
            }
        except ImportError:
            return {"error": "PyMuPDF not installed"}
        except Exception as e:
            return {"error": str(e)}

    def get_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF."""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            count = doc.page_count
            doc.close()
            return count
        except Exception:
            return 0

    def extract_text_from_doi(self, doi: str) -> Tuple[Optional[str], str]:
        """
        Try to download and extract text from a DOI.

        Returns:
            Tuple of (file_path_or_None, extracted_text)
        """
        # Try Sci-Hub mirror (for educational use)
        sci_hub_urls = [
            f"https://sci-hub.se/{doi}",
            f"https://sci-hub.st/{doi}",
            f"https://sci-hub.ru/{doi}",
        ]

        for sci_hub_url in sci_hub_urls:
            try:
                resp = requests.get(sci_hub_url, timeout=15,
                                   headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    # Try to find PDF link in the page
                    pdf_match = re.search(r'(https?://[^\s"\']+\.pdf)', resp.text)
                    if pdf_match:
                        pdf_url = pdf_match.group(1)
                        filename = doi.replace("/", "_") + ".pdf"
                        path = self.download_pdf(pdf_url, filename)
                        if path:
                            text = self.extract_text(path)
                            return path, text
            except Exception:
                continue

        return None, "Could not download PDF. Try downloading manually."
