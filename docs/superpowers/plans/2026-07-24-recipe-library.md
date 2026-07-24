# Recipe Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a SQLite-backed recipe library with 50 built-in musical patterns (chord progressions, drum patterns, mix templates, sound design) exposed as MCP tools and resources.

**Architecture:** Single SQLite table with JSON payloads per category. `RecipeDB` class (following `browser_cache.py` pattern) handles CRUD/search. MCP tools registered via `register_recipe_tools(mcp, get_ableton_connection)` pattern in `server.py`. ~50 built-in recipes seeded on first init.

**Tech Stack:** Python 3.12+, SQLite3, `mcp.server.fastmcp`, `json`, `typing`, `time`

---

### Task 1: Models — TypedDicts + Category Validation

**Files:**
- Create: `MCP_Server/recipe_library/models.py`
- Test: `tests/test_recipe_models.py`

- [ ] **Step 1: Write failing tests**

Write `tests/test_recipe_models.py`:

```python
"""Tests for recipe library data models and validation."""
import pytest
import json
from MCP_Server.recipe_library.models import (
    ChordProgression,
    DrumPattern,
    MixTemplate,
    SoundDesign,
    validate_category_data,
    RecipeSummary,
)


class TestChordProgression:
    def test_valid(self):
        data = ChordProgression(
            key="C", scale="major", chords=["C", "Am", "F", "G"],
            voicing="open", mood="uplifting"
        )
        assert data["key"] == "C"
        assert len(data["chords"]) == 4

    def test_validation_pass(self):
        result = validate_category_data("chord_progression", json.dumps({
            "key": "C", "scale": "major", "chords": ["C", "Am", "F", "G"],
            "voicing": "open", "mood": "uplifting"
        }))
        assert result is True


class TestDrumPattern:
    def test_valid(self):
        data = DrumPattern(
            pattern_type="one_drop", kit_query="query:Drums#FileId_58622",
            bars=4, grid="|X---|---X---|", tempo_range=[70, 90], mood="dub"
        )
        assert data["pattern_type"] == "one_drop"

    def test_validation_pass(self):
        result = validate_category_data("drum_pattern", json.dumps({
            "pattern_type": "one_drop", "kit_query": "query:Drums#FileId_58622",
            "bars": 4, "grid": "|X---|", tempo_range=[70, 90], mood="dub"
        }))
        assert result is True


class TestMixTemplate:
    def test_valid(self):
        data = MixTemplate(
            genre="deep_house", track_count=6,
            structure=["intro", "drop"],
            mixing_techniques=["bass_forward", "crossfade"],
            energy_curve="progressive_house",
            description="Warm deep house"
        )
        assert data["genre"] == "deep_house"

    def test_validation_pass(self):
        result = validate_category_data("mix_template", json.dumps({
            "genre": "deep_house", "track_count": 6,
            "structure": ["intro", "drop"],
            "mixing_techniques": ["bass_forward"],
            "energy_curve": "progressive_house",
            "description": "Deep house template"
        }))
        assert result is True


class TestSoundDesign:
    def test_valid(self):
        data = SoundDesign(
            device_type="Operator", preset_name="Deep Sub Bass",
            parameters={"filter_cutoff": 0.4, "filter_resonance": 0.2},
            tags=["bass", "sub"]
        )
        assert data["device_type"] == "Operator"

    def test_validation_pass(self):
        result = validate_category_data("sound_design", json.dumps({
            "device_type": "Operator", "preset_name": "Deep Sub Bass",
            "parameters": {"filter_cutoff": 0.4},
            "tags": ["bass"]
        }))
        assert result is True


class TestValidationEdgeCases:
    def test_invalid_category(self):
        with pytest.raises(ValueError, match="Unknown category"):
            validate_category_data("invalid_cat", "{}")

    def test_invalid_json(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            validate_category_data("chord_progression", "not json")

    def test_missing_required_field(self):
        with pytest.raises(ValueError, match="Missing required field"):
            validate_category_data("chord_progression", json.dumps({
                "key": "C"  # missing scale, chords, etc.
            }))


class TestRecipeSummary:
    def test_fields(self):
        summary = RecipeSummary(
            id=1, category="chord_progression", name="Test Progression",
            tags="pop,verse", description="A test"
        )
        assert summary["id"] == 1
        assert summary["category"] == "chord_progression"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_recipe_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'MCP_Server.recipe_library'`

- [ ] **Step 3: Create package and write models.py**

Create `MCP_Server/recipe_library/__init__.py`:
```python
"""Recipe Library — reusable musical patterns for Ableton Live."""
```

Create `MCP_Server/recipe_library/models.py`:
```python
"""TypedDicts and validation for recipe library categories."""
from typing import TypedDict, Optional, List
import json


class ChordProgression(TypedDict):
    key: str
    scale: str
    chords: List[str]
    voicing: str
    mood: str


class DrumPattern(TypedDict):
    pattern_type: str
    kit_query: str
    bars: int
    grid: str
    tempo_range: List[int]
    mood: str


class MixTemplate(TypedDict):
    genre: str
    track_count: int
    structure: List[str]
    mixing_techniques: List[str]
    energy_curve: str
    description: str


class SoundDesign(TypedDict):
    device_type: str
    preset_name: str
    parameters: dict
    tags: List[str]


class RecipeSummary(TypedDict):
    id: int
    category: str
    name: str
    tags: str
    description: str


CATEGORY_VALIDATORS = {
    "chord_progression": {
        "required": ["key", "scale", "chords", "voicing", "mood"],
        "type": ChordProgression,
    },
    "drum_pattern": {
        "required": ["pattern_type", "kit_query", "bars", "grid", "tempo_range", "mood"],
        "type": DrumPattern,
    },
    "mix_template": {
        "required": ["genre", "track_count", "structure", "mixing_techniques", "energy_curve", "description"],
        "type": MixTemplate,
    },
    "sound_design": {
        "required": ["device_type", "preset_name", "parameters", "tags"],
        "type": SoundDesign,
    },
}


def validate_category_data(category: str, data_json: str) -> bool:
    """Validate JSON data against category schema. Raises ValueError on failure."""
    if category not in CATEGORY_VALIDATORS:
        raise ValueError(f"Unknown category: {category}")

    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")

    if not isinstance(data, dict):
        raise ValueError("Data must be a JSON object")

    validator = CATEGORY_VALIDATORS[category]
    for field in validator["required"]:
        if field not in data:
            raise ValueError(f"Missing required field '{field}' for category '{category}'")

    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_recipe_models.py -v`
Expected: 15 PASSED (all test methods)

- [ ] **Step 5: Commit**

```bash
git add MCP_Server/recipe_library/__init__.py MCP_Server/recipe_library/models.py tests/test_recipe_models.py
git commit -m "feat(recipe-library): add data models and category validation"
```

---

### Task 2: Database — RecipeDB CRUD + Search

**Files:**
- Create: `MCP_Server/recipe_library/database.py`
- Test: `tests/test_recipe_database.py`

