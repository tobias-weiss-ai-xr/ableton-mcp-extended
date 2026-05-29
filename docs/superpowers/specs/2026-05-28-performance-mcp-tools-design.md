# Performance Automation MCP Tools

**Date:** 2026-05-28
**Status:** Design Document

## Problem

DJ performance scripts (`live_dj_performance.py`, `ultra_dj_loop.py`, `live_dj_scenes.py`,
`live_dj_bass_heavy.py`) contain reusable performance patterns that can only be invoked as standalone
Python scripts. AI assistants using the MCP server have no way to perform live transitions,
crossfades, or DJ-style parameter automation — they can only fire clips and set parameters
directly.

This means AI-driven live performance must coordinate dozens of primitive tool calls manually,
which produces glitchy, unmotivated transitions that lack musical shaping.

## Solution

Create 8 new MCP tools in `advanced_tools.py` that encapsulate DJ performance patterns into
callable, tempo-aware, parameterized primitives. Each tool uses UDP (port 9878) for real-time
parameter sweeps and TCP (port 9877) for setup/teardown state queries.

### Architecture Principle

```
AI Model → MCP tool call → advanced_tools.py → parameter validation
  → TCP for setup state queries
  → UDP loop for real-time parameter sweep (fire-and-forget)
  → Return JSON summary
```

All timing is beat-relative. All parameter values are normalized 0.0-1.0. The UDP loop runs
in-process with `time.sleep()` between steps (not async — these are synchronous sweeps that must
complete before the next operation).

### UDP Rationale

From existing benchmarks: UDP is 290-580x faster than TCP with ~0.2ms latency and 4536 Hz
throughput. A 32-step crossfade over 8 bars takes ~30ms of network time via UDP vs ~17 seconds
via TCP. TCP reliability is unnecessary here — if one parameter update drops, the next step
corrects it within 100-200ms, which is inaudible.

## Tools

### 1. `apply_crossfade`

Gradually shift volume from track A to track B over N beats.

```
Parameters:
  track_a_index: int       # Source track
  track_b_index: int       # Destination track  
  duration_beats: float    # Transition length (default 16.0 = 4 bars)
  curve: str               # "linear", "exponential", "logarithmic" (default "linear")
  steps: int               # Number of sweep steps (default 32)

Flow:
  1. TCP: get_track_info(a) → store current volumes
  2. TCP: get_track_info(b) → verify track exists
  3. For step i in range(steps):
       t = i / (steps - 1)
       curve_t = apply_curve(t, curve)  # 0.0 → 1.0
       vol_a = vol_a_original * (1 - curve_t)
       vol_b = min(vol_b_max, curve_t)  # ramp up from 0
       UDP: set_track_volume(a, vol_a)
       UDP: set_track_volume(b, vol_b)
       sleep(duration_beats / steps in seconds)
  4. Return: {status, volumes, duration_beats}

Errors:
  - Track not found → return error string
  - Same track for A and B → return error string
  - duration_beats < 1 → clamp to 1
  - steps < 4 → clamp to 4
```

### 2. `apply_gradual_clip_switch`

Fade one clip out while fading another in on the same track. Uses volume and filter cutoff.

```
Parameters:
  track_index: int         # Track to transition
  from_clip_index: int     # Clip to fade out
  to_clip_index: int       # Clip to fade in
  duration_beats: float    # Transition length (default 16.0)
  use_filter: bool         # Sweep filter during transition (default True)

Flow:
  1. TCP: verify both clips exist
  2. Set volume roof (protect against accidental full volume)
  3. If use_filter: set track volume to 1.0, sweep filter from open → closed → open
  4. Else: sweep volume from 1.0 → 0.0 (old clip), fire new clip, sweep 0.0 → 1.0 (new clip)
  5. If use_filter: open filter back
  6. Return: {status, transition_type, duration_beats}

Errors:
  - Clip not found → return error string
  - Same clip → return error string
```

### 3. `apply_scene_transition`

Crossfade between two scenes with effect wash.

