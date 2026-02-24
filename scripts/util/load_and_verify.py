#!/usr/bin/env python3
"""Create new track and load Drum Rack"""

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
print("CREATE NEW TRACK AND LOAD DRUM KIT")
print("=" * 70)

# Create a new MIDI track
print("\nCreating new MIDI track...")
create_result = send_command("create_midi_track", {"index": -1})
print(f"Create result: {json.dumps(create_result, indent=2)}")

# Check session
print("\nChecking session tracks...")
session = send_command("get_session_info")
track_count = session.get("result", {}).get("track_count", 0)
print(f"Total tracks: {track_count}")

# Name the track
new_track_index = track_count - 1
print(f'\nNaming track {new_track_index} to "Dub Hats"...')
name_result = send_command(
    "set_track_name", {"track_index": new_track_index, "name": "Dub Hats"}
)
print(f"Name result: {json.dumps(name_result, indent=2)}")

# Load Drum Rack
print(f"\nLoading Drum Rack onto track {new_track_index}...")
rack_result = send_command(
    "load_browser_item", {"track_index": new_track_index, "item_uri": "Drums/Drum Rack"}
)
print(f"Load result: {json.dumps(rack_result, indent=2)}")

# Get drum kits
print("\nGetting drum kits from drums/acoustic...")
kit_result = send_command("get_browser_items_at_path", {"path": "drums/acoustic"})
kit_items = kit_result.get("result", {}).get("items", [])
loadable_kits = [item for item in kit_items if item.get("is_loadable", False)]
print(f"Total kits: {len(kit_items)}, Loadable: {len(loadable_kits)}")

if loadable_kits:
    print(f"First loadable: {loadable_kits[0].get('name')}")

    # Load the kit
    kit_uri = loadable_kits[0].get("uri")
    print(f"\nLoading drum kit from: {kit_uri}")
    load_result = send_command(
        "load_browser_item", {"track_index": new_track_index, "item_uri": kit_uri}
    )
    print(f"Kit load result: {json.dumps(load_result, indent=2)}")

# Verify
print(f"\nVerifying track {new_track_index}...")
track_info = send_command("get_track_info", {"track_index": new_track_index})
devices = track_info.get("result", {}).get("devices", [])
print(f"Devices: {len(devices)}")

if devices:
    print("\nSUCCESS! Drum loaded with drum kit:")
    for i, dev in enumerate(devices):
        print(f"  {i}: {dev.get('name')} ({dev.get('class_name')})")
else:
    print("\nFAILED - no devices")
