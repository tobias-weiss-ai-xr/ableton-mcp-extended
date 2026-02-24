#!/usr/bin/env python3
"""
Load Instruments for Dub Techno Track - WORKING VERSION
=======================================================
Uses the working load_browser_item command with correct Ableton URIs
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
    print("Using load_browser_item with correct Ableton URIs")
    print("=" * 80)
    print()

    # Instruments with correct Ableton URIs
    instruments = [
        {
            "track": 0,
            "name": "Deep Kick",
            "uri": "query:Synths#Operator",
            "description": "Kick synth for dub techno pattern",
        },
        {
            "track": 1,
            "name": "Sub-Bass (HEAVY)",
            "uri": "query:Synths#Operator",
            "description": "Sawtooth + sub dub bass - THE STAR",
        },
        {
            "track": 2,
            "name": "Dub Hats",
            "uri": "query:Synths#Drum%20Rack",
            "description": "Drum Rack for hi-hats",
        },
        {
            "track": 3,
            "name": "Percs",
            "uri": "query:Synths#Drum%20Rack",
            "description": "Drum Rack for percussion",
        },
        {
            "track": 4,
            "name": "Atmo Pad",
            "uri": "query:Synths#Wavetable",
            "description": "Dark atmospheric pads",
        },
        {
            "track": 5,
            "name": "Dub FX",
            "uri": "query:Synths#Simpler",
            "description": "Simpler for FX samples",
        },
        {
            "track": 6,
            "name": "Dub Delay",
            "uri": "query:AudioFx#Simple%20Delay",
            "description": "Simple Delay effect send",
        },
        {
            "track": 7,
            "name": "Reverb",
            "uri": "query:AudioFx#Hybrid%20Reverb",
            "description": "Hybrid Reverb send",
        },
    ]

    loaded = []
    failed = []

    for inst in instruments:
        print(f"Track {inst['track']}: {inst['name']}")
        print(f"  Description: {inst['description']}")
        print(f"  URI: {inst['uri']}")

        # Use the WORKING command: load_browser_item
        result = send_command(
            "load_browser_item", {"track_index": inst["track"], "item_uri": inst["uri"]}
        )

        status = result.get("status")
        if status == "success":
            res = result.get("result", {})
            print(f"  [SUCCESS] Loaded!")
            print(f"    Item: {res.get('item_name')}")
            print(f"    Track: {res.get('track_name')}")
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
        print("INSTRUMENTS ARE NOW LOADED!")
        print("Each track has its instrument ready for configuration.")

    if failed:
        print("Failed to load:")
        for i, name in enumerate(failed, 1):
            print(f"  [{i}] {name}")
        print()
        print("These need manual loading in Ableton Live.")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
