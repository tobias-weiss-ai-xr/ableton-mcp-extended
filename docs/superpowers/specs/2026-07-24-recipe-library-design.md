# Recipe Library for Ableton MCP Extended

**Date**: July 24, 2026
**Priority**: P2 (Competitive differentiator)
**Status**: Design Approved

## Overview

A SQLite-backed recipe library providing reusable musical patterns (chord progressions, drum patterns, genre mix templates, sound design presets) as MCP resources and tools. Users browse, apply, and extend recipes at runtime — no file editing required. Follows the existing `browser_cache.py` pattern.

## 1. Data Model

### 1.1 SQLite Schema

Single table `recipes`:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK AUTOINCREMENT | Unique recipe ID |
| `category` | TEXT | NOT NULL | `chord_progression`, `drum_pattern`, `mix_template`, `sound_design` |
| `name` | TEXT | NOT NULL | Human-readable name |
| `tags` | TEXT | | Comma-separated keywords for search |
| `description` | TEXT | | Short description (1-3 sentences) |
| `data` | TEXT | NOT NULL | JSON payload, schema varies by category |
| `created_at` | TEXT | NOT NULL | ISO 8601 datetime |
| `updated_at` | TEXT | NOT NULL | ISO 8601 datetime |
| `is_builtin` | INTEGER | NOT NULL DEFAULT 0 | 1 = seeded, 0 = user-created |

**Indexes**: `(category)`, `(tags)`, `(category, name)` for search.

### 1.2 Category JSON Schemas

**Chord Progression:**
```json
{
  "key": "C",
  "scale": "major",
  "chords": ["C", "Am", "F", "G"],
  "voicing": "open",
  "mood": "uplifting"
}
```

**Drum Pattern:**
```json
{
  "pattern_type": "one_drop",
  "kit_query": "query:Drums#FileId_58622",
  "bars": 4,
  "grid": "|X---|---X---|---X---|---X---|",
  "tempo_range": [70, 90],
  "mood": "dub"
}
```

**Mix Template:**
```json
{
  "genre": "deep_house",
  "track_count": 6,
  "structure": ["intro", "groove_a", "build", "drop", "breakdown", "groove_b", "outro"],
  "mixing_techniques": ["bass_forward", "crossfade", "filter_sweep", "send_sweep", "strip_and_build"],
  "energy_curve": "progressive_house",
  "description": "Warm deep house arrangement with extended breakdown"
}
```

**Sound Design:**
```json
{
  "device_type": "Operator",
  "preset_name": "Deep Sub Bass",
  "parameters": {
    "osc1_coarse": 48,
    "osc1_fine": 0,
    "filter_type": "lowpass",
    "filter_cutoff": 0.4,
    "filter_resonance": 0.2,
    "envelope_attack": 0.01,
    "envelope_release": 0.5
  },
  "tags": ["bass", "sub", "minimal"]
}
```

### 1.3 Validation Rules

- `category` must be one of the four valid values
- `name` must be non-empty (unique per category, but not enforced at DB level — users can have duplicate-named recipes)
- `data` must be valid JSON and pass category-specific schema validation
- Built-in recipes (`is_builtin=1`) cannot be deleted or updated via MCP tools

## 2. File Structure

```
MCP_Server/recipe_library/
├── __init__.py              # Exports public API, module entry point
├── database.py              # RecipeDB class — SQLite CRUD, search, init
├── models.py                # TypedDicts + JSON schema validators per category
├── recipes.py               # ~50 built-in seed recipes
├── tools.py                 # MCP tool registrations (@server.tool)
└── resources.py             # MCP resource handlers (@server.resource)
```

### 2.1 Module Responsibilities

**`database.py`** — `RecipeDB` class wrapping SQLite:
- `__init__(db_path)` — Opens/creates SQLite, ensures schema
- `init_db()` — Create tables if not exist, seed built-in recipes on first run
- `search(category, tags, query)` — Search with optional filters. Tags is a comma-separated string (AND match — all specified tags must be present). Query is LIKE-matched against name/description.
- `get(recipe_id)` — Get single recipe by ID
- `create(category, name, data, tags, description)` — Insert user recipe
- `update(recipe_id, **kwargs)` — Update user recipe fields
- `delete(recipe_id)` — Delete user recipe (reject built-in)
- `seed_builtin()` — Insert/update built-in recipes from `recipes.py` (idempotent, upsert by name+category)

**`models.py`** — TypedDicts for each category:
- `ChordProgression`, `DrumPattern`, `MixTemplate`, `SoundDesign`
- `validate_category_data(category, data)` — Raises `ValueError` on invalid data
- `RecipeSummary` — Lightweight result for search listings

**`recipes.py`** — Static list of ~50 built-in recipes:
- 15 chord progressions (pop, deep house, techno, dub techno, ambient, jazz, lo-fi, minimal, drum & bass, trance)
- 12 drum patterns (existing 6 variants + rockers, half_time, shuffle, breakbeat_core, footwork, trap)
- 10 mix templates (deep house, techno, dub, ambient, pop, drum & bass, minimal, hip-hop, lo-fi, trance)
- 13 sound design presets (Operator bass x3, Analog pad x2, Wavetable lead, Electric piano, Sub-bass, FM bell, Pluck, Brass, Strings, Percussion)

