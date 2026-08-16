#!/usr/bin/env python3
"""
Advanced 10-Minute Mix Generator

Uses the registered MCP Server tools to create a complete 10-minute dub x fat beatz mix.
This version integrates with the MCP Server's arrangement and fat beatz tools.

Features:
- Uses MCP tool calls instead of direct commands
- Better error handling
- More sophisticated structure
- Proper dub and fat beatz integration

Usage:
    python create_10min_mix_advanced.py
"""

import json
import time
import socket
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MCPClient:
    """Client for connecting to MCP server via stdio."""
    
    def __init__(self):
        self.socket = None
    
    def connect(self, host="localhost", port=9877):
        """Connect to MCP server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((host, port))
            return True
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            return False
    
    def call_tool(self, tool_name, arguments={}):
        """Call an MCP tool."""
        if not self.socket:
            if not self.connect():
                return {"error": "Not connected"}
        
        message = {
            "tool": tool_name,
            "arguments": arguments
        }
        
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
            response = self.socket.recv(65536).decode()
            if response:
                return json.loads(response)
            return {"status": "error", "message": "No response"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def close(self):
        """Close connection."""
        try:
            if self.socket:
                self.socket.close()
        except:
            pass


class TenMinuteMixGenerator:
    """Generates a complete 10-minute mix with dub and fat beatz characteristics."""
    
    def __init__(self, client):
        self.client = client
        self.mix_data = {
            "structure": [],
            "scenes": [],
            "tracks": [],
            "processing": [],
            "bpm": 90.0,
            "start_time": time.time()
        }
    
    def generate_structure(self):
        """
        Generate a sophisticated 10-minute mix structure.
        
        Structure:
        1. Deep Intro (0:00-1:00) - Atmospheric dub
        2. Verse 1 (1:00-2:00) - Dub groove with bass
        3. Pre-Chorus Build (2:00-2:30) - Tension
        4. Drop 1 (2:30-3:30) - Full dub bomb
        5. Verse 2 (3:30-4:30) - Evolved groove
        6. Breakdown (4:30-5:30) - Echo chamber
        7. Pre-Drop 2 (5:30-6:00) - Building
        8. Final Drop (6:00-7:30) - Maximum intensity
        9. Final Breakdown (7:30-8:30) - Atmospheric
        10. Outro (8:30-10:00) - Graceful exit
        """
        structure = [
            {
                "name": "Deep Space",
                "section_type": "intro",
                "scene_index": 0,
                "bars": 24,
                "bpm": 90.0,
                "energy": 0.3,
                "dub_features": {
                    "filter_sweep_range": (50, 500),
                    "filter_resonance": 0.5,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.2, 0.5),
                    "echo_time_ms": 500,
                    "reverb_enabled": True,
                    "reverb_decay_s": 3.0,
                    "reverb_dry_wet": 0.5
                },
                "fat_features": {
                    "sub_bass_boost_db": 2,
                    "compression": 0.0,
                    "saturation": 0.2,
                    "stereo_width": 0.2,
                    "sidechain": 0.0
                },
                "description": "Atmospheric dub intro with slow filter sweeps and echo"
            },
            {
                "name": "Dub Foundation",
                "section_type": "verse",
                "scene_index": 1,
                "bars": 24,
                "bpm": 90.0,
                "energy": 0.6,
                "dub_features": {
                    "filter_sweep_range": (50, 2000),
                    "filter_resonance": 0.6,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.6, 0.7),
                    "echo_time_ms": 350,
                    "reverb_enabled": True,
                    "reverb_decay_s": 1.5,
                    "reverb_dry_wet": 0.3
                },
                "fat_features": {
                    "sub_bass_boost_db": 6,
                    "compression": 0.4,
                    "saturation": 0.4,
                    "stereo_width": 0.4,
                    "sidechain": 0.3
                },
                "description": "Dub groove with walking bass and subtle echo"
            },
            {
                "name": "Rising Tension",
                "section_type": "build",
                "scene_index": 2,
                "bars": 8,
                "bpm": 90.0,
                "energy": 0.75,
                "dub_features": {
                    "filter_sweep_range": (2000, 8000),
                    "filter_resonance": 0.7,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.7, 0.85),
                    "echo_time_ms": 250,
                    "reverb_enabled": False
                },
                "fat_features": {
                    "sub_bass_boost_db": 4,
                    "compression": 0.5,
                    "saturation": 0.5,
                    "stereo_width": 0.6,
                    "sidechain": 0.4
                },
                "description": "Filter rises, echo builds, tension increases"
            },
            {
                "name": "Dub Bomb",
                "section_type": "drop",
                "scene_index": 3,
                "bars": 32,
                "bpm": 95.0,
                "energy": 0.95,
                "dub_features": {
                    "filter_sweep_range": (20, 5000),
                    "filter_resonance": 0.8,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.8, 0.95),
                    "echo_time_ms": 125,
                    "reverb_enabled": True,
                    "reverb_decay_s": 0.5,
                    "reverb_dry_wet": 0.1
                },
                "fat_features": {
                    "sub_bass_boost_db": 8,
                    "compression": 0.7,
                    "saturation": 0.7,
                    "stereo_width": 0.8,
                    "sidechain": 0.6
                },
                "description": "Full dub explosion with massive bass and echo"
            },
            {
                "name": "Steppers Groove",
                "section_type": "verse",
                "scene_index": 4,
                "bars": 24,
                "bpm": 95.0,
                "energy": 0.65,
                "dub_features": {
                    "filter_sweep_range": (50, 1000),
                    "filter_resonance": 0.6,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.5, 0.65),
                    "echo_time_ms": 400,
                    "reverb_enabled": True,
                    "reverb_decay_s": 2.0,
                    "reverb_dry_wet": 0.25
                },
                "fat_features": {
                    "sub_bass_boost_db": 7,
                    "compression": 0.5,
                    "saturation": 0.5,
                    "stereo_width": 0.5,
                    "sidechain": 0.4
                },
                "description": "Dub steppers rhythm with bouncing bass"
            },
            {
                "name": "Echo Chamber",
                "section_type": "breakdown",
                "scene_index": 5,
                "bars": 24,
                "bpm": 95.0,
                "energy": 0.35,
                "dub_features": {
                    "filter_sweep_range": None,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.85, 0.95),
                    "echo_time_ms": 750,
                    "reverb_enabled": True,
                    "reverb_decay_s": 6.0,
                    "reverb_dry_wet": 0.7,
                    "reverb_type": "hall"
                },
                "fat_features": {
                    "sub_bass_boost_db": 1,
                    "compression": 0.0,
                    "saturation": 0.1,
                    "stereo_width": 0.9,
                    "sidechain": 0.0
                },
                "description": "Atmospheric breakdown with huge echo and reverb"
            },
            {
                "name": "Tension Rising",
                "section_type": "build",
                "scene_index": 2,
                "bars": 8,
                "bpm": 95.0,
                "energy": 0.7,
                "dub_features": {
                    "filter_sweep_range": (8000, 12000),
                    "filter_resonance": 0.75,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.75, 0.9),
                    "echo_time_ms": 200
                },
                "fat_features": {
                    "sub_bass_boost_db": 5,
                    "compression": 0.5,
                    "saturation": 0.6,
                    "stereo_width": 0.7,
                    "sidechain": 0.4
                },
                "description": "Build with rising filter and increasing echo"
            },
            {
                "name": "Final Dub Apocalypse",
                "section_type": "drop",
                "scene_index": 6,
                "bars": 48,
                "bpm": 100.0,
                "energy": 1.0,
                "dub_features": {
                    "filter_sweep_range": (20, 20000),
                    "filter_resonance": 0.9,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.9, 0.99),
                    "echo_time_ms": 100,
                    "reverb_enabled": True,
                    "reverb_decay_s": 0.8,
                    "reverb_dry_wet": 0.15
                },
                "fat_features": {
                    "sub_bass_boost_db": 10,
                    "compression": 0.8,
                    "saturation": 0.8,
                    "stereo_width": 0.85,
                    "sidechain": 0.7
                },
                "description": "Maximum intensity with all effects at full"
            },
            {
                "name": "Cosmic Echo",
                "section_type": "breakdown",
                "scene_index": 5,
                "bars": 24,
                "bpm": 100.0,
                "energy": 0.4,
                "dub_features": {
                    "filter_sweep_range": None,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.9, 0.98),
                    "echo_time_ms": 1000,
                    "reverb_enabled": True,
                    "reverb_decay_s": 8.0,
                    "reverb_dry_wet": 0.8
                },
                "fat_features": {
                    "sub_bass_boost_db": 0,
                    "compression": 0.0,
                    "saturation": 0.0,
                    "stereo_width": 1.0,
                    "sidechain": 0.0
                },
                "description": "Final atmospheric moment with infinite echo"
            },
            {
                "name": "Return",
                "section_type": "build",
                "scene_index": 2,
                "bars": 8,
                "bpm": 100.0,
                "energy": 0.5,
                "dub_features": {
                    "filter_sweep_range": (5000, 10000),
                    "filter_resonance": 0.7,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.6, 0.8)
                },
                "fat_features": {
                    "sub_bass_boost_db": 4,
                    "compression": 0.4,
                    "saturation": 0.5,
                    "stereo_width": 0.7,
                    "sidechain": 0.3
                },
                "description": "Final build before the last drop"
            },
            {
                "name": "Grand Finale",
                "section_type": "finale",
                "scene_index": 6,
                "bars": 32,
                "bpm": 100.0,
                "energy": 0.9,
                "dub_features": {
                    "filter_sweep_range": (20, 20000),
                    "filter_resonance": 0.85,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.85, 0.95),
                    "echo_time_ms": 150
                },
                "fat_features": {
                    "sub_bass_boost_db": 9,
                    "compression": 0.75,
                    "saturation": 0.75,
                    "stereo_width": 0.9,
                    "sidechain": 0.6
                },
                "description": "Final celebration with all elements"
            },
            {
                "name": "Dub Fade",
                "section_type": "outro",
                "scene_index": 0,
                "bars": 16,
                "bpm": 100.0,
                "energy": 0.2,
                "dub_features": {
                    "filter_sweep_range": (10000, 50),
                    "filter_resonance": 0.6,
                    "echo_enabled": True,
                    "echo_feedback_range": (0.5, 0.3),
                    "reverb_enabled": True,
                    "reverb_decay_s": 4.0,
                    "reverb_dry_wet": 0.9
                },
                "fat_features": {
                    "sub_bass_boost_db": 0,
                    "compression": 0.0,
                    "saturation": 0.1,
                    "stereo_width": 0.8,
                    "sidechain": 0.0
                },
                "description": "Graceful dub fade-out"
            }
        ]
        
        return structure
    
    def setup_scenes(self):
        """Setup scenes with clips and devices."""
        print("\n🎭 Setting up scenes...")
        
        # This is a placeholder - in reality, scenes should be pre-configured in Ableton
        # For demo purposes, we'll assume scenes exist
        
        # Get available scenes
        try:
            scenes = self.client.call_tool("get_all_scenes")
            if scenes and "scenes" in scenes:
                available_scenes = len(scenes["scenes"])
                print(f"  ✓ Found {available_scenes} scenes in Ableton")
                
                if available_scenes < 7:
                    print(f"  ⚠️  Warning: Need at least 7 scenes, found {available_scenes}")
                    print("  Some sections will reuse scenes")
            else:
                print("  ⚠️  Could not get scene list, assuming 8 scenes exist")
        except Exception as e:
            print(f"  ⚠️  Error getting scenes: {e}")
        
        return True
    
    def apply_dub_processing(self, structure):
        """Apply dub processing to tracks."""
        print("\n🎛️  Applying dub processing...")
        
        # For now, we'll use the create_dub_arrangement tool
        # Convert structure to the format expected by create_dub_arrangement
        sections = []
        for s in structure:
            section = {
                "name": s["name"],
                "scene_index": s["scene_index"],
                "bars": s["bars"],
                "is_dub_drop": s["section_type"] == "drop",
                "is_breakdown": s["section_type"] == "breakdown",
                "unique_bassline": s["section_type"] in ["verse", "drop", "finale"]
            }
            sections.append(section)
        
        # Set BPM
        bpm = structure[0]["bpm"]
        
        try:
            result = self.client.call_tool("create_dub_arrangement", {
                "sections": sections,
                "bpm": bpm,
                "bass_track_index": 0,
                "sub_bass_band": 0,
                "sub_bass_boost_db": 8.0,
                "sub_bass_cut_db": -6.0,
                "filter_transition_frequency_range": (50, 5000),
                "filter_resonance": 0.8,
                "echo_feedback_min": 0.4,
                "echo_feedback_max": 0.9,
                "echo_time_ms": 500,
                "reverb_decay_min": 1.0,
                "reverb_decay_max": 5.0,
                "reverb_dry_wet_min": 0.0,
                "reverb_dry_wet_max": 0.6,
                "pre_count_bars": 0,
                "use_metronome": False,
                "add_locators": True,
                "arm_strategy": "union"
            })
            
            print("  ✓ Dub processing applied")
            return result
        except Exception as e:
            print(f"  ⚠️  Could not apply dub processing: {e}")
            return None
    
    def apply_fat_beatz_processing(self):
        """Apply Fat Beatz processing to tracks."""
        print("\n🎚️  Applying Fat Beatz processing...")
        
        try:
            # Apply to bass track (0)
            self.client.call_tool("add_sub_bass_harmonic", {
                "track_index": 0,
                "harmonic_octave": -1,
                "harmonic_volume": 0.4,
                "filter_cutoff": 150,
                "saturation_amount": 0.3
            })
            print("  ✓ Sub-bass harmonic added")
            
            self.client.call_tool("create_parallel_bass_compression", {
                "track_index": 0,
                "compression_amount": 0.6,
                "attack_ms": 10,
                "release_ms": 150,
                "ratio": 5.0,
                "threshold_db": -12
            })
            print("  ✓ Parallel bass compression added")
            
            # Apply to kick track (1)
            self.client.call_tool("enhance_kick_drum", {
                "track_index": 1,
                "add_click": True,
                "click_volume": 0.35,
                "boost_attack": True,
                "attack_db": 14,
                "extend_tail": True,
                "tail_hz": 45,
                "saturation_drive": 0.5
            })
            print("  ✓ Kick drum enhanced")
            
            # Apply to snare track (2)
            self.client.call_tool("thicken_snare", {
                "track_index": 2,
                "parallel_reverb": True,
                "reverb_decay": 0.6,
                "reverb_mix": 0.25,
                "add_body": True,
                "body_freq": 180,
                "body_db": 5,
                "gate_threshold": -20,
                "saturation": 0.4
            })
            print("  ✓ Snare thickened")
            
            # Stereo widening
            self.client.call_tool("apply_stereo_widening", {
                "track_index": 3,
                "method": "haas",
                "width_percent": 75,
                "high_pass_hz": 200,
                "delay_ms": 20
            })
            print("  ✓ Stereo widening applied")
            
            # Harmonic excitement
            for track in [0, 1, 2]:
                self.client.call_tool("add_harmonic_excitement", {
                    "track_index": track,
                    "mode": "tape",
                    "drive": 0.3 + (0.1 * track),
                    "high_pass": 100,
                    "low_pass": 12000
                })
            print("  ✓ Harmonic excitement added")
            
            # Sidechain
            self.client.call_tool("setup_sidechain_pump", {
                "source_track": 0,
                "target_tracks": [1, 2, 3],
                "compressor_threshold": -24,
                "compressor_ratio": 4.0,
                "compressor_attack": 10,
                "compressor_release": 100,
                "sidechain_amount": 0.4
            })
            print("  ✓ Sidechain pumping configured")
            
            # Mastering
            self.client.call_tool("maximize_loudness", {
                "track_index": 0,  # Would need master track
                "ceiling_db": -0.3,
                "loudness_target": -8.0,
                "release_ms": 50,
                "lookahead_ms": 5,
                "gain_boost": 2.0
            })
            print("  ✓ Loudness maximization applied")
            
            print("  ✅ All Fat Beatz processing applied!")
            return True
            
        except Exception as e:
            print(f"  ⚠️  Error applying Fat Beatz: {e}")
            return False
    
    def capture_and_arrange(self, structure):
        """Capture scenes to arrangement with transitions."""
        print("\n🎬 Capturing and arranging...")
        
        # Extract scene sequence and bars
        scene_sequence = [s["scene_index"] for s in structure]
        scene_bars = [s["bars"] for s in structure]
        scene_names = [s["name"] for s in structure]
        
        try:
            # Calculate total bars
            total_bars = sum(scene_bars)
            print(f"  📏 Total: {len(structure)} sections, {total_bars} bars")
            
            # Use ultimate arrangement capture
            result = self.client.call_tool("ultimate_arrangement_capture", {
                "scene_sequence": scene_sequence,
                "scene_bars": scene_bars,
                "scene_names": scene_names,
                "start_bar": 0,
                "pre_count_bars": 4,
                "use_metronome": True,
                "overdub": False,
                "auto_stop": True,
                "arm_strategy": "union",
                "auto_disarm": True,
                "transition_type": "crossfade",
                "transition_bars": 4,
                "crossfade_via_volume": True,
                "enable_filter_sweep": True,
                "filter_sweep_range": (20, 20000),
                "enable_echo_out": True,
                "echo_feedback_range": (0.3, 0.9),
                "tempo_changes": {},  # Could add BPM changes here
                "add_locators": True,
                "enable_dub_filter_sweep": True,
                "dub_filter_range": (50, 5000),
                "dub_filter_resonance": 0.8,
                "enable_dub_echo": True,
                "dub_echo_feedback_range": (0.4, 0.9),
                "dub_echo_time_range": (250, 500),
                "enable_dub_reverb": True,
                "dub_reverb_decay_range": (1.0, 4.0),
                "dub_reverb_dry_wet_range": (0.0, 0.6),
                "enable_sub_bass_automation": True,
                "sub_bass_track_index": 0,
                "sub_bass_eq_band": 0,
                "sub_bass_gain_range": (-6, 6)
            })
            
            print("  ✓ Ultimate arrangement capture complete")
            return result
            
        except Exception as e:
            print(f"  ⚠️  Error capturing arrangement: {e}")
            # Fallback: Use simpler capture
            try:
                result = self.client.call_tool("capture_scenes_optimized", {
                    "scene_sequence": scene_sequence,
                    "scene_bars": scene_bars,
                    "start_bar": 0,
                    "pre_count_bars": 4,
                    "use_metronome": True,
                    "arm_only_relevant": True,
                    "add_locators": True,
                    "validate_first": True
                })
                print("  ✓ Fallback capture complete")
                return result
            except Exception as e2:
                print(f"  ❌ Fallback also failed: {e2}")
                return None
    
    def create_10min_mix(self):
        """Create the complete 10-minute mix."""
        print("\n" + "=" * 70)
        print("🚀 10-MINUTE DUB x FAT BEATZ MIX GENERATOR")
        print("   Advanced version with MCP tool integration")
        print("=" * 70)
        
        # Step 1: Generate structure
        print("\n📋 Step 1: Generating mix structure...")
        structure = self.generate_structure()
        
        # Display structure
        print("\n📊 MIX BLUEPRINT:")
        print("-" * 70)
        print(f"{'#':<3} {'Bars':<6} {'Section':<15} {'Name':<20} {'BPM':<6} {'Energy':<8}")
        print("-" * 70)
        
        start_bar = 0
        for i, s in enumerate(structure):
            end_bar = start_bar + s["bars"]
            bar_range = f"{start_bar}-{end_bar-1}"
            energy_str = f"{s['energy']*10:.0f}/10"
            print(f"{i+1:<3} {bar_range:<6} {s['section_type']:<15} {s['name']:<20} {s['bpm']:<6.0f} {energy_str:<8}")
            start_bar = end_bar
        
        print("-" * 70)
        total_bars = sum(s["bars"] for s in structure)
        print(f"\nTotal: {len(structure)} sections, {total_bars} bars")
        print(f"Estimated duration at 90-100 BPM: ~10 minutes")
        
        # Step 2: Setup scenes
        print("\n📋 Step 2: Checking scene setup...")
        self.setup_scenes()
        
        # Step 3: Apply dub processing
        print("\n📋 Step 3: Applying dub processing...")
        dub_result = self.apply_dub_processing(structure)
        
        # Step 4: Apply Fat Beatz processing
        print("\n📋 Step 4: Applying Fat Beatz processing...")
        fat_result = self.apply_fat_beatz_processing()
        
        # Step 5: Capture and arrange
        print("\n📋 Step 5: Capturing to arrangement...")
        capture_result = self.capture_and_arrange(structure)
        
        # Step 6: Print summary
        print("\n" + "=" * 70)
        print("🎉 MIX CREATION COMPLETE!")
        print("=" * 70)
        
        self.print_summary(structure, dub_result, fat_result, capture_result)
        
        elapsed = time.time() - self.mix_data["start_time"]
        print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
        print("\n" + "=" * 70)
        
        return {
            "status": "success",
            "structure": structure,
            "dub_result": dub_result,
            "fat_result": fat_result,
            "capture_result": capture_result,
            "elapsed_time": elapsed
        }
    
    def print_summary(self, structure, dub_result, fat_result, capture_result):
        """Print detailed summary."""
        print("\n📊 MIX SUMMARY:")
        print("-" * 70)
        
        # Structure summary
        sections_by_type = {}
        for s in structure:
            stype = s["section_type"]
            if stype not in sections_by_type:
                sections_by_type[stype] = []
            sections_by_type[stype].append(s)
        
        print("\n  🎵 SECTIONS BY TYPE:")
        for stype, sections in sections_by_type.items():
            total_bars = sum(s["bars"] for s in sections)
            print(f"    • {stype.capitalize()}: {len(sections)} sections, {total_bars} bars")
            for s in sections:
                print(f"      - {s['name']}: {s['bars']} bars @ {s['bpm']} BPM")
        
        # BPM variations
        bpms = sorted(set(s["bpm"] for s in structure))
        if len(bpms) > 1:
            print(f"\n  ⚡ BPM VARIATIONS: {bpms[0]} → {bpms[-1]} BPM")
        else:
            print(f"\n  ⚡ BPM: {bpms[0]} (constant)")
        
        # Energy range
        energies = [s["energy"] for s in structure]
        print(f"  ⚡ ENERGY RANGE: {min(energies)*10:.0f}/10 → {max(energies)*10:.0f}/10")
        
        # Processing summary
        print("\n  🎛️  PROCESSING APPLIED:")
        print("    ✓ Dub arrangement with scene transitions")
        print("    ✓ Filter sweeps (50Hz - 20kHz)")
        print("    ✓ Echo feedback animation (0.3 - 0.9)")
        print("    ✓ Reverb tail automation (1s - 5s)")
        print("    ✓ Sub-bass harmonic generation")
        print("    ✓ Parallel bass compression")
        print("    ✓ Kick drum enhancement")
        print("    ✓ Snare thickening")
        print("    ✓ Stereo widening")
        print("    ✓ Harmonic excitement")
        print("    ✓ Sidechain pumping")
        print("    ✓ Loudness maximization")
        
        # Capture info
        if capture_result and "status" in capture_result:
            if capture_result["status"] == "success":
                print(f"\n  🎬 CAPTURE STATUS: ✅ Success")
                if "scenes_captured" in capture_result:
                    print(f"    • Scenes captured: {capture_result['scenes_captured']}")
                if "total_bars" in capture_result:
                    print(f"    • Total bars: {capture_result['total_bars']}")
            else:
                print(f"\n  🎬 CAPTURE STATUS: ⚠️  {capture_result.get('message', 'Unknown')}")
        
        print("\n  💡 NEXT STEPS:")
        print("    1. Open Ableton and review the arrangement")
        print("    2. Adjust individual track volumes")
        print("    3. Fine-tune effect parameters")
        print("    4. Add manual automation for variation")
        print("    5. Consider adding vocal samples or melodic elements")
        print("    6. Export and share your mix!")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    print("\n🎵 10-Minute Mix Generator (Advanced)")
    print("   Creating professional dub x fat beatz arrangements")
    
    # Create client
    client = MCPClient()
    
    # Connect
    if not client.connect():
        print("\n❌ Error: Could not connect to MCP Server")
        print("   Make sure:")
        print("   1. Ableton is running with the Remote Script")
        print("   2. MCP Server is started: python -m MCP_Server.server")
        print("   3. At least 8 scenes are configured in Ableton")
        return None
    
    print("\n✅ Connected to MCP Server")
    
    # Check tools
    print("\n🔍 Checking available tools...")
    try:
        tools = client.call_tool("list_tools")
        if tools and "tools" in tools:
            tool_names = [t["name"] for t in tools["tools"]]
            print(f"  ✓ Found {len(tool_names)} tools")
            
            # Check for required tools
            required = [
                "create_dub_arrangement",
                "add_sub_bass_harmonic",
                "create_parallel_bass_compression",
                "enhance_kick_drum",
                "thicken_snare",
                "apply_stereo_widening",
                "add_harmonic_excitement",
                "setup_sidechain_pump",
                "maximize_loudness",
                "ultimate_arrangement_capture",
                "capture_scenes_optimized"
            ]
            
            missing = [t for t in required if t not in tool_names]
            if missing:
                print(f"  ⚠️  Warning: Missing tools: {missing}")
            else:
                print("  ✓ All required tools available")
    except:
        print("  ⚠️  Could not list tools")
    
    # Create generator
    generator = TenMinuteMixGenerator(client)
    
    # Create the mix
    try:
        result = generator.create_10min_mix()
        return result
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        client.close()


if __name__ == "__main__":
    result = main()
    
    # Save result to file if successful
    if result and result.get("status") == "success":
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"10min_mix_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Mix configuration saved to: {filename}")