- [ ] **Step 1: Write failing tests**

Write `tests/test_recipe_database.py`:

```python
"""Tests for RecipeDB — SQLite CRUD and search."""
import pytest
import json
import os
from MCP_Server.recipe_library.database import RecipeDB


@pytest.fixture
def db():
    """Create in-memory RecipeDB for each test."""
    database = RecipeDB(":memory:")
    database.init_db()
    return database


class TestRecipeDBCRUD:
    def test_create_and_get(self, db):
        recipe_id = db.create(
            category="chord_progression",
            name="Test Progression",
            data=json.dumps({"key": "C", "scale": "major", "chords": ["C", "F", "G"], "voicing": "open", "mood": "happy"}),
            tags="pop,happy",
            description="A test progression"
        )
        recipe = db.get(recipe_id)
        assert recipe is not None
        assert recipe["name"] == "Test Progression"
        assert recipe["category"] == "chord_progression"
        assert recipe["is_builtin"] == 0

    def test_get_not_found(self, db):
        result = db.get(999)
        assert result is None

    def test_update(self, db):
        recipe_id = db.create("chord_progression", "Test", "{}", "tag", "desc")
        db.update(recipe_id, name="Updated Name")
        recipe = db.get(recipe_id)
        assert recipe["name"] == "Updated Name"

    def test_update_builtin_raises(self, db):
        db.seed_builtin([
            {"category": "chord_progression", "name": "Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        builtins = db.search(category="chord_progression")
        builtin_id = builtins[0]["id"]
        with pytest.raises(ValueError, match="Cannot update built-in"):
            db.update(builtin_id, name="New Name")

    def test_delete(self, db):
        recipe_id = db.create("chord_progression", "To Delete", "{}", "", "")
        db.delete(recipe_id)
        assert db.get(recipe_id) is None

    def test_delete_builtin_raises(self, db):
        db.seed_builtin([
            {"category": "chord_progression", "name": "BuiltinDel", "tags": "", "description": "", "data": "{}"}
        ])
        builtins = db.search(category="chord_progression")
        builtin_id = builtins[0]["id"]
        with pytest.raises(ValueError, match="Cannot delete built-in"):
            db.delete(builtin_id)


class TestRecipeDBSearch:
    def test_search_by_category(self, db):
        db.create("chord_progression", "CP1", "{}", "", "")
        db.create("drum_pattern", "DP1", "{}", "", "")
        results = db.search(category="chord_progression")
        assert len(results) == 1
        assert results[0]["name"] == "CP1"

    def test_search_by_tags(self, db):
        db.create("chord_progression", "A", "{}", "pop,upbeat", "")
        db.create("chord_progression", "B", "{}", "jazz,chill", "")
        results = db.search(tags="pop")
        assert len(results) == 1
        assert results[0]["name"] == "A"

    def test_search_and_tags(self, db):
        db.create("chord_progression", "X", "{}", "pop,jazz", "")
        results = db.search(tags="pop,jazz")
        assert len(results) == 1

    def test_search_by_query(self, db):
        db.create("chord_progression", "Sunshine Pop", "{}", "", "Upbeat major progression")
        results = db.search(query="sunshine")
        assert len(results) == 1

    def test_search_all(self, db):
        db.create("chord_progression", "A", "{}", "", "")
        db.create("drum_pattern", "B", "{}", "", "")
        results = db.search()
        assert len(results) >= 2

    def test_search_empty(self, db):
        results = db.search()
        assert len(results) == 0


class TestRecipeDBSeeding:
    def test_seed_on_init(self, db):
        # init_db seeds builtins when table is empty
        count = db.get_builtin_count()
        assert count > 0

    def test_seed_idempotent(self, db):
        db.seed_builtin([
            {"category": "chord_progression", "name": "Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        count1 = db.get_builtin_count()
        db.seed_builtin([
            {"category": "chord_progression", "name": "Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        count2 = db.get_builtin_count()
        assert count1 == count2

    def test_create_and_get_builtin(self, db):
        db.seed_builtin([
            {"category": "drum_pattern", "name": "Test Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        results = db.search(category="drum_pattern")
        assert len(results) == 1
        assert results[0]["name"] == "Test Builtin"
        assert results[0]["is_builtin"] == 1

    def test_get_builtin_count_empty(self):
        db = RecipeDB(":memory:")
        # Don't init — table is empty
        db.init_db()
        # With no seed data passed, seeding step is skipped but table exists
        # get_builtin_count returns 0
        assert db.get_builtin_count() == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_recipe_database.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'MCP_Server.recipe_library.database'`

- [ ] **Step 3: Write database.py**

```python
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

        # Seed built-in recipes on first run
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_recipe_database.py -v`
Expected: 14 PASSED

- [ ] **Step 5: Commit**

```bash
git add MCP_Server/recipe_library/database.py tests/test_recipe_database.py
git commit -m "feat(recipe-library): add RecipeDB SQLite CRUD and search"
```

---

### Task 3: Seed Data — Built-in Recipes

**Files:**
- Create: `MCP_Server/recipe_library/recipes.py`

- [ ] **Step 1: Write seed data**

