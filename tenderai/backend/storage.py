import sqlite3
from contextlib import contextmanager
from pathlib import Path
from dataclasses import astuple
from .scoring import Result


class Store:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS screenings (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
                category TEXT, priority TEXT, score REAL, decision TEXT, explanation TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def save(self, title: str, description: str, result: Result):
        with self.connect() as db:
            key = db.execute("""INSERT INTO screenings
                (title, description, category, priority, score, decision, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (title, description, *astuple(result))).lastrowid
            return dict(db.execute("SELECT * FROM screenings WHERE id=?", (key,)).fetchone())

    def history(self, decision: str):
        with self.connect() as db:
            rows = db.execute("""SELECT * FROM screenings WHERE ?='' OR decision=?
                              ORDER BY id DESC LIMIT 100""", (decision, decision))
            return [dict(row) for row in rows]
