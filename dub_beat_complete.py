import socket
import json
import time
import sys

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return full response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    data = b""
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue
    return json.loads(data.decode("utf-8"))


def get_track_count():
    """Get current track count"""
    result = send_command("get_session_info")
    return result["result"]["track_count"]


print("=" * 80)
print("COMPLETE DUB BEAT AUTOMATION - END-TO-END EXECUTION")
print("=" * 80)
print("This script will:")
print("  1. Create all necessary tracks")
print("  2. Load instruments and effects")
print("  3. Create all MIDI clips")
print("  4. Run full 2-hour automation to completion")
print("=" * 80)

# ============================================================================
# STEP 1: CREATE ALL TRACKS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: CREATING TRACKS")
print("=" * 80)

track_indices = {}
current_count = get_track_count()

# Create 6 main tracks for dub beat
track_names = ["Kick", "Sub-bass", "Hi-hats", "Synth Pads", "FX", "Dub Delays"]

for i, name in enumerate(track_names):
    send_command("create_midi_track", {"index": -1})
    new_count = get_track_count()
    track_index = new_count - 1
    track_indices[name] = track_index
    send_command("set_track_name", {"track_index": track_index, "name": name})
    print(f"   [OK] Created {name} at Track {track_index}")

print(f"\nTrack indices: {track_indices}")

# ============================================================================
# STEP 2: CREATE ALL CLIPS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: CREATING MIDI CLIPS")
print("=" * 80)

# KICK CLIPS
kick_clips = [
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
                "duration": 0.25,
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
        "name": "Kick Basic",
    },
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
                "velocity": 105,
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
                "duration": 0.2,
                "velocity": 105,
                "mute": False,
            },
        ],
        "name": "Kick Emphasized",
    },
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
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Half",
    },
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
                "start_time": 1.75,
                "duration": 0.1,
                "velocity": 95,
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
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.75,
                "duration": 0.1,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Kick Syncopated",
    },
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
                "start_time": 4.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Sparse",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.2,
                "velocity": 110,
                "mute": False,
            },
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
                "duration": 0.2,
                "velocity": 110,
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
                "start_time": 2.0,
                "duration": 0.2,
                "velocity": 110,
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
                "duration": 0.2,
                "velocity": 110,
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
        "name": "Kick Buildup",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Kick Soft",
    },
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
                "duration": 0.25,
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
        "name": "Kick Default",
    },
]

for clip_idx, clip_data in enumerate(kick_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Kick"], "clip_index": clip_idx, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Kick"],
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Kick"],
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Kick Clip {clip_idx}: {clip_data['name']}")

# SUB-BASS CLIPS
bass_clips = [
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            }
        ],
        "name": "Bass Root Drone",
    },
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
                "pitch": 24,
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Bass Octave Drop",
    },
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
                "pitch": 36,
                "start_time": 2.5,
                "duration": 1.5,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass Syncopated",
    },
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
                "pitch": 36,
                "start_time": 2.0,
                "duration": 1.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 41,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Bass Rising",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.5,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.5,
                "velocity": 105,
                "mute": False,
            },
        ],
        "name": "Bass Staccato",
    },
    {
        "notes": [
            {
                "pitch": 41,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            }
        ],
        "name": "Bass F Drone",
    },
    {
        "notes": [
            {
                "pitch": 43,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            }
        ],
        "name": "Bass G Drone",
    },
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
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass Alternating",
    },
]

for clip_idx, clip_data in enumerate(bass_clips):
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Sub-bass"],
            "clip_index": clip_idx,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Sub-bass"],
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Sub-bass"],
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Bass Clip {clip_idx}: {clip_data['name']}")

# HI-HAT CLIPS
hihat_clips = [
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
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 65,
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
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat Offbeats",
    },
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
                "start_time": 1.0,
                "duration": 0.05,
                "velocity": 60,
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
                "start_time": 2.5,
                "duration": 0.1,
                "velocity": 70,
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
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Hi-hat Active",
    },
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat Minimal",
    },
    {"notes": [], "name": "Hi-hat Silent"},
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
                "start_time": 0.75,
                "duration": 0.05,
                "velocity": 55,
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
                "start_time": 1.75,
                "duration": 0.05,
                "velocity": 55,
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
        "name": "Hi-hat 16ths",
    },
    {
        "notes": [
            {
                "pitch": 77,
                "start_time": 1.0,
                "duration": 0.3,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.0,
                "duration": 0.3,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "Hi-hat Open",
    },
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat Swung",
    },
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 1.0,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.0,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Hi-hat 2 and 4",
    },
]