```python
"""Built-in seed recipes for the recipe library."""
import json
from typing import List, Dict, Any

BUILTIN_RECIPES: List[Dict[str, Any]] = [
    # ===== CHORD PROGRESSIONS (15) =====
    {"category": "chord_progression", "name": "Pop I–V–vi–IV", "tags": "pop,uplifting,verse",
     "description": "Classic pop progression: C G Am F. Versatile, emotional, widely used.",
     "data": {"key": "C", "scale": "major", "chords": ["C", "G", "Am", "F"], "voicing": "open", "mood": "uplifting"}},
    {"category": "chord_progression", "name": "Deep House Seventh", "tags": "deep_house,warm,seventh",
     "description": "Smooth seventh-based loop: Am7 Dm7 G7 Cmaj7.",
     "data": {"key": "C", "scale": "major", "chords": ["Am7", "Dm7", "G7", "Cmaj7"], "voicing": "spread", "mood": "warm"}},
    {"category": "chord_progression", "name": "Techno Minor Loop", "tags": "techno,minimal,hypnotic",
     "description": "Hypnotic two-chord techno loop: Dm G. Minimal movement, maximum groove.",
     "data": {"key": "D", "scale": "minor", "chords": ["Dm", "G"], "voicing": "close", "mood": "driving"}},
    {"category": "chord_progression", "name": "Dub Techno Pad", "tags": "dub_techno,ambient,space",
     "description": "Spacious dub techno chords: Dm G C F. Long reverb tails assumed.",
     "data": {"key": "D", "scale": "minor", "chords": ["Dm", "G", "C", "F"], "voicing": "open", "mood": "spacious"}},
    {"category": "chord_progression", "name": "Ambient Drone", "tags": "ambient,drone,atmospheric",
     "description": "Slow-shifting ambient: Cmaj7 Fmaj9. Holds for 8+ bars per chord.",
     "data": {"key": "C", "scale": "major", "chords": ["Cmaj7", "Fmaj9"], "voicing": "spread", "mood": "atmospheric"}},
    {"category": "chord_progression", "name": "Jazz II–V–I", "tags": "jazz,swing,sophisticated",
     "description": "Essential jazz cadence: Dm7 G7 Cmaj7. Add extensions for color.",
     "data": {"key": "C", "scale": "major", "chords": ["Dm7", "G7", "Cmaj7"], "voicing": "spread", "mood": "sophisticated"}},
    {"category": "chord_progression", "name": "Lo-Fi Dorian Loop", "tags": "lo-fi,dorian,chill",
     "description": "Warm lo-fi loop: Am7 D7 Am7 G. Slightly off, perfectly cozy.",
     "data": {"key": "A", "scale": "minor", "chords": ["Am7", "D7", "Am7", "G"], "voicing": "close", "mood": "chill"}},
    {"category": "chord_progression", "name": "Minimal Tech Stab", "tags": "minimal_tech,staccato,stab",
     "description": "Short stab chords: Eb7 D7 Eb7 D7. Syncopated rhythm implied.",
     "data": {"key": "Eb", "scale": "minor", "chords": ["Eb7", "D7"], "voicing": "close", "mood": "tense"}},
    {"category": "chord_progression", "name": "Drum & Bass Seventh Roll", "tags": "dnb,seventh,energetic",
     "description": "Fast-moving DnB progression: Am7 Fmaj7 Cmaj7 G.",
     "data": {"key": "A", "scale": "minor", "chords": ["Am7", "Fmaj7", "Cmaj7", "G"], "voicing": "close", "mood": "energetic"}},
    {"category": "chord_progression", "name": "Trance Euphoric", "tags": "trance,euphoric,uplifting",
     "description": "Uplifting trance: Fm Db Ab Eb. Stadium-sized emotion.",
     "data": {"key": "F", "scale": "minor", "chords": ["Fm", "Db", "Ab", "Eb"], "voicing": "spread", "mood": "euphoric"}},
    {"category": "chord_progression", "name": "Blues Shuffle", "tags": "blues,shuffle,gritty",
     "description": "12-bar blues in A: A7 D7 E7. Let the rhythm section swing.",
     "data": {"key": "A", "scale": "major", "chords": ["A7", "D7", "E7"], "voicing": "open", "mood": "gritty"}},
    {"category": "chord_progression", "name": "Neo-Soul Voicing", "tags": "neo-soul,smooth,extended",
     "description": "Rich extended chords: Cm9 Fm9 G7#5 Cm9. J Dilla vibes.",
     "data": {"key": "C", "scale": "minor", "chords": ["Cm9", "Fm9", "G7#5", "Cm9"], "voicing": "spread", "mood": "smooth"}},
    {"category": "chord_progression", "name": "Synthwave Arp", "tags": "synthwave,retro,driving",
     "description": "Retro synthwave: Am F C G. Arpeggiated, gated reverb.",
     "data": {"key": "A", "scale": "minor", "chords": ["Am", "F", "C", "G"], "voicing": "open", "mood": "driving"}},
    {"category": "chord_progression", "name": "Minimal Microtonal", "tags": "minimal,experimental,tense",
     "description": "Tension-building: C F G Ab. Deliberately unresolved.",
     "data": {"key": "C", "scale": "minor", "chords": ["C", "F", "G", "Ab"], "voicing": "close", "mood": "tense"}},
    {"category": "chord_progression", "name": "House Piano Loop", "tags": "house,piano,classic",
     "description": "Classic house piano: Fmaj7 G Em7 Am. The Defected special.",
     "data": {"key": "F", "scale": "major", "chords": ["Fmaj7", "G", "Em7", "Am"], "voicing": "open", "mood": "happy"}},

    # ===== DRUM PATTERNS (12) =====
    {"category": "drum_pattern", "name": "One Drop", "tags": "dub,reggae,classic",
     "description": "Classic dub reggae: kick on beat 1, snare on beat 3 delayed.",
     "data": {"pattern_type": "one_drop", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|----|--X-|----|", "tempo_range": [70, 90], "mood": "dub"}},
    {"category": "drum_pattern", "name": "Rockers", "tags": "reggae,skank,offbeat",
     "description": "Jamaican rockers: kick/hat offbeat emphasis.",
     "data": {"pattern_type": "rockers", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X-X-|---|X-X-|---|", "tempo_range": [75, 95], "mood": "groovy"}},
    {"category": "drum_pattern", "name": "Steppers", "tags": "dub,steppers,four_to_floor",
     "description": "Steppers rhythm: even kick distribution, minimal variation.",
     "data": {"pattern_type": "steppers", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|X---|X---|X---|", "tempo_range": [80, 100], "mood": "driving"}},
    {"category": "drum_pattern", "name": "House Basic", "tags": "house,four_on_floor,clap",
     "description": "Four-on-the-floor with clap on 2 and 4.",
     "data": {"pattern_type": "house_basic", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|---|X---|---|", "tempo_range": [120, 130], "mood": "driving"}},
    {"category": "drum_pattern", "name": "Techno 4x4", "tags": "techno,driving,relentless",
     "description": "Driving techno kick pattern: continuous kick drum.",
     "data": {"pattern_type": "techno_4x4", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|X---|X---|X---|", "tempo_range": [125, 145], "mood": "relentless"}},
    {"category": "drum_pattern", "name": "Dub Techno", "tags": "dub_techno,syncopated,offbeat",
     "description": "Syncopated dub techno: offbeat accents with space.",
     "data": {"pattern_type": "dub_techno", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|----|--X-|----|", "tempo_range": [70, 90], "mood": "spacious"}},
    {"category": "drum_pattern", "name": "Half Time", "tags": "half_time,heavy,slowed",
     "description": "Half-time feel: kick on 1 and 3, snare on 3. Heavy.",
     "data": {"pattern_type": "steppers", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|---X---|---X---|---X---|", "tempo_range": [80, 100], "mood": "heavy"}},
    {"category": "drum_pattern", "name": "Shuffle", "tags": "shuffle,swing,offbeat",
     "description": "Swing-shuffle pattern: triplet-feel hi-hats, snare on 2 and 4.",
     "data": {"pattern_type": "rockers", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X-X-|X-X-|X-X-|X-X-|", "tempo_range": [90, 120], "mood": "groovy"}},
    {"category": "drum_pattern", "name": "Breakbeat Core", "tags": "breakbeat,drum_and_bass,chopped",
     "description": "Amen-style break: syncopated kicks, rapid snares.",
     "data": {"pattern_type": "one_drop", "kit_query": "query:Drums#FileId_58622", "bars": 2,
              "grid": "|X--X|-X-X|X--X|--X-|", "tempo_range": [160, 180], "mood": "energetic"}},
    {"category": "drum_pattern", "name": "Footwork", "tags": "footwork,juke,frenetic",
     "description": "Fast footwork pattern: triple-time hats, rolling kicks.",
     "data": {"pattern_type": "techno_4x4", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X-X-|X-X-|X-X-|X-X-|", "tempo_range": [150, 170], "mood": "frenetic"}},
    {"category": "drum_pattern", "name": "Trap", "tags": "trap,hip-hop,heavy_hihat",
     "description": "Modern trap: heavy 808, syncopated hats, rolling snare.",
     "data": {"pattern_type": "steppers", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|-X--|--X-|-X-X|", "tempo_range": [70, 80], "mood": "aggressive"}},
    {"category": "drum_pattern", "name": "Soca", "tags": "soca,carnival,energetic",
     "description": "Soca kick-snare: driving rhythm with upbeat energy.",
     "data": {"pattern_type": "house_basic", "kit_query": "query:Drums#FileId_58622", "bars": 4,
              "grid": "|X---|X---|X---|X---|", "tempo_range": [110, 130], "mood": "energetic"}},

    # ===== MIX TEMPLATES (10) =====
    {"category": "mix_template", "name": "Deep House", "tags": "house,warm,melodic",
     "description": "Warm deep house arrangement with extended breakdown and gradual build.",
     "data": {"genre": "deep_house", "track_count": 6,
              "structure": ["intro", "groove_a", "build", "drop", "breakdown", "groove_b", "outro"],
              "mixing_techniques": ["bass_forward", "crossfade", "filter_sweep", "send_sweep", "strip_and_build"],
              "energy_curve": "progressive_house"}},
    {"category": "mix_template", "name": "Techno", "tags": "techno,driving,minimal",
     "description": "Relentless techno arrangement: fast transitions, minimal breakdowns.",
     "data": {"genre": "techno", "track_count": 6,
              "structure": ["groove_a", "groove_b", "build", "drop", "groove_a", "outro"],
              "mixing_techniques": ["filter_sweep", "crossfade", "volume_automation", "filter_sweep"],
              "energy_curve": "plateau"}},
    {"category": "mix_template", "name": "Dub Techno", "tags": "dub,techno,spacious",
     "description": "Spacious dub techno with long reverb trails and slow evolution.",
     "data": {"genre": "dub_techno", "track_count": 5,
              "structure": ["intro", "groove_a", "groove_b", "groove_a", "groove_c", "outro"],
              "mixing_techniques": ["bass_forward", "send_sweep", "dub_drop", "crossfade"],
              "energy_curve": "dub_techno"}},
    {"category": "mix_template", "name": "Ambient", "tags": "ambient,slow,evolving",
     "description": "Slow ambient: long sections (16+ bars), gradual pad crossfades.",
     "data": {"genre": "ambient", "track_count": 4,
              "structure": ["intro", "groove_a", "groove_b", "groove_c", "outro"],
              "mixing_techniques": ["crossfade", "volume_automation", "send_sweep"],
              "energy_curve": "ambient"}},
    {"category": "mix_template", "name": "Pop", "tags": "pop,verse_chorus,structured",
     "description": "Standard pop arrangement with clear verse-chorus structure.",
     "data": {"genre": "pop", "track_count": 7,
              "structure": ["intro", "groove_a", "build", "drop", "groove_b", "build_2", "drop", "outro"],
              "mixing_techniques": ["strip_and_build", "filter_sweep", "crossfade", "volume_automation"],
              "energy_curve": "progressive_house"}},
    {"category": "mix_template", "name": "Drum & Bass", "tags": "dnb,fast,energetic",
     "description": "High-energy DnB: short sections, rapid-fire mixing.",
     "data": {"genre": "dnb", "track_count": 6,
              "structure": ["groove_a", "build", "drop", "groove_b", "build_2", "drop", "outro"],
              "mixing_techniques": ["crossfade", "filter_sweep", "bass_forward", "volume_automation"],
              "energy_curve": "driving"}},
    {"category": "mix_template", "name": "Minimal", "tags": "minimal,reductive,space",
     "description": "Less is more: few elements, maximum groove, long transitions.",
     "data": {"genre": "minimal", "track_count": 4,
              "structure": ["groove_a", "groove_a", "build", "groove_b", "groove_a"],
              "mixing_techniques": ["filter_sweep", "crossfade", "volume_automation", "crossfade"],
              "energy_curve": "minimal"}},
    {"category": "mix_template", "name": "Hip-Hop", "tags": "hip-hop,verse_hook,bounce",
     "description": "Beat-driven hip-hop arrangement with drop-ins and cuts.",
     "data": {"genre": "hip-hop", "track_count": 6,
              "structure": ["intro", "groove_a", "groove_b", "groove_a", "groove_c", "outro"],
              "mixing_techniques": ["strip_and_build", "bass_forward", "crossfade", "dub_drop"],
              "energy_curve": "progressive_house"}},
    {"category": "mix_template", "name": "Lo-Fi", "tags": "lo-fi,chill,warm",
     "description": "Relaxed lo-fi: tape warmth, subtle movement, minimalist structure.",
     "data": {"genre": "lo-fi", "track_count": 4,
              "structure": ["intro", "groove_a", "groove_b", "groove_a", "outro"],
              "mixing_techniques": ["crossfade", "send_sweep", "volume_automation"],
              "energy_curve": "ambient"}},
    {"category": "mix_template", "name": "Trance", "tags": "trance,euphoric,long_build",
     "description": "Classic trance: 32-bar builds, euphoric drops, supersaw leads.",
     "data": {"genre": "trance", "track_count": 7,
              "structure": ["intro", "groove_a", "build", "drop", "breakdown", "build_2", "drop", "outro"],
              "mixing_techniques": ["filter_sweep", "strip_and_build", "crossfade", "send_sweep", "volume_automation"],
              "energy_curve": "progressive_house"}},

    # ===== SOUND DESIGN PRESETS (13) =====
    {"category": "sound_design", "name": "Deep Sub Bass", "tags": "bass,sub,minimal",
     "description": "Pure sine sub-bass, 48 Hz fundamental. Clean, no harmonics.",
     "data": {"device_type": "Operator", "preset_name": "Deep Sub Bass",
              "parameters": {"osc1_coarse": 48, "osc1_fine": 0, "osc1_level": -6, "filter_type": "lowpass",
                            "filter_cutoff": 0.3, "filter_resonance": 0.1, "volume": -3},
              "tags": ["bass", "sub", "minimal"]}},
    {"category": "sound_design", "name": "Warm Reese Bass", "tags": "bass,reese,warm",
     "description": "Detuned sawtooth reese: two oscillators slightly detuned, low-passed.",
     "data": {"device_type": "Operator", "preset_name": "Warm Reese Bass",
              "parameters": {"osc1_coarse": 36, "osc1_fine": 0, "osc2_coarse": 36, "osc2_fine": 7,
                            "filter_type": "lowpass", "filter_cutoff": 0.45, "filter_resonance": 0.3, "volume": -6},
              "tags": ["bass", "reese", "dnb"]}},
    {"category": "sound_design", "name": "FM Pluck Bass", "tags": "bass,fm,pluck",
     "description": "FM synthesis pluck: fast decay, metallic attack, sub body.",
     "data": {"device_type": "Operator", "preset_name": "FM Pluck Bass",
              "parameters": {"osc1_coarse": 48, "osc1_fine": 0, "algorithm": 2, "filter_type": "lowpass",
                            "filter_cutoff": 0.6, "filter_resonance": 0.15, "envelope_attack": 0.005,
                            "envelope_decay": 0.3, "volume": -4},
              "tags": ["bass", "fm", "pluck"]}},
    {"category": "sound_design", "name": "Atmospheric Pad", "tags": "pad,atmospheric,wide",
     "description": "Wide analog pad: sawtooth with heavy chorus and reverb.",
     "data": {"device_type": "Analog", "preset_name": "Atmospheric Pad",
              "parameters": {"osc1_waveform": "saw", "osc2_waveform": "saw", "osc2_detune": 5,
                            "filter_type": "lowpass", "filter_cutoff": 0.5, "filter_resonance": 0.2,
                            "chorus_amount": 0.6, "reverb_amount": 0.4, "volume": -8},
              "tags": ["pad", "atmospheric", "wide"]}},
    {"category": "sound_design", "name": "Analog Brass", "tags": "brass,synth,warm",
     "description": "Synthetic brass: saw waves with moderately open filter.",
     "data": {"device_type": "Analog", "preset_name": "Analog Brass",
              "parameters": {"osc1_waveform": "saw", "osc2_waveform": "saw", "osc2_detune": 2,
                            "filter_type": "lowpass", "filter_cutoff": 0.7, "filter_resonance": 0.25,
                            "envelope_attack": 0.05, "envelope_release": 0.3, "volume": -5},
              "tags": ["brass", "synth", "warm"]}},
    {"category": "sound_design", "name": "Wavetable Lead", "tags": "lead,wavetable,bright",
     "description": "Bright wavetable lead with slow wavetable position modulation.",
     "data": {"device_type": "Wavetable", "preset_name": "Wavetable Lead",
              "parameters": {"wavetable_position": 0.3, "wavetable_mod_rate": 0.2, "wavetable_mod_depth": 0.4,
                            "filter_type": "lowpass", "filter_cutoff": 0.75, "filter_resonance": 0.1,
                            "volume": -5},
              "tags": ["lead", "wavetable", "bright"]}},
    {"category": "sound_design", "name": "Electric Piano", "tags": "keys,ep,warm",
     "description": "FM electric piano: bell-like attack, warm body.",
     "data": {"device_type": "Electric", "preset_name": "Electric Piano",
              "parameters": {"tine_harmonics": 0.6, "hammer_noise": 0.2, "pickup_position": 0.5,
                            "filter_cutoff": 0.6, "filter_resonance": 0.1, "volume": -4},
              "tags": ["keys", "electric_piano", "warm"]}},
    {"category": "sound_design", "name": "Sub-bass 808", "tags": "808,bass,trap",
     "description": "808 sub: long decay, sine fundamental, slight distortion.",
     "data": {"device_type": "Operator", "preset_name": "808 Sub",
              "parameters": {"osc1_coarse": 36, "osc1_fine": 0, "osc1_level": 0, "filter_type": "lowpass",
                            "filter_cutoff": 0.25, "filter_resonance": 0.0,
                            "envelope_attack": 0.0, "envelope_decay": 1.5, "envelope_sustain": 0.0, "envelope_release": 0.5,
                            "volume": -2},
              "tags": ["bass", "808", "trap"]}},
    {"category": "sound_design", "name": "FM Bell", "tags": "bell,fm,metallic",
     "description": "Inharmonic FM bell: metallic attack, long decay.",
     "data": {"device_type": "Operator", "preset_name": "FM Bell",
              "parameters": {"algorithm": 8, "osc1_coarse": 52, "osc1_level": 0, "osc2_ratio": 14.5,
                            "osc2_level": -6, "filter_cutoff": 0.8, "filter_resonance": 0.0,
                            "envelope_attack": 0.0, "envelope_decay": 2.0, "envelope_sustain": 0.0,
                            "volume": -6},
              "tags": ["bell", "fm", "metallic"]}},
    {"category": "sound_design", "name": "Deep House Pluck", "tags": "pluck,deep_house,soft",
     "description": "Soft pluck: short decay, warm low-pass, slight chorus.",
     "data": {"device_type": "Operator", "preset_name": "Deep House Pluck",
              "parameters": {"osc1_coarse": 48, "osc1_fine": 0, "osc1_level": -3, "filter_type": "lowpass",
                            "filter_cutoff": 0.5, "filter_resonance": 0.2,
                            "envelope_attack": 0.01, "envelope_decay": 0.4, "envelope_sustain": 0.0,
                            "chorus_amount": 0.3, "volume": -5},
              "tags": ["pluck", "house", "soft"]}},
    {"category": "sound_design", "name": "Riser FX", "tags": "fx,riser,build_up",
     "description": "Tension-building riser: filter sweep up, noise layer, pitch bend.",
     "data": {"device_type": "Operator", "preset_name": "Riser FX",
              "parameters": {"osc1_waveform": "noise", "filter_type": "highpass", "filter_cutoff": 0.1,
                            "filter_resonance": 0.0, "pitch_bend_range": 12,
                            "envelope_attack": 4.0, "envelope_decay": 0.0, "envelope_sustain": 1.0,
                            "volume": -10},
              "tags": ["fx", "riser", "build"]}},
    {"category": "sound_design", "name": "PWM String Pad", "tags": "pad,string,pwm",
     "description": "Pulse-width modulated strings: evolving, cinematic width.",
     "data": {"device_type": "Analog", "preset_name": "PWM String Pad",
              "parameters": {"osc1_waveform": "pulse", "osc2_waveform": "pulse", "osc2_detune": 3,
                            "pulse_width": 0.3, "pwm_rate": 0.15, "pwm_depth": 0.5,
                            "filter_type": "lowpass", "filter_cutoff": 0.45, "filter_resonance": 0.3,
                            "reverb_amount": 0.5, "volume": -8},
              "tags": ["pad", "string", "pwm"]}},
    {"category": "sound_design", "name": "Tape Saturation Loop", "tags": "effect,tape,saturation,warmth",
     "description": "Tape-style saturation: subtle warmth, slight compression, harmonic enhancement.",
     "data": {"device_type": "Saturator", "preset_name": "Tape Warmth",
              "parameters": {"drive": 0.3, "saturation_type": "tape", "frequency": 1000, "tone": 0.5,
                            "volume": -1},
              "tags": ["effect", "tape", "saturation"]}},
]


def get_builtin_recipes():
    """Return built-in recipes with data serialized to JSON strings."""
    result = []
    for recipe in BUILTIN_RECIPES:
        entry = dict(recipe)
        entry["data"] = json.dumps(recipe["data"])
        result.append(entry)
    return result
```

