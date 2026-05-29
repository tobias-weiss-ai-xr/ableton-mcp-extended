# Performance Automation MCP Tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert 4 DJ Python scripts into 8 callable MCP tools that enable AI-driven live performance automation.

**Architecture:** Add 8 `@mcp.tool()` functions to `advanced_tools.py` following existing tool patterns. Tools use UDP (`send_command_udp`) for real-time parameter sweeps (~0.2ms latency) and TCP (`send_command`) for setup/teardown operations. All timing is beat-relative with a `_beats_to_seconds` helper that queries session tempo. All parameters normalized 0.0-1.0.

**Tech Stack:** Python, MCP FastMCP, AbletonConnection (TCP port 9877 + UDP port 9878), `time.sleep()` for beat-accurate timing

---

### Task 1: Add `_beats_to_seconds` helper + `_step_parameter_udp` utility functions

**Files:**
- Modify: `MCP_Server/advanced_tools.py` (after line 11, before `register_advanced_tools`)

- [ ] **Step 1: Add helper functions at module level**

Add these two helpers between `logger = logging.getLogger(...)` and `def register_advanced_tools(...)`:

```python
import time
import socket


def _get_tempo(ableton) -> float:
    """Query Ableton tempo via TCP, return BPM. Fallback: 120."""
    try:
        result = ableton.send_command("get_tempo", {})
        if isinstance(result, dict):
            return float(result.get("tempo", 120.0))
    except Exception:
        pass
    return 120.0


def _beats_to_seconds(beats: float, bpm: float) -> float:
    """Convert beats to seconds at given BPM."""
    return (beats / (bpm / 60.0))


def _step_param(ableton, track_index: int, device_index: int,
                parameter_index: int, value: float) -> None:
    """Set one device parameter via UDP fire-and-forget."""
    ableton.send_command_udp("set_device_parameter", {
        "track_index": track_index,
        "device_index": device_index,
        "parameter_index": parameter_index,
        "value": value,
    })


def _step_volume(ableton, track_index: int, volume: float) -> None:
    """Set track volume via UDP."""
    ableton.send_command_udp("set_track_volume", {
        "track_index": track_index,
        "volume": volume,
    })
```

- [ ] **Step 2: Verify no import errors**

