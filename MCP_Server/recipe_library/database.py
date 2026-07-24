"""RecipeDB — SQLite CRUD and search for the recipe library."""
import sqlite3
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger("AbletonMCPServer")


class RecipeDB:
    """SQLite-backed recipe storage."""

    def __init__(self, db_path: str = "recipe_library.db"):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def init_db(self, builtin_recipes: Optional[List[Dict[str, Any]]] = None):
        """Create tables if needed and seed built-in recipes on first run."""
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                tags TEXT DEFAULT '',
                description TEXT DEFAULT '',
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_builtin INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_recipes_tags ON recipes(tags)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_recipes_category_name ON recipes(category, name)")
        conn.commit()

        if builtin_recipes and self.get_builtin_count() == 0:
            self.seed_builtin(builtin_recipes)

    def get_builtin_count(self) -> int:
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) FROM recipes WHERE is_builtin = 1").fetchone()
        return row[0] if row else 0

    def seed_builtin(self, recipes: List[Dict[str, Any]]):
        """Insert or update built-in recipes (upsert by name+categories)."""
        conn = self._get_conn()
        now = datetime.now(timezone.utc).isoformat()
        for recipe in recipes:
            existing = conn.execute(
                "SELECT id FROM recipes WHERE name = ? AND category = ? AND is_builtin = 1",
                (recipe["name"], recipe["category"])
            ).fetchone()
            if existing:
                conn.execute(
                    """UPDATE recipes SET tags=?, description=?, data=?, updated_at=?
                       WHERE id=?""",
                    (recipe.get("tags", ""), recipe.get("description", ""),
                     recipe["data"], now, existing["id"])
                )
            else:
                conn.execute(
                    """INSERT INTO recipes (category, name, tags, description, data, created_at, updated_at, is_builtin)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                    (recipe["category"], recipe["name"], recipe.get("tags", ""),
                     recipe.get("description", ""), recipe["data"], now, now)
                )
        conn.commit()

    def search(self, category: Optional[str] = None, tags: Optional[str] = None,
               query: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        sql = "SELECT id, category, name, tags, description, is_builtin FROM recipes WHERE 1=1"
        params = []
        if category:
            sql += " AND category = ?"
            params.append(category)
        if tags:
            for tag in tags.split(","):
                tag = tag.strip()
                if tag:
                    sql += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
        if query:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        sql += " ORDER BY is_builtin DESC, name ASC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        return dict(row) if row else None

    def create(self, category: str, name: str, data: str,
               tags: str = "", description: str = "") -> int:
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO recipes (category, name, tags, description, data, created_at, updated_at, is_builtin)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (category, name, tags, description, data, now, now)
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, recipe_id: int, **kwargs) -> None:
        recipe = self.get(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found")
        if recipe["is_builtin"]:
            raise ValueError(f"Cannot update built-in recipe {recipe_id}")
        allowed = {"name", "tags", "description", "data", "category"}
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [recipe_id]
        conn = self._get_conn()
        conn.execute(f"UPDATE recipes SET {set_clause} WHERE id = ?", values)
        conn.commit()

    def delete(self, recipe_id: int) -> None:
        recipe = self.get(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found")
        if recipe["is_builtin"]:
            raise ValueError(f"Cannot delete built-in recipe {recipe_id}")
        conn = self._get_conn()
        conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
