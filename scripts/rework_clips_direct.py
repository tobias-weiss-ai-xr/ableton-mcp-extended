# DOCUMENT: Always load drum kit manually before reworking clips
# OR use load_browser_item directly
 if drum_kit_uri:
        params = {
            "track_index": 2,
            "uri": kit_uri,
        })
    else:
        # Fallback: load Drum Rack first, then load kit into the kit
        raise Exception(f"No URI provided and effect_type '{effect_type}' not mapped")

    # Add drum notes directly
    try:
        drum_notes = generate_drum_pattern(scene_index)
        if not drum_notes:
            continue
        
        notes_data = [{"pitch": n[0], "start_time": n[1], "duration": n[2], "velocity": n[3], "mute": False} for n in drum_notes]
        add_notes_to_clip(sock, track_index, clip_index, drum_notes)

    except Exception as e:
        print(f"  Error: {e}
        return None
    
    time.sleep(0.03)
}
#!/usr/bin/env python
"""
Direct clip reworking script - bypasses MCP server connection issues.
Connects directly to Ableton Remote Script via TCP.
"""

import socket
import json
import time

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 10.0


def send_command(sock, command_type, params=None):
    """Send a command to Ableton and return the response."""
    command = {"type": command_type, "params": params or {}}
    sock.sendall(json.dumps(command).encode("utf-8"))

    # Receive response
    chunks = []
    sock.settimeout(TIMEOUT)
    while True:
        try:
            chunk = sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            # Try to parse as JSON to check if complete
            try:
                data = b"".join(chunks)
                json.loads(data)
                break
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            break

    data = b"".join(chunks)
    response = json.loads(data.decode("utf-8"))

    if response.get("status") == "error":
        raise Exception(response.get("message", "Unknown error"))

    return response.get("result", {})


def get_session_info(sock):
    """Get session information."""
    return send_command(sock, "get_session_info")


def get_all_tracks(sock):
    """Get all tracks."""
    return send_command(sock, "get_all_tracks")


def get_all_clips(sock, track_index):
    """Get all clips in a track."""
    return send_command(sock, "get_all_clips_in_track", {"track_index": track_index})


def get_clip_notes(sock, track_index, clip_index):
    """Get notes from a clip."""
    return send_command(
        sock,
        "get_clip_notes",
        {
            "track_index": track_index,
            "clip_index": clip_index,
            "from_time": 0,
            "from_pitch": 0,
            "time_span": 999999,
            "pitch_span": 128,
        },
    )


def delete_clip(sock, track_index, clip_index):
    """Delete a clip."""
    return send_command(
        sock, "delete_clip", {"track_index": track_index, "clip_index": clip_index}
    )


def create_clip(sock, track_index, clip_index, length=4.0):
    """Create a new clip."""
    return send_command(
        sock,
        "create_clip",
        {"track_index": track_index, "clip_index": clip_index, "length": length},
    )


def add_notes_to_clip(sock, track_index, clip_index, notes):
    """Add notes to a clip."""
    return send_command(
        sock,
        "add_notes_to_clip",
        {"track_index": track_index, "clip_index": clip_index, "notes": notes},
    )


def set_clip_name(sock, track_index, clip_index, name):
    """Set clip name."""
    return send_command(
        sock,
        "set_clip_name",
        {"track_index": track_index, "clip_index": clip_index, "name": name},
    )


def create_drum_pattern(sock, track_index, clip_index, pattern_name, length=4.0):
    """Create a drum pattern."""
    return send_command(
        sock,
        "create_drum_pattern",
        {
            "track_index": track_index,
            "clip_index": clip_index,
            "pattern_name": pattern_name,
            "length": length,
        },
    )


def create_chord_progression(
    sock, track_index, clip_index, key, progression, duration_per_chord=4.0
):
    """Create a chord progression."""
    return send_command(
        sock,
        "create_chord_progression",
        {
            "track_index": track_index,
            "clip_index": clip_index,
            "key": key,
            "progression": progression,
            "duration_per_chord": duration_per_chord,
        },
    )


def create_chord_notes(
    sock,
    track_index,
    clip_index,
    root,
    chord_type,
    start_time=0,
    duration=4.0,
    velocity=100,
):
    """Create chord notes."""
    return send_command(
        sock,
        "create_chord_notes",
        {
            "track_index": track_index,
            "clip_index": clip_index,
            "root": root,
            "chord_type": chord_type,
            "start_time": start_time,
            "duration": duration,
            "velocity": velocity,
        },
    )


# Pattern definitions for different track types
DRUM_PATTERNS = {
    "intro": "techno_4x4",
    "build": "techno_4x4",
    "drop": "techno_4x4",
    "breakdown": "dub_techno",
    "outro": "dub_techno",
}

