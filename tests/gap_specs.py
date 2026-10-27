"""Command specs for the 7 adopted gaps + 3 bug fixes.

Each spec defines the TCP contract: command name, params, expected response
shape. The contract layer checks the Remote Script source against these specs;
the e2e layer round-trips them against a running Live.

Sources: RESEARCH_FINDINGS.md (jpoindexter, Ziforge, phantom, isobar, LivePilot).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParamSpec:
    name: str
    type: type
    required: bool = True
    default: object = None
    validate: object = None  # callable(value) -> (ok: bool, reason: str)


@dataclass(frozen=True)
class CommandSpec:
    name: str
    category: str            # gap-rack, gap-pads, gap-view, gap-fades,
                             # gap-mix, gap-problems, gap-midi, bugfix
    description: str
    params: tuple = ()
    returns: dict = field(default_factory=dict)
    implemented: bool = False   # False = gap; True = handler exists (maybe buggy)
    bug: str = ""               # for bugfix entries: the known defect


# --- Shared validators (pure functions, unit-tested below) ---

def norm01(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return (False, "must be number")
    return (0.0 <= float(v) <= 1.0, "must be 0.0-1.0")

def nonneg(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return (False, "must be number")
    return (float(v) >= 0.0, "must be >= 0.0")

def track_index(v):
    ok = isinstance(v, int) and not isinstance(v, bool) and v >= 0
    return (ok, "must be int >= 0")

def macro_index(v):
    ok = isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 127
    return (ok, "must be int 0-127")

def pad_index(v):
    ok = isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 127
    return (ok, "must be int 0-127")

def device_index(v):
    ok = isinstance(v, int) and not isinstance(v, bool) and v >= 0
    return (ok, "must be int >= 0")

def view_name(v):
    allowed = ("Session", "Arranger", "Clip", "Device", "Browser",
               "Detail/Clip", "Detail/Device")
    ok = isinstance(v, str) and v in allowed
    return (ok, "must be one of: " + ", ".join(allowed))

def str_nonempty(v):
    return (isinstance(v, str) and len(v) > 0, "must be non-empty string")

def file_path(v):
    if not isinstance(v, str) or not v:
        return (False, "must be non-empty string")
    if not v.lower().endswith((".mid", ".midi")):
        return (False, "must be .mid/.midi path")
    if not v.rsplit(".", 1)[0]:
        return (False, "must have filename before extension")
    return (True, "")


# --- Specs ---

RACK_MACROS = (
    CommandSpec("get_rack_macros", "gap-rack",
        "List rack macros (index, name, value 0.0-1.0) for a track's RackDevice.",
        (ParamSpec("track_index", int, validate=track_index),),
        {"macros": [{"index": 0, "name": "Filter", "value": 0.5}]},
        implemented=True),
    CommandSpec("set_rack_macro", "gap-rack",
        "Set one rack macro by index. Value normalized 0.0-1.0 (CRITICAL RULE).",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("macro_index", int, validate=macro_index),
         ParamSpec("value", float, validate=norm01)),
        {"track_index": 0, "macro_index": 0, "value": 0.5, "name": "Filter"},
        implemented=True),
    CommandSpec("set_rack_macro_by_name", "gap-rack",
        "Set one rack macro by its mapped name (case-insensitive).",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("macro_name", str, validate=str_nonempty),
         ParamSpec("value", float, validate=norm01)),
        {"track_index": 0, "macro_name": "Filter", "value": 0.5},
        implemented=True),
)

DRUM_PADS = (
    CommandSpec("get_drum_pads", "gap-pads",
        "List drum rack pads with names and mute/solo state.",
        (ParamSpec("track_index", int, validate=track_index),),
        {"pads": [{"index": 36, "name": "Kick", "muted": False, "soloed": False}]},
        implemented=True),
    CommandSpec("set_drum_pad_mute", "gap-pads",
        "Mute/unmute one pad - per-pad builds/breaks without track mutes.",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("pad_index", int, validate=pad_index),
         ParamSpec("muted", bool)),
        {"track_index": 0, "pad_index": 36, "muted": True},
        implemented=True),
    CommandSpec("set_drum_pad_solo", "gap-pads",
        "Solo/unsolo one pad.",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("pad_index", int, validate=pad_index),
         ParamSpec("soloed", bool)),
        {"track_index": 0, "pad_index": 36, "soloed": True},
        implemented=True),
    CommandSpec("set_drum_pad_name", "gap-pads",
        "Rename one pad.",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("pad_index", int, validate=pad_index),
         ParamSpec("name", str, validate=str_nonempty)),
        {"track_index": 0, "pad_index": 36, "name": "Kick"},
        implemented=True),
)

VIEW_SELECT = (
    CommandSpec("focus_view", "gap-view",
        "Focus a main view (app.view.focus_view).",
        (ParamSpec("view_name", str, validate=view_name),),
        {"focused": "Session"}),
    CommandSpec("select_track", "gap-view",
        "Select a track (song.view.selected_track).",
        (ParamSpec("track_index", int, validate=track_index),),
        {"track_index": 0, "selected": True}),
    CommandSpec("select_scene", "gap-view",
        "Select a scene (song.view.selected_scene).",
        (ParamSpec("scene_index", int, validate=track_index),),
        {"scene_index": 0, "selected": True}),
)

CLIP_FADES = (
    CommandSpec("set_clip_fade_in", "gap-fades",
        "Set audio clip fade-in time (seconds, >= 0).",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("clip_index", int, validate=track_index),
         ParamSpec("fade_time", float, validate=nonneg)),
        {"track_index": 0, "clip_index": 0, "fade_in": 0.01}),
    CommandSpec("set_clip_fade_out", "gap-fades",
        "Set audio clip fade-out time (seconds, >= 0).",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("clip_index", int, validate=track_index),
         ParamSpec("fade_time", float, validate=nonneg)),
        {"track_index": 0, "clip_index": 0, "fade_out": 0.02}),
)

MIX_COMPARE = (
    CommandSpec("snapshot_mix_state", "gap-mix",
        "Snapshot current mix: LUFS, band balance, stereo width.",
        (),
        {"lufs": -14.0, "bands": {"low": 0.3, "mid": 0.4, "high": 0.3},
         "stereo_width": 0.6}),
    CommandSpec("compare_mix_snapshots", "gap-mix",
        "Compare two snapshots: LUFS delta + band deltas (LivePilot A-B loop).",
        (ParamSpec("before", dict), ParamSpec("after", dict)),
        {"lufs_delta": 0.5, "band_deltas": {"low": 0.02}, "louder": True}),
)

PROBLEM_DETECTION = (
    CommandSpec("detect_audio_problems", "gap-problems",
        "Analyze WAV: clipping, DC offset, stereo polarity, masking rank.",
        (ParamSpec("file_path", str, validate=str_nonempty),),
        {"problems": [{"type": "clipping", "severity": "high"}]}),
)

MIDI_FILE_IO = (
    CommandSpec("import_midi_file", "gap-midi",
        "Load .mid notes into a session clip (mido).",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("clip_index", int, validate=track_index),
         ParamSpec("file_path", str, validate=file_path)),
        {"track_index": 0, "clip_index": 0, "notes_imported": 12}),
    CommandSpec("export_midi_file", "gap-midi",
        "Write a session clip's notes to .mid (mido).",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("clip_index", int, validate=track_index),
         ParamSpec("file_path", str, validate=file_path)),
        {"file_path": "out.mid", "notes_exported": 12}),
)

BUGFIXES = (
    CommandSpec("get_device_parameters", "bugfix",
        "Must return the device AT device_index - not device[0] for all indices.",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("device_index", int, validate=device_index)),
        {"device_name": "EQ Eight", "device_index": 2, "parameters": []},
        implemented=True,
        bug="Returns device[0] name for all indices (get_notes branch catches "
            "RackDevice). Repro: track with [DrumRack, EQ, Reverb] - query "
            "index 2 must show EQ Eight."),
    CommandSpec("delete_device", "bugfix",
        "Must delete device at index, including RackDevices (Drum Rack).",
        (ParamSpec("track_index", int, validate=track_index),
         ParamSpec("device_index", int, validate=device_index)),
        {"deleted_device": "Drum Rack", "verified": True},
        implemented=True,
        bug="RackDevice.delete_device() called when track.delete_device() "
            "missing; raises 'RackDevice object has no attribute delete_device'."),
    CommandSpec("build_arrangement", "bugfix",
        "N duplicate_clip_to_arrangement calls in one command must all succeed.",
        (ParamSpec("sections", list),),
        {"sections_placed": 7},
        implemented=True,
        bug="2nd+ call per track fails: 'Changes cannot be triggered by "
            "notifications'. Fix: defer each duplicate via schedule_message "
            "(Ziforge queue pattern)."),
)

ALL_SPECS = tuple(
    RACK_MACROS + DRUM_PADS + VIEW_SELECT + CLIP_FADES
    + MIX_COMPARE + PROBLEM_DETECTION + MIDI_FILE_IO + BUGFIXES
)

GAPS = tuple(s for s in ALL_SPECS if not s.implemented)
FIXES = tuple(s for s in ALL_SPECS if s.implemented and s.category == "bugfix")
IMPLEMENTED_GAPS = tuple(s for s in ALL_SPECS if s.implemented and s.category != "bugfix")

BY_CATEGORY = {}
for _s in ALL_SPECS:
    BY_CATEGORY.setdefault(_s.category, []).append(_s)

# --- Source analysis helpers (used by contract layer; unit-tested below) ---

HANDLER_RE = re.compile(r'"([a-z_0-9]+)":\s*lambda\s+p[:\s]')


def extract_handler_names(source):
    """Extract all TCP command names from _build_handlers source."""
    return set(HANDLER_RE.findall(source))


def missing_handlers(source, specs=ALL_SPECS):
    """Spec names with no handler in the source."""
    handlers = extract_handler_names(source)
    return [s.name for s in specs if s.name not in handlers]
