# sprint-07-dj-performance - Work Plan

## TL;DR (For humans)

**What you'll get:** Professional DJ tools running as first-class MCP tools — automatic beat-matched transitions between tracks, harmonic mixing suggestions via the Camelot Wheel, queue-based auto-mix playlists, DJ-style effects (filter sweep, echo out, beat repeat, brake, flanger), and loop roll / beat-jump effects. Built on top of Sprint 06's audio analysis for key detection.

**Why this approach:** Our existing DJ scripts (`ultra_dj_loop.py`, `live_dj_performance.py`) work but live outside the MCP tool surface — agents can't orchestrate them. Moving the logic into `dj_engine.py` (composable) and `dj_tools.py` (5 MCP tools) makes every transition, harmonic match, and effect callable directly. The Camelot Wheel knowledge file makes harmonic mixing deterministic and verifiable without real-time audio analysis.

**What it will NOT do:** No real-time audio analysis (pre-analyze at queuing time), no new UDP commands (existing 10-command limit), no external BPM/key detection (Sprint 06 or user-provided only), no modification of user's existing clip content, no beat-grid detection from scratch (use transport quantization).

**Effort:** Medium (5 days, 5 new tools)
**Risk:** Medium — transition timing drifts (mitigated by bar-based scheduling), DJ effects need devices that may not exist (mitigated by temporary device creation + cleanup), auto-mix crashes (mitigated by try/except per transition)
**Decisions to sanity-check:** Camelot Wheel data completeness (all 24 positions with correct neighbors), transition timeline structure (bar-relative vs absolute time), effect device fallback strategy

Your next move: Approve this plan, then run `$start-work` to begin execution.

---

> TL;DR (machine): Medium effort, Medium risk (Live API timing sensitivity). 7 deliverables across 4 waves. First wave: knowledge files + remote script handlers (parallel). Second wave: DJ engine core (transition calc + harmonic mixer). Third wave: 5 DJ MCP tools (depends on engine + handlers). Fourth wave: server integration + ultra_dj_loop refactor + test suite.

## Scope
### Must have
- `MCP_Server/knowledge/camelot_wheel.json`: Complete Camelot Wheel (12 keys × 2 modes = 24 positions) with neighbor energies
- `MCP_Server/knowledge/dj_effects.json`: 5 DJ effect recipes (filter_sweep, echo_out, beat_repeat, brake, flanger) with device/parameter specs
- `MCP_Server/dj_engine.py`: Transition Calculator (5 transition types), Harmonic Mixer (key compatibility + next-key suggestion), Cue Point Manager (set/get cues)
- `MCP_Server/dj_tools.py`: 5 MCP tools (execute_transition, queue_auto_mix, suggest_harmonic_match, apply_dj_effect, beat_jump_loop)
- `AbletonMCP_Remote_Script/__init__.py`: New handlers (`_get_clip_key`, `_get_playback_state`)
- `MCP_Server/server.py`: Import + register DJ tools via `register_dj_tools()`
- `scripts/ultra_dj_loop.py`: Light refactor for consistency with new tool API
- `tests/test_dj_tools.py`: Unit tests for transition calculation, harmonic compatibility, effect application

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT rely on external BPM/key detection (Sprint 06 or user-provided only)
- Do NOT attempt to analyze audio in real-time (pre-analyze at queuing time)
- Do NOT delete or modify user's existing clip content
- Do NOT add new UDP commands (use existing 10-command limit)
- Do NOT implement beat-grid detection from scratch (use transport quantization)
- Do NOT modify existing tool bodies in server.py (additive changes only)
- Do NOT add new pip dependencies

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: unit tests (`tests/test_dj_tools.py`) + Python assertion checks for each wave
- Evidence: .omo/evidence/task-<N>-sprint-07-dj-performance.<ext>