# Chord progressions for each scene (in A minor - 8A on Camelot wheel)
CHORD_PROGRESSIONS = {
    0: ["Am", "F", "C", "G"],  # Intro - i-VI-III-VII
    1: ["Am", "F", "C", "G"],  # Build 1
    2: ["Am", "Em", "F", "G"],  # Build 2
    3: ["Am", "F", "G", "Am"],  # Drop 1
    4: ["Am", "F", "C", "G"],  # Drop 2
    5: ["Dm", "Am", "Em", "Am"],  # Breakdown
    6: ["Am", "F", "C", "G"],  # Build 3
    7: ["Am", "Em", "F", "G"],  # Drop 3
    8: ["Am", "F", "C", "G"],  # Journey 1
    9: ["Am", "Em", "F", "C"],  # Journey 2
    10: ["Am", "F", "G", "Am"],  # Peak 1
    11: ["Am", "F", "C", "G"],  # Peak 2
    12: ["Dm", "Am", "F", "C"],  # Transition
    13: ["Am", "F", "C", "G"],  # Final push
    14: ["Am", "Em", "F", "G"],  # Wind down 1
    15: ["Am", "F"],  # Outro
}


# Bass patterns (root notes with rhythm)
def generate_bass_pattern(root_note, scene_index, length=4.0):
    """Generate a bass pattern for the given scene."""
    patterns = {
        # Scene 0-3: Building energy - simpler patterns
        0: [(root_note, 0.0, 1.0, 100), (root_note, 2.0, 1.0, 100)],
        1: [
            (root_note, 0.0, 0.5, 100),
            (root_note, 1.0, 0.5, 100),
            (root_note, 2.0, 0.5, 100),
            (root_note, 3.0, 0.5, 100),
        ],
        2: [
            (root_note, 0.0, 0.25, 100),
            (root_note, 0.5, 0.25, 100),
            (root_note, 1.0, 0.5, 100),
            (root_note, 2.0, 0.5, 100),
            (root_note, 3.0, 0.5, 100),
        ],
        3: [
            (root_note, 0.0, 0.5, 110),
            (root_note, 1.0, 0.5, 110),
            (root_note, 2.0, 0.5, 110),
            (root_note, 3.0, 0.5, 110),
        ],
        # Scene 4-7: Full energy - driving patterns
        4: [
            (root_note, 0.0, 0.25, 110),
            (root_note, 0.5, 0.25, 110),
            (root_note, 1.0, 0.25, 110),
            (root_note, 1.5, 0.25, 110),
            (root_note, 2.0, 0.25, 110),
            (root_note, 2.5, 0.25, 110),
            (root_note, 3.0, 0.25, 110),
            (root_note, 3.5, 0.25, 110),
        ],
        5: [
            (root_note, 0.0, 2.0, 90),
            (root_note, 2.0, 2.0, 90),
        ],  # Breakdown - sustained
        6: [
            (root_note, 0.0, 0.5, 100),
            (root_note, 1.0, 0.5, 100),
            (root_note, 2.0, 0.5, 100),
            (root_note, 3.0, 0.5, 100),
        ],
        7: [
            (root_note, 0.0, 0.25, 110),
            (root_note, 0.5, 0.25, 110),
            (root_note, 1.0, 0.25, 110),
            (root_note, 1.5, 0.25, 110),
            (root_note, 2.0, 0.25, 110),
            (root_note, 2.5, 0.25, 110),
            (root_note, 3.0, 0.25, 110),
            (root_note, 3.5, 0.25, 110),
        ],
        # Scene 8-11: Journey section
        8: [
            (root_note, 0.0, 0.5, 100),
            (root_note, 1.5, 0.25, 100),
            (root_note, 2.0, 0.5, 100),
            (root_note, 3.5, 0.25, 100),
        ],
        9: [
            (root_note, 0.0, 0.25, 100),
            (root_note, 0.5, 0.25, 100),
            (root_note, 1.0, 0.5, 100),
            (root_note, 2.0, 0.5, 100),
            (root_note, 3.0, 0.5, 100),
        ],
        10: [
            (root_note, 0.0, 0.25, 110),
            (root_note, 0.5, 0.25, 110),
            (root_note, 1.0, 0.25, 110),
            (root_note, 1.5, 0.25, 110),
            (root_note, 2.0, 0.25, 110),
            (root_note, 2.5, 0.25, 110),
            (root_note, 3.0, 0.25, 110),
            (root_note, 3.5, 0.25, 110),
        ],
        11: [
            (root_note, 0.0, 0.25, 110),
            (root_note, 0.5, 0.25, 110),
            (root_note, 1.0, 0.25, 110),
            (root_note, 1.5, 0.25, 110),
            (root_note, 2.0, 0.25, 110),
            (root_note, 2.5, 0.25, 110),
            (root_note, 3.0, 0.25, 110),
            (root_note, 3.5, 0.25, 110),
        ],
        # Scene 12-15: Final section
        12: [
            (root_note, 0.0, 0.5, 100),
            (root_note, 1.0, 0.5, 100),
            (root_note, 2.0, 0.5, 100),
            (root_note, 3.0, 0.5, 100),
        ],
        13: [
            (root_note, 0.0, 0.25, 110),
            (root_note, 0.5, 0.25, 110),
            (root_note, 1.0, 0.25, 110),
            (root_note, 1.5, 0.25, 110),
            (root_note, 2.0, 0.25, 110),
            (root_note, 2.5, 0.25, 110),
            (root_note, 3.0, 0.25, 110),
            (root_note, 3.5, 0.25, 110),
        ],
        14: [(root_note, 0.0, 1.0, 100), (root_note, 2.0, 1.0, 100)],  # Wind down
        15: [(root_note, 0.0, 2.0, 90), (root_note, 2.0, 2.0, 80)],  # Outro - fading
    }
    return patterns.get(scene_index, patterns[0])


