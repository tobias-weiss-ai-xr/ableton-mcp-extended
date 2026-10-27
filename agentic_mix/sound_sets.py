"""
Reusable sound sets for the AgentFlow mix orchestration.

Single source of truth for:
  - Browser URIs for instruments and effects in Ableton Live 12
  - Genre track templates (role -> track name)
  - Genre instrument/effect chains (role -> instrument + FX list to load)
  - Drum beat patterns and chord progressions (with variation tiers)

The URIs here are the ones verified working in the 8-lane live session and the
90-minute dub scripts (browser FileIds / AudioFx categories). Loading reorders
by the browser-search query, not display name.
"""

from typing import Dict, List, Tuple

# ============================================================================
# INSTRUMENT URIs (browser queries, verified working)
# ============================================================================
INSTRUMENT_URIS: Dict[str, str] = {
    "drums":   "query:Drums#FileId_58622",               # 32 Pad Kit Jazz
    "bass":    "query:Sounds#Bass:FileId_49654",         # 101 Essential Bass
    "pads":    "query:Sounds#Pad:FileId_45564",          # 5ths Glass Motion Pad
    "strings": "query:Sounds#Pad:FileId_45565",          # Analog Slow Sweep
    "lead":    "query:Sounds#Synth%20Lead:FileId_50175", # A Date With Analog
}

# ============================================================================
# EFFECT URIs (AudioFx categories; added to a track after its instrument)
# ============================================================================
FX_URIS: Dict[str, str] = {
    "reverb":         "query:AudioFx#Reverb",
    "delay":          "query:AudioFx#Delay",
    "echo":           "query:AudioFx#Echo",
    "filter_delay":   "query:AudioFx#Filter%20Delay",
    "eq8":            "query:AudioFx#EQ%20Eight",
    "compressor":     "query:AudioFx#Compressor",
    "auto_filter":    "query:AudioFx#Auto%20Filter",
    "drum_buss":      "query:AudioFx#Drum%20Buss",
    "saturator":      "query:AudioFx#Saturator",
    "utility":        "query:AudioFx#Utility",
}

# ============================================================================
# GENRE TRACK TEMPLATES (role -> track name), one entry per created track.
# Order matters: it drives both naming and the instrument chain lookup.
# ============================================================================
TRACK_TEMPLATES: Dict[str, List[str]] = {
    "dub_techno": ["Drums 1", "Drums 2", "Bass", "Chords", "Pads", "FX",
                   "Atmosphere", "Percussion"],
    "house":      ["Drums", "Bass", "Chords", "Pads", "Vocals", "FX",
                   "Atmosphere", "Percussion"],
    "techno":     ["Drums", "Bass", "Synth 1", "Synth 2", "Atmosphere", "FX",
                   "Pads", "Percussion"],
    "ambient":    ["Pads", "Bass", "Atmosphere", "FX", "Percussion", "Texture",
                   "Drone", "Reverbed"],
}

DEFAULT_GENRE = "dub_techno"


def track_names_for(genre: str, track_count: int) -> List[str]:
    """Return the track names to create, in order, for a genre."""
    names = TRACK_TEMPLATES.get(genre, TRACK_TEMPLATES[DEFAULT_GENRE])
    return names[:track_count] if len(names) >= track_count else names


def track_name_by_index(genre: str, idx: int, total_tracks: int = 8) -> str:
    """Get a track name at a given index for a genre with a maximum."""
    return track_names_for(genre, total_tracks)[idx] if idx < len(track_names_for(genre, total_tracks)) else f"Track {idx + 1}"


# ============================================================================
# GENRE INSTRUMENT/FFECT CHAINS
# role -> (instrument_uri | None, [fx_uris])
# Each role maps to a reusable combination that gets loaded per track.
# ============================================================================
INSTRUMENT_CHAIN: Dict[str, Tuple[str, List[str]]] = {
    "drums":   (INSTRUMENT_URIS["drums"],   ["drum_buss", "eq8"]),
    "bass":    (INSTRUMENT_URIS["bass"],    ["eq8", "auto_filter", "compressor"]),
    "sub":     (INSTRUMENT_URIS["bass"],    ["auto_filter", "saturator", "utility"]),
    "chords":  (INSTRUMENT_URIS["pads"],    ["delay", "auto_filter", "reverb"]),
    "pads":    (INSTRUMENT_URIS["strings"], ["reverb", "delay", "eq8"]),
    "lead":    (INSTRUMENT_URIS["lead"],    ["delay", "auto_filter", "reverb"]),
    "fx":      (INSTRUMENT_URIS["drums"],   ["delay", "auto_filter", "reverb"]),
    "perc":    (INSTRUMENT_URIS["drums"],   ["drum_buss", "reverb", "delay"]),
}