Run: `python -c "from MCP_Server.advanced_tools import _beats_to_seconds, _step_param, _step_volume, _get_tempo"`
Expected: no error

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add _beats_to_seconds and UDP step helpers for performance tools"
```

---

### Task 2: Implement `apply_crossfade`

**Files:**
- Modify: `MCP_Server/advanced_tools.py` (after all existing tools, before the closing of `register_advanced_tools`)

- [ ] **Step 1: Add `apply_crossfade` tool**

```python
    @mcp.tool()
    def apply_crossfade(
        ctx: Context,
        track_a_index: int,
        track_b_index: int,
        target_a_volume: float = 0.0,
        target_b_volume: float = 1.0,
        duration_beats: float = 16.0,
        steps: int = 16,
    ) -> str:
        """
        Gradually shift volume from track A to track B over N beats.

        Smoothly crossfades between two tracks by stepping volume in
        the opposite direction on each. All timing is beat-relative.

        Parameters:
        - track_a_index: Track fading OUT (volume goes down)
        - track_b_index: Track fading IN (volume goes up)
        - target_a_volume: Final volume for track A (0.0 = silent, default 0.0)
        - target_b_volume: Final volume for track B (0.0-1.0, default 1.0)
        - duration_beats: Total crossfade duration in beats (default 16 = 4 bars)
        - steps: Number of steps for smooth transition (default 16)

        Examples:
        - apply_crossfade(0, 1, 0.0, 1.0, 16.0, 16)
        """
        try:
            ableton = get_ableton_connection()
            bpm = _get_tempo(ableton)
            delay = _beats_to_seconds(duration_beats / steps, bpm)

            for i in range(steps + 1):
                t = i / steps
                vol_a = 1.0 - (1.0 - target_a_volume) * t
                vol_b = target_b_volume * t
                _step_volume(ableton, track_a_index, vol_a)
                _step_volume(ableton, track_b_index, vol_b)
                if i < steps:
                    time.sleep(delay)

            return json.dumps({
                "status": "success",
                "action": "crossfade",
                "from_track": track_a_index,
                "to_track": track_b_index,
                "duration_beats": duration_beats,
                "steps": steps,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in crossfade: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify LSP clean**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_crossfade tool"
```

---

### Task 3: Implement `apply_gradual_clip_switch`

**Files:**
- Modify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Add `apply_gradual_clip_switch` tool**

```python
    @mcp.tool()
    def apply_gradual_clip_switch(
        ctx: Context,
        track_index: int,
        source_clip_index: int,
        target_clip_index: int,
        duration_beats: float = 16.0,
        steps: int = 16,
        param_device_index: int = 0,
        param_filter_index: int = 2,
    ) -> str:
        """
        Fade out source clip while fading in target clip on the same track.

        Uses a filter sweep (parameter-based) for the fade, then fires the
        target clip and restores parameters. Creates smooth transitions
        without volume automation.

        Parameters:
        - track_index: Track containing both clips
        - source_clip_index: Clip to fade OUT
        - target_clip_index: Clip to fade IN
        - duration_beats: Transition duration in beats (default 16)
        - steps: Number of steps for smooth transition (default 16)
        - param_device_index: Device index for filter parameter (default 0)
        - param_filter_index: Parameter index for filter cutoff (default 2)

        Examples:
        - apply_gradual_clip_switch(5, 0, 1, 16.0, 16)
        """
        try:
            ableton = get_ableton_connection()
            bpm = _get_tempo(ableton)
            delay = _beats_to_seconds(duration_beats / steps, bpm)

            # Phase 1: Sweep filter down (muffle source clip)
            for i in range(steps // 2):
                t = i / (steps // 2)
                val = 0.8 - 0.6 * t  # 0.8 → 0.2
                _step_param(ableton, track_index, param_device_index, param_filter_index, val)
                time.sleep(delay)

            # Fire target clip
            ableton.send_command_udp("fire_clip", {
                "track_index": track_index,
                "clip_index": target_clip_index,
            })
            time.sleep(delay * 2)

            # Phase 2: Sweep filter up (reveal target clip)
            for i in range(steps // 2):
                t = (i + 1) / (steps // 2)
                val = 0.2 + 0.6 * t  # 0.2 → 0.8
                _step_param(ableton, track_index, param_device_index, param_filter_index, val)
                time.sleep(delay)

            return json.dumps({
                "status": "success",
                "action": "gradual_clip_switch",
                "track": track_index,
                "from_clip": source_clip_index,
                "to_clip": target_clip_index,
                "duration_beats": duration_beats,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in gradual clip switch: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify parse OK**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_gradual_clip_switch tool"
```

---

### Task 4: Implement `apply_scene_transition`

**Files:**
- Modify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Add `apply_scene_transition` tool**

```python
    @mcp.tool()
    def apply_scene_transition(
        ctx: Context,
        target_scene_index: int,
        duration_beats: float = 16.0,
        steps: int = 16,
        wash_device_indices: list = None,
        wash_param_reverb: int = 8,
        wash_param_delay: int = 6,
        reverb_track_indices: list = None,
    ) -> str:
        """
        Fire a new scene with a reverb/delay wash for smooth transitions.

        Increases reverb/delay on specified tracks, fires the new scene,
        then restores effects. Creates the "wash out → new scene emerges"
        effect common in dub/live performances.

        Parameters:
        - target_scene_index: Scene to fire
        - duration_beats: Transition duration in beats (default 16)
        - steps: Number of steps (default 16)
        - wash_device_indices: List of device indices to wash (default [0])
        - wash_param_reverb: Parameter index for reverb (default 8)
        - wash_param_delay: Parameter index for delay (default 6)
        - reverb_track_indices: Tracks to wash (default [0,4,5,6])

        Examples:
        - apply_scene_transition(1, 16.0, 16)
        """
        try:
            ableton = get_ableton_connection()
            bpm = _get_tempo(ableton)
            delay = _beats_to_seconds(duration_beats / steps, bpm)
            wash_devices = wash_device_indices or [0]
            wash_tracks = reverb_track_indices or [0, 4, 5, 6]

            # Phase 1: Increase reverb/delay (wash out)
            for i in range(steps // 2):
                t = i / (steps // 2)
                wash_val = 0.3 + 0.5 * t  # 0.3 → 0.8
                for tr in wash_tracks:
                    for dev in wash_devices:
                        _step_param(ableton, tr, dev, wash_param_reverb, wash_val)
                        _step_param(ableton, tr, dev, wash_param_delay, wash_val)
                time.sleep(delay)

            # Fire new scene
            ableton.send_command("fire_scene", {"scene_index": target_scene_index})
            time.sleep(delay * 2)

            # Phase 2: Restore effects (reveal new scene)
            for i in range(steps // 2):
                t = (i + 1) / (steps // 2)
                restore_val = 0.8 - 0.5 * t  # 0.8 → 0.3
                for tr in wash_tracks:
                    for dev in wash_devices:
                        _step_param(ableton, tr, dev, wash_param_reverb, restore_val)
                        _step_param(ableton, tr, dev, wash_param_delay, restore_val)
                time.sleep(delay)

            return json.dumps({
                "status": "success",
                "action": "scene_transition",
                "target_scene": target_scene_index,
                "duration_beats": duration_beats,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in scene transition: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify parse OK**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_scene_transition tool"
```

---

### Task 5: Implement `apply_parameter_lock`

**Files:**
- Modify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Add `apply_parameter_lock` tool**

```python
    @mcp.tool()
    def apply_parameter_lock(
        ctx: Context,
        track_index: int,
        device_index: int,
        parameter_index: int,
        target_value: float,
        duration_beats: float = 8.0,
        steps: int = 8,
        drift_amount: float = 0.0,
    ) -> str:
        """
        Sweep a parameter to a target value and optionally add random drift.

        Core building block for performance automation. Can be used for
        filter locks, effect stabs, and parameter modulations.

        Parameters:
        - track_index: Track containing the device
        - device_index: Device on the track
        - parameter_index: Parameter to automate
        - target_value: Target normalized value (0.0-1.0)
        - duration_beats: Sweep duration in beats (default 8)
        - steps: Number of sweep steps (default 8)
        - drift_amount: Random drift amplitude (0.0-0.2, default 0.0 = no drift)

        Examples:
        - apply_parameter_lock(0, 0, 2, 0.2, 8.0, 8)       # Lock filter closed
        - apply_parameter_lock(0, 0, 2, 0.8, 8.0, 8, 0.05)  # Drift near open
        """
        try:
            ableton = get_ableton_connection()
            bpm = _get_tempo(ableton)
            delay = _beats_to_seconds(duration_beats / steps, bpm)

            # Get current parameter value as starting point
            current_val = 0.5  # reasonable default
            try:
                params = ableton.send_command("get_device_parameters", {
                    "track_index": track_index,
                    "device_index": device_index,
                })
                if isinstance(params, dict) and "parameters" in params:
                    p_list = params["parameters"]
                    if parameter_index < len(p_list):
                        current_val = p_list[parameter_index].get("value", 0.5)
            except Exception:
                pass

            # Sweep from current to target
            for i in range(steps + 1):
                t = i / steps
                val = current_val + (target_value - current_val) * t
                if drift_amount > 0:
                    import random
                    val += random.uniform(-drift_amount, drift_amount)
                val = max(0.0, min(1.0, val))
                _step_param(ableton, track_index, device_index, parameter_index, val)
                if i < steps:
                    time.sleep(delay)

            return json.dumps({
                "status": "success",
                "action": "parameter_lock",
                "track": track_index,
                "device": device_index,
                "parameter": parameter_index,
                "target_value": target_value,
                "drift": drift_amount,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in parameter lock: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify parse OK**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_parameter_lock tool"
```

---

### Task 6: Implement `apply_volume_automation`

**Files:**
- Modify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Add `apply_volume_automation` tool**

```python
    @mcp.tool()
    def apply_volume_automation(
        ctx: Context,
        track_indices: list,
        curve: str = "rise",
        duration_beats: float = 32.0,
        steps: int = 32,
        min_volume: float = 0.0,
        max_volume: float = 1.0,
    ) -> str:
        """
        Automate volume along an energy curve for one or more tracks.

        Creates build-ups (rise), break-downs (fall), or pumping (sawtooth)
        volume patterns over the specified duration.

        Parameters:
        - track_indices: List of track indices to automate
        - curve: Energy curve shape - "rise", "fall", "sawtooth"
        - duration_beats: Total duration in beats (default 32 = 8 bars)
        - steps: Number of steps (default 32)
        - min_volume: Minimum volume (0.0-1.0, default 0.0)
        - max_volume: Maximum volume (0.0-1.0, default 1.0)

        Examples:
        - apply_volume_automation([4, 5], "rise", 32.0, 32)     # Build-up
        - apply_volume_automation([0], "sawtooth", 4.0, 8, 0.3, 0.9)  # Pumping
        """
        try:
            ableton = get_ableton_connection()
            bpm = _get_tempo(ableton)
            delay = _beats_to_seconds(duration_beats / steps, bpm)

            range_vol = max_volume - min_volume

            for i in range(steps + 1):
                t = i / steps
                if curve == "rise":
                    factor = t
                elif curve == "fall":
                    factor = 1.0 - t
                elif curve == "sawtooth":
                    # Triangle: up half, down half
                    factor = 2.0 * t if t < 0.5 else 2.0 * (1.0 - t)
                else:
                    factor = t

                vol = min_volume + range_vol * factor
                for tr in track_indices:
                    _step_volume(ableton, tr, vol)
                if i < steps:
                    time.sleep(delay)

            return json.dumps({
                "status": "success",
                "action": "volume_automation",
                "curve": curve,
                "tracks": track_indices,
                "duration_beats": duration_beats,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in volume automation: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify parse OK**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_volume_automation tool"
```

---

### Task 7: Implement `apply_hypnotic_groove`

**Files:**
- Modify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Add `apply_hypnotic_groove` tool**

```python
    @mcp.tool()
    def apply_hypnotic_groove(
        ctx: Context,
        track_index: int,
        device_index: int,
        parameter_indices: list = None,
        duration_beats: float = 64.0,
        steps: int = 64,
        drift_amount: float = 0.05,
    ) -> str:
        """
        Apply sustained random drift to multiple parameters for hypnotic grooves.

        Ideal for long sustained sections (8+ bars) where small parameter
        variations keep the groove alive without jarring changes.

        Parameters:
        - track_index: Track containing the device
        - device_index: Device to modulate
        - parameter_indices: List of parameter indices to drift (default [2])
        - duration_beats: Total duration in beats (default 64 = 16 bars)
        - steps: Number of steps (default 64)
        - drift_amount: Random drift per step (0.0-0.2, default 0.05)

        Examples:
        - apply_hypnotic_groove(0, 0, [2, 3], 64.0, 64, 0.03)
        """
        try:
            ableton = get_ableton_connection()
            bpm = _get_tempo(ableton)
            delay = _beats_to_seconds(duration_beats / steps, bpm)
            params = parameter_indices or [2]

            import random
            current_values = {}
            for p in params:
                try:
                    result = ableton.send_command("get_device_parameters", {
                        "track_index": track_index,
                        "device_index": device_index,
                    })
                    if isinstance(result, dict) and "parameters" in result:
                        p_list = result["parameters"]
                        if p < len(p_list):
                            current_values[p] = p_list[p].get("value", 0.5)
                        else:
                            current_values[p] = 0.5
                    else:
                        current_values[p] = 0.5
                except Exception:
                    current_values[p] = 0.5

            for _ in range(steps):
                for p in params:
                    val = current_values[p] + random.uniform(-drift_amount, drift_amount)
                    val = max(0.0, min(1.0, val))
                    current_values[p] = val
                    _step_param(ableton, track_index, device_index, p, val)
                time.sleep(delay)

            return json.dumps({
                "status": "success",
                "action": "hypnotic_groove",
                "track": track_index,
                "device": device_index,
                "parameters": params,
                "duration_beats": duration_beats,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in hypnotic groove: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify parse OK**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_hypnotic_groove tool"
```

---

### Task 8: Implement `apply_effect_stab`

**Files:**
- Modify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Add `apply_effect_stab` tool**

```python
    @mcp.tool()
    def apply_effect_stab(
        ctx: Context,
        track_index: int,
        device_index: int,
        param_reverb: int = 8,
        param_delay: int = 6,
        attack_beats: float = 2.0,
        hold_beats: float = 4.0,
        release_beats: float = 4.0,
        peak_value: float = 0.8,
        steps: int = 8,
    ) -> str:
        """
        Quick effect burst with attack/hold/release shape.

        Creates a reverb/delay burst effect - useful for transitions,
        accent hits, and dub techno stabs.

        Parameters:
        - track_index: Track containing the device
        - device_index: Device with reverb/delay parameters
        - param_reverb: Reverb parameter index (default 8)
        - param_delay: Delay parameter index (default 6)
        - attack_beats: Rise time in beats (default 2)
        - hold_beats: Hold at peak in beats (default 4)
        - release_beats: Fall time in beats (default 4)
        - peak_value: Maximum effect value (0.0-1.0, default 0.8)
        - steps: Steps per phase (default 8)

        Examples:
        - apply_effect_stab(0, 0, 8, 6, 2.0, 4.0, 4.0, 0.8)
        """
        try:
            ableton = get_ableton_connection()
            bpm = _get_tempo(ableton)

            def phase(dur_beats, from_val, to_val, phase_steps):
                if phase_steps <= 0 or dur_beats <= 0:
                    return
                d = _beats_to_seconds(dur_beats / phase_steps, bpm)
                for i in range(phase_steps):
                    t = (i + 1) / phase_steps
                    val = from_val + (to_val - from_val) * t
                    _step_param(ableton, track_index, device_index, param_reverb, val)
                    _step_param(ableton, track_index, device_index, param_delay, val)
                    time.sleep(d)

            # Attack: build up
            phase(attack_beats, 0.2, peak_value, steps)
            # Hold
            if hold_beats > 0:
                time.sleep(_beats_to_seconds(hold_beats, bpm))
            # Release
            phase(release_beats, peak_value, 0.2, steps)

            return json.dumps({
                "status": "success",
                "action": "effect_stab",
                "track": track_index,
                "device": device_index,
                "peak_value": peak_value,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in effect stab: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify parse OK**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_effect_stab tool"
```

---

### Task 9: Implement `apply_arrangement_sequence`

**Files:**
- Modify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Add `apply_arrangement_sequence` tool**

```python
    @mcp.tool()
    def apply_arrangement_sequence(
        ctx: Context,
        scene_transitions: list = None,
        energy_curve: list = None,
        transition_beats: float = 16.0,
    ) -> str:
        """
        Queue scene transitions that follow an energy curve.

        Fires scenes in sequence with wash transitions between them,
        following a specified energy/intensity progression.

        Parameters:
        - scene_transitions: List of scene indices to fire in order
                             Default: [0,1,2,3,4,5,6,7]
        - energy_curve: Optional energy level per scene (1-10)
                        Higher energy = faster transitions, more wash
        - transition_beats: Beats between scene transitions (default 16)

        Examples:
        - apply_arrangement_sequence()  # Default 8-scene sequence
        - apply_arrangement_sequence([0, 2, 4, 7], [1, 4, 7, 10], 32.0)
        """
        try:
            ableton = get_ableton_connection()
            scenes = scene_transitions or list(range(8))
            energy = energy_curve or [3, 7, 5, 9, 4, 8, 6, 10]

            # Pad energy curve if shorter than scenes
            while len(energy) < len(scenes):
                energy.append(energy[-1] if energy else 5)

            results = []
            for i, scene_idx in enumerate(scenes):
                # Calculate wash intensity from energy
                e = energy[i] if i < len(energy) else 5
                wash_dur = transition_beats * (e / 10.0)

                # Wash out
                if i > 0 and wash_dur > 2:
                    for dev in [0]:
                        _step_param(ableton, 5, dev, 8, min(0.7, 0.3 + e * 0.04))
                        _step_param(ableton, 5, dev, 6, min(0.6, 0.2 + e * 0.04))
                    time.sleep(_beats_to_seconds(2, _get_tempo(ableton)))

                # Fire scene
                ableton.send_command("fire_scene", {"scene_index": scene_idx})
                results.append({"scene": scene_idx, "energy": e})

                # Wait for transition
                time.sleep(_beats_to_seconds(transition_beats, _get_tempo(ableton)))

            return json.dumps({
                "status": "success",
                "action": "arrangement_sequence",
                "transitions": results,
                "total_scenes": len(scenes),
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in arrangement sequence: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify parse OK**

Run: `python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"`
Expected: Parse OK

- [ ] **Step 3: Commit**

```bash
git add MCP_Server/advanced_tools.py
git commit -m "feat: add apply_arrangement_sequence tool"
```

---

### Task 10: Final verification

**Files:**
- Verify: `MCP_Server/advanced_tools.py`

- [ ] **Step 1: Parse check and LSP diagnostics**

```bash
python -c "import ast; ast.parse(open('MCP_Server/advanced_tools.py').read()); print('Parse OK')"
lsp_diagnostics("MCP_Server/advanced_tools.py")
```

Expected: Parse OK, zero errors/warnings

- [ ] **Step 2: Verify module import works**

Run: `python -c "from MCP_Server.advanced_tools import _beats_to_seconds, _get_tempo; print('Import OK')"`
Expected: Import OK (may show socket connection error but import itself should work)

- [ ] **Step 3: Verify no duplicate tool names**

Search for `@mcp.tool()` and `def apply_` — ensure each tool name appears exactly once.

- [ ] **Step 4: Check advanced_tools.py is registered in server.py**

Search server.py for `register_advanced_tools` — it should be called at startup.
