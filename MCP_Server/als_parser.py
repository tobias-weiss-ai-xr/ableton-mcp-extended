"""
Ableton Live Set (.als) file parser.

Parses .als files offline using only stdlib (gzip + xml.etree.ElementTree).
Extracts track list, device chains, clips, tempo, time signature, and more.

Usage:
    from MCP_Server.als_parser import parse_als_file, detect_als_issues, suggest_als_changes

    data = parse_als_file("path/to/project.als")
    issues = detect_als_issues(data)
    suggestions = suggest_als_changes(data)
"""

import gzip
import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRACK_TAGS = frozenset({"MidiTrack", "AudioTrack", "GroupTrack"})  # ReturnTrack handled separately

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_attr(element: Optional[ET.Element], attr: str, default: Any = None) -> Any:
    """Safely get an attribute from an element."""
    if element is None:
        return default
    return element.get(attr, default)


def _find_child_text(element: Optional[ET.Element], tag: str) -> Optional[str]:
    """Find a child by tag and return its text content (not attribute)."""
    if element is None:
        return None
    child = element.find(tag)
    if child is not None:
        return child.text or None
    return None


def _find_value_attribute(parent: ET.Element, *path: str) -> Any:
    """
    Walk a chain of child tags and return the ``Value`` attribute of the last one.
    Example: _find_value_attribute(elem, "Name", "EffectiveName") -> Value attr.
    """
    current: Optional[ET.Element] = parent
    for tag in path:
        if current is None:
            return None
        current = current.find(tag)
    if current is not None:
        return current.get("Value")
    return None


# ---------------------------------------------------------------------------
# Track parsing
# ---------------------------------------------------------------------------


def _parse_track_name(track_elem: ET.Element) -> str:
    """Extract the effective name of a track."""
    name = _find_value_attribute(track_elem, "Name", "EffectiveName")
    if name:
        return name
    # fallback: try Name > EffectiveName > Value or direct text
    name_elem = track_elem.find("Name")
    if name_elem is not None:
        eff = name_elem.find("EffectiveName")
        if eff is not None:
            return eff.get("Value", "") or eff.text or ""
        # last resort — try <Name Value="..."/>
        return name_elem.get("Value", "")
    return ""


def _parse_track_type(tag: str) -> str:
    """Normalise Ableton track-tag names to readable types."""
    mapping = {
        "MidiTrack": "midi",
        "AudioTrack": "audio",
        "GroupTrack": "group",
        "ReturnTrack": "return",
    }
    return mapping.get(tag, tag)


def _parse_devices(device_chain: ET.Element) -> List[Dict[str, Any]]:
    """Extract device list from a <DeviceChain> element."""
    devices_elem = device_chain.find("Devices")
    if devices_elem is None:
        return []

    result: List[Dict[str, Any]] = []
    for dev in devices_elem:
        tag = dev.tag  # e.g. InstrumentDevice, AudioEffectDevice, MidiEffectDevice, Mixer
        device_info: Dict[str, Any] = {"type": tag, "name": "", "lom_id": None}

        # LomId
        lom = dev.find("LomId")
        if lom is not None:
            device_info["lom_id"] = int(lom.get("Value", 0)) if lom.get("Value") else None

        # UserName > EffectiveName
        uname = dev.find("UserName")
        if uname is not None:
            eff = uname.find("EffectiveName")
            if eff is not None:
                device_info["name"] = eff.get("Value", "") or eff.text or ""

        # If name still empty, try <PresetRef><FileRef><Name>...</Name></FileRef></PresetRef>
        if not device_info["name"]:
            preset = dev.find("PresetRef")
            if preset is not None:
                file_ref = preset.find("FileRef")
                if file_ref is not None:
                    ref_name = file_ref.find("Name")
                    if ref_name is not None:
                        device_info["name"] = ref_name.get("Value", "") or ref_name.text or ""

        result.append(device_info)

    return result


