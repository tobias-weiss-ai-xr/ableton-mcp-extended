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
print("ADDING 16-BEAT DUB TECHNO PATTERNS")
print("=" * 80)

session_info = send_command("get_session_info")
kick_track_index = 0
bass_track_index = 1
hihat_track_index = 2
pad_track_index = 3
fx_track_index = 4
delay_track_index = 5

print(f"\nCreating additional 16-beat patterns...")
print(
    f"Starting clip indices: Kick={8}, Bass={8}, Hihats={8}, Pads={8}, FX={8}, Delays={8}"
)

# ============================================================================
# KICK CLIPS - 16-beat minimal patterns
# ============================================================================
print("\nCreating Kick clips (16-beat)...")

kick_clips = [
    # Clip 8: Basic 4/4 extended
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
            {
                "pitch": 36,
                "start_time": 4.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 5.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 9.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 11.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick 16x4/4",
    },
    # Clip 9: Evolving pattern with syncopation
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
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 4.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 5.0,
                "duration": 0.25,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.0,
                "duration": 0.25,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.0,
                "duration": 0.3,
                "velocity": 115,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 9.0,
                "duration": 0.2,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.75,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 11.0,
                "duration": 0.25,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.0,
                "duration": 0.25,
                "velocity": 105,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.75,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.0,
                "duration": 0.25,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Kick Evolving",
    },
    # Clip 10: Half-time pattern
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
                "start_time": 2.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 4.0,
                "duration": 0.3,
                "velocity": 115,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.0,
                "duration": 0.3,
                "velocity": 115,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 0.3,
                "velocity": 115,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Half-time",
    },
    # Clip 11: Sparse with builds
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
            {
                "pitch": 36,
                "start_time": 4.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 9.0,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 11.0,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.0,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.5,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.75,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.0,
                "duration": 0.1,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Kick Buildup",
    },
    # Clip 12: 4/4 with ghost kicks
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
                "start_time": 0.75,
                "duration": 0.1,
                "velocity": 75,
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
                "start_time": 2.75,
                "duration": 0.1,
                "velocity": 75,
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
                "start_time": 4.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 5.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.0,
                "duration": 0.25,
                "velocity": 115,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 9.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 9.75,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 11.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.75,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.0,
                "duration": 0.25,
                "velocity": 110,
                "mute": False,
            },
        ],
        "name": "Kick Ghosts",
    },
]

for clip_idx, clip_data in enumerate(kick_clips):
    idx = clip_idx + 8
    send_command(
        "create_clip",
        {"track_index": kick_track_index, "clip_index": idx, "length": 16.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": kick_track_index,
            "clip_index": idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {"track_index": kick_track_index, "clip_index": idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {idx}: {clip_data['name']}")

# ============================================================================
# SUB-BASS CLIPS - 16-beat hypnotic patterns
# ============================================================================
print("\nCreating Sub-bass clips (16-beat)...")

bass_clips = [
    # Clip 8: Root drone with octave drop halfway
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 8.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 8.0,
                "duration": 8.0,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Bass 16 Drone Drop",
    },
    # Clip 9: Slow evolution pattern
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 4.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 8.0,
                "duration": 4.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass 16 Evolution",
    },
    # Clip 10: Pulsing drone
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
                "start_time": 2.0,
                "duration": 2.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 4.0,
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 2.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.0,
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.0,
                "duration": 2.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 2.0,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass 16 Pulsing",
    },
    # Clip 11: Alternating pattern
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 4.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 12.0,
                "duration": 4.0,
                "velocity": 100,
                "mute": False,
            },
        ],
        "name": "Bass 16 Alternating",
    },
    # Clip 12: Rising then falling
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
            {
                "pitch": 41,
                "start_time": 4.0,
                "duration": 2.0,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 43,
                "start_time": 6.0,
                "duration": 2.0,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 41,
                "start_time": 8.0,
                "duration": 2.0,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 38,
                "start_time": 10.0,
                "duration": 2.0,
                "velocity": 95,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 2.0,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 14.0,
                "duration": 2.0,
                "velocity": 95,
                "mute": False,
            },
        ],
        "name": "Bass 16 Rise Fall",
    },
]

