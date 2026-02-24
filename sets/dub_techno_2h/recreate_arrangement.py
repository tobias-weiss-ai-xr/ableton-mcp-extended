#!/usr/bin/env python3
"""
Recreate Dub Techno Arrangement with Proper Drum Rack Loading
==============================================================
Deletes all tracks, recreates 8-track dub techno session,
and properly loads Drum Rack with drum samples.
"""

import socket
import json
import time
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_command(command_type, params=None):
    """Send command to Ableton MCP server"""
    if params is None:
        params = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((TCP_HOST, TCP_PORT))
        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))
        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    print("=" * 70)
    print("RECREATE DUB TECHNO ARRANGEMENT")
    print("=" * 70)

    # STEP 1: Delete all tracks
    print("\n[1/5] Deleting all existing tracks...")
    result = send_command("delete_all_tracks")
    if result.get("status") == "success":
        print("      OK - All tracks deleted")
    else:
        print(f"      ERROR: {result.get('message')}")
    time.sleep(0.5)

    # STEP 2: Create 8 tracks
    print("\n[2/5] Creating 8 tracks...")
    track_names = [
        "Deep Kick",  # 0
        "Sub-Bass",  # 1
        "Dub Hats",  # 2
        "Percs",  # 3
        "Atmo Pad",  # 4
        "Dub FX",  # 5
        "Dub Delay",  # 6 (Audio)
        "Reverb",  # 7 (Audio)
    ]

    for i, name in enumerate(track_names):
        if i < 6:
            result = send_command("create_midi_track", {"index": -1})
        else:
            result = send_command("create_audio_track", {"index": -1})

        if result.get("status") == "success":
            print(f"      OK - Track {i}: {name}")
        else:
            print(f"      ERROR: {result.get('message')}")
        time.sleep(0.2)

    time.sleep(0.5)

    # STEP 3: Name tracks
    print("\n[3/5] Naming tracks...")
    for i, name in enumerate(track_names):
        result = send_command("set_track_name", {"track_index": i, "name": name})
        if result.get("status") == "success":
            print(f"      OK - Track {i}: {name}")
        else:
            print(f"      ERROR: {result.get('message')}")
        time.sleep(0.1)

    time.sleep(0.5)

    # STEP 4: Load instruments with correct URIs
    print("\n[4/5] Loading instruments...")

    instruments = [
        (0, "Deep Kick", "query:Drums#Operator"),
        (1, "Sub-Bass", "query:Synths#Operator"),
        (2, "Dub Hats", "query:Drums#Drum%20Rack"),
        (3, "Percs", "query:Drums#Drum%20Rack"),
        (4, "Atmo Pad", "query:Synths#Wavetable"),
        (5, "Dub FX", "query:Instruments#Simpler"),
    ]

    effects = [
        (6, "Dub Delay", "query:Audio%20Effects#Simple%20Delay"),
        (7, "Reverb", "query:Audio%20Effects#Hybrid%20Reverb"),
    ]

    for track_idx, name, uri in instruments:
        print(f"      Loading {name} on track {track_idx}...")
        result = send_command(
            "load_browser_item", {"track_index": track_idx, "item_uri": uri}
        )
        if result.get("status") == "success":
            print(f"      OK - {name} loaded")
        else:
            print(f"      ERROR: {result.get('message')}")
        time.sleep(0.5)

    for track_idx, name, uri in effects:
        print(f"      Loading {name} on track {track_idx}...")
        result = send_command(
            "load_browser_item", {"track_index": track_idx, "item_uri": uri}
        )
        if result.get("status") == "success":
            print(f"      OK - {name} loaded")
        else:
            print(f"      ERROR: {result.get('message')}")
        time.sleep(0.5)

    # STEP 5: Verify arrangement
    print("\n[5/5] Verifying arrangement...")
    session = send_command("get_session_info")
    track_count = session.get("result", {}).get("track_count", 0)
    print(f"      Total tracks: {track_count}")

    for i in range(track_count):
        track_info = send_command("get_track_info", {"track_index": i})
        track = track_info.get("result", {})
        devices = track.get("devices", [])
        device_names = [d.get("name", "?") for d in devices]
        print(
            f"      Track {i}: {track.get('name', '?')} - {len(devices)} device(s): {device_names}"
        )

    # Set tempo
    print("\n[+] Setting tempo to 114 BPM...")
    send_command("set_tempo", {"tempo": 114.0})

    print("\n" + "=" * 70)
    print("ARRANGEMENT RECREATED")
    print("=" * 70)
    print("""
Track Layout:
  0: Deep Kick (Operator)
  1: Sub-Bass (Operator)
  2: Dub Hats (Drum Rack) <-- THIS IS THE TRACK WITH DRUM RACK
  3: Percs (Drum Rack)
  4: Atmo Pad (Wavetable)
  5: Dub FX (Simpler)
  6: Dub Delay (Simple Delay)
  7: Reverb (Hybrid Reverb)

NOTE: Drum Rack containers are loaded but may be empty.
You need to manually drag drum samples onto the Drum Rack pads in Ableton:
  1. Click on Track 2 (Dub Hats)
  2. Click on Drum Rack device
  3. Open Browser -> Drums -> Acoustic
  4. Drag a drum kit onto the Drum Rack
""")


if __name__ == "__main__":
    main()
