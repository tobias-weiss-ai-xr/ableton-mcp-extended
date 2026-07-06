# Sprint 09: Project Templates + Session Management

**Theme:** Save, load, version, and diff complete session configurations.
**Est. days:** 4 | **New tools:** 4-5 | **Risk:** Medium
**Dependencies:** Sprint 03 (prompts reference templates)

## Goal
Let users save complete session templates (track layout, devices, routing, patterns), reload them later, diff two sessions, and tag snapshots for version recall. This turns Ableton into a project management tool.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/session_templates.py` | Create | Template serialization + loading |
| `MCP_Server/session_templates_db.py` | Create | SQLite storage for templates + tags |
| `MCP_Server/server.py` | Modify | Import + register template tools |
| `MCP_Server/knowledge/templates/` | Create | Built-in template library |
| `MCP_Server/knowledge/templates/4_on_floor.json` | Create | 4-on-the-floor template |
| `MCP_Server/knowledge/templates/dub_setup.json` | Create | Dub reggae template |
| `MCP_Server/knowledge/templates/ambient_pad.json` | Create | Ambient template |
| `MCP_Server/knowledge/templates/dj_rig.json` | Create | DJ setup template |
| `MCP_Server/knowledge/templates/techno_minimal.json` | Create | Minimal techno template |
| `MCP_Server/knowledge/templates/sound_design.json` | Create | Sound design workstation |
| `MCP_Server/knowledge/templates/studio_mastering.json` | Create | Mastering chain template |
| `tests/test_session_templates.py` | Create | Template serialization tests |

## Deliverables

### 9.1 Template Schema
Each template is a JSON file:
```json
{
  "template_name": "4_on_floor",
  "version": "1.0",
  "genre": "house",
  "description": "Classic 4-on-the-floor setup with drums, bass, chords, lead",
  "bpm": 125,
  "time_signature": [4, 4],
  "tracks": [
    {
      "name": "Kick",
      "type": "midi",
      "device_chain": [
        {"device": "Drum Rack", "preset_query": "query:909 Kick"}
      ],
      "patterns": [{"pattern": "techno_4x4", "bars": 4, "scene": 0}],
      "volume": 0.85,
      "pan": 0.0,
      "sends": {"reverb": 0.0, "delay": 0.0}
    },
    {
      "name": "Bass",
      "type": "midi",
      "device_chain": [
        {"device": "Operator", "preset_query": "query:Deep Sub Bass"}
      ],
      "patterns": [],
      "volume": 0.75,
      "pan": 0.0
    }
  ],
  "return_tracks": [
    {"name": "Reverb", "device": "Hybrid Reverb", "sends": {"reverb": 1.0}},
    {"name": "Delay", "device": "Simple Delay", "sends": {"delay": 1.0, "reverb": 0.3}}
  ],
  "master": {"volume": 0.9, "device": "Limiter"},
  "routing": {"master_output": "Master"},
  "scenes": [
    {"name": "Intro", "bars": 8, "tracks_active": [0]},
    {"name": "Main", "bars": 16, "tracks_active": [0, 1, 2, 3, 4]},
    {"name": "Break", "bars": 8, "tracks_active": [2, 3]},
    {"name": "Drop", "bars": 16, "tracks_active": [0, 1, 2, 3, 4, 5]}
  ]
}
```

### 9.2 Template Storage (`session_templates_db.py`)
SQLite-backed storage:
- Database at `~/.ableton-mcp-templates.db`
- Tables: `templates`, `tags`, `template_tags`
- CRUD operations: `list_templates()`, `get_template(name)`, `save_template(template, name)`, `delete_template(name)`, `tag_template(template_name, tag)`
- CLI/recovery: `sqlite3 ~/.ableton-mcp-templates.db .dump`

### 9.3 Template Library (7 built-in templates)
| Template | Genre | Tracks | Description |
|----------|-------|--------|-------------|
| `4_on_floor` | House | 6 | Classic house setup |
| `dub_setup` | Dub | 5 | Dub reggae with send effects |
| `ambient_pad` | Ambient | 4 | Evolving pad textures |
| `dj_rig` | DJ | 3 | DJ setup with crossfader |
| `techno_minimal` | Techno | 5 | Minimal techno |
| `sound_design` | General | 3 | Sound design workstation |
| `studio_mastering` | Mastering | 1 | Mastering chain |

### 9.4 Template Engine (`session_templates.py`)

**Function: `apply_template(template: dict) -> str`**
- Creates tracks per template definition
- Loads devices for each chain
- Sets track properties (volume, pan, sends)
- Creates patterns where defined
- Configures return tracks
- Sets master + routing
- Creates scenes
- Returns summary JSON

**Function: `capture_session() -> dict`**
- Reads current session state via existing get_* tools
- Serializes to template format
- Captures: all tracks with devices/params, patterns, routing, tempo, scene structure

**Function: `diff_templates(template_a: dict, template_b: dict) -> str`**
- Compares two templates structurally
- Returns diff: added/removed/modified tracks, devices, parameters
- Ignores: clip content, exact parameter values (compares structure)

### 9.5 MCP Tools

**Tool: `save_session_template`**
```
(ctx, name: str, description: str = "") -> str
```
- Captures current session state
- Saves to template database
- Returns: template summary

**Tool: `load_session_template`**
```
(ctx, name: str) -> str
```
- Loads template from database or built-in library
- Applies to current session (clears first: confirm prompt)
- Returns: session setup summary

**Tool: `list_session_templates`**
```
(ctx, genre: str = "", tag: str = "") -> str
```
- Lists available templates with metadata
- Filter by genre, tag, or both
- Returns: array of {name, genre, description, track_count, version}

**Tool: `diff_sessions`**
```
(ctx, template_a: str, template_b: str) -> str
```
- Loads two templates by name
- Computes structural diff
- Returns: added/removed/modified sections

**Tool: `tag_session`**
```
(ctx, tag_name: str) -> str
```
- Tags current session snapshot
- Store tag + timestamp + session representation
- `get_session_tags()` to list all tags
- `load_tagged_session(tag_name)` to restore

## API Surface

### New Tools
| Tool | Signature | Returns |
|------|-----------|---------|
| `save_session_template` | (name, description) | Template summary |
| `load_session_template` | (name) | Session setup summary |
| `list_session_templates` | (genre, tag) | Template list |
| `diff_sessions` | (template_a, template_b) | Structural diff |
| `tag_session` | (tag_name) | Tag confirmation |
| `get_session_tags` | () | Tag list |
| `load_tagged_session` | (tag_name) | Session recovery |

## Acceptance Criteria
```bash
# 7 built-in templates
ls MCP_Server/knowledge/templates/*.json  # 7 files

# Template serialization round-trip
python -c "
from MCP_Server.session_templates import diff_templates, apply_template
tmpl_a = {'tracks': [{'name': 'Kick', 'type': 'midi'}]}
tmpl_b = {'tracks': [{'name': 'Kick', 'type': 'midi'}, {'name': 'Bass', 'type': 'midi'}]}
diff = diff_templates(tmpl_a, tmpl_b)
assert 'added' in diff
assert 'Bass' in str(diff)
print('Template diff OK')
"

# Tool registration
grep -c "def save_session_template\|def load_session_template\|def list_session_templates\|def diff_sessions\|def tag_session" MCP_Server/server.py
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Template references device FileIds that don't exist on other systems | High | Template stores query strings, not FileIds; resolution at load time |
| Template has invalid device chains | Medium | Graceful per-track error; skip failed devices, continue |
| Large template save takes long | Low | Async with progress; max 5s timeout |
| SQLite corruption | Low | Include recovery in docs; schema includes version field |

## Must NOT Do
- Do NOT store actual audio or .als files in templates (metadata only)
- Do NOT attempt cross-machine template compatibility (FileIds differ)
- Do NOT auto-delete existing templates on name collision
- Do NOT store template data in git (SQLite is user-local; templates dir is source-controlled)
