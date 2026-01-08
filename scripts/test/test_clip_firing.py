import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    return json.loads(s.recv(8192).decode("utf-8"))


print("=" * 80)
print("TESTING CLIP FIRING")
print("=" * 80)

# Test firing clips from different tracks
test_clips = [
    (0, 0),  # Kick: Basic
    (1, 0),  # Sub-bass: Root Drone
    (2, 2),  # Hi-hats: Minimal
    (3, 4),  # Synth Pads: Minimal
    (4, 3),  # FX: Silent
    (5, 2),  # Dub Delays: Minimal
]

print("\nFiring test clips...")
for track_index, clip_index in test_clips:
    print(f"  Firing Track {track_index} Clip {clip_index}...")
    result = send_command(
        "fire_clip", {"track_index": track_index, "clip_index": clip_index}
    )
    print(f"    Result: {result.get('status', 'unknown')}")
    time.sleep(0.2)

# Start playback briefly
print("\nStarting playback for 5 seconds...")
send_command("start_playback", {})
print("  [OK] Playback started")

time.sleep(5)

print("\nStopping playback...")
send_command("stop_playback", {})
print("  [OK] Playback stopped")

s.close()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nIf you heard sound, clips are working correctly!")
print("If no sound, check:")
print("  1. Instruments are loaded with presets")
print("  2. Track volume faders are up")
print("  3. Master volume is not muted")
print("=" * 80)
