"""
Parameter sweep automation for live DJ performances.

Functions:
    - apply_filter_sweep: Smooth filter cutoff/ resonance sweeps
    - apply_format_filter: Frequency-based filter automation
    - apply_repeat_delay: Delay time and feedback sweeps
    - apply_reverb_decay: Reverb decay time automation

Usage:
    from parameter_sweeps import apply_filter_sweep, apply_repeat_delay

    apply_filter_sweep(0, 0, 2, 0.3, 0.9, 16, 0.1)  # filter sweep over 4 bars
    apply_repeat_delay(0, 1, 2, 1, 4, 8.0, 4)        # delay buildup
"""

import logging
from typing import List, Dict, Any

from mcp_client import MCPClientTCP

logger = logging.getLogger(__name__)


# =============================================================================
# Filter Sweeps (Task 6)
# =============================================================================

def apply_filter_sweep(
    track_idx: int,
    device_idx: int = 0,
    param_cutoff: int = 2,
    param_resonance: int = 3,
    start_cutoff: float = 0.3,
    end_cutoff: float = 0.9,
    duration_beats: float = 16.0,
    steps: int = 16,
    amplitude: float = 0.1
) -> Dict[str, Any]:
    """
    Apply smooth filter cutoff sweep on a track's device.

    Classic dub techno technique: gradually open filter from closed to open
    with optional resonance sweep for dramatic build-ups.

    Args:
        track_idx: Track index containing the device
        device_idx: Device index on the track (default 0)
        param_cutoff: Parameter index for filter cutoff (default 2)
        param_resonance: Parameter index for resonance (default 3)
        start_cutoff: Starting normalized cutoff value (0.0-1.0, default 0.3 = low)
        end_cutoff: Ending normalized cutoff value (0.0-1.0, default 0.9 = bright)
        duration_beats: Sweep duration in beats (default 16 = 4 bars at 120 BPM)
        steps: Number of automation steps (default 16)
        amplitude: Optional resonance change amount (default 0.1, set to 0 to disable)

    Returns:
        Dictionary with automation results

    Example:
        apply_filter_sweep(0, 0, 2, 3, 0.2, 0.95, 32, 32, 0.15)
        # 8-bar filter buildup with slight resonance increase

    Note:
        Pattern from scripts/dub_techno_automation.py:82-117:
        - Linear interpolation between start and end cutoff
        - Optional resonance sweep synchronized with cutoff
        - Common dub techno: start 0.2-0.4, end 0.8-0.95, 16-32 beats
    """
    client = MCPClientTCP()
    automation_points = []

    # Calculate cutoff step size
    cutoff_step = (end_cutoff - start_cutoff) / steps
    time_step = duration_beats / steps

    # Generate automation points
    for i in range(steps + 1):
        current_cutoff = start_cutoff + (i * cutoff_step)
        current_time = i * time_step

        # Add cutoff automation point
        result = client.send_command("add_automation_point", {
            "track_index": track_idx,
            "clip_index": 0,
            "device_index": device_idx,
            "parameter_index": param_cutoff,
            "time": current_time,
            "value": current_cutoff
        })

        if result.get("success", True):
            automation_points.append({
                "parameter": "cutoff",
                "time": current_time,
                "value": current_cutoff
            })

        # Optional resonance sweep
        if amplitude > 0 and param_resonance is not None:
            current_resonance = amplitude * (i / steps)  # Gradual resonance increase
            client.send_command("add_automation_point", {
                "track_index": track_idx,
                "clip_index": 0,
                "device_index": device_idx,
                "parameter_index": param_resonance,
                "time": current_time,
                "value": current_resonance
            })

            automation_points.append({
                "parameter": "resonance",
                "time": current_time,
                "value": current_resonance
            })

    logger.info(f"Applied filter sweep: {start_cutoff} → {end_cutoff} "
              f"over {duration_beats} beats ({steps} steps)")

    return {
        "track_idx": track_idx,
        "device_idx": device_idx,
        "start_cutoff": start_cutoff,
        "end_cutoff": end_cutoff,
        "duration_beats": duration_beats,
        "steps": steps,
        "points_added": len(automation_points),
        "resonance_enabled": amplitude > 0
    }


