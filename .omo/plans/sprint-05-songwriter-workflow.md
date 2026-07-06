# sprint-05-songwriter-workflow — Work Plan

## TL;DR (For humans)

**What you'll get:** An end-to-end songwriter orchestrator that turns a one-line brief (`"dark techno, 132 BPM, G minor"`) into a complete Ableton session with intro, verse, chorus, bridge, outro, full arrangement automation, scene structure, and genre-appropriate instruments. No more hand-cranking 30+ tools per song. Three new MCP tools: `compose_song_from_brief`, `generate_arrangement`, `generate_automation_build` — plus 10+ song structure templates and genre-appropriate instrument recipes.

**Why this approach:** The existing `@ableton-songwriter` skill is a set of markdown instructions an LLM reads and manually executes. This sprint builds it as real software — a deterministic orchestration engine that calls existing MCP tools in the correct order with proper error handling, progress reporting, and arrangement automation. Templates and recipes are data-driven (JSON + Python dicts), extensible, and version-controlled.

**What it will NOT do:** Generate audio files (MIDI-only composition), master or mix the session, delete existing sessions without creating a backup, hardcode FileIds (they differ per Live version), or replace the existing `@ableton-songwriter` skill (the skill remains for manual guided use).

**Effort:** Medium (1 sprint, ~5 days)
**Risk:** Medium-High — session creation is multi-step and can fail midway (invalid FileId, missing devices); partial sessions must not corrupt state
**Dependencies:** Sprint 04 (composition tools: `generate_chord_progression`, `generate_melody`)

Your next move: Approve this plan, then run `$start-work` to begin execution.

---

> TL;DR (machine): Medium effort, Medium-High risk (multi-step session creation). 7 deliverables across 3 waves. Wave 1: knowledge files + presets module (data layer). Wave 2: core engine + arrangement/automation functions. Wave 3: tool registration + demo + tests.

## Scope

### Must have
- `MCP_Server/knowledge/song_structure.json` — 10+ structure templates (techno_peak, pop_song, ambient_scape, dub_delay, house_anthem, dnb_roller, hiphop_trap, lo-fi_study, cinematic, minimal_deep) with sections, bars per section, energy curves, and track type definitions per spec
- `MCP_Server/knowledge/instrument_recipes.json` — genre-appropriate device chains mapping track types to Live device presets, using existing browser cache FileIds
- `MCP_Server/songwriter_presets.py` — Python module that loads JSON knowledge files and exports `STRUCTURE_TEMPLATES` dict and instrument recipe dicts
- `MCP_Server/songwriter.py` — core orchestration engine with three functions:
  - `compose_song_from_brief(brief: dict) -> str` — full session creation in 11-step flow
  - `generate_arrangement(track_count: int, sections: list) -> str` — scene structure + clip layout
  - `generate_automation_build(track_index, clip_index, bars, parameter_type) -> str` — envelope point generation
