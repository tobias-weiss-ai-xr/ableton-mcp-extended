#!/usr/bin/env python3
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 9877))

# Test create_drum_pattern with params
command = {
    "type": "create_drum_pattern",
    "params": {
        "track_index": 2,
        "clip_index": 0,
        "pattern_name": "dub_techno",
        "length": 4.0,
    },
}
sock.send(json.dumps(command).encode("utf-8"))
response = json.loads(sock.recv(8192).decode("utf-8"))
sock.close()

print("create_drum_pattern response:")
print(json.dumps(response, indent=2))
