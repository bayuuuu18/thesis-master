"""Example: Export thesis to DOCX."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thesis.config import Config
from thesis.database import ThesisDatabase
from thesis.modules.project_manager import ProjectManager
from thesis.modules.exporter import ThesisExporter

cfg = Config()
db = ThesisDatabase('thesis_example.db')
pm = ProjectManager(db)
exporter = ThesisExporter(db)

# Init chapters if needed
pm.init_default_chapters()

metadata = {
    'title': 'Analisis Implementasi Machine Learning untuk Deteksi Penyakit',
    'author': 'Muhammad Bayu Dharma Trinanda',
    'nim': '20210001',
    'university': 'Universitas Contoh',
    'year': 2026
}

print("📄 Exporting to DOCX...")
path = exporter.export_docx('skripsi.docx', metadata)
print(f"✅ Exported: {path}")

print("\n📄 Exporting to Markdown...")
path = exporter.export_markdown('skripsi.md', metadata)
print(f"✅ Exported: {path}")

print("\n📄 Exporting to BibTeX...")
path = exporter.export_bibtex('references.bib')
print(f"✅ Exported: {path}")
