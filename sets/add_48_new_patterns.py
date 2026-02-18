import json
import socket
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return the response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


print("=" * 80)
print("ADDING 48 NEW DUB TECHNO PATTERNS")
print("=" * 80)
print(f"Extending existing 48 patterns with 48 new advanced patterns")
print(f"Total: 96 patterns (16 per track)")
print("=" * 80)

# Get current session info to find track indices
session_info = send_command("get_session_info")
kick_track_index = 1
bass_track_index = 2
hihat_track_index = 3
pad_track_index = 4
fx_track_index = 5
delay_track_index = 6

# ============================================================================
# NEW KICK CLIPS - Advanced 4/4 variations
# ============================================================================
print("\nAdding NEW Kick clips (8-15)...")

kick_new_clips = [
    # Clip 8: Polyrhythmic 3-over-4 pattern (Basic Channel style)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.33,
                "duration": 0.15,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.33,
                "duration": 0.15,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Kick Polyrhythmic",
    },
    # Clip 9: Ghost notes on offbeats
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 0.75,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.75,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.75,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.75,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Kick Ghost Notes",
    },
    # Clip 10: Triplet pattern on beat 2 and 4
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.08,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.17,
                "duration": 0.08,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.33,
                "duration": 0.08,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Triplets",
    },
    # Clip 11: Reverse buildup pattern
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.15,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Kick Reverse Build",
    },
    # Clip 12: Micro-timing shuffle
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 0.97,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.97,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.97,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Shuffle",
    },
    # Clip 13: Deep minimal
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 105,
                "mute": False,
            },
        ],
        "name": "Kick Deep Minimal",
    },
    # Clip 14: Accented pattern
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.3,
                "velocity": 120,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.2,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.75,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.3,
                "velocity": 120,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.2,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.75,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Kick Accented",
    },
    # Clip 15: Slow decay
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.4,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.35,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.3,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Slow Decay",
    },
]

for i, clip_data in enumerate(kick_new_clips, start=8):
    send_command(
        "create_clip",
        {"track_index": kick_track_index, "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": kick_track_index,
            "clip_index": i,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": kick_track_index,
            "clip_index": i,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Added Clip {i}: {clip_data['name']}")

# ============================================================================
# NEW SUB-BASS CLIPS - Melodic and advanced patterns
# ============================================================================
print("\nAdding NEW Sub-bass clips (8-15)...")

subbass_new_clips = [
    # Clip 8: Melodic rise (C2-D2-Eb2)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 1.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 1.0,
                "duration": 1.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 39,
                "start_time": 2.0,
                "duration": 1.0,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass Melodic Rise",
    },
    # Clip 9: Pulsing fifth interval
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 0.0,
                "duration": 2.0,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 80,
                "mute": False,
            },
        ],
        "name": "Bass Fifth Pulsing",
    },
    # Clip 10: Call and response
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.75,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.5,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.25,
                "duration": 0.75,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass Call Response",
    },
    # Clip 11: Arpeggiated pattern
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.5,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 0.5,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.5,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 1.5,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.5,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 2.5,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.5,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Bass Arpeggio",
    },
    # Clip 12: Octave bounce
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 1.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 1.0,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.5,
                "duration": 1.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 2.5,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass Octave Bounce",
    },
    # Clip 13: Eb drone (subdominant)
    {
        "notes": [
            {
                "pitch": 39,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass Eb Drone",
    },
    # Clip 14: Syncopated triplet feel
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 1.33,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 1.33,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass Syncopated Triplet",
    },
    # Clip 15: Slow evolving drone
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 2.0,
                "duration": 1.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 39,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Bass Evolving Drone",
    },
]

for i, clip_data in enumerate(subbass_new_clips, start=8):
    send_command(
        "create_clip",
        {"track_index": bass_track_index, "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": bass_track_index,
            "clip_index": i,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": bass_track_index,
            "clip_index": i,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Added Clip {i}: {clip_data['name']}")

# ============================================================================
# NEW HI-HAT CLIPS - Advanced textural patterns
# ============================================================================
print("\nAdding NEW Hi-hat clips (8-15)...")

hihat_new_clips = [
    # Clip 8: Triplet pattern
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.5,
                "duration": 0.08,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 0.67,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 0.83,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.5,
                "duration": 0.08,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.67,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.83,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat Triplets",
    },
    # Clip 9: Ghost accents
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 0.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Hi-hat Ghost Accents",
    },
    # Clip 10: Closed-open combo
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.5,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 77,
                "start_time": 1.5,
                "duration": 0.2,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.5,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 77,
                "start_time": 3.5,
                "duration": 0.2,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "Hi-hat Closed Open",
    },
    # Clip 11: Shuffle pattern
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.52,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.52,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.52,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.52,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat Shuffle",
    },
    # Clip 12: 8th note build
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.0,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.0,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.0,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat 8th Build",
    },
    # Clip 13: Rolling buildup
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.0,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.0,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.0,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.25,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Hi-hat Rolling",
    },
    # Clip 14: Subtle texture
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Hi-hat Subtle Texture",
    },
    # Clip 15: Syncopated 16ths
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.75,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.25,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.75,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.25,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.75,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat Syncopated 16ths",
    },
]

