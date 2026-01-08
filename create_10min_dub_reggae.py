import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return the response"""
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
print("CREATING 10-MINUTE DUB REGGAE BEAT")
print("=" * 80)
print(f"Tempo: 75 BPM (classic dub tempo)")
print(f"Duration: 10 minutes")
print(f"Structure: 10 sections x 1 minute each")
print("=" * 80)

# ============================================================================
# STEP 1: SET TEMPO
# ============================================================================

print("\nSetting tempo to 75 BPM...")
send_command("set_tempo", {"tempo": 75.0})
print("   [OK] Tempo set to 75 BPM")

# ============================================================================
# STEP 2: CREATE TRACKS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: CREATING TRACKS")
print("=" * 80)

track_indices = {}
current_count = get_track_count()

# Create 8 main tracks for dub reggae
track_names = [
    "Kick",
    "Snare",
    "Hi-hats",
    "Dub Bass",
    "Guitar Chop",
    "Organ Bubble",
    "FX",
    "Dub Delays",
]

for i, name in enumerate(track_names):
    send_command("create_midi_track", {"index": -1})
    new_count = get_track_count()
    track_index = new_count - 1
    track_indices[name] = track_index
    send_command("set_track_name", {"track_index": track_index, "name": name})
    print(f"   [OK] Created {name} at Track {track_index}")

# Create 2 send tracks
send_command("create_audio_track", {"index": -1})
reverb_track = get_track_count() - 1
track_indices["Reverb Send"] = reverb_track
send_command("set_track_name", {"track_index": reverb_track, "name": "Reverb Send"})
print(f"   [OK] Created Reverb Send at Track {reverb_track}")

send_command("create_audio_track", {"index": -1})
delay_track = get_track_count() - 1
track_indices["Delay Send"] = delay_track
send_command("set_track_name", {"track_index": delay_track, "name": "Delay Send"})
print(f"   [OK] Created Delay Send at Track {delay_track}")

print(f"\nTrack indices: {track_indices}")

# ============================================================================
# STEP 3: CREATE DRUM CLIPS (One Drop Pattern)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: CREATING DRUM CLIPS")
print("=" * 80)

# Kick clips - One Drop style (kick on beat 3)
kick_clips = [
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.3,
                "velocity": 110,
                "mute": False,
            }
        ],
        "name": "Kick One Drop",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.35,
                "velocity": 115,
                "mute": False,
            }
        ],
        "name": "Kick Heavy",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 100,
                "mute": False,
            }
        ],
        "name": "Kick Light",
    },
    {
        "notes": [],
        "name": "Kick Muted",
    },
]

print(f"\nCreating {len(kick_clips)} Kick clips...")
for i, clip in enumerate(kick_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Kick"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": track_indices["Kick"], "clip_index": i, "notes": clip["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": track_indices["Kick"], "clip_index": i, "name": clip["name"]},
    )
    print(f"   [OK] Created Kick clip {i}: {clip['name']}")

# Snare clips - on beats 2 and 4
snare_clips = [
    {
        "notes": [
            {
                "pitch": 38,
                "start_time": 1.0,
                "duration": 0.2,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 3.0,
                "duration": 0.2,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Snare Basic",
    },
    {
        "notes": [
            {
                "pitch": 38,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Snare Accent",
    },
    {
        "notes": [],
        "name": "Snare Muted",
    },
    {
        "notes": [
            {
                "pitch": 38,
                "start_time": 1.0,
                "duration": 0.15,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 1.75,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 3.0,
                "duration": 0.15,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Snare Ghost",
    },
]

print(f"\nCreating {len(snare_clips)} Snare clips...")
for i, clip in enumerate(snare_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Snare"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Snare"],
            "clip_index": i,
            "notes": clip["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {"track_index": track_indices["Snare"], "clip_index": i, "name": clip["name"]},
    )
    print(f"   [OK] Created Snare clip {i}: {clip['name']}")

# Hi-hat clips - offbeat pattern
hihat_clips = [
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.5,
                "duration": 0.1,
                "velocity": 65,
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
        "name": "Hi-hat Offbeat",
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
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 70,
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
                "duration": 0.1,
                "velocity": 70,
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
        "name": "Hi-hat Sparse",
    },
    {
        "notes": [],
        "name": "Hi-hat Muted",
    },
]

print(f"\nCreating {len(hihat_clips)} Hi-hat clips...")
for i, clip in enumerate(hihat_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Hi-hats"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": i,
            "notes": clip["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Hi-hats"],
            "clip_index": i,
            "name": clip["name"],
        },
    )
    print(f"   [OK] Created Hi-hat clip {i}: {clip['name']}")

# ============================================================================
# STEP 4: CREATE BASS CLIPS (Dub Bass Patterns)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: CREATING DUB BASS CLIPS")
print("=" * 80)

bass_clips = [
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 105,
                "mute": False,
            }
        ],
        "name": "Bass Root Drone C",
    },
    {
        "notes": [
            {
                "pitch": 41,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 105,
                "mute": False,
            }
        ],
        "name": "Bass Root Drone F",
    },
    {
        "notes": [
            {
                "pitch": 38,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 105,
                "mute": False,
            }
        ],
        "name": "Bass Root Drone D",
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
                "pitch": 41,
                "start_time": 1.0,
                "duration": 1.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 2.0,
                "duration": 1.0,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass Walking C",
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
                "start_time": 0.75,
                "duration": 0.25,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 2.0,
                "duration": 0.5,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.5,
                "duration": 1.5,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass Syncopated",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.5,
                "velocity": 110,
                "mute": False,
            }
        ],
        "name": "Bass One Drop",
    },
    {
        "notes": [
            {
                "pitch": 34,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            }
        ],
        "name": "Bass Root Drone Bb",
    },
    {
        "notes": [],
        "name": "Bass Muted",
    },
]

print(f"\nCreating {len(bass_clips)} Bass clips...")
for i, clip in enumerate(bass_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Dub Bass"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Dub Bass"],
            "clip_index": i,
            "notes": clip["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Dub Bass"],
            "clip_index": i,
            "name": clip["name"],
        },
    )
    print(f"   [OK] Created Bass clip {i}: {clip['name']}")

# ============================================================================
# STEP 5: CREATE GUITAR CHOP CLIPS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: CREATING GUITAR CHOP CLIPS")
print("=" * 80)

guitar_clips = [
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 0.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "Chop C Major",
    },
    {
        "notes": [
            {
                "pitch": 51,
                "start_time": 0.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 0.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 2.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "Chop F Major",
    },
    {
        "notes": [
            {
                "pitch": 43,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 1.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 3.5,
                "duration": 0.15,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "Chop Fm Sparse",
    },
    {
        "notes": [],
        "name": "Chop Muted",
    },
]

print(f"\nCreating {len(guitar_clips)} Guitar clips...")
for i, clip in enumerate(guitar_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Guitar Chop"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Guitar Chop"],
            "clip_index": i,
            "notes": clip["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Guitar Chop"],
            "clip_index": i,
            "name": clip["name"],
        },
    )
    print(f"   [OK] Created Guitar clip {i}: {clip['name']}")

# ============================================================================
# STEP 6: CREATE ORGAN BUBBLE CLIPS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: CREATING ORGAN BUBBLE CLIPS")
print("=" * 80)

organ_clips = [
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 63,
                "start_time": 0.5,
                "duration": 0.25,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 63,
                "start_time": 1.5,
                "duration": 0.25,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 63,
                "start_time": 2.5,
                "duration": 0.25,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 63,
                "start_time": 3.5,
                "duration": 0.25,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Organ Shuffle",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.5,
                "duration": 0.5,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 63,
                "start_time": 1.5,
                "duration": 0.5,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 2.5,
                "duration": 0.5,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 63,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Organ Stab",
    },
    {
        "notes": [
            {
                "pitch": 55,
                "start_time": 1.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Organ Low",
    },
    {
        "notes": [],
        "name": "Organ Muted",
    },
]

print(f"\nCreating {len(organ_clips)} Organ clips...")
for i, clip in enumerate(organ_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Organ Bubble"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Organ Bubble"],
            "clip_index": i,
            "notes": clip["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Organ Bubble"],
            "clip_index": i,
            "name": clip["name"],
        },
    )
    print(f"   [OK] Created Organ clip {i}: {clip['name']}")

# ============================================================================
# STEP 7: CREATE FX CLIPS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 6: CREATING FX CLIPS")
print("=" * 80)

fx_clips = [
    {
        "notes": [],
        "name": "FX Muted",
    },
    {
        "notes": [
            {
                "pitch": 30,
                "start_time": 0.0,
                "duration": 0.5,
                "velocity": 80,
                "mute": False,
            }
        ],
        "name": "FX Sub Hit",
    },
    {
        "notes": [
            {
                "pitch": 50,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 75,
                "mute": False,
            }
        ],
        "name": "FX Cymbal",
    },
    {
        "notes": [
            {
                "pitch": 40,
                "start_time": 2.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            }
        ],
        "name": "FX Noise",
    },
]

print(f"\nCreating {len(fx_clips)} FX clips...")
for i, clip in enumerate(fx_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["FX"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": track_indices["FX"], "clip_index": i, "notes": clip["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": track_indices["FX"], "clip_index": i, "name": clip["name"]},
    )
    print(f"   [OK] Created FX clip {i}: {clip['name']}")

# ============================================================================
# STEP 8: CREATE DUB DELAYS CLIPS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 7: CREATING DUB DELAYS CLIPS")
print("=" * 80)

delay_clips = [
    {
        "notes": [],
        "name": "Delay Muted",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 2.0,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Delay Echo",
    },
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 0.5,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 1.0,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 2.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay Active",
    },
]

print(f"\nCreating {len(delay_clips)} Delay clips...")
for i, clip in enumerate(delay_clips):
    send_command(
        "create_clip",
        {"track_index": track_indices["Dub Delays"], "clip_index": i, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": i,
            "notes": clip["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": track_indices["Dub Delays"],
            "clip_index": i,
            "name": clip["name"],
        },
    )
    print(f"   [OK] Created Delay clip {i}: {clip['name']}")

# ============================================================================
# STEP 9: DEFINE SECTIONS (10 minutes total, 1 minute per section)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 8: DEFINING ARRANGEMENT SECTIONS")
print("=" * 80)

sections = [
    # SECTION 0: Intro (0:00-1:00) - Minimal bass + drums
    {
        "name": "Intro",
        "description": "Minimal intro with bass and drums only",
        "clips": [
            (track_indices["Kick"], 0),  # Kick One Drop
            (track_indices["Snare"], 0),  # Snare Basic
            (track_indices["Hi-hats"], 0),  # Hi-hat Offbeat
            (track_indices["Dub Bass"], 0),  # Bass Root Drone C
            (track_indices["Guitar Chop"], 3),  # Muted
            (track_indices["Organ Bubble"], 3),  # Muted
            (track_indices["FX"], 0),  # Muted
            (track_indices["Dub Delays"], 0),  # Muted
        ],
        "filter_freq": 0.2,
        "reverb_send": 0.3,
        "delay_send": 0.2,
    },
    # SECTION 1: Build (1:00-2:00) - Add guitar
    {
        "name": "Build",
        "description": "Add guitar chop to the groove",
        "clips": [
            (track_indices["Kick"], 0),  # Kick One Drop
            (track_indices["Snare"], 0),  # Snare Basic
            (track_indices["Hi-hats"], 1),  # Hi-hat Active
            (track_indices["Dub Bass"], 4),  # Bass Syncopated
            (track_indices["Guitar Chop"], 0),  # Chop C Major
            (track_indices["Organ Bubble"], 3),  # Muted
            (track_indices["FX"], 0),  # Muted
            (track_indices["Dub Delays"], 0),  # Muted
        ],
        "filter_freq": 0.3,
        "reverb_send": 0.4,
        "delay_send": 0.25,
    },
    # SECTION 2: Add Organ (2:00-3:00)
    {
        "name": "Add Organ",
        "description": "Bring in organ bubble",
        "clips": [
            (track_indices["Kick"], 1),  # Kick Heavy
            (track_indices["Snare"], 1),  # Snare Accent
            (track_indices["Hi-hats"], 0),  # Hi-hat Offbeat
            (track_indices["Dub Bass"], 3),  # Bass Walking C
            (track_indices["Guitar Chop"], 0),  # Chop C Major
            (track_indices["Organ Bubble"], 0),  # Organ Shuffle
            (track_indices["FX"], 1),  # FX Sub Hit
            (track_indices["Dub Delays"], 1),  # Delay Echo
        ],
        "filter_freq": 0.4,
        "reverb_send": 0.5,
        "delay_send": 0.35,
    },
    # SECTION 3: Peak 1 (3:00-4:00) - Full groove
    {
        "name": "Peak 1",
        "description": "Full groove with all elements",
        "clips": [
            (track_indices["Kick"], 0),  # Kick One Drop
            (track_indices["Snare"], 3),  # Snare Ghost
            (track_indices["Hi-hats"], 1),  # Hi-hat Active
            (track_indices["Dub Bass"], 4),  # Bass Syncopated
            (track_indices["Guitar Chop"], 1),  # Chop F Major
            (track_indices["Organ Bubble"], 1),  # Organ Stab
            (track_indices["FX"], 2),  # FX Cymbal
            (track_indices["Dub Delays"], 2),  # Delay Active
        ],
        "filter_freq": 0.7,
        "reverb_send": 0.6,
        "delay_send": 0.5,
    },
    # SECTION 4: Breakdown (4:00-5:00) - Strip down
    {
        "name": "Breakdown",
        "description": "Strip down to bass and drums",
        "clips": [
            (track_indices["Kick"], 2),  # Kick Light
            (track_indices["Snare"], 2),  # Muted
            (track_indices["Hi-hats"], 2),  # Hi-hat Sparse
            (track_indices["Dub Bass"], 1),  # Bass Root Drone F
            (track_indices["Guitar Chop"], 3),  # Muted
            (track_indices["Organ Bubble"], 3),  # Muted
            (track_indices["FX"], 0),  # Muted
            (track_indices["Dub Delays"], 0),  # Muted
        ],
        "filter_freq": 0.25,
        "reverb_send": 0.6,
        "delay_send": 0.2,
    },
    # SECTION 5: Rebuild (5:00-6:00)
    {
        "name": "Rebuild",
        "description": "Gradually bring elements back",
        "clips": [
            (track_indices["Kick"], 0),  # Kick One Drop
            (track_indices["Snare"], 0),  # Snare Basic
            (track_indices["Hi-hats"], 0),  # Hi-hat Offbeat
            (track_indices["Dub Bass"], 5),  # Bass One Drop
            (track_indices["Guitar Chop"], 2),  # Chop Fm Sparse
            (track_indices["Organ Bubble"], 2),  # Organ Low
            (track_indices["FX"], 1),  # FX Sub Hit
            (track_indices["Dub Delays"], 1),  # Delay Echo
        ],
        "filter_freq": 0.4,
        "reverb_send": 0.4,
        "delay_send": 0.3,
    },
    # SECTION 6: Peak 2 (6:00-7:00) - Intense
    {
        "name": "Peak 2",
        "description": "Intense peak with all effects",
        "clips": [
            (track_indices["Kick"], 1),  # Kick Heavy
            (track_indices["Snare"], 3),  # Snare Ghost
            (track_indices["Hi-hats"], 1),  # Hi-hat Active
            (track_indices["Dub Bass"], 4),  # Bass Syncopated
            (track_indices["Guitar Chop"], 0),  # Chop C Major
            (track_indices["Organ Bubble"], 0),  # Organ Shuffle
            (track_indices["FX"], 3),  # FX Noise
            (track_indices["Dub Delays"], 2),  # Delay Active
        ],
        "filter_freq": 0.8,
        "reverb_send": 0.65,
        "delay_send": 0.55,
    },
    # SECTION 7: Variation (7:00-8:00) - Change key
    {
        "name": "Variation",
        "description": "Change key to F minor",
        "clips": [
            (track_indices["Kick"], 0),  # Kick One Drop
            (track_indices["Snare"], 1),  # Snare Accent
            (track_indices["Hi-hats"], 0),  # Hi-hat Offbeat
            (track_indices["Dub Bass"], 1),  # Bass Root Drone F
            (track_indices["Guitar Chop"], 2),  # Chop Fm Sparse
            (track_indices["Organ Bubble"], 2),  # Organ Low
            (track_indices["FX"], 1),  # FX Sub Hit
            (track_indices["Dub Delays"], 1),  # Delay Echo
        ],
        "filter_freq": 0.5,
        "reverb_send": 0.5,
        "delay_send": 0.4,
    },
    # SECTION 8: Peak 3 (8:00-9:00) - Full intensity
    {
        "name": "Peak 3",
        "description": "Maximum intensity, all elements",
        "clips": [
            (track_indices["Kick"], 1),  # Kick Heavy
            (track_indices["Snare"], 3),  # Snare Ghost
            (track_indices["Hi-hats"], 1),  # Hi-hat Active
            (track_indices["Dub Bass"], 4),  # Bass Syncopated
            (track_indices["Guitar Chop"], 1),  # Chop F Major
            (track_indices["Organ Bubble"], 1),  # Organ Stab
            (track_indices["FX"], 2),  # FX Cymbal
            (track_indices["Dub Delays"], 2),  # Delay Active
        ],
        "filter_freq": 0.85,
        "reverb_send": 0.7,
        "delay_send": 0.6,
    },
    # SECTION 9: Wind Down (9:00-10:00) - Fade out
    {
        "name": "Wind Down",
        "description": "Gradual fade to minimal",
        "clips": [
            (track_indices["Kick"], 2),  # Kick Light
            (track_indices["Snare"], 2),  # Muted
            (track_indices["Hi-hats"], 2),  # Hi-hat Sparse
            (track_indices["Dub Bass"], 7),  # Muted
            (track_indices["Guitar Chop"], 3),  # Muted
            (track_indices["Organ Bubble"], 3),  # Muted
            (track_indices["FX"], 0),  # Muted
            (track_indices["Dub Delays"], 0),  # Muted
        ],
        "filter_freq": 0.2,
        "reverb_send": 0.8,
        "delay_send": 0.3,
    },
]

print(f"\nDefined {len(sections)} sections for 10-minute arrangement")

# ============================================================================
# STEP 10: SET UP SEND ROUTING
# ============================================================================

print("\n" + "=" * 80)
print("STEP 9: SETTING UP SEND ROUTING")
print("=" * 80)

# Set up sends from instrument tracks to delay and reverb
# Note: This would require knowing send indices, which may vary
print("\n[NOTE] Please manually set up send routing in Ableton:")
print("  - All tracks → Delay Send (send A)")
print("  - All tracks → Reverb Send (send B)")
print("  - Suggested send levels: 20-40% for Delay, 15-35% for Reverb")

# ============================================================================
# STEP 11: SET BASE TRACK VOLUMES
# ============================================================================

print("\n" + "=" * 80)
print("STEP 10: SETTING BASE TRACK VOLUMES")
print("=" * 80)

# Convert dB to normalized (0.0-1.0)
# -6dB ≈ 0.75, -12dB ≈ 0.5, -18dB ≈ 0.35
volumes = {
    "Kick": 0.75,  # -6dB
    "Snare": 0.60,  # -9dB
    "Hi-hats": 0.40,  # -15dB
    "Dub Bass": 0.85,  # -4dB (prominent)
    "Guitar Chop": 0.55,  # -10dB
    "Organ Bubble": 0.50,  # -12dB
    "FX": 0.45,  # -14dB
    "Dub Delays": 0.60,  # -9dB
}

for track_name, volume in volumes.items():
    send_command(
        "set_track_volume", {"track_index": track_indices[track_name], "volume": volume}
    )
    print(f"   [OK] Set {track_name} volume to {volume:.2f}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)
print("\nWhat was created:")
print(f"  - {len(track_indices)} tracks (8 MIDI + 2 Send)")
print(f"  - {len(kick_clips)} Kick clips")
print(f"  - {len(snare_clips)} Snare clips")
print(f"  - {len(hihat_clips)} Hi-hat clips")
print(f"  - {len(bass_clips)} Bass clips")
print(f"  - {len(guitar_clips)} Guitar clips")
print(f"  - {len(organ_clips)} Organ clips")
print(f"  - {len(fx_clips)} FX clips")
print(f"  - {len(delay_clips)} Delay clips")
print(f"  - {len(sections)} arrangement sections (10 minutes)")
print("\nNext steps:")
print("  1. Load instruments on each track (Kick, Bass, Guitar, Organ)")
print("  2. Add effects (Delay on Delay Send, Reverb on Reverb Send)")
print("  3. Set up send routing from all tracks to send tracks")
print("  4. Run automation script to play through sections")
print("=" * 80)

# ============================================================================
# OPTIONAL: AUTOMATION PLAYBACK SCRIPT
# ============================================================================

print("\n" + "=" * 80)
print("OPTIONAL: RUNNING AUTOMATION")
print("=" * 80)
print("\nTo run the 10-minute automation, create a separate script that:")
print("  1. Starts playback")
print("  2. Loops through sections")
print("  3. Fires clips for each section")
print("  4. Automates filter frequency (0.0-1.0 on synth tracks)")
print("  5. Automates send levels (delay and reverb)")
print("  6. Waits 1 minute per section (15 seconds at 75 BPM per 4-bar clip)")
print("\nTotal duration: 10 minutes")
print("=" * 80)

s.close()