- `MCP_Server/server.py` — import + register 3 new MCP tools via `@server.tool` decorators
- `scripts/songwriter_example.py` — end-to-end demo script
- `tests/test_songwriter.py` — integration tests with mocked Live connection

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT generate audio files (MIDI-only composition — audio export impossible via Remote Script API)
- Do NOT attempt to "master" or finalize the session (mixing is the user's job)
- Do NOT delete existing sessions without creating a backup first
- Do NOT hardcode FileIds (they differ per Live version — use browser cache queries)
- Do NOT modify existing @ableton-songwriter skill files
- Do NOT add new pip dependencies
- Do NOT add new Remote Script handlers (reuse existing socket dispatch)
- Do NOT create new TCP/UDP commands (reuse existing `send_command` flow)
- Do NOT modify LSP server configuration

## Verification strategy
> Zero human intervention — all verification is agent-executed.
- Test decision: tests-after + structure validation for each wave
- Evidence: `.omo/evidence/task-<N>-sprint-05-songwriter-workflow.<ext>`
- Key verification: parse JSON templates, import modules, verify function signatures, run mocked integration tests

## Execution strategy

### Parallel execution waves
| Wave | Focus | Todos | Est. days |
|------|-------|-------|-----------|
| 1 | Knowledge data + presets module | 1, 2 | 1 |
| 2 | Core engine (orchestration + arrangement) | 3, 4 | 2 |
| 3 | Tool registration + demo + tests | 5, 6, 7 | 2 |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Song structure JSON | None | 2 | None |
| 2. Presets module + instrument recipes | 1 | 3 | None |
| 3. Core engine: compose_song_from_brief | 2 | 4, 5 | None |
| 4. Arrangement + automation functions | 3 | 5 | None |
| 5. Tool registration in server.py | 3, 4 | 6, 7 | None |
| 6. Demo script | 5 | None | 7 |
| 7. Integration tests | 5 | None | 6 |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Create song structure templates (JSON knowledge files)
  What to do / Must NOT do:
  Create `MCP_Server/knowledge/song_structure.json` with 10+ named structure templates. Each template defines:
  - `sections`: ordered list of section names (intro, verse, chorus, etc.)
  - `bars_per_section`: array matching sections length
  - `energy_curve`: 0.0-1.0 values per section
  - `track_types`: dict with count, patterns, and optional flags per track type

  Required templates (from spec):
  - `techno_peak`: sections=[intro, build_1, drop_1, breakdown, build_2, drop_2, outro], track_types={kick, percussion, bass, pad, fx}
  - `pop_song`: sections=[intro, verse, pre_chorus, chorus, verse, chorus, bridge, chorus_outro], track_types={drums, bass, chords, lead, vocals}
  - `ambient_scape`: sections=[build, evolve, peak, decay, resolve], track_types={pad, texture, bass, fx}
  - `dub_delay`: sections=[intro, verses, chorus, dub, outro], track_types={drums, bass, rhythm_guitar, organ, fx}
  - Plus 6 more: `house_anthem`, `dnb_roller`, `hiphop_trap`, `lo-fi_study`, `cinematic`, `minimal_deep`

  Must NOT: Hardcode FileIds (use query: syntax like `query:909#FileId_...` with placeholder). Must NOT include audio tracks. Must NOT exceed 16 sections per template. Each template must have valid JSON with matching array lengths (sections, bars_per_section, energy_curve).

  Also create `MCP_Server/knowledge/instrument_recipes.json` with genre-appropriate device chain mappings:
  ```json
  {
    "techno_kick": {"device": "Drum Rack", "kit": "query:909#FileId_..."},
    "techno_bass": {"device": "Operator", "preset": "query:Deep Mono"},
    "house_chords": {"device": "Wavetable", "preset": "query:Warm Pad"},
    "ambient_pad": {"device": "Hybrid Reverb", "chain": ["Reverb", "Delay"]},
    "dub_bass": {"device": "Drift", "preset": "query:Deep Sub"}
  }
  ```
  At minimum 15 recipes covering: techno (kick, bass, percussion, pad, fx), house (drums, chords, lead, bass), ambient (pad, texture, bass, fx), dub (drums, bass, organ, fx, rhythm_guitar), hiphop (drums, bass, melody, fx).

  Parallelization: Wave 1 | Blocked by: None | Blocks: Presets module
  References:
  - Spec section 5.1: `knowledge/song_structure.json` with 4 detailed + 6 minimum templates
  - Spec section 5.2: `knowledge/instrument_recipes.json` with genre recipes
  - Energy curves must be 0.0-1.0 floats
  - `bar_per_section` must be integers (multiples of 4 for standard structures)
  - Existing `MCP_Server/knowledge/devices/` for pattern reference
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import json
  with open('MCP_Server/knowledge/song_structure.json') as f:
      templates = json.load(f)
  assert len(templates) >= 10, f'Expected >=10 templates, got {len(templates)}'
  for name, t in templates.items():
      assert len(t['sections']) == len(t['bars_per_section']) == len(t['energy_curve']), \
          f'{name}: sections/bars/energy length mismatch'
      assert all(0.0 <= e <= 1.0 for e in t['energy_curve']), \
          f'{name}: energy_curve out of range'
      assert 'track_types' in t, f'{name}: missing track_types'
  print(f'{len(templates)} structure templates validated')
  "
  python -c "
  import json
  with open('MCP_Server/knowledge/instrument_recipes.json') as f:
      recipes = json.load(f)
  assert len(recipes) >= 15, f'Expected >=15 recipes, got {len(recipes)}'
  for name, r in recipes.items():
      assert 'device' in r, f'{name}: missing device'
  print(f'{len(recipes)} instrument recipes validated')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Load song_structure.json, all 10+ templates parse, array lengths match in all templates
  - HAPPY: Load instrument_recipes.json, all 15+ recipes have `device` key
  - FAILURE: Template with mismatched section/bars/energy lengths → caught by validation
  - FAILURE: Recipe with missing `device` key → caught by validation
  Evidence: `.omo/evidence/task-1-sprint-05-songwriter-workflow.txt`
  Commit: Y | feat(knowledge): add song structure templates and instrument recipes for songwriter

- [ ] 2. Create presets module (songwriter_presets.py)
  What to do / Must NOT do:
  Create `MCP_Server/songwriter_presets.py` that:
  1. Loads `knowledge/song_structure.json` at import time into `STRUCTURE_TEMPLATES` dict
  2. Loads `knowledge/instrument_recipes.json` at import time into `INSTRUMENT_RECIPES` dict
  3. Exports both dicts at module level
  4. Provides helper function `get_template_names() -> list[str]`
  5. Provides `resolve_recipe(track_type: str, genre: str) -> dict` that matches track type + genre to best recipe
  6. Provides `get_section_count(template_name: str) -> int`
  7. Provides `get_total_bars(template_name: str) -> int` (sum of bars_per_section)

  Resolve path to JSON files using `os.path.dirname(__file__)` (relative to `MCP_Server/`), not hardcoded paths.
  Must fail gracefully: if JSON files are missing or malformed, log error and raise ImportError with helpful message.
  Must NOT: Load JSON files on every function call (load once at module init).
  Must NOT: Depend on any external libraries (stdlib only: json, os, pathlib).

  Parallelization: Wave 1 | Blocked by: Todo 1 | Blocks: Core engine
  References:
  - Knowledge directory: `MCP_Server/knowledge/`
  - JSON load pattern: `MCP_Server/knowledge/__init__.py` for reference
  - `os.path.dirname(__file__)` for relative path resolution
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.songwriter_presets import STRUCTURE_TEMPLATES, INSTRUMENT_RECIPES, get_template_names, resolve_recipe, get_total_bars
  assert 'techno_peak' in STRUCTURE_TEMPLATES, 'techno_peak template missing'
  assert 'pop_song' in STRUCTURE_TEMPLATES, 'pop_song template missing'
  assert len(STRUCTURE_TEMPLATES) >= 10, f'Expected >=10 templates, got {len(STRUCTURE_TEMPLATES)}'
  assert len(INSTRUMENT_RECIPES) >= 15, f'Expected >=15 recipes, got {len(INSTRUMENT_RECIPES)}'
  names = get_template_names()
  assert len(names) >= 10, f'get_template_names returned {len(names)}'
  recipe = resolve_recipe('kick', 'techno')
  assert recipe is not None, 'resolve_recipe returned None for techno kick'
  bars = get_total_bars('techno_peak')
  expected = sum(STRUCTURE_TEMPLATES['techno_peak']['bars_per_section'])
  assert bars == expected, f'get_total_bars: {bars} != {expected}'
  print('songwriter_presets.py OK: templates, recipes, helpers all working')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Import presets, STRUCTURE_TEMPLATES has 10+ entries, INSTRUMENT_RECIPES has 15+ entries
  - HAPPY: resolve_recipe("kick", "techno") returns a dict with device key
  - HAPPY: get_total_bars("pop_song") returns summed bars
  - FAILURE: Import presets when JSON files are deleted → ImportError with helpful message
  - FAILURE: resolve_recipe("theremin", "techno") returns None (no match) instead of crashing
  Evidence: `.omo/evidence/task-2-sprint-05-songwriter-workflow.txt`
  Commit: Y | feat(presets): add songwriter_presets module for structure templates and instrument recipes

- [ ] 3. Implement compose_song_from_brief core orchestration engine
  What to do / Must NOT do:
  Create `MCP_Server/songwriter.py` with `compose_song_from_brief(brief: dict, get_ableton_connection) -> str` that:

  1. Accepts brief dict with: genre, bpm, key, scale, structure (name or custom dict), complexity (0.0-1.0), mood, track_count
  2. Validates brief fields (genre in known list, bpm 20-999, key in [A-G][#b]? minor/major, complexity 0-1)
  3. Loads template from STRUCTURE_TEMPLATES using genre/structure keys
  4. Calls existing MCP tools via `get_ableton_connection().send_command("...")` in this order:
     - `delete_all_tracks` — clean slate
     - `create_midi_track` x N tracks (from template track_types total count)
     - `set_track_name(i, name)` — name from template
     - `load_instrument_or_effect(i, "query:...")` — resolve from INSTRUMENT_RECIPES
     - `set_tempo(brief.bpm)`
     - `create_drum_pattern(track, 0, pattern_name)` — on drum/percussion tracks
     - `generate_chord_progression(key, scale, complexity)` — on chord tracks
     - `generate_melody(key, scale, bars=8, complexity)` — on lead/melody tracks
     - Creates scene structure per template sections
     - Sets clip follow actions for auto-progression
  5. Wraps each step in try/except — if one step fails, logs and continues (partial session)
  6. Returns JSON summary string: {tracks, sections, estimated_duration_minutes, status}

  The function also accepts `get_ableton_connection` parameter to send commands to the Ableton bridge.
  When running standalone (demo script mode) without Live, gracefully mock the tool calls and return a plan summary.

  Must NOT: Create audio tracks (MIDI-only). Must NOT hardcode FileIds (use query: syntax). Must NOT block on a single failed step. Must NOT call delete_all_tracks without validation. Must NOT exceed 64 tracks.

  Each successful step should log a progress message via print/logging.

  Parallelization: Wave 2 | Blocked by: Todo 2 (presets) | Blocks: Arrangement/automation, Tool registration
  References:
  - Spec section 5.3: orchestration flow (11 steps)
  - Spec section 5.4: compose_song_from_brief tool signature
  - Existing tool calls pattern: `MCP_Server/server.py:send_command` (line 183)
  - `create_drum_pattern`: `MCP_Server/advanced_tools.py`
  - `generate_chord_progression`, `generate_melody`: from Sprint 04 (composition tools)
  - `create_midi_track`: `MCP_Server/server.py`
  - `load_instrument_or_effect`: `MCP_Server/server.py`
  - `set_tempo`: `MCP_Server/server.py`
  - `set_track_name`: `MCP_Server/server.py`
  - `delete_all_tracks`: `MCP_Server/server.py`
  - AGENTS.md session setup workflow for ordering
  - AGENTS.md drum pattern variants (one_drop, rockers, steppers, etc.)
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import ast
  with open('MCP_Server/songwriter.py') as f:
      tree = ast.parse(f.read())
  funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
  assert 'compose_song_from_brief' in funcs, 'compose_song_from_brief not found'
  assert any('delete_all_tracks' in open('MCP_Server/songwriter.py').read()), 'must reference delete_all_tracks'
  assert any('create_midi_track' in open('MCP_Server/songwriter.py').read()), 'must reference create_midi_track'
  assert any('set_tempo' in open('MCP_Server/songwriter.py').read()), 'must reference set_tempo'
  print('compose_song_from_brief structure OK')
  "
  python -c "
  # Test standalone mode (no Live)
  from MCP_Server.songwriter import compose_song_from_brief
  result = compose_song_from_brief({
      'genre': 'techno', 'bpm': 130, 'key': 'D', 'scale': 'minor',
      'structure': 'techno_peak', 'complexity': 0.6, 'mood': 'dark', 'track_count': 8
  }, get_ableton_connection=None)
  assert isinstance(result, str), f'Expected str, got {type(result)}'
  import json
  data = json.loads(result)
  assert 'tracks' in data, 'Missing tracks in result'
  assert 'sections' in data, 'Missing sections in result'
  assert 'status' in data, 'Missing status in result'
  print(f'compose_song_from_brief standalone mode: {data[\"status\"]}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: compose_song_from_brief(techno brief) → returns valid JSON with tracks, sections, estimated_duration
  - HAPPY: compose_song_from_brief(pop brief with custom structure) → uses custom structure instead of named template
  - HAPPY: Standalone mode (no Live) → returns plan summary instead of crashing
  - FAILURE: Invalid BPM "abc" → validation error with clear message
  - FAILURE: Unknown genre "bluegrass" → falls back to pop_song template with warning
  - FAILURE: Track step 3 fails (load_instrument) → continues with remaining steps, reports partial status
  Evidence: `.omo/evidence/task-3-sprint-05-songwriter-workflow.txt`
  Commit: Y | feat(songwriter): add compose_song_from_brief core orchestration engine

- [ ] 4. Implement generate_arrangement and generate_automation_build
  What to do / Must NOT do:
  Add two functions to `MCP_Server/songwriter.py`:

  **`generate_arrangement(track_count: int, sections: list, get_ableton_connection) -> str`:**
  1. Lays out scenes in order per sections list
  2. For each section:
     - Names scene (e.g., "Intro", "Verse 1", "Chorus 1")
     - Duplicates clips per section (if clip exists)
     - Sets scene color based on section type: green=verse, blue=chorus, orange=bridge, gray=intro/outro, yellow=build
     - Configures follow actions for auto-progression:
       - intro → verse (play next)
       - verse → chorus (play next)
       - chorus → verse or bridge (play next)
       - bridge → chorus (play next)
       - outro → stop
  3. Returns JSON: {scenes, scene_count, total_bars, estimated_duration_minutes, follow_action_chain}

  **`generate_automation_build(track_index: int, clip_index: int, bars: int = 8, parameter_type: str = "filter_sweep", get_ableton_connection) -> str`:**
  1. Generates automation envelope points for the specified parameter type:
     - `filter_sweep`: 16 points rising from 0.0 to 1.0 over `bars`
     - `volume_fade`: 8 points from 0.0→1.0 (fade in) or 1.0→0.0 (fade out)
     - `reverb_send`: 8 points from 0.0→0.7 (build reverb) or 0.7→0.0 (clear reverb)
     - `drive`: 8 points from 0.0→0.8 (increase distortion)
  2. Each point: {time (in beats), value (normalized 0.0-1.0), interpolation: "linear"}
  3. Returns JSON: {parameter_type, point_count, bars, envelope_points, targeted_parameter_name}

  Both functions must accept `get_ableton_connection` for Live mode and work in standalone (mocked) mode.
  Must NOT: Create clips (assumes clips already exist). Must NOT modify existing automation on non-targeted parameters. Must NOT hardcode parameter indices.

  Parallelization: Wave 2 | Blocked by: Todo 3 (core engine) | Blocks: Tool registration
  References:
  - Spec section 5.3: generate_arrangement flow (clip dup, scene naming, follow actions, automation)
  - Spec section 5.4: generate_arrangement and generate_automation_build signatures
  - Scene naming: existing `create_scene` or `set_scene_name` in `MCP_Server/server.py`
  - Follow actions: `set_clip_follow_action` or existing clip property tools
  - Automation: control surface `send_command("set_device_parameter", ...)` pattern
  - Section color mapping: Live scene color index values (0=no color, 1-7=section types)
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import ast
  with open('MCP_Server/songwriter.py') as f:
      tree = ast.parse(f.read())
  funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
  assert 'generate_arrangement' in funcs, 'generate_arrangement not found'
  assert 'generate_automation_build' in funcs, 'generate_automation_build not found'
  print('generate_arrangement and generate_automation_build defined')
  "
  python -c "
  from MCP_Server.songwriter_presets import STRUCTURE_TEMPLATES
  from MCP_Server.songwriter import generate_arrangement, generate_automation_build
  sections = STRUCTURE_TEMPLATES['techno_peak']['sections']
  result = generate_arrangement(track_count=8, sections=sections, get_ableton_connection=None)
  assert isinstance(result, str)
  import json
  data = json.loads(result)
  assert 'scenes' in data
  assert data['scene_count'] == len(sections)
  print(f'generate_arrangement: {data[\"scene_count\"]} scenes, {data[\"total_bars\"]} bars')
  result2 = generate_automation_build(track_index=0, clip_index=0, bars=8, parameter_type='filter_sweep', get_ableton_connection=None)
  data2 = json.loads(result2)
  assert data2['parameter_type'] == 'filter_sweep'
  assert len(data2['envelope_points']) >= 8
  print(f'generate_automation_build: {len(data2[\"envelope_points\"])} points for {data2[\"parameter_type\"]}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: generate_arrangement(8, pop_song sections) → 8 scenes with correct names, colors, follow action chain
  - HAPPY: generate_automation_build(0, 0, 16, "filter_sweep") → 16 rising envelope points
  - HAPPY: generate_automation_build(1, 2, 4, "volume_fade") → 8 fade-in points
  - HAPPY: Standalone mode for both → returns JSON with expected structure
  - FAILURE: generate_arrangement(0, []) → returns empty arrangement with scene_count=0
  - FAILURE: generate_automation_build with unknown parameter_type → returns error with valid types listed
  Evidence: `.omo/evidence/task-4-sprint-05-songwriter-workflow.txt`
  Commit: Y | feat(songwriter): add generate_arrangement and generate_automation_build functions

- [ ] 5. Register songwriter tools in server.py
  What to do / Must NOT do:
  Modify `MCP_Server/server.py` to register 3 new MCP tools:

  1. Add `from MCP_Server.songwriter import compose_song_from_brief, generate_arrangement, generate_automation_build` import

  2. Register `compose_song_from_brief` as `@server.tool`:
     ```python
     @server.tool(description="Compose a complete song from a high-level brief. Creates tracks, loads instruments, sets tempo, generates patterns and melodies, and arranges scenes.")
     async def compose_song_from_brief_tool(
         ctx,
         genre: str = "techno",
         bpm: int = 130,
         key: str = "C",
         scale: str = "minor",
         structure: str = "techno_peak",
         complexity: float = 0.5,
         mood: str = "neutral",
         track_count: int = 8
     ) -> str:
         brief = {"genre": genre, "bpm": bpm, "key": key, ...}
         return compose_song_from_brief(brief, get_ableton_connection)
     ```

  3. Register `generate_arrangement` as `@server.tool`:
     ```python
     @server.tool(description="Generate song arrangement from a structure template. Creates scenes, names them, sets follow actions for auto-progression.")
     async def generate_arrangement_tool(
         ctx,
         structure_template: str = "techno_peak",
         section_overrides: str = ""
     ) -> str:
         ...
     ```

  4. Register `generate_automation_build` as `@server.tool`:
     ```python
     @server.tool(description="Generate automation envelope points for builds, fades, and effects sweeps.")
     async def generate_automation_build_tool(
         ctx,
         track_index: int = 0,
         clip_index: int = 0,
         bars: int = 8,
         parameter_type: str = "filter_sweep"
     ) -> str:
         ...
     ```

  Place the new tools after the existing tool section (around line 2700+ in server.py, before `get_browser_items_at_path`).
  Follow the existing tool decorator pattern and import style.

  Must NOT: Modify existing tool bodies. Must NOT add new socket/transport handlers. Must NOT add new UDP commands.

  Parallelization: Wave 3 | Blocked by: Todos 3, 4 (core engine) | Blocks: Demo, Tests
  References:
  - Tool registration pattern: `MCP_Server/server.py:752-765` (@server.tool decorators)
  - Import pattern: `MCP_Server/server.py` top-level imports
  - Existing tool signature style: look at nearby `@server.tool` definitions
  - `get_ableton_connection` usage pattern from other tools
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import re
  with open('MCP_Server/server.py') as f:
      content = f.read()
  # Check imports
  assert 'from MCP_Server.songwriter import' in content, 'songwriter import not found'
  assert 'compose_song_from_brief' in content, 'compose_song_from_brief ref not found'
  assert 'generate_arrangement' in content, 'generate_arrangement ref not found'
  assert 'generate_automation_build' in content, 'generate_automation_build ref not found'
  # Check @server.tool decorators
  tools = re.findall(r'@server\.tool.*?\\n(?:async )?def (\\w+)', content, re.DOTALL)
  songwriter_tools = [t for t in tools if 'song' in t or 'arrangement' in t or 'automation' in t]
  assert len(songwriter_tools) >= 3, f'Found {len(songwriter_tools)} songwriter tools'
  print(f'Songwriter tools registered: {songwriter_tools[:3]}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Import server.py, all 3 tools registered with correct signatures
  - HAPPY: compose_song_from_brief_tool has all 8 params with defaults matching spec
  - HAPPY: generate_arrangement_tool accepts structure_template + section_overrides
  - FAILURE: Import server.py with missing songwriter module → ImportError caught by convenience import guard
  Evidence: `.omo/evidence/task-5-sprint-05-songwriter-workflow.txt`
  Commit: Y | feat(server): register compose_song_from_brief, generate_arrangement, generate_automation_build tools

- [ ] 6. Create songwriter demo script
  What to do / Must NOT do:
  Create `scripts/songwriter_example.py` that demonstrates the full songwriter workflow:

  ```python
  #!/usr/bin/env python3
  """End-to-end demo: compose a song from a brief using the songwriter engine."""
  import json
  import sys
  import os

  # Add parent dir to path for standalone running
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

  from MCP_Server.songwriter import compose_song_from_brief, generate_arrangement, generate_automation_build
  from MCP_Server.songwriter_presets import STRUCTURE_TEMPLATES, get_template_names

  DEMOS = [
      {
          "name": "Dark Techno",
          "brief": {
              "genre": "techno", "bpm": 132, "key": "G", "scale": "minor",
              "structure": "techno_peak", "complexity": 0.7, "mood": "dark", "track_count": 8
          }
      },
      {
          "name": "Uplifting House",
          "brief": {
              "genre": "house", "bpm": 126, "key": "C", "scale": "major",
              "structure": "pop_song", "complexity": 0.5, "mood": "uplifting", "track_count": 7
          }
      },
      {
          "name": "Ambient Padscape",
          "brief": {
              "genre": "ambient", "bpm": 80, "key": "D", "scale": "minor",
              "structure": "ambient_scape", "complexity": 0.3, "mood": "calm", "track_count": 6
          }
      }
  ]

  def main():
      print(f"Ableton MCP Songwriter Demo")
      print(f"{'='*50}")
      print(f"Available templates: {', '.join(get_template_names())}")
      print()

      for demo in DEMOS:
          print(f"{'─'*50}")
          print(f"Demo: {demo['name']}")
          print(f"{'─'*50}")
          brief = demo['brief']
          print(f"Brief: {json.dumps(brief, indent=2)}")
          print()

          # Run in standalone mode (no Live required)
          result = compose_song_from_brief(brief, get_ableton_connection=None)
          data = json.loads(result)
          print(f"Result: {json.dumps(data, indent=2)}")
          print()

          sections = STRUCTURE_TEMPLATES[brief['structure']]['sections']
          arrangement = generate_arrangement(data.get('track_count', brief['track_count']), sections, get_ableton_connection=None)
          print(f"Arrangement: {json.dumps(json.loads(arrangement), indent=2)}")
          print()

      print(f"{'='*50}")
      print(f"To use with Live: run this script with --live flag")
      print(f"Example: python scripts/songwriter_example.py --live")
      print(f"{'='*50}")

  if __name__ == '__main__':
      main()
  ```

  The script must run standalone (no Ableton Live) and demonstrate all 3 functions with sample briefs.
  Include a `--live` flag that attempts connection and executes against a running Live instance.

  Must NOT: Require Ableton Live to run (standalone-first design). Must NOT: Hardcode FileIds.
  Must output: clear progress messages, JSON results, and error handling with graceful fallback.

  Parallelization: Wave 3 | Blocked by: Todo 5 (tool registration) | Blocks: None
  References:
  - Existing demo scripts: `scripts/live_dj_performance.py` for style reference
  - Spec section 5.5: demo script example
  - `sys.path.insert(0, ...)` pattern for standalone running
  Acceptance criteria (agent-executable):
  ```bash
  python scripts/songwriter_example.py 2>&1 | head -20
  # Should output demo header and start showing template info without crashing
  ```
  ```bash
  python -c "
  # Verify standalone run produces expected output
  import subprocess, json
  result = subprocess.run(['python', 'scripts/songwriter_example.py'], capture_output=True, text=True)
  assert result.returncode == 0, f'Script failed: {result.stderr}'
  assert 'Songwriter Demo' in result.stdout
  assert 'Dark Techno' in result.stdout
  assert 'Uplifting House' in result.stdout
  print('Demo script runs standalone successfully')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Run `python scripts/songwriter_example.py` → outputs 3 demo briefs with JSON results
  - HAPPY: Run with `--live` flag → attempts Live connection and shows connection status
  - FAILURE: Script imports fail gracefully with ImportError message
  Evidence: `.omo/evidence/task-6-sprint-05-songwriter-workflow.txt`
  Commit: Y | feat(scripts): add songwriter_example.py end-to-end demo script

- [ ] 7. Create songwriter integration tests
  What to do / Must NOT do:
  Create `tests/test_songwriter.py` with mocked Live connection tests:

  1. Test structure template loading:
     - All 10+ templates load correctly
     - Each template validates section/bars/energy consistency
     - Edge cases: template with min sections (2), max sections (16)

  2. Test instrument recipes:
     - All 15+ recipes have valid device keys
     - resolve_recipe returns correct match for known genre+type
     - resolve_recipe returns None for unknown combos

  3. Test compose_song_from_brief standalone mode:
     - Returns valid JSON with tracks, sections, status
     - Different genres produce different track configurations
     - Validation rejects invalid brief fields
     - Partial failure continues and reports partial status

  4. Test generate_arrangement standalone mode:
     - Creates correct number of scenes
     - Scene names match section names
     - Follow actions configured correctly
     - Empty sections returns empty arrangement

  5. Test generate_automation_build standalone mode:
     - filter_sweep produces rising envelope
     - volume_fade produces correct interpolation
     - reverb_send produces correct range
     - Unknown parameter type returns error

  6. Test knowledge file loading via presets module:
     - Load from JSON works
     - Missing file raises ImportError

  Must NOT: Require Ableton Live (all tests run standalone). Must NOT: Use pytest fixtures (standalone scripts per project convention).
  Must use `unittest.TestCase` or simple assert-based test functions.

  Parallelization: Wave 3 | Blocked by: Todo 5 (tool registration) | Blocks: None
  References:
  - Existing test scripts: `scripts/test/test_connection.py` for style reference
  - Test convention: standalone assert-based scripts, no pytest discovery
  - `from MCP_Server.songwriter import ...` for all function imports
  - `from MCP_Server.songwriter_presets import ...` for template imports
  Acceptance criteria (agent-executable):
  ```bash
  python tests/test_songwriter.py
  # All tests pass, output shows OK for each test group
  ```
  ```bash
  python -c "
  import subprocess
  result = subprocess.run(['python', 'tests/test_songwriter.py'], capture_output=True, text=True)
  assert result.returncode == 0, f'Tests failed: {result.stderr[-500:]}'
  lines = [l for l in result.stdout.split('\\n') if 'FAIL' in l or 'ERROR' in l or 'OK' in l or 'PASS' in l]
  assert any('OK' in l for l in lines) or any('PASS' in l for l in lines), 'No passing tests detected'
  print(f'Tests passed: {len(lines)} result lines')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: All 6 test groups pass, template validation checks pass
  - HAPPY: compose_song_from_brief standalone returns correct JSON structure
  - HAPPY: generate_arrangement with pop_song produces 8 scenes with correct naming
  - FAILURE: Test deliberately loads malformed JSON → clean error, not crash
  - FAILURE: Test calls compose_song_from_brief with invalid bpm=0 → validation caught
  Evidence: `.omo/evidence/task-7-sprint-05-songwriter-workflow.txt`
  Commit: Y | test(songwriter): add integration tests for all songwriter components

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: Verify all 7 deliverables exist, all scope boundaries respected, all Must NOT rules followed
- [ ] F2. Code quality: All .py files pass `python -c "compile(open(f).read(), f, 'exec')"` — no syntax errors
- [ ] F3. Knowledge integrity: All 10+ templates validated, all 15+ recipes validated, array lengths consistent
- [ ] F4. Standalone execution: `python scripts/songwriter_example.py` runs without errors
- [ ] F5. Unit tests: `python tests/test_songwriter.py` passes all test groups
- [ ] F6. Scope fidelity: grep for Must NOT have violations (no audio export, no new deps, no new UDP, no LSP mods, no FileId hardcodes)

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(knowledge): add song structure templates and instrument recipes for songwriter
- feat(presets): add songwriter_presets module for structure templates and instrument recipes
- feat(songwriter): add compose_song_from_brief core orchestration engine
- feat(songwriter): add generate_arrangement and generate_automation_build functions
- feat(server): register compose_song_from_brief, generate_arrangement, generate_automation_build tools
- feat(scripts): add songwriter_example.py end-to-end demo script
- test(songwriter): add integration tests for all songwriter components

No squashing — each commit is independently testable. Tags: none.

## Success criteria
- All 10+ structure templates load with valid JSON and consistent array lengths
- All 15+ instrument recipes load with required fields
- `compose_song_from_brief` returns valid session summary JSON for all supported genres
- `generate_arrangement` produces correct scene structure with follow action chains
- `generate_automation_build` generates valid envelope points for all 4 parameter types
- Demo script runs standalone without Ableton Live
- Integration tests pass with 100% test groups passing
- All 3 MCP tools registered and importable via server.py
- Zero new pip dependencies added
- Zero new Remote Script handlers added
- Zero hardcoded FileIds in knowledge files