for i, clip_data in enumerate(hihat_new_clips, start=8):
    send_command(
        "create_clip",
        {"track_index": hihat_track_index, "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": hihat_track_index,
            "clip_index": i,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": hihat_track_index,
            "clip_index": i,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Added Clip {i}: {clip_data['name']}")

# ============================================================================
# NEW SYNTH PAD CLIPS - Extended chords and advanced harmony
# ============================================================================
print("\nAdding NEW Synth Pad clips (8-15)...")

pad_new_clips = [
    # Clip 8: Cm9 (C3, Eb3, G3, Bb3, D4)
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 40,
                "mute": False,
            },
            {
                "pitch": 62,
                "start_time": 1.0,
                "duration": 3.0,
                "velocity": 35,
                "mute": False,
            },
        ],
        "name": "Pad Cm9",
    },
    # Clip 9: Fm11 (F3, Ab3, C4, Eb4, Bb3)
    {
        "notes": [
            {
                "pitch": 53,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 56,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 63,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 40,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 1.5,
                "duration": 2.5,
                "velocity": 35,
                "mute": False,
            },
        ],
        "name": "Pad Fm11",
    },
    # Clip 10: Gm9 (G3, Bb3, D4, F4)
    {
        "notes": [
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 62,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 40,
                "mute": False,
            },
            {
                "pitch": 65,
                "start_time": 1.0,
                "duration": 3.0,
                "velocity": 35,
                "mute": False,
            },
        ],
        "name": "Pad Gm9",
    },
    # Clip 11: Fm first inversion (Ab3, C4, F4)
    {
        "notes": [
            {
                "pitch": 56,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 65,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
        ],
        "name": "Pad Fm Inversion",
    },
    # Clip 12: Csus2 (C3, D3, G3)
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 50,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
        ],
        "name": "Pad Csus2",
    },
    # Clip 13: Csus4 (C3, F3, G3)
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 53,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
        ],
        "name": "Pad Csus4",
    },
    # Clip 14: Evolving cluster (Cm to Gm)
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 2.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 0.0,
                "duration": 2.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 40,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 50,
                "mute": False,
            },
        ],
        "name": "Pad Evolving Cluster",
    },
    # Clip 15: Very sparse (high drone)
    {
        "notes": [
            {
                "pitch": 72,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 30,
                "mute": False,
            },
        ],
        "name": "Pad High Sparse",
    },
]

for i, clip_data in enumerate(pad_new_clips, start=8):
    send_command(
        "create_clip",
        {"track_index": pad_track_index, "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": pad_track_index,
            "clip_index": i,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": pad_track_index,
            "clip_index": i,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Added Clip {i}: {clip_data['name']}")

# ============================================================================
# NEW FX CLIPS - Advanced textures
# ============================================================================
print("\nAdding NEW FX clips (8-15)...")

fx_new_clips = [
    # Clip 8: Vinyl crackle (multiple low-velocity hits)
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.25,
                "duration": 0.05,
                "velocity": 35,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 0.75,
                "duration": 0.03,
                "velocity": 30,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 1.5,
                "duration": 0.04,
                "velocity": 35,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 2.25,
                "duration": 0.05,
                "velocity": 30,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 3.5,
                "duration": 0.03,
                "velocity": 35,
                "mute": False,
            },
        ],
        "name": "FX Vinyl Crackle",
    },
    # Clip 9: Downward sweep
    {
        "notes": [
            {
                "pitch": 84,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 80,
                "mute": False,
            },
        ],
        "name": "FX Downward Sweep",
    },
    # Clip 10: Glitch stutter
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 1.0,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 1.08,
                "duration": 0.08,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 1.16,
                "duration": 0.08,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 1.24,
                "duration": 0.08,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 1.32,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "FX Glitch Stutter",
    },
    # Clip 11: Tape stop (slow down effect)
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "FX Tape Stop",
    },
    # Clip 12: Metallic ring
    {
        "notes": [
            {
                "pitch": 79,
                "start_time": 1.5,
                "duration": 0.8,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "FX Metallic Ring",
    },
    # Clip 13: Sub rumble
    {
        "notes": [
            {
                "pitch": 20,
                "start_time": 0.0,
                "duration": 2.0,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "FX Sub Rumble",
    },
    # Clip 14: Reverse impact
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "FX Reverse Impact",
    },
    # Clip 15: White noise burst
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.75,
                "duration": 0.25,
                "velocity": 85,
                "mute": False,
            },
        ],
        "name": "FX Noise Burst",
    },
]