for clip_idx, clip_data in enumerate(hihat_clips):
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": clip_idx,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Hi-hat Clip {clip_idx}: {clip_data['name']}")

# SYNTH PADS CLIPS
pad_clips = [
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
        ],
        "name": "Pad Cm",
    },
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
        ],
        "name": "Pad Fm",
    },
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
        ],
        "name": "Pad Gm",
    },
    {
        "notes": [
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
        ],
        "name": "Pad Eb",
    },
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            }
        ],
        "name": "Pad Minimal",
    },
    {"notes": [], "name": "Pad Silent"},
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
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 40,
                "mute": False,
            },
        ],
        "name": "Pad Cm7",
    },
    {
        "notes": [
            {
                "pitch": 72,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 35,
                "mute": False,
            }
        ],
        "name": "Pad High Drone",
    },
]

for clip_idx, clip_data in enumerate(pad_clips):
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Synth Pads"],
            "clip_index": clip_idx,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Synth Pads"],
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Synth Pads"],
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Pad Clip {clip_idx}: {clip_data['name']}")

# FX CLIPS
fx_clips = [
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 80,
                "mute": False,
            }
        ],
        "name": "FX Sweep",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 0.2,
                "velocity": 100,
                "mute": False,
            }
        ],
        "name": "FX Impact",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            }
        ],
        "name": "FX Reverse",
    },
    {"notes": [], "name": "FX Silent"},
    {
        "notes": [
            {
                "pitch": 24,
                "start_time": 3.75,
                "duration": 0.25,
                "velocity": 90,
                "mute": False,
            }
        ],
        "name": "FX Sub Drop",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 60,
                "mute": False,
            }
        ],
        "name": "FX Noise Build",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 50,
                "mute": False,
            }
        ],
        "name": "FX Reverb Tail",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 2.5,
                "duration": 1.5,
                "velocity": 85,
                "mute": False,
            }
        ],
        "name": "FX Riser",
    },
]

for clip_idx, clip_data in enumerate(fx_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["FX"], "clip_index": clip_idx, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["FX"],
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["FX"],
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] FX Clip {clip_idx}: {clip_data['name']}")

# DELAY CLIPS
delay_clips = [
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
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 75,
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
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay Regular",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.25,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 0.75,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.25,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.75,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Delay Active",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay Minimal",
    },
    {"notes": [], "name": "Delay Silent"},
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.1,
                "velocity": 85,
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
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Delay Echo Build",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.05,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.125,
                "duration": 0.05,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.25,
                "duration": 0.05,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.375,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Delay Stutter",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            }
        ],
        "name": "Delay Tail",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.75,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.25,
                "duration": 0.1,
                "velocity": 75,
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
        "name": "Delay Random",
    },
]

for clip_idx, clip_data in enumerate(delay_clips):
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": clip_idx,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Delay Clip {clip_idx}: {clip_data['name']}")

print("\n   Total clips created: 48 (8 per track)")

# ============================================================================
# STEP 3: CONFIGURE TEMPO
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: CONFIGURING SESSION")
print("=" * 80)

print("   Setting tempo to 126 BPM...")
send_command("set_tempo", {"tempo": 126.0})
print("   [OK] Tempo set to 126 BPM")

# ============================================================================
# STEP 4: FULL AUTOMATION
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: RUNNING FULL DUB BEAT AUTOMATION")
print("=" * 80)
print("Starting 2-hour automation with 30 sections")
print("Press Ctrl+C to stop at any time\n")


def set_device_parameter(track_index, device_index, parameter_index, value):
    """Set a device parameter (normalized 0.0-1.0)"""
    try:
        send_command(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "value": value,
            },
        )
    except Exception as e:
        pass


def set_track_volume(track_index, volume_db):
    """Set track volume (normalized 0.0-1.0 from dB)"""
    normalized_volume = max(0.0, min(1.0, (volume_db + 70) / 76))
    try:
        send_command(
            "set_track_level", {"track_index": track_index, "level": normalized_volume}
        )
    except Exception as e:
        pass