# Lead patterns (melodic phrases)
def generate_lead_pattern(scene_index, key_root=69):  # A4 = 69
    """Generate a lead pattern for the given scene."""
    # Scale degrees in A minor (relative to A4)
    scale = [0, 2, 3, 5, 7, 8, 10]  # A minor scale intervals

    patterns = {
        0: [
            (key_root + 7, 0.0, 0.5, 80),
            (key_root + 5, 1.0, 0.5, 80),
            (key_root + 3, 2.0, 0.5, 80),
            (key_root + 5, 3.0, 0.5, 80),
        ],
        1: [
            (key_root + 3, 0.0, 0.25, 85),
            (key_root + 5, 0.5, 0.25, 85),
            (key_root + 7, 1.0, 0.5, 85),
            (key_root + 5, 2.0, 0.5, 85),
            (key_root + 3, 3.0, 0.5, 85),
        ],
        2: [
            (key_root + 7, 0.0, 0.25, 90),
            (key_root + 8, 0.5, 0.25, 90),
            (key_root + 10, 1.0, 0.25, 90),
            (key_root + 7, 1.5, 0.25, 90),
            (key_root + 5, 2.0, 0.5, 90),
            (key_root + 3, 3.0, 0.5, 90),
        ],
        3: [
            (key_root + 12, 0.0, 0.25, 95),
            (key_root + 10, 0.5, 0.25, 95),
            (key_root + 7, 1.0, 0.25, 95),
            (key_root + 5, 1.5, 0.25, 95),
            (key_root + 3, 2.0, 0.25, 95),
            (key_root + 5, 2.5, 0.25, 95),
            (key_root + 7, 3.0, 0.5, 95),
        ],
        4: [
            (key_root + 7, 0.0, 0.25, 100),
            (key_root + 5, 0.25, 0.25, 100),
            (key_root + 3, 0.5, 0.25, 100),
            (key_root + 5, 0.75, 0.25, 100),
            (key_root + 7, 1.0, 0.5, 100),
            (key_root + 10, 2.0, 0.5, 100),
            (key_root + 7, 3.0, 0.5, 100),
        ],
        5: [],  # Breakdown - no lead
        6: [
            (key_root + 3, 0.0, 0.5, 85),
            (key_root + 5, 1.0, 0.5, 85),
            (key_root + 7, 2.0, 0.5, 85),
            (key_root + 5, 3.0, 0.5, 85),
        ],
        7: [
            (key_root + 12, 0.0, 0.25, 100),
            (key_root + 10, 0.5, 0.25, 100),
            (key_root + 7, 1.0, 0.25, 100),
            (key_root + 5, 1.5, 0.25, 100),
            (key_root + 3, 2.0, 0.25, 100),
            (key_root + 5, 2.5, 0.25, 100),
            (key_root + 7, 3.0, 0.5, 100),
        ],
        8: [
            (key_root + 7, 0.0, 0.5, 90),
            (key_root + 8, 1.0, 0.25, 90),
            (key_root + 10, 1.5, 0.25, 90),
            (key_root + 7, 2.0, 0.5, 90),
            (key_root + 5, 3.0, 0.5, 90),
        ],
        9: [
            (key_root + 5, 0.0, 0.25, 90),
            (key_root + 7, 0.5, 0.25, 90),
            (key_root + 5, 1.0, 0.25, 90),
            (key_root + 3, 1.5, 0.25, 90),
            (key_root + 5, 2.0, 0.5, 90),
            (key_root + 3, 3.0, 0.5, 90),
        ],
        10: [
            (key_root + 12, 0.0, 0.25, 100),
            (key_root + 10, 0.25, 0.25, 100),
            (key_root + 7, 0.5, 0.25, 100),
            (key_root + 5, 0.75, 0.25, 100),
            (key_root + 7, 1.0, 0.5, 100),
            (key_root + 10, 2.0, 0.5, 100),
            (key_root + 12, 3.0, 0.5, 100),
        ],
        11: [
            (key_root + 15, 0.0, 0.25, 100),
            (key_root + 12, 0.5, 0.25, 100),
            (key_root + 10, 1.0, 0.25, 100),
            (key_root + 7, 1.5, 0.25, 100),
            (key_root + 5, 2.0, 0.25, 100),
            (key_root + 7, 2.5, 0.25, 100),
            (key_root + 10, 3.0, 0.5, 100),
        ],
        12: [
            (key_root + 7, 0.0, 0.5, 90),
            (key_root + 5, 1.0, 0.5, 90),
            (key_root + 3, 2.0, 0.5, 90),
            (key_root + 5, 3.0, 0.5, 90),
        ],
        13: [
            (key_root + 12, 0.0, 0.25, 100),
            (key_root + 10, 0.5, 0.25, 100),
            (key_root + 7, 1.0, 0.25, 100),
            (key_root + 5, 1.5, 0.25, 100),
            (key_root + 3, 2.0, 0.25, 100),
            (key_root + 5, 2.5, 0.25, 100),
            (key_root + 7, 3.0, 0.5, 100),
        ],
        14: [(key_root + 7, 0.0, 1.0, 85), (key_root + 5, 2.0, 1.0, 80)],
        15: [(key_root + 5, 0.0, 2.0, 75), (key_root + 3, 2.0, 2.0, 70)],
    }
    return patterns.get(scene_index, patterns[0])


