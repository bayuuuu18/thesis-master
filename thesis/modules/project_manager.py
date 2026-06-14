"""Project management for thesis progress tracking."""

import sqlite3
from datetime import datetime, timedelta


class ProjectManager:
    """Track thesis progress, chapters, milestones, and deadlines."""

    def __init__(self, db):
        self.db = db
        self._init_tables()

    def _init_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_number INTEGER,
                title TEXT,
                content TEXT DEFAULT '',
                status TEXT DEFAULT 'draft',
                word_count INTEGER DEFAULT 0,
                target_words INTEGER DEFAULT 5000,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT DEFAULT '',
                due_date DATE,
                completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                priority TEXT DEFAULT 'medium',
                due_date DATE,
                done INTEGER DEFAULT 0,
                chapter_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()

    # --- Chapters ---
    def add_chapter(self, number: int, title: str, target_words: int = 5000) -> int:
        cur = self.db.execute(
            "INSERT INTO chapters (chapter_number, title, target_words) VALUES (?, ?, ?)",
            (number, title, target_words)
        )
        self.db.commit()
        return cur.lastrowid

    def update_chapter(self, chapter_id: int, **kwargs):
        allowed = {'title', 'content', 'status', 'notes', 'target_words'}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if 'content' in updates:
            updates['word_count'] = len(updates['content'].split())
            updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [chapter_id]
        self.db.execute(f"UPDATE chapters SET {set_clause} WHERE id=?", values)
        self.db.commit()

    def get_chapters(self) -> list:
        return self.db.execute("SELECT * FROM chapters ORDER BY chapter_number").fetchall()

    def get_chapter(self, chapter_id: int):
        return self.db.execute("SELECT * FROM chapters WHERE id=?", (chapter_id,)).fetchone()

    def delete_chapter(self, chapter_id: int):
        self.db.execute("DELETE FROM chapters WHERE id=?", (chapter_id,))
        self.db.commit()

    # --- Milestones ---
    def add_milestone(self, title: str, due_date: str, description: str = '') -> int:
        cur = self.db.execute(
            "INSERT INTO milestones (title, description, due_date) VALUES (?, ?, ?)",
            (title, description, due_date)
        )
        self.db.commit()
        return cur.lastrowid

    def complete_milestone(self, milestone_id: int):
        self.db.execute(
            "UPDATE milestones SET completed=1, completed_at=? WHERE id=?",
            (datetime.now().isoformat(), milestone_id)
        )
        self.db.commit()

    def get_milestones(self, pending_only: bool = False) -> list:
        if pending_only:
            return self.db.execute(
                "SELECT * FROM milestones WHERE completed=0 ORDER BY due_date"
            ).fetchall()
        return self.db.execute("SELECT * FROM milestones ORDER BY due_date").fetchall()

    # --- Todos ---
    def add_todo(self, task: str, priority: str = 'medium', due_date: str = None, chapter_id: int = None) -> int:
        cur = self.db.execute(
            "INSERT INTO todos (task, priority, due_date, chapter_id) VALUES (?, ?, ?, ?)",
            (task, priority, due_date, chapter_id)
        )
        self.db.commit()
        return cur.lastrowid

    def complete_todo(self, todo_id: int):
        self.db.execute("UPDATE todos SET done=1 WHERE id=?", (todo_id,))
        self.db.commit()

    def get_todos(self, pending_only: bool = True) -> list:
        if pending_only:
            return self.db.execute("SELECT * FROM todos WHERE done=0 ORDER BY priority, due_date").fetchall()
        return self.db.execute("SELECT * FROM todos ORDER BY done, priority").fetchall()

    def delete_todo(self, todo_id: int):
        self.db.execute("DELETE FROM todos WHERE id=?", (todo_id,))
        self.db.commit()

    # --- Progress ---
    def get_progress(self) -> dict:
        chapters = self.get_chapters()
        total_words = sum(c['word_count'] for c in chapters)
        target_words = sum(c['target_words'] for c in chapters)
        completed = sum(1 for c in chapters if c['status'] == 'final')
        total = len(chapters) or 1

        milestones = self.get_milestones()
        ms_done = sum(1 for m in milestones if m['completed'])

        todos = self.get_todos(pending_only=False)
        todo_done = sum(1 for t in todos if t['done'])

        return {
            'chapters_total': len(chapters),
            'chapters_completed': completed,
            'chapters_progress': round(completed / total * 100),
            'total_words': total_words,
            'target_words': target_words,
            'words_progress': round(total_words / max(target_words, 1) * 100),
            'milestones_total': len(milestones),
            'milestones_done': ms_done,
            'todos_total': len(todos),
            'todos_done': todo_done,
            'chapter_details': [
                {
                    'id': c['id'],
                    'number': c['chapter_number'],
                    'title': c['title'],
                    'status': c['status'],
                    'word_count': c['word_count'],
                    'target_words': c['target_words'],
                    'progress': round(c['word_count'] / max(c['target_words'], 1) * 100)
                } for c in chapters
            ]
        }

    def init_default_chapters(self):
        """Initialize standard Indonesian thesis chapters."""
        defaults = [
            (1, 'BAB I — Pendahuluan', 3000),
            (2, 'BAB II — Tinjauan Pustaka', 8000),
            (3, 'BAB III — Metodologi Penelitian', 5000),
            (4, 'BAB IV — Hasil dan Pembahasan', 8000),
            (5, 'BAB V — Kesimpulan dan Saran', 2000),
        ]
        for num, title, target in defaults:
            existing = self.db.execute(
                "SELECT id FROM chapters WHERE chapter_number=?", (num,)
            ).fetchone()
            if not existing:
                self.add_chapter(num, title, target)