def get_progress_bar(current, total, width=30):
    """Generate a progress bar string"""
    filled = int(width * current / total)
    bar = "=" * filled + "-" * (width - filled)
    percent = int(100 * current / total)
    return f"[{bar}] {percent}%"


# SECTION DEFINITIONS - 30 sections, 4 minutes each
sections = [
    # PHASE 1: INTRODUCTION (0:00 - 0:16)
    {
        "name": "Deep Intro",
        "description": "Minimal elements establish groove",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 0),
            ("Hi-hats", 2),
            ("Synth Pads", 4),
            ("FX", 3),
            ("Dub Delays", 2),
        ],
        "pad_volume": -20,
    },
    {
        "name": "Subtle Build",
        "description": "Adding slight variations, more delays",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 0),
            ("Hi-hats", 0),
            ("Synth Pads", 4),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -20,
    },
    {
        "name": "Atmosphere Enters",
        "description": "Synth pads create depth",
        "clips": [
            ("Kick", 1),
            ("Sub-bass", 1),
            ("Hi-hats", 0),
            ("Synth Pads", 0),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -18,
    },
    {
        "name": "First Movement",
        "description": "Bass starts to breathe",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 2),
            ("Hi-hats", 1),
            ("Synth Pads", 0),
            ("FX", 0),
            ("Dub Delays", 1),
        ],
        "pad_volume": -18,
    },
    # PHASE 2: HYPNOTIC GROOVE (0:16 - 0:32)
    {
        "name": "Hypnotic Lock",
        "description": "Full groove established",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 0),
            ("Hi-hats", 0),
            ("Synth Pads", 0),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -22,
    },
    {
        "name": "Subtle Shift",
        "description": "Bass variation, same pads",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 4),
            ("Hi-hats", 0),
            ("Synth Pads", 0),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -22,
    },
    {
        "name": "Pad Evolution",
        "description": "Chord change to Fm",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 0),
            ("Hi-hats", 0),
            ("Synth Pads", 1),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -20,
    },
    {
        "name": "Deepening",
        "description": "More depth in delays",
        "clips": [
            ("Kick", 1),
            ("Sub-bass", 5),
            ("Hi-hats", 2),
            ("Synth Pads", 1),
            ("FX", 3),
            ("Dub Delays", 1),
        ],
        "pad_volume": -18,
    },
    # PHASE 3: FIRST BUILD (0:32 - 0:48)
    {
        "name": "Gathering Energy",
        "description": "Hi-hats become more active",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 5),
            ("Hi-hats", 1),
            ("Synth Pads", 1),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -20,
    },
    {
        "name": "More Movement",
        "description": "Kick with emphasis",
        "clips": [
            ("Kick", 2),
            ("Sub-bass", 3),
            ("Hi-hats", 1),
            ("Synth Pads", 1),
            ("FX", 1),
            ("Dub Delays", 1),
        ],
        "pad_volume": -18,
    },
    {
        "name": "Peak Intensity",
        "description": "Full elements, high energy",
        "clips": [
            ("Kick", 2),
            ("Sub-bass", 3),
            ("Hi-hats", 4),
            ("Synth Pads", 6),
            ("FX", 4),
            ("Dub Delays", 4),
        ],
        "pad_volume": -16,
    },
    {
        "name": "Holding Pattern",
        "description": "Sustain intensity",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 2),
            ("Hi-hats", 4),
            ("Synth Pads", 6),
            ("FX", 3),
            ("Dub Delays", 1),
        ],
        "pad_volume": -16,
    },
    # PHASE 4: BREAKDOWN (0:48 - 1:04)
    {
        "name": "Thinning Out",
        "description": "Removing elements gradually",
        "clips": [
            ("Kick", 3),
            ("Sub-bass", 0),
            ("Hi-hats", 3),
            ("Synth Pads", 6),
            ("FX", 3),
            ("Dub Delays", 3),
        ],
        "pad_volume": -24,
    },
    {
        "name": "Just Kick and Bass",
        "description": "Rhythmic core",
        "clips": [
            ("Kick", 3),
            ("Sub-bass", 0),
            ("Hi-hats", 3),
            ("Synth Pads", 5),
            ("FX", 3),
            ("Dub Delays", 3),
        ],
        "pad_volume": -999,
    },
    {
        "name": "Space and Atmosphere",
        "description": "Just pads, no rhythm",
        "clips": [
            ("Kick", -1),
            ("Sub-bass", -1),
            ("Hi-hats", -1),
            ("Synth Pads", 7),
            ("FX", 6),
            ("Dub Delays", 6),
        ],
        "pad_volume": -20,
    },
    {
        "name": "Re-emerging",
        "description": "Kick returns, pads evolve",
        "clips": [
            ("Kick", 5),
            ("Sub-bass", 0),
            ("Hi-hats", 2),
            ("Synth Pads", 2),
            ("FX", 6),
            ("Dub Delays", 2),
        ],
        "pad_volume": -18,
    },
    # PHASE 5: SECOND BUILD (1:04 - 1:20)
    {
        "name": "Gradual Return",
        "description": "Building back up slowly",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 6),
            ("Hi-hats", 0),
            ("Synth Pads", 2),
            ("FX", 3),
            ("Dub Delays", 2),
        ],
        "pad_volume": -18,
    },
    {
        "name": "New Energy",
        "description": "Chord change, more active",
        "clips": [
            ("Kick", 1),
            ("Sub-bass", 7),
            ("Hi-hats", 1),
            ("Synth Pads", 3),
            ("FX", 2),
            ("Dub Delays", 2),
        ],
        "pad_volume": -18,
    },
    {
        "name": "Complex Layers",
        "description": "More delays and FX",
        "clips": [
            ("Kick", 4),
            ("Sub-bass", 7),
            ("Hi-hats", 1),
            ("Synth Pads", 3),
            ("FX", 2),
            ("Dub Delays", 4),
        ],
        "pad_volume": -18,
    },
    {
        "name": "Peak Again",
        "description": "Maximum intensity",
        "clips": [
            ("Kick", 6),
            ("Sub-bass", 3),
            ("Hi-hats", 4),
            ("Synth Pads", 6),
            ("FX", 7),
            ("Dub Delays", 5),
        ],
        "pad_volume": -16,
    },
    # PHASE 6: JOURNEY CONTINUES (1:20 - 1:36)
    {
        "name": "Deep Hypnosis",
        "description": "Sustaining groove",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 0),
            ("Hi-hats", 6),
            ("Synth Pads", 0),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -22,
    },
    {
        "name": "Minor Shift",
        "description": "Soft kick, minimal change",
        "clips": [
            ("Kick", 7),
            ("Sub-bass", 0),
            ("Hi-hats", 7),
            ("Synth Pads", 0),
            ("FX", 3),
            ("Dub Delays", 0),
        ],
        "pad_volume": -22,
    },
    {
        "name": "Pad Evolution",
        "description": "Atmospheric shift",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 4),
            ("Hi-hats", 2),
            ("Synth Pads", 1),
            ("FX", 3),
            ("Dub Delays", 2),
        ],
        "pad_volume": -20,
    },
    {
        "name": "Gathering Again",
        "description": "Building energy",
        "clips": [
            ("Kick", 2),
            ("Sub-bass", 2),
            ("Hi-hats", 1),
            ("Synth Pads", 1),
            ("FX", 5),
            ("Dub Delays", 4),
        ],
        "pad_volume": -18,
    },
    # PHASE 7: FINAL PUSH (1:36 - 1:52)
    {
        "name": "Complex Rhythms",
        "description": "Kick syncopation increases",
        "clips": [
            ("Kick", 4),
            ("Sub-bass", 3),
            ("Hi-hats", 4),
            ("Synth Pads", 6),
            ("FX", 7),
            ("Dub Delays", 4),
        ],
        "pad_volume": -16,
    },
    {
        "name": "Maximum Movement",
        "description": "All elements active",
        "clips": [
            ("Kick", 6),
            ("Sub-bass", 7),
            ("Hi-hats", 4),
            ("Synth Pads", 6),
            ("FX", 7),
            ("Dub Delays", 5),
        ],
        "pad_volume": -14,
    },
    {
        "name": "Holding Peak",
        "description": "Sustained intensity",
        "clips": [
            ("Kick", 2),
            ("Sub-bass", 3),
            ("Hi-hats", 4),
            ("Synth Pads", 6),
            ("FX", 0),
            ("Dub Delays", 1),
        ],
        "pad_volume": -16,
    },
    {
        "name": "Beginning Release",
        "description": "Starting to thin out",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 2),
            ("Hi-hats", 1),
            ("Synth Pads", 6),
            ("FX", 3),
            ("Dub Delays", 2),
        ],
        "pad_volume": -20,
    },
    # PHASE 8: WIND DOWN (1:52 - 2:00)
    {
        "name": "Returning to Simplicity",
        "description": "Stripping back to core",
        "clips": [
            ("Kick", 0),
            ("Sub-bass", 0),
            ("Hi-hats", 2),
            ("Synth Pads", 4),
            ("FX", 3),
            ("Dub Delays", 2),
        ],
        "pad_volume": -22,
    },
    {
        "name": "Fading Out",
        "description": "Final breakdown to silence",
        "clips": [
            ("Kick", 3),
            ("Sub-bass", 5),
            ("Hi-hats", 3),
            ("Synth Pads", 5),
            ("FX", 6),
            ("Dub Delays", 6),
        ],
        "pad_volume": -24,
    },
]

