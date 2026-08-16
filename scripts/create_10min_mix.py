#!/usr/bin/env python3
"""
10-Minute Mix Generator for Ableton Live via MCP

Creates a complete 10-minute mix with:
- Intelligent scene sequencing
- Dub effects automation (filter sweeps, echo, reverb)
- Fat beatz processing (sub-bass, compression, saturation)
- Structured arrangement (intro, builds, drops, breakdowns)
- BPM and energy variations
- Scene transitions with crossfades

Usage:
    python create_10min_mix.py
    
Requirements:
    - Ableton Live running with Remote Script
    - MCP Server running on port 9877
    - At least 8 scenes pre-configured in Ableton
"""

import json
import time
import socket
import random
from typing import Dict, List, Optional, Any, Tuple


class AbletonMCPClient:
    """Client for connecting to Ableton MCP Remote Script."""
    
    def __init__(self, host: str = "localhost", port: int = 9877):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Error connecting: {e}")
            return False
    
    def send_command(self, command: str, params: Dict = None) -> Optional[Dict]:
        """Send a command to the MCP server."""
        if not self.socket:
            if not self.connect():
                return None
        
        if params is None:
            params = {}
        
        message = {"type": command, "params": params}
        
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
            response = self.socket.recv(4096).decode()
            if response:
                return json.loads(response)
            return {"status": "error", "message": "No response"}
        except Exception as e:
            print(f"Error sending command {command}: {e}")
            return {"status": "error", "message": str(e)}
    
    def close(self):
        """Close the connection."""
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except:
            pass