# Map each track NAME (in any genre) to its INSTRUMENT_CHAIN role. Names with
# trailing digits (Drums 1, Synth 1) normalize by stripping the number.
_NAME_ROLE: Dict[str, str] = {
    "drums":   "drums",
    "bass":    "bass",
    "chords":  "chords",
    "pads":    "pads",
    "synth":   "lead",
    "lead":    "lead",
    "fx":      "fx",
    "atmosphere": "pads",
    "percussion": "perc",
    "vocals":  "lead",
    "texture": "pads",
    "drone":   "pads",
    "reverbed": "pads",
}


def chain_for_track(track_name: str) -> Tuple[str, List[str]]:
    """Return (instrument_uri, [fx_keys]) for a track name (unknown -> pads)."""
    base = _strip_number(track_name).lower()
    role = _NAME_ROLE.get(base, "pads")
    return INSTRUMENT_CHAIN[role]


def _strip_number(name: str) -> str:
    while name and name[-1].isdigit():
        name = name[:-1]
    return name.strip()


# ============================================================================
# DRUM BEAT PATTERNS
# Grids are (beat_offset_within_bar, drum, duration) per 4-beat bar; the
# pattern is repeated to fill a clip. Also used for live one-shot triggering.
# ============================================================================
DRUM_PATTERNS: Dict[str, List[Tuple[float, str, float]]] = {
    # --- dub family (sparse, offbeat emphasis) ---
    "one_drop":    [(0.0, "kick", 0.5), (2.5, "snare", 0.25), (1.0, "hat", 0.1), (3.0, "hat", 0.1)],
    "dub_techno":  [(0.0, "kick", 0.5), (2.5, "snare", 0.25), (0.5, "hat", 0.1), (3.5, "hat", 0.1)],
    "rockers":     [(0.0, "kick", 0.5), (0.5, "kick", 0.5), (2.0, "kick", 0.5), (2.5, "kick", 0.5),
                    (0.5, "hat", 0.1), (1.5, "hat", 0.1), (2.5, "hat", 0.1), (3.5, "hat", 0.1)],
    "steppers":    [(0.0, "kick", 0.5), (1.0, "kick", 0.5), (2.0, "kick", 0.5), (3.0, "kick", 0.5),
                    (0.5, "hat", 0.1), (1.5, "hat", 0.1), (2.5, "hat", 0.1), (3.5, "hat", 0.1)],
    # --- four-on-the-floor family ---
    "house_basic": [(0.0, "kick", 0.5), (1.0, "kick", 0.5), (2.0, "kick", 0.5), (3.0, "kick", 0.5),
                    (1.0, "clap", 0.25), (3.0, "clap", 0.25)],
    "techno_4x4":  [(0.0, "kick", 0.5), (1.0, "kick", 0.5), (2.0, "kick", 0.5), (3.0, "kick", 0.5),
                    (0.5, "hat", 0.1), (1.5, "hat", 0.1), (2.5, "hat", 0.1), (3.5, "hat", 0.1)],
    "house_swing": [(0.0, "kick", 0.5), (1.0, "kick", 0.5), (2.0, "kick", 0.5), (3.0, "kick", 0.5),
                    (1.0, "clap", 0.25), (3.0, "clap", 0.25),
                    (0.25, "hat", 0.1), (1.25, "hat", 0.1), (2.25, "hat", 0.1), (3.25, "hat", 0.1)],
    # --- minimal / breakbeat ---
    "minimal":     [(0.0, "kick", 0.5), (1.0, "kick", 0.5), (2.0, "kick", 0.5), (3.0, "kick", 0.5),
                    (1.0, "hat", 0.1), (3.0, "hat", 0.1)],
    "half_time":   [(0.0, "kick", 0.5), (2.0, "kick", 0.5), (2.5, "snare", 0.25)],
}

# Genre -> ordered pool of patterns to cycle through for variation.
GENRE_PATTERNS: Dict[str, List[str]] = {
    "dub_techno": ["one_drop", "dub_techno", "rockers", "steppers"],
    "house":      ["house_basic", "house_swing", "one_drop"],
    "techno":     ["techno_4x4", "minimal", "half_time"],
    "ambient":    ["one_drop", "half_time"],
}

# ============================================================================
# CHORD PROGRESSIONS (Roman numerals, reused across genres)
# ============================================================================
PROGRESSIONS: List[List[str]] = [
    ["i", "vii", "VI", "vii"],   # Classic dub
    ["i", "VII", "VI", "VII"],   # Minor progression
    ["i", "iv", "VII", "i"],     # Modal
    ["i", "VI", "VII", "v"],     # Tension
    ["i", "v", "VI", "VII"],     # Movement
    ["I", "V", "vi", "IV"],      # Major (house/pop)
]

# ============================================================================
# MINOR SCALE (for client-side melody generation)
# ============================================================================
MINOR_SCALE: List[int] = [0, 2, 3, 5, 7, 8, 10]
