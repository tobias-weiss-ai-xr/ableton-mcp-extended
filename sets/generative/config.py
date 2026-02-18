"""
Central configuration module for the generative dub techno system.

All constants for pattern generation, Markov transitions, UDP rate limits,
and humanization parameters are defined here.
"""

# =============================================================================
# TEMPO & TIMING
# =============================================================================

TEMPO = 126  # Dub techno standard BPM

# Prime-length pattern durations (bars) for phase relationships
PATTERN_DURATIONS = [3, 5, 7]

# Timing humanization
MICRO_TIMING_VARIATION = 0.02  # Beats, Gaussian std dev
VELOCITY_HUMANIZATION = 10  # ±10 uniform

# Ghost note probability for organic feel
GHOST_NOTE_PROBABILITY = 0.2

# =============================================================================
# TRACK STRUCTURE
# =============================================================================

TRACKS = {
    "kick": 0,
    "bass": 1,
    "hihat": 2,
    "pads": 3,
    "fx": 4,
    "delays": 5,
}

CLIPS_PER_TRACK = 8

# =============================================================================
# VARIATION & EVOLUTION
# =============================================================================

VARIATION_BALANCE = {
    "familiar": 0.7,  # 70% recognizable patterns
    "novel": 0.3,  # 30% new variations
}

FOLLOW_ACTION_STAY_PROB = 0.6  # 60% stay, 40% transition

# =============================================================================
# MARKOV TRANSITION MATRICES
# =============================================================================

# Bass: 2nd order Markov for scale degree transitions
# States: I (root), III (3rd), V (5th), VII (7th)
BASS_STATES = ["I", "III", "V", "VII"]

# Transition matrix: bass[state][next_state] = probability
# High probability to stay on root (0.4), moderate to 5th (0.3)
BASS_MARKOV = {
    "I": {"I": 0.4, "III": 0.15, "V": 0.3, "VII": 0.15},
    "III": {"I": 0.3, "III": 0.2, "V": 0.3, "VII": 0.2},
    "V": {"I": 0.25, "III": 0.2, "V": 0.35, "VII": 0.2},
    "VII": {"I": 0.3, "III": 0.25, "V": 0.25, "VII": 0.2},
}

# Pads: Chord progression transitions (minor key: i, VII, VI, V)
PAD_STATES = ["i", "VII", "VI", "V"]

# Transition matrix: pads[state][next_state] = probability
PAD_MARKOV = {
    "i": {"i": 0.2, "VII": 0.3, "VI": 0.25, "V": 0.25},
    "VII": {"i": 0.25, "VII": 0.15, "VI": 0.35, "V": 0.25},
    "VI": {"i": 0.25, "VII": 0.2, "VI": 0.15, "V": 0.4},
    "V": {"i": 0.5, "VII": 0.2, "VI": 0.2, "V": 0.1},
}

MARKOV_MATRICES = {
    "bass": {
        "states": BASS_STATES,
        "transitions": BASS_MARKOV,
    },
    "pads": {
        "states": PAD_STATES,
        "transitions": PAD_MARKOV,
    },
}

# =============================================================================
# UDP RATE LIMITS (High-frequency parameter updates)
# =============================================================================

UDP_RATE_LIMITS = {
    "filter_hz": 200,  # Filter sweeps up to 200Hz
    "volume_hz": 100,  # Volume changes up to 100Hz
}

# =============================================================================
# NETWORK PROTOCOL
# =============================================================================

TCP_PORT = 9877  # Reliable operations (get_*, delete_*, quantize, undo/redo)
UDP_PORT = 9878  # High-frequency parameter updates

# Commands that MUST use TCP (Category D operations)
TCP_ONLY_COMMANDS = frozenset(
    [
        "get_session_info",
        "get_session_overview",
        "get_track_info",
        "get_clip_notes",
        "get_device_parameters",
        "get_playhead_position",
        "get_all_tracks",
        "get_all_scenes",
        "get_all_clips_in_track",
        "get_clip_envelopes",
        "get_clip_warp_markers",
        "get_clip_follow_actions",
        "get_master_track_info",
        "get_return_tracks",
        "delete_track",
        "delete_clip",
        "delete_device",
        "delete_notes_from_clip",
        "delete_warp_marker",
        "delete_scene",
        "delete_locator",
        "quantize_clip",
        "mix_clip",
        "crop_clip",
        "undo",
        "redo",
        "start_recording",
        "stop_recording",
    ]
)

# Commands approved for UDP (9 high-frequency operations)
UDP_APPROVED_COMMANDS = frozenset(
    [
        "set_device_parameter",
        "set_track_volume",
        "set_track_pan",
        "set_track_mute",
        "set_track_solo",
        "set_track_arm",
        "set_clip_launch_mode",
        "fire_clip",
        "set_master_volume",
    ]
)

# =============================================================================
# BASELINE PARAMETER VALUES
# =============================================================================

BASELINE_VALUES = {
    "volume": {
        "kick": 0.75,
        "bass": 0.70,
        "hihat": 0.55,
        "pads": 0.60,
        "fx": 0.50,
        "delays": 0.45,
        "master": 0.80,
    },
    "pan": {
        "kick": 0.0,  # Center
        "bass": 0.0,  # Center
        "hihat": 0.2,  # Slight right
        "pads": -0.15,  # Slight left
        "fx": 0.3,  # Right
        "delays": -0.1,  # Slight left
    },
    "filter": {
        "pads_min_hz": 400,
        "pads_max_hz": 2000,
        "pads_default_hz": 800,
    },
    "sends": {
        "reverb_default": 0.3,
        "delay_default": 0.4,
    },
}

# =============================================================================
# SCALE DEFINITIONS (Minor key for dub techno)
# =============================================================================

# MIDI note numbers (C3 = 60)
SCALE_ROOT = 36  # C2 for bass

# Minor scale intervals (semitones from root)
MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]  # Natural minor

# Chord definitions (semitones from root for each chord type)
CHORD_INTERVALS = {
    "i": [0, 3, 7],  # Minor: root, minor 3rd, perfect 5th
    "VII": [0, 4, 7],  # Major: root, major 3rd, perfect 5th
    "VI": [0, 3, 7],  # Minor
    "V": [0, 4, 7],  # Major
}

# =============================================================================
# UTILITY FUNCTIONS (No external dependencies)
# =============================================================================


def get_track_index(name: str) -> int:
    """Get track index by name. Returns -1 if not found."""
    return TRACKS.get(name, -1)


def is_tcp_only(command: str) -> bool:
    """Check if command must use TCP protocol."""
    return command in TCP_ONLY_COMMANDS


def is_udp_approved(command: str) -> bool:
    """Check if command is approved for UDP protocol."""
    return command in UDP_APPROVED_COMMANDS
