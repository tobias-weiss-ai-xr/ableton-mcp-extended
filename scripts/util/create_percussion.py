import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))

# Create percussion track
s.send(
    json.dumps({"type": "create_midi_track", "params": {"index": 10}}).encode("utf-8")
)
response = json.loads(s.recv(4096).decode("utf-8"))
print("Created track:", response)

# Name the track
s.send(
    json.dumps(
        {"type": "set_track_name", "params": {"track_index": 10, "name": "Percussion"}}
    ).encode("utf-8")
)
response = json.loads(s.recv(4096).decode("utf-8"))
print("Named track:", response)

# Create percussion clip
s.send(
    json.dumps(
        {
            "type": "create_clip",
            "params": {"track_index": 10, "clip_index": 0, "length": 4.0},
        }
    ).encode("utf-8")
)
response = json.loads(s.recv(4096).decode("utf-8"))
print("Created clip:", response)

# Add percussion notes
notes = [
    {"pitch": 72, "start_time": 0.0, "duration": 0.125, "velocity": 70, "mute": False},
    {"pitch": 72, "start_time": 2.0, "duration": 0.125, "velocity": 65, "mute": False},
    {"pitch": 76, "start_time": 1.0, "duration": 0.0625, "velocity": 75, "mute": False},
    {"pitch": 76, "start_time": 3.0, "duration": 0.0625, "velocity": 70, "mute": False},
]

s.send(
    json.dumps(
        {
            "type": "add_notes_to_clip",
            "params": {"track_index": 10, "clip_index": 0, "notes": notes},
        }
    ).encode("utf-8")
)
response = json.loads(s.recv(4096).decode("utf-8"))
print("Added notes:", response)

s.close()
