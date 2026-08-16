#!/usr/bin/env python3
"""
Smart 10-Minute Mix Generator

Intelligently adapts the mix structure based on:
- Available scenes in Ableton
- Track content analysis
- Randomized variations for unique mixes each time
- Energy balancing algorithms

Usage:
    python scripts/create_smart_mix.py
"""

import json
import time
import socket
import random
from typing import List, Dict, Any


class AbletonClient:
    """Enhanced client with tracking capabilities."""
    
    def __init__(self, host="localhost", port=9877):
        self.host = host
        self.port = port
        self.socket = None
        self.scenes_cache = None
        self.tracks_cache = None
    
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
            self.socket = None
            return {"status": "error", "message": str(e)}
    
    def get_scenes(self):
        """Get and cache scenes."""
        if self.scenes_cache is None:
            result = self.send("get_all_scenes")
            if result and "result" in result and "scenes" in result["result"]:
                self.scenes_cache = result["result"]["scenes"]
        return self.scenes_cache or []
    
    def get_tracks(self):
        """Get and cache tracks."""
        if self.tracks_cache is None:
            result = self.send("get_all_tracks")
            if result and "result" in result and "tracks" in result["result"]:
                self.tracks_cache = result["result"]["tracks"]
        return self.tracks_cache or []
    
    def get_scene_clips(self, scene_index):
        """Get clips in a specific scene."""
        # This would need to be implemented in Remote Script
        # For now, return mock data
        return {"clips": []}
    
    def close(self):
        try:
            if self.socket:
                self.socket.close()
        except:
            pass