## Execution strategy
### Parallel execution waves
| Wave | Focus | Todos | Est. days |
|------|-------|-------|-----------|
| 1 | Knowledge files + Remote Script handlers | 1, 2 | 1 |
| 2 | DJ Engine core (transition, harmony, cues) | 3 | 1.5 |
| 3 | 5 DJ MCP tools | 4, 5 | 1.5 |
| 4 | Server integration + ultra_dj_loop refactor + tests | 6, 7 | 1 |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Knowledge files (camelot_wheel.json, dj_effects.json) | None | 3 | 2 |
| 2. Remote Script handlers (_get_clip_key, _get_playback_state) | None | 5 | 1 |
| 3. DJ Engine (dj_engine.py) | 1 | 4, 5 | None |
| 4. DJ Tools part 1 (execute_transition, suggest_harmonic_match) | 3 | 6 | 5 |
| 5. DJ Tools part 2 (queue_auto_mix, apply_dj_effect, beat_jump_loop) | 2, 3 | 6 | 4 |
| 6. Server integration + ultra_dj_loop refactor | 4, 5 | 7 | None |
| 7. Test suite | 6 | None | None |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [ ] 1. Create knowledge files (camelot_wheel.json + dj_effects.json)
  What to do / Must NOT do:
  Create `MCP_Server/knowledge/camelot_wheel.json`:
  - Full Camelot Wheel with all 24 positions (8A through 1B → wrapping back to 8A)
  - Each position: `{"key": "...", "mode": "...", "neighbors": ["...", "...", "..."]}`
  - Neighbors: +1 energy (next key same mode), -1 energy (prev key same mode), relative major/minor
  - Verify: 8A neighbors = ["8B", "9A", "7A"], 8B neighbors = ["8A", "9B", "7B"]
  - Final entry wraps: 1A neighbors = ["1B", "2A", "8A"], 1B neighbors = ["1A", "2B", "8B"]

  Create `MCP_Server/knowledge/dj_effects.json`:
  - 5 effect recipes with device name, parameter names, automation curve:
    - `filter_sweep`: Auto Filter, frequency=0.0→1.0, resonance=0.3, 4 bars
    - `echo_out`: Beat Repeat / Delay, feedback=0.3→0.9, repeat_rate=1/4, 4 bars
    - `beat_repeat`: Beat Repeat, chance=0.0→0.8, rate=1/8→1/16→1/32, 4 bars (stutter effect)
    - `brake`: Utility, volume=1.0→0.0, reverb=0.0→0.5, 2 bars (stop effect)
    - `flanger`: Flanger, rate=0.1→0.5, feedback=0.2→0.7, 4 bars
  - Each effect: `{name, device, params [{name, start, end}], bars, description}`

  Must NOT: Add incomplete or approximate Camelot data — all 24 positions must be correct.
  Must NOT: Add effects that require devices not available in Live 12.

  Parallelization: Wave 1 | Blocked by: None | Blocks: DJ Engine
  References:
  - Camelot Wheel: https://mixedinkey.com/camelot-wheel/
  - Effect parameters: Standard Live 12 built-in device parameters
  - Knowledge dir pattern: `MCP_Server/knowledge/` (existing directory)
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import json
  with open('MCP_Server/knowledge/camelot_wheel.json') as f:
      wheel = json.load(f)
  assert len(wheel) == 24, f'Expected 24 positions, got {len(wheel)}'
  assert '8A' in wheel, '8A missing'
  assert '8B' in wheel, '8B missing'
  assert wheel['8A']['neighbors'] == ['8B', '9A', '7A'], f'Wrong neighbors for 8A: {wheel[\"8A\"][\"neighbors\"]}'
  assert wheel['1A']['neighbors'] == ['1B', '2A', '8A'], f'Wrong neighbors for 1A (wraparound): {wheel[\"1A\"][\"neighbors\"]}'
  assert wheel['1B']['neighbors'] == ['1A', '2B', '8B'], f'Wrong neighbors for 1B (wraparound): {wheel[\"1B\"][\"neighbors\"]}'
  print(f'Camelot Wheel OK: {len(wheel)} positions, neighbors verified')
  "
  ```
  ```bash
  python -c "
  import json
  with open('MCP_Server/knowledge/dj_effects.json') as f:
      effects = json.load(f)
  assert len(effects) >= 5, f'Expected >=5 effects, got {len(effects)}'
  assert 'filter_sweep' in effects, 'filter_sweep missing'
  assert 'echo_out' in effects, 'echo_out missing'
  assert 'beat_repeat' in effects, 'beat_repeat missing'
  assert 'brake' in effects, 'brake missing'
  assert 'flanger' in effects, 'flanger missing'
  for name, spec in effects.items():
      assert 'device' in spec, f'{name}: device missing'
      assert 'params' in spec, f'{name}: params missing'
      assert 'bars' in spec, f'{name}: bars missing'
  print(f'DJ Effects OK: {len(effects)} effects with valid structure')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Load camelot_wheel.json, query 8A neighbors → returns ["8B", "9A", "7A"]
  - HAPPY: Load camelot_wheel.json, query 1A → returns with wraparound neighbors ["1B", "2A", "8A"]
  - HAPPY: Load dj_effects.json, query filter_sweep → returns device "Auto Filter" with frequency start=0.0 end=1.0
  - FAILURE: Load camelot_wheel.json with missing position, assert error
  Evidence: .omo/evidence/task-1-sprint-07-dj-performance.txt
  Commit: Y | feat(knowledge): add Camelot Wheel and DJ effects knowledge files