for clip_idx, clip_data in enumerate(bass_clips):
    idx = clip_idx + 8
    send_command(
        "create_clip",
        {"track_index": bass_track_index, "clip_index": idx, "length": 16.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": bass_track_index,
            "clip_index": idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {"track_index": bass_track_index, "clip_index": idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {idx}: {clip_data['name']}")

# ============================================================================
# HI-HAT CLIPS - 16-beat atmospheric patterns
# ============================================================================
print("\nCreating Hi-hat clips (16-beat)...")

hihat_clips = [
    # Clip 8: Extended offbeats
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
            {
                "pitch": 76,
                "start_time": 4.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 5.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 6.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 7.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 8.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 9.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 10.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 11.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 12.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 14.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 15.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat 16 Offbeats",
    },
    # Clip 9: Gradual buildup
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
            {
                "pitch": 76,
                "start_time": 5.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 7.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 9.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 10.5,
                "duration": 0.1,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 11.5,
                "duration": 0.1,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 12.5,
                "duration": 0.1,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.25,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.5,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 14.25,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 14.5,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 14.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 15.25,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 15.5,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 15.75,
                "duration": 0.05,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Hi-hat 16 Buildup",
    },
    # Clip 10: Swung pattern throughout
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
            {
                "pitch": 76,
                "start_time": 4.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 5.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 6.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 7.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 8.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 9.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 10.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 11.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 12.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 14.55,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 15.55,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat 16 Swung",
    },
    # Clip 11: Open hi-hat evolution
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
            {
                "pitch": 77,
                "start_time": 4.0,
                "duration": 0.2,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 4.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 5.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 6.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 7.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 77,
                "start_time": 8.0,
                "duration": 0.3,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 8.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 9.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 10.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 11.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 77,
                "start_time": 12.0,
                "duration": 0.4,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 12.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 14.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 15.5,
                "duration": 0.1,
                "velocity": 65,
                "mute": False,
            },
        ],
        "name": "Hi-hat 16 Open",
    },
    # Clip 12: Triplets for texture
    {
        "notes": [
            {
                "pitch": 76,
                "start_time": 1.5,
                "duration": 0.08,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.67,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 1.83,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 5.5,
                "duration": 0.08,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 5.67,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 5.83,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 9.5,
                "duration": 0.08,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 9.67,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 9.83,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.5,
                "duration": 0.08,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.67,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 76,
                "start_time": 13.83,
                "duration": 0.08,
                "velocity": 55,
                "mute": False,
            },
        ],
        "name": "Hi-hat 16 Triplets",
    },
]

for clip_idx, clip_data in enumerate(hihat_clips):
    idx = clip_idx + 8
    send_command(
        "create_clip",
        {"track_index": hihat_track_index, "clip_index": idx, "length": 16.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": hihat_track_index,
            "clip_index": idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": hihat_track_index,
            "clip_index": idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Created Clip {idx}: {clip_data['name']}")

# ============================================================================
# SYNTH PAD CLIPS - 16-beat atmospheric chords
# ============================================================================
print("\nCreating Synth Pad clips (16-beat)...")

pad_clips = [
    # Clip 8: Slow chord progression
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
            {
                "pitch": 53,
                "start_time": 4.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 56,
                "start_time": 4.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 4.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 8.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 8.0,
                "duration": 4.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 62,
                "start_time": 8.0,
                "duration": 4.0,
                "velocity": 40,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 12.0,
                "duration": 4.0,
                "velocity": 60,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 12.0,
                "duration": 4.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 12.0,
                "duration": 4.0,
                "velocity": 50,
                "mute": False,
            },
        ],
        "name": "Pad 16 Progression",
    },
    # Clip 9: Cm7 drone with subtle movement
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 58,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 40,
                "mute": False,
            },
        ],
        "name": "Pad 16 Cm7 Drone",
    },
    # Clip 10: Evolving chord
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 8.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 0.0,
                "duration": 8.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 0.0,
                "duration": 8.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 8.0,
                "duration": 8.0,
                "velocity": 55,
                "mute": False,
            },
            {
                "pitch": 51,
                "start_time": 8.0,
                "duration": 8.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 55,
                "start_time": 8.0,
                "duration": 8.0,
                "velocity": 45,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 12.0,
                "duration": 4.0,
                "velocity": 40,
                "mute": False,
            },
        ],
        "name": "Pad 16 Evolving",
    },
    # Clip 11: Minimal drone
    {
        "notes": [
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 50,
                "mute": False,
            },
        ],
        "name": "Pad 16 Minimal Drone",
    },
    # Clip 12: High and low drone
    {
        "notes": [
            {
                "pitch": 24,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 35,
                "mute": False,
            },
            {
                "pitch": 48,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 50,
                "mute": False,
            },
            {
                "pitch": 72,
                "start_time": 0.0,
                "duration": 16.0,
                "velocity": 30,
                "mute": False,
            },
        ],
        "name": "Pad 16 Wide Drone",
    },
]

for clip_idx, clip_data in enumerate(pad_clips):
    idx = clip_idx + 8
    send_command(
        "create_clip",
        {"track_index": pad_track_index, "clip_index": idx, "length": 16.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": pad_track_index,
            "clip_index": idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {"track_index": pad_track_index, "clip_index": idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {idx}: {clip_data['name']}")

# ============================================================================
# FX CLIPS - 16-beat dub effects
# ============================================================================
print("\nCreating FX clips (16-beat)...")

fx_clips = [
    # Clip 8: Multiple sweeps
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.5,
                "duration": 0.5,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 7.5,
                "duration": 0.5,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 11.5,
                "duration": 0.5,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 15.5,
                "duration": 0.5,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "FX 16 Sweeps",
    },
    # Clip 9: Long noise build
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 10.0,
                "duration": 6.0,
                "velocity": 60,
                "mute": False,
            },
        ],
        "name": "FX 16 Long Build",
    },
    # Clip 10: Impacts and drops
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 0.0,
                "duration": 0.2,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 7.75,
                "duration": 0.25,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 8.0,
                "duration": 0.2,
                "velocity": 100,
                "mute": False,
            },
            {
                "pitch": 24,
                "start_time": 15.75,
                "duration": 0.25,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "FX 16 Impacts",
    },
    # Clip 11: Reverse cymbals
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 3.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 7.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 11.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 15.0,
                "duration": 1.0,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "FX 16 Reverses",
    },
    # Clip 12: Risers
    {
        "notes": [
            {
                "pitch": 60,
                "start_time": 6.0,
                "duration": 2.0,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 60,
                "start_time": 14.0,
                "duration": 2.0,
                "velocity": 80,
                "mute": False,
            },
        ],
        "name": "FX 16 Risers",
    },
]

