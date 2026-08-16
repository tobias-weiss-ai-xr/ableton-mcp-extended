#!/usr/bin/env python3
"""
Quick Arrangement Demo - Minimal E2E test

This script demonstrates the core arrangement workflow in a simplified form.
It creates a basic session, captures it to arrangement, adds some automation,
and prepares for export.

Usage:
    python scripts/quick_arrangement_demo.py

Time: ~2-3 minutes
"""

import sys
import time
import json
import socket

HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_PORT = 9878
BPM = 120


def tcp(cmd, params=None):
    """Send TCP command"""
    if params is None:
        params = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15.0)
    sock.connect((HOST, TCP_PORT))
    msg = json.dumps({"type": cmd, "params": params})
    sock.sendall((msg + "\n").encode())
    data = b""
    while True:
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            break
        if not chunk:
            break
        data += chunk
    sock.close()
    return json.loads(data.decode())


def udp(cmd, params):
    """Send UDP command"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps({"type": cmd, "params": params}).encode(), (HOST, UDP_PORT))
    sock.close()


def main():
    print("=" * 60)
    print("QUICK ARRANGEMENT DEMO")
    print("=" * 60)
    
    # Step 1: Clean and setup
    print("\n[1/7] Cleaning up...")
    tcp("delete_all_tracks")
    time.sleep(2)
    
    # Step 2: Create tracks
    print("[2/7] Creating 4 tracks...")
    for i in range(4):
        tcp("create_midi_track", {"index": i})
        time.sleep(0.3)
    
    # Load instruments
    print("[2/7] Loading instruments...")
    tcp("load_browser_item", {"track_index": 0, "item_uri": "query:Drums#FileId_58622"})
    time.sleep(0.5)
    tcp("load_browser_item", {"track_index": 1, "item_uri": "query:Sounds#Bass:FileId_49654"})
    time.sleep(0.5)
    tcp("load_browser_item", {"track_index": 2, "item_uri": "query:Sounds#Pad:FileId_45564"})
    time.sleep(0.5)
    tcp("load_browser_item", {"track_index": 3, "item_uri": "query:Sounds#Synth%20Lead:FileId_50175"})
    time.sleep(0.5)
    
    # Name tracks
    for i, name in enumerate(["Drums", "Bass", "Chords", "Lead"]):
        tcp("set_track_name", {"track_index": i, "name": name})
        time.sleep(0.1)
    
    tcp("set_tempo", {"tempo": BPM})
    tcp("set_master_volume", {"volume": 0.8})
    time.sleep(0.3)
    
    # Step 3: Create simple clips
    print("[3/7] Creating clips...")
    from MCP_Server.server import create_drum_pattern, create_chord_notes
    
    # Drums - 2 scenes
    for si, pat in enumerate(["house_basic", "techno_4x4"]):
        create_drum_pattern(None, 0, si, pat, 16)
        time.sleep(0.2)
    
    # Bass - simple pattern
    for si in range(2):
        tcp("create_clip", {"track_index": 1, "clip_index": si, "length": 16})
        time.sleep(0.05)
        notes = []
        for b in range(0, 64, 4):
            notes.append({"pitch": 40 + si * 2, "start_time": b, "duration": 2.0, "velocity": 90, "mute": False})
        tcp("add_notes_to_clip", {"track_index": 1, "clip_index": si, "notes": notes})
        time.sleep(0.1)
    
    # Chords
    for si, root in enumerate([48, 50]):
        tcp("create_clip", {"track_index": 2, "clip_index": si, "length": 16})
        time.sleep(0.05)
        create_chord_notes(None, 2, si, root, "min7", 0, 8.0, 70)
        create_chord_notes(None, 2, si, root, "min7", 8, 8.0, 70)
        time.sleep(0.1)
    
    # Lead
    for si in range(2):
        tcp("create_clip", {"track_index": 3, "clip_index": si, "length": 16})
        time.sleep(0.05)
        notes = []
        for b in range(0, 64, 2):
            notes.append({"pitch": 60 + si * 5 + (b % 8), "start_time": b, "duration": 1.0, "velocity": 75, "mute": False})
        tcp("add_notes_to_clip", {"track_index": 3, "clip_index": si, "notes": notes})
        time.sleep(0.1)
    
    # Create scenes
    print("[3/7] Creating scenes...")
    for i, name in enumerate(["Verse", "Chorus"]):
        tcp("create_scene", {"index": i})
        tcp("set_scene_name", {"scene_index": i, "name": name})
        time.sleep(0.1)
    
    # Step 4: Session to Arrangement
    print("[4/7] Capturing session to arrangement...")
    tcp("set_playhead_position", {"bar": 0, "beat": 0})
    time.sleep(0.5)
    
    # Start recording
    tcp("start_recording", {})
    tcp("start_playback", {})
    time.sleep(0.5)
    
    # Trigger scenes
    tcp("trigger_scene", {"scene_index": 0})
    time.sleep(5)  # Wait ~5 seconds for 16 bars at 120 BPM
    tcp("trigger_scene", {"scene_index": 1})
    time.sleep(5)
    
    # Stop
    tcp("stop_recording", {})
    tcp("stop_playback", {})
    print("  Recording complete!")
    
    # Alternative: non-real-time capture
    print("[4/7] Non-real-time capture...")
    result = tcp("capture_and_insert_arrangement", {"start_bar": 0, "length_bars": 32, "quantize": True})
    print(f"  Capture result: {result.get('status', 'unknown')}")
    
    # Step 5: Check arrangement
    print("[5/7] Checking arrangement clips...")
    clips = tcp("get_arrangement_clips")
    if clips.get("status") == "success":
        arr_clips = clips.get("result", {}).get("arrangement_clips", [])
        print(f"  Found {len(arr_clips)} arrangement clips")
        for clip in arr_clips[:5]:
            print(f"    Track {clip.get('track_index')}, Clip {clip.get('clip_index')}: "
                  f"{clip.get('name')} at bar {clip.get('position', 0)/4.0:.1f}")
    
    # Step 6: Add automation
    print("[6/7] Adding automation...")
    
    # Filter sweep on all tracks
    for track_idx in range(4):
        tcp("create_filter_sweep", {
            "track_index": track_idx,
            "start_bar": 8,
            "end_bar": 16,
            "start_freq": 100.0,
            "end_freq": 5000.0,
            "device_index": 0,
            "parameter_index": 0,
        })
    
    # Volume fade in
    tcp("create_volume_automation_ramp", {
        "track_index": -1,
        "start_bar": 0,
        "end_bar": 4,
        "start_volume": 0.0,
        "end_volume": 0.8,
    })
    
    # Volume fade out
    tcp("create_volume_automation_ramp", {
        "track_index": -1,
        "start_bar": 28,
        "end_bar": 32,
        "start_volume": 0.8,
        "end_volume": 0.0,
    })
    
    print("  Automation added!")
    
    # Step 7: Polish
    print("[7/7] Final polish...")
    tcp("set_arrangement_view_position", {"bar": 0, "beat": 0})
    tcp("set_arrangement_zoom", {"zoom_level": 0.5})
    tcp("set_playhead_position", {"bar": 0, "beat": 0})
    tcp("set_master_volume", {"volume": 0.85})
    
    print("\n" + "=" * 60)
    print("QUICK DEMO COMPLETE!")
    print("=" * 60)
    print("\nArrangement created with:")
    print("- 4 tracks (Drums, Bass, Chords, Lead)")
    print("- 2 scenes (Verse, Chorus)")
    print("- ~32 bars of music")
    print("- Filter sweeps and volume automation")
    print("\nNext: Open Ableton, switch to Arrangement View (Tab)")
    print("      and fine-tune to your liking!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
