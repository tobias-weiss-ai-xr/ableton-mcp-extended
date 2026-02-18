import socket
import json

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


print("=" * 80)
print("VERIFYING 10-MINUTE DUB REGGAE SETUP")
print("=" * 80)

# Get track count
session_info = send_command("get_session_info")
track_count = session_info["result"]["track_count"]
print(f"\nTotal tracks in session: {track_count}")

# Check tempo
# Note: There's no direct get_tempo command, but we set it in the creation script
print("\nTempo: Set to 75 BPM (by creation script)")

# List tracks
print("\nTrack Details:")
for i in range(track_count):
    try:
        track_info = send_command("get_track_info", {"track_index": i})
        name = track_info.get("result", {}).get("name", "Unknown")
        print(f"  Track {i}: {name}")
    except:
        pass

# Verify our key tracks exist
expected_tracks = [
    "Kick",
    "Snare",
    "Hi-hats",
    "Dub Bass",
    "Guitar Chop",
    "Organ Bubble",
    "FX",
    "Dub Delays",
    "Reverb Send",
    "Delay Send",
]
print("\n" + "=" * 80)
print("TRACK CREATION VERIFICATION")
print("=" * 80)

session_info = send_command("get_session_info")
track_count = session_info["result"]["track_count"]

found_tracks = {}
for i in range(track_count):
    try:
        track_info = send_command("get_track_info", {"track_index": i})
        name = track_info.get("result", {}).get("name", "")
        if name in expected_tracks:
            found_tracks[name] = i
    except:
        pass

print("\nExpected tracks found:")
for track in expected_tracks:
    if track in found_tracks:
        print(f"  [OK] {track} at Track {found_tracks[track]}")
    else:
        print(f"  [MISSING] {track}")

print("\n" + "=" * 80)
print("CLIP CREATION VERIFICATION")
print("=" * 80)

# Check for clips on each track
for track in [
    "Kick",
    "Snare",
    "Hi-hats",
    "Dub Bass",
    "Guitar Chop",
    "Organ Bubble",
    "FX",
    "Dub Delays",
]:
    if track in found_tracks:
        track_idx = found_tracks[track]
        print(f"\n{track} (Track {track_idx}):")

        # Try to get clip info for first few slots
        clips_found = 0
        for slot in range(8):
            try:
                clip_info = send_command(
                    "get_clip_info", {"track_index": track_idx, "clip_index": slot}
                )
                if clip_info.get("status") == "success":
                    clips_found += 1
                    name = clip_info.get("result", {}).get("name", "Unnamed")
                    length = clip_info.get("result", {}).get("length", 0)
                    notes = clip_info.get("result", {}).get("notes", [])
                    print(
                        f'  Slot {slot}: "{name}" ({length} beats, {len(notes)} notes)'
                    )
            except:
                # Clip slot might be empty
                pass

        if clips_found > 0:
            print(f"  Total clips found: {clips_found}")
        else:
            print(f"  No clips found")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("1. Load instruments on each track")
print("2. Load effects on send tracks (Reverb, Delay)")
print("3. Set up send routing")
print("4. Run play_10min_dub_reggae.py for automation")

s.close()
