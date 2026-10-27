"""
Ableton MCP tools wrapper for LangGraph agents.

Provides Python functions that call Ableton MCP tools via TCP/UDP protocol.
All functions are compatible with LangGraph's tool calling mechanism.
"""
import socket
import json
import threading
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import sound catalog data for client-side instrument-pattern generation
from agentic_mix.sound_sets import DRUM_PATTERNS, FX_URIS, MINOR_SCALE as _MINOR_SCALE_CATALOG


HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_PORT = 9788


@dataclass
class AbletonClient:
    """Client for communicating with Ableton Remote Script.

    Uses ONE persistent TCP connection for all commands. The remote script's
    handler loops on a single connection, and reusing it skips the ~300ms
    per-command overhead of socket setup + handler-thread spawn in Live.
    Stale/broken connections trigger one reconnect + retry.
    """
    host: str = HOST
    tcp_port: int = TCP_PORT
    udp_port: int = UDP_PORT

    def __post_init__(self):
        self._sock: Optional[socket.socket] = None
        self._lock = threading.Lock()

    def _connect(self) -> socket.socket:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(30.0)
        self._sock.connect((self.host, self.tcp_port))
        return self._sock

    def _close(self):
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def tcp_command(self, cmd: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send TCP command (for critical operations)."""
        msg = (json.dumps({"type": cmd, "params": params or {}}) + "\n").encode()
        with self._lock:
            last_err: Optional[Exception] = None
            for _attempt in (1, 2):  # retry once on stale connection
                try:
                    sock = self._sock if self._sock is not None else self._connect()
                    sock.sendall(msg)
                    # Read until a complete JSON response parses. The remote
                    # script sends exactly one JSON object per command.
                    data = b""
                    while True:
                        try:
                            chunk = sock.recv(262144)
                        except socket.timeout:
                            raise ConnectionError(f"timeout waiting for response to {cmd}")
                        if not chunk:
                            raise ConnectionError(f"connection closed during {cmd}")
                        data += chunk
                        try:
                            return json.loads(data.decode())
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue  # partial chunk - keep reading
                except (ConnectionError, OSError, json.JSONDecodeError) as e:
                    last_err = e
                    self._close()  # force fresh connection on retry
            raise last_err

    def udp_command(self, cmd: str, params: Dict[str, Any]) -> None:
        """Send UDP command (for low-latency parameter updates)."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            msg = json.dumps({"type": cmd, "params": params})
            sock.sendto(msg.encode(), (self.host, self.udp_port))
        finally:
            sock.close()


# Global client instance
_client = AbletonClient()


def beat_seconds(beats: float, bpm: int) -> float:
    """Convert beats to seconds."""
    return beats * 60.0 / bpm


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def get_session_info() -> Dict[str, Any]:
    """Get current Ableton session information."""
    return _client.tcp_command("get_session_info")


def set_tempo(tempo: int) -> Dict[str, Any]:
    """Set session tempo."""
    return _client.tcp_command("set_tempo", {"tempo": tempo})


def set_time_signature(numerator: int = 4, denominator: int = 4) -> Dict[str, Any]:
    """Set time signature."""
    return _client.tcp_command("set_time_signature", {
        "numerator": numerator,
        "denominator": denominator
    })


def set_master_volume(volume: float) -> None:
    """Set master volume (0.0-1.0)."""
    _client.udp_command("set_master_volume", {"volume": volume})


def start_playback() -> Dict[str, Any]:
    """Start session playback."""
    return _client.tcp_command("start_playback")


def stop_playback() -> Dict[str, Any]:
    """Stop session playback."""
    return _client.tcp_command("stop_playback")


# ============================================================================
# TRACK MANAGEMENT
# ============================================================================

def get_all_tracks() -> List[Dict[str, Any]]:
    """Get all track information."""
    resp = _client.tcp_command("get_all_tracks")
    return resp.get("result", resp).get("tracks", [])


def delete_all_tracks() -> Dict[str, Any]:
    """Delete all tracks from session."""
    return _client.tcp_command("delete_all_tracks")


def create_midi_track(index: int = -1) -> Dict[str, Any]:
    """Create a new MIDI track."""
    return _client.tcp_command("create_midi_track", {"index": index})


def create_audio_track(index: int = -1) -> Dict[str, Any]:
    """Create a new audio track."""
    return _client.tcp_command("create_audio_track", {"index": index})


def set_track_name(track_index: int, name: str) -> Dict[str, Any]:
    """Set track name."""
    return _client.tcp_command("set_track_name", {
        "track_index": track_index,
        "name": name
    })


def set_track_volume(track_index: int, volume: float) -> None:
    """Set track volume (0.0-1.0)."""
    _client.udp_command("set_track_volume", {
        "track_index": track_index,
        "volume": volume
    })


def set_track_pan(track_index: int, pan: float) -> None:
    """Set track pan (-1.0 to 1.0)."""
    _client.udp_command("set_track_pan", {
        "track_index": track_index,
        "pan": pan
    })


def set_track_mute(track_index: int, mute: bool) -> Dict[str, Any]:
    """Mute or unmute track."""
    return _client.tcp_command("set_track_mute", {
        "track_index": track_index,
        "mute": mute
    })


def set_track_solo(track_index: int, solo: bool) -> Dict[str, Any]:
    """Solo or unsolo track."""
    return _client.tcp_command("set_track_solo", {
        "track_index": track_index,
        "solo": solo
    })


def get_track_info(track_index: int) -> Dict[str, Any]:
    """Get detailed track information."""
    return _client.tcp_command("get_track_info", {"track_index": track_index})


# ============================================================================
# SCENE MANAGEMENT
# ============================================================================

def get_all_scenes() -> List[Dict[str, Any]]:
    """Get all scene information."""
    resp = _client.tcp_command("get_all_scenes")
    return resp.get("result", resp).get("scenes", [])


def delete_track(track_index: int) -> Dict[str, Any]:
    """Delete a track by index."""
    return _client.tcp_command("delete_track", {"track_index": track_index})


def delete_scene(scene_index: int) -> Dict[str, Any]:
    """Delete a scene by index."""
    return _client.tcp_command("delete_scene", {"scene_index": scene_index})


def create_scene(index: int = -1) -> Dict[str, Any]:
    """Create a new scene."""
    return _client.tcp_command("create_scene", {"index": index})


def set_scene_name(scene_index: int, name: str) -> Dict[str, Any]:
    """Set scene name."""
    return _client.tcp_command("set_scene_name", {
        "scene_index": scene_index,
        "name": name
    })


def trigger_scene(scene_index: int) -> Dict[str, Any]:
    """Trigger a scene (fire all clips)."""
    return _client.tcp_command("trigger_scene", {"scene_index": scene_index})


# ============================================================================
# CLIP MANAGEMENT
# ============================================================================

def create_clip(track_index: int, clip_index: int, length: float = 4.0) -> Dict[str, Any]:
    """Create a MIDI clip.

    Clip slots live on the scene grid - a slot beyond the current scene
    count raises "Clip index out of range", so append scene rows as needed.
    """
    scenes = get_all_scenes()
    for _ in range(len(scenes), clip_index + 1):
        create_scene(index=-1)
    return _client.tcp_command("create_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "length": length
    })


