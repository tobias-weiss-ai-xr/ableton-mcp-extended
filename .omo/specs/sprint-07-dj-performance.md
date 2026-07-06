# Sprint 07: DJ Performance Mode

**Theme:** Professional DJ tools — automatic transitions, harmonic mixing, loop effects.
**Est. days:** 5 | **New tools:** 4-5 | **Risk:** Medium
**Dependencies:** Sprint 06 (audio analysis — for harmonic mixing)

## Goal
Elevate our existing DJ scripts (`scripts/ultra_dj_loop.py`, `live_dj_performance.py`) into first-class MCP tools with beat-matched transitions, harmonic mixing, and queue-based auto-mix.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/dj_tools.py` | Create | register_dj_tools(): 4-5 performance tools |
| `MCP_Server/dj_engine.py` | Create | Core DJ logic (transition calculation, harmonic mixing) |
| `MCP_Server/server.py` | Modify | Import + register DJ tools |
| `AbletonMCP_Remote_Script/__init__.py` | Modify | Add playback control handlers (crossfader, cue, loop) |
| `scripts/ultra_dj_loop.py` | Refactor (light) | Ensure consistent with new tool API |
| `tests/test_dj_tools.py` | Create | Unit tests for transition calculation, harmonic mixing |
| `MCP_Server/knowledge/camelot_wheel.json` | Create | Camelot harmonic mixing wheel |
| `MCP_Server/knowledge/dj_effects.json` | Create | DJ effect recipes (echo out, filter sweep, etc.) |

## Deliverables

### 7.1 DJ Engine (`dj_engine.py`)

**Transition Calculator:**
```python
def calculate_transition(state_a: dict, state_b: dict, bars: int = 8) -> list[dict]:
    """
    Returns a timeline of actions to transition from track A to B:
    [{bar: 0, action: "filter_down", track: 0, value: 0.0},
     {bar: 4, action: "crossfade", value: 0.5},
     {bar: 6, action: "filter_up", track: 1, value: 1.0},
     {bar: 8, action: "complete"}]
    """
```

Transition types:
| Type | Bars | Pattern |
|------|------|---------|
| `hard_cut` | 0 | Instant swap at bar boundary |
| `eq_sweep` | 8 | Low pass A → fade volume A → high pass B → full B |
| `filter_fade` | 4 | Filter knob A down → crossfade → filter knob B up |
| `loop_roll` | 8 | Loop 1/4 on A → stutter → crossfade → drop B |
| `beat_match` | 16 | Tempo ramp A→B → EQ swap → crossfade → B full |

**Harmonic Mixer:**
- Implements Camelot Wheel (e.g., 8A → 9A = +1 energy, no key clash)
- `get_harmonic_compatibility(key_a: str, mode_a: str, key_b: str, mode_b: str) -> dict`
  - Returns: compatible (bool), energy_change (-2 to +2), relationship_text
- `suggest_next_key(current_key: str, current_mode: str, direction: str) -> dict`
  - direction: "up_energy", "down_energy", "relative_minor", "relative_major"
- Camelot mapping (12 keys × 2 modes = 24 positions)

**Cue Point Manager:**
- Stores cue points per track (name, time, color)
- `set_cue(track_index, clip_index, cue_time, cue_name) -> str`
- `get_cues(track_index, clip_index) -> list`

### 7.2 DJ Tools (`dj_tools.py`)

**Tool: `execute_transition`**
```
(ctx, from_track: int, to_track: int, from_clip: int = 0,
 to_clip: int = 0, transition_type: str = "eq_sweep",
 bars: int = 8) -> str
```
- Calculates transition timeline
- Executes each step at the correct bar position
- Uses `set_master_volume`, `set_track_volume`, `set_track_mute`, `fire_clip`
- Syncs to Live transport
- Returns: transition summary with each step

**Tool: `queue_auto_mix`**
```
(ctx, track_pairs: str) -> str
```
- `track_pairs`: JSON string: `[{"track": 0, "clip": 0}, {"track": 1, "clip": 0}, ...]`
- Schedules auto-mixes sequentially
- Each transition uses harmonic matching to choose transition type
- Returns: mix playlist with transition types per pair

**Tool: `suggest_harmonic_match`**
```
(ctx, track_index: int, clip_index: int, 
 available_tracks: str = "") -> str
