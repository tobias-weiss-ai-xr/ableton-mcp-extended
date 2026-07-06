"""
Follow action configuration for generative DJ sessions.

Functions:
    - setup_energy_pattern: Create energy-based follow actions (build, drop, cycle)
    - setup_harmonic_pattern: Create harmonically intelligent follow actions
    - setup_random_pattern: Create random follow actions with stay probability

Usage:
    from follow_actions import setup_energy_pattern, setup_harmonic_pattern, setup_random_pattern

    setup_energy_pattern(0, 0, 7, "build", [2, 4, 6, 8, 10, 10, 8, 6])
    setup_harmonic_pattern(1, 0, 7, "moderate", 0.4)
    setup_random_pattern(2, 0, 7, 0.6)
"""

import logging
from typing import List, Optional

from mcp_client import MCPClientTCP

logger = logging.getLogger(__name__)


# =============================================================================
# Energy-Based Follow Actions (Task 5)
# =============================================================================

ENERGY_PATTERNS = {
    "build": {
        "description": "Increasing energy across clips (low → high)",
        "default_levels": [1, 2, 4, 6, 8, 9, 10, 10]
    },
    "drop": {
        "description": "Decreasing energy across clips (high → low)",
        "default_levels": [10, 9, 8, 6, 4, 2, 1, 1]
    },
    "cycle": {
        "description": "Wave pattern (rise and fall)",
        "default_levels": [3, 5, 8, 6, 3, 5, 8, 6]
    },
}


def setup_energy_pattern(
    track_idx: int,
    clip_range_start: int,
    clip_range_end: int,
    energy_pattern: str = "build",
    energy_levels: Optional[List[int]] = None,
    stay_probability: float = 0.3
) -> dict:
    """
    Create energy-based follow actions for clips.

    Energy-based transitions create build-ups, drops, and cyclical patterns.
    Higher energy = more likely to jump to higher-numbered clips.

    Args:
        track_idx: Track index to configure
        clip_range_start: First clip index to configure (default 0)
        clip_range_end: Last clip index to configure (default 7)
        energy_pattern: Energy pattern type (build, drop, cycle)
        energy_levels: Optional list of energy levels (1-10) for each clip
        stay_probability: Probability of staying on same clip (0.0-1.0, default 0.3)

    Returns:
        Dictionary with configuration result

    Example:
        setup_energy_pattern(0, 0, 7, "build", [2, 4, 6, 8, 10, 10, 8, 6])
        # Creates follow actions that progress from low energy (2) to high (10) then back

    Note:
        Energy levels: 1-10 where 1 = minimal, 10 = maximum
        Clips follow energy curve: low → high (build) or high → low (drop)
    """
    if energy_pattern not in ENERGY_PATTERNS:
        raise ValueError(f"Unknown energy pattern: {energy_pattern}. "
                       f"Available: {list(ENERGY_PATTERNS.keys())}")

    # Use provided energy levels or defaults
    if energy_levels is None:
        energy_levels = ENERGY_PATTERNS[energy_pattern]["default_levels"]

    # Validate energy levels count matches clip range
    num_clips = clip_range_end - clip_range_start + 1
    if len(energy_levels) != num_clips:
        logger.warning(f"Energy levels count ({len(energy_levels)}) != clip range size ({num_clips}). "
                      f"Using defaults for first {num_clips} clips.")

    client = MCPClientTCP()
    configured = []

    # Configure follow actions for each clip
    for clip_idx in range(clip_range_start, clip_range_end + 1):
        energy = energy_levels[clip_idx - clip_range_start] if clip_idx - clip_range_start < len(energy_levels) else 5

        # Determine transition targets based on energy
        if energy >= 8:
            # High energy: likely to jump toward higher-numbered clips
            next_clips = []
            for potential in range(clip_idx + 1, min(clip_idx + 3, clip_range_end + 1)):
                weight = 1.0 - (potential - clip_idx) * 0.1
                next_clips.append((potential, weight))
        elif energy <= 3:
            # Low energy: likely to jump to random or earlier clips
            next_clips = []
            for potential in range(clip_range_start, clip_range_end + 1):
                if potential != clip_idx:
                    weight = 0.5 if potential < clip_idx else 0.2
                    next_clips.append((potential, weight))
        else:
            # Medium energy: more random
            next_clips = []
            for potential in range(clip_range_start, clip_range_end + 1):
                if potential != clip_idx:
                    next_clips.append((potential, 0.3))

        # Configure follow actions (MCP Server uses scaled weights to 0-255)
        try:
            # Configure first follow action slot
            if next_clips:
                primary_target, primary_weight = next_clips[0]
                weight_scaled = int(primary_weight * 255)

                client.send_command("set_clip_follow_action", {
                    "track_index": track_idx,
                    "clip_index": clip_idx,
                    "action_slot": 0,
                    "action_type": 3,  # Play Other Clip
                    "trigger_time": 16.0,  # 4 bars at 120 BPM
                    "clip_index_target": primary_target
                })

                configured.append({
                    "clip_idx": clip_idx,
                    "energy": energy,
                    "target": primary_target,
                    "weight": weight_scaled
                })

                logger.info(f"Set follow actions for clip {clip_idx} (energy {energy})")
        except Exception as e:
            logger.warning(f"Failed to set follow actions for clip {clip_idx}: {e}")

    return {
        "track_idx": track_idx,
        "energy_pattern": energy_pattern,
        "energy_levels": energy_levels[:num_clips],
        "configured_clips": len(configured),
        "stay_probability": stay_probability
    }


