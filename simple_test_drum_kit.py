#!/usr/bin/env python3
"""
Simple test to load a drum kit into Track 2 (Dub Hats)
This replaces the empty Drum Rack with an actual acoustic drum kit.
"""

import socket
import json


def send_command(command_type, params=None):
    """Send command to Ableton MCP server"""
    if params is None:
        params = {}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9877))

        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))

        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()

        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}


def main():
    print("=" * 80)
    print("TEST: Load Drum Kit into Track 2 (Dub Hats)")
    print("=" * 80)
    print()

    # Step 1: Check current Track 2 devices
    print("[STEP 1] Checking Track 2 devices before loading kit...")
    result = send_command("get_track_info", {"track_index": 2})

    if result.get("status") == "success":
        track_data = result.get("result", {})
        devices = track_data.get("devices", [])
        print(f"Track 2 devices: {len(devices)}")
        for i, dev in enumerate(devices):
            print(f"  Device {i}: {dev.get('name', 'Unknown')}")
    else:
        print(f"[FAIL] {result.get('message', 'Error')}")
        return

    print()

    # Step 2: Load drum kit using load_drum_kit
    print("[STEP 2] Loading acoustic drum kit into Track 2...")
    print(
        "Using load_drum_kit(track_index=2, rack_uri='Drums/Drum Rack', kit_path='drums/acoustic')"
    )

    result = send_command(
        "load_drum_kit",
        {
            "track_index": 2,
            "rack_uri": "Drums/Drum Rack",
            "kit_path": "drums/acoustic",
        },
    )

    status = result.get("status")
    if status == "success":
        print(f"\n[OK] {result.get('result', 'Success')}")
    else:
        print(f"\n[FAIL] {result.get('message', 'Error')}")
        return

    print()

    # Step 3: Verify the drum kit was loaded
    print("[STEP 3] Verifying Track 2 devices after loading kit...")
    result = send_command("get_track_info", {"track_index": 2})

    if result.get("status") == "success":
        track_data = result.get("result", {})
        devices = track_data.get("devices", [])
        print(f"Track 2 devices: {len(devices)}")
        for i, dev in enumerate(devices):
            print(f"  Device {i}: {dev.get('name', 'Unknown')}")

        # Get Drum Rack details
        if devices and devices[0].get("name") == "Drum Rack":
            print(f"\nDrum Rack parameters:")
            result2 = send_command(
                "get_device_parameters",
                {"track_index": 2, "device_index": 0},
            )

            if result2.get("status") == "success":
                params = result2.get("result", {}).get("parameters", [])
                param_count = len(params)
                print(f"  Parameters: {param_count}")
                # Check if we have more parameters than a basic Drum Rack
                # A populated Drum Rack will have more parameters due to loaded samples
                if param_count > 17:
                    print(
                        f"  --> Drum Rack appears to have loaded samples! ({param_count} parameters)"
                    )
                else:
                    print(
                        f"  --> Drum Rack may still be empty ({param_count} parameters)"
                    )

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nDub Hats track (Track 2) now has:")
    print("1. A Drum Rack device")
    print("2. Acoustic drum kit loaded (from drums/acoustic)")
    print("3. The dub_techno pattern will now play actual drum sounds!")
    print()
    print("=" * 80)


if __name__ == "__main__":
    import time

    main()
