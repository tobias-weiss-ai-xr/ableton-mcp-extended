"""
Enhanced asset indexing for fast fuzzy search and predictive loading.
"""

import json
import re
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class AssetIndex:
    """
    Enhanced asset indexing for fast fuzzy search and predictive loading.
    
    Maintains a searchable index of Ableton browser items with:
    - Full-text search on names
    - Levenshtein distance for fuzzy matching
    - Category-based indexing
    - Usage tracking for predictive loading
    - Scene-based asset preloading hints
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the asset index."""
        self.db_path = Path(db_path) if db_path else Path.home() / ".ableton_mcp" / "asset_index.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_index_db()
    
    def _init_index_db(self) -> None:
        """Create the asset index database."""
        with sqlite3.connect(self.db_path) as conn:
            # Main asset index table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    uri TEXT UNIQUE NOT NULL,
                    category TEXT,
                    type TEXT,
                    file_id TEXT,
                    search_terms TEXT,
                    last_used REAL,
                    use_count INTEGER DEFAULT 0,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Index for fast text search
            conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON assets(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON assets(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_used ON assets(last_used)")
            
            # Scene presets for predictive loading
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scene_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scene_name TEXT UNIQUE NOT NULL,
                    track_index INTEGER,
                    suggested_uris TEXT,
                    last_used REAL,
                    use_count INTEGER DEFAULT 0
                )
            """)
            
            # Popular search queries
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    result_count INTEGER DEFAULT 0,
                    timestamp REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            conn.commit()
    
    def index_asset(
        self,
        name: str,
        uri: str,
        category: Optional[str] = None,
        asset_type: Optional[str] = None,
        file_id: Optional[str] = None
    ) -> None:
        """Index a single asset for search."""
        search_terms = self._generate_search_terms(name)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO assets 
                (name, uri, category, type, file_id, search_terms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, uri, category, asset_type, file_id, search_terms))
            conn.commit()
    
    def _generate_search_terms(self, name: str) -> str:
        """Generate searchable terms from asset name."""
        cleaned = re.sub(r'[^\w\s]', ' ', name.lower())
        terms = cleaned.split()
        words = [t for t in terms if len(t) > 2]
        bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)]
        return ' '.join(terms + bigrams)
    
    def fuzzy_search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search for assets using fuzzy matching."""
        query_lower = query.lower()
        results = []
        
        with sqlite3.connect(self.db_path) as conn:
            if category:
                cursor = conn.execute(
                    "SELECT id, name, uri, category, type FROM assets WHERE category = ?",
                    (category,)
                )
            else:
                cursor = conn.execute("SELECT id, name, uri, category, type FROM assets")
            
            assets = cursor.fetchall()
            
            for asset_id, name, uri, cat, typ in assets:
                score = self._fuzzy_score(query_lower, name.lower())
                if score >= min_score:
                    results.append({
                        "id": asset_id,
                        "name": name,
                        "uri": uri,
                        "category": cat,
                        "type": typ,
                        "score": score
                    })
            
            results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:limit]
    
    def _fuzzy_score(self, query: str, target: str) -> float:
        """Calculate fuzzy similarity score using multiple strategies."""
        base_score = SequenceMatcher(None, query, target).ratio()
        prefix_bonus = 0.3 if target.startswith(query) else 0.0
        
        query_tokens = set(query.split())
        target_tokens = set(target.split())
        query_words = [t for t in query.split() if len(t) > 2]
        target_words = [t for t in target.split() if len(t) > 2]
        
        token_score = 0.0
        if query_words and target_words:
            matches = len(query_tokens & target_tokens) / max(len(query_tokens), len(target_tokens))
            token_score = matches * 0.2
        
        return min(1.0, base_score + prefix_bonus + token_score)
    
    def record_usage(self, uri: str) -> None:
        """Record that an asset was used (for predictive loading)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE assets SET 
                    last_used = strftime('%s', 'now'),
                    use_count = use_count + 1
                WHERE uri = ?
            """, (uri,))
            conn.commit()
    
    def get_popular_assets(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently used assets."""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                cursor = conn.execute("""
                    SELECT name, uri, category, use_count 
                    FROM assets 
                    WHERE category = ? AND use_count > 0
                    ORDER BY use_count DESC
                    LIMIT ?
                """, (category, limit))
            else:
                cursor = conn.execute("""
                    SELECT name, uri, category, use_count 
                    FROM assets 
                    WHERE use_count > 0
                    ORDER BY use_count DESC
                    LIMIT ?
                """, (limit,))
            
            return [
                {"name": name, "uri": uri, "category": cat, "use_count": count}
                for name, uri, cat, count in cursor.fetchall()
            ]
    
    def save_scene_preset(self, scene_name: str, track_index: int, uris: List[str]) -> None:
        """Save a scene's asset configuration for predictive loading."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO scene_presets 
                (scene_name, track_index, suggested_uris, last_used)
                VALUES (?, ?, ?, strftime('%s', 'now'))
            """, (scene_name, track_index, json.dumps(uris)))
            conn.commit()
    
    def get_scene_preset(self, scene_name: str, track_index: int) -> Optional[List[str]]:
        """Get suggested URIs for a scene/track combination."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT suggested_uris FROM scene_presets
                WHERE scene_name = ? AND track_index = ?
            """, (scene_name, track_index))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            return None
    
    def preload_scene_assets(self, scene_name: str) -> List[Tuple[str, str]]:
        """Preload assets for a scene based on past usage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT a.uri, a.category
                FROM assets a
                JOIN scene_presets s ON s.suggested_uris LIKE '%' || a.uri || '%'
                WHERE s.scene_name = ?
            """, (scene_name,))
            
            return [(uri, cat) for uri, cat in cursor.fetchall() if uri and cat]
    
    def clear_index(self) -> None:
        """Clear the entire asset index."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM assets")
            conn.execute("DELETE FROM scene_presets")
            conn.execute("DELETE FROM search_history")
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        with sqlite3.connect(self.db_path) as conn:
            asset_count = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
            preset_count = conn.execute("SELECT COUNT(*) FROM scene_presets").fetchone()[0]
            popular = conn.execute("SELECT COUNT(*) FROM assets WHERE use_count > 0").fetchone()[0]
            
            return {
                "total_indexed_assets": asset_count,
                "scene_presets": preset_count,
                "assets_with_usage": popular,
                "index_location": str(self.db_path)
            }