def apply_format_filter(
    track_idx: int,
    device_idx: int = 0,
    param_resonance: int = 3,
    center_freq: float = 0.5,
    band_width: float = 0.3,
    duration_beats: float = 8.0,
    sweep_range: float = 0.4
) -> Dict[str, Any]:
    """
    Apply formant filter variation for vocal/dub texture.

    Moves formant frequency center to create vocal-like textures.

    Args:
        track_idx: Track index
        device_idx: Device index (default 0)
        param_resonance: Resonance parameter index
        center_freq: Starting normalized frequency center (0.0-1.0)
        band_width: Filter bandwidth (0.0-1.0)
        duration_beats: Sweep duration in beats (default 8)
        sweep_range: Frequency sweep range (±0.4 from center, default 0.4)

    Returns:
        Dictionary with automation results

    Note:
        Formant filters simulate vowel sounds (A, E, I, O, U)
        Sweep ranges: warm (0.3-0.7), bright (0.5-0.9), nasal (0.1-0.5)
    """
    client = MCPClientTCP()
    automation_points = []

    # Peak resonance at mid-point
    peak_time = duration_beats / 2

    # Formant form: rise to peak, then fall
    for i in range(33):  # 32 steps
        current_time = (i / 32) * duration_beats

        # Bell curve frequency sweep
        normalized_pos = i / 32
        freq_sweep = (center_freq + sweep_range * normalized_pos) % 1.0

        # Add automation point
        client.send_command("add_automation_point", {
            "track_index": track_idx,
            "clip_index": 0,
            "device_index": device_idx,
            "parameter_index": param_resonance,
            "time": current_time,
            "value": freq_sweep
        })

        automation_points.append({
            "time": current_time,
            "value": freq_sweep
        })

    logger.info(f"Applied formant filter sweep: center {center_freq}, "
              f"range ±{sweep_range} over {duration_beats} beats")

    return {
        "track_idx": track_idx,
        "center_freq": center_freq,
        "band_width": band_width,
        "sweep_range": sweep_range,
        "duration_beats": duration_beats,
        "points_added": len(automation_points)
    }


# =============================================================================
# Delay Automation (Task 6)
# =============================================================================

def apply_repeat_delay(
    track_idx: int,
    device_idx: int = 0,
    param_time_left: int = 1,
    param_feedback: int = 2,
    start_time: float = 1.0,
    end_time: float = 4.0,
    feedback_amount: float = 0.6,
    duration_beats: float = 8.0,
    steps: int = 8
) -> Dict[str, Any]:
    """
    Apply rising delay time automation for rhythmic buildup.

    Creates rhythmic echoes that speed up or slow down over time.

    Args:
        track_idx: Track index
        device_idx: Delay device index (default 0)
        param_time_left: Left delay time parameter index (default 1)
        param_feedback: Feedback parameter index (default 2)
        start_time: Starting delay time in beats (default 1.0 = quarter note)
        end_time: Ending delay time in beats (default 4.0 = whole note)
        feedback_amount: Feedback amount (0.0-1.0, default 0.6)
        duration_beats: Automation duration in beats (default 8)
        steps: Number of automation steps (default 8)

    Returns:
        Dictionary with automation results

    Example:
        apply_repeat_delay(0, 1, 1, 2, 1, 4, 0.7, 8, 4)
        # 2-bar delay time sweep from quarter to whole with 70% feedback

    Note:
        Delay beat divisions: 1/4 = 0.25, 1/2 = 0.5, 1 = 1.0, 2 = 2.0, 4 = 4.0
        Dub techno常用的延迟模式:
        - 1/4 → 1/2: 快速stutter
        - 1/2 → 2: 经典delay buildup
        - 1 → 4: 长echo wash
    """
    client = MCPClientTCP()
    automation_points = []

    # Time step calculation
    time_step = (end_time - start_time) / steps
    beat_step = duration_beats / steps

    # Generate delay time automation
    for i in range(steps + 1):
        current_delay_time = start_time + (i * time_step)
        current_beat = i * beat_step

        # Add delay time automation
        client.send_command("add_automation_point", {
            "track_index": track_idx,
            "clip_index": 0,
            "device_index": device_idx,
            "parameter_index": param_time_left,
            "time": current_beat,
            "value": current_delay_time
        })

        automation_points.append({
            "parameter": "delay_time",
            "time": current_beat,
            "value": current_delay_time
        })

    # Set constant feedback once
    try:
        client.send_command("set_device_parameter", {
            "track_index": track_idx,
            "device_index": device_idx,
            "parameter_index": param_feedback,
            "value": feedback_amount
        })

        logger.info(f"Set feedback to {feedback_amount}")
    except Exception as e:
        logger.warning(f"Failed to set feedback: {e}")

    logger.info(f"Applied repeat delay sweep: {start_time}s → {end_time}s "
              f"over {duration_beats} beats ({steps} steps)")

    return {
        "track_idx": track_idx,
        "device_idx": device_idx,
        "start_time_seconds": start_time,
        "end_time_seconds": end_time,
        "feedback_amount": feedback_amount,
        "duration_beats": duration_beats,
        "points_added": len(automation_points)
    }


# =============================================================================
# Reverb Automation (Task 6)
# =============================================================================