for i, clip_data in enumerate(fx_new_clips, start=8):
    send_command(
        "create_clip",
        {"track_index": fx_track_index, "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": fx_track_index,
            "clip_index": i,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": fx_track_index,
            "clip_index": i,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Added Clip {i}: {clip_data['name']}")

# ============================================================================
# NEW DUB DELAY CLIPS - Advanced dub delay techniques
# ============================================================================
print("\nAdding NEW Dub Delay clips (8-15)...")

delay_new_clips = [
    # Clip 8: Ping-pong delay (alternating pattern)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
        ],
        "name": "Delay Ping Pong",
    },
    # Clip 9: Echo feedback (gradually decreasing)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.15,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.75,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.5,
                "duration": 0.08,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.05,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "Delay Echo Feedback",
    },
    # Clip 10: Tape delay simulation (slight timing drift)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.52,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.51,
                "duration": 0.1,
                "velocity": 78,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.53,
                "duration": 0.1,
                "velocity": 76,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
        ],
        "name": "Delay Tape Sim",
    },
    # Clip 11: Slapback delay (short, single echo)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.5,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 0.65,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.5,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.65,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay Slapback",
    },
    # Clip 12: Dotted eighth delays (classic dub)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.75,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.75,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.75,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.75,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay Dotted Eighth",
    },
    # Clip 13: Multi-tap delay (3-tap pattern)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.25,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.5,
                "duration": 0.06,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.25,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.06,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Delay Multi-tap",
    },
    # Clip 14: Infinite decay (long sustained echo)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.2,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Delay Infinite Decay",
    },
    # Clip 15: Dub echo (rhythmic pattern)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.5,
                "duration": 0.15,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.75,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.25,
                "duration": 0.08,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
        ],
        "name": "Delay Dub Echo",
    },
]

for i, clip_data in enumerate(delay_new_clips, start=8):
    send_command(
        "create_clip",
        {"track_index": delay_track_index, "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": delay_track_index,
            "clip_index": i,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": delay_track_index,
            "clip_index": i,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Added Clip {i}: {clip_data['name']}")

print("\n" + "=" * 80)
print("ALL 48 NEW PATTERNS ADDED SUCCESSFULLY!")
print("=" * 80)
print(f"\nSummary:")
print(
    f"  Track {kick_track_index} (Kick):        {8 + len(kick_new_clips)} total clips"
)
print(
    f"  Track {bass_track_index} (Sub-bass):    {8 + len(subbass_new_clips)} total clips"
)
print(
    f"  Track {hihat_track_index} (Hi-hats):     {8 + len(hihat_new_clips)} total clips"
)
print(f"  Track {pad_track_index} (Synth Pads):  {8 + len(pad_new_clips)} total clips")
print(f"  Track {fx_track_index} (FX):          {8 + len(fx_new_clips)} total clips")
print(
    f"  Track {delay_track_index} (Dub Delays):  {8 + len(delay_new_clips)} total clips"
)
print(
    f"  Total clips:           {(8 * 6) + len(kick_new_clips) + len(subbass_new_clips) + len(hihat_new_clips) + len(pad_new_clips) + len(fx_new_clips) + len(delay_new_clips)} clips"
)

print("\n" + "=" * 80)
print("PATTERN ADDITION COMPLETE!")
print("=" * 80)
print("\nNew advanced techniques added:")
print("  KICK: Polyrhythms, ghost notes, triplets, shuffle")
print("  SUB-BASS: Melodic lines, pulsing fifths, arpeggios")
print("  HI-HATS: Triplets, ghost accents, closed-open combos")
print("  PADS: Extended chords (m9, m11), inversions, sus chords")
print("  FX: Vinyl crackle, glitches, tape stops, metallic rings")
print("  DELAYS: Ping-pong, tape sim, multi-tap, dotted eighth")
print("\nYou now have 96 total dub techno patterns for 2-hour+ productions!")
print("\n")

s.close()