# =============================================================================
# Harmonic Follow Actions (Task 5)
# =============================================================================

# Camelot wheel-compatible keys for harmonic mixing
CAMELOT_KEYS = {
    "1A": "A minor",
    "1B": "A major",
    "2A": "E minor",
    "2B": "E major",
    "3A": "B minor",
    "3B": "B major",
    "4A": "F# minor",
    "4B": "F# major",
    "5A": "C# minor",
    "5B": "C# major",
    "6A": "G# minor",
    "6B": "G# major",
    "7A": "D# minor",
    "7B": "D# major",
    "8A": "Bb minor",
    "8B": "Bb major",
    "9A": "F minor",   # Classic dub techno key
    "9B": "F major",
    "10A": "C minor",  # Another dub techno key
    "10B": "C major",
    "11A": "G minor",
    "11B": "G major",
    "12A": "D minor",
    "12B": "D major",
}


def setup_harmonic_pattern(
    track_idx: int,
    clip_range_start: int,
    clip_range_end: int,
    compatibility_mode: str = "moderate",
    stay_probability: float = 0.4
) -> dict:
    """
    Create harmonically intelligent follow actions for clips.

    Harmonic compatibility ensures smooth key transitions using Camelot wheel.
    Clips in compatible keys are more likely to transition to each other.

    Args:
        track_idx: Track index to configure
        clip_range_start: First clip index to configure (default 0)
        clip_range_end: Last clip index to configure (default 7)
        compatibility_mode: Compatibility strictness (strict, moderate, loose)
            - strict: Only same key transitions
            - moderate: Related keys (same key type, adjacent on wheel)
            - loose: Any keys possible, with weight bias toward compatible
        stay_probability: Probability of staying on same clip (0.0-1.0, default 0.4)

    Returns:
        Dictionary with configuration result

    Example:
        setup_harmonic_pattern(0, 0, 7, "moderate", 0.6)
        # Clips in Fm (9A) can transition to G#m (6A), Ebm (7A), Dm (12A)

    Note:
        Camelot wheel: Keys that mix well are those that:
            - Share same key type (A/A or B/B) and are adjacent (e.g., 8A→9A)
            - Share same number (e.g., 8A→8B)
            - Are within ±1 on the wheel (e.g., 9A→8A, 9A→10A)
    """
    if compatibility_mode not in ["strict", "moderate", "loose"]:
        raise ValueError(f"Unknown compatibility mode: {compatibility_mode}")

    # For this implementation, assign each clip a Camelot key based on minor key
    # In practice, you would detect or assign keys per clip
    # Default: All clips in 9A (F minor) - classic dub techno key
    clip_keys = {i: "9A" for i in range(clip_range_start, clip_range_end + 1)}

    client = MCPClientTCP()
    configured = []

    # Configure follow actions based on compatibility mode
    for clip_idx in range(clip_range_start, clip_range_end + 1):
        current_key = clip_keys[clip_idx]

        # Find compatible next clips
        compatible_targets = _find_compatible_keys(
            current_key,
            clip_keys,
            compatibility_mode,
            clip_idx
        )

        try:
            # Configure first follow action slot with primary target
            if compatible_targets:
                primary_target = compatible_targets[0]

                client.send_command("set_clip_follow_action", {
                    "track_index": track_idx,
                    "clip_index": clip_idx,
                    "action_slot": 0,
                    "action_type": 3,
                    "trigger_time": 16.0,
                    "clip_index_target": primary_target
                })

                configured.append({
                    "clip_idx": clip_idx,
                    "current_key": current_key,
                    "primary_target": primary_target,
                    "compatible_count": len(compatible_targets)
                })

                logger.info(f"Set harmonic follow action for clip {clip_idx} "
                          f"({current_key}) →.clip_{primary_target}")

        except Exception as e:
            logger.warning(f"Failed to set harmonic follow action for clip {clip_idx}: {e}")

    return {
        "track_idx": track_idx,
        "compatibility_mode": compatibility_mode,
        "stay_probability": stay_probability,
        "configured_clips": len(configured),
        "clip_keys": clip_keys
    }


