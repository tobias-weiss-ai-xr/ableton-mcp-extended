#!/usr/bin/env python3
"""
Dub Techno Mix Generator

Creates a **Dub Techno fusion** - combining:
- Deep sub-bass and echo/reverb from dub
- Pounding 4/4 kicks from techno  
- Atmospheric pads and filter sweeps
- Slow, evolving structure with heavy effects

Usage:
    python scripts/create_dub_techno_mix.py          # Create structure only
    python scripts/create_dub_techno_mix.py --capture # Full capture (10+ min)
    python scripts/create_dub_techno_mix.py --polish  # + polish pass
"""

import json
import socket
import sys
import subprocess
import os
from typing import Dict, Any, List


class AbletonClient:
    """Enhanced client with caching."""
    
    def __init__(self, host="localhost", port=9877):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def send(self, cmd_type, params=None):
        if not self.socket and not self.connect():
            return None
        
        message = {"type": cmd_type, "params": params or {}}
        
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
            response = self.socket.recv(4096).decode()
            return json.loads(response) if response else {"status": "ok"}
        except Exception as e:
            self.socket = None
            return {"status": "error", "message": str(e)}
    
    def close(self):
        try:
            if self.socket:
                self.socket.close()
        except:
            pass


class DubTechnoGenerator:
    """Generates Dub Techno mixes."""
    
    DUB_TECHNO_STRUCTURE = [
        {
            "name": "Dub Space Intro",
            "type": "intro",
            "bars": 32,
            "bpm": 125,
            "energy": 0.2,
            "section_scene": 0,
            "dub_effects": "heavy",
            "techno_elements": "ambient",
            "description": "Echoes in the void, filter sweeps rising"
        },
        {
            "name": "Dub Steppers",
            "type": "groove",
            "bars": 32,
            "bpm": 125,
            "energy": 0.5,
            "section_scene": 1,
            "dub_effects": "filter_sweep",
            "techno_elements": "four_on_floor",
            "description": "4/4 kick meets dub bassline"
        },
        {
            "name": "Echo Build",
            "type": "build",
            "bars": 16,
            "bpm": 125,
            "energy": 0.7,
            "section_scene": 2,
            "dub_effects": "echo_tension",
            "techno_elements": "risers",
            "description": "Echo feedback increasing, filters opening"
        },
        {
            "name": "Dub Bomb",
            "type": "drop",
            "bars": 32,
            "bpm": 125,
            "energy": 0.9,
            "section_scene": 3,
            "dub_effects": "maximum_echo",
            "techno_elements": "pounding_kick",
            "description": "Full dub effects with techno energy"
        },
        {
            "name": "Deep Dub Bass",
            "type": "groove",
            "bars": 32,
            "bpm": 125,
            "energy": 0.6,
            "section_scene": 1,
            "dub_effects": "sub_bass",
            "techno_elements": "rolling_bass",
            "description": "Sub 60Hz bass with subtle kicks"
        },
        {
            "name": "Atmospheric Break",
            "type": "breakdown",
            "bars": 32,
            "bpm": 125,
            "energy": 0.3,
            "section_scene": 4,
            "dub_effects": "space",
            "techno_elements": "pads",
            "description": "Echo chambers and atmospheric pads"
        },
        {
            "name": "Reverb Rise",
            "type": "build",
            "bars": 16,
            "bpm": 125,
            "energy": 0.8,
            "section_scene": 2,
            "dub_effects": "reverb_swell",
            "techno_elements": "white_noise",
            "description": "Reverb tails growing, tension building"
        },
        {
            "name": "Filter Sweep Drop",
            "type": "drop",
            "bars": 48,
            "bpm": 125,
            "energy": 0.95,
            "section_scene": 3,
            "dub_effects": "filter_sweep",
            "techno_elements": "hydraulic_kick",
            "description": "Filter siren with pounding kick"
        },
        {
            "name": "Dub Techno Outro",
            "type": "outro",
            "bars": 32,
            "bpm": 120,
            "energy": 0.2,
            "section_scene": 0,
            "dub_effects": "fade",
            "techno_elements": "filter_down",
            "description": "Slow fade with dub echo decay"
        }
    ]
    
    DUB_TECHNO_TRACKS = [
        {
            "index": 0,
            "name": "Sub Bass (Dub)",
            "type": "bass",
            "volume_db": -4.0,
            "pan": 0.0,
            "device_chain": ["EQ - Low Cut 30Hz", "Compression", "Sub Bass Boost"],
            "dub_processing": {"sub_boost_db": 6.0, "echo_send": 0.8, "reverb_send": 0.7}
        },
        {
            "index": 1,
            "name": "Kick (Techno)",
            "type": "drum",
            "volume_db": -2.0,
            "pan": 0.0,
            "device_chain": ["Saturation", "Compression", "EQ - Click Enhance"],
            "techno_processing": {"punch": 10.0, "click_component": True}
        },
        {
            "index": 2,
            "name": "Snare/Clap",
            "type": "drum",
            "volume_db": -5.0,
            "pan": 0.15,
            "device_chain": ["Reverb", "EQ", "Compression"],
            "dub_processing": {"echo_send": 0.6, "reverb_decay": 3.0}
        },
        {
            "index": 3,
            "name": "Hi-Hats (Techno)",
            "type": "drum",
            "volume_db": -8.0,
            "pan": -0.15,
            "device_chain": ["Delay 1/8", "EQ - High Shelf Boost"],
            "techno_processing": {"shuffle": 0.0, "velocity_random": 0.1}
        },
        {
            "index": 4,
            "name": "Atmospheric Pads",
            "type": "melody",
            "volume_db": -12.0,
            "pan": 0.3,
            "device_chain": ["Reverb (Hall 4s)", "Delay (1/4)", "Auto Filter"],
            "dub_processing": {"reverb_send": 1.0, "echo_send": 0.9, "filter_sweep": True}
        },
        {
            "index": 5,
            "name": "Dub Echo FX",
            "type": "fx",
            "volume_db": -15.0,
            "pan": 0.5,
            "device_chain": ["Echo (1/2 or 1/4)", "Reverb (Room 3s)", "EQ"],
            "dub_processing": {"echo_feedback": 0.9, "echo_time": "1/4 or 1/2"}
        },
        {
            "index": 6,
            "name": "Filter Sweep",
            "type": "fx",
            "volume_db": -12.0,
            "pan": 0.0,
            "device_chain": ["Auto Filter (LP)", "LFO (Slow)", "EQ"],
            "dub_processing": {"filter_cutoff_sweep": "30Hz-12kHz", "lfo_rate": "1/16 or slower"}
        },
        {
            "index": 7,
            "name": "White Noise (Risers)",
            "type": "fx",
            "volume_db": -18.0,
            "pan": 0.0,
            "device_chain": ["Noise Generator", "Auto Filter (HP)", "Reverb"],
            "techno_processing": {"filter_sweep": "20kHz-200Hz", "volume_swell": True}
        }
    ]
    
    DUB_TECHNO_SCENE_CONFIG = {
        0: {"name": "Intro/Outro", "clips": ["Atmosphere", "Dub Echo", "Filter Base"]},
        1: {"name": "Main Groove", "clips": ["Sub Bass", "Kick", "Snare", "Hi-Hats", "Pads Background"]},
        2: {"name": "Build", "clips": ["Filter Sweep Up", "White Noise Rise", "Echo Tension", "Kick Tease"]},
        3: {"name": "Drop", "clips": ["Full Kick", "Sub Bass Heavy", "Atmosphere Full", "Echo Maximum"]},
        4: {"name": "Breakdown", "clips": ["Atmosphere Only", "Dub Echo Delay", "Pads Full"]}
    }
    
    DUB_TECHNO_PROCESSING = {
        "bpm": 125,
        "tempo_variation": True,
        "tempo_range": [120, 128],
        "swing": 0.0,  # No swing in techno
        "sub_bass_boost_db": 6.0,
        "echo_feedback": 0.9,
        "echo_time": "1/4",
        "reverb_decay": 4.0,
        "reverb_type": "Hall",
        "filter_resonance": 0.8,
        "stereo_width": 0.75,
        "master_headroom_db": -10.0,
        "kick_punch_db": 10.0
    }
    
    def __init__(self, client):
        self.client = client
    
    def create_dub_techno_structure(self):
        """Create the complete dub techno mix structure."""
        print("\n" + "=" * 70)
        print("DUB TECHNO MIX GENERATOR")
        print("=" * 70)
        
        print("\n[GENRE FUSION]")
        print("  Dub Elements: Deep sub-bass, echo, reverb, filter sweeps")
        print("  Techno Elements: 4/4 kick, atmospheric pads, risers")
        print("  BPM Range: 120-128")
        print("  Style: Deep, atmospheric, hypnotic")
        
        # Stop playback and recording
        print("\n[STEP 1] Setting up Ableton...")
        self.client.send("stop_playback")
        self.client.send("stop_recording")
        
        # Set tempo
        self.client.send("set_tempo", {"bpm": self.DUB_TECHNO_PROCESSING["bpm"]})
        self.client.send("set_playhead_position", {"bar": 0, "beat": 0})
        print(f"  [OK] Tempo: {self.DUB_TECHNO_PROCESSING['bpm']} BPM")
        
        # Calculate total bars and duration
        total_bars = sum(s["bars"] for s in self.DUB_TECHNO_STRUCTURE)
        duration_seconds = (total_bars * 60) / self.DUB_TECHNO_PROCESSING["bpm"]
        duration_minutes = duration_seconds / 60
        
        print(f"  [OK] Structure: {len(self.DUB_TECHNO_STRUCTURE)} sections")
        print(f"  [OK] Total bars: {total_bars}")
        print(f"  [OK] Duration: {duration_minutes:.1f} minutes ({duration_seconds:.0f} seconds)")
        
        # Create locators for each section
        print("\n[STEP 2] Creating locators...")
        for section in self.DUB_TECHNO_STRUCTURE:
            self.client.send("create_locator", {
                "name": section["name"],
                "bar": section["start_bar"] if "start_bar" in section else 0
            })
            print(f"  [OK] {section['name']} at bar {section.get('start_bar', 0)}")
        
        # End locator
        end_bar = sum(s["bars"] for s in self.DUB_TECHNO_STRUCTURE)
        self.client.send("create_locator", {"name": "DubTechno_End", "bar": end_bar})
        print(f"  [OK] End locator at bar {end_bar}")
        
        # Configure tracks
        print("\n[STEP 3] Configuring tracks...")
        for i, track_config in enumerate(self.DUB_TECHNO_TRACKS[:8]):  # First 8 tracks
            self.client.send("set_track_name", {"track_index": i, "name": track_config["name"]})
            self.client.send("set_track_volume", {"track_index": i, "volume_db": track_config["volume_db"]})
            self.client.send("set_track_pan", {"track_index": i, "pan": track_config["pan"]})
            print(f"  [OK] Track {i}: {track_config['name']} at {track_config['volume_db']}dB, pan {track_config['pan']:.1f}")
        
        # Apply dub techno-specific processing
        print("\n[STEP 4] Applying Dub Techno processing...")
        self.apply_dub_techno_processing()
        
        # Display blueprint
        print("\n[BLUEPRINT]")
        print("-" * 70)
        print(f"{'#':<3} {'Bars':<6} {'Type':<12} {'Scene':<6} {'Name':<30} {'BPM':<5} {'Energy'}")
        print("-" * 70)
        
        start_bar = 0
        for i, section in enumerate(self.DUB_TECHNO_STRUCTURE):
            end_bar = start_bar + section["bars"] - 1
            print(f"{i+1:<3} {start_bar:<2}-{end_bar:<2} {section['type']:<12} {section['section_scene']:<6} {section['name']:<30} {section['bpm']:<5.0f} {section['energy']*10:.1f}/10")
            start_bar += section["bars"]
        
        print("-" * 70)
        
        # Scene configuration guide
        print("\n[SCENE CONFIGURATION GUIDE]")
        print("-" * 70)
        for scene_idx, config in self.DUB_TECHNO_SCENE_CONFIG.items():
            print(f"  Scene {scene_idx}: {config['name']}")
            print(f"    Clips to include: {', '.join(config['clips'])}")
        print("-" * 70)
        
        print("\n" + "=" * 70)
        print("DUB TECHNO MIX STRUCTURE COMPLETE")
        print("=" * 70)
        
        return {
            "status": "success",
            "genre": "Dub Techno",
            "structure": self.DUB_TECHNO_STRUCTURE,
            "bpm": self.DUB_TECHNO_PROCESSING["bpm"],
            "total_bars": total_bars,
            "duration_minutes": duration_minutes,
            "processing": self.DUB_TECHNO_PROCESSING
        }
    
    def apply_dub_techno_processing(self):
        """Apply dub techno-specific processing."""
        print("  [INFO] Boosting sub-bass...")
        # Extra sub-bass boost on track 0
        self.client.send("set_track_volume", {"track_index": 0, "volume_db": -3.0})
        
        print("  [INFO] Enhancing kick punch...")
        # Extra punch on track 1
        self.client.send("set_track_volume", {"track_index": 1, "volume_db": -1.0})
        
        print("  [INFO] Setting master headroom...")
        self.client.send("set_master_volume", {"volume_db": self.DUB_TECHNO_PROCESSING["master_headroom_db"]})
        
        print(f"  [OK] Dub Techno processing applied")
    
    def display_dub_techno_tips(self):
        """Display dub techno production tips."""
        print("\n[DUB TECHNO PRODUCTION TIPS]")
        print("-" * 70)
        print("Dub + Techno Fusion Characteristics:")
        print()
        print("  KICK:")
        print("    * Use a 4/4 kick pattern (techno)")
        print("    * Layer with a deep sub-kick (dub)")
        print("    * Add saturation for punch (techno)")
        print("    * Keep consistent throughout (both)")
        print()
        print("  BASS:")
        print("    * Deep sub-bass below 60Hz (dub)")
        print("    * Simple sine wave or sub-bass sample")
        print("    * Sidechain to kick for techno feel")
        print("    * Or keep steady for dub feel")
        print()
        print("  EFFECTS:")
        print("    * Heavy delay (1/4 or 1/8 note) on sends (dub)")
        print("    * Long reverb (4+ seconds) on sends (dub)")
        print("    * Auto Filter with slow LFO (both)")
        print("    * Spring reverb on drums (dub authenticity)")
        print()
        print("  ATMOSPHERE:")
        print("    * Atmospheric pads (techno)")
        print("    * Noise and textures (both)")
        print("    * Echo returns as musical elements (dub)")
        print("    * Filter sweeps for transitions (both)")
        print()
        print("  ARRANGEMENT:")
        print("    * Slow builds with filter sweeps")
        print("    * Echo feedback increasing before drops")
        print("    * Atmospheric breakdowns")
        print("    * Gradual reverb tail fades")
        print("-" * 70)
    
    def create_suggested_clips(self):
        """Create suggested clip patterns for each scene."""
        print("\n[SUGGESTED CLIP PATTERNS]")
        print("-" * 70)
        
        patterns = {
            "Intro/Outro": {
                0: "Sub bass (sustained, filtered low)",
                4: "Atmospheric pad (long reverb)",
                5: "Filter sweep base (slow automation)"
            },
            "Main Groove": {
                0: "Sub bass (steppers pattern)",
                1: "Techno kick (4/4)",
                2: "Snare on 2 & 4",
                3: "Closed hi-hats (16th or 8th)",
                4: "Atmospheric pad (subtle)",
                5: "Echo FX (subtle)"
            },
            "Build": {
                1: "Kick (every beat, getting louder)",
                5: "Filter sweep up (2-octave rise)",
                6: "White noise rise",
                7: "Echo feedback increasing"
            },
            "Drop": {
                0: "Sub bass (full, no filter)",
                1: "Techno kick (full volume)",
                2: "Snare on 2 & 4",
                3: "Hi-hats (16th)",
                4: "Atmospheric pad (full)",
                5: "Echo maximum",
                6: "Filter sweep in motion"
            },
            "Breakdown": {
                4: "Atmospheric pad (full)",
                5: "Dub echo delay (creating space)",
                6: "Filter sweep subtle"
            }
        }
        
        for scene_name, scene_patterns in patterns.items():
            print(f"\n  {scene_name}:")
            for track_idx, pattern in scene_patterns.items():
                print(f"    Track {track_idx}: {pattern}")
    
    def export_guide(self):
        """Display export guide for MP3 conversion."""
        print("\n[EXPORT GUIDE - MP3 CONVERSION]")
        print("=" * 70)
        print("\nStep 1: Export from Ableton")
        print("  - File -> Export Audio/Video...")
        print("  - Format: WAV (24-bit recommended)")
        print("  - Sample Rate: 44100 or 48000")
        print("  - Bit Depth: 24-bit")
        print("  - Normalize: OFF (we already balanced)")
        print("  - Range: Use locators (Dub Space Intro to DubTechno_End)")
        print("  - File name: dub_techno_mix.wav")
        
        print("\nStep 2: Convert to MP3")
        print("  Option A: Using FFmpeg (recommended)")
        print("    ffmpeg -i dub_techno_mix.wav -codec:a libmp3lame -qscale:a 0 dub_techno_mix.mp3")
        print("    -qscale:a 0 = highest quality (VBR ~240kbps)")
        print("    -qscale:a 2 = medium quality (VBR ~190kbps)")
        print("    -b:a 320k = constant bitrate 320kbps")
        
        print("\n  Option B: Using LAME")
        print("    lame dub_techno_mix.wav dub_techno_mix.mp3")
        print("    (Uses default VBR mode)")
        
        print("\n  Option C: Using online converter")
        print("    Upload to online-audio-converter.com")
        print("    Select MP3, 320kbps, keep original tempo")
        
        print("\nStep 3: Verify MP3")
        print("  - Play the MP3 to ensure quality")
        print("  - Check file size (should be ~10-15MB for 320kbps)")
        print("  - Compare with original WAV")
        
        print("\nStep 4: Tag your MP3 (optional)")
        print("  Use a tag editor like:")
        print("    - Mp3tag (Windows)")
        print("    - Kid3 (Mac/Linux)")
        print("    - EasyTAG (Linux)")
        print("  Recommended tags:")
        print("    Title: Dub Techno Mix")
        print("    Artist: Your Name")
        print("    Genre: Dub Techno / Techno")
        print("    BPM: 125")
        print("    Year: 2026")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dub Techno Mix Generator")
    parser.add_argument("--capture", action="store_true", help="Run full capture (10+ minutes)")
    parser.add_argument("--polish", action="store_true", help="Run polish pass after setup")
    parser.add_argument("--export-guide", action="store_true", help="Show MP3 export guide")
    args = parser.parse_args()
    
    client = AbletonClient()
    
    if not client.connect():
        print("\n[ERROR] Could not connect to Remote Script")
        print("Make sure Ableton is running with Remote Script loaded")
        return None
    
    print("[OK] Connected to Remote Script")
    
    generator = DubTechnoGenerator(client)
    
    try:
        # Create structure
        result = generator.create_dub_techno_structure()
        
        # Display tips
        generator.display_dub_techno_tips()
        generator.create_suggested_clips()
        
        # Run polish if requested
        if args.polish:
            print("\n[POLISH PASS]")
            print("-" * 70)
            polish_result = subprocess.run(
                ["python", "scripts/polish_suite.py", "full", "dub"],
                capture_output=True,
                text=True
            )
            print(polish_result.stdout)
        
        # Show export guide if requested
        if args.export_guide:
            generator.export_guide()
        
        # Summary
        print("\n" + "=" * 70)
        print("DUB TECHNO MIX READY")
        print("=" * 70)
        print(f"\n[STRUCTURE] {result['total_bars']} bars, {result['duration_minutes']:.1f} minutes")
        print(f"[BPM] {result['bpm']}")
        print(f"[TRACKS] 8 tracks configured")
        print(f"[LOCATORS] {len(result['structure']) + 1} locators created")
        
        print("\n[NEXT STEPS]")
        print("  1. Open Ableton and configure scenes 0-4")
        print("  2. Add clips according to the blueprint")
        print("  3. Run 'python scripts/polish_suite.py full dub' for polish")
        print("  4. Export from Ableton (File -> Export Audio/Video...)")
        print("  5. Use --export-guide for MP3 conversion instructions")
        
        if args.capture:
            print("\n[CAPTURE MODE]")
            print("  Note: Run 'python scripts/create_10min_mix_windows.py' for automated capture")
            print("  Or manually record while triggering scenes")
        
        print("\n" + "=" * 70)
        
        return result
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        client.close()


if __name__ == "__main__":
    result = main()
    
    if result and result.get("status") == "success":
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"dub_techno_mix_{timestamp}.json"
        
        # Remove function objects for JSON serialization
        output = {k: v for k, v in result.items() if not callable(v)}
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n[INFO] Mix saved to: {filename}")