def add_notes_to_clip(track_index: int, clip_index: int, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Add MIDI notes to a clip."""
    return _client.tcp_command("add_notes_to_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "notes": notes
    })


def fire_clip(track_index: int, clip_index: int) -> Dict[str, Any]:
    """Fire/start playing a clip."""
    return _client.tcp_command("fire_clip", {
        "track_index": track_index,
        "clip_index": clip_index
    })


def stop_clip(track_index: int, clip_index: int) -> Dict[str, Any]:
    """Stop playing a clip."""
    return _client.tcp_command("stop_clip", {
        "track_index": track_index,
        "clip_index": clip_index
    })


# ============================================================================
# DEVICE AND EFFECT MANAGEMENT
# ============================================================================

def load_instrument_or_effect(track_index: int, uri: str) -> Dict[str, Any]:
    """Load an instrument or effect from browser. Uses retry + delay to avoid Live main thread overload."""
    for attempt in range(3):
        resp = _client.tcp_command("load_instrument_or_effect", {
            "track_index": track_index,
            "uri": uri
        })
        if isinstance(resp, dict) and resp.get("status") == "success":
            time.sleep(1.5)  # let Live finish loading before next
            return resp
        if attempt < 2:
            time.sleep(2.0)
    return resp


def get_device_parameters(track_index: int, device_index: int) -> List[Dict[str, Any]]:
    """Get all parameters for a device."""
    resp = _client.tcp_command("get_device_parameters", {
        "track_index": track_index,
        "device_index": device_index
    })
    return resp.get("parameters", [])


def set_device_parameter(track_index: int, device_index: int, parameter_index: int, value: float) -> None:
    """Set device parameter (0.0-1.0)."""
    _client.udp_command("set_device_parameter", {
        "track_index": track_index,
        "device_index": device_index,
        "parameter_index": parameter_index,
        "value": value
    })


# ============================================================================
# DRUM PATTERNS
# ============================================================================

# Drum patterns and mappings are centralized in agentic_mix.sound_sets
DRUM_NOTE = {"kick": 36, "snare": 40, "hat": 42, "clap": 39}



def create_drum_pattern(track_index: int, clip_index: int, pattern_name: str,
                        length: float = 4.0, kick_note: int = 36,
                        snare_note: int = 40, hat_note: int = 42,
                        clap_note: int = 39) -> Dict[str, Any]:
    """Create a drum pattern clip.

    ponytail: notes are generated client-side and sent via create_clip +
    add_notes_to_clip - the remote script has no create_drum_pattern command.
    """
    # allow per-call note overrides
    notes_map = dict(DRUM_NOTE, kick=kick_note, snare=snare_note, hat=hat_note, clap=clap_note)
    grid = DRUM_PATTERNS.get(pattern_name, DRUM_PATTERNS["dub_techno"])

    create_clip(track_index, clip_index, length=length)
    notes = []
    bar = 0
    while bar * 4.0 < length:
        offset = bar * 4.0
        for beat, drum, dur in grid:
            if offset + beat < length:
                notes.append({"pitch": notes_map[drum], "start_time": offset + beat,
                              "duration": dur, "velocity": 100, "mute": False})
        bar += 1
    return add_notes_to_clip(track_index, clip_index, notes)


# ============================================================================
# SEND/RETURN MANAGEMENT
# ============================================================================

def get_return_tracks() -> List[Dict[str, Any]]:
    """Get all return tracks."""
    resp = _client.tcp_command("get_return_tracks")
    return resp.get("result", resp).get("return_tracks", [])


def set_send_amount(track_index: int, send_index: int, amount: float) -> Dict[str, Any]:
    """Set send amount to a return track (0.0-1.0)."""
    return _client.tcp_command("set_send_amount", {
        "track_index": track_index,
        "send_index": send_index,
        "amount": amount
    })


# ============================================================================
# CROSSFADER
# ============================================================================

def get_crossfader_position() -> Dict[str, Any]:
    """Get master crossfader position."""
    return _client.tcp_command("get_crossfader_position")


def set_crossfader_position(value: float) -> Dict[str, Any]:
    """Set crossfader position (0.0-1.0)."""
    return _client.tcp_command("set_crossfader_position", {"value": value})


# ============================================================================
# ADVANCED MIXING TOOLS
# ============================================================================

def apply_bass_forward_mix(bass_track_index: int, other_track_indices: List[int],
                           bass_volume: float = 0.85, other_volume: float = 0.55,
                           bass_device_index: int = 0, bass_filter_param: Optional[int] = None,
                           bass_filter_value: Optional[float] = None) -> Dict[str, Any]:
    """Apply bass-forward mix balance."""
    params = {
        "bass_track_index": bass_track_index,
        "other_track_indices": other_track_indices,
        "bass_volume": bass_volume,
        "other_volume": other_volume,
        "bass_device_index": bass_device_index,
    }
    if bass_filter_param is not None:
        params["bass_filter_param"] = bass_filter_param
    if bass_filter_value is not None:
        params["bass_filter_value"] = bass_filter_value

    return _client.tcp_command("apply_bass_forward_mix", params)


def apply_dub_drop(track_indices: List[int], device_index: int = 0,
                  parameter_index: int = 2, drop_value: float = 0.2,
                  return_value: float = 0.8, drop_instant: bool = True) -> Dict[str, Any]:
    """Apply a dub-style drop with filter slam and return."""
    return _client.tcp_command("apply_dub_drop", {
        "track_indices": track_indices,
        "device_index": device_index,
        "parameter_index": parameter_index,
        "drop_value": drop_value,
        "return_value": return_value,
        "drop_instant": drop_instant
    })


def apply_crossfade(track_a_index: int, track_b_index: int,
                   target_a_volume: float = 0.0, target_b_volume: float = 1.0,
                   duration_beats: float = 16.0, steps: int = 16) -> Dict[str, Any]:
    """Gradually shift volume from track A to track B."""
    return _client.tcp_command("apply_crossfade", {
        "track_a_index": track_a_index,
        "track_b_index": track_b_index,
        "target_a_volume": target_a_volume,
        "target_b_volume": target_b_volume,
        "duration_beats": duration_beats,
        "steps": steps
    })


def apply_crossfader_sweep(from_value: float = 0.0, to_value: float = 1.0,
                           duration_beats: float = 16.0, steps: int = 16) -> Dict[str, Any]:
    """Sweep crossfader from one position to another."""
    return _client.tcp_command("apply_crossfader_sweep", {
        "from_value": from_value,
        "to_value": to_value,
        "duration_beats": duration_beats,
        "steps": steps
    })


def apply_scene_transition(target_scene_index: int, duration_beats: float = 16.0,
                          steps: int = 16, wash_device_indices: Optional[List[int]] = None,
                          wash_param_reverb: int = 8, wash_param_delay: int = 6,
                          reverb_track_indices: Optional[List[int]] = None) -> Dict[str, Any]:
    """Fire a new scene with reverb/delay wash for smooth transitions."""
    params = {
        "target_scene_index": target_scene_index,
        "duration_beats": duration_beats,
        "steps": steps,
        "wash_param_reverb": wash_param_reverb,
        "wash_param_delay": wash_param_delay,
    }
    if wash_device_indices is not None:
        params["wash_device_indices"] = wash_device_indices
    if reverb_track_indices is not None:
        params["reverb_track_indices"] = reverb_track_indices

    return _client.tcp_command("apply_scene_transition", params)


def apply_send_sweep(track_index: int, send_index: int,
                    from_amount: float = 0.0, to_amount: float = 1.0,
                    duration_beats: float = 16.0, steps: int = 16) -> Dict[str, Any]:
    """Sweep send amount over time."""
    return _client.tcp_command("apply_send_sweep", {
        "track_index": track_index,
        "send_index": send_index,
        "from_amount": from_amount,
        "to_amount": to_amount,
        "duration_beats": duration_beats,
        "steps": steps
    })


def apply_strip_and_build(track_indices: List[int], strip_clip_indices: Optional[List[int]] = None,
                         build_phases: Optional[List[Dict[str, Any]]] = None,
                         strip_volume: float = 0.3, phase_beats: float = 8.0) -> Dict[str, Any]:
    """Strip mix to minimal state then gradually rebuild layers."""
    params = {
        "track_indices": track_indices,
        "strip_volume": strip_volume,
        "phase_beats": phase_beats,
    }
    if strip_clip_indices is not None:
        params["strip_clip_indices"] = strip_clip_indices
    if build_phases is not None:
        params["build_phases"] = build_phases

    return _client.tcp_command("apply_strip_and_build", params)


def apply_filter_buildup(track_indices: List[int], device_index: int, parameter_index: int,
                        start_value: float = 0.3, end_value: float = 0.9,
                        duration_beats: float = 16.0, steps: int = 16) -> Dict[str, Any]:
    """Apply filter sweep buildup across specified tracks."""
    return _client.tcp_command("apply_filter_buildup", {
        "track_indices": track_indices,
        "device_index": device_index,
        "parameter_index": parameter_index,
        "start_value": start_value,
        "end_value": end_value,
        "duration_beats": duration_beats,
        "steps": steps
    })


def apply_volume_automation(track_indices: List[int], curve: str = "rise",
                           duration_beats: float = 32.0, steps: int = 32,
                           min_volume: float = 0.0, max_volume: float = 1.0) -> Dict[str, Any]:
    """Automate volume along an energy curve."""
    return _client.tcp_command("apply_volume_automation", {
        "track_indices": track_indices,
        "curve": curve,
        "duration_beats": duration_beats,
        "steps": steps,
        "min_volume": min_volume,
        "max_volume": max_volume
    })


def batch_fire_clips(clips: List[Dict[str, int]]) -> Dict[str, Any]:
    """Fire multiple clips simultaneously."""
    return _client.tcp_command("batch_fire_clips", {"clips": clips})


# ============================================================================
# GENERATIVE TOOLS
# ============================================================================

def create_generative_chain(track_index: int, chain_type: str = "dub_techno",
                           key: str = "Fm", include_arpeggiator: bool = False) -> Dict[str, Any]:
    """Create a complete generative MIDI effect chain."""
    return _client.tcp_command("create_generative_chain", {
        "track_index": track_index,
        "chain_type": chain_type,
        "key": key,
        "include_arpeggiator": include_arpeggiator
    })


def generate_chord_progression_clip(track_index: int, clip_index: int, key: str,
                                   progression: List[str], duration_per_chord: float = 4.0,
                                   voicing: str = "close", pattern_type: str = "sustained") -> Dict[str, Any]:
    """Generate a chord progression clip (server command: create_chord_progression)."""
    return _client.tcp_command("create_chord_progression", {
        "track_index": track_index,
        "clip_index": clip_index,
        "key": key,
        "progression": progression,
        "duration_per_chord": duration_per_chord,
    })


def generate_melody_clip(track_index: int, clip_index: int, key: str, scale: str = "minor",
                        length_beats: float = 8.0, complexity: str = "medium",
                        range_notes: List[int] = [60, 84]) -> Dict[str, Any]:
    """Generate a scale-constrained melody clip.

    ponytail: notes generated client-side (random walk on the scale) and sent
    via create_clip + add_notes_to_clip - no server-side melody command.
    """
    import random
    root = {"F": 53, "Fm": 53, "C": 60, "Cm": 60, "A": 57, "Am": 57,
            "D": 62, "Dm": 62, "G": 55, "Gm": 55, "E": 64, "Em": 64}.get(key, 60)
    intervals = _MINOR_SCALE_CATALOG if "minor" in scale or scale in ("dorian", "phrygian") else [0, 2, 4, 5, 7, 9, 11]
    step = 0
    spacing = 1.0 if complexity == "simple" else 0.5

    create_clip(track_index, clip_index, length=length_beats)
    notes = []
    beat = 0.0
    while beat < length_beats:
        if random.random() > 0.15:  # occasional rest
            degree = intervals[step % len(intervals)]
            octave = 12 * (step // len(intervals))
            pitch = min(max(root + degree + octave, range_notes[0]), range_notes[1])
            notes.append({"pitch": pitch, "start_time": beat,
                          "duration": spacing * 0.9, "velocity": 90, "mute": False})
            step += random.choice((1, 1, 2, -1))
            if step < 0:
                step = 0
        beat += spacing
    return add_notes_to_clip(track_index, clip_index, notes)