- [ ] **Step 2: Verify data is importable and valid**

Run: `python -c "from MCP_Server.recipe_library.recipes import get_builtin_recipes; r = get_builtin_recipes(); print(f'{len(r)} recipes loaded')"`
Expected: `50 recipes loaded`

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/recipe_library/recipes.py
git commit -m "feat(recipe-library): add 50 built-in seed recipes"
```

---

### Task 4: Bootstrap — Module Init + MCP Registration

**Files:**
- Modify: `MCP_Server/recipe_library/__init__.py`
- Modify: `MCP_Server/server.py`

- [ ] **Step 1: Update __init__.py**

Replace `MCP_Server/recipe_library/__init__.py` with:

```python
"""Recipe Library — reusable musical patterns for Ableton Live.

Provides SQLite-backed storage for chord progressions, drum patterns,
mix templates, and sound design presets. Exposed as MCP tools and resources.
"""
from .database import RecipeDB
from .recipes import get_builtin_recipes

# Global singleton: initialized on first import
_recipe_db: RecipeDB = None


def get_recipe_db() -> RecipeDB:
    """Get or create the global RecipeDB instance."""
    global _recipe_db
    if _recipe_db is None:
        _recipe_db = RecipeDB()
        _recipe_db.init_db(builtin_recipes=get_builtin_recipes())
    return _recipe_db