# Pad patterns (sustained chords)
def generate_pad_pattern(scene_index, key_root=57):  # A3 = 57
    """Generate a pad pattern (sustained chord notes)."""
    # A minor chord notes relative to A3
    chord_tones = {
        "Am": [0, 3, 7],  # A-C-E
        "F": [5, 9, 12],  # F-A-C
        "C": [0, 4, 7],  # C-E-G (relative to C)
        "G": [7, 11, 14],  # G-B-D
        "Dm": [2, 5, 9],  # D-F-A
        "Em": [4, 7, 11],  # E-G-B
    }

    progressions = {
        0: ["Am", "F", "C", "G"],
        1: ["Am", "F", "C", "G"],
        2: ["Am", "Em", "F", "G"],
        3: ["Am", "F", "G", "Am"],
        4: ["Am", "F", "C", "G"],
        5: ["Dm", "Am", "Em", "Am"],
        6: ["Am", "F", "C", "G"],
        7: ["Am", "Em", "F", "G"],
        8: ["Am", "F", "C", "G"],
        9: ["Am", "Em", "F", "C"],
        10: ["Am", "F", "G", "Am"],
        11: ["Am", "F", "C", "G"],
        12: ["Dm", "Am", "F", "C"],
        13: ["Am", "F", "C", "G"],
        14: ["Am", "Em", "F", "G"],
        15: ["Am", "F"],
    }

    progression = progressions.get(scene_index, progressions[0])
    notes = []
    chord_duration = 4.0 / len(progression)

    for i, chord_name in enumerate(progression):
        tones = chord_tones.get(chord_name, [0, 3, 7])
        start = i * chord_duration
        for tone in tones:
            notes.append((key_root + tone, start, chord_duration, 70))

    return notes


# Strings patterns (arpeggiated or sustained)
def generate_strings_pattern(scene_index, key_root=57):  # A3
    """Generate a strings pattern."""
    if scene_index == 5:  # Breakdown - sustained
        return [
            (key_root, 0.0, 4.0, 65),
            (key_root + 3, 0.0, 4.0, 65),
            (key_root + 7, 0.0, 4.0, 65),
        ]

    # Arpeggiated pattern
    patterns = {
        0: [
            (key_root, 0.0, 1.0, 60),
            (key_root + 3, 1.0, 1.0, 60),
            (key_root + 7, 2.0, 1.0, 60),
            (key_root + 3, 3.0, 1.0, 60),
        ],
        1: [
            (key_root, 0.0, 0.5, 65),
            (key_root + 7, 0.5, 0.5, 65),
            (key_root + 3, 1.0, 0.5, 65),
            (key_root + 7, 1.5, 0.5, 65),
            (key_root, 2.0, 0.5, 65),
            (key_root + 7, 2.5, 0.5, 65),
            (key_root + 3, 3.0, 0.5, 65),
            (key_root + 7, 3.5, 0.5, 65),
        ],
        2: [
            (key_root + 12, 0.0, 0.25, 65),
            (key_root + 7, 0.25, 0.25, 65),
            (key_root + 3, 0.5, 0.25, 65),
            (key_root + 7, 0.75, 0.25, 65),
            (key_root, 1.0, 0.5, 65),
            (key_root + 3, 2.0, 0.5, 65),
            (key_root + 7, 3.0, 0.5, 65),
        ],
        3: [
            (key_root, 0.0, 0.5, 70),
            (key_root + 3, 0.5, 0.5, 70),
            (key_root + 7, 1.0, 0.5, 70),
            (key_root + 12, 1.5, 0.5, 70),
            (key_root + 7, 2.0, 0.5, 70),
            (key_root + 3, 2.5, 0.5, 70),
            (key_root, 3.0, 0.5, 70),
            (key_root + 3, 3.5, 0.5, 70),
        ],
        4: [
            (key_root + 12, 0.0, 0.25, 70),
            (key_root + 7, 0.25, 0.25, 70),
            (key_root + 3, 0.5, 0.25, 70),
            (key_root, 0.75, 0.25, 70),
        ]
        * 2,
        5: [
            (key_root, 0.0, 4.0, 60),
            (key_root + 3, 0.0, 4.0, 60),
            (key_root + 7, 0.0, 4.0, 60),
        ],
        6: [
            (key_root, 0.0, 0.5, 65),
            (key_root + 7, 0.5, 0.5, 65),
            (key_root + 3, 1.0, 0.5, 65),
            (key_root + 7, 1.5, 0.5, 65),
        ]
        * 2,
        7: [
            (key_root + 12, 0.0, 0.25, 70),
            (key_root + 7, 0.25, 0.25, 70),
            (key_root + 3, 0.5, 0.25, 70),
            (key_root, 0.75, 0.25, 70),
        ]
        * 2,
        8: [
            (key_root, 0.0, 1.0, 65),
            (key_root + 3, 1.0, 1.0, 65),
            (key_root + 7, 2.0, 1.0, 65),
            (key_root + 3, 3.0, 1.0, 65),
        ],
        9: [
            (key_root + 7, 0.0, 0.5, 65),
            (key_root + 3, 0.5, 0.5, 65),
            (key_root, 1.0, 0.5, 65),
            (key_root + 7, 1.5, 0.5, 65),
        ]
        * 2,
        10: [
            (key_root + 12, 0.0, 0.25, 70),
            (key_root + 7, 0.25, 0.25, 70),
            (key_root + 3, 0.5, 0.25, 70),
            (key_root, 0.75, 0.25, 70),
        ]
        * 2,
        11: [
            (key_root + 12, 0.0, 0.25, 70),
            (key_root + 15, 0.25, 0.25, 70),
            (key_root + 12, 0.5, 0.25, 70),
            (key_root + 7, 0.75, 0.25, 70),
        ]
        * 2,
        12: [
            (key_root, 0.0, 0.5, 65),
            (key_root + 3, 0.5, 0.5, 65),
            (key_root + 7, 1.0, 0.5, 65),
            (key_root + 12, 1.5, 0.5, 65),
            (key_root + 7, 2.0, 0.5, 65),
            (key_root + 3, 2.5, 0.5, 65),
            (key_root, 3.0, 0.5, 65),
            (key_root + 3, 3.5, 0.5, 65),
        ],
        13: [
            (key_root + 12, 0.0, 0.25, 70),
            (key_root + 7, 0.25, 0.25, 70),
            (key_root + 3, 0.5, 0.25, 70),
            (key_root, 0.75, 0.25, 70),
        ]
        * 2,
        14: [
            (key_root, 0.0, 2.0, 60),
            (key_root + 3, 0.0, 2.0, 60),
            (key_root + 7, 2.0, 2.0, 55),
            (key_root + 3, 2.0, 2.0, 55),
        ],
        15: [(key_root, 0.0, 4.0, 50), (key_root + 3, 0.0, 4.0, 50)],
    }
    return patterns.get(scene_index, patterns[0])


