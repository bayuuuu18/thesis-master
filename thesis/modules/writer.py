"""
Markdown-based writing environment.

Chapter management for Indonesian thesis (Bab 1-5),
auto-generate table of contents, track word count.
"""

import re
from typing import List, Dict, Optional
from datetime import datetime

from thesis.database import Database
from thesis.utils import count_words, sanitize_filename


# Default Indonesian thesis template chapters
DEFAULT_CHAPTERS = [
    {"number": 1, "title": "PENDAHULUAN", "content": """# BAB I PENDAHULUAN

## 1.1 Latar Belakang Masalah
[Isi latar belakang masalah penelitian di sini]

## 1.2 Rumusan Masalah
[Berdasarkan latar belakang di atas, rumusan masalah dalam penelitian ini adalah:]
1. [Rumusan masalah 1]
2. [Rumusan masalah 2]
3. [Rumusan masalah 3]

## 1.3 Tujuan Penelitian
[Berdasarkan rumusan masalah, tujuan penelitian ini adalah:]
1. [Tujuan 1]
2. [Tujuan 2]
3. [Tujuan 3]

## 1.4 Manfaat Penelitian
### 1.4.1 Manfaat Teoritis
[Manfaat teoritis penelitian]

### 1.4.2 Manfaat Praktis
[Manfaat praktis penelitian]

## 1.5 Sistematika Penulisan
[Penulisan skripsi ini terdiri dari 5 bab sebagai berikut:]
"""},
    {"number": 2, "title": "TINJAUAN PUSTAKA", "content": """# BAB II TINJAUAN PUSTAKA

## 2.1 Landasan Teori
### 2.1.1 [Teori 1]
[Deskripsi teori 1]

### 2.1.2 [Teori 2]
[Deskripsi teori 2]

## 2.2 Penelitian Terdahulu
[Tabel penelitian terdahulu]

| No | Peneliti | Tahun | Judul | Hasil |
|----|----------|-------|-------|-------|
| 1  |          |       |       |       |

## 2.3 Kerangka Pemikiran
[Kerangka pemikiran / framework penelitian]

## 2.4 Hipotesis
[Berdasarkan tinjauan pustaka, hipotesis penelitian ini adalah:]
"""},
    {"number": 3, "title": "METODOLOGI PENELITIAN", "content": """# BAB III METODOLOGI PENELITIAN

## 3.1 Metode Penelitian
[Jenis dan metode penelitian yang digunakan]

## 3.1 Tempat dan Waktu Penelitian
### 3.1.1 Tempat Penelitian
[Lokasi penelitian]

### 3.1.2 Waktu Penelitian
[Jadwal penelitian]

## 3.2 Populasi dan Sampel
### 3.2.1 Populasi
[Populasi penelitian]

### 3.2.2 Sampel
[Sampel dan teknik sampling]

## 3.3 Teknik Pengumpulan Data
[Metode pengumpulan data: observasi, wawancara, kuesioner, dll.]

## 3.4 Teknik Analisis Data
[Metode analisis data yang digunakan]

## 3.5 Instrumen Penelitian
[Deskripsi instrumen penelitian]
"""},
    {"number": 4, "title": "HASIL DAN PEMBAHASAN", "content": """# BAB IV HASIL DAN PEMBAHASAN

## 4.1 Gambaran Umum Objek Penelitian
[Deskripsi objek/lokasi penelitian]

## 4.2 Hasil Penelitian
### 4.2.1 [Sub-bagian 1]
[Hasil analisis data]

### 4.2.2 [Sub-bagian 2]
[Hasil analisis data]

## 4.3 Pembahasan
### 4.3.1 [Topik pembahasan 1]
[Pembahasan hasil penelitian dengan teori]

### 4.3.2 [Topik pembahasan 2]
[Pembahasan hasil penelitian dengan teori]
"""},
    {"number": 5, "title": "KESIMPULAN DAN SARAN", "content": """# BAB V KESIMPULAN DAN SARAN

## 5.1 Kesimpulan
[Berdasarkan hasil penelitian dan pembahasan, dapat disimpulkan bahwa:]
1. [Kesimpulan 1]
2. [Kesimpulan 2]
3. [Kesimpulan 3]

## 5.2 Saran
[Berdasarkan kesimpulan di atas, peneliti memberikan saran:]
### 5.2.1 Saran untuk Praktisi
[Saran untuk praktisi/industri]

### 5.2.2 Saran untuk Penelitian Selanjutnya
[Saran untuk penelitian berikutnya]
"""},
]


