# ableton-mcp-comprehensive-upgrade - Work Plan

## TL;DR (For humans)

**What you'll get:** Your Ableton MCP grows from 211 tools with zero MCP resources into a proper MCP server with live session resources (like `live://track/1` you can just read), a knowledge base of 30+ Live device parameters so the AI stops guessing parameter indices, a verify loop that catches silent failures, automation envelope control, offline project file analysis, full browser crawling, and groove templates.

**Why this approach:** MCP Resources are the #1 missing pattern - without them agents must call tools repeatedly to learn session state. The verify loop is #2 - 211 unchecked tools can silently fail. Device knowledge is the feature that makes the AI actually useful for production. Everything else builds on these foundations.

**What it will NOT do:** Rewrite existing tools, add audio export (impossible via Remote Script), add Push hardware support (no hardware to test), or add new pip dependencies beyond what's needed for Max bridge (deferred).

**Effort:** Large (5-7 sprints, ~3-4 weeks total)
**Risk:** Medium - Remote Script API changes risk Live crashes; verify loop must not mutate state
**Decisions to sanity-check:** Resource URI naming scheme, device knowledge extraction approach (manual vs scraped), Max bridge technology choice

Your next move: Approve this plan, then run `$start-work` to begin execution.

---

> TL;DR (machine): XL effort, Medium risk (Live API stability). 8 deliverables across 4 waves. First wave: MCP Resources + verify loop. Second wave: device knowledge + browser scan. Third wave: automation + .als parsing. Fourth wave: groove tools + Max bridge spec.

## Scope
### Must have
- MCP Resource URIs for session, track, scene, device, clip state (read-only, wrapping existing get_*)
- Device knowledge base: 30+ Live native devices with full parameter schemas (JSON)
- Verify loop: post-call decorator on all modifying tools returning {ok, verified, diff}
- Automation envelope: read/write clip envelopes, read track automation, write automation points
- Offline .als parsing: open .als, extract track/clip/device structure, return structured info
- Browser deep scan: recursive browser tree walk to discover all instruments/effects
- Groove tools: list grooves, apply groove, remove groove, set groove amount
- Max for Live bridge: architecture document + prototype IPC path

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT modify existing tool bodies (verify wraps externally)
- Do NOT add new pip deps for device knowledge, .als parsing, or resources (stdlib only; Max bridge is the exception)
- Do NOT attempt audio render/export - impossible via Remote Script API
- Do NOT add Push hardware support
- Do NOT duplicate existing get_* functionality as tools
- Do NOT exceed 10 UDP commands
- Do NOT modify LSP server configuration
- Do NOT add new socket protocols (OSC for Max bridge is the only new transport)

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after + manual Live smoke for each wave
- Evidence: .omo/evidence/task-<N>-ableton-mcp-comprehensive-upgrade.<ext>

