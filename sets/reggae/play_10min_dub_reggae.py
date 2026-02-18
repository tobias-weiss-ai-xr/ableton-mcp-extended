import socket
import json
import time
import sys

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


def get_track_count():
    """Get current track count"""
    result = send_command("get_session_info")
    return result["result"]["track_count"]


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
print("10-MINUTE DUB REGGAE AUTOMATION")
print("=" * 80)
print(f"Tempo: 75 BPM")
print(f"Duration: 10 minutes")
print(f"Sections: 10 sections x 1 minute each")
print("=" * 80)

# ============================================================================
# GET TRACK INDICES BY NAME
# ============================================================================

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
        print("\nPlease run create_10min_dub_reggae.py first to create the tracks!")
        s.close()
        sys.exit(1)

# ============================================================================
# DEFINE SECTIONS (same as in creation script)
# ============================================================================

print("\n" + "=" * 80)
print("LOADING SECTIONS")
print("=" * 80)

sections = [
    # SECTION 0: Intro (0:00-1:00)
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
    # SECTION 1: Build (1:00-2:00)
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
    # SECTION 2: Add Organ (2:00-3:00)
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
    # SECTION 3: Peak 1 (3:00-4:00)
    {
        "name": "Peak 1",
        "description": "Full groove with all elements",
        "clips": [
            ("Kick", 0),
            ("Snare", 3),
            ("Hi-hats", 1),
            ("Dub Bass", 4),
            ("Guitar Chop", 1),
            ("Organ Bubble", 1),
            ("FX", 2),
            ("Dub Delays", 2),
        ],
        "filter_freq": 0.7,
        "reverb_send": 0.6,
        "delay_send": 0.5,
    },
    # SECTION 4: Breakdown (4:00-5:00)
    {
        "name": "Breakdown",
        "description": "Strip down to bass and drums",
        "clips": [
            ("Kick", 2),
            ("Snare", 2),
            ("Hi-hats", 2),
            ("Dub Bass", 1),
            ("Guitar Chop", 3),
            ("Organ Bubble", 3),
            ("FX", 0),
            ("Dub Delays", 0),
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
            ("Kick", 0),
            ("Snare", 0),
            ("Hi-hats", 0),
            ("Dub Bass", 5),
            ("Guitar Chop", 2),
            ("Organ Bubble", 2),
            ("FX", 1),
            ("Dub Delays", 1),
        ],
        "filter_freq": 0.4,
        "reverb_send": 0.4,
        "delay_send": 0.3,
    },
    # SECTION 6: Peak 2 (6:00-7:00)
    {
        "name": "Peak 2",
        "description": "Intense peak with all effects",
        "clips": [
            ("Kick", 1),
            ("Snare", 3),
            ("Hi-hats", 1),
            ("Dub Bass", 4),
            ("Guitar Chop", 0),
            ("Organ Bubble", 0),
            ("FX", 3),
            ("Dub Delays", 2),
        ],
        "filter_freq": 0.8,
        "reverb_send": 0.65,
        "delay_send": 0.55,
    },
    # SECTION 7: Variation (7:00-8:00)
    {
        "name": "Variation",
        "description": "Change key to F minor",
        "clips": [
            ("Kick", 0),
            ("Snare", 1),
            ("Hi-hats", 0),
            ("Dub Bass", 1),
            ("Guitar Chop", 2),
            ("Organ Bubble", 2),
            ("FX", 1),
            ("Dub Delays", 1),
        ],
        "filter_freq": 0.5,
        "reverb_send": 0.5,
        "delay_send": 0.4,
    },
    # SECTION 8: Peak 3 (8:00-9:00)
    {
        "name": "Peak 3",
        "description": "Maximum intensity, all elements",
        "clips": [
            ("Kick", 1),
            ("Snare", 3),
            ("Hi-hats", 1),
            ("Dub Bass", 4),
            ("Guitar Chop", 1),
            ("Organ Bubble", 1),
            ("FX", 2),
            ("Dub Delays", 2),
        ],
        "filter_freq": 0.85,
        "reverb_send": 0.7,
        "delay_send": 0.6,
    },
    # SECTION 9: Wind Down (9:00-10:00)
    {
        "name": "Wind Down",
        "description": "Gradual fade to minimal",
        "clips": [
            ("Kick", 2),
            ("Snare", 2),
            ("Hi-hats", 2),
            ("Dub Bass", 7),
            ("Guitar Chop", 3),
            ("Organ Bubble", 3),
            ("FX", 0),
            ("Dub Delays", 0),
        ],
        "filter_freq": 0.2,
        "reverb_send": 0.8,
        "delay_send": 0.3,
    },
]

