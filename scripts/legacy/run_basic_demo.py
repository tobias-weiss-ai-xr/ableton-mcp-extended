#!/usr/bin/env python
"""Basic arrangement demo using only core commands"""
import sys
import time
import json
import socket

def tcp_command(cmd, params=None):
    """Send TCP command to MCP Server on port 9877"""
    if params is None:
        params = {}
    HOST, PORT = 'localhost', 9877
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.settimeout(30)
        message = json.dumps({"type": cmd, "params": params}) + "\n"
        s.sendall(message.encode())
        response = s.recv(4096).decode()
        return json.loads(response)

def main():
    print("=" * 70)
    print("BASIC ARRANGEMENT DEMO")
    print("=" * 70)
    print("\nCreating a simple arrangement with 4 tracks.")
    print("Estimated time: 2-3 minutes\n")
    
    try:
        # Step 1: Clean up
        print("[1/6] Deleting all tracks...")
        tcp_command("delete_all_tracks")
        print("  Done\n")
        
        # Step 2: Create tracks
        print("[2/6] Creating 4 MIDI tracks...")
        for i in range(4):
            tcp_command("create_midi_track", {"index": i})
            tcp_command("set_track_name", {"track_index": i, "name": f"Track {i}"})
            print(f"  Track {i} created")
        print("  Done\n")
        
        # Step 3: Create clips with simple notes
        print("[3/6] Creating session clips...")
        for track_idx in range(4):
            tcp_command("create_clip", {"track_index": track_idx, "clip_index": 0, "length": 4})
            
            # Simple notes for each track (different pitches)
            notes = []
            for beat in range(4):
                notes.append({
                    "pitch": 48 + track_idx * 12 + beat,
                    "start_time": beat * 1.0,
                    "duration": 0.5,
                    "velocity": 80
                })
            
            tcp_command("add_notes_to_clip", {
                "track_index": track_idx,
                "clip_index": 0,
                "notes": notes
            })
            print(f"  Clip created for track {track_idx}")
        print("  Done\n")
        
        # Step 4: Capture to arrangement
        print("[4/6] Capturing session to arrangement...")
        result = tcp_command("capture_and_insert_arrangement", {
            "start_bar": 0,
            "length_bars": 16,
            "quantize": True
        })
        print(f"  Status: {result.get('status', 'unknown')}")
        print("  Done\n")
        
        # Step 5: Add automation
        print("[5/6] Adding master volume automation...")
        tcp_command("create_volume_automation_ramp", {
            "track_index": -1,
            "start_bar": 0,
            "end_bar": 4,
            "start_volume": 0.0,
            "end_volume": 0.8,
            "curve_type": "s_curve"
        })
        print("  Done\n")
        
        # Step 6: Get arrangement info
        print("[6/6] Verifying arrangement...")
        result = tcp_command("get_arrangement_clips")
        clips = result.get("result", {}).get("arrangement_clips", [])
        print(f"  Found {len(clips)} arrangement clips")
        for clip in clips[:5]:  # Show first 5
            print(f"    - {clip.get('name', 'unnamed')} at bar {clip.get('position', 0)/4:.1f}")
        print("  Done\n")
        
        print("=" * 70)
        print("DEMO COMPLETE!")
        print("=" * 70)
        print("\nYour arrangement is ready!")
        print("\nIn Ableton Live:")
        print("  1. Press TAB to switch to Arrangement View")
        print("  2. You should see 16 bars of MIDI clips on 4 tracks")
        print("  3. Master volume fades in from bar 0-4")
        print("\nEach track has:")
        print("  - A 4-bar clip with simple notes")
        print("  - Different pitch ranges for each track")
        print("  - All clips captured to arrangement")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