## Execution strategy
### Parallel execution waves
| Wave | Focus | Todos | Est. days |
|------|-------|-------|-----------|
| 1 | MCP Resources + Verify loop | 1, 2 | 4 |
| 2 | Device knowledge + Browser scan | 3, 4 | 5 |
| 3 | Automation envelopes + .als parsing | 5, 6 | 5 |
| 4 | Groove tools + Max bridge | 7, 8 | 5 |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. MCP Resources | None | 2 | None |
| 2. Verify loop | 1 | None | None |
| 3. Device knowledge | None | None | 4 |
| 4. Browser deep scan | None | None | 3 |
| 5. Automation envelopes | None | None | 6 |
| 6. Offline .als parsing | None | None | 5 |
| 7. Groove tools | None | None | 8 |
| 8. Max bridge architecture | None | None | 7 |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [x] 1. Add MCP Resource URIs for session state
  What to do / Must NOT do:
  Register `@mcp.resource` URIs on the FastMCP `mcp` instance in `MCP_Server/server.py` wrapping existing get_* handlers:
  - `live://status` → get_session_info() wrapper (connection + transport state)
  - `live://session/current` → get_session_info() (tempo, time sig, track count, transport)
  - `live://track/{track_index}` → get_track_info(track_index) wrapper
  - `live://scene/{scene_index}` → get_all_scenes() filtered to one scene
  - `live://device/{track_index}/{device_index}` → get_device_parameters(ti, di) wrapper
  - `live://clip/{track_index}/{clip_index}` → get_all_clips_in_track(ti) filtered to one clip
  Must NOT: Create new get_* TCP commands (reuse existing). Must NOT duplicate existing tool functionality.
  Must add resource templates for parameterized URIs using FastMCP's `@mcp.resource` URI template syntax.

  Parallelization: Wave 1 | Blocked by: None | Blocks: Verify loop
  References:
  - FastMCP resource registration: `MCP_Server/server.py:747` mcp = FastMCP(...)
  - Existing tools to wrap: `MCP_Server/server.py:send_command` (line 183)
  - get_session_info: `MCP_Server/server.py` around line 1062
  - get_track_info: `MCP_Server/server.py` around line 1072
  - get_all_scenes: `MCP_Server/advanced_tools.py` line 160
  - get_all_clips_in_track: `MCP_Server/advanced_tools.py` line 171
  - FastMCP resource docs: https://github.com/modelcontextprotocol/python-sdk
  - livemcp URIs for reference: live://status, live://session/current, live://track/{track_index}
  Acceptance criteria (agent-executable):
  ```bash
  # Verify each resource returns valid JSON
  python -c "
  import asyncio; from mcp.client.session import ClientSession
  # or: test that @mcp.resource decorators are present in server.py
  import re
  code = open('MCP_Server/server.py').read()
  resources = re.findall(r'@mcp\.resource\([\"'](.+?)[\"']\)', code)
  assert len(resources) >= 6, f'Expected >=6 resources, got {len(resources)}'
  print(f'Resources registered: {resources}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Register `live://track/1`, call via MCP client, verify returns valid JSON with track info
  - HAPPY: Register `live://status`, call without Ableton running, returns error state gracefully
  - FAILURE: Register `live://track/9999`, verify returns error for out-of-range index
  Evidence: .omo/evidence/task-1-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | feat(resources): add live:// MCP resource URIs for session/track/scene/device/clip state