**`tools.py`** — All MCP tool functions (imported by `server.py` or `advanced_tools.py`):
- `list_recipes(category, tags, query)` — Returns list of `RecipeSummary`
- `get_recipe(recipe_id)` — Returns full recipe with data JSON
- `create_recipe(category, name, data, tags, description)` — Returns new recipe ID
- `update_recipe(recipe_id, name, data, tags, description)` — Returns updated recipe
- `delete_recipe(recipe_id)` — Returns success/error
- `apply_recipe(recipe_id, track_index, target)` — Apply recipe to Ableton session
- `seed_recipes()` — Re-seed built-in recipes (admin tool)

**`resources.py`** — MCP resource handlers:
- `live://recipes/` — List all categories with recipe counts
- `live://recipes/{category}` — List recipes in category
- `live://recipes/{category}/{id}` — Recipe detail (full JSON)

## 3. MCP Surface

### 3.1 Tools

| Tool | Arguments | Returns |
|------|-----------|---------|
| `list_recipes` | `category` (optional), `tags` (optional), `query` (optional) | `List[RecipeSummary]` |
| `get_recipe` | `recipe_id: int` | `Recipe` with full data |
| `create_recipe` | `category, name, data, tags, description` | `{id: int}` |
| `update_recipe` | `recipe_id, name?, data?, tags?, description?` | `{id: int}` |
| `delete_recipe` | `recipe_id: int` | `{success: bool}` |
| `apply_recipe` | `recipe_id, track_index, target` (optional) | `{result: str}` |
| `seed_recipes` | None | `{count: int}` |

### 3.2 Resources

- `live://recipes/` — Category overview
- `live://recipes/{category}` — Recipe listing
- `live://recipes/{category}/{id}` — Full recipe JSON

### 3.3 `apply_recipe` Behavior

| Category | Action |
|----------|--------|
| `chord_progression` | Create MIDI clip on track with chord notes, quantized to grid |
| `drum_pattern` | Create drum clip on track at given scene_index using `create_drum_pattern` |
| `mix_template` | Configure agentic_mix `Config` — overlay genre, structure, techniques, energy_curve onto the config |
| `sound_design` | Load device matching `device_type`, apply `parameters` via `set_device_parameter` |

## 4. Integration with Agentic Mix

### 4.1 Mix Template Hook

`agentic_mix/nodes/construct_arrangement.py` gets an optional path:

```python
# In construct_arrangement_node:
mix_template_id = config.get("mix_template_id")
if mix_template_id:
    recipe = recipe_db.get(mix_template_id)
    template = json.loads(recipe["data"])
    # Override structure, techniques, energy_curve from template
    structure = template["structure"]
    techniques = template["mixing_techniques"]
    energy_curve = template["energy_curve"]
```

This is a non-breaking change — when `mix_template_id` is absent, existing hardcoded defaults apply.

### 4.2 Recipe Library Initialization

The recipe DB is initialized once at module import time:

```python
# In __init__.py
from .database import RecipeDB
recipe_db = RecipeDB()
recipe_db.init_db()
```

`MCP_Server/server.py` imports `recipe_library` which triggers init. The `recipe_db` instance is accessible to tools and resources.

## 5. Built-in Seed Strategy

### 5.1 First-Run Seeding

`init_db()` checks if `recipes` table is empty. If so, inserts all recipes from `recipes.py`. Idempotent — does not re-seed on subsequent starts.

`seed_recipes()` tool upserts all built-in recipes (by name+category), useful after manual DB deletion or corruption.

### 5.2 Built-in Protection

The `RecipeDB` class enforces:
- `delete()` raises `ValueError` if `is_builtin == 1`
- `update()` raises `ValueError` if `is_builtin == 1`
- These checks happen at the DB layer, not just the tool layer

## 6. Error Handling

| Situation | Behavior |
|-----------|----------|
| Recipe not found by ID | `get()` returns `None`, tools return "Recipe N not found" |
| Category validation fails | `create()/update()` raises `ValueError`, tools format as clear message |
| SQLite failure | Caught, logged, tool returns error string |
| Delete built-in recipe | `ValueError`: "Cannot delete built-in recipe N" |
| Update built-in recipe | `ValueError`: "Cannot update built-in recipe N" |
| DB file missing/unwritable | `RecipeDB` creates it; if fails, logs error and tools return "Recipe library unavailable" |
| Invalid JSON in `data` field | `json.loads` on retrieval returns error to user |

## 7. Testing

### 7.1 Unit Tests

| Test File | Tests |
|-----------|-------|
| `test_database.py` | DB CRUD, search, built-in isolation, seeding idempotency, edge cases |
| `test_models.py` | Schema validation pass/fail per category, TypedDict construction |
| `test_tools.py` | Tool function behavior with mocking RecipeDB |

### 7.2 Test Strategy

- SQLite `:memory:` for all DB tests
- Mock `RecipeDB` for tool tests
- Test data: minimal inline dicts (not relying on `recipes.py` seed data)
- Coverage: CRUD operations, search filtering, error paths, built-in protection

## 8. Out of Scope

- Direct audio analysis integration (handled by P1 audio feedback loop)
- Recipe sharing/export between Live sets
- Auto-tagging or machine learning on recipes
- Advanced recipe composition (mixing multiple recipes)
- Full agentic_mix integration beyond the documented hooks
