"""Example: Generate literature review from saved references."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thesis.config import Config
from thesis.database import ThesisDatabase
from thesis.modules.reference_manager import ReferenceManager
from thesis.modules.ai_assistant import AIAssistant

cfg = Config()
db = ThesisDatabase('thesis_example.db')
ref_mgr = ReferenceManager(db)
ai = AIAssistant(cfg)

refs = ref_mgr.list_references()
topic = "deep learning in medical imaging"

print(f"📚 Generating literature review on: {topic}")
print(f"   Using {len(refs)} references\n")

review = ai.generate_literature_review(topic, refs[:10])
print(review)

with open('literature_review.md', 'w') as f:
    f.write(review)
print("\n✅ Saved to literature_review.md")
