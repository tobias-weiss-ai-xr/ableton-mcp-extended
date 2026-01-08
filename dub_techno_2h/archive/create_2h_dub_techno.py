import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


print("=" * 80)
print("CREATING 2-HOUR DUB TECHNOPO TRACK")
print("=" * 80)
print(f"Tempo: 126 BPM")
print(f"Duration: 2 hours (120 minutes)")
print(f"Structure: 30 sections x 4 minutes each")
print("=" * 80)

# ============================================================================
# CLEAR SESSION - Delete all existing tracks
# ============================================================================
print("\n[1/7] Clearing session - deleting all existing tracks...")
result = send_command("delete_all_tracks")
deleted_count = result.get("result", {}).get("deleted_count", 0)
print(f"   [OK] Deleted {deleted_count} tracks")
time.sleep(0.5)

# Set tempo
print("\n[2/7] Setting tempo to 126 BPM...")
send_command("set_tempo", {"tempo": 126.0})
print("   [OK] Tempo set to 126 BPM")
time.sleep(0.5)

# ============================================================================
# TRACK CREATION - Start fresh from index 0
# ============================================================================

# Track 0: Kick
print("\n[3/7] Creating Kick track...")
send_command("create_midi_track", {"index": 0})
send_command("set_track_name", {"track_index": 0, "name": "Kick"})
print("   [OK] Created Kick track (Track 0)")

# Track 1: Sub-bass
print("[4/7] Creating Sub-bass track...")
send_command("create_midi_track", {"index": 1})
send_command("set_track_name", {"track_index": 1, "name": "Sub-bass"})
print("   [OK] Created Sub-bass track (Track 1)")

# Track 2: Hi-hats
print("[5/7] Creating Hi-hat track...")
send_command("create_midi_track", {"index": 2})
send_command("set_track_name", {"track_index": 2, "name": "Hi-hats"})
print("   [OK] Created Hi-hat track (Track 2)")

# Track 3: Synth Pads
print("[6/7] Creating Synth Pads track...")
send_command("create_midi_track", {"index": 3})
send_command("set_track_name", {"track_index": 3, "name": "Synth Pads"})
print("   [OK] Created Synth Pads track (Track 3)")

# Track 4: FX
print("[7/7] Creating FX track...")
send_command("create_midi_track", {"index": 4})
send_command("set_track_name", {"track_index": 4, "name": "FX"})
print("   [OK] Created FX track (Track 4)")

# Track 5: Dub Delays (send track)
print("       Creating Dub Delays track...")
send_command("create_midi_track", {"index": 5})
send_command("set_track_name", {"track_index": 5, "name": "Dub Delays"})
print("   [OK] Created Dub Delays track (Track 5)")

print("\n" + "=" * 80)
print("ALL TRACKS CREATED")
print("=" * 80)

# ============================================================================
# KICK CLIPS - Minimal 4/4 patterns
# ============================================================================
print("\nCreating Kick clips (Track 0)...")

kick_clips = [
    # Clip 0: Basic 4/4 (main pattern)
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
    # Clip 1: Slight swing
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 115,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 115,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 105,
                "mute": False,
            },
        ],
        "name": "Kick Swing",
    },
    # Clip 2: Extra emphasis on beat 1
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
    # Clip 3: Minimal (every other beat)
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
    # Clip 4: With offbeat kick
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
    # Clip 5: Very sparse
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
    # Clip 6: Rolling buildup
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
    # Clip 7: Basic but softer
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
]

