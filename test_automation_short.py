import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return response"""
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


def get_track_index_by_name(track_name):
    """Find track index by name (searches all tracks)"""
    session_info = send_command("get_session_info")
    track_count = session_info["result"]["track_count"]

    for i in range(track_count):
        track_info = send_command("get_track_info", {"track_index": i})
        if track_info["result"]["name"] == track_name:
            return i

    raise Exception(f"Track '{track_name}' not found")


print("=" * 80)
print("10-MINUTE DUB REGGAE AUTOMATION (TEST MODE)")
print("=" * 80)
print("Running first 3 sections only (3 minutes)")
print("=" * 80)

# Get track indices
print("\nFinding tracks by name...")
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
track_indices = {}

for name in track_names:
    try:
        track_indices[name] = get_track_index_by_name(name)
        print(f"   [OK] Found {name} at Track {track_indices[name]}")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")
        s.close()
        exit(1)

# Define first 3 sections only
sections = [
    # SECTION 0: Intro
    {
        "name": "Intro",
        "description": "Minimal intro with bass and drums only",
        "clips": [
            ("Kick", 0),
            ("Snare", 0),
            ("Hi-hats", 0),
            ("Dub Bass", 0),
            ("Guitar Chop", 3),
            ("Organ Bubble", 3),
            ("FX", 0),
            ("Dub Delays", 0),
        ],
        "filter_freq": 0.2,
        "reverb_send": 0.3,
        "delay_send": 0.2,
    },
    # SECTION 1: Build
    {
        "name": "Build",
        "description": "Add guitar chop to the groove",
        "clips": [
            ("Kick", 0),
            ("Snare", 0),
            ("Hi-hats", 1),
            ("Dub Bass", 4),
            ("Guitar Chop", 0),
            ("Organ Bubble", 3),
            ("FX", 0),
            ("Dub Delays", 0),
        ],
        "filter_freq": 0.3,
        "reverb_send": 0.4,
        "delay_send": 0.25,
    },
    # SECTION 2: Add Organ
    {
        "name": "Add Organ",
        "description": "Bring in organ bubble",
        "clips": [
            ("Kick", 1),
            ("Snare", 1),
            ("Hi-hats", 0),
            ("Dub Bass", 3),
            ("Guitar Chop", 0),
            ("Organ Bubble", 0),
            ("FX", 1),
            ("Dub Delays", 1),
        ],
        "filter_freq": 0.4,
        "reverb_send": 0.5,
        "delay_send": 0.35,
    },
]

# Start playback
print("\n" + "=" * 80)
print("STARTING AUTOMATED PLAYBACK")
print("=" * 80)

print("Starting playback...")
send_command("start_playback")
time.sleep(0.5)

# Run through sections
try:
    for section_idx, section in enumerate(sections):
        print(f"\n{'=' * 80}")
        print(f"SECTION {section_idx}: {section['name']}")
        print(f"Description: {section['description']}")
        print(f"{'=' * 80}")

        # Fire clips
        for track_name, clip_idx in section["clips"]:
            track_index = track_indices[track_name]

            if clip_idx == 3:
                # Clip index 3 means "Muted" - stop track
                send_command("stop_clip", {"track_index": track_index, "clip_index": 0})
                print(f"   Stop {track_name}")
            else:
                # Fire clip
                send_command(
                    "fire_clip", {"track_index": track_index, "clip_index": clip_idx}
                )
                print(f"   Fire {track_name} clip {clip_idx}")

            time.sleep(0.1)

        # Log automation targets
        print(f"\n   Automation targets:")
        print(f"   - Filter frequency: {section['filter_freq']:.2f}")
        print(f"   - Reverb send: {section['reverb_send']:.2f}")
        print(f"   - Delay send: {section['delay_send']:.2f}")

        # Progress
        progress = (section_idx + 1) / len(sections) * 100
        print(
            f"\n   Progress: {progress:.0f}% ({section_idx + 1}/{len(sections)} sections)"
        )
        print(f"   Playing for 20 seconds...")

        # Wait for 20 seconds (instead of 60)
        try:
            time.sleep(20)
        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt detected!")
            break

    # Completed all sections
    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print(f"\nPlayed {len(sections)} sections over 1 minute")
    print("Full 10-minute version runs all 10 sections")
    print("\nStopping playback in 5 seconds...")

    time.sleep(5)
    send_command("stop_playback")

    print("\n" + "=" * 80)
    print("AUTOMATION FINISHED")
    print("=" * 80)

except KeyboardInterrupt:
    print("\n\n" + "=" * 80)
    print("AUTOMATION STOPPED BY USER")
    print("=" * 80)

    print("\nStopping playback...")
    send_command("stop_playback")

s.close()