# Module-level convenience functions
_asset_index: Optional[AssetIndex] = None


def get_asset_index() -> AssetIndex:
    """Get or create the singleton asset index instance."""
    global _asset_index
    if _asset_index is None:
        _asset_index = AssetIndex()
    return _asset_index


def fuzzy_search_assets(
    query: str,
    category: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search for assets using fuzzy matching."""
    return get_asset_index().fuzzy_search(query, category, limit)


def index_asset(
    name: str,
    uri: str,
    category: Optional[str] = None,
    asset_type: Optional[str] = None,
    file_id: Optional[str] = None
) -> None:
    """Index a single asset."""
    get_asset_index().index_asset(name, uri, category, asset_type, file_id)


def preload_scene_assets(scene_name: str) -> List[Tuple[str, str]]:
    """Preload assets for a scene."""
    return get_asset_index().preload_scene_assets(scene_name)


def save_scene_preset(scene_name: str, track_index: int, uris: List[str]) -> None:
    """Save scene preset for predictive loading."""
    get_asset_index().save_scene_preset(scene_name, track_index, uris)


def get_popular_assets(category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Get most frequently used assets."""
    return get_asset_index().get_popular_assets(category, limit)


def record_asset_usage(uri: str) -> None:
    """Record that an asset was used."""
    get_asset_index().record_usage(uri)


def get_asset_index_stats() -> Dict[str, Any]:
    """Get asset index statistics."""
    return get_asset_index().get_stats()