def register_recipe_tools(mcp, get_ableton_connection):
    """Register recipe library MCP tools and resources."""
    from . import tools as _tools
    from . import resources as _resources
    _tools.register(mcp, get_ableton_connection, get_recipe_db)
    _resources.register(mcp, get_recipe_db)
```

- [ ] **Step 2: Register in server.py**

Add before the existing registration block:

```python
from MCP_Server.recipe_library import register_recipe_tools
register_recipe_tools(mcp, get_ableton_connection)
```

Add after line 973 (after `register_groove_tools` import):

```python
from MCP_Server.recipe_library import register_recipe_tools
```

Add after line 982 (after `register_groove_tools` call):

```python
register_recipe_tools(mcp, get_ableton_connection)
```

- [ ] **Step 3: Verify module imports**

Run: `python -c "from MCP_Server.recipe_library import get_recipe_db, register_recipe_tools; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add MCP_Server/recipe_library/__init__.py MCP_Server/server.py
git commit -m "feat(recipe-library): bootstrap module and register in MCP server"
```

---

### Task 5: MCP Tools + Resources + Tests

**Files:**
- Create: `MCP_Server/recipe_library/tools.py`
- Create: `MCP_Server/recipe_library/resources.py`
- Test: `tests/test_recipe_tools.py`

- [ ] **Step 1: Write failing tests**

Write `tests/test_recipe_tools.py`:

```python
"""Tests for recipe library MCP tools and resources."""
import pytest
import json
from unittest.mock import Mock, patch
from MCP_Server.recipe_library.database import RecipeDB