```
Parameters:
  from_scene_index: int    # Current scene
  to_scene_index: int      # Target scene
  duration_beats: float    # Transition length (default 32.0 = 8 bars)
  wash_intensity: float    # 0.0-1.0, how much reverb/delay to add during wash (default 0.7)
  effect_track_index: int  # Track with reverb/delay device for wash (default 0)

Flow:
  1. TCP: get all clips in both scenes
  2. Increase reverb/delay on all tracks based on wash_intensity
  3. Wait duration_beats * 0.3 (wash phase)
  4. TCP: fire_scene(to_scene_index)
  5. Wait duration_beats * 0.4 (overlap phase — both scenes play)
  6. Gradually decrease reverb/delay to normal
  7. Return: {status, from_scene, to_scene, duration_beats}

Errors:
  - Scene not found → return error string
  - Same scene → return error string
  - wash_intensity out of range → clamp to 0.0-1.0
```

### 4. `apply_parameter_lock`

Set a parameter with gradual entry and optional random drift during sustained grooves.

```
Parameters:
  track_index: int         # Track containing the device
  device_index: int        # Device on the track  
  parameter_index: int     # Parameter to automate
  target_value: float      # 0.0-1.0, target parameter value
  entry_time_beats: float  # Time to reach target (default 4.0 = 1 bar)
  drift_amount: float      # 0.0-1.0, random drift range around target (default 0.0)
  drift_interval_beats: float  # How often to re-randomize drift (default 4.0)
  duration_beats: float    # How long to maintain the lock (default 0 = indefinite)

Flow:
  1. Clamp target_value to 0.0-1.0
  2. Get current value via TCP
  3. Sweep from current → target over entry_time_beats (UDP, ~4 steps per beat)
  4. If drift_amount > 0 and duration_beats > 0:
       Loop for duration_beats:
         new_val = target_value + random.uniform(-drift_amount, drift_amount) * 0.5
         Clamp to 0.0-1.0
         UDP: set_device_parameter(track, device, param, new_val)
         Sleep(drift_interval_beats)
  5. Return: {status, target_value, drift_amount, duration_beats}
```

### 5. `apply_volume_automation`

Automate track volume along an energy curve shape.

```
Parameters:
  track_index: int         # Track to automate
  curve_type: str          # "rise", "fall", "rise_fall", "fall_rise", "sawtooth"
  start_value: float       # 0.0-1.0 (default 0.0 for rise, 1.0 for fall)
  peak_value: float        # 0.0-1.0 (default 1.0)
  duration_beats: float    # Total duration (default 32.0)
  steps: int               # Number of sweep steps (default 32)

Flow:
  1. Generate curve points based on curve_type
  2. Map curve to volume range [start_value, peak_value]
  3. Loop: UDP volume updates at each step
  4. Hold at final value for 1 bar
  5. Return: {status, curve_type, start, end, duration_beats}
```

### 6. `apply_hypnotic_groove`

Low-intensity random parameter drift on multiple tracks for sustained grooves.

```
Parameters:
  track_device_params: List[dict]  # Each: {track_index, device_index, parameter_index, 
                                    #         center_value, drift_amount}
  duration_beats: float            # How long to groove (default 64.0 = 16 bars)
  update_interval_beats: float     # How often to update (default 4.0 = 1 bar)

Flow:
  1. Validate all parameter references
  2. For each update_interval:
       For each param in track_device_params:
         new_val = param.center_value + random.uniform(-param.drift_amount, param.drift_amount)
         Clamp to 0.0-1.0
         UDP: set_device_parameter(...)
       Sleep(update_interval_beats)
  3. Return: {status, params_count, duration_beats, updates_count}
```

### 7. `apply_effect_stab`

Quick burst of effect parameter change (build → release).