def apply_reverb_decay(
    track_idx: int,
    device_idx: int = 0,
    param_decay: int = 4,
    start_decay: float = 1.0,
    end_decay: float = 6.0,
    duration_beats: float = 16.0,
    steps: int = 16
) -> Dict[str, Any]:
    """
    Apply reverb decay time automation for atmospheric wash.

    Gradually extends reverb tails for enveloping effect.

    Args:
        track_idx: Track index
        device_idx: Reverb device index (default 0)
        param_decay: Decay time parameter index (default 4)
        start_decay: Starting decay time in seconds (default 1.0s)
        end_decay: Ending decay time in seconds (default 6.0s)
        duration_beats: Automation duration in beats (default 16 = 4 bars)
        steps: Number of automation steps (default 16)

    Returns:
        Dictionary with automation results

    Example:
        apply_reverb_decay(0, 2, 4, 1, 6, 32, 16)
        # 8-bar reverb wash from tight to ambient tails

    Note:
        Decay time ranges: tight (0.5-2.0s), medium (2.0-4.0s), long (4.0-8.0s)
        Dub techno reverb: 1.0–6.0s sweeps formaximal spaciousness
    """
    client = MCPClientTCP()
    automation_points = []

    # Calculate step sizes
    decay_step = (end_decay - start_decay) / steps
    beat_step = duration_beats / steps

    # Generate decay automation
    for i in range(steps + 1):
        current_decay = start_decay + (i * decay_step)
        current_beat = i * beat_step

        # Normalize decay time (assuming max 10s)
        normalized_decay = min(current_decay / 10.0, 1.0)

        # Add decay automation point
        client.send_command("add_automation_point", {
            "track_index": track_idx,
            "clip_index": 0,
            "device_index": device_idx,
            "parameter_index": param_decay,
            "time": current_beat,
            "value": normalized_decay
        })

        automation_points.append({
            "time": current_beat,
            "value_seconds": current_decay,
            "value_normalized": normalized_decay
        })

    logger.info(f"Applied reverb decay sweep: {start_decay}s → {end_decay}s "
              f"over {duration_beats} beats ({steps} steps)")

    return {
        "track_idx": track_idx,
        "device_idx": device_idx,
        "start_decay_seconds": start_decay,
        "end_decay_seconds": end_decay,
        "duration_beats": duration_beats,
        "points_added": len(automation_points)
    }


# =============================================================================
# Combined Sweeps (Task 6)
# =============================================================================

def apply_synchronized_sweep(
    track_indices: List[int],
    sweep_type: str = "build",
    duration_beats: float = 16.0,
    energy_level: float = 0.8
) -> Dict[str, Any]:
    """
    Apply coordinated sweeps across multiple tracks.

    Creates unified energy rise/fall across drums, bass, chords.

    Args:
        track_indices: List of track indices to automate
        sweep_type: Sweep type (build, drop, cycle)
        duration_beats: Sweep duration (default 16)
        energy_level: Maximum energy (0.0-1.0, default 0.8)

    Returns:
        Dictionary with combined sweep results

    Example:
        apply_synchronized_sweep([0, 1, 2, 3], "build", 32, 0.9)
        # 8-bar coordinated buildup across drums, bass, chord, pad tracks

    Note:
        Track order: drums (0), bass (1), chord (2), pad (3), fx (4, 5)
        Automated parameters: filter cutoff, delay, volume (track-dependent)
    """
    results = {}

    # Different sweep patterns for different tracks
    for track_idx in track_indices:
        if track_idx == 0:
            # Drums: filter sweep + hat intensity
            apply_filter_sweep(
                track_idx, device_idx=0, param_cutoff=2,
                start_cutoff=0.4 * energy_level,
                end_cutoff=0.9 * energy_level,
                duration_beats=duration_beats,
                steps=16
            )
            results[track_idx] = {"type": "drums", "filter": True}

        elif track_idx == 1:
            # Bass: filter + resonance
            apply_filter_sweep(
                track_idx, device_idx=0, param_cutoff=2, param_resonance=3,
                start_cutoff=0.2 * energy_level,
                end_cutoff=0.95 * energy_level,
                duration_beats=duration_beats,
                steps=16,
                amplitude=0.15 * energy_level
            )
            results[track_idx] = {"type": "bass", "filter": True, "resonance": True}

        elif track_idx in [2, 3]:
            # Chords/Pads: reverb decay
            apply_reverb_decay(
                track_idx, device_idx=1, param_decay=4,
                start_decay=1.0 * energy_level,
                end_decay=6.0 * energy_level,
                duration_beats=duration_beats,
                steps=16
            )
            results[track_idx] = {"type": "pad" if track_idx == 3 else "chord", "reverb": True}

        elif track_idx >= 4:
            # FX tracks: delay sweeps
            apply_repeat_delay(
                track_idx, device_idx=0, param_time_left=1, param_feedback=2,
                start_time=1.0, end_time=4.0,
                feedback_amount=0.6 * energy_level,
                duration_beats=duration_beats,
                steps=8
            )
            results[track_idx] = {"type": "fx", "delay": True}

    logger.info(f"Applied synchronized {sweep_type} sweep across {len(track_indices)} tracks")

    return {
        "sweep_type": sweep_type,
        "duration_beats": duration_beats,
        "energy_level": energy_level,
        "tracks_count": len(track_indices),
        "results": results
    }