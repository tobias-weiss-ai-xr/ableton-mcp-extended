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


print("=" * 80)
print("CREATING DUB BEAT")
print("=" * 80)
print(f"Tempo: 140 BPM")
print(f"Style: Deep, atmospheric dub with heavy bass and delays")
print("=" * 80)

# Set tempo first
print("\nSetting tempo to 140 BPM...")
send_command("set_tempo", {"tempo": 140.0})
print("   [OK] Tempo set to 140 BPM")

# ============================================================================
# TRACK CREATION
# ============================================================================

# Track 0: Kick (create new track at the end)
print("\n[1/5] Creating Kick track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
kick_track_index = session_info["result"]["track_count"] - 1
send_command("set_track_name", {"track_index": kick_track_index, "name": "Kick"})
print(f"   [OK] Created Kick track (Track {kick_track_index})")

# Track 1: Bass (dub bass is essential)
print("[2/5] Creating Bass track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
bass_track_index = session_info["result"]["track_count"] - 1
send_command("set_track_name", {"track_index": bass_track_index, "name": "Dub Bass"})
print(f"   [OK] Created Bass track (Track {bass_track_index})")

# Track 2: Hi-hats (sparse, atmospheric)
print("[3/5] Creating Hi-hat track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
hihat_track_index = session_info["result"]["track_count"] - 1
send_command("set_track_name", {"track_index": hihat_track_index, "name": "Hi-hats"})
print(f"   [OK] Created Hi-hat track (Track {hihat_track_index})")

# Track 4: Synth Pads (atmosphere)
print("[4/5] Creating Synth Pads track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
pad_track_index = session_info["result"]["track_count"] - 1
send_command("set_track_name", {"track_index": pad_track_index, "name": "Synth Pads"})
print(f"   [OK] Created Synth Pads track (Track {pad_track_index})")

# Track 5: FX (sweeps, impacts)
print("[5/5] Creating FX track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
fx_track_index = session_info["result"]["track_count"] - 1
send_command("set_track_name", {"track_index": fx_track_index, "name": "FX"})
print(f"   [OK] Created FX track (Track {fx_track_index})")

print("\n" + "=" * 80)
print("ALL TRACKS CREATED")
print("=" * 80)

# ============================================================================
# KICK CLIPS - Deep, punchy kick pattern
# ============================================================================
print("\nCreating Kick clips...")

kick_clips = [
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
                "duration": 0.3,
                "velocity": 115,
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
                "duration": 0.3,
                "velocity": 115,
                "mute": False,
            },
        ],
        "name": "Kick Main",
    },
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.4,
                "velocity": 120,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.4,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Dub Style",
    },
]

for clip_idx, clip_data in enumerate(kick_clips):
    send_command(
        "create_clip",
        {"track_index": kick_track_index, "clip_index": clip_idx, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": kick_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": kick_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# BASS CLIPS - Deep, resonant dub bass
# ============================================================================
print("\nCreating Bass clips...")

bass_clips = [
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
        "name": "Bass Drone C",
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
        "name": "Bass Drone F",
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
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Bass Syncopated",
    },
]

for clip_idx, clip_data in enumerate(bass_clips):
    send_command(
        "create_clip",
        {"track_index": bass_track_index, "clip_index": clip_idx, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": bass_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": bass_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# HI-HAT CLIPS - Sparse, offbeat hi-hats
# ============================================================================
print("\nCreating Hi-hat clips...")

hihat_clips = [
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 0.5,
                "duration": 0.1,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 2.5,
                "duration": 0.1,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Hi-hat Offbeat",
    },
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.1,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 3.5,
                "duration": 0.1,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "Hi-hat Minimal",
    },
]

for clip_idx, clip_data in enumerate(hihat_clips):
    send_command(
        "create_clip",
        {"track_index": hihat_track_index, "clip_index": clip_idx, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": hihat_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": hihat_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# SYNTH PAD CLIPS - Dark, atmospheric chords
# ============================================================================
print("\nCreating Synth Pad clips...")

pad_clips = [
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 40,
                "mute": False,
            },
        ],
        "name": "Pad Cm Dark",
    },
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
        ],
        "name": "Pad Single Note",
    },
]

for clip_idx, clip_data in enumerate(pad_clips):
    send_command(
        "create_clip",
        {"track_index": pad_track_index, "clip_index": clip_idx, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": pad_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": pad_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

# ============================================================================
# FX CLIPS - Sweeps and impacts
# ============================================================================
print("\nCreating FX clips...")

fx_clips = [
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
        "name": "FX Sweep",
    },
    {
        "notes": [],
        "name": "FX Silent",
    },
]

for clip_idx, clip_data in enumerate(fx_clips):
    send_command(
        "create_clip",
        {"track_index": fx_track_index, "clip_index": clip_idx, "length": 4.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": fx_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": fx_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Created Clip {clip_idx}: {clip_data['name']}")

print("\n" + "=" * 80)
print("ALL CLIPS CREATED")
print("=" * 80)
print(f"\nSummary:")
print(f"  Track {kick_track_index} (Kick):           {len(kick_clips)} clips")
print(f"  Track {bass_track_index} (Bass):          {len(bass_clips)} clips")
print(f"  Track {hihat_track_index} (Hi-hats):       {len(hihat_clips)} clips")
print(f"  Track {pad_track_index} (Synth Pads):    {len(pad_clips)} clips")
print(f"  Track {fx_track_index} (FX):             {len(fx_clips)} clips")
print(
    f"  Total clips: {len(kick_clips) + len(bass_clips) + len(hihat_clips) + len(pad_clips) + len(fx_clips)} clips"
)

# ============================================================================
# START PLAYBACK
# ============================================================================
print("\n" + "=" * 80)
print("STARTING PLAYBACK")
print("=" * 80)

# Fire clips and start playback
print("\nFiring clips...")
try:
    send_command("fire_clip", {"track_index": kick_track_index, "clip_index": 0})
    print(f"   [OK] Kick clip fired")

    send_command("fire_clip", {"track_index": bass_track_index, "clip_index": 0})
    print(f"   [OK] Bass clip fired")

    send_command("fire_clip", {"track_index": hihat_track_index, "clip_index": 0})
    print(f"   [OK] Hi-hat clip fired")

    send_command("fire_clip", {"track_index": pad_track_index, "clip_index": 0})
    print(f"   [OK] Pad clip fired")

    send_command("fire_clip", {"track_index": fx_track_index, "clip_index": 1})
    print(f"   [OK] FX clip (silent) fired")

    print("\nStarting playback...")
    send_command("start_playback")
    print("[OK] Playback started!")

    print("\n" + "=" * 80)
    print("DUB BEAT COMPLETE!")
    print("=" * 80)
    print("\nYour dub beat is now playing!")
    print(f"Tempo: 140 BPM")
    print(f"Tracks: {5}")
    print(
        f"Clips: {len(kick_clips) + len(bass_clips) + len(hihat_clips) + len(pad_clips) + len(fx_clips)}"
    )
    print("\nNext steps:")
    print("  1. Load instruments on each track in Ableton")
    print("  2. Add reverb and delay effects")
    print("  3. Set up send routing for echo/delay effects")
    print("  4. Adjust mix levels to taste")
    print("  5. Enjoy your dub beat!")
    print()

except Exception as e:
    print(f"\n[ERROR] Could not start playback: {e}")
    print("Please check that Ableton Live is running and the Remote Script is loaded")

s.close()
