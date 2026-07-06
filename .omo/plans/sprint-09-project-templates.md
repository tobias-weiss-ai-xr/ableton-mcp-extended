# Sprint 09: Project Templates + Session Management

## TL;DR (For humans)

**What you'll get:** Save any Ableton setup as a named template and reload it later — tracks, devices, routing, patterns, scenes. Recall past sessions by tag. Compare two session configurations to see what changed. 7 built-in templates (house, dub, ambient, DJ, techno, sound design, mastering).

**Why this approach:** The #1 time-sink in Live is rebuilding session setups. Templates capture the structural essence (tracks → devices → routing → patterns) without storing audio. SQLite for user templates, JSON for built-in library.

**What it will NOT do:** Store audio files. Save exact clip content. Auto-delete templates on name collision. Support cross-machine template sharing (FileIds differ).

**Effort:** Medium (4 days) | **Risk:** Medium (template references may not resolve on other systems)

Your next move: Approve and `$start-work` to begin.

---

> TL;DR (machine): Medium effort, Medium risk. Template schema (JSON), SQLite storage, 7 built-in templates, template engine (apply/capture/diff), 7 MCP tools. New files: session_templates.py, session_templates_db.py, 7 JSON templates, tests.

## Scope

### Must have
- Template JSON schema with tracks, devices, patterns, routing, scenes, tempo, time signature
- SQLite database at `~/.ableton-mcp-templates.db` with `templates`, `tags`, `template_tags` tables
- 7 built-in templates in `MCP_Server/knowledge/templates/`
- `session_templates.py` — `apply_template()`, `capture_session()`, `diff_templates()`
- `session_templates_db.py` — CRUD for templates + tags
- 7 MCP tools: save/load/list/diff/tag/load_tagged/get_tags
- No new pip dependencies (stdlib: sqlite3, json, os, pathlib)

### Must NOT have
- Do NOT store actual audio or .als files
- Do NOT attempt cross-machine template compatibility
- Do NOT auto-delete on name collision
- Do NOT store template data in git (SQLite is user-local)
- Do NOT modify existing server.py tool registrations (add new file + registration only)

## Verification strategy
- Test decision: tests-after
- Evidence: .omo/evidence/task-<N>-sprint-09-project-templates.txt

## Execution strategy

### Parallel execution waves

| Wave | Focus | Todos |
|------|-------|-------|
| 1 | Schema + DB + Engine | 1, 2, 3 |
| 2 | Templates + Tools + Tests | 4, 5, 6, 7 |

### Dependency matrix

| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Template schema + session_templates.py | None | 3, 5 | 2 |
| 2. SQLite storage + session_templates_db.py | None | 5 | 1 |
| 3. 7 built-in templates JSON | 1 | None | 4 |
| 4. MCP tools in server.py | 1, 2 | None | 3 |
| 5. save_session_template tool | 1, 2 | None | 3, 4 |
| 6. load/list/diff/tag tools | 1, 2 | None | 3, 4, 5 |
| 7. tests/test_session_templates.py | 1, 2, 3, 4 | None | 5, 6 |

## Todos

