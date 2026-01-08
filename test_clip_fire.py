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


print("=" * 80)
print("TESTING CLIP FIRE ON DUB REGGAE TRACKS")
print("=" * 80)

# Find track indices
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

print("\nFinding tracks...")
session_info = send_command("get_session_info")
track_count = session_info["result"]["track_count"]

for i in range(track_count):
    try:
        track_info = send_command("get_track_info", {"track_index": i})
        name = track_info.get("result", {}).get("name", "")
        if name in track_names:
            track_indices[name] = i
            print(f"  [OK] Found {name} at Track {i}")
    except:
        pass

print(f"\nFound {len(track_indices)} tracks")

if len(track_indices) < 8:
    print("\n[ERROR] Missing tracks!")
    print("Required:")
    for name in track_names:
        if name not in track_indices:
            print(f"  - {name}")
    s.close()
    exit(1)

# Test firing clips on each track
print("\n" + "=" * 80)
print("TESTING CLIP FIRE")
print("=" * 80)

for track_name, track_idx in track_indices.items():
    print(f"\n{track_name} (Track {track_idx}):")

    # Try to fire clip 0
    result = send_command("fire_clip", {"track_index": track_idx, "clip_index": 0})
    if result.get("status") == "success":
        print(f"  [OK] Fired clip 0")
    else:
        print(f"  [ERROR] {result.get('message')}")

    time.sleep(0.5)

print("\n" + "=" * 80)
print("ALL CLIPS FIRED - LISTENING FOR 5 SECONDS")
print("=" * 80)

time.sleep(5)

print("\nStopping all clips...")
for track_name, track_idx in track_indices.items():
    send_command("stop_clip", {"track_index": track_idx, "clip_index": 0})
    print(f"  Stopped {track_name}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nIf you heard music, the setup is working!")
print("You can now run the full automation:")
print("  python play_10min_dub_reggae.py")

s.close()