for clip_idx, clip_data in enumerate(kick_clips):
    send_command(
        "create_clip", {"track_index": 0, "clip_index": clip_idx, "length": 4.0}
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": 0, "clip_index": clip_idx, "notes": clip_data["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": 0, "clip_index": clip_idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# SUB-BASS CLIPS - Deep, hypnotic bass patterns
# ============================================================================
print("\nCreating Sub-bass clips (Track 1)...")

bass_clips = [
    # Clip 0: Root drone (C2)
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass Root Drone",
    },
    # Clip 1: Root drone with octave drop
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
    # Clip 2: Syncopated pattern
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
    # Clip 3: Rising pattern
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
    # Clip 4: Minimal staccato
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
    # Clip 5: F drone (F2)
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
    # Clip 6: G drone (G2)
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
    # Clip 7: Alternating notes
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
        "create_clip", {"track_index": 1, "clip_index": clip_idx, "length": 4.0}
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": 1, "clip_index": clip_idx, "notes": clip_data["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": 1, "clip_index": clip_idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# HI-HAT CLIPS - Sparse, atmospheric
# ============================================================================
print("\nCreating Hi-hat clips (Track 2)...")

hihat_clips = [
    # Clip 0: Closed hi-hat on offbeats
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
    # Clip 1: More active
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
    # Clip 2: Very minimal
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
    # Clip 3: No hi-hats
    {"notes": [], "name": "Hi-hat Silent"},
    # Clip 4: 16th notes for buildups
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
    # Clip 5: Open hi-hat accents
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
    # Clip 6: Swung pattern
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
    # Clip 7: Only on 2 and 4
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
        "create_clip", {"track_index": 2, "clip_index": clip_idx, "length": 4.0}
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": 2, "clip_index": clip_idx, "notes": clip_data["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": 2, "clip_index": clip_idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# SYNTH PADS CLIPS - Atmospheric, evolving
# ============================================================================
print("\nCreating Synth Pads clips (Track 3)...")

pad_clips = [
    # Clip 0: C minor chord (C3, Eb3, G3)
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
    # Clip 1: F minor chord (F3, Ab3, C4)
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
    # Clip 2: G minor chord (G3, Bb3, D4)
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
    # Clip 3: Eb major (Eb3, G3, Bb3)
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
    # Clip 4: Very minimal (just root)
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Pad Minimal",
    },
    # Clip 5: No pad
    {"notes": [], "name": "Pad Silent"},
    # Clip 6: Evolving chord (Cm7)
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
    # Clip 7: High drone for atmosphere
    {
        "notes": [
            {
                "pitch": 72,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 35,
                "mute": False,
            },
        ],
        "name": "Pad High Drone",
    },
]

for clip_idx, clip_data in enumerate(pad_clips):
    send_command(
        "create_clip", {"track_index": 3, "clip_index": clip_idx, "length": 4.0}
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": 3, "clip_index": clip_idx, "notes": clip_data["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": 3, "clip_index": clip_idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# FX CLIPS - Dub effects, sweeps
# ============================================================================
print("\nCreating FX clips (Track 4)...")

fx_clips = [
    # Clip 0: Noise sweep
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 80,
                "mute": False,
            },
        ],
        "name": "FX Sweep",
    },
    # Clip 1: Impact
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 0.2,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "FX Impact",
    },
    # Clip 2: Reverse cymbal
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "FX Reverse",
    },
    # Clip 3: No FX
    {"notes": [], "name": "FX Silent"},
    # Clip 4: Sub drop
    {
        "notes": [
            {
                "pitch": 24,
                "start_time": 3.75,
                "duration": 0.25,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "FX Sub Drop",
    },
    # Clip 5: Noise build
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "FX Noise Build",
    },
    # Clip 6: Reverb tail
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 50,
                "mute": False,
            },
        ],
        "name": "FX Reverb Tail",
    },
    # Clip 7: Riser
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 2.5,
                "duration": 1.5,
                "velocity": 85,
                "mute": False,
            },
        ],
        "name": "FX Riser",
    },
]

for clip_idx, clip_data in enumerate(fx_clips):
    send_command(
        "create_clip", {"track_index": 4, "clip_index": clip_idx, "length": 4.0}
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": 4, "clip_index": clip_idx, "notes": clip_data["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": 4, "clip_index": clip_idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# DUB DELAYS CLIPS - Send track for delays
# ============================================================================
print("\nCreating Dub Delays clips (Track 5)...")

delay_clips = [
    # Clip 0: Regular delays
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
    # Clip 1: More active delays
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
    # Clip 2: Minimal delays
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
    # Clip 3: No delays
    {"notes": [], "name": "Delay Silent"},
    # Clip 4: Echo build
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
    # Clip 5: Stutter delays
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
    # Clip 6: Long delay tail
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Delay Tail",
    },
    # Clip 7: Random delays
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
        "create_clip", {"track_index": 5, "clip_index": clip_idx, "length": 4.0}
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": 5, "clip_index": clip_idx, "notes": clip_data["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": 5, "clip_index": clip_idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

print("\n" + "=" * 80)
print("ALL CLIPS CREATED")
print("=" * 80)
print(f"\nSummary:")
print(f"  Track 0 (Kick):        {len(kick_clips)} clips")
print(f"  Track 1 (Sub-bass):    {len(bass_clips)} clips")
print(f"  Track 2 (Hi-hats):     {len(hihat_clips)} clips")
print(f"  Track 3 (Synth Pads):  {len(pad_clips)} clips")
print(f"  Track 4 (FX):          {len(fx_clips)} clips")
print(f"  Track 5 (Dub Delays):  {len(delay_clips)} clips")
print(
    f"  Total clips:           {len(kick_clips) + len(bass_clips) + len(hihat_clips) + len(pad_clips) + len(fx_clips) + len(delay_clips)} clips"
)

print("\n" + "=" * 80)
print("CREATION COMPLETE!")
print("=" * 80)
print("\nNext steps:")
print("  1. Load instruments and sounds on each track")
print("  2. Add effects (reverb, delay, filters)")
print("  3. Run arrangement script to create 2-hour structure")
print("  4. Start playback and enjoy your dub techno journey!")
print("\n")

s.close()