print(f"\nLoaded {len(sections)} sections")

# ============================================================================
# FUNCTION TO FIRE CLIPS FOR A SECTION
# ============================================================================


def fire_section_clips(section_idx, section):
    """Fire all clips for a section"""
    print(f"\n[{section_idx}] {section['name']}: {section['description']}")

    # Fire clips for each track
    for track_name, clip_idx in section["clips"]:
        track_index = track_indices[track_name]

        if clip_idx == -1:
            # Stop the track
            send_command("stop_clip", {"track_index": track_index, "clip_index": 0})
            print(f"   Stop {track_name}")
        else:
            # Fire the clip
            send_command(
                "fire_clip", {"track_index": track_index, "clip_index": clip_idx}
            )
            print(f"   Fire {track_name} clip {clip_idx}")

        time.sleep(0.05)  # Small delay between clip fires

    # Log automation targets (would need device indices to actually automate)
    print(f"\n   Automation targets:")
    print(
        f"   - Filter frequency: {section['filter_freq']:.2f} (manual adjustment required)"
    )
    print(
        f"   - Reverb send: {section['reverb_send']:.2f} (manual adjustment required)"
    )
    print(f"   - Delay send: {section['delay_send']:.2f} (manual adjustment required)")


# ============================================================================
# START PLAYBACK
# ============================================================================

print("\n" + "=" * 80)
print("STARTING AUTOMATED PLAYBACK")
print("=" * 80)
print("\nPress Ctrl+C to stop early")
print("")

# Start playback
print("Starting playback...")
send_command("start_playback")
time.sleep(0.5)

# ============================================================================
# MAIN LOOP THROUGH SECTIONS
# ============================================================================

try:
    for section_idx, section in enumerate(sections):
        # Fire clips for this section
        fire_section_clips(section_idx, section)

        # Calculate section end time (in minutes)
        section_end = (section_idx + 1) * 1.0

        # Progress bar
        progress = (section_idx + 1) / len(sections) * 100
        print(
            f"\n   Progress: {progress:.0f}% ({section_idx + 1}/{len(sections)} sections)"
        )
        print(f"   Time: {section_end:.0f} min / 10 min")
        print(f"   Waiting 60 seconds...")

        # Wait for section duration (60 seconds at 75 BPM = 15 four-bar clips)
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt detected!")
            break

except KeyboardInterrupt:
    print("\n\n" + "=" * 80)
    print("AUTOMATION STOPPED BY USER")
    print("=" * 80)
else:
    # Completed all sections
    print("\n" + "=" * 80)
    print("AUTOMATION COMPLETE!")
    print("=" * 80)
    print(f"\nPlayed {len(sections)} sections over 10 minutes")
    print("Playback continues... (press Ctrl+C to stop)")

    # Let it run for a bit then stop
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        pass

# ============================================================================
# CLEANUP
# ============================================================================

print("\nStopping playback...")
send_command("stop_playback")

print("Closing connection...")
s.close()

print("\n" + "=" * 80)
print("DUB REGGAE AUTOMATION FINISHED")
print("=" * 80)
print("\nTotal clips fired:", len(sections) * len(sections[0]["clips"]))
print("Sections played:", len(sections))
print("Duration: 10 minutes")
print("=" * 80)