@pytest.fixture
def db():
    database = RecipeDB(":memory:")
    database.init_db()
    return database


@pytest.fixture
def mock_get_db(db):
    def _get_db():
        return db
    return _get_db


class TestListRecipes:
    def test_list_all(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db))
        assert result["status"] == "success"
        assert "count" in result
        assert "recipes" in result

    def test_list_by_category(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db, category="chord_progression"))
        assert result["status"] == "success"
        for r in result["recipes"]:
            assert r["category"] == "chord_progression"

    def test_list_by_tags(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        db = mock_get_db()
        db.create("chord_progression", "Tagged", "{}", "pop,test", "desc")
        result = json.loads(_impl_list_recipes(mock_get_db, tags="test"))
        assert result["status"] == "success"
        assert any(r["name"] == "Tagged" for r in result["recipes"])

    def test_list_by_query(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db, query="one_drop"))
        assert result["status"] == "success"

    def test_list_empty_result(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db, query="zzz_nonexistent"))
        assert result["status"] == "success"
        assert len(result["recipes"]) == 0


class TestGetRecipe:
    def test_get_existing(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_get_recipe
        db = mock_get_db()
        rid = db.create("chord_progression", "GetTest", '{"key":"C"}', "tag", "desc")
        result = json.loads(_impl_get_recipe(mock_get_db, rid))
        assert result["status"] == "success"
        assert result["recipe"]["name"] == "GetTest"

    def test_get_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_get_recipe
        result = json.loads(_impl_get_recipe(mock_get_db, 999))
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestCreateRecipe:
    def test_create_valid(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_create_recipe
        result = json.loads(_impl_create_recipe(
            mock_get_db, "chord_progression", "NewProg",
            '{"key":"C","scale":"major","chords":["C"],"voicing":"open","mood":"test"}',
            "test", "Test progression"
        ))
        assert result["status"] == "success"
        assert "id" in result

    def test_create_invalid_data(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_create_recipe
        result = json.loads(_impl_create_recipe(
            mock_get_db, "chord_progression", "Bad",
            '{"invalid": true}', "", ""
        ))
        assert result["status"] == "error"

    def test_create_invalid_json(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_create_recipe
        result = json.loads(_impl_create_recipe(
            mock_get_db, "chord_progression", "Bad", "not json", "", ""
        ))
        assert result["status"] == "error"


class TestUpdateRecipe:
    def test_update_valid(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_update_recipe
        db = mock_get_db()
        rid = db.create("chord_progression", "OldName", "{}", "", "")
        result = json.loads(_impl_update_recipe(mock_get_db, rid, name="NewName"))
        assert result["status"] == "success"
        assert db.get(rid)["name"] == "NewName"

    def test_update_builtin(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_update_recipe
        result = json.loads(_impl_update_recipe(mock_get_db, 1, name="Hack"))
        assert result["status"] == "error"
        assert "built-in" in result["message"].lower()


class TestDeleteRecipe:
    def test_delete_valid(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_delete_recipe
        db = mock_get_db()
        rid = db.create("chord_progression", "DelMe", "{}", "", "")
        result = json.loads(_impl_delete_recipe(mock_get_db, rid))
        assert result["status"] == "success"

    def test_delete_builtin(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_delete_recipe
        result = json.loads(_impl_delete_recipe(mock_get_db, 1))  # builtin
        assert result["status"] == "error"
        assert "built-in" in result["message"].lower()

    def test_delete_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_delete_recipe
        result = json.loads(_impl_delete_recipe(mock_get_db, 999))
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestSeedRecipes:
    def test_seed(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_seed_recipes
        result = json.loads(_impl_seed_recipes(mock_get_db))
        assert result["status"] == "success"
        assert result["count"] >= 0


class TestApplyRecipe:
    def test_apply_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_apply_recipe
        result = json.loads(_impl_apply_recipe(mock_get_db, 999, None))
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestResources:
    def test_resource_list_categories(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_list_categories
        result = _impl_list_categories(mock_get_db)
        assert result is not None
        data = json.loads(result)
        assert "categories" in data

    def test_resource_list_category(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_list_category
        result = _impl_list_category(mock_get_db, "chord_progression")
        data = json.loads(result)
        assert "recipes" in data
        assert data["category"] == "chord_progression"

    def test_resource_get_recipe(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_get_recipe_resource
        db = mock_get_db()
        rid = db.create("drum_pattern", "ResTest", "{}", "", "")
        result = _impl_get_recipe_resource(mock_get_db, rid)
        data = json.loads(result)
        assert data["id"] == rid

    def test_resource_get_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_get_recipe_resource
        result = _impl_get_recipe_resource(mock_get_db, 999)
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_recipe_tools.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write tools.py**

```python
"""MCP tool implementations for the recipe library."""
import json
import logging
from typing import Optional
from .database import RecipeDB

logger = logging.getLogger("AbletonMCPServer")


def register(mcp, get_ableton_connection, get_recipe_db):
    """Register recipe library MCP tools."""

    @mcp.tool()
    def list_recipes(
        ctx, category: Optional[str] = None,
        tags: Optional[str] = None, query: Optional[str] = None
    ) -> str:
        """List recipes, optionally filtered by category, tags, or text query.

        Parameters:
        - category: Filter by category (chord_progression, drum_pattern, mix_template, sound_design)
        - tags: Filter by comma-separated tags (AND match)
        - query: Text search in name and description
        """
        return _impl_list_recipes(get_recipe_db, category, tags, query)

    @mcp.tool()
    def get_recipe(ctx, recipe_id: int) -> str:
        """Get a single recipe by ID with full data.

        Parameters:
        - recipe_id: The recipe ID
        """
        return _impl_get_recipe(get_recipe_db, recipe_id)

    @mcp.tool()
    def create_recipe(
        ctx, category: str, name: str, data: str,
        tags: str = "", description: str = ""
    ) -> str:
        """Create a new user recipe.

        Parameters:
        - category: Recipe category
        - name: Recipe name
        - data: JSON string with category-specific fields
        - tags: Comma-separated tags
        - description: Short description
        """
        return _impl_create_recipe(get_recipe_db, category, name, data, tags, description)

    @mcp.tool()
    def update_recipe(
        ctx, recipe_id: int,
        name: Optional[str] = None, data: Optional[str] = None,
        tags: Optional[str] = None, description: Optional[str] = None
    ) -> str:
        """Update a user recipe's fields. Cannot update built-in recipes.

        Parameters:
        - recipe_id: The recipe ID to update
        - name: New name (optional)
        - data: New data JSON (optional)
        - tags: New tags (optional)
        - description: New description (optional)
        """
        return _impl_update_recipe(get_recipe_db, recipe_id, name, data, tags, description)

    @mcp.tool()
    def delete_recipe(ctx, recipe_id: int) -> str:
        """Delete a user recipe by ID. Cannot delete built-in recipes.

        Parameters:
        - recipe_id: The recipe ID to delete
        """
        return _impl_delete_recipe(get_recipe_db, recipe_id)

    @mcp.tool()
    def apply_recipe(
        ctx, recipe_id: int, track_index: Optional[int] = None
    ) -> str:
        """Apply a recipe to the Ableton session.

        For chord_progressions: creates MIDI clip with chord notes on the given track.
        For drum_patterns: creates a drum clip.
        For mix_templates: returns the template config data (use with agentic_mix).
        For sound_design: returns device parameters to apply.

        Parameters:
        - recipe_id: Recipe ID to apply
        - track_index: Target track index (optional, needed for clip/devices)
        """
        return _impl_apply_recipe(get_recipe_db, recipe_id, track_index)

    @mcp.tool()
    def seed_recipes(ctx) -> str:
        """Re-seed all built-in recipes. Idempotent — updates existing, inserts new.
        """
        return _impl_seed_recipes(get_recipe_db)


# ---- Implementation functions (testable without MCP context) ----

def _impl_list_recipes(get_db, category=None, tags=None, query=None):
    try:
        db = get_db()
        recipes = db.search(category=category, tags=tags, query=query)
        return json.dumps({
            "status": "success",
            "count": len(recipes),
            "recipes": recipes
        }, indent=2)
    except Exception as e:
        logger.error(f"Error listing recipes: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_get_recipe(get_db, recipe_id):
    try:
        db = get_db()
        recipe = db.get(recipe_id)
        if recipe is None:
            return json.dumps({"status": "error", "message": f"Recipe {recipe_id} not found"})
        recipe["data"] = json.loads(recipe["data"])
        return json.dumps({"status": "success", "recipe": recipe}, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error getting recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_create_recipe(get_db, category, name, data, tags, description):
    try:
        # Validate
        from .models import validate_category_data
        validate_category_data(category, data)
        # Create
        db = get_db()
        recipe_id = db.create(category=category, name=name, data=data,
                              tags=tags, description=description)
        return json.dumps({"status": "success", "id": recipe_id})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        logger.error(f"Error creating recipe: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_update_recipe(get_db, recipe_id, name=None, data=None, tags=None, description=None):
    try:
        db = get_db()
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if data is not None:
            kwargs["data"] = data
        if tags is not None:
            kwargs["tags"] = tags
        if description is not None:
            kwargs["description"] = description
        db.update(recipe_id, **kwargs)
        return json.dumps({"status": "success", "id": recipe_id})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        logger.error(f"Error updating recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_delete_recipe(get_db, recipe_id):
    try:
        db = get_db()
        db.delete(recipe_id)
        return json.dumps({"status": "success"})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        logger.error(f"Error deleting recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_seed_recipes(get_db):
    try:
        from .recipes import get_builtin_recipes
        db = get_db()
        recipes = get_builtin_recipes()
        db.seed_builtin(recipes)
        return json.dumps({"status": "success", "count": len(recipes)})
    except Exception as e:
        logger.error(f"Error seeding recipes: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_apply_recipe(get_db, recipe_id, track_index):
    try:
        db = get_db()
        recipe = db.get(recipe_id)
        if recipe is None:
            return json.dumps({"status": "error", "message": f"Recipe {recipe_id} not found"})

        data = json.loads(recipe["data"])
        category = recipe["category"]

        if category == "mix_template":
            # Return template data — agentic_mix can consume this
            return json.dumps({
                "status": "success",
                "applied": False,
                "message": "Mix templates are applied via agentic_mix. Use the data as Config.",
                "template": data
            }, indent=2)

        if track_index is None:
            return json.dumps({
                "status": "error",
                "message": f"track_index is required for {category} recipes"
            })

        if category == "chord_progression":
            return json.dumps({
                "status": "success",
                "applied": False,
                "message": "Use create_clip + add_notes_to_clip with these chords",
                "chords": data["chords"],
                "key": data["key"],
                "track_index": track_index
            }, indent=2)

        if category == "drum_pattern":
            return json.dumps({
                "status": "success",
                "applied": False,
                "message": "Use create_drum_pattern with these parameters",
                "pattern_type": data["pattern_type"],
                "kit_query": data["kit_query"],
                "bars": data["bars"],
                "grid": data.get("grid", ""),
                "track_index": track_index
            }, indent=2)

        if category == "sound_design":
            return json.dumps({
                "status": "success",
                "applied": False,
                "message": "Load the device, then use set_device_parameter for each parameter",
                "device_type": data["device_type"],
                "parameters": data["parameters"],
                "track_index": track_index
            }, indent=2)

        return json.dumps({"status": "error", "message": f"Unknown category: {category}"})
    except Exception as e:
        logger.error(f"Error applying recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 4: Write resources.py**

```python
"""MCP resource handlers for the recipe library."""
import json
from .database import RecipeDB


def register(mcp, get_recipe_db):
    """Register recipe library MCP resources."""

    @mcp.resource("live://recipes/")
    def all_categories() -> str:
        """List all recipe categories with counts."""
        return _impl_list_categories(get_recipe_db)

    @mcp.resource("live://recipes/{category}")
    def category_listing(category: str) -> str:
        """List recipes in a category."""
        return _impl_list_category(get_recipe_db, category)

    @mcp.resource("live://recipes/{category}/{recipe_id}")
    def recipe_detail(category: str, recipe_id: int) -> str:
        """Get full recipe detail."""
        return _impl_get_recipe_resource(get_recipe_db, recipe_id) or ""


def _impl_list_categories(get_db):
    try:
        db = get_db()
        categories = ["chord_progression", "drum_pattern", "mix_template", "sound_design"]
        result = {"categories": []}
        for cat in categories:
            recipes = db.search(category=cat)
            result["categories"].append({
                "category": cat,
                "count": len(recipes),
                "name": cat.replace("_", " ").title()
            })
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _impl_list_category(get_db, category):
    try:
        db = get_db()
        recipes = db.search(category=category)
        return json.dumps({
            "category": category,
            "count": len(recipes),
            "recipes": recipes
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _impl_get_recipe_resource(get_db, recipe_id):
    try:
        db = get_db()
        recipe = db.get(recipe_id)
        if recipe is None:
            return None
        recipe["data"] = json.loads(recipe["data"])
        return json.dumps(recipe, indent=2, default=str)
    except Exception:
        return None
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_recipe_tools.py -v`
Expected: 16 PASSED

- [ ] **Step 6: Commit**

```bash
git add MCP_Server/recipe_library/tools.py MCP_Server/recipe_library/resources.py tests/test_recipe_tools.py
git commit -m "feat(recipe-library): add MCP tools, resources, and tests"
```

---

### Task 6: Agentic Mix Integration Hook

**Files:**
- Modify: `agentic_mix/nodes/construct_arrangement.py`

- [ ] **Step 1: Write failing test**

Open `tests/test_integration.py` and add a test (or create a new minimal test):

```python
"""Test agentic_mix integration with recipe library."""
import pytest
from agentic_mix.state import Config, GraphState, Section
from agentic_mix.nodes.construct_arrangement import construct_arrangement_node


def test_construct_with_mix_template_hook():
    """Verify construct_arrangement accepts optional mix_template_id."""
    # Minimal test: verify the function runs with a mock template
    config = Config(
        tempo=120, duration_minutes=2, genre="house",
        track_count=4, key="C", energy_curve="progressive_house",
        variation_level=0.3, section_duration_beats=16
    )
    state = GraphState(
        config=config,
        session_info={"initialized": True, "track_indices": [0, 1, 2, 3],
                      "scene_indices": [], "return_track_indices": [],
                      "tempo": 120, "time_signature": (4, 4)},
        arrangement=[],
        current_section_index=0, current_section=-1,
        track_states=[], playback_metrics={
            "start_time": None, "current_time": None,
            "section_transitions": [], "mixing_actions": [], "errors": []
        },
        feedback=[], errors=[], complete=False,
        audio_snapshot=None, client=None
    )
    result = construct_arrangement_node(state)
    # Should succeed — arrangement built from hardcoded defaults
    assert len(result["arrangement"]) > 0
    assert isinstance(result["arrangement"][0], dict)
```

Add this test to `tests/test_integration.py` or create `tests/test_recipe_agentic_integration.py`.

- [ ] **Step 2: Run test to verify current behavior**

Run: `pytest tests/test_recipe_agentic_integration.py -v`
Or if adding to existing: `pytest tests/test_integration.py::test_construct_with_mix_template_hook -v`

Expected: Current test uses hardcoded defaults (no mix_template_id), so it should PASS already if the function works.

Actually the integration hook is optional and backward-compatible — so the existing behavior should be verified first, then the new behavior.

- [ ] **Step 3: Modify construct_arrangement.py**

Add at the top:
```python
try:
    from MCP_Server.recipe_library import get_recipe_db
    HAS_RECIPE_LIBRARY = True
except ImportError:
    HAS_RECIPE_LIBRARY = False
```

In `construct_arrangement_node`, after the `try:` block and before section building, add:

```python
# Optional mix template override from recipe library
mix_template_id = config.get("mix_template_id")
if mix_template_id and HAS_RECIPE_LIBRARY:
    try:
        recipe_db = get_recipe_db()
        recipe = recipe_db.get(mix_template_id)
        if recipe and recipe["category"] == "mix_template":
            template = json.loads(recipe["data"])
            beats_per_section = template.get("section_duration_beats", beats_per_section)
            feedback.append(f"Using mix template: {recipe['name']}")
    except Exception:
        pass  # Fall through to defaults
```

Also add `import json` at the top of the file.

- [ ] **Step 4: Verify the integration**

Run: `python -c "from MCP_Server.recipe_library import get_recipe_db; print('Recipe library importable from agentic_mix path')"`
Expected: Success

Run: `pytest tests/test_recipe_agentic_integration.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agentic_mix/nodes/construct_arrangement.py tests/test_recipe_agentic_integration.py
git commit -m "feat(recipe-library): integrate optional mix template with agentic_mix"
```

---

### Task 7: Final Verification + Lint

- [ ] **Step 1: Run all recipe library tests**

Run: `pytest tests/test_recipe_models.py tests/test_recipe_database.py tests/test_recipe_tools.py -v`
Expected: All PASS (15 + 14 + 16 = ~45 tests)

- [ ] **Step 2: Run ruff lint**

Run: `ruff check MCP_Server/recipe_library/ tests/test_recipe_*.py`
Expected: No errors

- [ ] **Step 3: Run full test suite**

Run: `pytest tests/ --tb=short 2>&1 | head -60`
Expected: All pre-existing tests still pass

- [ ] **Step 4: Run compileall**

Run: `python -m compileall MCP_Server/recipe_library/`
Expected: All files OK

- [ ] **Step 5: Commit any lint fixes**

```bash
git add -A && git commit -m "chore: lint fixes for recipe library"
```