- [ ] 2. Add Remote Script handlers (playback control + clip key)
  What to do / Must NOT do:
  Add new handlers in `AbletonMCP_Remote_Script/__init__.py`:
  - `_get_clip_key(track_index, clip_index)` — reads key from clip name (parses "C minor" or "8A" patterns), or from track/clip user data if tagged. Returns dict: `{key, mode, camelot_position, source}`
  - `_get_playback_state(track_index, clip_index)` — returns: `{is_playing: bool, is_triggered: bool, position: float, playing_status: str}` using Live's `Clip.playing_status`, `Clip.is_triggered`, `Clip.playing_position`

  Follow existing handler dispatch pattern (command name → handler method mapping in the socket receive loop).
  Must NOT: Add new UDP commands. Must NOT: Create new socket messages — reuse existing `send_command` pattern.
  Must handle: clip doesn't exist (return error), no key tagged (return null key with source="unknown").

  Parallelization: Wave 1 | Blocked by: None | Blocks: queue_auto_mix, beat_jump_loop
  References:
  - Handler dispatch pattern: `AbletonMCP_Remote_Script/__init__.py` — command dispatch in socket receive loop
  - UDP commands pattern (existing): `set_crossfader` already implemented
  - Live API: `Clip.playing_status`, `Clip.is_triggered`, `Clip.playing_position`, `Clip.name`
  - Crossfader handler: `_set_crossfader` (already exists via UDP — do NOT duplicate)
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('AbletonMCP_Remote_Script/__init__.py') as f:
      content = f.read()
  assert 'def _get_clip_key' in content, '_get_clip_key handler not found'
  assert 'def _get_playback_state' in content, '_get_playback_state handler not found'
  # Verify dispatch entries exist
  assert \"'get_clip_key'\" in content or '\"get_clip_key\"' in content, 'get_clip_key not in command dispatch'
  assert \"'get_playback_state'\" in content or '\"get_playback_state\"' in content, 'get_playback_state not in command dispatch'
  print('Remote Script handlers registered')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call _get_clip_key(track=0, clip=0) on a track named "C minor" → returns `{key: "C", mode: "minor", source: "clip_name"}`
  - HAPPY: Call _get_playback_state(track=0, clip=0) on a playing clip → returns `{is_playing: true, position: 4.0}`
  - FAILURE: Call _get_clip_key(track=99, clip=0) → returns error "track index out of range"
  - FAILURE: Call _get_playback_state(track=0, clip=0) on empty slot → returns `{is_playing: false, is_triggered: false}`
  Evidence: .omo/evidence/task-2-sprint-07-dj-performance.txt
  Commit: Y | feat(remote-script): add get_clip_key and get_playback_state handlers

