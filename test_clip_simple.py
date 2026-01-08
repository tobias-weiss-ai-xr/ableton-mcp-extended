import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))

def send_command(cmd_type, params=None):
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

print("Creating test clip on Track 4...")
result = send_command("create_clip", {"track_index": 4, "clip_index": 0, "length": 4.0})
print("Create clip result:", result)

time.sleep(0.5)

print("Adding notes...")
notes = [{"pitch": 36, "start_time": 2.0, "duration": 0.3, "velocity": 110, "mute": False}]
result = send_command("add_notes_to_clip", {"track_index": 4, "clip_index": 0, "notes": notes})
print("Add notes result:", result)

time.sleep(0.5)

print("Setting clip name...")
result = send_command("set_clip_name", {"track_index": 4, "clip_index": 0, "name": "Test Kick"})
print("Set name result:", result)

s.close()
