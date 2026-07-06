# Sprint 08: MCP Resources V2 + Knowledge Base V2 - Work Plan

## TL;DR (For humans)

**What you'll get:** 4 new URI-addressable MCP resources (`live://track/{ti}/clip/{ci}/notes`, `live://track/{ti}/device/{di}/parameters`, `live://scene/{si}/clip/{ci}`, `live://session/projects`), a polling-based resource subscription system so the AI gets Live-updating state, 20+ third-party plugin schemas (Serum, Massive, Kontakt, FabFilter, etc.) expanding the knowledge base from 36 to 55+ devices, 5+ production recipes for common workflows (minimal techno, ambient pad, drum mix), and a `get_resource_preview` tool for discovering what resources return — all while reducing server.py bloat by extracting resources into a dedicated module.

**Why this approach:** Resources are our strongest differentiator — making session state URI-addressable lets MCP clients treat Live like a filesystem rather than calling tools one-by-one. Subscriptions make state reactive. Third-party device knowledge fills the biggest gap: the AI currently has no idea what parameters Serum or FabFilter Pro-Q 3 expose, so it fumbles parameter indices. Recipes give the agent prescriptive, multi-track, multi-device blueprints for common production tasks.

**What it will NOT do:** Poll more than 5 subscriptions simultaneously (rate limit). Add external plugin detection (schemas are manual best-effort). Modify or delete existing resource URIs. Attempt real-time audio resource streaming (Live API doesn't support it). Add new pip dependencies beyond stdlib. Create new TCP/UDP commands or modify the socket protocol.

**Effort:** Medium (1 sprint, ~5 days)
**Risk:** Low — no new Remote Script handlers, no socket protocol changes, no tool body rewrites. Subscriptions poll safely. Third-party schemas are static JSON (no API calls).
**Decisions to sanity-check:** Polling interval minimum (500ms vs 1000ms), resource URI naming consistency with existing scheme, subscription timeout behavior.

---

> TL;DR (machine): Medium effort, Low risk. 8 deliverables across 4 waves. Wave 1: resources.py module + 4 new URIs + third-party devices + recipes (all parallel). Wave 2: subscription system + get_resource_preview tool (blocked by Wave 1). Wave 3: subscribe/unsubscribe tools + wire registrations. Wave 4: tests.

## Scope

### Must have
- `MCP_Server/resources.py` — extracted resource definitions from server.py, plus 4 new resource URIs:
  - `live://track/{ti}/clip/{ci}/notes` — MIDI note data (pitch, time, duration, velocity)
  - `live://track/{ti}/device/{di}/parameters` — full parameter details with current values
  - `live://scene/{si}/clip/{ci}` — clip data filtered to scene
  - `live://session/projects` — recent project list from Live Projects folder
- `MCP_Server/resources_sub.py` — polling-based subscription handler (`subscribe_resource`, `unsubscribe_resource`)
  - Change-detection via last-seen hash per URI
  - Configurable polling interval (min 500ms)
  - Max 5 concurrent subscriptions
  - Auto-unsubscribe on server stop or resource error
- `MCP_Server/knowledge/devices/third_party.json` — 20+ third-party plugin schemas (essential params, not all 500+)
  - Synths: Serum, Massive, Sylenth1, Spire, Diva, Hive, Pigments, Vital
  - Samplers: Kontakt, Battery
  - Effects: Valhalla Room, Valhalla Shimmer, FabFilter Pro-Q 3, Pro-C 2, Pro-L 2, EchoBoy, Decapitator, Little AlterBoy, iZotope Ozone 11, iZotope Neutron 5
- `MCP_Server/knowledge/recipes/` — 5+ production recipe JSON files:
  - `minimal_techno.json` — full session blueprint (tracks, instruments, patterns, mix levels)
  - `ambient_pad.json` — ambient pad sound design recipe
  - `drum_mix.json` — drum processing chain on return/group track
  - `minimal_techno.json` — minimal techno setup (per spec)
  - Additional 2+ recipes as time permits
- Tool `get_resource_preview(ctx, uri_pattern: str) -> str` — shows sample output for a resource URI
- Tool `subscribe_resource(ctx, uri: str, interval_ms: int = 1000) -> str` — subscribe to live updates
- Tool `unsubscribe_resource(ctx, uri: str) -> str` — cancel a subscription
- Knowledge base `__init__.py` updated to load third-party schemas and recipes

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT poll more than 5 subscriptions simultaneously (hard rate limit in registry)
- Do NOT add external plugin detection (third-party schemas are manual best-effort)
- Do NOT modify or delete existing resource URIs
- Do NOT attempt real-time audio resource streaming (Live API doesn't support it)
- Do NOT add new TCP/UDP commands or modify the socket protocol
- Do NOT add new pip dependencies (stdlib only — time, threading, hashlib, json)
- Do NOT modify existing tool bodies or Remote Script code
- Do NOT modify LSP server configuration
- Do NOT create new Remote Script handlers (all data comes from existing get_* commands)

## Verification strategy
> Zero human intervention — all verification is agent-executed.
- Test decision: tests-after + static validation for each todo
- Evidence: `.omo/evidence/task-<N>-sprint-08-resources-knowledge-v2.txt`

## Execution strategy

### Parallel execution waves
| Wave | Focus | Todos | Est. days |
|------|-------|-------|-----------|
| 1 | Resources module + third-party data + recipes | 1, 3, 4 | 2 |
| 2 | Subscription system + resource preview tool | 2, 5 | 1 |
| 3 | Subscribe/unsubscribe tools + wire registrations | 6, 7 | 1 |
| 4 | Tests | 8 | 1 |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Resources module + 4 new URIs | None | 2, 5, 7 | 3, 4 |
| 2. Subscription system | 1 | 6, 7 | 5 |
| 3. Third-party device knowledge | None | 7 | 1, 4 |
| 4. Production recipes | None | 7 | 1, 3 |
| 5. get_resource_preview tool | 1 | 7 | 2 |
| 6. subscribe/unsubscribe tools | 2 | 7 | None |
| 7. Wire all registrations in server.py | 1, 2, 3, 4, 5, 6 | 8 | None |
| 8. Tests | 1, 2, 7 | None | None |

## Todos

> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Create `resources.py` with extracted + 4 new resource URIs
  What to do / Must NOT do:
  Create `MCP_Server/resources.py` that:
  1. Extracts any existing `@mcp.resource()` decorators from `MCP_Server/server.py` into this module (search for existing resource registrations — likely few/none currently)
  2. Exports `register_resources(mcp)` function that registers all resource URIs on the FastMCP instance
  3. Adds 4 new resource URIs using `@mcp.resource()`:

     `live://track/{track_index}/clip/{clip_index}/notes`:
     - Calls `send_command("add_notes_to_clip", track_index, clip_index, ...)` in reverse — uses existing get_clip_data mechanism
     - Returns MIDI note data: pitch, time, duration, velocity as JSON array
     - Falls back gracefully if clip has no notes: returns empty `[]`

     `live://track/{track_index}/device/{device_index}/parameters`:
     - Calls `send_command("get_device_parameters", track_index, device_index)`
     - Returns full parameter details with current values
     - Returns error state if device_index is out of range

     `live://scene/{scene_index}/clip/{clip_index}`:
     - Calls `send_command("get_all_clips_in_track", clip_index)` per-track, filtered to scene
     - Returns clip data (name, color, length, is_playing) for that specific scene/clip combination
     - Returns empty if scene/clip doesn't exist

     `live://session/projects`:
     - Scans the Live Projects folder (configurable path, default `~/Music/Ableton/Projects`)
     - Returns recent project list (name, path, last_modified, file_size)
     - Caches result for 60s (frequent calls shouldn't hit disk)
     - Falls back to empty list if folder doesn't exist

  4. Registers all resources at module import via `register_resources(mcp)` called from server.py

  Resource decorator pattern:
  ```python
  @mcp.resource("live://track/{track_index}/device/{device_index}/parameters")
  def get_device_parameters_resource(track_index: int, device_index: int) -> str:
      """Get all parameters with current values for a device."""
      ...
  ```

  Must NOT: Create new TCP commands (reuse existing send_command). Must NOT modify existing resource URIs. Must NOT add pip dependencies. Must NOT use absolute file paths for projects folder (use ~ expansion).

  Parallelization: Wave 1 | Blocked by: None | Blocks: 2, 5, 7 | Can parallelize with: 3, 4
  References:
  - FastMCP resource registration pattern: `MCP_Server/server.py:747` mcp = FastMCP(...)
  - send_command: `MCP_Server/server.py:183` (TCP command dispatch)
  - get_device_parameters: used in server.py via send_command
  - add_notes_to_clip: `MCP_Server/advanced_tools.py` (reverse for reading notes)
  - get_all_clips_in_track: `MCP_Server/advanced_tools.py:171`
  - get_all_scenes: `MCP_Server/advanced_tools.py:160`
  - New file: `MCP_Server/resources.py`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import re
  # Verify resources.py exists and has register_resources
  with open('MCP_Server/resources.py') as f:
      content = f.read()
  assert 'def register_resources' in content, 'register_resources not found in resources.py'
  # Count resource decorators
  resources = re.findall(r'@mcp\\.resource\\([\"\\'](.+?)[\"\\']\\)', content)
  assert len(resources) >= 4, f'Expected >=4 resource URIs, got {len(resources)}'
  # Verify specific URI patterns
  uris = ' '.join(resources)
  assert 'notes' in uris or 'clip' in uris, 'clip notes URI missing'
  assert 'device' in uris and 'parameters' in uris, 'device parameters URI missing'
  assert 'scene' in uris or 'projects' in uris, 'scene or projects URI missing'
  print(f'{len(resources)} resource URIs registered: {resources}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Access `live://track/0/device/0/parameters` → returns valid JSON with parameter names, values, ranges
  - HAPPY: Access `live://session/projects` → returns list of recent projects with metadata
  - HAPPY: Access `live://track/0/clip/0/notes` on a MIDI clip with notes → returns [{pitch, time, duration, velocity}, ...]
  - FAILURE: Access `live://track/9999/device/0/parameters` → returns error for out-of-range track index
  - FAILURE: Access `live://session/projects` without Ableton Projects folder → returns empty list
  - FAILURE: `register_resources` called without mcp instance → raises clear TypeError
  Evidence: .omo/evidence/task-1-sprint-08-resources-knowledge-v2.txt
  Commit: Y | feat(resources): add resources.py module with 4 new resource URIs

- [ ] 2. Create `resources_sub.py` subscription system
  What to do / Must NOT do:
  Create `MCP_Server/resources_sub.py` with a polling-based subscription system:

  ```python
  _subscription_registry: dict[str, dict] = {}
  # { uri: {"interval": int, "last_hash": str, "timer": TimerThread, "ctx": Context, "active": bool} }
  ```

  Implement:
  - `subscribe_resource(ctx, uri: str, interval_ms: int = 1000) -> str`:
    1. Validates URI is a registered resource (check against `resources.py` registry)
    2. Validates interval >= 500ms (hard minimum)
    3. Enforces max 5 concurrent subscriptions
    4. Stores initial state hash via `_compute_hash(resource_data)`
    5. Starts a daemon `TimerThread` that:
       - Calls `_get_resource_data(uri)` to fetch current state
       - Computes `_compute_hash(response)` 
       - If hash differs from `last_hash`, sends `resources/updated` notification via `ctx.session.send_resources_updated([uri])` and updates `last_hash`
       - Reschedules itself at the configured interval
    6. Returns confirmation JSON with subscription details

  - `unsubscribe_resource(ctx, uri: str) -> str`:
    1. Looks up URI in `_subscription_registry`
    2. Cancels the timer thread
    3. Removes entry from registry
    4. Returns confirmation

  - `_compute_hash(data: str) -> str`: `hashlib.md5(data.encode()).hexdigest()` — fast, no collisions matter

  - `_get_resource_data(uri: str) -> str`: fetches resource data by calling the registered handler for that URI

  - `_cleanup_subscriptions()`: called on server stop — cancels all timer threads, clears registry

  - Exports `register_subscription_handlers(mcp)` — registers MCP tools `subscribe_resource` and `unsubscribe_resource` on the FastMCP instance (NOTE: these will be registered via server.py wiring in Todo 7 instead; this module exports the internal functions)

  Thread safety: use `threading.Lock` on registry writes. Timer threads are daemon (don't block shutdown).

  Must NOT: Exceed 5 concurrent subscriptions (hard limit in `subscribe_resource`). Must NOT allow interval < 500ms. Must NOT use real-time push (Live API doesn't support it). Must NOT modify resources.py. Must NOT import external libs (stdlib only: `threading`, `hashlib`, `time`, `json`).

  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 6, 7 | Can parallelize with: 5
  References:
  - MCP subscribe protocol: `resources/updated` notification
  - MCP SDK: `ctx.session.send_resources_updated([uri])` in FastMCP
  - Stdlib: `threading.Timer`, `threading.Lock`, `hashlib.md5`
  - New file: `MCP_Server/resources_sub.py`
  - Auto-unsubscribe: hook into `mcp.on("shutdown")` or similar lifecycle
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import ast
  with open('MCP_Server/resources_sub.py') as f:
      content = f.read()
  tree = ast.parse(content)
  funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
  assert 'subscribe_resource' in funcs, 'subscribe_resource function not found'
  assert 'unsubscribe_resource' in funcs, 'unsubscribe_resource function not found'
  assert '_compute_hash' in funcs or '_hash' in content, 'hash computation not found'
  assert '_subscription_registry' in content or 'subscription_registry' in content, 'registry dict not found'
  # Check threading usage
  assert 'threading' in content or 'Timer' in content, 'threading/Timer not found'
  assert 'Lock' in content, 'thread lock not found for registry safety'
  print('resources_sub.py structure OK — subscription functions + registry + threading')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Subscribe to `live://track/0/device/0/parameters` with interval=1000 → returns confirmation, starts polling
  - HAPPY: Change a device parameter, subscription detects hash change, sends `resources/updated`
  - HAPPY: Unsubscribe from a URI → timer stops, registry entry removed
  - HAPPY: Try subscribing same URI twice → returns "already subscribed" or updates interval
  - FAILURE: Subscribe with interval=100 (< 500ms) → rejected, minimum enforced
  - FAILURE: Subscribe to non-existent URI → rejected, "resource not found"
  - FAILURE: Try 6th subscription (max 5) → rejected, "max 5 concurrent subscriptions"
  - FAILURE: Subscribe while interval_ms not int → clamp to 500ms or return error
  Evidence: .omo/evidence/task-2-sprint-08-resources-knowledge-v2.txt
  Commit: Y | feat(resources): add polling-based resource subscription system

- [ ] 3. Create third-party device knowledge (20+ plugins)
  What to do / Must NOT do:
  Create `MCP_Server/knowledge/devices/third_party.json` with realistic parameter schemas for 20+ popular plugins:

  Synths (8):
  - Serum (Xfer Records) — ~15 documented params: Osc A pitch/coarse/fine/level/blend, Osc B similar, Filter type/cutoff/res, env amounts, LFO rate
  - Massive (Native Instruments) — ~15 documented params: 3 oscillator tuning/position/intensity, filter cutoff/resonance, envelope amounts, modulation
  - Sylenth1 (Lennar Digital) — ~12 params: 4 oscillator tuning, filter, envelope
  - Spire (Reveal Sound) — ~12 params
  - Diva (u-he) — ~15 params
  - Hive (u-he) — ~12 params
  - Pigments (Arturia) — ~15 params
  - Vital (Matt Tytel) — ~12 params

  Samplers (2):
  - Kontakt (Native Instruments) — ~12 params
  - Battery (Native Instruments) — ~10 params

  Effects (10):
  - Valhalla Room — ~10 params (decay, pre-delay, mix, mod settings)
  - Valhalla Shimmer — ~10 params
  - FabFilter Pro-Q 3 — ~12 params (frequency, gain, Q, filter type, band settings)
  - FabFilter Pro-C 2 — ~10 params (threshold, ratio, attack, release, knee)
  - FabFilter Pro-L 2 — ~8 params (ceiling, threshold, style, attack, release)
  - Soundtoys EchoBoy — ~12 params (delay time, feedback, mix, filter, mode)
  - Soundtoys Decapitator — ~8 params (drive, tone, mix, style)
  - Soundtoys Little AlterBoy — ~6 params (formant, pitch, mix, robot)
  - iZotope Ozone 11 — ~15 params (mastering sections)
  - iZotope Neutron 5 — ~12 params (mix sections, EQ, comp)

  Schema format:
  ```json
  {
    "name": "Serum",
    "class_name": "SynthPluginDevice",
    "company": "Xfer Records",
    "parameter_count": 250,
    "parameters": [
      {"name": "Osc A Pitch", "index": 0, "range": [-24, 24], "default": 0, "unit": "semitones", "page": "Osc A"},
      {"name": "Osc A Coarse", "index": 1, "range": [-48, 48], "default": 0, "unit": "semitones"},
      {"name": "Osc A Level", "index": 2, "range": [0.0, 1.0], "default": 0.8, "unit": "normalized"},
      ...
    ]
  }
  ```

  Also update `MCP_Server/knowledge/__init__.py`:
  - Add `_load_third_party_devices()` that loads `third_party.json`
  - Exports `get_device_knowledge(device_name) -> dict` that searches both native and third-party
  - Exports `list_all_devices() -> list[str]` that returns merged list
  - Add `_third_party_cache: dict` for in-memory caching

  Must NOT: Include all 500+ params per device (document ~10-15 essential params each). Must NOT include undocumented/guessed parameter indices. Must mark all indices as "approximate" in a `disclaimer` field per device: `"disclaimer": "Parameter indices are approximate — verify with get_device_parameters in Live before critical use"`. Must NOT scrape websites.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 4
  References:
  - Existing device knowledge: `MCP_Server/knowledge/` directory
  - Knowledge __init__.py: `MCP_Server/knowledge/__init__.py` (add third-party loading here)
  - Existing devices: `MCP_Server/knowledge/devices/` (synths.json, samplers.json, etc.)
  - Parameter index usage pattern: `send_command("set_device_parameter", track, device, param_index, value)`
  - Parameter index reference pattern: `MCP_Server/server.py` set_device_parameter tool
  - Reference: ableton-mind 55 device schemas, Ableton user manual for plugin parameter ranges
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import json
  with open('MCP_Server/knowledge/devices/third_party.json') as f:
      devices = json.load(f)
  assert isinstance(devices, list), 'third_party.json should be a list'
  assert len(devices) >= 20, f'Expected >=20 devices, got {len(devices)}'
  total_params = sum(len(d.get('parameters', [])) for d in devices)
  assert total_params >= 100, f'Expected >=100 total params, got {total_params}'
  # Verify each device has required fields
  for d in devices:
      assert 'name' in d, f'Device missing name: {d.get(\"name\", \"UNKNOWN\")}'
      assert 'company' in d, f'{d[\"name\"]} missing company'
      assert 'parameters' in d, f'{d[\"name\"]} missing parameters'
      assert len(d['parameters']) >= 5, f'{d[\"name\"]} has < 5 parameters'
  print(f'{len(devices)} devices, {total_params} parameters — all valid')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call `get_device_knowledge("Serum")` → returns schema with 15+ params, company, disclaimer
  - HAPPY: Call `list_all_devices()` → returns 55+ names (36 native + 20+ third-party)
  - HAPPY: Call `get_device_knowledge("FabFilter Pro-Q 3")` → returns EQ params with frequency/gain/Q ranges
  - HAPPY: Each parameter has name, index, range, default, unit fields
  - FAILURE: Call `get_device_knowledge("NonExistentPlugin")` → returns None or "device not found"
  - FAILURE: third_party.json malformed JSON → __init__.py logs error and continues (graceful fallback)
  Evidence: .omo/evidence/task-3-sprint-08-resources-knowledge-v2.txt
  Commit: Y | feat(knowledge): add 20+ third-party plugin device schemas

- [ ] 4. Create production recipes directory (5+ recipes)
  What to do / Must NOT do:
  Create `MCP_Server/knowledge/recipes/` directory with 5+ production recipe JSON files:

  **`minimal_techno.json`:**
  ```json
  {
    "name": "Minimal Techno Setup",
    "genre": "techno",
    "description": "Build a minimal techno session from scratch",
    "tracks": [
      {"name": "Kick", "instrument": "Drum Rack", "pattern": "techno_4x4", "effects": ["EQ Eight", "Compressor"]},
      {"name": "Hihat", "instrument": "Drum Rack", "pattern": "one_drop"},
      {"name": "Clap", "instrument": "Drum Rack", "pattern": "house_basic"},
      {"name": "Bass", "instrument": "Operator", "preset": "Deep Mono"},
      {"name": "Pad", "instrument": "Wavetable", "preset": "Warm Pad"}
    ],
    "mix": {"kick_level": -6, "bass_level": -8, "pad_level": -12},
    "effects_sends": {"reverb": 0.3, "delay": 0.15},
    "steps": [
      "1. delete_all_tracks()",
      "2. create_midi_track(0..4) for each track",
      "3. Set track names and load instruments",
      "4. set_tempo(130)",
      "5. create_drum_pattern on Kick/Hihat/Clap",
      "6. create_clip + add_notes_to_clip for Bass and Pad",
      "7. Apply mix levels and effect sends"
    ]
  }
  ```

  **`ambient_pad.json`:**
  ```json
  {
    "name": "Ambient Pad Sound",
    "genre": "ambient",
    "description": "Create a lush ambient pad using Wavetable with extensive reverb and delay",
    "tracks": [
      {"name": "Pad", "instrument": "Wavetable", "preset": "Warm Pad"},
      {"name": "Texture", "instrument": "Wavetable", "preset": "Cloud Texture"}
    ],
    "effects_chain": [
      {"device": "Hybrid Reverb", "params": {"decay": 12, "mix": 0.6}},
      {"device": "Delay", "params": {"time": 0.5, "feedback": 0.3}},
      {"device": "Auto Filter", "params": {"frequency": 0.3, "resonance": 0.4}}
    ],
    "mix": {"pad_level": -10, "texture_level": -16}
  }
  ```

  **`drum_mix.json`:**
  ```json
  {
    "name": "Drum Bus Mix Chain",
    "genre": "generic",
    "description": "Standard drum processing chain on a return/group track",
    "chain": [
      {"device": "Drum Buss", "params": {"mode": 0, "drive": 0.15, "boom": 0.2}},
      {"device": "Glue Compressor", "params": {"threshold": -12, "ratio": 4, "attack": 0.1, "release": 100}},
      {"device": "EQ Eight", "params": {"band": {"freq": 40, "gain": 2, "type": "low_shelf"}}}
    ],
    "notes": "Apply this chain to a group track containing all drum tracks"
  }
  ```

  Plus 2 more recipes (choose from):
  - `acid_bass.json` — 303-style acid bassline using Drift or Operator
  - `deep_house_chords.json` — lush deep house chord progression setup
  - `reverb_dub_echo.json` — classic dub reggae echo/delay chain
  - `sidechain_pump.json` — sidechain compression recipe for pumping effect

  Update `MCP_Server/knowledge/__init__.py`:
  - Add `_load_recipes()` that scans `recipes/` directory
  - Exports `get_recipe(name: str) -> dict`
  - Exports `list_recipes() -> list[str]` — returns recipe names
  - Caches recipes in `_recipe_cache: dict`

  Must NOT: Include executable Python code (recipes are guidance JSON, not scripts). Must NOT reference absolute file paths. Must NOT create recipes with destructive operations (no delete without confirmation steps).

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 3
  References:
  - Knowledge base loading: `MCP_Server/knowledge/__init__.py`
  - New directory: `MCP_Server/knowledge/recipes/`
  - Drum pattern variants from AGENTS.md: one_drop, rockers, steppers, house_basic, techno_4x4, dub_techno
  - Existing AGENTS.md session setup workflow order
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import json, os
  recipes_dir = 'MCP_Server/knowledge/recipes'
  assert os.path.isdir(recipes_dir), 'recipes directory not found'
  files = [f for f in os.listdir(recipes_dir) if f.endswith('.json')]
  assert len(files) >= 5, f'Expected >=5 recipe files, found {len(files)}: {files}'
  for f in files:
      with open(os.path.join(recipes_dir, f)) as fh:
          recipe = json.load(fh)
      assert 'name' in recipe, f'{f} missing name'
      assert 'description' in recipe, f'{f} missing description'
      assert 'tracks' in recipe or 'chain' in recipe or 'effects_chain' in recipe, f'{f} no recipe content'
      print(f'  {f}: \"{recipe[\"name\"]}\"')
  print(f'{len(files)} recipe files — all valid')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call `list_recipes()` → returns ["minimal_techno", "ambient_pad", "drum_mix", ...]
  - HAPPY: Call `get_recipe("minimal_techno")` → returns full recipe with tracks, mix, steps
  - HAPPY: Each recipe has name, description, and content (tracks/chain/effects)
  - FAILURE: Call `get_recipe("nonexistent")` → returns None or "recipe not found"
  - FAILURE: malformed recipe JSON → __init__.py logs error and skips that recipe
  Evidence: .omo/evidence/task-4-sprint-08-resources-knowledge-v2.txt
  Commit: Y | feat(knowledge): add 5+ production recipe JSON files

- [ ] 5. Create `get_resource_preview` tool
  What to do / Must NOT do:
  In `MCP_Server/server.py` (or via `resources.py`), register a new MCP tool:

  ```python
  @mcp.tool()
  def get_resource_preview(ctx: Context, uri_pattern: str) -> str:
      """Preview the output format of a resource URI without connecting to Live.
      
      Shows sample JSON output for the given resource URI pattern.
      Useful for discovering what resources are available and their format.
      
      Examples:
        get_resource_preview("live://track/0/device/0/parameters")
        get_resource_preview("live://session/projects")
      """
      resource_previews = {
          "live://track/{ti}/device/{di}/parameters": [
              {"name": "Volume", "index": 0, "value": 0.85, "min": 0.0, "max": 1.0},
              {"name": "Pan", "index": 1, "value": 0.0, "min": -1.0, "max": 1.0},
              {"name": "Device On", "index": 2, "value": True}
          ],
          "live://track/{ti}/clip/{ci}/notes": [
              {"pitch": 60, "time": 0.0, "duration": 0.25, "velocity": 100},
              {"pitch": 64, "time": 1.0, "duration": 0.5, "velocity": 90},
              {"pitch": 67, "time": 2.0, "duration": 0.25, "velocity": 85}
          ],
          "live://scene/{si}/clip/{ci}": {
              "name": "Clip 1", "color": "#3366FF", "length": 4.0,
              "is_playing": False, "is_midi": True
          },
          "live://session/projects": [
              {"name": "My Track", "path": "~/Music/Ableton/Projects/My Track", 
               "last_modified": "2026-06-15", "file_size": 1024000}
          ]
      }
      # Match the URI pattern (handle URI templates with {placeholders})
      matched = _match_uri_pattern(uri_pattern, resource_previews)
      if matched is not None:
          return json.dumps({"status": "success", "uri": uri_pattern, "preview": matched}, indent=2)
      return json.dumps({"status": "error", "message": f"Unknown resource URI: {uri_pattern}. Available: {list(resource_previews.keys())}"}, indent=2)
  ```

  Also add a helper `_match_uri_pattern` in `resources.py` that matches a URI against known resource templates (strip {params} and compare structure).

  Must NOT: Connect to Live (preview is static mock data). Must NOT replace the actual resource handler. Must NOT include real session data. Must update the preview data if resource schemas change.

  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 7 | Can parallelize with: 2
  References:
  - MCP tool registration: `MCP_Server/server.py` @mcp.tool() pattern
  - Resource URIs: defined in Todo 1 (resources.py)
  - URI template matching: extract URI stem (strip {params} parts) and compare
  - Helper function location: `MCP_Server/resources.py`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  # Verify get_resource_preview tool exists in server.py or resources.py
  with open('MCP_Server/resources.py') as f:
      content = f.read()
  assert 'get_resource_preview' in content, 'get_resource_preview not found in resources.py'
  assert 'resource_previews' in content or 'preview' in content, 'preview data not found'
  assert '_match_uri_pattern' in content or 'match' in content, 'URI pattern matching not found'
  print('get_resource_preview tool found with preview data')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call `get_resource_preview("live://track/0/device/0/parameters")` → returns example JSON with device params
  - HAPPY: Call `get_resource_preview("live://session/projects")` → returns example project list
  - HAPPY: Call `get_resource_preview("live://track/0/clip/0/notes")` → returns example MIDI note data
  - FAILURE: Call `get_resource_preview("live://invalid/uri")` → returns error with available URIs
  Evidence: .omo/evidence/task-5-sprint-08-resources-knowledge-v2.txt
  Commit: Y | feat(resources): add get_resource_preview tool for URI discovery

- [ ] 6. Create `subscribe_resource` and `unsubscribe_resource` MCP tools
  What to do / Must NOT do:
  Register two MCP tools (in `MCP_Server/resources.py` alongside `get_resource_preview`):

  ```python
  @mcp.tool()
  def subscribe_resource(ctx: Context, uri: str, interval_ms: int = 1000) -> str:
      """Subscribe to a resource URI for live updates.
      
      Polls the resource at the given interval and sends resources/updated
      notifications when the state changes.
      
      Args:
          uri: The resource URI to subscribe to (e.g., live://track/0/device/0/parameters)
          interval_ms: Polling interval in milliseconds (minimum 500ms, default 1000ms)
      
      Returns:
          JSON confirmation with subscription details
      """
      # Delegates to resources_sub.subscribe_resource(ctx, uri, interval_ms)
      ...

  @mcp.tool()
  def unsubscribe_resource(ctx: Context, uri: str) -> str:
      """Unsubscribe from a resource URI, stopping live updates.
      
      Args:
          uri: The resource URI to unsubscribe from
      
      Returns:
          JSON confirmation or error if not subscribed
      """
      # Delegates to resources_sub.unsubscribe_resource(ctx, uri)
      ...
  ```

  These tools delegate to the subscription system in `resources_sub.py` (Todo 2).
  Import from `MCP_Server.resources_sub` and call the internal functions.
  Handle errors: resource not found, not subscribed, max subscriptions reached.
  Return JSON responses for MCP client compatibility.

  Must NOT: Implement polling logic here (delegate to resources_sub.py). Must NOT exceed max 5 subscriptions. Must NOT allow interval < 500ms.

  Parallelization: Wave 3 | Blocked by: 2 | Blocks: 7 | Can parallelize with: None
  References:
  - Subscription system: `MCP_Server/resources_sub.py` (Todo 2)
  - Tool pattern: `MCP_Server/server.py` @mcp.tool() decorator usage
  - Error handling: return JSON with status: "error" and message field
  - import: `from MCP_Server.resources_sub import subscribe_resource as _sub_subscribe, unsubscribe_resource as _sub_unsubscribe`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/resources.py') as f:
      content = f.read()
  assert 'def subscribe_resource' in content, 'subscribe_resource not found in resources.py'
  assert 'def unsubscribe_resource' in content, 'unsubscribe_resource not found in resources.py'
  assert 'resources_sub' in content, 'delegation to resources_sub not found'
  # Verify the tools handle errors
  assert 'error' in content.lower() or 'not subscribed' in content or 'not found' in content, 'error handling missing'
  print('subscribe_resource and unsubscribe_resource tools registered')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call `subscribe_resource("live://track/0/device/0/parameters", interval_ms=1000)` → subscription confirmed, polling starts
  - HAPPY: Call `unsubscribe_resource("live://track/0/device/0/parameters")` → subscription cancelled
  - FAILURE: Call `subscribe_resource("live://invalid")` → error "resource not found"
  - FAILURE: Call `unsubscribe_resource("live://track/0/device/0/parameters")` when not subscribed → error "not subscribed"
  - FAILURE: Call `subscribe_resource(..., interval_ms=100)` → error "minimum interval 500ms"
  Evidence: .omo/evidence/task-6-sprint-08-resources-knowledge-v2.txt
  Commit: Y | feat(resources): add subscribe_resource and unsubscribe_resource MCP tools

- [ ] 7. Wire all registrations in server.py
  What to do / Must NOT do:
  Update `MCP_Server/server.py` to integrate all new modules:

  1. Add imports at top of server.py:
  ```python
  from MCP_Server.resources import register_resources, get_resource_preview, subscribe_resource, unsubscribe_resource
  from MCP_Server.resources_sub import cleanup_subscriptions
  from MCP_Server.knowledge import get_device_knowledge, list_all_devices, get_recipe, list_recipes
  ```

  2. Find or create a resource registration block after the existing submodule registrations (around line ~775):
  ```python
  # ------------------------------------------------------------------
  # MCP Resources — URI-addressable session state
  # ------------------------------------------------------------------
  register_resources(mcp)
  ```

  3. Register tools (if not using decorators directly in resources.py):
  ```python
  # Resource preview and subscription tools are registered via @mcp.tool()
  # in resources.py — already handled at module import
  ```

  4. Hook cleanup on shutdown:
  ```python
  # In the shutdown handler or on_startup callback:
  @mcp.on("shutdown")
  def _on_shutdown():
      cleanup_subscriptions()
  ```

  5. Update knowledge loading to include third-party and recipes:
  - The knowledge `__init__.py` is already updated in Todo 3 and 4 — ensure `list_all_devices()` and `list_recipes()` work
  - Verify no import errors or circular imports

  6. Verify the server starts without errors:
  ```bash
  python -c "from MCP_Server.server import mcp; print('Server module loaded OK')"
  ```

  Must NOT: Create circular imports (resources.py should not import from server.py). Must NOT modify existing tool bodies. Must NOT break existing registrations order.

  Parallelization: Wave 3 | Blocked by: 1, 2, 3, 4, 5, 6 | Blocks: 8 | Can parallelize with: None
  References:
  - Server submodule registration: `MCP_Server/server.py:752-775`
  - Import pattern: `from MCP_Server.advanced_tools import register_advanced_tools` (line ~750)
  - Shutdown handler: not yet in server.py — create `@mcp.on("shutdown")` callback
  - FastMCP lifecycle: `@mcp.on("startup")`, `@mcp.on("shutdown")`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import ast
  # Verify all imports present in server.py
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'from MCP_Server.resources import' in content or 'from MCP_Server import resources' in content, 'resources import missing'
  assert 'register_resources' in content, 'register_resources call missing'
  assert 'cleanup_subscriptions' in content or 'resources_sub' in content, 'subscription cleanup missing'
  
  # Verify the module loads without syntax errors
  compile(content, 'MCP_Server/server.py', 'exec')
  print('server.py imports, registrations, and syntax OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: server.py imports resources module → no import errors
  - HAPPY: `register_resources(mcp)` called → resource URIs available
  - HAPPY: Shutdown handler calls `cleanup_subscriptions()` → all timers stopped
  - FAILURE: Circular import between resources.py and server.py → caught at test time
  Evidence: .omo/evidence/task-7-sprint-08-resources-knowledge-v2.txt
  Commit: Y | feat(server): wire resource module, subscription cleanup, and knowledge updates

- [ ] 8. Create `tests/test_resources_v2.py`
  What to do / Must NOT do:
  Create `tests/test_resources_v2.py` with standalone test cases (no pytest discovery):

  Test cases:
  1. `test_resources_module_imports()` — verify `resources.py` imports cleanly, `register_resources` is callable
  2. `test_resource_uri_count()` — verify at least 4 URIs registered via `@mcp.resource()` in resources.py
  3. `test_uri_pattern_matching()` — test `_match_uri_pattern` with various URI formats (exact match, template match, no match)
  4. `test_get_resource_preview_known_uri()` — verify preview returns data for known URIs
  5. `test_get_resource_preview_unknown_uri()` — verify preview returns error for unknown URIs
  6. `test_subscription_registry_creation()` — test that `_subscription_registry` dict is created and accessible
  7. `test_subscription_max_concurrent()` — verify subscribing 6 times returns error (if implemented)
  8. `test_subscription_min_interval()` — verify interval < 500ms is rejected
  9. `test_third_party_device_count()` — verify third_party.json has >= 20 devices with >= 100 total params
  10. `test_recipe_count()` — verify recipes directory has >= 5 JSON files
  11. `test_knowledge_loading_integration()` — verify `list_all_devices()` returns combined list
  12. `test_resource_uri_syntax()` — verify all URIs start with `live://` and use valid template syntax

  Each test must:
  - Print "PASS: <test_name>" on success
  - Print "FAIL: <test_name>: <reason>" on failure with `sys.exit(1)`
  - Be self-contained (no external Live connection needed)
  - Handle ImportError gracefully (skip with clear message if module not found)

  Must NOT: Require pytest or external test runners. Must NOT require Ableton Live running. Must NOT connect to Live. Must use mock/static data for resource resolution tests.

  Parallelization: Wave 4 | Blocked by: 1, 2, 7 | Blocks: None | Can parallelize with: None
  References:
  - Existing standalone test pattern: `scripts/test/test_connection.py`
  - Test directory: `tests/` (already exists)
  - Module APIs: `MCP_Server.resources`, `MCP_Server.resources_sub`, `MCP_Server.knowledge`
  - Static data: third_party.json is a JSON file — no Live connection needed
  - URI template matching test: provide known templates and verify matching logic
  Acceptance criteria (agent-executable):
  ```bash
  python tests/test_resources_v2.py
  # Expected: All 12 tests PASS
  # Exit code 0 on success, 1 on failure
  ```
  QA scenarios: happy + failure
  - HAPPY: All 12 tests pass → clean exit code 0, all "PASS" lines
  - HAPPY: Each test has clear test name describing what it verifies
  - FAILURE: Missing module dependency → specific test fails with ImportError message
  - FAILURE: third_party.json has < 20 devices → test_third_party_device_count fails with count
  Evidence: .omo/evidence/task-8-sprint-08-resources-knowledge-v2.txt
  Commit: Y | test(resources): add test suite for resource URIs, subscriptions, knowledge, and recipes

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: Verify all 8 deliverables exist, all scope boundaries respected
- [ ] F2. Resource URI count: `grep -c "@mcp.resource" MCP_Server/resources.py` >= 4
- [ ] F3. Third-party device count: `python -c "import json; devices=json.load(open('MCP_Server/knowledge/devices/third_party.json')); print(len(devices))"` >= 20
- [ ] F4. Recipe count: `ls MCP_Server/knowledge/recipes/*.json | wc -l` >= 5
- [ ] F5. Test suite: `python tests/test_resources_v2.py` — all tests pass (exit 0)
- [ ] F6. Syntax check: All new/modified .py files pass `python -c "compile(open(f).read(), f, 'exec')"` for `MCP_Server/resources.py`, `MCP_Server/resources_sub.py`, `MCP_Server/server.py`, `MCP_Server/knowledge/__init__.py`, `tests/test_resources_v2.py`
- [ ] F7. Scope fidelity: grep for Must NOT have violations (no >5 concurrent subscriptions, no pip deps, no Remote Script handler modifications, no existing URI modifications)
- [ ] F8. Subscription limit check: verify `_subscription_registry` enforces max 5 concurrent

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(resources): add resources.py module with 4 new resource URIs
- feat(resources): add polling-based resource subscription system
- feat(knowledge): add 20+ third-party plugin device schemas
- feat(knowledge): add 5+ production recipe JSON files
- feat(resources): add get_resource_preview tool for URI discovery
- feat(resources): add subscribe_resource and unsubscribe_resource MCP tools
- feat(server): wire resource module, subscription cleanup, and knowledge updates
- test(resources): add test suite for resource URIs, subscriptions, knowledge, and recipes

No squashing — each commit is independently testable. Tags: none.

## Success criteria
- `grep -c "@mcp.resource" MCP_Server/resources.py` >= 4
- `python -c "import json; devices=json.load(open('MCP_Server/knowledge/devices/third_party.json')); assert len(devices) >= 20"` passes
- `ls MCP_Server/knowledge/recipes/*.json | wc -l` >= 5
- `python tests/test_resources_v2.py` exits with code 0 (all 12 tests pass)
- `python -c "from MCP_Server.resources_sub import _subscription_registry; assert isinstance(_subscription_registry, dict)"` passes
- `subscribe_resource("live://track/0/device/0/parameters", interval_ms=1000)` returns confirmation
- `subscribe_resource("live://invalid")` returns error
- `subscribe_resource(..., interval_ms=100)` returns error (minimum 500ms)
- `get_resource_preview("live://track/0/device/0/parameters")` returns sample JSON with parameter data
- `get_resource_preview("live://invalid")` returns error with available URIs
- `list_all_devices()` returns 55+ device names
- `list_recipes()` returns 5+ recipe names
- No new pip dependencies added
- No existing resource URIs modified or deleted
- No new TCP/UDP commands or Remote Script handlers