```
Parameters:
  track_index: int         # Track with effect device
  device_index: int        # Effect device (reverb, delay, filter)
  parameter_index: int     # Parameter to stab
  stab_value: float        # 0.0-1.0, peak value during stab (default 1.0)
  return_value: float      # 0.0-1.0, value to return to (default 0.3)
  attack_beats: float      # Time to reach stab (default 0.5)
  hold_beats: float        # Time at stab (default 0.5)
  release_beats: float     # Time to return (default 2.0)

Flow:
  1. UDP: Set parameter to stab_value immediately
  2. If attack_beats > 0: sweep from current → stab over attack_beats
  3. Hold for hold_beats
  4. Sweep from stab → return_value over release_beats
  5. Return: {status, stab_value, total_duration}

Errors:
  - parameter_index out of range → return error string
```

### 8. `apply_arrangement_sequence`

Queue and execute a sequence of scene transitions with energy curve.

```
Parameters:
  scene_sequence: List[int]     # Ordered list of scene indices to fire
  duration_beats_per_scene: float  # How long each scene plays (default 32.0)
  transition_type: str          # "crossfade", "hard_cut", "filter_sweep" (default "crossfade")
  energy_curve: str             # Energy progression: "build", "cycle", "random" (default "build")

Flow:
  1. Validate all scene indices exist
  2. For each scene in sequence:
       If not first:
         apply appropriate transition from previous scene
       Fire scene
       Wait duration_beats_per_scene
  3. Return: {status, scenes_played, total_duration, energy_curve}

Errors:
  - Any scene not found → return error with index
  - Empty sequence → return error string
```

## Helper Functions

All tools use shared helpers:

### `_validate_and_clamp`

```python
def _validate_and_clamp(value: float, min_v: float, max_v: float, name: str) -> float:
    """Validate and clamp normalized parameter. Logs warning if out of range."""
    if value < min_v or value > max_v:
        logger.warning(f"{name}={value} out of range [{min_v}, {max_v}], clamping")
    return max(min_v, min(max_v, value))
```

### `_beats_to_seconds`

All sweep timing is beat-relative. Each tool calls `_beats_to_seconds` at the start of its
execution to query the current session tempo and compute the conversion factor:

```python
def _beats_to_seconds(ableton, beats: float) -> float:
    """Query session tempo and convert beats to seconds."""
    info = ableton.send_command("get_session_info", {})
    tempo = info.get("tempo", 120.0)  # fallback 120 BPM
    return beats * 60.0 / tempo
```

This means the AI never needs to know or provide the BPM. Tempo is discovered automatically.

## Error Handling

All tools follow the existing `advanced_tools.py` pattern:

```python
try:
    ableton = get_ableton_connection()
    # ... logic ...
    return json.dumps({"status": "success", ...}, indent=2)
except Exception as e:
    logger.error(f"Error in tool_name: {str(e)}")
    return f"Error in tool_name: {str(e)}"
```

- All return JSON strings on success, single-line error strings on failure
- All parameter validation happens before any Ableton commands
- All UDP commands are fire-and-forget (non-blocking for network)

## Implementation Plan

### Files to Modify

- `MCP_Server/advanced_tools.py` — Add 8 new `@mcp.tool()` functions in `register_advanced_tools()`

### No Changes Needed

- No new files
- No new dependencies
- No Remote Script changes (tools use existing UDP/TCP commands)
- No test changes (existing tests exercise underlying commands)

### Order of Implementation

1. Helper function `_validate_and_clamp` (shared, used by all tools)
2. `apply_effect_stab` (simplest — single param, short duration)
3. `apply_crossfade` (core DJ primitive, two-track volume)
4. `apply_gradual_clip_switch` (crossfade + clip fire)
5. `apply_volume_automation` (single-track curve)
6. `apply_parameter_lock` (entry + drift)
7. `apply_hypnotic_groove` (multi-parameter drift)
8. `apply_scene_transition` (complex — scene fire + effect wash)
9. `apply_arrangement_sequence` (highest-level — orchestrates scene transitions)

### Testing

Each tool can be tested manually by:
1. Starting the MCP server and Ableton session
2. Calling the tool with known-good parameters
3. Verifying the expected parameter change and return JSON

Future: Create mocked unit tests with `unittest.mock.patch` for `get_ableton_connection` to verify
parameter clamping, error returns, and sweep correctness without Ableton running.
