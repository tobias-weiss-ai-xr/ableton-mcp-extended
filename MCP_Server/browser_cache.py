"""
SQLite-based browser cache for Ableton MCP.

Provides persistent caching for browser tree data (instruments, effects, sounds, drums)
with TTL-based expiration. Data persists across MCP server restarts.

Database location: ~/.ableton_mcp/browser_cache.db
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Default cache directory
CACHE_DIR = Path.home() / ".ableton_mcp"
CACHE_DB = CACHE_DIR / "browser_cache.db"
DEFAULT_TTL = 3600  # 1 hour in seconds


class BrowserCache:
    """SQLite-backed cache for Ableton browser data."""

    def __init__(self, db_path: Optional[Path] = None, ttl: int = DEFAULT_TTL):
        """
        Initialize the browser cache.

        Args:
            db_path: Path to SQLite database file (default: ~/.ableton_mcp/browser_cache.db)
            ttl: Time-to-live in seconds for cache entries (default: 3600 = 1 hour)
        """
        self.db_path = Path(db_path) if db_path else CACHE_DB
        self.ttl = ttl

        # Ensure cache directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS browser_cache (
                    category_type TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    ttl INTEGER DEFAULT 3600
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON browser_cache(timestamp)
            """)
            conn.commit()

    def is_cache_valid(self, category_type: str) -> bool:
        """
        Check if cached data for a category is still valid (not expired).

        Args:
            category_type: The category to check (e.g., 'instruments', 'audio_effects')

        Returns:
            True if cache exists and is within TTL, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp, ttl FROM browser_cache WHERE category_type = ?",
                (category_type,),
            )
            row = cursor.fetchone()

            if row is None:
                return False

            timestamp, ttl = row
            return (time.time() - timestamp) < ttl

    def update_cache(self, category_type: str, data: Dict[str, Any]) -> None:
        """
        Update cache for a specific category type.

        Args:
            category_type: The category to cache (e.g., 'instruments', 'audio_effects')
            data: The data to cache (will be serialized to JSON)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO browser_cache (category_type, data, timestamp, ttl)
                VALUES (?, ?, ?, ?)
                """,
                (category_type, json.dumps(data), time.time(), self.ttl),
            )
            conn.commit()

    def get_cache(self, category_type: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a specific category type.

        Args:
            category_type: The category to retrieve

        Returns:
            Cached data dict if valid, None if expired or not found
        """
        if not self.is_cache_valid(category_type):
            return None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM browser_cache WHERE category_type = ?",
                (category_type,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return json.loads(row[0])

    def clear_cache(self, category_type: Optional[str] = None) -> None:
        """
        Clear cache for a specific category or all categories.

        Args:
            category_type: The category to clear, or None to clear all
        """
        with sqlite3.connect(self.db_path) as conn:
            if category_type:
                conn.execute(
                    "DELETE FROM browser_cache WHERE category_type = ?",
                    (category_type,),
                )
            else:
                conn.execute("DELETE FROM browser_cache")
            conn.commit()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current browser cache.

        Returns:
            Dict with cache statistics including entries, TTL, and per-category details
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get total count
            cursor = conn.execute("SELECT COUNT(*) FROM browser_cache")
            cache_entries = cursor.fetchone()[0]

            # Get all entries
            cursor = conn.execute(
                "SELECT category_type, timestamp, ttl FROM browser_cache"
            )
            rows = cursor.fetchall()

            categories = {}
            for category_type, timestamp, ttl in rows:
                age_seconds = time.time() - timestamp
                is_valid = age_seconds < ttl

                categories[category_type] = {
                    "cached": True,
                    "valid": is_valid,
                    "age_seconds": round(age_seconds, 1),
                    "ttl_seconds": ttl,
                    "expires_in_seconds": round(max(0, ttl - age_seconds), 1),
                }

            return {
                "cache_entries": cache_entries,
                "default_ttl": self.ttl,
                "cache_file": str(self.db_path),
                "categories": categories,
            }

    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT category_type, timestamp, ttl FROM browser_cache"
            )
            rows = cursor.fetchall()

            removed = 0
            for category_type, timestamp, ttl in rows:
                if (time.time() - timestamp) >= ttl:
                    conn.execute(
                        "DELETE FROM browser_cache WHERE category_type = ?",
                        (category_type,),
                    )
                    removed += 1

            conn.commit()
            return removed


# Convenience functions matching the original interface
_cache_instance: Optional[BrowserCache] = None


def get_cache_instance() -> BrowserCache:
    """Get or create the singleton cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = BrowserCache()
    return _cache_instance


def is_cache_valid(category_type: str) -> bool:
    """Check if cached data for a category is still valid."""
    return get_cache_instance().is_cache_valid(category_type)


def update_cache(category_type: str, data: Dict[str, Any]) -> None:
    """Update cache for a specific category type."""
    get_cache_instance().update_cache(category_type, data)


def get_cache(category_type: str) -> Optional[Dict[str, Any]]:
    """Get cached data for a specific category type."""
    return get_cache_instance().get_cache(category_type)


def clear_browser_cache(category_type: Optional[str] = None) -> None:
    """Clear cache for a specific category or all categories."""
    get_cache_instance().clear_cache(category_type)


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about the current browser cache."""
    return get_cache_instance().get_cache_stats()