# FX patterns (impacts, risers, etc.)
def generate_fx_pattern(scene_index):
    """Generate FX pattern for the scene."""
    # FX uses high MIDI notes for impact/riser sounds
    # These would typically be mapped to specific FX samples in a drum rack

    patterns = {
        0: [],  # Intro - no FX
        1: [(60, 3.75, 0.25, 100)],  # Pre-drop riser
        2: [(61, 3.5, 0.5, 100)],  # Build riser
        3: [(62, 0.0, 0.25, 120)],  # Impact on drop
        4: [(62, 0.0, 0.25, 120), (60, 3.75, 0.25, 100)],  # Impact + riser
        5: [(63, 0.0, 1.0, 80)],  # Atmospheric
        6: [(60, 3.75, 0.25, 100)],  # Pre-drop
        7: [(62, 0.0, 0.25, 120)],  # Impact
        8: [],  # No FX
        9: [(60, 3.75, 0.25, 100)],  # Subtle riser
        10: [(62, 0.0, 0.25, 120), (61, 3.5, 0.5, 100)],  # Impact + riser
        11: [(62, 0.0, 0.25, 120)],  # Impact
        12: [(63, 0.0, 1.0, 80)],  # Atmospheric
        13: [(62, 0.0, 0.25, 120), (61, 3.0, 1.0, 100)],  # Impact + riser
        14: [(64, 0.0, 2.0, 70)],  # Wind down
        15: [],  # Outro - no FX
    }
    return patterns.get(scene_index, [])