- [ ] 1. Template schema + session_templates.py engine
  What to do / Must NOT do:
  Create `MCP_Server/session_templates.py` with:
  1. `Template` dataclass matching schema from spec: template_name, version, genre, description, bpm, time_signature, tracks, return_tracks, master, routing, scenes
  2. `TrackTemplate` dataclass: name, type (midi/audio), device_chain, patterns, volume, pan, sends
  3. `capture_session(client) -> dict` — reads current session state via existing get_* tools and serializes to template dict format
  4. `apply_template(mcp_server, template: dict) -> str` — creates tracks per template, loads devices, sets properties, creates patterns, configures returns + master + scenes
  5. `diff_templates(template_a: dict, template_b: dict) -> str` — structural diff comparing tracks/devices/routing/scenes, returns added/removed/modified sections
  6. Error handling: per-track errors don't abort entire template (skip failed, continue)
  Must NOT: Store actual audio data. Must use existing MCP tools for apply_template (via send_command).
  Must reference devices by query strings (not FileIds) for portability.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 3, 4, 5, 6, 7
  References:
  - Spec: `.omo/specs/sprint-09-project-templates.md`
  - Existing get_* tools in `MCP_Server/server.py` for capture_session
  - Existing create_* tools in `MCP_Server/server.py` for apply_template
  - Python dataclasses for schema
  Acceptance criteria:
  ```bash
  python -c "
  from MCP_Server.session_templates import diff_templates, capture_session
  tmpl_a = {'tracks': [{'name': 'Kick', 'type': 'midi'}]}
  tmpl_b = {'tracks': [{'name': 'Kick', 'type': 'midi'}, {'name': 'Bass', 'type': 'midi'}]}
  diff = diff_templates(tmpl_a, tmpl_b)
  assert 'added' in diff.lower() or 'Bass' in str(diff), 'diff not found'
  print(f'Template diff OK: {diff}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: diff_templates returns diff with added/removed sections
  - HAPPY: capture_session returns valid template dict with tracks key
  - FAILURE: Empty template raises ValidationError
  Evidence: .omo/evidence/task-1-sprint-09-project-templates.txt
  Commit: Y | feat(templates): add template schema and engine module

- [ ] 2. SQLite storage + session_templates_db.py
  What to do / Must NOT do:
  Create `MCP_Server/session_templates_db.py` with:
  1. `TemplateDB(db_path: str = DEFAULT_PATH)` class
  2. Database at `~/.ableton-mcp-templates.db` (DEFAULT_PATH)
  3. Schema: `templates(name TEXT PK, version TEXT, genre TEXT, description TEXT, template_data TEXT)` + `tags(name TEXT PK)` + `template_tags(template_name TEXT FK, tag_name TEXT FK)`
  4. Methods: `list_templates(genre, tag)`, `get_template(name)`, `save_template(name, template_dict)`, `delete_template(name)`, `tag_template(name, tag)`, `get_tags(name)`, `list_tags()`
  5. Uses sqlite3 (stdlib) — no SQLAlchemy
  6. `get_template` returns dict; `save_template` accepts dict + serializes
  7. Thread-safe via sqlite3 check_same_thread=False + WAL mode
  Must NOT: Store in git. Must NOT add new dependencies.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 4, 5, 6, 7
  References:
  - Python sqlite3 docs: https://docs.python.org/3/library/sqlite3.html
  - Existing similar: `MCP_Server/browser_cache.py` (SQLite pattern)
  - Accept connection from main thread only
  Acceptance criteria:
  ```bash
  python -c "
  from MCP_Server.session_templates_db import TemplateDB
  import tempfile, os
  db = TemplateDB(tempfile.mktemp())
  db.save_template('test', {'tracks': [{'name': 'Test', 'type': 'midi'}]})
  t = db.get_template('test')
  assert t['name'] == 'test'
  assert len(t['template_data']['tracks']) == 1
  db.tag_template('test', 'demo')
  assert 'demo' in db.get_tags('test')
  db.delete_template('test')
  assert db.get_template('test') is None
  os.unlink(db.db_path)
  print('TemplateDB CRUD OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: save → get returns same data
  - HAPPY: tag → get_tags returns tag
  - FAILURE: get_nonexistent returns None
  - FAILURE: delete nonexistent is no-op
  Evidence: .omo/evidence/task-2-sprint-09-project-templates.txt
  Commit: Y | feat(templates): add SQLite template storage

- [ ] 3. 7 built-in template JSON files
  What to do / Must NOT do:
  Create `MCP_Server/knowledge/templates/` with 7 JSON files matching the schema from todo 1:
  1. `4_on_floor.json` — 6 tracks, house, 125 BPM, 4/4
  2. `dub_setup.json` — 5 tracks, dub, 75 BPM, 4/4
  3. `ambient_pad.json` — 4 tracks, ambient, 90 BPM, 4/4
  4. `dj_rig.json` — 3 tracks, DJ, 128 BPM, 4/4
  5. `techno_minimal.json` — 5 tracks, techno, 130 BPM, 4/4
  6. `sound_design.json` — 3 tracks, general, 120 BPM, 4/4
  7. `studio_mastering.json` — 1 track, mastering, auto BPM, 4/4

  Each template must have: template_name, version, genre, description, bpm, time_signature, tracks, scenes
  Each track must have: name, type, device_chain, volume, pan
  Use query strings for device loading (e.g. "query:909 Kick", "query:Deep Sub Bass")

  Must NOT: Include FileIds (use query strings). Must NOT reference non-existent devices.

  Parallelization: Wave 2 | Blocked by: 1 | Blocks: None
  References:
  - Template schema from Todo 1
  - `MCP_Server/knowledge/devices/` for device name references
  - Existing drum pattern names: one_drop, rockers, steppers, house_basic, techno_4x4, dub_techno
  Acceptance criteria:
  ```bash
  python -c "
  import json, os
  tmpl_dir = 'MCP_Server/knowledge/templates'
  files = os.listdir(tmpl_dir)
  assert len([f for f in files if f.endswith('.json')]) >= 7, 'Need 7+ templates'
  for f in sorted(os.listdir(tmpl_dir)):
      if f.endswith('.json'):
          t = json.load(open(os.path.join(tmpl_dir, f)))
          assert 'template_name' in t, f'{f} missing template_name'
          assert 'tracks' in t, f'{f} missing tracks'
          assert 'scenes' in t, f'{f} missing scenes'
          print(f'{f}: {t[\"template_name\"]} ({len(t[\"tracks\"])} tracks, {t[\"bpm\"]} BPM)')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Each template parses as valid JSON with required fields
  - HAPPY: All 7 files present with different genres
  Evidence: .omo/evidence/task-3-sprint-09-project-templates.txt
  Commit: Y | feat(templates): add 7 built-in project templates

- [ ] 4. Register template engine functions + module in server.py
  What to do / Must NOT do:
  Create `MCP_Server/template_tools.py` with `register_template_tools(mcp, get_ableton_connection)` registering 7 tools:
  1. `save_session_template(ctx, name: str, description: str = "")` — captures current session via capture_session(), saves via TemplateDB
  2. `load_session_template(ctx, name: str)` — loads from DB or built-in library, calls apply_template()
  3. `list_session_templates(ctx, genre: str = "", tag: str = "")` — lists all templates filtered by genre/tag
  4. `diff_sessions(ctx, template_a: str, template_b: str)` — loads two templates, computes diff
  5. `tag_session(ctx, tag_name: str)` — captures + saves current session as tagged snapshot
  6. `get_session_tags(ctx)` — lists all tags with timestamps
  7. `load_tagged_session(ctx, tag_name: str)` — loads template by tag name

  Add import + registration in `MCP_Server/server.py` at lines 760-775:
  ```python
  from MCP_Server.template_tools import register_template_tools
  register_template_tools(mcp, get_ableton_connection)
  ```
  Must NOT: Duplicate existing get_* tools. Must NOT modify existing tool registrations.

  Parallelization: Wave 2 | Blocked by: 1, 2 | Blocks: 7
  References:
  - Registration pattern: `MCP_Server/server.py:760-775`
  - Submodule pattern: `MCP_Server/groove_tools.py`
  Acceptance criteria:
  ```bash
  python -c "
  with open('MCP_Server/template_tools.py') as f:
      content = f.read()
  for tool in ['save_session_template', 'load_session_template', 'list_session_templates',
               'diff_sessions', 'tag_session', 'get_session_tags', 'load_tagged_session']:
      assert tool in content, f'{tool} not in template_tools.py'
  assert 'register_template_tools' in open('MCP_Server/server.py').read(), 'registration missing'
  print('All 7 tools + registration OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: All 7 tool functions defined
  - HAPPY: Registration import + call present in server.py
  - FAILURE: Missing tool function detected
  Evidence: .omo/evidence/task-4-sprint-09-project-templates.txt
  Commit: Y | feat(templates): add 7 MCP tools for template management

- [ ] 5. tests/test_session_templates.py
  What to do / Must NOT do:
  Create `tests/test_session_templates.py` with pytest tests:
  1. Template schema validation (required fields, types)
  2. diff_templates detects added/removed/modified tracks
  3. diff_templates detects changed device chain
  4. diff_templates detects scene changes
  5. TemplateDB CRUD (save/get/delete)
  6. TemplateDB tag workflow (tag/get_tags)
  7. 7 built-in templates parse as valid JSON
  8. Template round-trip (json → dict → json → dict)
  9. Error handling: invalid template data
  10. Library template listing (list all 7)

  Use `from MCP_Server.session_templates import diff_templates`
  Use `from MCP_Server.session_templates_db import TemplateDB` with tempfile

  Must NOT: Import server.py (causes sounddevice dep). Must NOT require Ableton Live.

  Parallelization: Wave 2 | Blocked by: 1, 2, 3, 4 | Blocks: None
  Acceptance criteria:
  ```bash
  python -m pytest tests/test_session_templates.py -v 2>&1 | tail -20
  # Expected: 10+ passed, 0 failed
  ```
  QA scenarios: happy + failure
  - HAPPY: All 10 tests pass
  - HAPPY: TemplateDB CRUD round-trip works
  - FAILURE: Invalid template raises validation error
  Evidence: .omo/evidence/task-5-sprint-09-project-templates.txt
  Commit: Y | test(templates): add tests for template engine and storage

## Final verification wave
- [ ] F1. `python -m pytest tests/test_session_templates.py -v 2>&1` all pass
- [ ] F2. `ls MCP_Server/knowledge/templates/*.json | wc -l` = 7
- [ ] F3. `python -c "compile(open('MCP_Server/session_templates.py').read(), 'st', 'exec')"` compiles
- [ ] F4. Scope fidelity: no existing tool modification, no audio storage, no auto-delete

## Commit strategy
- feat(templates): add template schema and engine module
- feat(templates): add SQLite template storage
- feat(templates): add 7 built-in project templates
- feat(templates): add 7 MCP tools for template management
- test(templates): add tests for template engine and storage

## Success criteria
- Template diff detects structural changes between two sessions
- TemplateDB CRUD works with SQLite persistence
- 7 built-in templates load and parse correctly
- All 7 MCP tools registered and return expected results
- 10+ pytest scenarios pass for template engine, storage, built-in templates
