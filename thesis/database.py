"""
Database layer for Thesis Master.

SQLite database for storing references, notes, chapters, and citations.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from thesis.config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database() -> None:
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS references_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT,
            year INTEGER,
            journal TEXT,
            volume TEXT,
            issue TEXT,
            pages TEXT,
            doi TEXT UNIQUE,
            isbn TEXT,
            url TEXT,
            abstract TEXT,
            bibtex TEXT,
            tags TEXT DEFAULT '[]',
            notes TEXT,
            pdf_path TEXT,
            source TEXT,
            citation_format TEXT,
            citation_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_id INTEGER,
            chapter_id INTEGER,
            content TEXT NOT NULL,
            note_type TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reference_id) REFERENCES references_table(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_id INTEGER,
            citation_text TEXT NOT NULL,
            format TEXT NOT NULL,
            in_text_citation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reference_id) REFERENCES references_table(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_refs_doi ON references_table(doi);
        CREATE INDEX IF NOT EXISTS idx_refs_year ON references_table(year);
        CREATE INDEX IF NOT EXISTS idx_refs_title ON references_table(title);
    """)

    conn.commit()
    conn.close()


class Database:
    """Database helper class for common operations."""

    def __init__(self):
        self.conn = get_connection()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        return self.conn.execute(query, params)

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch a single row as dictionary."""
        row = self.conn.execute(query, params).fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows as list of dictionaries."""
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def insert(self, table: str, data: dict) -> int:
        """Insert a row and return its ID."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.conn.execute(query, tuple(data.values()))
        self.conn.commit()
        return cursor.lastrowid

    def update(self, table: str, data: dict, where: str, params: tuple) -> int:
        """Update rows and return count of affected rows."""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE {where}"
        values = tuple(data.values()) + params
        cursor = self.conn.execute(query, values)
        self.conn.commit()
        return cursor.rowcount

    def delete(self, table: str, where: str, params: tuple) -> int:
        """Delete rows and return count of affected rows."""
        query = f"DELETE FROM {table} WHERE {where}"
        cursor = self.conn.execute(query, params)
        self.conn.commit()
        return cursor.rowcount


# Initialize database on import
init_database()