# Percussion patterns (hi-hats, shakers, etc.)
def generate_percussion_pattern(scene_index):
    """Generate percussion pattern."""
    # Using note 42 for closed hat, 46 for open hat, 39 for clap

    patterns = {
        0: [
            (42, 0.5, 0.25, 80),
            (42, 1.5, 0.25, 80),
            (42, 2.5, 0.25, 80),
            (42, 3.5, 0.25, 80),
        ],  # Sparse
        1: [
            (42, 0.5, 0.25, 85),
            (42, 1.5, 0.25, 85),
            (42, 2.5, 0.25, 85),
            (42, 3.5, 0.25, 85),
            (39, 2.0, 0.25, 90),
        ],
        2: [
            (42, 0.5, 0.25, 85),
            (42, 1.0, 0.25, 85),
            (42, 1.5, 0.25, 85),
            (42, 2.5, 0.25, 85),
            (42, 3.0, 0.25, 85),
            (42, 3.5, 0.25, 85),
            (39, 2.0, 0.25, 90),
        ],
        3: [
            (42, 0.5, 0.25, 90),
            (42, 1.0, 0.25, 90),
            (42, 1.5, 0.25, 90),
            (42, 2.0, 0.25, 90),
            (42, 2.5, 0.25, 90),
            (42, 3.0, 0.25, 90),
            (42, 3.5, 0.25, 90),
            (39, 2.0, 0.25, 95),
        ],  # Full hats
        4: [
            (42, 0.5, 0.25, 90),
            (42, 1.0, 0.25, 90),
            (42, 1.5, 0.25, 90),
            (42, 2.0, 0.25, 90),
            (42, 2.5, 0.25, 90),
            (42, 3.0, 0.25, 90),
            (42, 3.5, 0.25, 90),
            (39, 2.0, 0.25, 95),
        ],
        5: [(46, 0.0, 0.5, 70), (46, 2.0, 0.5, 70)],  # Open hats for breakdown
        6: [
            (42, 0.5, 0.25, 85),
            (42, 1.5, 0.25, 85),
            (42, 2.5, 0.25, 85),
            (42, 3.5, 0.25, 85),
            (39, 2.0, 0.25, 90),
        ],
        7: [
            (42, 0.5, 0.25, 90),
            (42, 1.0, 0.25, 90),
            (42, 1.5, 0.25, 90),
            (42, 2.0, 0.25, 90),
            (42, 2.5, 0.25, 90),
            (42, 3.0, 0.25, 90),
            (42, 3.5, 0.25, 90),
            (39, 2.0, 0.25, 95),
        ],
        8: [
            (42, 0.5, 0.25, 85),
            (42, 1.5, 0.25, 85),
            (42, 2.5, 0.25, 85),
            (42, 3.5, 0.25, 85),
        ],
        9: [
            (42, 0.5, 0.25, 85),
            (42, 1.0, 0.25, 85),
            (42, 2.5, 0.25, 85),
            (42, 3.0, 0.25, 85),
            (39, 2.0, 0.25, 90),
        ],
        10: [
            (42, 0.5, 0.25, 90),
            (42, 1.0, 0.25, 90),
            (42, 1.5, 0.25, 90),
            (42, 2.0, 0.25, 90),
            (42, 2.5, 0.25, 90),
            (42, 3.0, 0.25, 90),
            (42, 3.5, 0.25, 90),
            (39, 2.0, 0.25, 95),
        ],
        11: [
            (42, 0.5, 0.25, 90),
            (42, 1.0, 0.25, 90),
            (42, 1.5, 0.25, 90),
            (42, 2.0, 0.25, 90),
            (42, 2.5, 0.25, 90),
            (42, 3.0, 0.25, 90),
            (42, 3.5, 0.25, 90),
            (39, 2.0, 0.25, 95),
        ],
        12: [
            (42, 0.5, 0.25, 85),
            (42, 1.5, 0.25, 85),
            (42, 2.5, 0.25, 85),
            (42, 3.5, 0.25, 85),
        ],
        13: [
            (42, 0.5, 0.25, 90),
            (42, 1.0, 0.25, 90),
            (42, 1.5, 0.25, 90),
            (42, 2.0, 0.25, 90),
            (42, 2.5, 0.25, 90),
            (42, 3.0, 0.25, 90),
            (42, 3.5, 0.25, 90),
            (39, 2.0, 0.25, 95),
        ],
        14: [(42, 0.5, 0.25, 80), (42, 2.5, 0.25, 75)],  # Sparse
        15: [(46, 0.0, 1.0, 60), (46, 2.0, 1.0, 55)],  # Open hats fading
    }
    return patterns.get(scene_index, patterns[0])