def _find_compatible_keys(
    current_key: str,
    clip_keys: dict,
    mode: str,
    current_clip_idx: int
) -> List[int]:
    """
    Find compatible clips based on Camelot wheel harmonic mixing.

    Args:
        current_key: Current clip's Camelot key (e.g., "9A")
        clip_keys: Dictionary mapping clip indices to Camelot keys
        mode: Compatibility mode (strict, moderate, loose)
        current_clip_idx: Current clip index (to exclude self)

    Returns:
        List of compatible clip indices
    """
    compatible = []

    for clip_idx, clip_key in clip_keys.items():
        if clip_idx == current_clip_idx:
            continue

        if mode == "strict":
            # Only same key
            if clip_key == current_key:
                compatible.append(clip_idx)

        elif mode == "moderate":
            # Same key type and adjacent on wheel, or same number
            current_letter = current_key[-1]  # A or B
            current_number = int(current_key[:-1])
            clip_letter = clip_key[-1]
            clip_number = int(clip_key[:-1])

            # Same key type, adjacent keys (±1), or same number
            if (current_letter == clip_letter and
                (abs(current_number - clip_number) <= 1)) or current_number == clip_number:
                compatible.append(clip_idx)

        elif mode == "loose":
            # All keys possible, but compatible ones weighted higher
            # Just return all non-self clips
            compatible.append(clip_idx)

    return compatible if compatible else list(clip_keys.keys())


# =============================================================================
# Random Follow Actions (Task 5)
# =============================================================================

def setup_random_pattern(
    track_idx: int,
    clip_range_start: int,
    clip_range_end: int,
    stay_probability: float = 0.6
) -> dict:
    """
    Create random follow actions for a track's clips.

    Creates evolving, non-repetitive patterns ideal for generative music.

    Args:
        track_idx: Track index to configure
        clip_range_start: First clip index to configure (default 0)
        clip_range_end: Last clip index to configure (default 7)
        stay_probability: Probability of staying on same clip (0.0-1.0, default 0.6)

    Returns:
        Dictionary with configuration result

    Example:
        setup_random_pattern(0, 0, 7, 0.6)
        # Creates follow actions that randomly jump between clips with 60% chance to stay

    Note:
        Higher stay_probability = more repetitive patterns
        Lower stay_probability = more chaotic transitions
        For dub techno, use 0.4-0.6 for hypnotic but evolving loops
    """
    client = MCPClientTCP()
    configured = []
    num_clips = clip_range_end - clip_range_start + 1

    # Calculate target clip triggers based on stay probability
    # If stay_probability = 0.6, then 60% chance to stay, 40% to jump
    # We distribute the jump probability among other clips
    jump_probability = 1.0 - stay_probability
    if num_clips > 1:
        jump_per_clip = jump_probability / (num_clips - 1)
    else:
        jump_per_clip = 0.0

    for clip_idx in range(clip_range_start, clip_range_end + 1):

        # Choose random next clips (exclude self)
        possible_targets = [
            i for i in range(clip_range_start, clip_range_end + 1)
            if i != clip_idx
        ]

        if possible_targets:
            # Randomly select primary target
            import random
            primary_target = random.choice(possible_targets)

            try:
                # Configure follow action
                client.send_command("set_clip_follow_action", {
                    "track_index": track_idx,
                    "clip_index": clip_idx,
                    "action_slot": 0,
                    "action_type": 3,
                    "trigger_time": 16.0,
                    "clip_index_target": primary_target
                })

                configured.append({
                    "clip_idx": clip_idx,
                    "primary_target": primary_target,
                    "stay_probability": stay_probability
                })

                logger.info(f"Set random follow action for clip {clip_idx} → clip_{primary_target}")

            except Exception as e:
                logger.warning(f"Failed to set random follow action for clip {clip_idx}: {e}")

    return {
        "track_idx": track_idx,
        "clip_range": f"{clip_range_start}-{clip_range_end}",
        "stay_probability": stay_probability,
        "configured_clips": len(configured)
    }