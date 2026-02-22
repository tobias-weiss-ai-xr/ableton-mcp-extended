#!/usr/bin/env python3
"""Browse Drums category and find loadable items"""

import socket
import json


def send_command(cmd_type, params=None):
    if params is None:
        params = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9877))
    command = {"type": cmd_type, "params": params}
    sock.send(json.dumps(command).encode("utf-8"))

    # Read response in chunks
    chunks = []
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        chunks.append(chunk)
        # Try to parse to see if complete
        try:
            data = b"".join(chunks)
            result = json.loads(data.decode("utf-8"))
            sock.close()
            return result
        except:
            continue

    sock.close()
    return {"error": "Incomplete response"}


print("=" * 70)
print("BROWSE DRUMS - FIND LOADABLE KITS")
print("=" * 70)

# Try getting browser tree first (smaller response)
print("\n1. Getting browser tree...")
result = send_command("get_browser_tree")
categories = result.get("result", {}).get("categories", [])
print(f"   Categories: {len(categories)}")
for cat in categories:
    print(f"   - {cat.get('name')}: {cat.get('uri')}")

# Try to load from Sounds category which might have actual kits
print("\n2. Loading from Sounds category on Track 2...")
result = send_command(
    "load_browser_item", {"track_index": 2, "item_uri": "query:Sounds"}
)
print(f"   Result: {result}")

# Check device
track = send_command("get_track_info", {"track_index": 2})
devices = track.get("result", {}).get("devices", [])
d0 = devices[0] if devices else {}
cls = d0.get("class_name", "")
print(f"   Device: {d0.get('name')} ({cls})")

if "InstrumentGroup" in cls:
    print("\n   SUCCESS! Found drum kit with samples!")
elif "DrumGroup" in cls:
    print("\n   Empty Drum Rack - need to find another approach")

    # Try loading again with different query
    print("\n3. Trying query:Drums#Drum%20Rack followed by query:Drums...")
    send_command(
        "load_browser_item", {"track_index": 2, "item_uri": "query:Drums#Drum%20Rack"}
    )
    send_command("load_browser_item", {"track_index": 2, "item_uri": "query:Drums"})

    track = send_command("get_track_info", {"track_index": 2})
    devices = track.get("result", {}).get("devices", [])
    d0 = devices[0] if devices else {}
    print(f"   Device: {d0.get('name')} ({d0.get('class_name')})")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
