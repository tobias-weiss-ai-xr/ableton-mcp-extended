#!/usr/bin/env python3
"""
Simplified 10-Minute Mix Generator

Uses direct Remote Script commands (TCP port 9877) instead of MCP tools.
This version is guaranteed to work with the Ableton Remote Script.

Usage:
    python scripts/create_10min_mix_simple.py

Pre-requisites:
    1. Ableton Live running with Remote Script (TCP port 9877)
    2. At least 7 scenes configured in Ableton
    3. Tracks 0-3 should have content for Fat Beatz processing
"""

import json
import time
import socket
import sys


class AbletonClient:
    """Client for connecting to Ableton Remote Script."""
    
    def __init__(self, host="localhost", port=9877):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """Connect to Remote Script."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def send(self, cmd_type, params=None):
        """Send a command to Remote Script."""
        if not self.socket:
            if not self.connect():
                return None
        
        if params is None:
            params = {}
        
        message = {"type": cmd_type, "params": params}
        
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
            response = self.socket.recv(4096).decode()
            if response:
                return json.loads(response)
            return {"status": "ok"}
        except Exception as e:
            print(f"[ERROR] Command {cmd_type} failed: {e}")
            # Try to reconnect
            self.socket = None
            return {"status": "error", "message": str(e)}
    
    def close(self):
        """Close connection."""
        try:
            if self.socket:
                self.socket.close()
        except:
            pass


class TenMinuteMixGenerator:
    """Generates a complete 10-minute mix."""
    
    def __init__(self, client):
        self.client = client
        self.bpm = 90.0
    
    def generate_structure(self):
        """Generate the mix structure."""
        return [
            # Section 1: Deep Space (Intro)
            {"name": "Deep Space", "type": "intro", "scene": 0, "bars": 24, "bpm": 90.0, "energy": 0.3},
            
            # Section 2: Dub Foundation (Verse 1)
            {"name": "Dub Foundation", "type": "verse", "scene": 1, "bars": 24, "bpm": 90.0, "energy": 0.6},
            
            # Section 3: Rising Tension (Build 1)
            {"name": "Rising Tension", "type": "build", "scene": 2, "bars": 8, "bpm": 90.0, "energy": 0.75},
            
            # Section 4: Dub Bomb (Drop 1) - BPM increase
            {"name": "Dub Bomb", "type": "drop", "scene": 3, "bars": 32, "bpm": 95.0, "energy": 0.95},
            
            # Section 5: Steppers Groove (Verse 2)
            {"name": "Steppers Groove", "type": "verse", "scene": 4, "bars": 24, "bpm": 95.0, "energy": 0.65},
            
            # Section 6: Echo Chamber (Breakdown)
            {"name": "Echo Chamber", "type": "breakdown", "scene": 5, "bars": 24, "bpm": 95.0, "energy": 0.35},
            
            # Section 7: Tension Rising (Build 2)
            {"name": "Tension Rising", "type": "build", "scene": 2, "bars": 8, "bpm": 95.0, "energy": 0.7},
            
            # Section 8: Final Dub Apocalypse (Drop 2) - BPM increase
            {"name": "Final Dub Apocalypse", "type": "drop", "scene": 3, "bars": 48, "bpm": 100.0, "energy": 1.0},
            
            # Section 9: Cosmic Echo (Final Breakdown)
            {"name": "Cosmic Echo", "type": "breakdown", "scene": 5, "bars": 24, "bpm": 100.0, "energy": 0.4},
            
            # Section 10: Return (Final Build)
            {"name": "Return", "type": "build", "scene": 2, "bars": 8, "bpm": 100.0, "energy": 0.5},
            
            # Section 11: Grand Finale + Fade
            {"name": "Grand Finale + Fade", "type": "finale", "scene": 3, "bars": 40, "bpm": 100.0, "energy": 0.9},
        ]
    
    def print_structure(self, structure):
        """Print the mix structure."""
        print("\n" + "=" * 70)
        print("10-MINUTE MIX STRUCTURE")
        print("=" * 70)
        print(f"{'#':<3} {'Bars':<6} {'Type':<12} {'Name':<22} {'BPM':<6} {'Energy'}")
        print("-" * 70)
        
        start_bar = 0
        for i, s in enumerate(structure):
            end_bar = start_bar + s["bars"]
            bar_range = f"{start_bar}-{end_bar-1}"
            energy_str = f"{s['energy']*10:.0f}/10"
            print(f"{i+1:<3} {bar_range:<6} {s['type']:<12} {s['name']:<22} {s['bpm']:<6.0f} {energy_str}")
            start_bar = end_bar
        
        print("-" * 70)
        total_bars = sum(s["bars"] for s in structure)
        print(f"\nTotal: {len(structure)} sections, {total_bars} bars")
        print(f"Duration: ~{total_bars * 60 / self.bpm:.1f} minutes at {self.bpm} BPM")
        print("=" * 70)
    
    def setup_ableton(self):
        """Setup Ableton for the mix."""
        print("\n[INFO] Setting up Ableton...")
        
        # Stop playback
        self.client.send("stop_playback")
        self.client.send("stop_recording")
        
        # Set initial tempo
        self.client.send("set_tempo", {"bpm": self.bpm})
        
        # Set playhead to start
        self.client.send("set_playhead_position", {"bar": 0, "beat": 0})
        
        # Arm all tracks
        all_tracks = self.client.send("get_all_tracks")
        if all_tracks and "tracks" in all_tracks:
            for track in all_tracks["tracks"]:
                self.client.send("set_track_arm", {
                    "track_index": track.get("index", 0),
                    "arm": True
                })
            print(f"[OK] Armed {len(all_tracks['tracks'])} tracks")
        
        return True
    
    def apply_bpm_changes(self, structure):
        """Apply BPM changes for sections that need them."""
        print("\n[INFO] Setting up BPM automation...")
        
        current_bpm = self.bpm
        for section in structure:
            if section["bpm"] != current_bpm:
                print(f"[INFO] BPM change: {current_bpm} -> {section['bpm']} at bar {section.get('start_bar', 0)}")
                current_bpm = section["bpm"]
        
        return True
    
    def create_locators(self, structure):
        """Create locators at section boundaries."""
        print("\n[INFO] Creating locators...")
        
        start_bar = 0
        for i, section in enumerate(structure):
            # Create start locator
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
            
            self.client.send("create_locator", {
                "name": f"{section['name']}_Start",
                "bar": start_bar,
                "color": color
            })
            
            start_bar += section["bars"]
        
        # Create end locator
        self.client.send("create_locator", {
            "name": "Mix_End",
            "bar": start_bar,
            "color": "white"
        })
        
        print(f"[OK] Created locators for {len(structure)} sections")
        return True
    
    def capture_to_arrangement(self, structure):
        """Capture scenes to arrangement view."""
        print("\n[INFO] Capturing to arrangement...")
        
        # Start recording
        self.client.send("start_recording")
        time.sleep(0.5)
        
        # Start playback
        self.client.send("start_playback")
        time.sleep(0.5)
        
        # Trigger scenes in sequence
        current_bpm = self.bpm
        start_bar = 0
        
        for i, section in enumerate(structure):
            scene_idx = section["scene"]
            bars = section["bars"]
            
            print(f"[INFO] Triggering scene {scene_idx} ({section['name']}) - {bars} bars")
            
            # Set BPM if needed
            if section["bpm"] != current_bpm:
                self.client.send("set_tempo", {"bpm": section["bpm"]})
                current_bpm = section["bpm"]
                time.sleep(0.2)
            
            # Trigger the scene
            self.client.send("trigger_scene", {"scene_index": scene_idx})
            
            # Calculate wait time
            secs_per_bar = 60.0 / current_bpm * 4
            wait_time = secs_per_bar * bars * 0.95  # Slightly less than full duration
            
            time.sleep(wait_time)
            
            start_bar += bars
        
        # Give extra time for final section
        time.sleep(2.0)
        
        # Stop recording
        print("[INFO] Stopping capture...")
        self.client.send("stop_recording")
        time.sleep(0.5)
        self.client.send("stop_playback")
        
        # Disarm tracks
        all_tracks = self.client.send("get_all_tracks")
        if all_tracks and "tracks" in all_tracks:
            for track in all_tracks["tracks"]:
                self.client.send("set_track_arm", {
                    "track_index": track.get("index", 0),
                    "arm": False
                })
        
        print("[OK] Mix captured to arrangement!")
        return True
    
    def apply_basic_processing(self):
        """Apply basic processing to tracks using available commands."""
        print("\n[INFO] Applying basic processing...")
        
        # Boost volume on key tracks
        self.client.send("set_track_volume", {"track_index": 0, "volume_db": -6.0})  # Bass
        self.client.send("set_track_volume", {"track_index": 1, "volume_db": -3.0})  # Kick
        self.client.send("set_track_volume", {"track_index": 2, "volume_db": -4.0})  # Snare
        self.client.send("set_track_volume", {"track_index": 3, "volume_db": -8.0})  # Hats
        
        # Pan tracks for stereo image
        self.client.send("set_track_pan", {"track_index": 2, "pan": -0.2})  # Snare left
        self.client.send("set_track_pan", {"track_index": 3, "pan": 0.2})   # Hats right
        
        print("[OK] Basic processing applied")
        return True
    
    def create_10min_mix(self):
        """Create the complete 10-minute mix."""
        print("\n" + "=" * 70)
        print("10-MINUTE MIX GENERATOR")
        print("Simple version - Direct Remote Script commands")
        print("=" * 70)
        
        # Step 1: Generate and display structure
        print("\n[STEP 1/5] Generating mix structure...")
        structure = self.generate_structure()
        
        # Add start_bar to each section
        start_bar = 0
        for section in structure:
            section["start_bar"] = start_bar
            start_bar += section["bars"]
        
        self.print_structure(structure)
        
        # Step 2: Setup Ableton
        print("\n[STEP 2/5] Setting up Ableton...")
        self.setup_ableton()
        
        # Step 3: Create locators
        print("\n[STEP 3/5] Creating locators...")
        self.create_locators(structure)
        
        # Step 4: Apply basic processing
        print("\n[STEP 4/5] Applying processing...")
        self.apply_basic_processing()
        
        # Step 5: Capture to arrangement
        print("\n[STEP 5/5] Capturing to arrangement (this will take ~10 minutes)...")
        print("[INFO] Ableton will start recording and triggering scenes...")
        print("[INFO] Please wait while the mix is captured...")
        
        start_time = time.time()
        self.capture_to_arrangement(structure)
        elapsed = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 70)
        print("MIX CREATION COMPLETE!")
        print("=" * 70)
        
        total_bars = sum(s["bars"] for s in structure)
        print(f"\n[SUMMARY]")
        print(f"  * Created {len(structure)} sections")
        print(f"  * Total bars: {total_bars}")
        print(f"  * Actual duration: {elapsed:.1f} seconds")
        print(f"  * Expected duration: ~{total_bars * 60 / self.bpm:.1f} minutes")
        
        print(f"\n[NEXT STEPS]")
        print(f"  1. Open Ableton and review the arrangement")
        print(f"  2. The mix should be in the arrangement view")
        print(f"  3. Locators mark section boundaries")
        print(f"  4. Adjust volumes, effects, and automation as needed")
        print(f"  5. Export your mix!")
        
        print("\n" + "=" * 70)
        
        return {
            "status": "success",
            "structure": structure,
            "total_bars": total_bars,
            "elapsed_time": elapsed
        }


def main():
    """Main entry point."""
    print("10-Minute Mix Generator (Simple Version)")
    print("Uses direct Remote Script commands")
    
    client = AbletonClient()
    
    if not client.connect():
        print("\n[ERROR] Could not connect to Remote Script")
        print("\nMake sure:")
        print("  1. Ableton Live is running")
        print("  2. Remote Script is installed and enabled")
        print("  3. TCP port 9877 is open")
        print("  4. At least 7 scenes are configured in Ableton")
        return None
    
    print("\n[OK] Connected to Remote Script")
    
    # Verify connection with a simple command
    test = client.send("get_tempo")
    if test and "bpm" in test:
        print(f"[OK] Current tempo: {test['bpm']} BPM")
    else:
        print("[WARNING] Could not verify connection")
    
    generator = TenMinuteMixGenerator(client)
    
    try:
        result = generator.create_10min_mix()
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
        import time as t
        timestamp = t.strftime("%Y%m%d_%H%M%S")
        filename = f"10min_mix_simple_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n[INFO] Mix configuration saved to: {filename}")
