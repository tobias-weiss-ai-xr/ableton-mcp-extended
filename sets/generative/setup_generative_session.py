#!/usr/bin/env python
"""Automated setup for Generative Dub Techno System."""

import sys
import os
import time

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from dub_techno_2h.generative.config import TEMPO, PATTERN_DURATIONS, CLIPS_PER_TRACK
from dub_techno_2h.generative.mcp_client import MCPClient
from dub_techno_2h.generative.pattern_generator import PatternGenerator
from dub_techno_2h.generative.follow_action_setup import FollowActionSetup

TRACK_NAMES = ["Kick", "Sub-bass", "Hi-hats", "Synth Pads", "FX", "Dub Delays"]
BASS_ROOTS = [36, 38, 41, 43]
HIHAT_DENSITIES = ["sparse", "medium", "dense", "evolving"]
PAD_CHORD_TYPES = ["minor", "major", "diminished"]
FX_TYPES = ["sweep", "impact", "riser", "mixed"]

def setup():
    print("=" * 60)
    print("GENERATIVE DUB TECHNO - SESSION SETUP")
    print("=" * 60)
    
    generator = PatternGenerator()
    
    with MCPClient() as client:
        print("\n[1/7] Setting tempo to 126 BPM...")
        client.tcp_command("set_tempo", {"tempo": TEMPO})
        
        print("[2/7] Clearing existing tracks...")
        client.tcp_command("delete_all_tracks", {})
        time.sleep(0.3)
        
        print("[3/7] Creating 6 MIDI tracks...")
        for i, name in enumerate(TRACK_NAMES):
            client.tcp_command("create_midi_track", {"index": -1})
            client.tcp_command("set_track_name", {"track_index": i, "name": name})
        print("      Created 6 tracks")
        
        print("[4/7] Creating 48 clips with generated patterns...")
        for track_idx in range(6):
            for clip_idx in range(CLIPS_PER_TRACK):
                bars = PATTERN_DURATIONS[clip_idx % 3]
                length = bars * 4.0
                
                client.tcp_command("create_clip", {
                    "track_index": track_idx,
                    "clip_index": clip_idx,
                    "length": length
                })
                
                if track_idx == 0:
                    notes = generator.generate_kick(bars)
                elif track_idx == 1:
                    notes = generator.generate_bass(bars, BASS_ROOTS[clip_idx % 4])
                elif track_idx == 2:
                    notes = generator.generate_hihat(bars, HIHAT_DENSITIES[clip_idx % 4])
                elif track_idx == 3:
                    notes = generator.generate_pads(bars, PAD_CHORD_TYPES[clip_idx % 3])
                else:
                    notes = generator.generate_fx(bars, FX_TYPES[clip_idx % 4])
                
                if notes:
                    client.tcp_command("add_notes_to_clip", {
                        "track_index": track_idx,
                        "clip_index": clip_idx,
                        "notes": notes
                    })
                
                name = f"{TRACK_NAMES[track_idx][:3]}_{bars}bar_{clip_idx+1}"
                client.tcp_command("set_clip_name", {
                    "track_index": track_idx,
                    "clip_index": clip_idx,
                    "name": name
                })
                
                done = track_idx * 8 + clip_idx + 1
                if done % 12 == 0:
                    print(f"      {done}/48 clips...")
        print("      Created 48 clips")
        
        print("[5/7] Configuring follow actions...")
        fas = FollowActionSetup(client)
        fas.setup_all_chains()
        print("      Follow actions configured")
        
        print("[6/7] Setting initial volumes...")
        for i in range(6):
            client.send("set_track_volume", {"track_index": i, "volume": 0.75})
        print("      Volumes set to 0.75")
        
        print("[7/7] Setup complete!")
        
        print("\n" + "=" * 60)
        print("SESSION READY!")
        print("  6 tracks | 48 clips | 126 BPM")
        print("  Pattern lengths: 3, 5, 7 bars (prime)")
        print("  Fire any clip to start!")
        print("=" * 60)

if __name__ == "__main__":
    setup()