def rework_scene(sock, scene_index, tracks):
    """Rework all clips in a scene with proper patterns."""
    print(f"\n=== Reworking Scene {scene_index} ===")

    # Track indices (from session overview)
    # 2: Drums, 3: Bass, 4: Chords, 5: Lead, 6: Pad, 7: Strings, 8: FX, 9: Percussion

    track_map = {t["name"]: t["index"] for t in tracks}

    results = {}

    # 1. Drums - Create drum pattern
    if "Drums" in track_map:
        track_idx = track_map["Drums"]
        try:
            # Delete existing clip
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)

            # Create new clip
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            # Choose drum pattern based on scene energy
            if scene_index <= 3:
                pattern = "dub_techno"
            elif scene_index == 5:
                pattern = "dub_techno"
            elif scene_index >= 14:
                pattern = "dub_techno"
            else:
                pattern = "techno_4x4"

            create_drum_pattern(sock, track_idx, scene_index, pattern, 4.0)
            set_clip_name(sock, track_idx, scene_index, f"Drums_S{scene_index:02d}")
            results["Drums"] = f"Created {pattern} pattern"
            print(f"  Drums: Created {pattern} pattern")
        except Exception as e:
            results["Drums"] = f"Error: {e}"
            print(f"  Drums: Error - {e}")

    # 2. Bass - Create bass pattern
    if "Bass" in track_map:
        track_idx = track_map["Bass"]
        try:
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            # Generate bass notes (A2 = 45)
            bass_notes = generate_bass_pattern(45, scene_index)
            notes_data = [
                {
                    "pitch": n[0],
                    "start_time": n[1],
                    "duration": n[2],
                    "velocity": n[3],
                    "mute": False,
                }
                for n in bass_notes
            ]
            add_notes_to_clip(sock, track_idx, scene_index, notes_data)
            set_clip_name(sock, track_idx, scene_index, f"Bass_S{scene_index:02d}")
            results["Bass"] = f"Added {len(bass_notes)} notes"
            print(f"  Bass: Added {len(bass_notes)} notes")
        except Exception as e:
            results["Bass"] = f"Error: {e}"
            print(f"  Bass: Error - {e}")

    # 3. Chords - Create chord progression
    if "Chords" in track_map:
        track_idx = track_map["Chords"]
        try:
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            # Add chord notes
            progression = CHORD_PROGRESSIONS.get(scene_index, CHORD_PROGRESSIONS[0])
            chord_duration = 4.0 / len(progression)

            # Root notes for chords (A3 = 57)
            chord_roots = {"Am": 57, "F": 53, "C": 48, "G": 55, "Dm": 50, "Em": 52}

            all_notes = []
            for i, chord_name in enumerate(progression):
                root = chord_roots.get(chord_name, 57)
                start = i * chord_duration

                # Add chord tones
                if chord_name == "Am":
                    tones = [0, 3, 7]  # A-C-E
                elif chord_name == "F":
                    tones = [0, 4, 7]  # F-A-C
                elif chord_name == "C":
                    tones = [0, 4, 7]  # C-E-G
                elif chord_name == "G":
                    tones = [0, 4, 7]  # G-B-D
                elif chord_name == "Dm":
                    tones = [0, 3, 7]  # D-F-A
                elif chord_name == "Em":
                    tones = [0, 3, 7]  # E-G-B
                else:
                    tones = [0, 3, 7]

                for tone in tones:
                    all_notes.append(
                        {
                            "pitch": root + tone,
                            "start_time": start,
                            "duration": chord_duration,
                            "velocity": 85,
                            "mute": False,
                        }
                    )

            add_notes_to_clip(sock, track_idx, scene_index, all_notes)
            set_clip_name(sock, track_idx, scene_index, f"Chords_S{scene_index:02d}")
            results["Chords"] = (
                f"Added {len(all_notes)} notes ({'-'.join(progression)})"
            )
            print(f"  Chords: Added {len(all_notes)} notes ({'-'.join(progression)})")
        except Exception as e:
            results["Chords"] = f"Error: {e}"
            print(f"  Chords: Error - {e}")

    # 4. Lead - Create lead melody
    if "Lead" in track_map:
        track_idx = track_map["Lead"]
        try:
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            lead_notes = generate_lead_pattern(scene_index)
            if lead_notes:
                notes_data = [
                    {
                        "pitch": n[0],
                        "start_time": n[1],
                        "duration": n[2],
                        "velocity": n[3],
                        "mute": False,
                    }
                    for n in lead_notes
                ]
                add_notes_to_clip(sock, track_idx, scene_index, notes_data)
                results["Lead"] = f"Added {len(lead_notes)} notes"
                print(f"  Lead: Added {len(lead_notes)} notes")
            else:
                results["Lead"] = "Empty (breakdown)"
                print(f"  Lead: Empty (breakdown)")
            set_clip_name(sock, track_idx, scene_index, f"Lead_S{scene_index:02d}")
        except Exception as e:
            results["Lead"] = f"Error: {e}"
            print(f"  Lead: Error - {e}")

    # 5. Pad - Create pad pattern
    if "Pad" in track_map:
        track_idx = track_map["Pad"]
        try:
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            pad_notes = generate_pad_pattern(scene_index)
            notes_data = [
                {
                    "pitch": n[0],
                    "start_time": n[1],
                    "duration": n[2],
                    "velocity": n[3],
                    "mute": False,
                }
                for n in pad_notes
            ]
            add_notes_to_clip(sock, track_idx, scene_index, notes_data)
            set_clip_name(sock, track_idx, scene_index, f"Pad_S{scene_index:02d}")
            results["Pad"] = f"Added {len(pad_notes)} notes"
            print(f"  Pad: Added {len(pad_notes)} notes")
        except Exception as e:
            results["Pad"] = f"Error: {e}"
            print(f"  Pad: Error - {e}")

    # 6. Strings - Create strings pattern
    if "Strings" in track_map:
        track_idx = track_map["Strings"]
        try:
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            strings_notes = generate_strings_pattern(scene_index)
            notes_data = [
                {
                    "pitch": n[0],
                    "start_time": n[1],
                    "duration": n[2],
                    "velocity": n[3],
                    "mute": False,
                }
                for n in strings_notes
            ]
            add_notes_to_clip(sock, track_idx, scene_index, notes_data)
            set_clip_name(sock, track_idx, scene_index, f"Strings_S{scene_index:02d}")
            results["Strings"] = f"Added {len(strings_notes)} notes"
            print(f"  Strings: Added {len(strings_notes)} notes")
        except Exception as e:
            results["Strings"] = f"Error: {e}"
            print(f"  Strings: Error - {e}")

    # 7. FX - Create FX pattern
    if "FX" in track_map:
        track_idx = track_map["FX"]
        try:
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            fx_notes = generate_fx_pattern(scene_index)
            if fx_notes:
                notes_data = [
                    {
                        "pitch": n[0],
                        "start_time": n[1],
                        "duration": n[2],
                        "velocity": n[3],
                        "mute": False,
                    }
                    for n in fx_notes
                ]
                add_notes_to_clip(sock, track_idx, scene_index, notes_data)
                results["FX"] = f"Added {len(fx_notes)} notes"
                print(f"  FX: Added {len(fx_notes)} notes")
            else:
                results["FX"] = "Empty"
                print(f"  FX: Empty")
            set_clip_name(sock, track_idx, scene_index, f"FX_S{scene_index:02d}")
        except Exception as e:
            results["FX"] = f"Error: {e}"
            print(f"  FX: Error - {e}")

    # 8. Percussion - Create percussion pattern
    if "Percussion" in track_map:
        track_idx = track_map["Percussion"]
        try:
            delete_clip(sock, track_idx, scene_index)
            time.sleep(0.05)
            create_clip(sock, track_idx, scene_index, 4.0)
            time.sleep(0.05)

            perc_notes = generate_percussion_pattern(scene_index)
            notes_data = [
                {
                    "pitch": n[0],
                    "start_time": n[1],
                    "duration": n[2],
                    "velocity": n[3],
                    "mute": False,
                }
                for n in perc_notes
            ]
            add_notes_to_clip(sock, track_idx, scene_index, notes_data)
            set_clip_name(sock, track_idx, scene_index, f"Perc_S{scene_index:02d}")
            results["Percussion"] = f"Added {len(perc_notes)} notes"
            print(f"  Percussion: Added {len(perc_notes)} notes")
        except Exception as e:
            results["Percussion"] = f"Error: {e}"
            print(f"  Percussion: Error - {e}")

    return results


