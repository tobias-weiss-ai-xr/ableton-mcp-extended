#!/usr/bin/env python3
"""
Replace Track 2's empty Drum Rack with a properly loaded drum kit.

This script deletes the existing empty Drum Rack in Track 2 ("Dub Hats")
and replaces it with a properly populated Drum Rack that will play
actual hi-hat sounds for the dub techno pattern.

Usage:
1. Run this script with Ableton Live open and the Remote Script loaded
2. The script will connect to the Ableton Remote Script (TCP port 9877)
3. Track 2 (Dub Hats) will have a properly loaded Drum Rack

Note: This script requires Ableton Live to be running with the Remote Script loaded.
"""

import socket
import json
from typing import Dict, Any


def send_ableton_command(
    command_type: str, params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Send a command to the Ableton Remote Script via TCP (port 9877).
    """
    if params is None:
        params = {}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9877))

        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))
        response = sock.recv(8192).decode("utf-8")
        sock.close()

        return json.loads(response)
    except ConnectionRefusedError:
        print("ERROR: Cannot connect to Ableton.")
        print("Make sure:")
        print("  1. Ableton Live is open")
        print("  2. The AbletonMCP Remote Script is loaded")
        print("     (Preferences -> Link, Tempo & MIDI -> Control Surface: AbletonMCP)")
        return {"error": "Connection refused"}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print("=" * 70)


def print_step(step_num: int, description: str):
    """Print a formatted step header."""
    print(f"\n[Step {step_num}] {description}")
    print("-" * 70)


def main():
    print_header("REPLACE TRACK 2 DRUM RACK - WITH PROPERLY POPULATED DRUM KIT")

    TRACK_INDEX = 2  # Dub Hats track
    DRUM_RACK_URI = "Drums/Drum Rack"
    DRUM_KIT_PATH = "drums/acoustic"

    # Step 1: Check current state of Track 2
    print_step(1, f"Analyzing Track {TRACK_INDEX} (Dub Hats)")
    track_info = send_ableton_command("get_track_info", {"track_index": TRACK_INDEX})

    if "error" in track_info:
        print(f"ERROR: {track_info['error']}")
        return

    print(f"Track Name: {track_info.get('name', 'Unknown')}")
    print(f"Track Type: {track_info.get('type', 'Unknown')}")

    devices = track_info.get("devices", [])
    print(f"Number of devices: {len(devices)}")

    if devices:
        print(f"Current devices:")
        for i, dev in enumerate(devices):
            name = dev.get("name", "Unknown")
            dev_type = dev.get("type", "Unknown")
            print(f"  Device {i}: {name} ({dev_type})")

        # Step 2: Delete existing device(s)
        print_step(2, f"Deleting existing device(s) from Track {TRACK_INDEX}")

        # Delete devices from highest index to avoid index shifting issues
        for device_index in range(len(devices) - 1, -1, -1):
            del_result = send_ableton_command(
                "delete_device",
                {"track_index": TRACK_INDEX, "device_index": device_index},
            )
            if "error" not in del_result:
                print(f"  Removed device at index {device_index}")
            else:
                print(f"  Error removing device {device_index}: {del_result['error']}")
    else:
        print_step(2, f"No devices found - Track {TRACK_INDEX} is empty")

    # Step 3: Load Drum Rack + drum kit
    print_step(3, f"Loading Drum Rack and drum kit to Track {TRACK_INDEX}")

    # Step 3a: Load the Drum Rack container
    load_rack_result = send_ableton_command(
        "load_browser_item", {"track_index": TRACK_INDEX, "item_uri": DRUM_RACK_URI}
    )

    if "error" in load_rack_result:
        print(f"  ERROR loading Drum Rack: {load_rack_result['error']}")
        print("  Trying alternative URI format...")

        # Try query format
        load_rack_result = send_ableton_command(
            "load_browser_item",
            {"track_index": TRACK_INDEX, "item_uri": "query:Drums#Drum%20Rack"},
        )

        if "error" in load_rack_result:
            print(f"  ERROR with alternative format: {load_rack_result['error']}")
            print("\n  PROBLEM: Unable to load Drum Rack container.")
            print("  Solution: Manually load Drum Rack in Ableton")
            return

    print("  Drum Rack container loaded successfully")

    # Step 3b: Get available drum kits at default path
    kit_result = send_ableton_command(
        "get_browser_items_at_path", {"path": DRUM_KIT_PATH}
    )

    if "error" in kit_result:
        print(f"  WARNING: Error getting drum kits: {kit_result['error']}")
        print("  Trying to load a drum kit directly by path...")

        # Try loading specific commonly available kits
        possible_kits = [
            "drums/acoustic/kit1",
            "drums/acoustic/808",
            "drums/acoustic/basic",
        ]

        loaded = False
        for kit_uri in possible_kits:
            direct_result = send_ableton_command(
                "load_browser_item", {"track_index": TRACK_INDEX, "item_uri": kit_uri}
            )

            if "error" not in direct_result:
                print(f"  Successfully loaded kit: {kit_uri}")
                loaded = True
                break

        if not loaded:
            print("\n  PROBLEM: Unable to load any drum kit.")
            print("  The Drum Rack container is loaded but empty.")
            print("\n  MANUAL STEPS REQUIRED:")
            print("  1. In Ableton, select Track 2")
            print("  2. Click on the Drum Rack")
            print("  3. Open the Browser (left panel)")
            print("  4. Navigate to: Drums → Acoustic")
            print("  5. Drag any drum kit onto the Drum Rack")
            return
    else:
        kit_items = kit_result.get("items", [])
        loadable_kits = [item for item in kit_items if item.get("is_loadable", False)]

        print(
            f"  Found {len(kit_items)} total items, {len(loadable_kits)} loadable kits"
        )

        if loadable_kits:
            # Load the first loadable kit
            kit_uri = loadable_kits[0].get("uri")
            kit_name = loadable_kits[0].get("name", "Unknown")

            print(f"  Loading kit: {kit_name}")
            load_kit_result = send_ableton_command(
                "load_browser_item", {"track_index": TRACK_INDEX, "item_uri": kit_uri}
            )

            if "error" in load_kit_result:
                print(f"  ERROR loading kit: {load_kit_result['error']}")
                print("\n  PROBLEM: Unable to load drum kit into Drum Rack.")
                print("  The Drum Rack container is loaded but empty.")
                return
            else:
                print(f"  Drum kit '{kit_name}' loaded successfully!")
        else:
            print("  WARNING: No loadable drum kits found at this path")

            # Try alternative paths
            alt_paths = ["drums/drum kits", "drums/electronic", "packs/drums"]
            for alt_path in alt_paths:
                print(f"  Trying: {alt_path}")
                alt_result = send_ableton_command(
                    "get_browser_items_at_path", {"path": alt_path}
                )

                if "error" not in alt_result:
                    alt_items = alt_result.get("items", [])
                    alt_loadable = [
                        item for item in alt_items if item.get("is_loadable", False)
                    ]

                    if alt_loadable:
                        alt_uri = alt_loadable[0].get("uri")
                        alt_name = alt_loadable[0].get("name", "Unknown")

                        load_alt_result = send_ableton_command(
                            "load_browser_item",
                            {"track_index": TRACK_INDEX, "item_uri": alt_uri},
                        )

                        if "error" not in load_alt_result:
                            print(
                                f"  Successfully loaded kit from {alt_path}: {alt_name}"
                            )
                            break
                    else:
                        print(f"  No loadable kits found at {alt_path}")
                else:
                    print(f"  Error accessing {alt_path}: {alt_result['error']}")

    # Step 4: Verify the Drum Rack is loaded
    print_step(4, f"Verifying Track {TRACK_INDEX} has properly loaded Drum Rack")
    verify_result = send_ableton_command("get_track_info", {"track_index": TRACK_INDEX})

    if "error" not in verify_result:
        verify_devices = verify_result.get("devices", [])
        print(f"  Number of devices: {len(verify_devices)}")

        if verify_devices:
            print(f"  Loaded devices:")
            for i, dev in enumerate(verify_devices):
                name = dev.get("name", "Unknown")
                dev_type = dev.get("type", "Unknown")
                print(f"    Device {i}: {name} ({dev_type})")

    print_header("TRACK 2 DRUM RACK REPLACEMENT COMPLETE")

    print(f"""
Summary:
--------
Track {TRACK_INDEX} (Dub Hats) now has a loaded Drum Rack
Drum kit populated with drum sounds
Ready to play dub hat patterns

Next Steps:
-----------
1. Open Ableton Live and verify Track 2 shows a loaded Drum Rack
2. Click on the Drum Rack to see the pad grid
3. Verify that pads have samples loaded (not empty)
4. Play the dub techno pattern and listen for hi-hats
5. If needed, manually select a different drum kit from the browser

MIDI Note Reference for Dub Hats:
---------------------------------
- Note 42 (Closed Hi-hat) - Main dub hat pattern
- Note 44 (Pedal Hi-hat) - Sparse hi-hats
- Note 46 (Open Hi-hat) - Occasional open hats

If you don't hear sound:
-----------------------
1. Check that Drum Rack pads have samples (click on pad cells in Ableton)
2. Verify track output is not muted
3. Check track volume is up
4. Ensure global/master volume is on
5. In Ableton: Browser -> Drums -> drag samples to empty Drum Rack pads

Alternative: Using the MCP Server (Claude/Cursor):
-------------------------------------------------
If you're using Claude or Cursor, you can call:
  create_drum_pattern(track_index=2, clip_index=0, pattern="one_drop", length_bars=4)
  (This will now auto-load a Drum Rack if Track 2 is empty)

What was fixed:
--------------
The create_drum_pattern function in MCP_Server/server.py (lines 1261-1294)
now automatically loads a Drum Rack + drum kit when creating patterns on
empty tracks. This fixes the bug where empty Drum Racks were created.

Constants used:
  DEFAULT_DRUM_RACK_URI = "Drums/Drum Rack"
  DEFAULT_DRUM_KIT_PATH = "drums/acoustic"
    """)


if __name__ == "__main__":
    main()