def _parse_clips(device_chain: ET.Element) -> List[Dict[str, Any]]:
    """Extract clip info from a <DeviceChain> element."""
    slot_list = device_chain.find("ClipSlotList")
    if slot_list is None:
        return []

    clips: List[Dict[str, Any]] = []
    for clip_slot_wrapper in slot_list.findall("ClipSlot"):
        # .als files often double-nest ClipSlot: <ClipSlot><ClipSlot>...</ClipSlot></ClipSlot>
        inner = clip_slot_wrapper.find("ClipSlot")
        if inner is None:
            inner = clip_slot_wrapper

        clip = inner.find("Clip")
        if clip is None:
            continue

        clip_info: Dict[str, Any] = {
            "name": _get_attr(clip, "Value", ""),
            "start": None,
            "duration": None,
            "loop_start": None,
            "loop_end": None,
            "has_notes": False,
            "note_count": 0,
        }

        # Try various known clip sub-structures
        # <Clip><Name><EffectiveName Value="..."/></Name> ...
        clip_info["name"] = _find_value_attribute(clip, "Name", "EffectiveName") or clip_info["name"]

        # CurrentTime / Start
        ct = clip.find("CurrentTime")
        if ct is not None:
            clip_info["start"] = float(ct.get("Value", 0))

        # Duration
        dur = clip.find("Duration")
        if dur is not None:
            clip_info["duration"] = float(dur.get("Value", 0))

        # Loop start/end (TimeSpan > Start / End)
        loop = clip.find("Loop")
        if loop is not None:
            clip_info["loop_start"] = float(loop.get("Start", 0)) if loop.get("Start") else None
            clip_info["loop_end"] = float(loop.get("End", 0)) if loop.get("End") else None
            # also try nested Looping > TimeSpan
            looping = loop.find("Looping")
            if looping is not None:
                ts = looping.find("TimeSpan")
                if ts is not None:
                    clip_info["loop_start"] = float(ts.get("Start", 0)) if ts.get("Start") else None

        # Notes — count <MidiNote> elements
        notes = clip.findall(".//MidiNote")  # MidiNote under Notes / KeyTracks / ...
        clip_info["note_count"] = len(notes)
        clip_info["has_notes"] = clip_info["note_count"] > 0

        clips.append(clip_info)

    return clips


# ---------------------------------------------------------------------------
# Tempo / Time Signature
# ---------------------------------------------------------------------------


def _find_tempo(live_set: ET.Element) -> Optional[float]:
    """
    Attempt multiple known XML paths for tempo.
    Modern Ableton versions store it inside MasterTrack > DeviceChain > Devices > Mixer.
    """
    # Path A: LiveSet > MasterTrack > DeviceChain > Devices > Mixer > Tempo > Manual
    master = live_set.find("MasterTrack")
    if master is not None:
        chain = master.find("DeviceChain")
        if chain is not None:
            devices = chain.find("Devices")
            if devices is not None:
                for mixer_candidate in devices.findall("*"):
                    if "Mixer" in mixer_candidate.tag:
                        tempo_elem = mixer_candidate.find("Tempo")
                        if tempo_elem is not None:
                            manual = tempo_elem.find("Manual")
                            if manual is not None:
                                val = manual.get("Value")
                                if val:
                                    return float(val)
                            # also try direct Value
                            val = tempo_elem.get("Value")
                            if val:
                                return float(val)

    # Path B: LiveSet > Tempo
    tempo = live_set.find("Tempo")
    if tempo is not None:
        val = tempo.get("Value") or (tempo.text or "")
        if val:
            try:
                return float(val)
            except (ValueError, TypeError):
                pass

    return None


def _find_time_signature(live_set: ET.Element) -> Optional[Dict[str, int]]:
    """
    Extract numerator/denominator from the Master mixer's TimeSignature.

    Path: LiveSet > MasterTrack > DeviceChain > Devices > Mixer > TimeSignature
    Contains: Numerator Value="4" / Denominator Value="4"
    """
    master = live_set.find("MasterTrack")
    if master is not None:
        chain = master.find("DeviceChain")
        if chain is not None:
            devices = chain.find("Devices")
            if devices is not None:
                for mixer_candidate in devices.findall("*"):
                    if "Mixer" in mixer_candidate.tag:
                        ts = mixer_candidate.find("TimeSignature")
                        if ts is not None:
                            num = ts.find("Numerator")
                            den = ts.find("Denominator")
                            n_val = int(num.get("Value", 0)) if num is not None else None
                            d_val = int(den.get("Value", 0)) if den is not None else None
                            if n_val and d_val:
                                return {"numerator": n_val, "denominator": d_val}

    return None


