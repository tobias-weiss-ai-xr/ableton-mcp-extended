import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return the response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


def get_track_count():
    """Get current track count"""
    result = send_command("get_session_info")
    return result["result"]["track_count"]


def find_track_by_name(name, max_tracks=20):
    """Find track index by name"""
    for i in range(max_tracks):
        try:
            result = send_command("get_track_info", {"track_index": i})
            if result["result"]["name"] == name:
                return i
        except:
            break
    return None


print("=" * 80)
print("EXPANDED DUB BEAT - MORE VARIANT CLIPS")
print("=" * 80)

track_indices = {}
current_count = get_track_count()

track_names = ["Kick", "Sub-bass", "Hi-hats", "Synth Pads", "FX", "Dub Delays"]

for name in track_names:
    track_index = find_track_by_name(name, max_tracks=20)
    if track_index is not None:
        track_indices[name] = track_index
        print(f"   Found {name} at Track {track_index}")
    else:
        print(f"   [WARNING] {name} not found - will create")
        send_command("create_midi_track", {"index": -1})
        new_count = get_track_count()
        track_index = new_count - 1
        track_indices[name] = track_index
        send_command("set_track_name", {"track_index": track_index, "name": name})
        print(f"   Created {name} at Track {track_index}")

# ============================================================================
# KICK VARIANTS (8 new patterns)
# ============================================================================
print("\nCreating additional Kick variants...")

kick_variants = [
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
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 95,
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
        "name": "Kick Syncopated A",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.3,
                "velocity": 115,
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
                "velocity": 115,
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
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 0.5,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 100,
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
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Kick Offbeat Ghost",
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
                "start_time": 0.25,
                "duration": 0.05,
                "velocity": 90,
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
                "start_time": 1.25,
                "duration": 0.05,
                "velocity": 90,
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
                "start_time": 2.25,
                "duration": 0.05,
                "velocity": 90,
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
                "start_time": 3.25,
                "duration": 0.05,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Kick Rolling",
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
        "name": "Kick Sparse",
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
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
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
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 105,
                "mute": False,
            },
        ],
        "name": "Kick Syncopated B",
    },
    {
        "notes": [],
        "name": "Kick Silent",
    },
]

kick_start_index = 8
for i, clip_data in enumerate(kick_variants):
    clip_index = kick_start_index + i
    send_command(
        "create_clip",
        {"track_index": track_indices["Kick"], "clip_index": clip_index, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Kick"],
            "clip_index": clip_index,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Kick"],
            "clip_index": clip_index,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Kick Clip {clip_index}: {clip_data['name']}")

# ============================================================================
# BASS VARIANTS (8 new patterns)
# ============================================================================
print("\nCreating additional Bass variants...")

bass_variants = [
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 1.0,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 1.0,
                "duration": 1.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 1.0,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass Octave Walk",
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
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass Root to Second",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.5,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.5,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.5,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.5,
                "velocity": 110,
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
            },
        ],
        "name": "Bass F Drone",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 3.0,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Bass Drone to Fill",
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
                "pitch": 36,
                "start_time": 1.5,
                "duration": 0.5,
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
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass Syncopated Stab",
    },
    {
        "notes": [
            {
                "pitch": 43,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass G Drone",
    },
    {
        "notes": [],
        "name": "Bass Silent",
    },
]

bass_start_index = 8
for i, clip_data in enumerate(bass_variants):
    clip_index = bass_start_index + i
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Sub-bass"],
            "clip_index": clip_index,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Sub-bass"],
            "clip_index": clip_index,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Sub-bass"],
            "clip_index": clip_index,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Bass Clip {clip_index}: {clip_data['name']}")

# ============================================================================
# HI-HAT VARIANTS (8 new patterns)
# ============================================================================
print("\nCreating additional Hi-hat variants...")

hihat_variants = [
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
                "pitch": 76,
                "start_time": 1.0,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.0,
                "duration": 0.05,
                "velocity": 65,
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
                "pitch": 76,
                "start_time": 3.0,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.5,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Hi-hat 8ths",
    },
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
                "start_time": 2.0,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.0,
                "duration": 0.05,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat Random",
    },
    {
        "notes": [],
        "name": "Hi-hat Silent",
    },
]

hihat_start_index = 8
for i, clip_data in enumerate(hihat_variants):
    clip_index = hihat_start_index + i
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": clip_index,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": clip_index,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": clip_index,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Hi-hat Clip {clip_index}: {clip_data['name']}")

# ============================================================================
# PAD VARIANTS (8 new patterns)
# ============================================================================
print("\nCreating additional Pad variants...")

pad_variants = [
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
                "pitch": 48,
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Pad Root Only",
    },
    {
        "notes": [],
        "name": "Pad Silent",
    },
]

pad_start_index = 8
for i, clip_data in enumerate(pad_variants):
    clip_index = pad_start_index + i
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Synth Pads"],
            "clip_index": clip_index,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Synth Pads"],
            "clip_index": clip_index,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Synth Pads"],
            "clip_index": clip_index,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Pad Clip {clip_index}: {clip_data['name']}")

# ============================================================================
# FX VARIANTS (8 new patterns)
# ============================================================================
print("\nCreating additional FX variants...")

fx_variants = [
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
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 1.0,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 2.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 3.75,
                "duration": 0.25,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "FX Triple Hit",
    },
    {
        "notes": [],
        "name": "FX Silent",
    },
]

fx_start_index = 8
for i, clip_data in enumerate(fx_variants):
    clip_index = fx_start_index + i
    send_command(
        "create_clip",
        {"track_index": track_indices["FX"], "clip_index": clip_index, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["FX"],
            "clip_index": clip_index,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["FX"],
            "clip_index": clip_index,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] FX Clip {clip_index}: {clip_data['name']}")

# ============================================================================
# DELAY VARIANTS (8 new patterns)
# ============================================================================
print("\nCreating additional Delay variants...")

delay_variants = [
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
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.1,
                "velocity": 85,
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
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Delay Decay",
    },
    {
        "notes": [],
        "name": "Delay Silent",
    },
]

delay_start_index = 8
for i, clip_data in enumerate(delay_variants):
    clip_index = delay_start_index + i
    send_command(
        "create_clip",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": clip_index,
            "length": 4.0,
        },
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": clip_index,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": clip_index,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Delay Clip {clip_index}: {clip_data['name']}")

print("\n" + "=" * 80)
print("VARIANT CLIPS CREATED!")
print("=" * 80)
print(f"\nSummary:")
print(
    f"  Kick:           {len(kick_variants)} new variants (clips {kick_start_index}-{kick_start_index + len(kick_variants) - 1})"
)
print(
    f"  Sub-bass:       {len(bass_variants)} new variants (clips {bass_start_index}-{bass_start_index + len(bass_variants) - 1})"
)
print(
    f"  Hi-hats:        {len(hihat_variants)} new variants (clips {hihat_start_index}-{hihat_start_index + len(hihat_variants) - 1})"
)
print(
    f"  Synth Pads:     {len(pad_variants)} new variants (clips {pad_start_index}-{pad_start_index + len(pad_variants) - 1})"
)
print(
    f"  FX:             {len(fx_variants)} new variants (clips {fx_start_index}-{fx_start_index + len(fx_variants) - 1})"
)
print(
    f"  Dub Delays:     {len(delay_variants)} new variants (clips {delay_start_index}-{delay_start_index + len(delay_variants) - 1})"
)
print(
    f"  Total:          {len(kick_variants) + len(bass_variants) + len(hihat_variants) + len(pad_variants) + len(fx_variants) + len(delay_variants)} new clips"
)
print("\nAll variants created successfully!")

s.close()