class ThesisWriter:
    """Markdown-based thesis writing environment."""

    def __init__(self):
        pass

    def init_chapters(self, template: str = "indonesian") -> List[int]:
        """Initialize thesis chapters from template."""
        ids = []
        with Database() as db:
            # Check if chapters already exist
            existing = db.fetch_all("SELECT COUNT(*) as cnt FROM chapters")
            if existing and existing[0]["cnt"] > 0:
                return []  # Don't overwrite

            for ch in DEFAULT_CHAPTERS:
                word_count = count_words(ch["content"])
                ch_id = db.insert("chapters", {
                    "title": ch["title"],
                    "chapter_number": ch["number"],
                    "content": ch["content"],
                    "status": "draft",
                    "word_count": word_count,
                    "sort_order": ch["number"],
                })
                ids.append(ch_id)
        return ids

    def get_chapters(self) -> List[Dict]:
        """Get all chapters ordered by number."""
        with Database() as db:
            return db.fetch_all(
                "SELECT * FROM chapters ORDER BY sort_order, chapter_number"
            )

    def get_chapter(self, chapter_id: int) -> Optional[Dict]:
        """Get a specific chapter."""
        with Database() as db:
            return db.fetch_one("SELECT * FROM chapters WHERE id = ?", (chapter_id,))

    def get_chapter_by_number(self, number: int) -> Optional[Dict]:
        """Get chapter by number."""
        with Database() as db:
            return db.fetch_one(
                "SELECT * FROM chapters WHERE chapter_number = ?", (number,)
            )

    def update_chapter(self, chapter_id: int, content: str = None,
                       title: str = None, status: str = None,
                       deadline: str = None) -> int:
        """Update chapter content and/or metadata."""
        data = {}
        if content is not None:
            data["content"] = content
            data["word_count"] = count_words(content)
        if title is not None:
            data["title"] = title
        if status is not None:
            data["status"] = status
        if deadline is not None:
            data["deadline"] = deadline

        if not data:
            return 0

        with Database() as db:
            return db.update("chapters", data, "id = ?", (chapter_id,))

    def add_chapter(self, title: str, number: int, content: str = "") -> int:
        """Add a new chapter."""
        with Database() as db:
            return db.insert("chapters", {
                "title": title,
                "chapter_number": number,
                "content": content,
                "status": "draft",
                "word_count": count_words(content),
                "sort_order": number,
            })

    def delete_chapter(self, chapter_id: int) -> int:
        """Delete a chapter."""
        with Database() as db:
            return db.delete("chapters", "id = ?", (chapter_id,))

    def generate_toc(self) -> str:
        """Generate table of contents from chapters."""
        chapters = self.get_chapters()
        toc_lines = ["# DAFTAR ISI\n"]
        for ch in chapters:
            number = ch["chapter_number"]
            title = ch["title"]
            toc_lines.append(f"BAB {number}  {title}  {'.' * (50 - len(title))}  ...")
            # Parse sub-sections from content
            if ch.get("content"):
                sections = re.findall(r'^##\s+(.+)$', ch["content"], re.MULTILINE)
                for section in sections:
                    toc_lines.append(f"    {section}  {'.' * (40 - len(section))}  ...")
            toc_lines.append("")
        return "\n".join(toc_lines)

    def generate_lof(self) -> str:
        """Generate list of figures (placeholder)."""
        return "# DAFTAR GAMBAR\n\n[Daftar gambar akan di-generate otomatis saat export]\n"

    def generate_lot(self) -> str:
        """Generate list of tables (placeholder)."""
        return "# DAFTAR TABEL\n\n[Daftar tabel akan di-generate otomatis saat export]\n"

    def get_word_count_summary(self) -> Dict:
        """Get word count summary for all chapters."""
        chapters = self.get_chapters()
        total = 0
        summary = []
        for ch in chapters:
            wc = ch.get("word_count", 0)
            total += wc
            summary.append({
                "chapter_number": ch["chapter_number"],
                "title": ch["title"],
                "word_count": wc,
                "status": ch.get("status", "draft"),
            })
        return {
            "chapters": summary,
            "total_words": total,
        }

    def get_full_thesis(self, include_toc: bool = True) -> str:
        """Get the full thesis as a single markdown document."""
        chapters = self.get_chapters()
        parts = []

        # Title page info
        parts.append("<!-- Thesis Master - Full Document -->\n")

        if include_toc:
            parts.append(self.generate_toc())
            parts.append("\n---\n")

        for ch in chapters:
            if ch.get("content"):
                parts.append(ch["content"])
                parts.append("\n\n---\n\n")

        return "\n".join(parts)

    def get_progress(self) -> Dict:
        """Get overall thesis progress."""
        chapters = self.get_chapters()
        total = len(chapters)
        if total == 0:
            return {"percentage": 0, "total": 0, "completed": 0, "in_progress": 0}

        completed = sum(1 for ch in chapters if ch.get("status") == "final")
        in_progress = sum(1 for ch in chapters if ch.get("status") in ("draft", "review"))

        percentage = int(completed / total * 100) if total > 0 else 0

        return {
            "percentage": percentage,
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "outline": sum(1 for ch in chapters if ch.get("status") == "outline"),
            "draft": sum(1 for ch in chapters if ch.get("status") == "draft"),
            "review": sum(1 for ch in chapters if ch.get("status") == "review"),
            "final": completed,
        }