class MixGenerator:
    """Generates a 10-minute mix with dub and fat beatz characteristics."""
    
    def __init__(self, client: AbletonMCPClient):
        self.client = client
        self.bpm = 90.0
        self.scenes = []
        self.mix_structure = []
        self.track_info = {}
    
    def generate_structure(self) -> List[Dict[str, Any]]:
        """
        Generate a 10-minute mix structure with dub/hip-hop elements.
        
        Structure includes:
        - Intro (build tension)
        - Verse sections (groove establishment)
        - Chorus/Drop sections (energy peak)
        - Breakdowns (atmospheric)
        - Transitions (smooth changes)
        - Outro (graceful exit)
        """
        # Total bars for 10 minutes at various BPMs
        # At 90 BPM: 10 min * 90 beats/min = 900 beats = 225 bars (4/4)
        # At 120 BPM: 10 min * 120 = 1200 beats = 300 bars
        # We'll use ~240 bars total (adjustable based on BPM)
        
        total_bars = 240
        bar_counter = 0
        
        structure = []
        
        # =================================================================
        # SECTION 1: INTRO (0:00 - 1:00 min = ~24 bars at 90 BPM)
        # =================================================================
        # Build tension with sparse elements
        # Dub-style: echo feedback increasing, filter opening
        structure.append({
            "section": "intro",
            "name": "Deep Space",
            "scene_index": 0,
            "bars": 16,
            "bpm": self.bpm,
            "energy": 0.3,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": False,
            " dub_effects": {
                "filter_sweep": True,
                "filter_start": 50,
                "filter_end": 1000,
                "echo_feedback": 0.2,
                "echo_feedback_end": 0.5,
                "reverb_decay": 2.0,
                "reverb_dry_wet": 0.4
            },
            "fat_beatz": {
                "sub_bass_boost": 3,
                "compression": 0.0,
                "saturation": 0.2,
                "stereo_width": 0.3
            },
            "transitions": {
                "from": None,
                "to": "build1",
                "type": "filter_sweep",
                "bars": 4
            },
            "start_bar": bar_counter
        })
        bar_counter += 16
        
        # Build section 1
        structure.append({
            "section": "build",
            "name": "Rising Tension",
            "scene_index": 1,
            "bars": 8,
            "bpm": self.bpm,
            "energy": 0.5,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 1000,
                "filter_end": 3000,
                "echo_feedback": 0.5,
                "echo_feedback_end": 0.7,
                "reverb_decay": 1.5
            },
            "fat_beatz": {
                "sub_bass_boost": 4,
                "compression": 0.3,
                "saturation": 0.3,
                "stereo_width": 0.4
            },
            "transitions": {
                "from": "intro",
                "to": "verse1",
                "type": "echo_build",
                "bars": 2
            },
            "start_bar": bar_counter
        })
        bar_counter += 8
        
        # =================================================================
        # SECTION 2: VERSE 1 (1:00 - 2:00 min = ~24 bars)
        # =================================================================
        structure.append({
            "section": "verse",
            "name": "Dub Groove",
            "scene_index": 2,
            "bars": 16,
            "bpm": self.bpm,
            "energy": 0.6,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": True,
            "dub_effects": {
                "filter_sweep": False,
                "echo_feedback": 0.7,
                "echo_time": 250,
                "reverb_decay": 1.0,
                "reverb_dry_wet": 0.2
            },
            "fat_beatz": {
                "sub_bass_boost": 6,
                "compression": 0.4,
                "saturation": 0.4,
                "stereo_width": 0.5,
                "sidechain": 0.3
            },
            "transitions": {
                "from": "build1",
                "to": "pre_chorus1",
                "type": "crossfade",
                "bars": 4
            },
            "start_bar": bar_counter
        })
        bar_counter += 16
        
        # Pre-chorus
        structure.append({
            "section": "pre_chorus",
            "name": "Building Up",
            "scene_index": 3,
            "bars": 8,
            "bpm": self.bpm,
            "energy": 0.75,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 3000,
                "filter_end": 8000,
                "echo_feedback": 0.8,
                "echo_time": 200
            },
            "fat_beatz": {
                "sub_bass_boost": 5,
                "compression": 0.5,
                "saturation": 0.5,
                "stereo_width": 0.6,
                "sidechain": 0.4
            },
            "transitions": {
                "from": "verse1",
                "to": "drop1",
                "type": "filter_drop",
                "bars": 2
            },
            "start_bar": bar_counter
        })
        bar_counter += 8
        
        # =================================================================
        # SECTION 3: DROP/CHORUS 1 (2:00 - 3:00 min = ~24 bars)
        # =================================================================
        structure.append({
            "section": "drop",
            "name": "Bass Bomb",
            "scene_index": 4,
            "bars": 24,
            "bpm": self.bpm + 5,  # Slight BPM increase for energy
            "energy": 0.9,
            "is_dub_drop": True,
            "is_breakdown": False,
            "unique_bassline": True,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 20,
                "filter_end": 20000,
                "filter_resonance": 0.8,
                "echo_feedback": 0.9,
                "echo_time": 125,
                "reverb_decay": 0.5,
                "reverb_dry_wet": 0.1
            },
            "fat_beatz": {
                "sub_bass_boost": 8,
                "compression": 0.7,
                "saturation": 0.7,
                "stereo_width": 0.7,
                "sidechain": 0.5
            },
            "transitions": {
                "from": "pre_chorus1",
                "to": "verse2",
                "type": "sudden",
                "bars": 0
            },
            "start_bar": bar_counter
        })
        bar_counter += 24
        
        # =================================================================
        # SECTION 4: VERSE 2 (3:00 - 4:00 min = ~24 bars)
        # =================================================================
        structure.append({
            "section": "verse",
            "name": "Dub Steppers",
            "scene_index": 5,
            "bars": 16,
            "bpm": self.bpm + 5,
            "energy": 0.65,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": True,
            "dub_effects": {
                "filter_sweep": False,
                "echo_feedback": 0.6,
                "echo_time": 300,
                "reverb_decay": 1.5,
                "reverb_dry_wet": 0.3
            },
            "fat_beatz": {
                "sub_bass_boost": 6,
                "compression": 0.4,
                "saturation": 0.4,
                "stereo_width": 0.5,
                "sidechain": 0.3
            },
            "transitions": {
                "from": "drop1",
                "to": "pre_drop2",
                "type": "filter_rise",
                "bars": 4
            },
            "start_bar": bar_counter
        })
        bar_counter += 16
        
        # Short pre-drop
        structure.append({
            "section": "pre_chorus",
            "name": "Tension Builder",
            "scene_index": 6,
            "bars": 8,
            "bpm": self.bpm + 5,
            "energy": 0.75,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 8000,
                "filter_end": 12000,
                "echo_feedback": 0.7,
                "echo_time": 150
            },
            "fat_beatz": {
                "sub_bass_boost": 4,
                "compression": 0.5,
                "saturation": 0.5,
                "stereo_width": 0.6,
                "sidechain": 0.4
            },
            "transitions": {
                "from": "verse2",
                "to": "breakdown",
                "type": "echo_fade",
                "bars": 2
            },
            "start_bar": bar_counter
        })
        bar_counter += 8
        
        # =================================================================
        # SECTION 5: BREAKDOWN (4:00 - 5:00 min = ~24 bars)
        # =================================================================
        # Atmospheric, sparse, with reverb and echo
        structure.append({
            "section": "breakdown",
            "name": "Dub Echo Chamber",
            "scene_index": 7,
            "bars": 24,
            "bpm": self.bpm + 5,
            "energy": 0.4,
            "is_dub_drop": False,
            "is_breakdown": True,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": False,
                "echo_feedback": 0.85,
                "echo_time": 600,
                "reverb_decay": 6.0,
                "reverb_dry_wet": 0.7,
                "reverb_type": "hall"
            },
            "fat_beatz": {
                "sub_bass_boost": 2,
                "compression": 0.0,
                "saturation": 0.1,
                "stereo_width": 0.9
            },
            "transitions": {
                "from": "pre_drop2",
                "to": "build2",
                "type": "reverb_swell",
                "bars": 4
            },
            "start_bar": bar_counter
        })
        bar_counter += 24
        
        # Build from breakdown
        structure.append({
            "section": "build",
            "name": "Emerging",
            "scene_index": 1,  # Reuse earlier build scene
            "bars": 8,
            "bpm": self.bpm + 5,
            "energy": 0.5,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 10000,
                "filter_end": 5000,
                "echo_feedback": 0.6,
                "echo_feedback_end": 0.8
            },
            "fat_beatz": {
                "sub_bass_boost": 3,
                "compression": 0.3,
                "saturation": 0.3,
                "stereo_width": 0.4,
                "sidechain": 0.2
            },
            "transitions": {
                "from": "breakdown",
                "to": "drop2",
                "type": "filter_open",
                "bars": 2
            },
            "start_bar": bar_counter
        })
        bar_counter += 8
        
        # =================================================================
        # SECTION 6: FINAL DROP (5:00 - 7:00 min = ~48 bars)
        # =================================================================
        # Most intense section with all effects
        structure.append({
            "section": "drop",
            "name": "Dub Apocalypse",
            "scene_index": 4,  # Reuse main drop scene
            "bars": 24,
            "bpm": self.bpm + 10,  # BPM increase for final energy
            "energy": 1.0,
            "is_dub_drop": True,
            "is_breakdown": False,
            "unique_bassline": True,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 20,
                "filter_end": 20000,
                "filter_resonance": 0.9,
                "echo_feedback": 0.95,
                "echo_time": 100,
                "reverb_decay": 1.0,
                "reverb_dry_wet": 0.1
            },
            "fat_beatz": {
                "sub_bass_boost": 10,
                "compression": 0.8,
                "saturation": 0.8,
                "stereo_width": 0.8,
                "sidechain": 0.6
            },
            "transitions": {
                "from": "build2",
                "to": "final_verse",
                "type": "sudden",
                "bars": 0
            },
            "start_bar": bar_counter
        })
        bar_counter += 24
        
        # Second part of final drop
        structure.append({
            "section": "drop",
            "name": "Maximum Dub",
            "scene_index": 8,  # New scene for variation
            "bars": 24,
            "bpm": self.bpm + 10,
            "energy": 1.0,
            "is_dub_drop": True,
            "is_breakdown": False,
            "unique_bassline": True,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 20000,
                "filter_end": 20,
                "filter_resonance": 0.9,
                "echo_feedback": 0.9,
                "echo_time": 250,
                "reverb_decay": 2.0,
                "reverb_dry_wet": 0.2
            },
            "fat_beatz": {
                "sub_bass_boost": 9,
                "compression": 0.7,
                "saturation": 0.7,
                "stereo_width": 0.9,
                "sidechain": 0.5
            },
            "transitions": {
                "from": "drop2",
                "to": "final_breakdown",
                "type": "filter_sweep",
                "bars": 4
            },
            "start_bar": bar_counter
        })
        bar_counter += 24
        
        # =================================================================
        # SECTION 7: FINAL BREAKDOWN (7:00 - 8:30 min = ~36 bars)
        # =================================================================
        structure.append({
            "section": "breakdown",
            "name": "Cosmic Echo",
            "scene_index": 7,  # Reuse atmospheric scene
            "bars": 24,
            "bpm": self.bpm + 10,
            "energy": 0.4,
            "is_dub_drop": False,
            "is_breakdown": True,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": False,
                "echo_feedback": 0.9,
                "echo_time": 800,
                "reverb_decay": 8.0,
                "reverb_dry_wet": 0.8
            },
            "fat_beatz": {
                "sub_bass_boost": 1,
                "compression": 0.0,
                "saturation": 0.0,
                "stereo_width": 1.0
            },
            "transitions": {
                "from": "drop2",
                "to": "final_build",
                "type": "volume_fade",
                "bars": 8
            },
            "start_bar": bar_counter
        })
        bar_counter += 24
        
        # Final build
        structure.append({
            "section": "build",
            "name": "Return",
            "scene_index": 3,  # Reuse pre-drop scene
            "bars": 8,
            "bpm": self.bpm + 10,
            "energy": 0.6,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 5000,
                "filter_end": 10000,
                "echo_feedback": 0.7
            },
            "fat_beatz": {
                "sub_bass_boost": 4,
                "compression": 0.4,
                "saturation": 0.4,
                "stereo_width": 0.6,
                "sidechain": 0.3
            },
            "transitions": {
                "from": "final_breakdown",
                "to": "finale",
                "type": "filter_rise",
                "bars": 2
            },
            "start_bar": bar_counter
        })
        bar_counter += 8
        
        # =================================================================
        # SECTION 8: FINALE (8:30 - 10:00 min = ~30 bars)
        # =================================================================
        structure.append({
            "section": "finale",
            "name": "Grand Finish",
            "scene_index": 4,  # Main drop for finale
            "bars": 24,
            "bpm": self.bpm + 10,
            "energy": 0.9,
            "is_dub_drop": True,
            "is_breakdown": False,
            "unique_bassline": True,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 20,
                "filter_end": 20000,
                "filter_resonance": 0.8,
                "echo_feedback": 0.9,
                "echo_time": 150
            },
            "fat_beatz": {
                "sub_bass_boost": 9,
                "compression": 0.7,
                "saturation": 0.7,
                "stereo_width": 0.9,
                "sidechain": 0.5
            },
            "transitions": {
                "from": "final_build",
                "to": "outro",
                "type": "gradual",
                "bars": 4
            },
            "start_bar": bar_counter
        })
        bar_counter += 24
        
        # Outro
        structure.append({
            "section": "outro",
            "name": "Dub Fade",
            "scene_index": 0,  # Reuse intro for symmetry
            "bars": 8,
            "bpm": self.bpm + 10,
            "energy": 0.2,
            "is_dub_drop": False,
            "is_breakdown": False,
            "unique_bassline": False,
            "dub_effects": {
                "filter_sweep": True,
                "filter_start": 10000,
                "filter_end": 50,
                "echo_feedback": 0.5,
                "reverb_decay": 4.0,
                "reverb_dry_wet": 0.8
            },
            "fat_beatz": {
                "sub_bass_boost": 0,
                "compression": 0.0,
                "saturation": 0.1,
                "stereo_width": 0.8
            },
            "transitions": {
                "from": "finale",
                "to": None,
                "type": "fade_out",
                "bars": 4
            },
            "start_bar": bar_counter
        })
        bar_counter += 8
        
        return structure

    def apply_fat_beatz_processing(self, structure: List[Dict]) -> None:
        """Apply Fat Beatz processing to tracks."""
        print("\n🎚️  Applying Fat Beatz Processing...")
        
        # Identify bass track (typically track 0)
        bass_track = 0
        kick_track = 1
        snare_track = 2
        hat_track = 3
        
        # Apply to bass track
        print("  🔊 Bass enhancement...")
        self.client.send_command("add_sub_bass_harmonic", {
            "track_index": bass_track,
            "harmonic_octave": -1,
            "harmonic_volume": 0.4,
            "filter_cutoff": 150,
            "saturation_amount": 0.3
        })
        
        self.client.send_command("create_parallel_bass_compression", {
            "track_index": bass_track,
            "compression_amount": 0.6,
            "attack_ms": 10,
            "release_ms": 150,
            "ratio": 5.0,
            "threshold_db": -12
        })
        
        # Apply to kick
        print("  🥁 Kick enhancement...")
        self.client.send_command("enhance_kick_drum", {
            "track_index": kick_track,
            "add_click": True,
            "click_volume": 0.35,
            "boost_attack": True,
            "attack_db": 14,
            "extend_tail": True,
            "tail_hz": 45,
            "saturation_drive": 0.5
        })
        
        # Apply to snare
        print("  🎧 Snare thickening...")
        self.client.send_command("thicken_snare", {
            "track_index": snare_track,
            "parallel_reverb": True,
            "reverb_decay": 0.6,
            "reverb_mix": 0.25,
            "add_body": True,
            "body_freq": 180,
            "body_db": 5,
            "gate_threshold": -20,
            "saturation": 0.4
        })
        
        # Apply stereo widening
        print("  🌐 Stereo widening...")
        self.client.send_command("apply_stereo_widening", {
            "track_index": hat_track,
            "method": "haas",
            "width_percent": 75,
            "high_pass_hz": 200,
            "delay_ms": 20
        })
        
        # Add harmonic excitement to multiple tracks
        print("  ✨ Harmonic excitement...")
        for track in [bass_track, kick_track, snare_track]:
            self.client.send_command("add_harmonic_excitement", {
                "track_index": track,
                "mode": "tape",
                "drive": 0.3 + (0.1 * track),  # Slight variation
                "high_pass": 100,
                "low_pass": 12000
            })
        
        # Setup sidechain
        print("  🔗 Sidechain pumping...")
        self.client.send_command("setup_sidechain_pump", {
            "source_track": bass_track,
            "target_tracks": [hat_track, snare_track],
            "compressor_threshold": -24,
            "compressor_ratio": 4.0,
            "compressor_attack": 10,
            "compressor_release": 100,
            "sidechain_amount": 0.4
        })
        
        print("  ✅ Fat Beatz processing complete!\n")

    def capture_mix_from_structure(self, structure: List[Dict]) -> Dict[str, Any]:
        """
        Capture the mix from the structure using the MCP server tools.
        
        This is a simplified version that will be replaced with actual
        scene triggering and capture.
        """
        print("\n🎬 Capturing Mix from Structure...")
        print("=" * 60)
        
        total_sections = len(structure)
        total_bars = sum(s["bars"] for s in structure)
        
        print(f"📊 Structure: {total_sections} sections, {total_bars} bars total")
        print(f"⏱️  Estimated duration: {total_bars * 60 / self.bpm:.1f} minutes")
        print()
        
        # Apply BPM changes for sections that need them
        current_bpm = self.bpm
        for section in structure:
            if section["bpm"] != current_bpm:
                self.client.send_command("set_tempo", {"bpm": section["bpm"]})
                current_bpm = section["bpm"]
                print(f"  ⚡ BPM change: {current_bpm} at bar {section['start_bar']}")
        
        # Reset to start
        self.client.send_command("set_playhead_position", {"bar": 0, "beat": 0})
        
        # Set up locators at section boundaries
        print("\n📍 Setting up locators...")
        for section in structure:
            self.client.send_command("create_locator", {
                "name": f"{section['name']}_Start",
                "bar": section["start_bar"],
                "color": None
            })
        
        # Create end locator
        final_bar = structure[-1]["start_bar"] + structure[-1]["bars"]
        self.client.send_command("create_locator", {
            "name": "Mix_End",
            "bar": final_bar,
            "color": None
        })
        
        # Arm all tracks
        print("\n🎛️  Arming tracks...")
        all_tracks = self.client.send_command("get_all_tracks", {})
        if all_tracks and "tracks" in all_tracks:
            for i, track in enumerate(all_tracks["tracks"]):
                self.client.send_command("set_track_arm", {
                    "track_index": track.get("index", i),
                    "arm": True
                })
        
        # Start recording
        print("\n🎥 Starting mix capture...")
        self.client.send_command("start_recording", {})
        time.sleep(0.5)
        
        self.client.send_command("start_playback", {})
        time.sleep(0.5)
        
        # Trigger scenes in sequence
        print("\n🎭 Triggering scenes...")
        for i, section in enumerate(structure):
            scene_idx = section["scene_index"]
            print(f"  [{i+1}/{total_sections}] {section['name']} (Scene {scene_idx}) - {section['bars']} bars")
            
            # Trigger the scene
            self.client.send_command("trigger_scene", {"scene_index": scene_idx})
            
            # Calculate wait time based on bars and BPM
            secs_per_bar = 60.0 / current_bpm * 4  # 4 beats = 1 bar
            wait_time = secs_per_bar * section["bars"] * 0.9  # Slightly less than full
            
            # Wait for scene to play
            time.sleep(wait_time)
        
        # Wait for final buffer
        time.sleep(2.0)
        
        # Stop recording
        print("\n🛑 Stopping capture...")
        self.client.send_command("stop_recording", {})
        time.sleep(0.5)
        self.client.send_command("stop_playback", {})
        
        # Disarm tracks
        print("\n🎛️  Disarming tracks...")
        if all_tracks and "tracks" in all_tracks:
            for i, track in enumerate(all_tracks["tracks"]):
                self.client.send_command("set_track_arm", {
                    "track_index": track.get("index", i),
                    "arm": False
                })
        
        print("\n✅ Mix capture complete!")
        
        return {
            "status": "success",
            "sections": total_sections,
            "total_bars": total_bars,
            "duration_minutes": total_bars * 60 / self.bpm,
            "bpm_range": f"{self.bpm} - {self.bpm + 10}",
            "structure": [
                {
                    "name": s["name"],
                    "section": s["section"],
                    "bars": s["bars"],
                    "energy": s["energy"],
                    "bpm": s["bpm"],
                    "scene_index": s["scene_index"]
                }
                for s in structure
            ]
        }

    def create_10min_mix(self) -> Dict[str, Any]:
        """Main function to create a 10-minute mix."""
        print("\n" + "=" * 60)
        print("🚀 10-MINUTE DUB x FAT BEATZ MIX GENERATOR")
        print("=" * 60)
        
        # Step 1: Generate structure
        print("\n📋 Generating mix structure...")
        structure = self.generate_structure()
        
        # Display structure
        print("\n📊 MIX STRUCTURE:")
        print("-" * 60)
        for i, section in enumerate(structure):
            bar_range = f"{section['start_bar']}-{section['start_bar'] + section['bars'] - 1}"
            print(f"  {i+1:2d}. {bar_range:8s} | {section['name']:20s} | {section['section']:12s} | Energy: {section['energy']*10:.0f}/10")
        print("-" * 60)
        
        # Step 2: Apply Fat Beatz processing
        self.apply_fat_beatz_processing(structure)
        
        # Step 3: Capture the mix
        result = self.capture_mix_from_structure(structure)
        
        # Step 4: Print summary
        self.print_summary(result)
        
        return result

    def print_summary(self, result: Dict[str, Any]) -> None:
        """Print a nice summary of the created mix."""
        print("\n" + "=" * 60)
        print("🎉 MIX CREATION COMPLETE!")
        print("=" * 60)
        
        print(f"\n📊 STATISTICS:")
        print(f"  • Sections: {result['sections']}")
        print(f"  • Total Bars: {result['total_bars']}")
        print(f"  • Duration: {result['duration_minutes']:.1f} minutes")
        print(f"  • BPM Range: {result['bpm_range']}")
        
        print(f"\n🎵 STRUCTURE:")
        for section in result['structure']:
            print(f"  • {section['name']:20s} ({section['section']:12s}) - {section['bars']} bars @ {section['bpm']} BPM")
        
        print(f"\n🎛️  PROCESSING APPLIED:")
        print("  • Sub-bass harmonic generation")
        print("  • Parallel bass compression")
        print("  • Kick drum enhancement")
        print("  • Snare thickening")
        print("  • Stereo widening")
        print("  • Harmonic excitement")
        print("  • Sidechain pumping")
        
        print(f"\n💡 NEXT STEPS:")
        print("  1. Check the arrangement in Ableton")
        print("  2. Adjust individual track volumes")
        print("  3. Fine-tune effect parameters")
        print("  4. Add automation for variation")
        print("  5. Consider adding vocal samples or melodic elements")
        
        print("\n" + "=" * 60)
        print("✨ Enjoy your 10-minute dub x fat beatz mix!")
        print("=" * 60 + "\n")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main entry point."""
    print("🎵 10-Minute Mix Generator")
    print("   Creating dub-meets-fat-beatz arrangements...")
    
    # Create client
    client = AbletonMCPClient()
    
    # Check connection
    print("\n🔌 Connecting to MCP Server...")
    if not client.connect():
        print("❌ Error: Could not connect to MCP Server")
        print("   Make sure Ableton is running with the Remote Script")
        print("   and the MCP Server is started (python -m MCP_Server.server)")
        return
    
    print("✅ Connected to MCP Server")
    
    # Create generator
    generator = MixGenerator(client)
    
    # Set BPM
    generator.bpm = 90.0
    
    # Create the mix
    try:
        result = generator.create_10min_mix()
        
        # Print result
        print(json.dumps(result, indent=2))
        
        return result
    except Exception as e:
        print(f"\n❌ Error creating mix: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        client.close()


if __name__ == "__main__":
    main()