- [x] 2. Add verify loop for all modifying tools
  What to do / Must NOT do:
  Create `MCP_Server/verify.py` with a decorator `@verify_modification` that:
  1. Captures pre-call snapshot of relevant session state (via existing get_* tools)
  2. Calls the original tool
  3. Captures post-call snapshot
  4. Computes diff between pre and post state
  5. Returns `{"ok": true/false, "verified": bool, "diff": {...}}` alongside the tool's original output

  The verify loop wraps only modifying tools (create/delete/set/add/duplicate/load etc.) - NOT read-only get_* tools.
  Categorize the ~211 tools into read-only vs modifying using the existing `is_modifying_command` list at `server.py:193-251` as the reference.

  Must NOT: Modify existing tool bodies. Must NOT add latency to read-only tools. Must NOT call verify on UDP commands.
  Must store pre/post snapshots in a thread-safe way (post-call only, no file I/O).

  Parallelization: Wave 1 | Blocked by: None (parallel with MCP Resources) | Blocks: None
  References:
  - Modifying command list: `MCP_Server/server.py:193-251`
  - Tool registration pattern: `MCP_Server/server.py:752-765`
  - ableton-mind verify loop pattern: https://github.com/Pantani/ableton-mind (verify loop returns {ok, verified, diff})
  - Python decorator pattern for existing functions
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import ast, sys
  with open('MCP_Server/verify.py') as f:
      tree = ast.parse(f.read())
  # Verify decorator exists
  funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
  assert 'verify_modification' in funcs or any('verify' in f for f in funcs), 'verify function not found'
  print('verify.py structure OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call `create_midi_track(0)` wrapped with verify, verify returns {ok: true, verified: true, diff: {track_count: +1}}
  - HAPPY: Call `get_session_info()` (read-only), verify does NOT wrap it
  - FAILURE: Call `delete_track(1)` when only 1 track exists, verify catches that it returns error
  Evidence: .omo/evidence/task-2-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | feat(verify): add post-call verify loop for all modifying MCP tools

- [x] 3. Device knowledge base (30+ Live native devices)
  What to do / Must NOT do:
  Create directory `MCP_Server/knowledge/devices/` with one JSON file per device group:
  - `MCP_Server/knowledge/__init__.py` (load all device schemas)
  - `MCP_Server/knowledge/devices/synths.json` (Wavetable, Operator, Drift, Meld, Bass, Analog, Collision, Electric, Tension)
  - `MCP_Server/knowledge/devices/samplers.json` (Simpler, Sampler, Drum Sampler)
  - `MCP_Server/knowledge/devices/audio_effects.json` (EQ Eight, Glue Compressor, Drum Buss, Multiband Dynamics, Spectral Resonator, Roar, Hybrid Reverb, Pedal, Channel EQ, Compressor, Gate, Limiter, Utility)
  - `MCP_Server/knowledge/devices/midi_effects.json` (Arpeggiator, Chord, Scale, Pitch, Random, Velocity)
  - `MCP_Server/knowledge/devices/instruments.json` (Impulse, Instrument Rack, Drum Rack)

  Each device schema format:
  ```json
  {
    "name": "Wavetable",
    "class_name": "WavetableDevice",
    "parameters": [
      {"name": "Osc 1 Position", "index": 0, "range": [0.0, 1.0], "default": 0.0, "unit": "normalized"},
      {"name": "Osc 1 Semi", "index": 1, "range": [-24, 24], "default": 0, "unit": "semitones"},
      ...
    ],
    "categories": ["synth"]
  }
  ```

  Add a tool `query_device_knowledge(ctx, device_name: str, parameter_name: str = "")` that returns the schema for a device or parameter.
  Must NOT: Scrape undocumented XML formats. Must NOT add new pip dependencies.
  Must cover: name, class_name, parameter name, index, range, default, unit for each parameter.

  Parallelization: Wave 2 | Blocked by: None | Blocks: None
  References:
  - Parameter index pattern: `MCP_Server/server.py:send_command("set_device_parameter", ...)` with parameter_index
  - ableton-mind device schemas: https://github.com/Pantani/ableton-mind (55 devices)
  - Live 12 built-in device list: https://www.ableton.com/en/live/learn-live/
  - To extract device parameters: run `get_device_parameters` for each device type in Live and record the output
  - `MCP_Server/knowledge/` - new directory
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import json, os
  knowledge_dir = 'MCP_Server/knowledge/devices'
  files = os.listdir(knowledge_dir)
  total_devices = 0
  total_params = 0
  for f in files:
      if f.endswith('.json'):
          with open(os.path.join(knowledge_dir, f)) as fh:
              devices = json.load(fh)
              for dev in devices:
                  total_devices += 1
                  total_params += len(dev.get('parameters', []))
  assert total_devices >= 30, f'Expected >=30 devices, got {total_devices}'
  assert total_params >= 200, f'Expected >=200 total params, got {total_params}'
  print(f'{total_devices} devices, {total_params} parameters')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Open session with Wavetable, call query_device_knowledge("Wavetable"), get back full parameter schema
  - HAPPY: query_device_knowledge("Wavetable", "Osc 1 Position"), get back specific parameter range [0.0, 1.0]
  - FAILURE: query_device_knowledge("NonExistentDevice"), get "device not found"
  Evidence: .omo/evidence/task-3-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | feat(knowledge): add device knowledge base with 30+ Live native device schemas

- [x] 4. Browser recursive deep scan
  What to do / Must NOT do:
  Add a new tool `scan_browser_recursive(ctx, root_path: str = "", max_depth: int = 5) -> str` in `MCP_Server/server.py` that:
  1. Starts from a browser root (e.g. "Instruments", "Audio Effects", "MIDI Effects", "Sounds", "Drums", "Plugins")
  2. Recursively calls `get_browser_items_at_path` for each folder discovered
  3. Builds a tree structure of all discoverable items (name, type, uri, is_loadable, is_folder)
  4. Returns the full tree as JSON
  5. Implements depth limit + visited-set dedup to avoid infinite loops
  6. Caches result per root path with TTL (reuse existing `_browser_cache` pattern)

  Also add a new Remote Script handler `_get_recursive_browser_children(path, depth)` in `AbletonMCP_Remote_Script/__init__.py` that walks a browser branch server-side and returns the subtree (reduces round-trips).

  Must NOT: Overwrite existing get_browser_items_at_path. Must NOT crawl the entire browser on startup.
  Must have: max_items limits, depth limits, visited-path dedup, timeout protection.

  Parallelization: Wave 2 | Blocked by: None | Blocks: None
  References:
  - Existing browser tool: `MCP_Server/server.py:2759` get_browser_items_at_path
  - Browser cache pattern: `MCP_Server/server.py:548-615` _browser_cache, BROWSER_CACHE_TTL
  - Remote Script browser handler: `AbletonMCP_Remote_Script/__init__.py` get_browser_items_at_path
  - livemcp recursive crawl: https://github.com/alaarab/livemcp - recursive browser explorer
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  # Verify the tool function is registered
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'def scan_browser_recursive' in content or 'browser_recursive' in content, 'scan_browser_recursive not found'
  assert 'def _get_recursive_browser_children' in open('AbletonMCP_Remote_Script/__init__.py').read(), '_get_recursive_browser_children not found'
  print('Browser recursive scan functions registered')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call scan_browser_recursive("Instruments", max_depth=3), get tree of synths/subfolders/samples
  - HAPPY: Call scan_browser_recursive("Drums", max_depth=2), get drum kits with loadable URIs
  - FAILURE: Call scan_browser_recursive("", max_depth=0), get "root path required"
  - FAILURE: Call scan_browser_recursive("InvalidCategory", max_depth=5), get "category not found" with available categories
  Evidence: .omo/evidence/task-4-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | feat(browser): add recursive browser deep scan tool

- [x] 5. Automation envelope support
  What to do / Must NOT do:
  Add new Remote Script handlers and MCP tools for clip and track automation:

  New Remote Script handlers in `AbletonMCP_Remote_Script/__init__.py`:
  - `_get_clip_envelope(track_index, clip_index, parameter_index)` → returns envelope points [{time, value, interpolation}]
  - `_set_clip_envelope_point(track_index, clip_index, parameter_index, time, value)` → adds/updates an envelope point
  - `_clear_clip_envelope(track_index, clip_index, parameter_index)` → removes all automation for a parameter
  - `_get_track_automation(track_index, device_index, parameter_index)` → returns track automation envelope points
  - `_set_track_automation_point(track_index, device_index, parameter_index, time, value)` → adds track automation point

  New MCP tools in new `MCP_Server/automation_tools.py`:
  - `register_automation_tools(mcp, get_ableton_connection)` following the existing submodule pattern
  - Tools: `get_clip_envelope`, `set_clip_envelope_point`, `clear_clip_envelope`, `get_track_automation`, `set_track_automation_point`

  Must NOT: Attempt arrangement automation (Live API is read-only for arrangement via Remote Script).
  Must use `Clip.automation_envelopes` and `DeviceParameter.automation_state` in Remote Script.
  Must handle: no envelope exists (return empty list), parameter has no automation (return empty).

  Parallelization: Wave 3 | Blocked by: None | Blocks: None
  References:
  - Existing clip envelope tool: `MCP_Server/advanced_tools.py:288` get_clip_envelopes (basic - needs extension)
  - Live API: Clip.automation_envelopes, AutomationEnvelope (Live 12 Object Model)
  - Remote Script handler registration pattern: `AbletonMCP_Remote_Script/__init__.py` command dispatch
  - Submodule pattern: `MCP_Server/advanced_tools.py:48` register_advanced_tools
  - Server registration: `MCP_Server/server.py:752-765`
  - livemcp arrangement tools: 9 arrangement tools including automation
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/automation_tools.py') as f:
      content = f.read()
  assert 'def register_automation_tools' in content, 'register_automation_tools not found'
  assert 'get_clip_envelope' in content, 'get_clip_envelope not found'
  assert 'set_clip_envelope_point' in content, 'set_clip_envelope_point not found'
  assert 'clear_clip_envelope' in content, 'clear_clip_envelope not found'
  assert 'def _get_clip_envelope' in open('AbletonMCP_Remote_Script/__init__.py').read(), '_get_clip_envelope not found'
  print('Automation tools + handlers registered')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call get_clip_envelope(track=0, clip=0, param=2) on a clip with volume automation, returns envelope points
  - HAPPY: Call set_clip_envelope_point(track=0, clip=0, param=2, time=2.0, value=0.8), creates a point at beat 2
  - HAPPY: Call clear_clip_envelope(track=0, clip=0, param=2), removes all points for that parameter
  - FAILURE: Call get_clip_envelope(track=999, clip=0, param=2), get "track index out of range"
  - FAILURE: Call set_clip_envelope_point(track=0, clip=0, param=999, time=2.0, value=0.8), parameter not found
  Evidence: .omo/evidence/task-5-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | feat(automation): add clip/track automation envelope read/write tools

- [x] 6. Offline .als project parsing
  What to do / Must NOT do:
  Create standalone module `MCP_Server/als_parser.py` with no Ableton connection dependency:
  - `parse_als_file(path: str) -> dict` → opens gzipped .als, parses XML, extracts:
    - track list (name, type, devices, clips, automation count)
    - device chain per track (device name, class_name, parameter count)
    - tempo, time signature, global transport settings
    - return tracks, master track settings
    - cue/locator points
  - `detect_als_issues(data: dict) -> list` → returns potential issues:
    - empty tracks
    - tracks with no devices
    - clips with no notes
    - missing sends on tracks
    - tempo automation present
  - `suggest_als_changes(data: dict) -> list` → returns suggestions:
    - tracks that could be grouped
    - naming inconsistencies
    - optimization suggestions

  Add a new tool `analyze_als_project(ctx, file_path: str) -> str` that loads and analyzes a .als file.
  Add a new tool `suggest_als_improvements(ctx, file_path: str) -> str` that returns suggestions.

  Must NOT: Create new dependencies (stdlib gzip + xml.etree.ElementTree only).
  Must NOT: Write to .als files (read-only analysis).
  Must use test fixtures: include a minimal .als test file (gzipped XML with one track).

  Parallelization: Wave 3 | Blocked by: None | Blocks: None
  References:
  - .als format: gzipped XML (Ableton Live Set). Root element: `<Ableton MajorVersion="5" MinorVersion="...">`
  - XML schema: `<LiveSet> → <Tracks> → <MidiTrack>/<AudioTrack> → <DeviceChain> → <Devices> → <ClipSlotList>`
  - Existing projects: teamallnighter/ableton-cookbook-mcp, closestfriend/ableton-proj-mcp, bassDaddyDevices/ABLE-MCP
  - Python stdlib: `gzip`, `xml.etree.ElementTree`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.als_parser import parse_als_file, detect_als_issues
  import tempfile, gzip, os
  # Create a minimal .als test file
  als_content = b'<?xml version=\"1.0\"?><Ableton MajorVersion=\"5\"><LiveSet><Tracks><MidiTrack><Name><EffectiveName Value=\"Test Track\"/></Name><DeviceChain/></MidiTrack></Tracks></LiveSet></Ableton>'
  tmp = tempfile.NamedTemporaryFile(suffix='.als', delete=False)
  with gzip.open(tmp.name, 'wb') as f: f.write(als_content)
  result = parse_als_file(tmp.name)
  os.unlink(tmp.name)
  assert 'tracks' in result, 'tracks key missing'
  assert len(result['tracks']) >= 1, 'expected >= 1 track'
  assert result['tracks'][0]['name'] == 'Test Track'
  issues = detect_als_issues(result)
  assert isinstance(issues, list)
  print('als_parser.py works correctly')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call analyze_als_project("test.als") on a .als with 3 tracks, returns track list + metadata
  - HAPPY: Call suggest_als_improvements("test.als"), gets suggestions
  - FAILURE: Call analyze_als_project("nonexistent.als"), get "file not found"
  - FAILURE: Call analyze_als_project("not_an_als.txt"), get "not a valid .als file"
  Evidence: .omo/evidence/task-6-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | feat(als): add offline .als project parsing and analysis tools

- [x] 7. Groove template tools
  What to do / Must NOT do:
  Add new Remote Script handlers in `AbletonMCP_Remote_Script/__init__.py`:
  - `_get_available_grooves()` → returns list of groove template names from Live's groove pool
  - `_apply_groove(track_index, clip_index, groove_name, amount=1.0)` → applies groove to a clip
  - `_remove_groove(track_index, clip_index)` → removes groove from a clip
  - `_set_groove_amount(amount)` → sets global groove amount

  Add new MCP tools in new `MCP_Server/groove_tools.py`:
  - `register_groove_tools(mcp, get_ableton_connection)` following the existing submodule pattern
  - Tools: `list_groove_templates`, `apply_groove_to_clip`, `remove_groove_from_clip`, `set_global_groove_amount`
  - Register in `MCP_Server/server.py:752-765` alongside other tools

  Must NOT: Create new groove templates (read-only pool). Must NOT apply groove to audio clips.
  Must verify: clip exists, groove name exists, track index valid.

  Parallelization: Wave 4 | Blocked by: None | Blocks: None
  References:
  - Live API: Song.groove_amount, Clip.groove, Clip.is_midi_clip
  - Remote Script handler pattern: `AbletonMCP_Remote_Script/__init__.py` command dispatch
  - Submodule pattern: `MCP_Server/mixer_tools.py:28` register_mixer_tools
  - Server registration: `MCP_Server/server.py:752-765`
  - livemcp groove support (reference implementation)
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/groove_tools.py') as f:
      content = f.read()
  assert 'def register_groove_tools' in content, 'register_groove_tools not found'
  assert 'list_groove_templates' in content or 'apply_groove_to_clip' in content, 'groove tools not found'
  assert 'def _get_available_grooves' in open('AbletonMCP_Remote_Script/__init__.py').read(), '_get_available_grooves not found'
  assert 'register_groove_tools(mcp' in open('MCP_Server/server.py').read(), 'groove registration not found in server.py'
  print('Groove tools + handlers registered')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call list_groove_templates(), get list of available groove names
  - HAPPY: Call apply_groove_to_clip(track=0, clip=0, groove="Swing 16", amount=0.5), groove applied
  - HAPPY: Call remove_groove_from_clip(track=0, clip=0), groove removed
  - FAILURE: Call apply_groove_to_clip(track=0, clip=0, groove="NonexistentGroove", amount=0.5), "groove not found"
  - FAILURE: Call apply_groove_to_clip(track=0, clip=-1, groove="Swing 16"), "invalid clip index"
  Evidence: .omo/evidence/task-7-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | feat(grooves): add groove template tools (list/apply/remove/amount)

- [x] 8. Max for Live bridge architecture document + prototype
  What to do / Must NOT do:
  Create `docs/max-bridge-architecture.md` covering:
  1. Communication options: OSC (python-osc) vs named pipes vs UDP
  2. Recommended approach: OSC via python-osc connecting to Max's `udpreceive` object
  3. Security model: localhost-only, configurable port, command allowlist
  4. Data flow: MCP tool → TCP to Remote Script → OSC to Max patcher → Max for Live device
  5. Required Max patcher: `max_devices/mcp_bridge.maxpat` that receives OSC messages and forwards to Live API
  6. Tool surface (planned): `load_max_device`, `get_max_device_info`, `send_max_message`, `open_in_max`, `toggle_presentation`
  7. Capabilities unlocked: audio rendering, custom device creation, signal processing, UI manipulation

  Create prototype implementation:
  - `MCP_Server/max_bridge.py` with MaxBridgeClient class (OSC sender)
  - `max_devices/mcp_bridge.maxpat` skeleton (empty patcher with udpreceive + forward)
  - Connection test tool: `test_max_bridge(ctx) → str` that sends ping OSC message and checks response

  Must NOT: Implement full Max tool surface (this is architecture + prototype only).
  Must NOT: Add python-osc as hard dependency (optional import with graceful fallback).
  Must document: security implications, failure modes, latency characteristics.

  Parallelization: Wave 4 | Blocked by: None | Blocks: None (architecture only)
  References:
  - AbletonOSC: https://github.com/ideoforms/AbletonOSC (OSC protocol for Live)
  - python-osc: https://pypi.org/project/python-osc/
  - livemcp Max bridge: `src/livemcp/tools/max.py`, `remote_script/LiveMCP/handlers/max.py`
  - Existing Max device: `max_devices/audio_export_device.maxpat` (reference patcher)
  - OSC spec: http://opensoundcontrol.org/spec-1_0
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  assert open('docs/max-bridge-architecture.md').read().strip(), 'architecture doc missing or empty'
  "
  python -c "
  with open('MCP_Server/max_bridge.py') as f:
      content = f.read()
  assert 'MaxBridgeClient' in content, 'MaxBridgeClient not found'
  assert 'test_max_bridge' in content, 'test_max_bridge not found'
  print('Max bridge module OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Read docs/max-bridge-architecture.md, verify all 6 planned tools documented
  - HAPPY: Import MCP_Server.max_bridge without python-osc installed, graceful import error with helpful message
  - HAPPY: Call test_max_bridge() without Max running, get "Max not reachable"
  Evidence: .omo/evidence/task-8-ableton-mcp-comprehensive-upgrade.txt
  Commit: Y | docs(max-bridge): add Max for Live bridge architecture document and prototype

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [x] F1. Plan compliance audit: Verify all 8 deliverables exist, all scope boundaries respected
- [x] F2. Code quality review: All .py files pass `python -c "compile(open(f).read(), f, 'exec')"`, no syntax errors
- [ ] F3. Live smoke test: Start Ableton + Remote Script, call one tool from each new domain (resource, verify, knowledge, browser, automation, als, groove, max) — **requires Ableton Live running, skip in CI**
- [x] F4. Scope fidelity: grep for Must NOT have violations (no Push, no audio export, no new UDP, no LSP mods)

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(resources): ...
- feat(verify): ...
- feat(knowledge): ...
- feat(browser): ...
- feat(automation): ...
- feat(als): ...
- feat(grooves): ...
- docs(max-bridge): ...

No squashing - each commit is independently testable. Tags: none.

## Success criteria
All MCP resources return valid JSON responses
All 30+ device schemas load and return correct parameter data
Verify loop returns {ok, verified, diff} for all modifying tools
Automation envelope points can be read, written, and cleared
.als parser extracts track/clip/device structure from real Ableton projects
Browser deep scan discovers 100+ items in a real Live installation
Groove tools list/apply/remove grooves without errors
Max bridge document covers all architectural decisions and next steps