```
- Analyzes current track for key (uses Sprint 06 or user-provided key)
- Scans available tracks for harmonic compatibility
- Returns ranked list: track, key, compatibility, energy_change, transition_suggestion
- If no key info, uses BPM difference as fallback

**Tool: `apply_dj_effect`**
```
(ctx, track_index: int, effect: str = "filter_sweep",
 wet_amount: float = 0.5, bars: int = 4) -> str
```
- Applies a DJ-style effect to a track
- Effects: `filter_sweep` (auto-filter), `echo_out` (increasing feedback), `beat_repeat` (stutter), `brake` (stop effect), `flanger`
- Uses existing devices + parameter automation
- Returns: effect applied confirmation

**Tool: `beat_jump_loop`**
```
(ctx, track_index: int, clip_index: int,
 loop_size: float = 1.0, bars: int = 4) -> str
```
- Creates a loop roll effect by modifying clip loop settings
- `loop_size`: 0.25, 0.5, 1.0, 2.0, 4.0 beats
- Automates loop on/off for `bars` duration
- Returns: loop effect parameters

### 7.3 Remote Script Handlers

Add handlers in `__init__.py`:
- `_get_clip_key(track_index, clip_index)` — if key is tagged on clip
- `_set_crossfader(position: float)` — smooth crossfader control (already exists via UDP)
- `_get_playback_state(track_index, clip_index)` — playing, stopped, triggered

### 7.4 Knowledge Files

**`camelot_wheel.json`**:
```json
{
  "8A": {"key": "C", "mode": "minor", "neighbors": ["8B", "9A", "7A"]},
  "8B": {"key": "Eb", "mode": "major", "neighbors": ["8A", "9B", "7B"]},
  ...
}
```

**`dj_effects.json`**:
```json
{
  "filter_sweep": {
    "device": "Auto Filter",
    "params": {"frequency": {"start": 0.0, "end": 1.0}, "resonance": 0.3}
  },
  "echo_out": {
    "device": "Beat Repeat / Delay",
    "params": {"feedback": {"start": 0.3, "end": 0.9}, "repeat_rate": "1/4"}
  }
}
```

## API Surface

### New Tools
| Tool | Signature | Returns |
|------|-----------|---------|
| `execute_transition` | (from_track, to_track, from_clip, to_clip, transition_type, bars) | Transition timeline + result |
| `queue_auto_mix` | (track_pairs) | Mix playlist JSON |
| `suggest_harmonic_match` | (track_index, clip_index, available_tracks) | Ranked matches |
| `apply_dj_effect` | (track_index, effect, wet_amount, bars) | Effect confirmation |
| `beat_jump_loop` | (track_index, clip_index, loop_size, bars) | Loop effect result |

## Acceptance Criteria
```bash
python -c "
from MCP_Server.dj_engine import get_harmonic_compatibility, suggest_next_key
result = get_harmonic_compatibility('C', 'minor', 'G', 'minor')
assert 'compatible' in result
assert 'energy_change' in result
print(f'Harmonic compatibility: {result}')
next_key = suggest_next_key('C', 'minor', 'up_energy')
assert next_key['key'] in ['G', 'C#', 'D']
print(f'Next key up: {next_key}')
"
```

```bash
python -c "
from MCP_Server.dj_engine import calculate_transition
timeline = calculate_transition(
    {'bpm': 128, 'key': 'C minor'},
    {'bpm': 130, 'key': 'G minor'},
    bars=8
)
assert len(timeline) > 0
assert timeline[-1]['action'] == 'complete'
print(f'Transition plan: {len(timeline)} steps')
"
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Transition timing drifts (beat sync issues) | High | Use Live transport + clip quantization; schedule by bar number, not ms |
| Harmonic matching without key data | Low | Fall back to BPM matching |
| DJ effects need devices that may not exist | Medium | Create temporary devices, clean up after |
| Auto-mix queued jobs crash on error | Medium | Try/except per transition; skip failed, continue queue |
| Crossfader not smooth enough via UDP | Medium | Line up multiple UDP set_crossfader calls with interpolation |

## Must NOT Do
- Do NOT rely on external BPM/key detection (ours from Sprint 06 or user-provided only)
- Do NOT attempt to analyze audio in real-time (pre-analyze at queuing time)
- Do NOT delete or modify user's existing clip content
- Do NOT add new UDP commands (use existing 10-command limit)
- Do NOT implement beat-grid detection from scratch (use transport quantization)