def verify_scene(sock, scene_index, tracks):
    """Verify that a scene has proper patterns (not just single notes)."""
    print(f"\n--- Verifying Scene {scene_index} ---")

    track_map = {t["name"]: t["index"] for t in tracks}
    verification = {}

    midi_tracks = [
        "Drums",
        "Bass",
        "Chords",
        "Lead",
        "Pad",
        "Strings",
        "FX",
        "Percussion",
    ]

    for track_name in midi_tracks:
        if track_name not in track_map:
            continue

        track_idx = track_map[track_name]
        try:
            result = get_clip_notes(sock, track_idx, scene_index)
            notes = result.get("notes", [])
            note_count = len(notes)

            # Check if it's a proper pattern (more than 1-2 notes)
            if note_count <= 2 and track_name not in ["FX", "Lead"]:
                verification[track_name] = (
                    f"WARNING: Only {note_count} notes (may need rework)"
                )
                print(f"  {track_name}: WARNING - Only {note_count} notes")
            else:
                verification[track_name] = f"OK - {note_count} notes"
                print(f"  {track_name}: OK - {note_count} notes")
        except Exception as e:
            verification[track_name] = f"Error: {e}"
            print(f"  {track_name}: Error - {e}")

    return verification


def main():
    """Main function to rework all 16 scenes."""
    print("=" * 60)
    print("CLIP REWORKING SCRIPT - Direct TCP Connection")
    print("=" * 60)

    # Connect to Ableton
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    try:
        print(f"\nConnecting to Ableton at {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        print("Connected!")

        # Get session info
        session = get_session_info(sock)
        print(
            f"\nSession: {session.get('tempo')} BPM, {session.get('track_count')} tracks"
        )

        # Get all tracks
        tracks_result = get_all_tracks(sock)
        tracks = tracks_result.get("tracks", [])
        print(f"Tracks: {[t['name'] for t in tracks if t.get('is_midi')]}")

        # Update todo list
        all_results = {}

        # Rework all 16 scenes
        for scene_index in range(16):
            results = rework_scene(sock, scene_index, tracks)
            all_results[f"scene_{scene_index}"] = results
            time.sleep(0.1)  # Small delay between scenes

        print("\n" + "=" * 60)
        print("VERIFICATION PHASE")
        print("=" * 60)

        # Verify all scenes
        all_verifications = {}
        for scene_index in range(16):
            verification = verify_scene(sock, scene_index, tracks)
            all_verifications[f"scene_{scene_index}"] = verification
            time.sleep(0.05)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        # Count successes and warnings
        total_ok = 0
        total_warnings = 0
        total_errors = 0

        for scene_key, verification in all_verifications.items():
            for track, status in verification.items():
                if "OK" in status:
                    total_ok += 1
                elif "WARNING" in status:
                    total_warnings += 1
                elif "Error" in status:
                    total_errors += 1

        print(f"Total OK: {total_ok}")
        print(f"Total Warnings: {total_warnings}")
        print(f"Total Errors: {total_errors}")

        print("\n" + "=" * 60)
        print("REWORKING COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        sock.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()
