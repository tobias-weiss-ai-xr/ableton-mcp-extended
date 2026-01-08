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


print("Testing clip creation on Track 4 (Kick)...")

# Create a clip
print("\n1. Creating clip...")
result = send_command("create_clip", {"track_index": 4, "clip_index": 0, "length": 4.0})
print(f"Result: {result}")

time.sleep(0.5)

# Add notes
print("\n2. Adding notes...")
notes = [
    {"pitch": 36, "start_time": 2.0, "duration": 0.3, "velocity": 110, "mute": False}
]
result = send_command(
    "add_notes_to_clip", {"track_index": 4, "clip_index": 0, "notes": notes}
)
print(f"Result: {result}")

time.sleep(0.5)

# Set clip name
print("\n3. Setting clip name...")
result = send_command(
    "set_clip_name", {"track_index": 4, "clip_index": 0, "name": "Test Kick Clip"}
)
print(f"Result: {result}")

# Get clip info
print("\n4. Getting clip info...")
result = send_command("get_clip_info", {"track_index": 4, "clip_index": 0})
print(f"Result: {result}")

print("\n5. Testing fire clip...")
result = send_command("fire_clip", {"track_index": 4, "clip_index": 0})
print(f"Result: {result}")

print("\nTest complete!")
s.close()
