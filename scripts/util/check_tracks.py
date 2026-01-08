import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    return json.loads(s.recv(8192).decode("utf-8"))


print("=" * 80)
print("CHECKING TRACKS AND DEVICES")
print("=" * 80)

# Check first 8 tracks
for i in range(8):
    result = send_command("get_track_info", {"track_index": i})
    track_name = result.get("name", "Unknown")
    clip_count = result.get("clip_count", 0)
    print(f"\nTrack {i}: {track_name}")
    print(f"  Clips: {clip_count}")

s.close()

print("\n" + "=" * 80)