# Start playback
print("[START] Starting playback...")
try:
    send_command("start_playback")
    print("[OK] Playback started")
except Exception as e:
    print(f"[ERROR] Could not start playback: {e}")
    s.close()
    sys.exit(1)

# Main automation loop
total_time_minutes = len(sections) * 4
elapsed_minutes = 0

try:
    for section_idx, section in enumerate(sections):
        # Update progress
        progress = get_progress_bar(section_idx, len(sections))
        total_time = f"{elapsed_minutes // 60}:{elapsed_minutes % 60:02d}"
        print(f"\n{progress} Section {section_idx}/29 | Elapsed: {total_time}")
        print("-" * 80)
        print(f"  {section['name']}")
        print(f"  {section['description']}")
        print("-" * 80)

        # Fire clips for this section
        print("  Firing clips...")
        for track_name, clip_idx in section["clips"]:
            if clip_idx >= 0:
                try:
                    send_command(
                        "fire_clip",
                        {
                            "track_index": track_indices[track_name],
                            "clip_index": clip_idx,
                        },
                    )
                    print(f"    [OK] {track_name} -> Clip {clip_idx}")
                except Exception as e:
                    print(f"    [SKIP] {track_name}: {e}")
            else:
                try:
                    send_command(
                        "stop_clip",
                        {"track_index": track_indices[track_name], "clip_index": 0},
                    )
                    print(f"    [STOP] {track_name}")
                except Exception as e:
                    print(f"    [ERROR] {track_name}: {e}")

        # Set track volumes
        print("  Setting track volumes...")
        volume_targets = {
            "Kick": -7,
            "Sub-bass": -5,
            "Hi-hats": -14,
            "Synth Pads": section["pad_volume"],
            "FX": -18,
            "Dub Delays": -17,
        }

        for track_name, vol_db in volume_targets.items():
            if vol_db > -500:
                try:
                    set_track_volume(track_indices[track_name], vol_db)
                    print(f"    [OK] {track_name}: {vol_db} dB")
                except Exception as e:
                    print(f"    [SKIP] {track_name}: {e}")

        # Wait for section duration (4 minutes)
        print(f"  Waiting 4 minutes (240 seconds)...")
        time.sleep(240)

        # Update elapsed time
        elapsed_minutes += 4

    # All sections complete
    print("\n" + "=" * 80)
    print("AUTOMATION COMPLETE!")
    print("=" * 80)
    print(
        f"\nTotal Duration: {elapsed_minutes // 60} hours {(elapsed_minutes % 60):02d} minutes"
    )
    print("All 30 sections have been played")
    print("\nDub beat creation complete!")

except KeyboardInterrupt:
    print("\n\n" + "=" * 80)
    print("AUTOMATION STOPPED BY USER")
    print("=" * 80)
    print(
        f"\nStopped at: {elapsed_minutes // 60} hours {(elapsed_minutes % 60):02d} minutes"
    )
    print(f"Current Section: {min(section_idx, len(sections) - 1)}")

    # Stop playback
    print("\n[STOP] Stopping playback...")
    try:
        send_command("stop_playback")
        print("[OK] Playback stopped")
    except Exception as e:
        print(f"[ERROR] Could not stop playback: {e}")

s.close()
print("\n" + "=" * 80)
print("SCRIPT FINISHED")
print("=" * 80)
