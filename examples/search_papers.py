"""Example: Search papers and save as references."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thesis.config import Config
from thesis.database import ThesisDatabase
from thesis.modules.searcher import PaperSearcher
from thesis.modules.reference_manager import ReferenceManager

cfg = Config()
db = ThesisDatabase('thesis_example.db')
searcher = PaperSearcher()
ref_mgr = ReferenceManager(db)

# Search
query = "deep learning medical image segmentation"
print(f"🔍 Searching: {query}")
results = searcher.search(query, source='arxiv', max_results=5)

# Display and save
for i, paper in enumerate(results, 1):
    print(f"\n{i}. {paper.get('title')}")
    print(f"   Authors: {paper.get('authors', 'N/A')}")
    print(f"   Year: {paper.get('year', 'N/A')}")

    ref_mgr.add_reference(
        title=paper.get('title', ''),
        authors=paper.get('authors', ''),
        year=paper.get('year', ''),
        doi=paper.get('doi', ''),
        journal=paper.get('source', 'arXiv')
    )

print(f"\n✅ {len(results)} referensi disimpan!")