- [ ] 3. Implement DJ Engine (dj_engine.py)
  What to do / Must NOT do:
  Create `MCP_Server/dj_engine.py` with three classes/functions:

  **Transition Calculator:**
  ```python
  def calculate_transition(state_a: dict, state_b: dict, bars: int = 8,
                           transition_type: str = "eq_sweep") -> list[dict]
  ```
  - Takes track state dicts: `{bpm, key, mode, volume, filter_state, current_bar}`
  - Returns timeline of `[{bar, action, track, value, ...}]` actions
  - 5 transition types with distinct patterns:
    - `hard_cut` (0 bars): Instant swap at bar boundary. 2 steps: crossfade to B at bar 0, complete at bar 0
    - `eq_sweep` (8 bars): Low pass filter A down (bars 0-3, 0.0→1.0) → fade A volume down (bars 3-4, 1.0→0.0) → crossfade to B (bar 4, 0.0→1.0 over 1 bar) → filter B up (bars 5-7, 1.0→0.0) → complete at bar 8. ~16 steps baseline.
    - `filter_fade` (4 bars): Filter A down (bars 0-1) → crossfade (bar 1-2) → filter B up (bar 2-3) → complete. ~8 steps.
    - `loop_roll` (8 bars): Loop 1/4 on A (bars 0-3) → stutter loop 1/8 (bar 3-4) → crossfade (bar 4-6) → drop B (bar 6) → complete. ~12 steps
    - `beat_match` (16 bars): Tempo ramp A→B (bar 0-8) → EQ swap (bar 8-12) → crossfade (bar 12-14) → B full (bar 14-16). ~20 steps
  - Each timeline entry: `{bar: float, action: str, track: int, value: float}`
  - Actions: `filter_down`, `filter_up`, `volume_down`, `volume_up`, `crossfade`, `tempo_ramp`, `loop_on`, `loop_off`, `stutter_on`, `stutter_off`, `fire_clip`, `complete`
  - Validate: transition_type must be one of the 5; bars must align with type's minimum; states must have `bpm`

  **Harmonic Mixer:**
  ```python
  def get_harmonic_compatibility(key_a: str, mode_a: str,
                                  key_b: str, mode_b: str) -> dict
  ```
  - Returns: `{compatible: bool, energy_change: int (-2 to +2), relationship_text: str, camelot_a: str, camelot_b: str}`
  - Uses camelot_wheel.json for lookup
  - Loads camelot_wheel.json from `MCP_Server/knowledge/camelot_wheel.json`
  - Energy change: same position = 0, neighbor = ±1, skip neighbor = ±2, incompatible = None
  - Relationship text: "Same key" / "Energy +1" / "Energy -1" / "Major boost" / etc.

  ```python
  def suggest_next_key(current_key: str, current_mode: str,
                       direction: str) -> dict
  ```
  - direction: "up_energy", "down_energy", "relative_minor", "relative_major"
  - Returns: `{key: str, mode: str, camelot: str, relationship: str}`
  - Maps key+mode to Camelot position via lookup table

  **Cue Point Manager:**
  ```python
  def set_cue(track_index: int, clip_index: int,
              cue_time: float, cue_name: str = "") -> dict
  def get_cues(track_index: int, clip_index: int) -> list[dict]
  ```
  - In-memory cue store (dict keyed by `f"{track_index}:{clip_index}"`)
  - Each cue: `{name: str, time: float, color: str (default "white")}`
  - `set_cue` returns: `{cue_id: str, name: str, time: float}`
  - `get_cues` returns: list of cues sorted by time

  Must NOT: Access any Live API directly (pure computation). Must NOT: Have external dependencies beyond stdlib + json.
  Must handle: unknown keys (return incompatible), negative energy change (wrap to 0 minimum - not below -2).

  Parallelization: Wave 2 | Blocked by: knowledge files | Blocks: DJ Tools
  References:
  - Camelot Wheel: `MCP_Server/knowledge/camelot_wheel.json` (created in todo 1)
  - Transition types spec: sprint-07 spec section 7.1
  - Crossfader action values: 0.0 = track A, 1.0 = track B (consistent with Live)
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.dj_engine import get_harmonic_compatibility, suggest_next_key, calculate_transition, set_cue, get_cues

  # Harmonic mixer tests
  result = get_harmonic_compatibility('C', 'minor', 'G', 'minor')
  assert 'compatible' in result, f'compatible key missing: {result}'
  assert 'energy_change' in result, f'energy_change missing: {result}'
  print(f'Harmonic compatibility Cm→Gm: {result}')

  # Same key should be compatible, energy change 0
  same = get_harmonic_compatibility('C', 'minor', 'C', 'minor')
  assert same['compatible'] == True
  assert same['energy_change'] == 0
  print(f'Same key: {same}')

  # Next key suggestion
  next_key = suggest_next_key('C', 'minor', 'up_energy')
  print(f'Next key up from Cm: {next_key}')

  # Transition calculator
  timeline = calculate_transition(
      {'bpm': 128, 'key': 'C', 'mode': 'minor'},
      {'bpm': 130, 'key': 'G', 'mode': 'minor'},
      bars=8
  )
  assert len(timeline) > 0, 'timeline empty'
  assert timeline[-1]['action'] == 'complete', f'last action not complete: {timeline[-1]}'
  print(f'Transition plan: {len(timeline)} steps')

  # Cue point manager
  cue = set_cue(0, 0, 4.0, 'Drop')
  assert 'cue_id' in cue and 'name' in cue
  cues = get_cues(0, 0)
  assert len(cues) >= 1
  print(f'Cue points: {cues}')

  print('DJ Engine ALL OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: get_harmonic_compatibility("C", "minor", "G", "minor") → compatible=True, energy_change=+1
  - HAPPY: suggest_next_key("C", "minor", "up_energy") → returns key in {"G", "C#", "D"} range
  - HAPPY: calculate_transition(..., "eq_sweep", 8) → returns 16±2 step timeline ending in "complete"
  - HAPPY: calculate_transition(..., "hard_cut", 0) → returns 2-3 step timeline (instant)
  - HAPPY: set_cue + get_cues roundtrip → cue stored and retrieved
  - FAILURE: get_harmonic_compatibility("C#", "unknown", "G", "minor") → compatible=False, energy_change=None
  - FAILURE: calculate_transition({}, {}) → ValueError (missing required fields)
  - FAILURE: calculate_transition(..., transition_type="unknown") → ValueError (invalid type)
  Evidence: .omo/evidence/task-3-sprint-07-dj-performance.txt
  Commit: Y | feat(engine): add DJ engine with transition calculator, harmonic mixer, cue point manager

- [ ] 4. Implement DJ Tools part 1 (execute_transition + suggest_harmonic_match)
  What to do / Must NOT do:
  Create `MCP_Server/dj_tools.py` with:

  ```python
  def register_dj_tools(mcp, get_ableton_connection):
  ```

  Following the existing submodule pattern (see `MCP_Server/advanced_tools.py:48` `register_advanced_tools`).

  **Tool: `execute_transition`**
  - Signature: `(ctx, from_track: int, to_track: int, from_clip: int = 0, to_clip: int = 0, transition_type: str = "eq_sweep", bars: int = 8) -> str`
  - Implementation:
    1. Get current state of both tracks (BPM via `get_session_info`, volume/mute via existing get_* tools)
    2. Call `dj_engine.calculate_transition(state_a, state_b, bars, transition_type)`
    3. Execute each timeline step at the correct bar position:
       - Uses `set_track_volume`, `set_track_mute`, `fire_clip`, `set_master_volume` via UDP/TCP
       - Filter actions → `set_device_parameter` on Auto Filter device (if present)
       - Crossfade actions → `set_master_volume` or crossfader
       - Tempo ramp → multiple `set_tempo` calls over the ramp duration
    4. Sync to Live transport timing: schedule by bar number using `get_current_beats_playing_bar` + `set_clip_launch_mode`
    5. Returns: JSON string with timeline summary + result per step

  - Validate: transition_type in {"hard_cut", "eq_sweep", "filter_fade", "loop_roll", "beat_match"}; bars >= minimum for type; track indices valid
  - Error handling: If a step fails, log error and continue with remaining steps (best-effort)

  **Tool: `suggest_harmonic_match`**
  - Signature: `(ctx, track_index: int, clip_index: int, available_tracks: str = "") -> str`
  - Implementation:
    1. Read current track's key via `_get_clip_key` handler or `get_harmonic_compatibility` with user-provided key
    2. Parse `available_tracks` JSON: `[{"track": N, "key": "...", "mode": "..."}, ...]`
    3. If no key in available_tracks, try to detect via `_get_clip_key` for each
    4. If no key data at all, fall back to BPM-based matching (closest BPM wins)
    5. For each available track, call `get_harmonic_compatibility(current_key, current_mode, track_key, track_mode)`
    6. Rank by: compatible first, then by energy_change magnitude (smaller = better mix)
    7. Append `transition_suggestion` based on energy_change:
       - energy_change == 0: "eq_sweep" is safe
       - abs(energy_change) == 1: "filter_fade"
       - else: "beat_match" (needs more blending)
    8. Returns: JSON string with ranked list: `[{track, key, mode, camelot_a, camelot_b, compatible, energy_change, transition_suggestion}]`

  Must NOT: Modify user's existing clips. Must NOT: Use external key detection services.
  Must store timeline steps with timestamps for audit/logging.

  Parallelization: Wave 3 | Blocked by: DJ Engine | Blocks: Server integration
  References:
  - Submodule registration pattern: `MCP_Server/advanced_tools.py:48`
  - Server tool annotation pattern: `MCP_Server/server.py:752-765` @server.tool decorators
  - UDP commands available: `set_track_volume`, `set_track_mute`, `fire_clip`, `set_master_volume`, `set_device_parameter`, `set_clip_launch_mode`
  - get_session_info: `MCP_Server/server.py` around line 1062
  - dj_engine functions: todo 3
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/dj_tools.py') as f:
      content = f.read()
  assert 'def register_dj_tools' in content, 'register_dj_tools not found'
  assert 'def execute_transition' in content or 'execute_transition' in content, 'execute_transition not found'
  assert 'def suggest_harmonic_match' in content or 'suggest_harmonic_match' in content, 'suggest_harmonic_match not found'
  # Verify both tools are in register_dj_tools
  assert '@server.tool' in content or 'mcp.tool' in content or '@mcp.tool' in content, 'tool decorator pattern not found'
  print('DJ Tools part 1 registered')
  "
  ```
  ```bash
  python -c "
  from MCP_Server.dj_engine import calculate_transition
  # Verify transition calculator is importable from tool context
  timeline = calculate_transition(
      {'bpm': 128, 'key': 'C', 'mode': 'minor'},
      {'bpm': 130, 'key': 'G', 'mode': 'minor'},
      bars=8, transition_type='eq_sweep'
  )
  actions = {step['action'] for step in timeline}
  assert 'complete' in actions, 'complete action missing'
  print(f'execute_transition backing engine OK: {len(timeline)} steps, actions: {actions}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: execute_transition(from_track=0, to_track=1, transition_type="eq_sweep", bars=8) → returns JSON timeline with 16±2 steps ending in complete
  - HAPPY: execute_transition with hard_cut → returns 2-step timeline, instant swap
  - HAPPY: suggest_harmonic_match with available_tracks=[{track:1, key:"G", mode:"minor"}] → returns ranked list with compatible=True
  - FAILURE: execute_transition(from_track=0, to_track=1, transition_type="unknown") → error "invalid transition type"
  - FAILURE: execute_transition(from_track=0, to_track=1, bars=0) → error "bars < minimum for eq_sweep" (or valid for hard_cut)
  - FAILURE: suggest_harmonic_match with empty available_tracks → returns empty list
  Evidence: .omo/evidence/task-4-sprint-07-dj-performance.txt
  Commit: Y | feat(dj-tools): add execute_transition and suggest_harmonic_match tools

- [ ] 5. Implement DJ Tools part 2 (queue_auto_mix + apply_dj_effect + beat_jump_loop)
  What to do / Must NOT do:
  Add three more tools in `MCP_Server/dj_tools.py` (same `register_dj_tools` function):

  **Tool: `queue_auto_mix`**
  - Signature: `(ctx, track_pairs: str) -> str`
  - `track_pairs`: JSON string: `[{"track": 0, "clip": 0}, {"track": 1, "clip": 0}, {"track": 2, "clip": 0}]`
  - Implementation:
    1. Parse JSON input into list of track/clip pairs
    2. For each adjacent pair (0→1, 1→2, ...), determine optimal transition:
       - Call `suggest_harmonic_match` internally to check compatibility
       - If compatible and energy_change == 0: use `eq_sweep`
       - If compatible and abs(energy_change) == 1: use `filter_fade`
       - If compatible and abs(energy_change) == 2: use `beat_match` (16 bars)
       - If not compatible: use `hard_cut` (minimal interaction)
    3. Execute transitions sequentially (each waits for previous to complete via polling playback position)
    4. Try/except per transition — skip failed, continue queue
    5. Returns: JSON string: `{playlist: [{from, to, transition_type, bars, status}], total_duration_bars: N}`

  **Tool: `apply_dj_effect`**
  - Signature: `(ctx, track_index: int, effect: str = "filter_sweep", wet_amount: float = 0.5, bars: int = 4) -> str`
  - Implementation:
    1. Load effect recipe from `MCP_Server/knowledge/dj_effects.json`
    2. Check if target device exists on track (by device name match)
    3. If device doesn't exist, create temporary device on track
    4. Automate parameters over `bars` duration:
       - For each param with start/end: ramp from start to end over bars
       - For wet_amount < 1.0: scale all parameter targets by wet_amount
    5. After bars complete: optionally clean up temporary devices
    6. Returns: `{effect: str, track: int, bars: int, device: str, params_automated: [str]}`
  - Validate: effect must be one of the 5 in dj_effects.json; track_index valid; wet_amount 0.0-1.0; bars 1-16

  **Tool: `beat_jump_loop`**
  - Signature: `(ctx, track_index: int, clip_index: int, loop_size: float = 1.0, bars: int = 4) -> str`
  - Implementation:
    1. Get current clip loop settings (via existing get_clip_info or get_clip_loop)
    2. Set clip loop to `loop_size` beats (0.25, 0.5, 1.0, 2.0, 4.0)
    3. Enable loop on the clip
    4. Wait for `bars` duration (using bar counting via `get_current_beats_playing_bar`)
    5. Restore original loop settings and disable loop
    6. Returns: `{track: int, clip: int, loop_size: float, bars: int, original_loop_start: float, original_loop_end: float}`
  - Validate: loop_size in {0.25, 0.5, 1.0, 2.0, 4.0}; clip exists and is MIDI; bars 1-16
  - Must restore original loop settings after effect completes

  Must NOT: Leave temporary devices on tracks after completion (clean up). Must NOT: Block MCP server thread (async or fire-and-forget execution where possible).
  Must restore clip loop settings after beat_jump_loop completes.

  Parallelization: Wave 3 | Blocked by: DJ Engine, Remote Script handlers | Blocks: Server integration
  References:
  - dj_effects.json: `MCP_Server/knowledge/dj_effects.json` (created in todo 1)
  - Effect device creation: `load_instrument_or_effect` existing tool
  - Clip loop settings: existing `get_clip_loop` / `set_clip_loop` tools
  - get_current_beats_playing_bar: existing command
  - suggest_harmonic_match: todo 4 (internal call)
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/dj_tools.py') as f:
      content = f.read()
  assert 'def queue_auto_mix' in content or 'queue_auto_mix' in content, 'queue_auto_mix not found'
  assert 'def apply_dj_effect' in content or 'apply_dj_effect' in content, 'apply_dj_effect not found'
  assert 'def beat_jump_loop' in content or 'beat_jump_loop' in content, 'beat_jump_loop not found'
  print('DJ Tools part 2 registered')
  "
  ```
  ```bash
  python -c "
  import json
  with open('MCP_Server/knowledge/dj_effects.json') as f:
      effects = json.load(f)
  for name in ['filter_sweep', 'echo_out', 'beat_repeat', 'brake', 'flanger']:
      assert name in effects, f'{name} effect not found in knowledge file'
      spec = effects[name]
      assert 'device' in spec, f'{name}: missing device'
      assert 'params' in spec, f'{name}: missing params'
      assert 'bars' in spec, f'{name}: missing bars'
  print('All 5 DJ effects have valid knowledge entries')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: queue_auto_mix([{track:0}, {track:1}, {track:2}]) → returns playlist with transition choices for 0→1 and 1→2
  - HAPPY: apply_dj_effect(track=0, effect="filter_sweep", wet_amount=1.0, bars=4) → applies Auto Filter automation
  - HAPPY: beat_jump_loop(track=0, clip=0, loop_size=0.5, bars=4) → creates loop roll on 1/2-beat for 4 bars
  - FAILURE: apply_dj_effect(track=0, effect="nonexistent") → error "unknown effect"
  - FAILURE: beat_jump_loop(track=0, clip=0, loop_size=8.0) → error "loop_size must be one of 0.25, 0.5, 1.0, 2.0, 4.0"
  - FAILURE: queue_auto_mix("invalid json") → error "invalid track_pairs JSON"
  Evidence: .omo/evidence/task-5-sprint-07-dj-performance.txt
  Commit: Y | feat(dj-tools): add queue_auto_mix, apply_dj_effect, and beat_jump_loop tools

- [ ] 6. Server integration + ultra_dj_loop refactor
  What to do / Must NOT do:
  **Server integration in `MCP_Server/server.py`:**
  1. Add import: `from MCP_Server.dj_tools import register_dj_tools`
  2. Add registration call alongside existing tool registrations (near line 752-765):
     ```python
     from MCP_Server.dj_tools import register_dj_tools
     register_dj_tools(mcp, get_ableton_connection)
     ```
  3. Verify all 5 new tools appear in `server.py`'s tool list

  **ultra_dj_loop.py light refactor:**
  1. Open `scripts/ultra_dj_loop.py` and identify functions that overlap with new DJ Engine/Tools:
     - Transition logic → delegate to `dj_engine.calculate_transition`
     - Harmonic matching → delegate to `dj_engine.get_harmonic_compatibility`
     - Effect application → delegate to `dj_tools` apply_dj_effect
  2. Add import redirects so ultra_dj_loop.py calls MCP_Server.dj_engine functions internally
  3. Keep CLI entry points intact (don't break existing CLI usage)
  4. Add deprecation notice in docstring: "This script is being superseded by MCP Server DJ tools (MCP_Server/dj_tools.py)"

  Must NOT: Remove any existing functionality from ultra_dj_loop.py (additive refactor only).
  Must NOT: Change ultra_dj_loop.py CLI interface.
  Must verify import path works: `from MCP_Server.dj_tools import register_dj_tools`

  Parallelization: Wave 4 | Blocked by: DJ Tools (both parts) | Blocks: Tests
  References:
  - Tool registration area: `MCP_Server/server.py:752-765`
  - Existing imports pattern: `from MCP_Server.advanced_tools import register_advanced_tools` at top of server.py
  - ultra_dj_loop.py location: `scripts/ultra_dj_loop.py`
  - Submodule registration pattern: `MCP_Server/mixer_tools.py:28` register_mixer_tools
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'from MCP_Server.dj_tools import register_dj_tools' in content, 'DJ tools import not found in server.py'
  assert 'register_dj_tools(mcp' in content, 'register_dj_tools call not found in server.py'
  print('Server integration OK')
  "
  ```
  ```bash
  python -c "
  # Verify DJ tools module is importable (syntax check + all tools present)
  import importlib, sys
  # Add MCP_Server to path
  import MCP_Server.dj_tools as dt
  assert hasattr(dt, 'register_dj_tools'), 'register_dj_tools not found'
  print('DJ tools module importable OK')
  "
  ```
  ```bash
  python -c "
  # Verify ultra_dj_loop still runs (CLI should work or have deprecation notice)
  with open('scripts/ultra_dj_loop.py') as f:
      content = f.read()
  # Should reference dj_engine in some way
  has_ref = 'dj_engine' in content or 'MCP_Server.dj' in content or 'deprecat' in content.lower()
  print(f'ultra_dj_loop refactored: {has_ref}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Import MCP_Server.dj_tools, call register_dj_tools with mock mcp, verify 5 tools registered
  - HAPPY: Run `python scripts/ultra_dj_loop.py --help`, CLI still works
  - FAILURE: Import MCP_Server.dj_tools with broken dependencies, graceful error
  Evidence: .omo/evidence/task-6-sprint-07-dj-performance.txt
  Commit: Y | feat(server): integrate DJ tools into MCP server and refactor ultra_dj_loop.py

- [ ] 7. Create test suite (test_dj_tools.py)
  What to do / Must NOT do:
  Create `tests/test_dj_tools.py` with standalone tests (no pytest discovery — follows existing test pattern):

  **Test categories:**

  1. **Transition Calculator Tests:**
     - `test_transition_hard_cut()`: Verify 2-step timeline, instant swap
     - `test_transition_eq_sweep()`: Verify 16±2 step timeline with filter/volume/crossfade actions
     - `test_transition_filter_fade()`: Verify 8±2 step timeline (shorter than eq_sweep)
     - `test_transition_loop_roll()`: Verify loop/stutter actions present, ~12 steps
     - `test_transition_beat_match()`: Verify tempo_ramp action, ~20 steps
     - `test_transition_invalid_type()`: Verify ValueError for unknown type
     - `test_transition_invalid_bars()`: Verify ValueError when bars < minimum
     - `test_transition_all_end_with_complete()`: All transition types end with "complete" action

  2. **Harmonic Mixer Tests:**
     - `test_harmonic_same_key()`: compatible=True, energy_change=0
     - `test_harmonic_neighbor_up()`: Cm→Gm, compatible=True, energy_change=+1
     - `test_harmonic_neighbor_down()`: Cm→Fm, compatible=True, energy_change=-1
     - `test_harmonic_relative_minor_major()`: Cm→Eb, compatible=True
     - `test_harmonic_incompatible()`: Cm→F#m, compatible=False
     - `test_harmonic_all_24_positions()`: Verify all 24 positions have valid neighbors with correct wraparound
     - `test_suggest_next_key_up_energy()`: Verify direction="up_energy" returns correct neighbor
     - `test_suggest_next_key_down_energy()`: Verify direction="down_energy" returns correct neighbor
     - `test_suggest_next_key_relative_minor()`: Verify correct relative minor
     - `test_suggest_next_key_relative_major()`: Verify correct relative major

  3. **Cue Point Manager Tests:**
     - `test_set_cue()`: Create cue, verify returned dict has cue_id, name, time
     - `test_get_cues()`: Set multiple cues, verify returned sorted by time
     - `test_get_cues_empty()`: Get cues for track with no cues, verify empty list

  4. **Auto-Mix Tests:**
     - `test_queue_auto_mix_parsing()`: Verify valid JSON input parsed correctly
     - `test_queue_auto_mix_invalid_json()`: Verify error on invalid JSON

  5. **Knowledge File Tests:**
     - `test_camelot_wheel_completeness()`: 24 positions, all neighbors correct
     - `test_camelot_wheel_wraparound()`: 1A→8A, 1B→8B wraparound neighbors
     - `test_dj_effects_all_present()`: All 5 effects with required keys

  Each test is a standalone function with assert statements and print output (no pytest discovery).
  Tests must be runnable without Ableton Live (pure computation tests).

  Must NOT: Depend on pytest or any test framework. Must NOT: Require Ableton Live connection.
  Must cover: all transition types, all harmonic edge cases, camelot wheel completeness and wraparound.

  Parallelization: Wave 4 | Blocked by: Server integration | Blocks: None
  References:
  - Existing test pattern: `scripts/test/test_connection.py` (standalone assert + print)
  - Test dir: `scripts/test/` directory has 18 standalone test scripts
  - Test run command: `python tests/test_dj_tools.py`
  Acceptance criteria (agent-executable):
  ```bash
  python tests/test_dj_tools.py 2>&1 | tail -5
  ```
  Expected output: "ALL DJ TOOLS TESTS PASSED" or similar final line with all tests passing.
  If any test fails, the script must exit with non-zero code.

  QA scenarios: happy + failure
  - HAPPY: Run all tests, all pass → exit code 0
  - FAILURE (test detects bug): Add a bad assertion, test should fail with clear message
  - FAILURE: Missing camelot_wheel.json → test_camelot_wheel_completeness fails with FileNotFoundError
  Evidence: .omo/evidence/task-7-sprint-07-dj-performance.txt
  Commit: Y | feat(tests): add comprehensive test suite for DJ engine and tools

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: Verify all 5 new tools registered, all 7 deliverables exist, all scope boundaries respected (no new UDP, no external BPM detection, no clip content modification)
- [ ] F2. Code quality review: All .py files pass `python -c "compile(open(f).read(), f, 'exec')"` for dj_engine.py, dj_tools.py, and tests/test_dj_tools.py. No syntax errors.
- [ ] F3. Unit test suite run: Execute `python tests/test_dj_tools.py` — all tests pass exit code 0
- [ ] F4. Knowledge file integrity: Verify camelot_wheel.json has all 24 positions with correct neighbor relationships (including wraparound), verify dj_effects.json has all 5 effects with valid device/param specs
- [ ] F5. Scope fidelity: grep for Must NOT have violations (no new UDP, no external BPM detection, no audio analysis, no clip modification, no new pip deps)

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(knowledge): add Camelot Wheel and DJ effects knowledge files
- feat(remote-script): add get_clip_key and get_playback_state handlers
- feat(engine): add DJ engine with transition calculator, harmonic mixer, cue point manager
- feat(dj-tools): add execute_transition and suggest_harmonic_match tools
- feat(dj-tools): add queue_auto_mix, apply_dj_effect, and beat_jump_loop tools
- feat(server): integrate DJ tools into MCP server and refactor ultra_dj_loop.py
- feat(tests): add comprehensive test suite for DJ engine and tools

No squashing - each commit is independently testable. Tags: none.

## Success criteria
- All 5 new DJ tools registered and callable via MCP (execute_transition, queue_auto_mix, suggest_harmonic_match, apply_dj_effect, beat_jump_loop)
- Transition Calculator generates correct timelines for all 5 transition types (hard_cut, eq_sweep, filter_fade, loop_roll, beat_match)
- Harmonic Mixer correctly evaluates compatibility for all 24 Camelot positions with correct neighbor relationships (including wraparound)
- Camelot Wheel covers all 24 positions (12 keys × 2 modes) with verified neighbors
- DJ Effects knowledge file covers all 5 effects with device names and parameter automation specs
- Cue Point Manager stores and retrieves cues per track/clip pair
- queue_auto_mix generates valid playlists with appropriate transition type per pair
- apply_dj_effect loads effect recipes and automates parameters correctly
- beat_jump_loop creates loop roll effects and restores original settings
- All unit tests pass without Ableton Live connection (pure computation)
- Remote Script handlers `_get_clip_key` and `_get_playback_state` registered in command dispatch
- ultra_dj_loop.py refactored to delegate to dj_engine where applicable, CLI intact