class SmartMixGenerator:
    """Intelligently creates mix structures based on available resources."""
    
    BASE_ENERGY = {
        "intro": 0.3,
        "verse": 0.6,
        "build": 0.75,
        "drop": 0.95,
        "breakdown": 0.4,
        "finale": 0.85,
        "outro": 0.25
    }
    
    BASE_BARS = {
        "intro": 24,
        "verse": 24,
        "build": 8,
        "drop": 32,
        "breakdown": 24,
        "finale": 32,
        "outro": 16
    }
    
    # Scene type preferences
    SCENE_TYPE_MAP = {
        "intro": [0, 7],      # Atmospheric scenes
        "verse": [1, 4],      # Groove scenes
        "build": [2, 6],      # Tension scenes
        "drop": [3, 5],       # Full energy scenes
        "breakdown": [5, 7],  # Atmospheric/break scenes
        "finale": [3, 6],     # Full or variation scenes
        "outro": [0, 7]       # Atmospheric scenes (match intro)
    }
    
    # Transition types
    TRANSITIONS = [
        ("filter_sweep", 0.4),
        ("echo_build", 0.3),
        ("crossfade", 0.2),
        ("sudden", 0.1)
    ]
    
    def __init__(self, client: AbletonClient):
        self.client = client
        self.scenes = []
        self.tracks = []
        self.base_bpm = 90.0
        self.mood = "balanced"  # Can be: chill, balanced, intense
    
    def set_mood(self, mood: str):
        """Set the mood for the mix."""
        self.mood = mood
        if mood == "chill":
            self.base_bpm = 85.0
            self.BASE_ENERGY["drop"] = 0.85
            self.BASE_BARS["drop"] = 24
        elif mood == "intense":
            self.base_bpm = 100.0
            self.BASE_ENERGY["drop"] = 1.0
            self.BASE_BARS["drop"] = 40
        else:  # balanced
            self.base_bpm = 90.0
            self.BASE_ENERGY = {
                "intro": 0.3,
                "verse": 0.6,
                "build": 0.75,
                "drop": 0.95,
                "breakdown": 0.4,
                "finale": 0.85,
                "outro": 0.25
            }
            self.BASE_BARS = {
                "intro": 24,
                "verse": 24,
                "build": 8,
                "drop": 32,
                "breakdown": 24,
                "finale": 32,
                "outro": 16
            }
    
    def detect_available_scenes(self):
        """Detect what scenes are available in Ableton."""
        self.scenes = self.client.get_scenes()
        self.tracks = self.client.get_tracks()
        
        num_scenes = len(self.scenes)
        num_tracks = len(self.tracks)
        
        print(f"\n[DETECTION] Found {num_scenes} scenes and {num_tracks} tracks")
        
        # Print scene info
        for i, scene in enumerate(self.scenes):
            flags = []
            if scene.get("has_clips", False):
                flags.append("CLIPS")
            if scene.get("has_audio", False):
                flags.append("AUDIO")
            if scene.get("has_midi", False):
                flags.append("MIDI")
            flag_str = f" ({', '.join(flags)})" if flags else ""
            print(f"  Scene {i}: {scene.get('name', 'Unnamed')}{flag_str}")
        
        # Print track info
        for i, track in enumerate(self.tracks):
            print(f"  Track {i}: {track.get('name', 'Unnamed')} [{'Audio' if track.get('is_audio') else 'MIDI'}]")
        
        return num_scenes, num_tracks
    
    def choose_scene(self, section_type: str, used_scenes: List[int]) -> int:
        """Intelligently choose a scene for a section type."""
        # Get preferred scenes for this type
        preferred = self.SCENE_TYPE_MAP.get(section_type, [0])
        
        # Filter out already used scenes
        available = [s for s in preferred if s < len(self.scenes) and s not in used_scenes]
        
        # If no preferred scenes available, use any unused scene
        if not available:
            available = [s for s in range(len(self.scenes)) if s not in used_scenes]
        
        # If still none, reuse scenes
        if not available:
            available = list(range(len(self.scenes)))
        
        # Choose intelligently based on mood
        if self.mood == "chill":
            return min(available)  # Use lower-numbered scenes
        elif self.mood == "intense":
            return max(available)  # Use higher-numbered scenes
        else:
            return random.choice(available)  # Random for balanced
    
    def generate_smart_structure(self) -> List[Dict[str, Any]]:
        """
        Generate a smart mix structure based on available scenes.
        
        Pattern: Intro -> Verse -> Build -> Drop -> Verse -> Breakdown -> 
                 Build -> Drop -> Breakdown -> Build -> Finale -> Outro
        """
        # Standard pattern
        pattern = ["intro", "verse", "build", "drop", "verse", "breakdown", 
                   "build", "drop", "breakdown", "build", "finale", "outro"]
        
        # Adapts based on number of scenes
        num_scenes = len(self.scenes)
        if num_scenes < 4:
            # Minimal scenes - simpler structure
            pattern = ["intro", "verse", "build", "drop", "outro"]
        elif num_scenes < 6:
            # Limited scenes
            pattern = ["intro", "verse", "build", "drop", "verse", "breakdown", "drop", "outro"]
        
        # Generate structure
        structure = []
        used_scenes = []
        current_bar = 0
        current_bpm = self.base_bpm
        
        for i, section_type in enumerate(pattern):
            # Choose scene
            scene_idx = self.choose_scene(section_type, used_scenes)
            used_scenes.append(scene_idx)
            
            # Adapt section length based on number of sections
            total_sections = len(pattern)
            bar_multiplier = 1.0
            if total_sections > 10:
                bar_multiplier = 0.8  # Shorter sections for complex mixes
            elif total_sections < 8:
                bar_multiplier = 1.2  # Longer sections for simple mixes
            
            base_bars = self.BASE_BARS.get(section_type, 16) * bar_multiplier
            
            # Random variation (10-20%)
            bar_variation = int(base_bars * random.uniform(0.9, 1.1))
            bars = max(4, bar_variation)  # Minimum 4 bars
            
            # Energy with variation
            base_energy = self.BASE_ENERGY.get(section_type, 0.5)
            energy_variation = base_energy * random.uniform(0.9, 1.1)
            energy = min(1.0, max(0.1, energy_variation))
            
            # BPM changes for drops
            bpm = current_bpm
            if section_type == "drop" and i > 0:
                bpm = current_bpm + random.choice([0, 5, 10])
                current_bpm = bpm
            
            # Generate name
            names = {
                "intro": ["Deep Space", "Cosmic Dawn", "Atmosphere", "Void", "Echo Begins"],
                "verse": ["Dub Foundation", "Steppers", "Groove", "Bassline", "Rhythm"],
                "build": ["Rising Tension", "Filter Rise", "Echo Build", "Tension", "Ascent"],
                "drop": ["Dub Bomb", "Bass Apocalypse", "Echo Chamber", "Reverb Explosion", "Filter Sweep"],
                "breakdown": ["Echo Chamber", "Space", "Atmosphere", "Pause", "Silence"],
                "finale": ["Grand Finale", "Final Dub", "Maximum", "Peak", "Climax"],
                "outro": ["Dub Fade", "Fade Out", "Echo Exit", "Endless", "Closing"]
            }
            name = random.choice(names.get(section_type, [f"Section {i}"]))
            
            # Add transition
            transition = None
            if i > 0:
                trans_type, prob = random.choice(self.TRANSITIONS)
                if random.random() < prob:
                    transition = trans_type
            
            section = {
                "name": name,
                "section_type": section_type,
                "scene_index": scene_idx,
                "bars": bars,
                "bpm": bpm,
                "energy": round(energy, 2),
                "start_bar": current_bar,
                "transition": transition
            }
            
            structure.append(section)
            current_bar += bars
        
        return structure
    
    def add_variation(self, structure: List[Dict]) -> List[Dict]:
        """Add subtle variations to make the mix more interesting."""
        # Randomly add half-bar offsets
        for section in structure:
            if section["section_type"] in ["build", "breakdown"]:
                if random.random() < 0.3:
                    section["bars"] += random.choice([-2, -1, 1, 2])
                    section["bars"] = max(4, section["bars"])
        
        # Add fill sections
        extended = []
        for i, section in enumerate(structure):
            extended.append(section)
            
            # Add fills between certain sections
            if i < len(structure) - 1:
                next_section = structure[i + 1]
                fill_types = [
                    ("Intro", "Verse"),
                    ("Verse", "Build"),
                    ("Breakdown", "Build"),
                ]
                
                if (section["section_type"], next_section["section_type"]) in fill_types:
                    if random.random() < 0.5:
                        fill = {
                            "name": "Fill",
                            "section_type": "fill",
                            "scene_index": random.choice([0, 7, 5]),  # Atmospheric scenes
                            "bars": 4,
                            "bpm": section["bpm"],
                            "energy": (section["energy"] + next_section["energy"]) / 2,
                            "start_bar": section["start_bar"] + section["bars"],
                            "transition": "sudden"
                        }
                        extended.append(fill)
        
        # Recalculate start bars
        current_bar = 0
        for section in extended:
            section["start_bar"] = current_bar
            current_bar += section["bars"]
        
        return extended
    
    def apply_adaptive_processing(self, structure: List[Dict]):
        """Apply processing based on the generated structure."""
        print("\n[INFO] Applying adaptive processing...")
        
        # Count section types
        section_counts = {}
        for s in structure:
            stype = s["section_type"]
            section_counts[stype] = section_counts.get(stype, 0) + 1
        
        num_drops = section_counts.get("drop", 0)
        num_breakdowns = section_counts.get("breakdown", 0)
        
        # Apply dub processing intensity based on structure
        dub_intensity = min(1.0, num_drops * 0.25 + num_breakdowns * 0.2)
        
        print(f"[INFO] Dub intensity: {dub_intensity:.1f}")
        print(f"[INFO] Section counts: {section_counts}")
        
        # Apply track volume based on energy levels
        tracks = self.client.get_tracks()
        for i, track in enumerate(tracks[:4]):  # First 4 tracks
            # Base volume
            base_vol = -6.0
            
            # Adjust based on mood
            if self.mood == "chill":
                base_vol -= 2.0
            elif self.mood == "intense":
                base_vol += 1.0
            
            # Apply
            self.client.send("set_track_volume", {
                "track_index": i,
                "volume_db": base_vol + (i * 0.5)  # Spread out slightly
            })
        
        print(f"[OK] Adaptive processing applied")
        return True
    
    def create_smart_mix(self):
        """Create a smart, adaptive 10-minute mix."""
        print("\n" + "=" * 70)
        print("SMART 10-MINUTE MIX GENERATOR")
        print("=" * 70)
        print(f"\n[MODE] Mood: {self.mood.capitalize()}")
        
        # Step 1: Detect available resources
        print("\n[STEP 1/5] Detecting available scenes and tracks...")
        num_scenes, num_tracks = self.detect_available_scenes()
        
        if num_scenes < 2:
            print("[ERROR] Need at least 2 scenes. Please add more scenes to Ableton.")
            return None
        
        # Step 2: Generate smart structure
        print("\n[STEP 2/5] Generating adaptive mix structure...")
        structure = self.generate_smart_structure()
        structure = self.add_variation(structure)
        
        total_bars = sum(s["bars"] for s in structure)
        total_time = total_bars * 60 / self.base_bpm
        
        print(f"\n[STRUCTURE] {len(structure)} sections, {total_bars} bars")
        print(f"[ESTIMATE] {total_time:.1f} minutes at {self.base_bpm:.0f} BPM")
        
        # Display structure
        print("\n[BLUEPRINT]")
        print("-" * 70)
        print(f"{'#':<3} {'Bars':<6} {'Type':<12}({'Scene':<7}) {'Name':<18} {'BPM':<6} {'Energy':<8}")
        print("-" * 70)
        
        for i, s in enumerate(structure):
            trans = ""
            if s.get("transition"):
                trans = f" [{s['transition']}]"
            print(f"{i+1:<3} {s['start_bar']:<3}-{s['start_bar']+s['bars']-1:<3} {s['section_type']:<12}({s['scene_index']:<2}) {s['name']:<18} {s['bpm']:<6.0f} {s['energy']*10:.1f}/10{trans}")
        
        print("-" * 70)
        
        # Step 3: Setup Ableton
        print("\n[STEP 3/5] Setting up Ableton...")
        self.client.send("stop_playback")
        self.client.send("stop_recording")
        self.client.send("set_tempo", {"bpm": self.base_bpm})
        self.client.send("set_playhead_position", {"bar": 0, "beat": 0})
        print("[OK]")
        
        # Step 4: Create locators
        print("\n[STEP 4/5] Creating locators...")
        for section in structure:
            color = None
            if section["section_type"] == "drop":
                color = "red"
            elif section["section_type"] == "breakdown":
                color = "blue"
            elif section["section_type"] == "build":
                color = "yellow"
            elif section["section_type"] == "intro":
                color = "green"
            elif section["section_type"] == "outro":
                color = "green"
            
            self.client.send("create_locator", {
                "name": f"{section['name']}",
                "bar": section["start_bar"],
                "color": color
            })
        
        # End locator
        end_bar = structure[-1]["start_bar"] + structure[-1]["bars"]
        self.client.send("create_locator", {
            "name": "Mix_End",
            "bar": end_bar,
            "color": "white"
        })
        print(f"[OK] Created {len(structure) + 1} locators")
        
        # Step 5: Apply adaptive processing
        print("\n[STEP 5/5] Applying adaptive processing...")
        self.apply_adaptive_processing(structure)
        
        # Summary
        print("\n" + "=" * 70)
        print("SMART MIX CREATION COMPLETE!")
        print("=" * 70)
        
        # Statistics
        by_type = {}
        for s in structure:
            stype = s["section_type"]
            if stype not in by_type:
                by_type[stype] = 0
            by_type[stype] += 1
        
        print("\n[STATISTICS]")
        for stype, count in sorted(by_type.items()):
            total_type_bars = sum(s["bars"] for s in structure if s["section_type"] == stype)
            print(f"  {stype.capitalize()}: {count} sections ({total_type_bars} bars)")
        
        print(f"\n[CUSTOMIZATION]")
        print(f"  Mood: {self.mood}")
        print(f"  Base BPM: {self.base_bpm}")
        print(f"  Total sections: {len(structure)}")
        print(f"  Total bars: {total_bars}")
        
        sections_with_transitions = sum(1 for s in structure if s.get("transition"))
        print(f"  Sections with transitions: {sections_with_transitions}")
        
        print(f"\n[NEXT STEPS]")
        print(f"  1. Review the structure in Ableton")
        print(f"  2. Arm tracks and start recording")
        print(f"  3. Trigger scenes in sequence")
        print(f"  4. Or run: python scripts/capture_manual.py")
        
        print("\n" + "=" * 70)
        
        return {
            "status": "success",
            "structure": structure,
            "mood": self.mood,
            "base_bpm": self.base_bpm,
            "total_bars": total_bars,
            "total_time_minutes": total_time,
            "scenes_used": len(set(s["scene_index"] for s in structure)),
            "num_scenes_available": len(self.scenes),
            "num_tracks": len(self.tracks)
        }


def main():
    """Main entry point."""
    print("Smart 10-Minute Mix Generator")
    print("Generates adaptive mixes based on your Ableton setup")
    
    # Parse mood from command line
    mood = "balanced"
    if len(sys.argv) > 1:
        mood = sys.argv[1].lower()
        if mood not in ["chill", "balanced", "intense"]:
            mood = "balanced"
    
    client = AbletonClient()
    
    if not client.connect():
        print("\n[ERROR] Could not connect to Remote Script")
        return None
    
    print("\n[OK] Connected to Remote Script")
    
    generator = SmartMixGenerator(client)
    generator.set_mood(mood)
    
    try:
        result = generator.create_smart_mix()
        return result
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    
    result = main()
    
    if result and result.get("status") == "success":
        import time as t
        timestamp = t.strftime("%Y%m%d_%H%M%S")
        mood = result.get("mood", "balanced")
        filename = f"smart_mix_{mood}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n[INFO] Mix saved to: {filename}")
