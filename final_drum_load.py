#!/usr/bin/env python3
"""Load Drum Rack on fresh Track 2 - final version"""

import socket
import json


def send_command(cmd_type, params=None):
    if params is None:
        params = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9877))
    command = {"type": cmd_type, "params": params}
    sock.send(json.dumps(command).encode("utf-8"))
    response = sock.recv(8192).decode("utf-8")
    sock.close()
    return json.loads(response)


print("=" * 70)
print("DRUM KIT LOADING - TRACK 2 (DUB HATS)")
print("=" * 70)

TRACK_INDEX = 2

# 1. Load Drum Rack
print(f"\n1. Loading Drum Rack onto track {TRACK_INDEX}...")
rack_result = send_command(
    "load_browser_item",
    {"track_index": TRACK_INDEX, "item_uri": "query:Drums#Drum%20Rack"},
)
print(f"Load result: {rack_result}")

# 2. Try loading drum kit from query format paths
paths_to_try = [
    "query:Drums#acoustic",
    "query:Drums#Acoustic:FileId_58622",  # Common drum kit ID
]

print("\n2. Trying to load drum kits...")
for path in paths_to_try:
    print(f"\n  Trying: {path}")
    kit_result = send_command(
        "load_browser_item", {"track_index": TRACK_INDEX, "item_uri": path}
    )
    if kit_result.get("status") == "success":
        print(f"    SUCCESS: {kit_result.get('result', {})}")
    else:
        print(f"    FAILED: {kit_result.get('message', 'Unknown')}")

# 3. Verify final state
print(f"\n3. Verifying track {TRACK_INDEX}...")
track_info = send_command("get_track_info", {"track_index": TRACK_INDEX})
track_data = track_info.get("result", {})
devices = track_data.get("devices", [])

print(f"Name: {track_data.get('name', 'Unknown')}")
print(f"Devices: {len(devices)}")

if devices:
    print("\nDevice chain:")
    for i, dev in enumerate(devices):
        print(f"  {i}: {dev.get('name')} ({dev.get('class_name')})")
    print("\nSUCCESS - Drum Rack loaded!")
else:
    print("\nFAILED - no devices")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