for clip_idx, clip_data in enumerate(fx_clips):
    idx = clip_idx + 8
    send_command(
        "create_clip",
        {"track_index": fx_track_index, "clip_index": idx, "length": 16.0},
    )
    send_command(
        "add_notes_to_clip",
        {"track_index": fx_track_index, "clip_index": idx, "notes": clip_data["notes"]},
    )
    send_command(
        "set_clip_name",
        {"track_index": fx_track_index, "clip_index": idx, "name": clip_data["name"]},
    )
    print(f"   [OK] Created Clip {idx}: {clip_data['name']}")

# ============================================================================
# DUB DELAYS CLIPS - 16-beat delay patterns
# ============================================================================
print("\nCreating Dub Delay clips (16-beat)...")

delay_clips = [
    # Clip 8: Regular delays throughout
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
            {
                "pitch": 36,
                "start_time": 4.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 5.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 9.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 11.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay 16 Regular",
    },
    # Clip 9: Echo buildup pattern
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 4.0,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 4.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 5.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 5.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.0,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.5,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.0,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 12.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.5,
                "duration": 0.1,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.0,
                "duration": 0.1,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.5,
                "duration": 0.1,
                "velocity": 90,
                "mute": False,
            },
        ],
        "name": "Delay 16 Echo Build",
    },
    # Clip 10: Stutter delays
    {
        "notes": [
            {
                "pitch": 36,
                "start_time": 2.0,
                "duration": 0.05,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.125,
                "duration": 0.05,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.25,
                "duration": 0.05,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 2.375,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.0,
                "duration": 0.05,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.125,
                "duration": 0.05,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.25,
                "duration": 0.05,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 6.375,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.0,
                "duration": 0.05,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.125,
                "duration": 0.05,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.25,
                "duration": 0.05,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 10.375,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.0,
                "duration": 0.05,
                "velocity": 85,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.125,
                "duration": 0.05,
                "velocity": 80,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.25,
                "duration": 0.05,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 14.375,
                "duration": 0.05,
                "velocity": 70,
                "mute": False,
            },
        ],
        "name": "Delay 16 Stutter",
    },
    # Clip 11: Minimal with echoes
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
            {
                "pitch": 36,
                "start_time": 5.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 9.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 11.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay 16 Minimal",
    },
    # Clip 12: Random delays
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
                "start_time": 4.5,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 7.25,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 8.75,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 11.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 13.0,
                "duration": 0.1,
                "velocity": 70,
                "mute": False,
            },
            {
                "pitch": 36,
                "start_time": 15.5,
                "duration": 0.1,
                "velocity": 75,
                "mute": False,
            },
        ],
        "name": "Delay 16 Random",
    },
]

for clip_idx, clip_data in enumerate(delay_clips):
    idx = clip_idx + 8
    send_command(
        "create_clip",
        {"track_index": delay_track_index, "clip_index": idx, "length": 16.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": delay_track_index,
            "clip_index": idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": delay_track_index,
            "clip_index": idx,
            "name": clip_data["name"],
        },
    )
    print(f"   [OK] Created Clip {idx}: {clip_data['name']}")

print("\n" + "=" * 80)
print("16-BEAT PATTERNS ADDED!")
print("=" * 80)
print(f"\nSummary:")
print(f"  Kick clips:        {len(kick_clips)} new 16-beat patterns (clips 8-12)")
print(f"  Sub-bass clips:    {len(bass_clips)} new 16-beat patterns (clips 8-12)")
print(f"  Hi-hat clips:      {len(hihat_clips)} new 16-beat patterns (clips 8-12)")
print(f"  Pad clips:         {len(pad_clips)} new 16-beat patterns (clips 8-12)")
print(f"  FX clips:          {len(fx_clips)} new 16-beat patterns (clips 8-12)")
print(f"  Delay clips:       {len(delay_clips)} new 16-beat patterns (clips 8-12)")
print(
    f"  Total new clips:   {len(kick_clips) + len(bass_clips) + len(hihat_clips) + len(pad_clips) + len(fx_clips) + len(delay_clips)}"
)
print("\nThese patterns are designed for slow evolution and hypnotic repetition.")

s.close()
