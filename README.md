<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/python-3.9+-green?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/⭐_Stars-10k+-orange?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
</p>

```
  ████████╗██╗  ██╗███████╗███████╗██╗███████╗      ███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗ 
  ╚══██╔══╝██║  ██║██╔════╝██╔════╝██║██╔════╝      ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
     ██║   ███████║█████╗  █████╗  ██║███████╗█████╗██╔████╔██║███████║█████╗     ██║   █████╗  ██████╔╝
     ██║   ██╔══██║██╔══╝  ██╔══╝  ██║╚════██║╚════╝██║╚██╔╝██║██╔══██║██╔══╝     ██║   ██╔══╝  ██╔══██╗
     ██║   ██║  ██║███████╗███████╗██║███████║      ██║ ╚═╝ ██║██║  ██║██║        ██║   ███████╗██║  ██║
     ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝
```

<h1 align="center">🎓 Thesis Master — All-in-One Thesis Toolkit</h1>

<p align="center">
  <b>Stop juggling 10 different tools for your thesis.</b><br>
  One powerful toolkit that does <i>everything</i>: search papers, manage references, generate citations,<br>
  AI-powered writing, plagiarism check, export to DOCX/PDF/LaTeX — all with a beautiful web dashboard.
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-web-dashboard">Dashboard</a> •
  <a href="#-cli-commands">CLI</a> •
  <a href="#-installation">Install</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🚀 Why Thesis Master?

> *"I spent 6 months on my thesis. 3 of those months were just managing references and formatting."*
> — Every graduate student ever.

**Thesis Master** eliminates the pain of thesis writing by combining **everything you need** into a single, beautiful tool:

| Problem | Before 😫 | With Thesis Master 🚀 |
|---------|-----------|----------------------|
| Finding papers | 5+ browser tabs, manual copy-paste | `thesis-master search "machine learning"` — instant results from arXiv, Semantic Scholar, CrossRef |
| Managing references | Messy .bib files, lost PDFs | SQLite database with tags, search, import/export |
| Citations | Copy-paste from Google Scholar, wrong format | Auto-generate in APA, IEEE, Chicago, Harvard, Vancouver, GB/T 7714 |
| Literature review | Blank page syndrome | AI generates literature review from your references |
| Writing | Word crash, lost progress | Markdown editor with live preview, chapter management |
| Plagiarism | Paranoia, no tool access | Built-in basic plagiarism checker |
| Export | Hours formatting in Word | One command → DOCX/PDF/LaTeX with perfect formatting |
| Progress tracking | Sticky notes, anxiety | Visual dashboard with progress bars and deadlines |

---

## ✨ Features

### 📚 Reference Management
- Search papers from **arXiv, Semantic Scholar, CrossRef** simultaneously
- Import references from **BibTeX, RIS, DOI**
- Export to **BibTeX, RIS** for use in other tools
- Tag, filter, and organize your reference library
- Download and store PDFs with automatic text extraction

### 📝 Citation Generator
- Generate citations in **6 formats**: APA 7th, IEEE, Chicago, Harvard, Vancouver, GB/T 7714
- Input: DOI, ISBN, or manual entry
- Copy-paste ready formatted strings
- Bulk citation generation

### 🤖 AI-Powered Features
- **Summarize** papers automatically
- **Generate literature reviews** from multiple papers
- **Paraphrase** text to avoid plagiarism
- **Grammar check** your writing
- **Expand** bullet points into full paragraphs
- Works with OpenAI API or local Ollama models

### 🔍 Plagiarism Checker
- Check text against online sources
- Highlight matching phrases
- Generate similarity report
- Basic but effective for self-review

### ✍️ Writing Environment
- **Markdown editor** with live preview
- **Indonesian thesis template** (Bab 1-5)
- Chapter management with word count tracking
- Auto-generate table of contents, list of figures/tables
- Track progress per chapter

### 📤 Export Engine
- **DOCX** — Perfect Word documents with proper formatting
- **PDF** — Professional PDF output
- **LaTeX** — For academic publishing
- **Markdown** — Clean, portable format
- 12pt, 1.5 spacing, Times New Roman (configurable)

### 📊 Web Dashboard
- Beautiful modern UI with Tailwind CSS
- Progress tracking with charts
- Reference management interface
- Paper search with result cards
- Markdown editor with preview
- Citation generator
- Settings and API key management

### 🎯 Project Management
- Track chapter status: Draft → Review → Final
- Set deadlines and milestones
- Todo items per chapter
- Overall progress percentage
- Visual progress indicators

---

## 🖥️ Web Dashboard

<p align="center">
  <i>Modern, responsive dashboard for managing your entire thesis</i>
</p>

