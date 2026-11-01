#!/usr/bin/env python
"""Run the quick arrangement demo with progress tracking"""
import sys
import time
import json

sys.path.insert(0, '.')

# Import the tcp function from the demo
from scripts.quick_arrangement_demo import tcp

def main():
    print("=" * 70)
    print("RUNNING QUICK ARRANGEMENT DEMO")
    print("=" * 70)
    print("\nThis will create 4 tracks, add clips, capture to arrangement,")
    print("add automation, and prepare a mix ready for manual fine-tuning.")
    print("Estimated time: 2-4 minutes\n")
    
    try:
        # Step 1
        print("[1/7] Deleting all tracks...")
        tcp("delete_all_tracks", {})
        print("  ✓ Done\n")
        
        # Step 2 - Create tracks
        print("[2/7] Creating 4 MIDI tracks...")
        INSTRUMENTS = [
            "query:Drums#FileId_58622",
            "query:Sounds#Bass",
            "query:Sounds#Pad",
            "query:Sounds#Synth%20Lead",
        ]
        TRACK_NAMES = ["Drums", "Bass", "Chords", "Lead"]
        
        for i in range(4):
            print(f"  Creating track {i}...")
            tcp("create_midi_track", {"index": i})
            tcp("set_track_name", {"track_index": i, "name": TRACK_NAMES[i]})
        print("  ✓ Tracks created\n")
        
        # Step 2b - Load instruments (this can take time)
        print("[2/7] Loading instruments (this may take 30-60 seconds)...")
        for i, uri in enumerate(INSTRUMENTS):
            print(f"  Loading instrument on track {i}: {uri}...")
            result = tcp("load_browser_item", {
                "track_index": i,
                "item_uri": uri
            })
            print(f"    Status: {result.get('status', 'unknown')}")
        print("  ✓ Instruments loaded\n")
        
        # Step 3 - Create simple patterns
        print("[3/7] Creating drum pattern...")
        tcp("create_drum_pattern", {
            "track_index": 0,
            "clip_index": 0,
            "pattern": "one_drop",
            "length": 4
        })
        print("  ✓ Drum pattern created\n")
        
        print("[4/7] Creating bass pattern...")
        tcp("create_clip", {"track_index": 1, "clip_index": 0, "length": 4})
        # Simple bass notes
        notes = []
        for beat in [0, 1, 2, 3]:
            notes.append({
                "pitch": 36,
                "start_time": beat * 1.0,
                "duration": 1.0,
                "velocity": 90
            })
        tcp("add_notes_to_clip", {
            "track_index": 1,
            "clip_index": 0,
            "notes": notes
        })
        print("  ✓ Bass line created\n")
        
        print("[5/7] Creating chord progression...")
        tcp("create_clip", {"track_index": 2, "clip_index": 0, "length": 4})
        tcp("create_chord_notes", {
            "track_index": 2,
            "clip_index": 0,
            "root_note": 48,
            "chord_type": "min7",
            "start_time": 0,
            "duration": 4.0,
            "velocity": 75
        })
        print("  ✓ Chord clip created\n")
        
        print("[6/7] Creating lead melody...")
        tcp("create_clip", {"track_index": 3, "clip_index": 0, "length": 4})
        lead_notes = []
        for beat in [0, 2]:
            lead_notes.append({
                "pitch": 60 + beat,
                "start_time": beat * 1.0,
                "duration": 0.5,
                "velocity": 80
            })
        tcp("add_notes_to_clip", {
            "track_index": 3,
            "clip_index": 0,
            "notes": lead_notes
        })
        print("  ✓ Lead melody created\n")
        
        # Step 4 - Capture to arrangement
        print("[7/7] Capturing session to arrangement...")
        result = tcp("capture_and_insert_arrangement", {
            "start_bar": 0,
            "length_bars": 16,
            "quantize": True
        })
        print(f"  Status: {result.get('status', 'unknown')}")
        print("  ✓ Arrangement created\n")
        
        # Step 5 - Add automation
        print("[BONUS] Adding automation...")
        tcp("create_volume_automation_ramp", {
            "track_index": -1,
            "start_bar": 0,
            "end_bar": 4,
            "start_volume": 0.0,
            "end_volume": 0.8,
            "curve_type": "s_curve"
        })
        print("  ✓ Master volume fade-in added\n")
        
        print("=" * 70)
        print("DEMO COMPLETE!")
        print("=" * 70)
        print("\nYour arrangement is ready for manual fine-tuning in Ableton.")
        print("\nIn AbletonLive:")
        print("  - Press TAB to switch to Arrangement View")
        print("  - You should see 16 bars of audio/MIDI clips")
        print("  - Master volume automation starts at 0 and fades in")
        print("  - All 4 tracks have content")
        print("\nFile locations:")
        print("  - Tracks: Drums, Bass, Chords, Lead")
        print("  - Arrangement: 0-16 bars")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
