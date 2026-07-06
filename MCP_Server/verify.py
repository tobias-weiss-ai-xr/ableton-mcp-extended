"""
Verify loop for Ableton MCP.

Wraps AbletonConnection.send_command() to capture pre/post snapshots
for all state-modifying commands and return a diff.

This is a zero-tool-body-change approach: the wrapper is applied once
in get_ableton_connection() and all 211 tools benefit automatically.
"""

import json
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Snapshot strategy per command type
# ---------------------------------------------------------------------------
# Maps each modifying command to one or more (get_*, param_extractor) tuples.
# param_extractor receives the tool's params dict and returns params for the
# get_* call, or None to call with no params.

SnapshotStrategy = list[tuple[str, Optional[Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]]]]

VERIFY_STRATEGY: Dict[str, SnapshotStrategy] = {
    # Track operations → session info (track count) + track info
    "create_midi_track":   [("get_session_info", None)],
    "create_audio_track":  [("get_session_info", None)],
    "delete_all_tracks":   [("get_session_info", None)],
    "delete_track":        [("get_session_info", None)],

    # Track property changes → track info
    "set_track_name":      [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_track_color":     [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_track_fold":      [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "duplicate_track":     [("get_session_info", None)],

    # Mixer changes → track info
    "set_track_volume":    [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_track_pan":       [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_track_mute":      [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_track_solo":      [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_track_arm":       [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_send_amount":     [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_track_monitoring_state": [("get_track_info", lambda p: {"track_index": p.get("track_index", 0)})],

    # Clip operations → session info + clip track info
    "create_clip":         [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "delete_clip":         [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "duplicate_clip":      [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "move_clip":           [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "add_notes_to_clip":   [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "delete_notes_from_clip": [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "quantize_clip":       [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "transpose_clip":      [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_clip_name":       [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_clip_loop":       [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "set_clip_launch_mode":[("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "fire_clip":           [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "stop_clip":           [("get_all_clips_in_track", lambda p: {"track_index": p.get("track_index", 0)})],
    "get_clip_notes":      [],  # read-only, no verify needed but in modifying list

    # Scene operations → session info
    "create_scene":        [("get_session_info", None)],
    "delete_scene":        [("get_session_info", None)],
    "duplicate_scene":     [("get_session_info", None)],
    "set_scene_name":      [("get_session_info", None)],

    # Transport → session info
    "set_tempo":           [("get_session_info", None)],
    "set_time_signature":  [("get_session_info", None)],
    "set_metronome":       [("get_session_info", None)],
    "start_playback":      [("get_session_info", None)],
    "stop_playback":       [("get_session_info", None)],
    "start_recording":     [("get_session_info", None)],
    "stop_recording":      [("get_session_info", None)],
    "set_playhead_position": [("get_session_info", None)],
    "undo":                [("get_session_info", None)],
    "redo":                [("get_session_info", None)],

    # Device operations → device parameters
    "load_instrument_or_effect": [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": 0,
    })],
    "load_instrument_preset": [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": 0,
    })],
    "set_device_parameter": [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": p.get("device_index", 0),
    })],
    "add_automation_point": [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": p.get("device_index", 0),
    })],
    "clear_automation":    [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": p.get("device_index", 0),
    })],
    "duplicate_device":    [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": 0,
    })],
    "delete_device":       [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": 0,
    })],
    "move_device":         [("get_device_parameters", lambda p: {
        "track_index": p.get("track_index", 0),
        "device_index": 0,
    })],

    # Locator operations → session info
    "create_locator":      [("get_session_info", None)],
    "delete_locator":      [("get_session_info", None)],
    "jump_to_locator":     [("get_session_info", None)],
    "set_loop":            [("get_session_info", None)],

    # getters in the modifying list — no verify needed
    "get_device_parameters": [],
    "get_playhead_position": [],
}

# Derive the modifying-commands set from strategy keys
MODIFYING_COMMANDS: set[str] = set(VERIFY_STRATEGY.keys())

# The original is_modifying_command list in server.py also includes these.
# We keep the authoritative list in server.py and derive our own copy here
# for the verify wrapper.  If they drift the wrapper silently skips
# unknown commands (treats them as read-only), which is safe.


def capture_snapshot(ableton, command_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Capture relevant session state before/after a modifying command."""
    strategy = VERIFY_STRATEGY.get(command_type, [("get_session_info", None)])
    snapshot: Dict[str, Any] = {}
    for check_cmd, param_extractor in strategy:
        if not check_cmd:
            continue
        try:
            check_params = param_extractor(params) if param_extractor else None
            result = ableton.send_command(check_cmd, check_params or {})
            snapshot[check_cmd] = result
        except Exception as e:
            logger.debug("Verify snapshot error for %s: %s", check_cmd, e)
            snapshot[check_cmd] = {"error": str(e)}
    return snapshot


def compute_diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a shallow structural diff between two snapshots.

    Returns only keys where values differ, with before/after for each.
    Deeply nested dicts are compared at top level by repr equality.
    """
    diff: Dict[str, Any] = {}
    all_keys = set(before.keys()) | set(after.keys())
    for key in sorted(all_keys):
        b = before.get(key)
        a = after.get(key)
        if b != a:
            diff[key] = {"before": b, "after": a}
    return diff


def _make_verify_wrapper(connection):
    """Create a wrapped version of send_command with verify loop.

    Binds to the specific ``connection`` instance via closure.
    """
    import functools

    original_send_command = connection.send_command

    @functools.wraps(original_send_command)
    def verified_send_command(command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if params is None:
            params = {}

        is_modifying = command_type in MODIFYING_COMMANDS

        # Pre-call snapshot for modifying commands
        before: Dict[str, Any] = {}
        if is_modifying:
            before = capture_snapshot(connection, command_type, params)

        # Execute the original command
        result = original_send_command(command_type, params)

        # Post-call snapshot and diff for modifying commands
        if is_modifying:
            after = capture_snapshot(connection, command_type, params)
            diff = compute_diff(before, after)
            verify_info = {
                "verified": True,
                "has_diff": bool(diff),
                "diff": diff if diff else {},
                "command": command_type,
            }
            if diff:
                logger.info(
                    "Verify OK for %s: %d state changes detected",
                    command_type, len(diff),
                )
            else:
                logger.warning(
                    "Verify NOOP for %s: no state change detected — "
                    "command may have had no effect or snapshot is incomplete",
                    command_type,
                )

            # Attach verify info to result (modifying commands only)
            if isinstance(result, dict):
                result["_verify"] = verify_info

        return result

    return verified_send_command


def wrap_ableton_connection(connection):
    """Wrap an AbletonConnection with verify loop.

    Call this once in get_ableton_connection() after the connection is established.
    The wrapper intercepts send_command for modifying commands, captures
    pre/post snapshots, computes diffs, and attaches ``_verify`` to the result.
    """
    if not getattr(connection, "_verify_wrapped", False):
        connection.send_command = _make_verify_wrapper(connection)
        connection._verify_wrapped = True
        logger.info("Verify loop installed on AbletonConnection")
    return connection
