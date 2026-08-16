#!/usr/bin/env python3
"""
Quick test of 10-min mix setup - NO capturing (takes 2 seconds instead of 10 minutes)
"""

import json
import socket


def send_cmd(cmd, params=None):
    """Send command to Remote Script."""
    if params is None:
        params = {}
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 9877))
        s.settimeout(10)
        message = {"type": cmd, "params": params}
        s.sendall(json.dumps(message).encode() + b"\n")
        response = s.recv(4096).decode()
        if response:
            return json.loads(response)
        return {"status": "ok"}


def main():
    print("=" * 70)
    print("10-MINUTE MIX SETUP TEST (No Capture)")
    print("=" * 70)
    
    # Structure definition
    structure = [
        {"name": "Deep Space", "type": "intro", "scene": 0, "bars": 24, "bpm": 90.0},
        {"name": "Dub Foundation", "type": "verse", "scene": 1, "bars": 24, "bpm": 90.0},
        {"name": "Rising Tension", "type": "build", "scene": 2, "bars": 8, "bpm": 90.0},
        {"name": "Dub Bomb", "type": "drop", "scene": 3, "bars": 32, "bpm": 95.0},
        {"name": "Steppers Groove", "type": "verse", "scene": 4, "bars": 24, "bpm": 95.0},
        {"name": "Echo Chamber", "type": "breakdown", "scene": 5, "bars": 24, "bpm": 95.0},
        {"name": "Tension Rising", "type": "build", "scene": 2, "bars": 8, "bpm": 95.0},
        {"name": "Final Dub Apocalypse", "type": "drop", "scene": 3, "bars": 48, "bpm": 100.0},
        {"name": "Cosmic Echo", "type": "breakdown", "scene": 5, "bars": 24, "bpm": 100.0},
        {"name": "Return", "type": "build", "scene": 2, "bars": 8, "bpm": 100.0},
        {"name": "Grand Finale + Fade", "type": "finale", "scene": 3, "bars": 40, "bpm": 100.0},
    ]
    
    total_bars = sum(s["bars"] for s in structure)
    print(f"\nStructure: {len(structure)} sections, {total_bars} bars")
    print(f"Expected duration: {total_bars * 60 / 90:.1f} minutes")
    
    # Step 1: Stop playback
    print("\n[1/5] Stopping playback and recording...")
    send_cmd("stop_playback")
    send_cmd("stop_recording")
    print("[OK]")
    
    # Step 2: Set initial tempo
    print("\n[2/5] Setting initial BPM...")
    send_cmd("set_tempo", {"bpm": 90})
    print("[OK] BPM: 90")
    
    # Step 3: Set playhead to start
    print("\n[3/5] Setting playhead to start...")
    send_cmd("set_playhead_position", {"bar": 0, "beat": 0})
    print("[OK]")
    
    # Step 4: Create locators
    print("\n[4/5] Creating locators at section boundaries...")
    start_bar = 0
    for section in structure:
        color = None
        if section["type"] == "drop":
            color = "red"
        elif section["type"] == "breakdown":
            color = "blue"
        elif section["type"] == "build":
            color = "yellow"
        elif section["type"] == "intro":
            color = "green"
        elif section["type"] == "finale":
            color = "purple"
        
        send_cmd("create_locator", {
            "name": f"{section['name']}",
            "bar": start_bar,
            "color": color
        })
        start_bar += section["bars"]
    
    # End locator
    send_cmd("create_locator", {"name": "Mix_End", "bar": start_bar, "color": "white"})
    print(f"[OK] Created {len(structure) + 1} locators")
    
    # Step 5: Basic track setup
    print("\n[5/5] Setting up track volumes and panning...")
    send_cmd("set_track_volume", {"track_index": 0, "volume_db": -6.0})  # Bass
    send_cmd("set_track_volume", {"track_index": 1, "volume_db": -3.0})  # Kick
    send_cmd("set_track_volume", {"track_index": 2, "volume_db": -4.0})  # Snare
    send_cmd("set_track_volume", {"track_index": 3, "volume_db": -8.0})  # Hats
    send_cmd("set_track_pan", {"track_index": 2, "pan": -0.2})  # Snare left
    send_cmd("set_track_pan", {"track_index": 3, "pan": 0.2})   # Hats right
    print("[OK]")
    
    # Summary
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print("\nAbleton is now configured with:")
    print(f"  * {len(structure)} section locators in arrangement")
    print(f"  * Track volumes and panning adjusted")
    print(f"  * Initial BPM set to 90")
    print(f"  * Playhead at start")
    print("\nTo capture the mix:")
    print("  1. Arm all tracks (Manually in Ableton)")
    print("  2. Start recording")
    print("  3. Trigger scenes 0-5 in sequence")
    print("  4. Follow the structure above")
    print("\nOr run: python scripts/create_10min_mix_simple.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