# ---------------------------------------------------------------------------
# Return tracks / Master track
# ---------------------------------------------------------------------------


def _parse_return_tracks(tracks_parent: ET.Element) -> List[Dict[str, Any]]:
    """Parse ReturnTrack children."""
    returns: List[Dict[str, Any]] = []
    for rt in tracks_parent.findall("ReturnTrack"):
        name = _parse_track_name(rt)
        chain = rt.find("DeviceChain")
        devices = _parse_devices(chain) if chain is not None else []
        returns.append({"name": name, "type": "return", "devices": devices})
    return returns


def _parse_master_track(live_set: ET.Element) -> Dict[str, Any]:
    """Extract master track info (name, devices)."""
    master = live_set.find("MasterTrack")
    if master is None:
        return {"name": "Master", "devices": []}

    name = _parse_track_name(master) or "Master"
    chain = master.find("DeviceChain")
    devices = _parse_devices(chain) if chain is not None else []
    return {"name": name, "devices": devices}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_als_file(path: str) -> Dict[str, Any]:
    """
    Parse an Ableton Live Set (.als) file and return a structured dict.

    The .als file is a gzipped XML document.  This function uses only stdlib
    (gzip + xml.etree.ElementTree).

    Parameters
    ----------
    path : str
        Absolute or relative path to the .als file.

    Returns
    -------
    dict
        Dictionary with keys:
            - ``ableton_version``  — (MajorVersion.MinorVersion)
            - ``tracks``           — list of parsed track dicts
            - ``return_tracks``    — list of return track dicts
            - ``master_track``     — master track dict
            - ``tempo``            — float or None
            - ``time_signature``   — dict with numerator/denominator or None
            - ``file_path``        — the input path
    """
    result: Dict[str, Any] = {
        "ableton_version": "",
        "tracks": [],
        "return_tracks": [],
        "master_track": {"name": "Master", "devices": []},
        "tempo": None,
        "time_signature": None,
        "file_path": path,
    }

    # Read and decompress
    try:
        with gzip.open(path, "rb") as f:
            raw = f.read()
    except Exception as exc:
        # Might not be gzipped (e.g. uncompressed XML test fixtures)
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except Exception as inner:
            raise ValueError(
                f"Cannot read {path}: not gzip ({exc}) and not plain text ({inner})"
            ) from inner

    # Parse XML
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        raise ValueError(f"XML parse error in {path}: {e}") from e

    # -- Ableton version --
    version = root.get("MajorVersion", "")
    minor = root.get("MinorVersion", "")
    result["ableton_version"] = f"{version}.{minor}" if minor else version

    # -- Find LiveSet --
    live_set = root.find("LiveSet")
    if live_set is None:
        # One more level of wrapping?  Some .als variants.
        live_set = root.find(".//LiveSet")
    if live_set is None:
        raise ValueError(f"No <LiveSet> element found in {path}")

    # -- Tempo & TimeSignature --
    result["tempo"] = _find_tempo(live_set)
    result["time_signature"] = _find_time_signature(live_set)

    # -- Master track --
    result["master_track"] = _parse_master_track(live_set)

    # -- Tracks --
    tracks_parent = live_set.find("Tracks")
    tracks_list: List[Dict[str, Any]] = []

    if tracks_parent is not None:
        for child in list(tracks_parent):
            if child.tag in TRACK_TAGS:
                track_info = _parse_single_track(child)
                tracks_list.append(track_info)
            # Also collect return tracks from the same <Tracks> container
            if child.tag == "ReturnTrack":
                # handled via _parse_return_tracks, but double-capture here is fine
                pass

    result["tracks"] = tracks_list

    # -- Return tracks (also check top-level alongside Tracks) --
    # Some .als files put ReturnTrack inside <Tracks>, some at <LiveSet> level
    returns = _parse_return_tracks(live_set)
    if not returns and tracks_parent is not None:
        returns = _parse_return_tracks(tracks_parent)
    result["return_tracks"] = returns

    return result


