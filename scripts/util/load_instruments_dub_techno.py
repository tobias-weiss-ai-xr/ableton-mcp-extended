#!/usr/bin/env python3
"""
Load Instruments for Dub Techno Track
======================================
Loads all 8 instruments directly via socket to Ableton MCP Remote Script
"""

import socket
import json
import time


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
        return {"status": "error", "message": str(e)}


def main():
    print("=" * 80)
    print("LOADING INSTRUMENTS - 2-HOUR DUB TECHNO TRACK")
    print("=" * 80)
    print()

    instruments = [
        {
            "track": 0,
            "name": "Deep Kick",
            "uri": "Operator",
            "description": "Punchy operator kick",
        },
        {
            "track": 1,
            "name": "Sub-Bass (HEAVY)",
            "uri": "Operator",
            "description": "Sawtooth + sub dub bass",
        },
        {
            "track": 2,
            "name": "Dub Hats",
            "uri": "Drums/Drum Rack",
            "description": "Minimal hi-hat drum rack",
        },
        {
            "track": 3,
            "name": "Percs",
            "uri": "Drums/Drum Rack",
            "description": "Percussion drum rack",
        },
        {
            "track": 4,
            "name": "Atmo Pad",
            "uri": "Wavetable",
            "description": "Dark wavetable pads",
        },
        {
            "track": 5,
            "name": "Dub FX",
            "uri": "Instruments/Simpler",
            "description": "FX sample loader",
        },
        {
            "track": 6,
            "name": "Dub Delay",
            "uri": "Audio Effects/Simple Delay",
            "description": "Dub delay send",
        },
        {
            "track": 7,
            "name": "Reverb",
            "uri": "Audio Effects/Hybrid Reverb",
            "description": "Reverb send",
        },
    ]

    loaded = []
    failed = []

    for inst in instruments:
        print(f"Track {inst['track']}: {inst['name']}")
        print(f"  Description: {inst['description']}")
        print(f"  URI: {inst['uri']}")

        result = send_command(
            "load_instrument_or_effect",
            {"track_index": inst["track"], "uri": inst["uri"]},
        )

        status = result.get("status")
        if status == "success":
            print(f"  [SUCCESS] Instrument loaded!")
            loaded.append(inst["name"])
        else:
            msg = result.get("message", "Unknown error")
            print(f"  [FAILED] {msg}")
            failed.append(inst["name"])

        print()
        time.sleep(0.5)

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Loaded: {len(loaded)}/{len(instruments)}")
    print()
    if loaded:
        print("Successfully loaded:")
        for i, name in enumerate(loaded, 1):
            print(f"  [{i}] {name}")
        print()

    if failed:
        print("Failed to load (manual setup required):")
        for i, name in enumerate(failed, 1):
            print(f"  [{i}] {name}")
        print()
        print("Manual setup in Ableton:")
        for inst in instruments:
            if inst["name"] in failed:
                print(f"  Track {inst['track']} ({inst['name']}):")
                print(f"    - Click device area")
                print(f"    - Press TAB to open browser")
                print(f"    - Navigate to: {inst['uri']}")
                print(f"    - Load instrument/device")
        print()

    print("=" * 80)


if __name__ == "__main__":
    main()