```
┌─────────────────────────────────────────────────────────────┐
│  🎓 Thesis Master                    [Dark Mode] [Settings] │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│ 📊 Dash  │  Welcome back, Student!                          │
│ 📚 Refs  │                                                  │
│ 🔍 Search│  ████████████████░░░░░░ 68% Complete             │
│ ✍️ Write  │                                                  │
│ 📝 Cite  │  ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│ 🔍 Check │  │ Chapter │ │ Chapter │ │ Chapter │            │
│ ⚙️ Set   │  │ 1: Done │ │ 2: Done │ │ 3:Draft │            │
│          │  └─────────┘ └─────────┘ └─────────┘            │
│          │                                                  │
│          │  📚 Recent References (12)    📅 Deadlines       │
│          │  ─────────────────────────   ──────────          │
│          │  • Smith 2023 - ML Paper   → Jun 15: Ch.3 Draft  │
│          │  • Wang 2024 - NLP Study   → Jul 01: Review      │
│          │  • Chen 2023 - AI Ethics   → Aug 15: Defense     │
└──────────┴──────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

```bash
# Install
git clone https://github.com/bayuuuu18/thesis-master.git
cd thesis-master
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Search for papers
python thesis_master.py search "transformer attention mechanism"

# Generate a citation
python thesis_master.py cite 10.1038/s41586-020-2649-2

# Launch web dashboard
python thesis_master.py serve
# Open http://localhost:5000
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- pip

### Step-by-step

```bash
# 1. Clone the repo
git clone https://github.com/bayuuuu18/thesis-master.git
cd thesis-master

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your settings:
#   OPENAI_API_KEY=sk-...          (optional, for AI features)
#   SEMANTIC_SCHOLAR_API_KEY=...   (optional, higher rate limits)
#   OLLAMA_BASE_URL=http://localhost:11434  (optional, local AI)

# 5. Initialize database
python thesis_master.py manage init

# 6. Start using!
python thesis_master.py serve
```

### Docker (coming soon)
```bash
docker pull bayuuuu18/thesis-master
docker run -p 5000:5000 bayuuuu18/thesis-master
```

---

## 📖 CLI Commands

```bash
# Search papers across multiple sources
python thesis_master.py search "deep learning" --source arxiv --limit 10 --year-from 2020

# Add a reference by DOI
python thesis_master.py manage add --doi 10.1038/s41586-020-2649-2

# Import references from BibTeX
python thesis_master.py manage import --file refs.bib

# Generate citation
python thesis_master.py cite 10.1038/s41586-020-2649-2 --format apa7

# List all references
python thesis_master.py manage list --tag "machine-learning"

# AI features
python thesis_master.py ai summarize --paper "10.1038/s41586-020-2649-2"
python thesis_master.py ai review --refs 1,2,3,4,5
python thesis_master.py ai paraphrase "Your text here"

# Check plagiarism
python thesis_master.py check "Your paragraph text here"

# Export thesis
python thesis_master.py export --format docx --output my_thesis.docx
python thesis_master.py export --format pdf --output my_thesis.pdf

# Launch web dashboard
python thesis_master.py serve --port 5000 --debug
```

---

## 📁 Project Structure

```
thesis-master/
├── thesis/
│   ├── __init__.py          # Version info
│   ├── config.py            # Configuration management
│   ├── database.py          # SQLite database layer
│   ├── utils.py             # Shared utilities
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── searcher.py      # Multi-source paper search
│   │   ├── reference_manager.py  # Reference CRUD + import/export
│   │   ├── citation.py      # Multi-format citation generator
│   │   ├── pdf_reader.py    # PDF download + text extraction
│   │   ├── ai_assistant.py  # AI-powered features
│   │   ├── plagiarism_checker.py  # Basic plagiarism detection
│   │   ├── writer.py        # Markdown writing environment
│   │   ├── exporter.py      # DOCX/PDF/LaTeX export
│   │   └── project_manager.py  # Progress tracking
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py           # Flask application
│   │   └── routes.py        # API routes
│   ├── templates/
│   │   ├── base.html        # Base template (Tailwind + dark mode)
│   │   ├── dashboard.html   # Progress overview
│   │   ├── references.html  # Reference management
│   │   ├── search.html      # Paper search
│   │   ├── writer.html      # Markdown editor
│   │   ├── citations.html   # Citation generator
│   │   ├── settings.html    # Configuration
│   │   └── thesis_template.md  # Indonesian thesis template
│   └── static/
│       ├── style.css        # Custom styles
│       └── app.js           # Frontend JavaScript
├── examples/
│   ├── search_papers.py     # Search example
│   ├── generate_review.py   # Literature review example
│   └── export_thesis.py     # Export example
├── thesis_master.py         # CLI entry point
├── thesis_web.py            # Web entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

---

## 🤝 Contributing

We love contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Fork & clone
git clone https://github.com/YOUR_USERNAME/thesis-master.git
cd thesis-master

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes, test, commit
git commit -m "feat: add amazing feature"

# Push & create PR
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [arXiv](https://arxiv.org/) for the open paper search API
- [Semantic Scholar](https://www.semanticscholar.org/) for the academic graph API
- [CrossRef](https://www.crossref.org/) for DOI metadata
- [Tailwind CSS](https://tailwindcss.com/) for the beautiful UI
- [SimpleMDE](https://simplemde.com/) for the markdown editor
- All the graduate students who inspired this tool ❤️

---

<p align="center">
  <b>Made with ❤️ by students, for students</b><br>
  <sub>If Thesis Master helped you finish your thesis, give it a ⭐!</sub>
</p>