def _parse_single_track(track_elem: ET.Element) -> Dict[str, Any]:
    """Parse one <MidiTrack>, <AudioTrack>, <GroupTrack> element."""
    tag = track_elem.tag
    track_info: Dict[str, Any] = {
        "name": _parse_track_name(track_elem),
        "type": _parse_track_type(tag),
        "devices": [],
        "clips": [],
        "raw_tag": tag,
    }

    chain = track_elem.find("DeviceChain")
    if chain is not None:
        track_info["devices"] = _parse_devices(chain)
        track_info["clips"] = _parse_clips(chain)

    return track_info


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------


def _is_empty_track(track: Dict[str, Any]) -> bool:
    """A track that has no name and no devices (and no clips)."""
    return (
        not track.get("name", "").strip()
        and not track.get("devices")
        and not track.get("clips")
    )


def _is_unused_return(rt: Dict[str, Any]) -> bool:
    """A return track with a default name and no devices."""
    name = rt.get("name", "").strip().lower()
    return name in ("", "return a", "return b", "return c") and not rt.get("devices")


# ---------------------------------------------------------------------------
# Public detection / suggestion API
# ---------------------------------------------------------------------------


def detect_als_issues(data: dict) -> list:
    """
    Analyse parsed .als data and return a list of potential issues.

    Checks for:
        - Empty tracks (no name, no devices, no clips)
        - Tracks with no devices
        - Clips with no MIDI notes
        - Naming inconsistencies (empty names, duplicate names)
        - Unused return tracks
        - Missing tempo / time signature

    Parameters
    ----------
    data : dict
        Output from ``parse_als_file()``.

    Returns
    -------
    list[dict]
        Each entry: {"type": str, "severity": str, "message": str}
    """
    issues: List[Dict[str, str]] = []

    if not data.get("tracks"):
        issues.append({
            "type": "structure",
            "severity": "warning",
            "message": "No tracks found in the session.",
        })

    seen_names: Dict[str, int] = {}
    name_by_track: List[Tuple[str, int]] = []

    for idx, track in enumerate(data.get("tracks", [])):
        tname = track.get("name", "").strip()

        # -- Empty track --
        if _is_empty_track(track):
            issues.append({
                "type": "empty_track",
                "severity": "warning",
                "message": f"Track {idx} is empty (no name, no devices, no clips).",
            })
            continue

        # -- No name --
        if not tname:
            issues.append({
                "type": "naming",
                "severity": "info",
                "message": f"Track {idx} (type: {track.get('type', '?')}) has an empty name.",
            })

        # -- No devices --
        if not track.get("devices"):
            issues.append({
                "type": "no_devices",
                "severity": "info",
                "message": f"Track '{tname or idx}' has no devices loaded.",
            })

        # -- Clips with no notes --
        for clip_idx, clip in enumerate(track.get("clips", [])):
            if not clip.get("has_notes") and clip.get("duration", 0) > 0:
                cname = clip.get("name", "") or f"clip_{clip_idx}"
                issues.append({
                    "type": "empty_clip",
                    "severity": "info",
                    "message": (
                        f"Track '{tname or idx}' clip '{cname}' has no MIDI notes "
                        f"(duration: {clip.get('duration', '?')} beats)."
                    ),
                })

        # -- Track name duplication --
        if tname:
            seen_names[tname] = seen_names.get(tname, 0) + 1
            name_by_track.append((tname, idx))

    for tname, idx in name_by_track:
        if seen_names.get(tname, 0) > 1:
            issues.append({
                "type": "naming",
                "severity": "warning",
                "message": f"Track {idx} name '{tname}' is used by multiple tracks.",
            })
            # Avoid duplicate warnings for the same name
            seen_names[tname] = 0

    # -- Return tracks --
    for ridx, rt in enumerate(data.get("return_tracks", [])):
        if _is_unused_return(rt):
            issues.append({
                "type": "unused_return",
                "severity": "info",
                "message": f"Return track '{rt.get('name', f'return_{ridx}')}' appears unused (no devices).",
            })

    # -- Tempo --
    if data.get("tempo") is None:
        issues.append({
            "type": "metadata",
            "severity": "warning",
            "message": "Tempo not found in the .als file.",
        })

    # -- Time signature --
    if data.get("time_signature") is None:
        issues.append({
            "type": "metadata",
            "severity": "info",
            "message": "Time signature not found in the .als file.",
        })

    return issues


