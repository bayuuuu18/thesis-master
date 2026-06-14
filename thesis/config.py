"""
Configuration management for Thesis Master.

Loads settings from environment variables and .env files with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
PDF_DIR = DATA_DIR / "pdfs"

# Ensure directories exist
for d in [DATA_DIR, EXPORTS_DIR, PDF_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    """Load environment variables from .env file."""
    if load_dotenv:
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            load_dotenv(env_file)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default."""
    load_env()
    return os.environ.get(key, default)


# ─── Database ────────────────────────────────────────────────────
DATABASE_PATH = str(DATA_DIR / "thesis_master.db")

# ─── API Keys ────────────────────────────────────────────────────
def get_openai_key() -> str:
    return get_env("OPENAI_API_KEY", "") or ""

def get_semantic_scholar_key() -> str:
    return get_env("SEMANTIC_SCHOLAR_API_KEY", "") or ""

# ─── AI Settings ─────────────────────────────────────────────────
AI_PROVIDER = get_env("AI_PROVIDER", "openai") or "openai"
OPENAI_MODEL = get_env("OPENAI_MODEL", "gpt-3.5-turbo") or "gpt-3.5-turbo"
OLLAMA_BASE_URL = get_env("OLLAMA_BASE_URL", "http://localhost:11434") or "http://localhost:11434"
OLLAMA_MODEL = get_env("OLLAMA_MODEL", "llama2") or "llama2"
AI_MAX_TOKENS = int(get_env("AI_MAX_TOKENS", "2000") or "2000")
AI_TEMPERATURE = float(get_env("AI_TEMPERATURE", "0.7") or "0.7")

# ─── Search Settings ────────────────────────────────────────────
SEARCH_DEFAULT_LIMIT = int(get_env("SEARCH_DEFAULT_LIMIT", "20") or "20")
SEARCH_TIMEOUT = int(get_env("SEARCH_TIMEOUT", "30") or "30")

# ─── Export Settings ────────────────────────────────────────────
EXPORT_FONT = get_env("EXPORT_FONT", "Times New Roman") or "Times New Roman"
EXPORT_FONT_SIZE = int(get_env("EXPORT_FONT_SIZE", "12") or "12")
EXPORT_LINE_SPACING = float(get_env("EXPORT_LINE_SPACING", "1.5") or "1.5")

# ─── Thesis Info ────────────────────────────────────────────────
THESIS_TITLE = get_env("THESIS_TITLE", "") or ""
THESIS_AUTHOR = get_env("THESIS_AUTHOR", "") or ""
THESIS_UNIVERSITY = get_env("THESIS_UNIVERSITY", "") or ""
THESIS_YEAR = get_env("THESIS_YEAR", "2026") or "2026"

# ─── Web Settings ───────────────────────────────────────────────
WEB_HOST = get_env("WEB_HOST", "0.0.0.0") or "0.0.0.0"
WEB_PORT = int(get_env("WEB_PORT", "5000") or "5000")
WEB_DEBUG = (get_env("WEB_DEBUG", "false") or "false").lower() == "true"
SECRET_KEY = get_env("SECRET_KEY", "thesis-master-secret-change-me") or "thesis-master-secret-change-me"


def get_config() -> dict:
    """Return full configuration as dictionary."""
    load_env()
    return {
        "database_path": DATABASE_PATH,
        "data_dir": str(DATA_DIR),
        "exports_dir": str(EXPORTS_DIR),
        "pdf_dir": str(PDF_DIR),
        "openai_api_key": get_openai_key(),
        "semantic_scholar_api_key": get_semantic_scholar_key(),
        "ai_provider": AI_PROVIDER,
        "openai_model": OPENAI_MODEL,
        "ollama_base_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "ai_max_tokens": AI_MAX_TOKENS,
        "ai_temperature": AI_TEMPERATURE,
        "search_default_limit": SEARCH_DEFAULT_LIMIT,
        "search_timeout": SEARCH_TIMEOUT,
        "export_font": EXPORT_FONT,
        "export_font_size": EXPORT_FONT_SIZE,
        "export_line_spacing": EXPORT_LINE_SPACING,
        "thesis_title": THESIS_TITLE,
        "thesis_author": THESIS_AUTHOR,
        "thesis_university": THESIS_UNIVERSITY,
        "thesis_year": THESIS_YEAR,
        "web_host": WEB_HOST,
        "web_port": WEB_PORT,
        "web_debug": WEB_DEBUG,
        "secret_key": SECRET_KEY,
    }


def update_config(updates: dict) -> None:
    """Update environment variables from a dictionary."""
    for key, value in updates.items():
        env_key = key.upper()
        os.environ[env_key] = str(value)