def suggest_als_changes(data: dict) -> list:
    """
    Generate improvement suggestions based on parsed .als data.

    Suggestions include:
        - Adding default devices to empty tracks
        - Naming unnamed tracks
        - Removing unused return tracks
        - Adding content to empty clips
        - Removing duplicate tracks

    Parameters
    ----------
    data : dict
        Output from ``parse_als_file()``.

    Returns
    -------
    list[dict]
        Each entry: {"type": str, "message": str}
    """
    suggestions: List[Dict[str, str]] = []

    for idx, track in enumerate(data.get("tracks", [])):
        tname = track.get("name", "").strip()

        if _is_empty_track(track):
            suggestions.append({
                "type": "cleanup",
                "message": f"Delete empty track {idx} or load an instrument into it.",
            })
            continue

        if not tname:
            suggestions.append({
                "type": "naming",
                "message": (
                    f"Rename track {idx} (type: {track.get('type', '?')}) to a "
                    f"descriptive name based on its role (e.g. 'Kick', 'Bass', 'Synth')."
                ),
            })

        if not track.get("devices") and track.get("type") in ("midi",):
            suggestions.append({
                "type": "instrument",
                "message": (
                    f"Load an instrument on MIDI track '{tname or idx}' — "
                    f"e.g. Drums (FileId_58622) for percussion, or Operator/Wavetable for synths."
                ),
            })

        for clip in track.get("clips", []):
            if not clip.get("has_notes") and clip.get("duration", 0) > 0:
                cname = clip.get("name", "") or "unnamed clip"
                suggestions.append({
                    "type": "content",
                    "message": (
                        f"Add MIDI notes to clip '{cname}' on track "
                        f"'{tname or idx}' (duration: {clip.get('duration', '?')} beats)."
                    ),
                })

    # -- Return tracks --
    for rt in data.get("return_tracks", []):
        if _is_unused_return(rt):
            suggestions.append({
                "type": "cleanup",
                "message": (
                    f"Remove unused return track '{rt.get('name', '?')}' or "
                    f"add effects (e.g. Reverb, Delay) to it."
                ),
            })

    # -- Tempo --
    if data.get("tempo") is None:
        suggestions.append({
            "type": "metadata",
            "message": "Set a tempo for the session (e.g. 120 BPM for house, 170 BPM for drum & bass).",
        })

    # -- Master check --
    master = data.get("master_track", {})
    if not master.get("devices"):
        suggestions.append({
            "type": "mastering",
            "message": (
                "Master track has no devices — consider adding a limiter to prevent clipping."
            ),
        })

    # -- General structure --
    if len(data.get("tracks", [])) == 0:
        suggestions.append({
            "type": "structure",
            "message": "Session is empty — create at least one MIDI track with an instrument to start.",
        })

    return suggestions


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m MCP_Server.als_parser <path/to/project.als>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        data = parse_als_file(path)
        print(json.dumps(data, indent=2, default=str))

        issues = detect_als_issues(data)
        if issues:
            print("\n--- Issues ---")
            for issue in issues:
                print(f"[{issue['severity']}] {issue['type']}: {issue['message']}")

        suggestions = suggest_als_changes(data)
        if suggestions:
            print("\n--- Suggestions ---")
            for s in suggestions:
                print(f"[{s['type']}] {s['message']}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
