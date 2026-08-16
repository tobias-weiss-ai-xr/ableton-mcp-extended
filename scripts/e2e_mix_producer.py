#!/usr/bin/env python3
"""
End-to-End Mix Producer for Ableton Live MCP Extended

This script demonstrates a complete workflow for producing a real mix:
1. Build a session with tracks, instruments, clips, and scenes
2. Create arrangement from session (capture session to arrangement)
3. Edit and refine the arrangement
4. Add automation for mix dynamics
5. Polish with master effects
6. Prepare for manual fine-tuning

Usage:
    python scripts/e2e_mix_producer.py

Requires:
    - Ableton Live with MCP Remote Script running on port 9877
    - MCP Server running (ableton-mcp-extended)

Workflow Steps:
    Step 1: Setup Session - Creates tracks, loads instruments, sets up scenes
    Step 2: Create Content - Generates drum patterns, basslines, melodies
    Step 3: Session to Arrangement - Captures session into arrangement view
    Step 4: Arrange & Edit - Structures the arrangement, adds variations
    Step 5: Mix Automation - Adds volume, filter, effect automation
    Step 6: Polish - Final touches, master FX, optimization
    Step 7: Save & Ready - Saves the project for manual fine-tuning
"""

import sys
import time
import random
import json
import socket
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configuration
HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_PORT = 9878
BPM = 126
BEATS_PER_BAR = 4
BAR = 4.0

# Track configuration
TRACK_CONFIG = {
    0: {"name": "Drums", "type": "drum", "color": 10, "volume": 0.82, "pan": 0.0},
    1: {"name": "Bass", "type": "bass", "color": 20, "volume": 0.88, "pan": 0.0},
    2: {"name": "Chords", "type": "chord", "color": 60, "volume": 0.60, "pan": -0.18},
    3: {"name": "Lead", "type": "lead", "color": 40, "volume": 0.68, "pan": 0.15},
    4: {"name": "FX", "type": "fx", "color": 80, "volume": 0.45, "pan": 0.0},
    5: {"name": "Percussion", "type": "percussion", "color": 15, "volume": 0.70, "pan": 0.0},
    6: {"name": "Strings", "type": "strings", "color": 70, "volume": 0.50, "pan": 0.22},
    7: {"name": "Arp", "type": "arp", "color": 50, "volume": 0.52, "pan": -0.12},
}

# Scene structure: [intro, verse, build, drop, breakdown, bridge, verse2, outro]
SCENE_STRUCTURE = ["Intro", "Verse", "Build", "Drop", "Breakdown", "Bridge", "Verse 2", "Outro"]
SCENE_BARS = [8, 16, 16, 16, 8, 16, 16, 8]  # Bars per scene

# Instrument URIs
INSTRUMENT_URIS = {
    "drum": "query:Drums#FileId_58622",
    "bass": "query:Sounds#Bass:FileId_49654",
    "chord": "query:Sounds#Pad:FileId_45564",
    "lead": "query:Sounds#Synth%20Lead:FileId_50175",
    "fx": "query:Sounds#Synth%20FX:FileId_50176",
    "percussion": "query:Drums#FileId_58623",
    "strings": "query:Sounds#Pad:FileId_45565",
    "arp": "query:Sounds#Synth%20Lead:FileId_50177",
}

# Return track effects
RETURN_EFFECTS = {
    0: {"name": "Reverb", "uri": "query:AudioFx#Hybrid%20Reverb"},
    1: {"name": "Delay", "uri": "query:AudioFx#Delay"},
}

# Per-track effects chains
TRACK_EFFECTS = {
    0: ["query:AudioFx#Drum%20Buss", "query:AudioFx#Glue%20Compressor"],
    1: ["query:AudioFx#Glue%20Compressor", "query:AudioFx#Saturator"],
    2: ["query:AudioFx#Chorus-Ensemble", "query:AudioFx#Convolution%20Reverb%20Pro"],
    3: ["query:AudioFx#Echo", "query:AudioFx#Auto%20Filter"],
    4: ["query:AudioFx#Spectral%20Resonator", "query:AudioFx#Reverb"],
    5: ["query:AudioFx#Compressor", "query:AudioFx#Gate"],
    6: ["query:AudioFx#Chorus-Ensemble", "query:AudioFx#Auto%20Filter"],
    7: ["query:AudioFx#Delay", "query:AudioFx#Beat%20Repeat"],
}

# Master FX
MASTER_FX = ["query:AudioFx#Glue%20Compressor", "query:AudioFx#Limiter"]


class AbletonTCPClient:
    """TCP client for Ableton MCP communication"""
    
    def __init__(self, host=HOST, port=TCP_PORT):
        self.host = host
        self.port = port
        self.sock = None
    
    def connect(self):
        """Connect to Ableton Remote Script"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(15.0)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Error connecting to Ableton: {e}")
            self.sock = None
            return False
    
    def tcp_command(self, command_type, params=None):
        """Send a TCP command and get response"""
        if params is None:
            params = {}
        
        if self.sock is None:
            if not self.connect():
                return {"status": "error", "message": "Not connected"}
        
        try:
            msg = json.dumps({"type": command_type, "params": params})
            self.sock.sendall((msg + "\n").encode())
            data = b""
            self.sock.settimeout(15.0)
            while True:
                try:
                    chunk = self.sock.recv(65536)
                except socket.timeout:
                    break
                if not chunk:
                    break
                data += chunk
            return json.loads(data.decode())
        except Exception as e:
            print(f"Error in TCP command {command_type}: {e}")
            return {"status": "error", "message": str(e)}
    
    def udp_command(self, command_type, params=None):
        """Send a UDP command (fire-and-forget)"""
        if params is None:
            params = {}
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            msg = json.dumps({"type": command_type, "params": params}).encode()
            sock.sendto(msg, (self.host, UDP_PORT))
            sock.close()
        except Exception as e:
            print(f"Error in UDP command {command_type}: {e}")
    
    def close(self):
        """Close connection"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None


class E2EMixProducer:
    """End-to-End Mix Producer"""
    
    def __init__(self):
        self.client = AbletonTCPClient()
        self.logs = []
        self.start_time = datetime.now()
        self.stats = {
            "commands_sent": 0,
            "arrangement_bars": 0,
            "automation_points": 0,
            "clips_created": 0,
            "scenes_created": 0,
        }
    
    def log(self, message, level="INFO"):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = (datetime.now() - self.start_time).total_seconds()
        log_entry = f"[{timestamp} +{elapsed:.1f}s] [{level}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def cmd(self, command_type, params=None, udp=False):
        """Send a command and track it"""
        self.stats["commands_sent"] += 1
        if udp:
            self.client.udp_command(command_type, params)
        else:
            return self.client.tcp_command(command_type, params)
    
    def load_instrument(self, track_index, uri):
        """Load instrument on a track"""
        result = self.cmd("load_browser_item", {"track_index": track_index, "item_uri": uri})
        time.sleep(0.5)
        return result
    
    def load_effect(self, track_index, uri):
        """Load effect on a track"""
        result = self.cmd("load_browser_item", {"track_index": track_index, "item_uri": uri})
        time.sleep(0.3)
        return result
    
    def cleanup_extra_tracks(self, max_tracks=8):
        """Remove any tracks beyond max_tracks"""
        try:
            tracks = self.cmd("get_all_tracks").get("result", {}).get("tracks", [])
            for track in sorted(tracks, key=lambda x: x.get("index"), reverse=True):
                if track.get("index", 0) >= max_tracks:
                    self.cmd("delete_track", {"track_index": track.get("index")})
                    time.sleep(0.15)
        except:
            pass
    
    # =========================================================================
    # STEP 1: SETUP SESSION
    # =========================================================================
    
    def setup_session(self):
        """Step 1: Create tracks, load instruments, set up returns"""
        self.log("\n" + "=" * 60)
        self.log("STEP 1: SETUP SESSION")
        self.log("=" * 60)
        
        # Clean slate
        self.log("Cleaning up existing session...")
        self.cmd("delete_all_tracks")
        time.sleep(2)
        
        # Create return tracks
        self.log("Creating return tracks...")
        for i, ret in RETURN_EFFECTS.items():
            self.cmd("create_return_track", {"index": i})
            time.sleep(0.3)
            self.load_instrument(-1, ret["uri"])
            time.sleep(0.3)
            self.cmd("set_track_name", {"track_index": -1, "name": ret["name"]})
            time.sleep(0.1)
            self.cleanup_extra_tracks()
        
        # Create MIDI tracks
        self.log("Creating MIDI tracks...")
        for i in range(8):
            self.cmd("create_midi_track", {"index": i})
            time.sleep(0.3)
        
        # Name tracks and set basic properties
        self.log("Configuring tracks...")
        for track_idx, config in TRACK_CONFIG.items():
            self.cmd("set_track_name", {"track_index": track_idx, "name": config["name"]})
            time.sleep(0.05)
            self.cmd("set_track_color", {"track_index": track_idx, "color_index": config["color"]})
            time.sleep(0.05)
            self.client.udp_command("set_track_volume", {"track_index": track_idx, "volume": config["volume"]})
            time.sleep(0.02)
            self.client.udp_command("set_track_pan", {"track_index": track_idx, "pan": config["pan"]})
            time.sleep(0.02)
        
        # Load instruments
        self.log("Loading instruments...")
        for track_idx, config in TRACK_CONFIG.items():
            if config["type"] in INSTRUMENT_URIS:
                self.load_instrument(track_idx, INSTRUMENT_URIS[config["type"]])
                self.cleanup_extra_tracks()
        
        # Load effects
        self.log("Loading effects...")
        for track_idx, effect_uris in TRACK_EFFECTS.items():
            for uri in effect_uris:
                self.load_effect(track_idx, uri)
                self.cleanup_extra_tracks()
        
        # Load master FX
        self.log("Loading master effects...")
        for uri in MASTER_FX:
            self.load_instrument(-1, uri)
            self.cleanup_extra_tracks()
            time.sleep(0.3)
        
        # Set tempo and time signature
        self.cmd("set_tempo", {"tempo": BPM})
        time.sleep(0.2)
        self.cmd("set_time_signature", {"numerator": 4, "denominator": 4})
        time.sleep(0.2)
        self.cmd("set_master_volume", {"volume": 0.85})
        time.sleep(0.2)
        
        # Configure send levels
        self.log("Configuring sends...")
        rt = self.cmd("get_return_tracks").get("result", {}).get("return_tracks", [])
        reverb_idx = next((r.get("index") for r in rt if "Reverb" in r.get("name", "")), None)
        delay_idx = next((r.get("index") for r in rt if "Delay" in r.get("name", "")), None)
        
        if reverb_idx is not None:
            self.client.udp_command("set_send_amount", {"track_index": 0, "send_index": reverb_idx, "amount": 0.15})
            self.client.udp_command("set_send_amount", {"track_index": 2, "send_index": reverb_idx, "amount": 0.28})
            self.client.udp_command("set_send_amount", {"track_index": 3, "send_index": reverb_idx, "amount": 0.22})
            self.client.udp_command("set_send_amount", {"track_index": 6, "send_index": reverb_idx, "amount": 0.25})
        
        if delay_idx is not None:
            self.client.udp_command("set_send_amount", {"track_index": 3, "send_index": delay_idx, "amount": 0.30})
            self.client.udp_command("set_send_amount", {"track_index": 7, "send_index": delay_idx, "amount": 0.20})
        
        self.log("Session setup complete!")
        return True
    
    # =========================================================================
    # STEP 2: CREATE CONTENT
    # =========================================================================
    
    def create_content(self):
        """Step 2: Create clips and scenes with musical content"""
        self.log("\n" + "=" * 60)
        self.log("STEP 2: CREATE CONTENT")
        self.log("=" * 60)
        
        # Create scenes
        self.log("Creating scenes...")
        for i, name in enumerate(SCENE_STRUCTURE):
            self.cmd("create_scene", {"index": i})
            self.cmd("set_scene_name", {"scene_index": i, "name": name})
            time.sleep(0.1)
        
        # Delete extra scenes
        for s in range(50, 7, -1):
            try:
                self.cmd("delete_scene", {"scene_index": s})
                time.sleep(0.02)
            except:
                pass
        
        # Create clips and content for each track
        self.log("Creating clips and content...")
        
        # Track 0: Drums
        self.log("  Track 0: Drums...")
        patterns = ["house_basic", "techno_4x4", "dub_techno", "rockers", "steppers", "techno_4x4", "house_basic", "dub_techno"]
        for scene_idx, pattern in enumerate(patterns[:len(SCENE_STRUCTURE)]):
            from MCP_Server.server import create_drum_pattern
            create_drum_pattern(
                ctx=None,
                track_index=0,
                clip_index=scene_idx,
                pattern_name=pattern,
                length=SCENE_BARS[scene_idx],
            )
            time.sleep(0.2)
            self.stats["clips_created"] += 1
        
        # Track 1: Bass
        self.log("  Track 1: Bass...")
        bass_roots = [36, 36, 36, 41, 34, 39, 36, 34]
        for scene_idx, root in enumerate(bass_roots[:len(SCENE_STRUCTURE)]):
            self.cmd("create_clip", {"track_index": 1, "clip_index": scene_idx, "length": SCENE_BARS[scene_idx]})
            time.sleep(0.05)
            
            notes = []
            bar_length = SCENE_BARS[scene_idx]
            beats = int(bar_length * BEATS_PER_BAR)
            
            if scene_idx in [0, 4, 7]:  # Sparse - half notes
                for b in range(0, beats, 8):
                    notes.append({"pitch": root, "start_time": b, "duration": 4.0, "velocity": 90, "mute": False})
                    notes.append({"pitch": root - 2, "start_time": b + 4, "duration": 2.0, "velocity": 80, "mute": False})
            elif scene_idx == 3:  # Drop - fast 16th notes
                for b in range(0, beats, 2):
                    octave = (b // 8) % 2
                    notes.append({"pitch": root + octave * 12, "start_time": b, "duration": 0.5, "velocity": 100, "mute": False})
                    if b % 4 < 2:
                        notes.append({"pitch": root + 5 + octave * 12, "start_time": b + 0.75, "duration": 0.25, "velocity": 85, "mute": False})
            else:  # Normal - quarter notes with variations
                for b in range(0, beats, 4):
                    notes.append({"pitch": root, "start_time": b, "duration": 1.5, "velocity": 95, "mute": False})
                    if b % 8 < 4:
                        notes.append({"pitch": root + 7, "start_time": b + 2, "duration": 0.5, "velocity": 85, "mute": False})
                    notes.append({"pitch": root + 3, "start_time": b + 4, "duration": 1.0, "velocity": 90, "mute": False})
            
            self.cmd("add_notes_to_clip", {"track_index": 1, "clip_index": scene_idx, "notes": notes})
            time.sleep(0.1)
            self.stats["clips_created"] += 1
        
        # Track 2: Chords
        self.log("  Track 2: Chords...")
        from MCP_Server.server import create_chord_notes
        chord_presets = [
            {"root": 48, "type": "min7", "vel": 65, "prog": [(0, 0), (4, 4)]},
            {"root": 50, "type": "min7", "vel": 75, "prog": [(0, 0), (4, 4)]},
            {"root": 50, "type": "min7", "vel": 80, "prog": [(0, 0), (4, 0), (8, 4)]},
            {"root": 50, "type": "maj7", "vel": 85, "prog": [(0, 0), (4, 4), (8, 7), (12, 0)]},
            {"root": 48, "type": "min7", "vel": 65, "prog": [(0, 0), (8, 4)]},
            {"root": 52, "type": "min7", "vel": 72, "prog": [(0, 0), (4, 0), (8, 5)]},
            {"root": 50, "type": "min7", "vel": 75, "prog": [(0, 0), (4, 4), (8, 0)]},
            {"root": 48, "type": "maj7", "vel": 60, "prog": [(0, 0), (8, 7)]},
        ]
        for scene_idx, cp in enumerate(chord_presets[:len(SCENE_STRUCTURE)]):
            self.cmd("create_clip", {"track_index": 2, "clip_index": scene_idx, "length": SCENE_BARS[scene_idx]})
            time.sleep(0.05)
            for start_beat, root_offset in cp["prog"]:
                create_chord_notes(
                    ctx=None,
                    track_index=2,
                    clip_index=scene_idx,
                    root=cp["root"] + root_offset,
                    chord_type=cp["type"],
                    start_time=start_beat,
                    duration=min(8.0, SCENE_BARS[scene_idx] * BEATS_PER_BAR - start_beat),
                    velocity=cp["vel"],
                )
                time.sleep(0.05)
            self.stats["clips_created"] += 1
        
        # Track 3: Lead
        self.log("  Track 3: Lead...")
        leads = [
            [67, 64, 69, 67, 62, 64, 69, 67, 67, 69, 71, 72, 71, 69, 67, 64],
            [67, 69, 71, 72, 74, 72, 71, 69, 67, 64, 67, 69, 71, 72, 71, 69],
            [64, 65, 67, 69, 71, 72, 71, 69, 67, 69, 71, 72, 74, 72, 71, 69],
            [72, 74, 76, 77, 79, 77, 76, 74, 72, 71, 72, 74, 76, 74, 72, 71],
            [67, 64, 69, 67, 62, 64, 69, 67, 67, 69, 71, 72, 71, 69, 67, 64],
            [72, 74, 76, 74, 72, 71, 69, 67, 69, 71, 72, 74, 72, 71, 69, 67],
            [69, 71, 72, 74, 72, 71, 69, 67, 69, 71, 72, 74, 76, 74, 72, 71],
            [71, 72, 74, 72, 71, 69, 67, 69, 71, 72, 74, 71, 69, 67, 64, 67],
        ]
        for scene_idx, phrase in enumerate(leads[:len(SCENE_STRUCTURE)]):
            self.cmd("create_clip", {"track_index": 3, "clip_index": scene_idx, "length": SCENE_BARS[scene_idx]})
            time.sleep(0.05)
            phrase_notes = []
            beats = int(SCENE_BARS[scene_idx] * BEATS_PER_BAR)
            for i in range(beats):
                pitch = phrase[i % len(phrase)]
                vel = 80 + random.randint(-8, 12)
                if i % 2 == 0:
                    phrase_notes.append({
                        "pitch": pitch,
                        "start_time": i * 0.5,
                        "duration": 0.4,
                        "velocity": vel,
                        "mute": False,
                    })
            if scene_idx == 3:  # Add high notes in drop
                for b in range(0, beats, 8):
                    phrase_notes.append({
                        "pitch": 84,
                        "start_time": b,
                        "duration": 0.15,
                        "velocity": 50,
                        "mute": False,
                    })
            self.cmd("add_notes_to_clip", {"track_index": 3, "clip_index": scene_idx, "notes": phrase_notes})
            time.sleep(0.1)
            self.stats["clips_created"] += 1
        
        # Track 4: FX
        self.log("  Track 4: FX...")
        for scene_idx in range(len(SCENE_STRUCTURE)):
            self.cmd("create_clip", {"track_index": 4, "clip_index": scene_idx, "length": SCENE_BARS[scene_idx]})
            time.sleep(0.05)
            notes = []
            beats = int(SCENE_BARS[scene_idx] * BEATS_PER_BAR)
            
            if scene_idx in [0, 4]:  # Sparse risers
                for b in range(0, beats, 16):
                    notes.append({"pitch": 60, "start_time": b, "duration": 0.5, "velocity": 40, "mute": False})
            elif scene_idx == 2:  # Fast FX before drop
                for i in range(64):
                    if i * 0.25 < beats:
                        notes.append({
                            "pitch": 36 + (i % 12),
                            "start_time": i * 0.25,
                            "duration": 0.12,
                            "velocity": min(35 + i, 75),
                            "mute": False,
                        })
            elif scene_idx == 3:  # White noise sweeps in drop
                for b in range(0, beats, 4):
                    notes.append({"pitch": 72, "start_time": b, "duration": 0.08, "velocity": 75, "mute": False})
                    notes.append({"pitch": 84, "start_time": b, "duration": 0.08, "velocity": 65, "mute": False})
            elif scene_idx == 5:  # Atmospheric FX in bridge
                for i in range(32):
                    if i * 0.5 < beats:
                        notes.append({
                            "pitch": 60 + (i % 24),
                            "start_time": i * 0.5,
                            "duration": 0.15,
                            "velocity": 50 + random.randint(-10, 15),
                            "mute": False,
                        })
            else:
                for b in range(0, beats, 32):
                    notes.append({"pitch": 60, "start_time": b, "duration": 1.0, "velocity": 55, "mute": False})
            
            self.cmd("add_notes_to_clip", {"track_index": 4, "clip_index": scene_idx, "notes": notes})
            time.sleep(0.05)
            self.stats["clips_created"] += 1
        
        # Track 5: Percussion
        self.log("  Track 5: Percussion...")
        perc_patterns = ["steppers", "rockers", "house_basic", "techno_4x4", "dub_techno", "rockers", "steppers", "rockers"]
        for scene_idx, pattern in enumerate(perc_patterns[:len(SCENE_STRUCTURE)]):
            from MCP_Server.server import create_drum_pattern
            create_drum_pattern(
                ctx=None,
                track_index=5,
                clip_index=scene_idx,
                pattern_name=pattern,
                length=SCENE_BARS[scene_idx],
                kick_note=47,
                snare_note=45,
                hat_note=42,
                clap_note=39,
            )
            time.sleep(0.2)
            self.stats["clips_created"] += 1
        
        # Track 6: Strings
        self.log("  Track 6: Strings...")
        string_chords = [
            [(45, 48, 52, 57), (48, 52, 55, 60), (43, 47, 50, 55), (45, 49, 52, 57)],
            [(48, 52, 55, 60), (50, 54, 57, 62), (48, 52, 55, 60), (45, 49, 52, 57)],
            [(48, 52, 55, 60), (50, 54, 57, 62), (48, 52, 55, 60), (43, 47, 50, 56)],
            [(48, 52, 55, 60), (53, 57, 60, 64), (50, 54, 57, 62), (45, 49, 52, 57)],
            [(45, 49, 52, 57), (43, 47, 50, 55), (45, 49, 52, 57), (48, 52, 55, 60)],
            [(50, 54, 57, 62), (48, 52, 55, 60), (52, 56, 59, 64), (48, 52, 55, 60)],
            [(48, 52, 55, 60), (50, 54, 57, 62), (45, 49, 52, 57), (48, 52, 55, 60)],
            [(45, 49, 52, 57), (48, 52, 55, 60), (43, 47, 50, 55), (45, 49, 52, 57)],
        ]
        for scene_idx, voicings in enumerate(string_chords[:len(SCENE_STRUCTURE)]):
            self.cmd("create_clip", {"track_index": 6, "clip_index": scene_idx, "length": SCENE_BARS[scene_idx]})
            time.sleep(0.05)
            section_length = int(SCENE_BARS[scene_idx] * BEATS_PER_BAR) // len(voicings)
            notes = []
            for vi, (n1, n2, n3, n4) in enumerate(voicings):
                beat = vi * section_length
                notes.extend([
                    {"pitch": n1, "start_time": beat, "duration": section_length, "velocity": 70, "mute": False},
                    {"pitch": n2, "start_time": beat, "duration": section_length, "velocity": 68, "mute": False},
                    {"pitch": n3, "start_time": beat, "duration": section_length, "velocity": 66, "mute": False},
                    {"pitch": n4, "start_time": beat, "duration": section_length, "velocity": 64, "mute": False},
                ])
            self.cmd("add_notes_to_clip", {"track_index": 6, "clip_index": scene_idx, "notes": notes})
            time.sleep(0.05)
            self.stats["clips_created"] += 1
        
        # Track 7: Arp
        self.log("  Track 7: Arp...")
        arp_presets = [
            {"root": 48, "base": [0, 4, 7, 12], "vel": 60, "pat": "up"},
            {"root": 48, "base": [0, 3, 7, 10], "vel": 70, "pat": "updown"},
            {"root": 48, "base": [0, 3, 7, 10], "vel": 75, "pat": "updown"},
            {"root": 48, "base": [0, 4, 7, 11], "vel": 80, "pat": "random"},
            {"root": 45, "base": [0, 3, 7, 10], "vel": 60, "pat": "up"},
            {"root": 50, "base": [0, 4, 7, 10], "vel": 72, "pat": "updown"},
            {"root": 50, "base": [0, 3, 7, 10], "vel": 75, "pat": "updown"},
            {"root": 48, "base": [0, 4, 7, 11], "vel": 60, "pat": "up"},
        ]
        for scene_idx, ap in enumerate(arp_presets[:len(SCENE_STRUCTURE)]):
            self.cmd("create_clip", {"track_index": 7, "clip_index": scene_idx, "length": SCENE_BARS[scene_idx]})
            time.sleep(0.05)
            beats = int(SCENE_BARS[scene_idx] * BEATS_PER_BAR)
            base = ap["base"]
            root = ap["root"]
            vel = ap["vel"]
            pat = ap["pat"]
            notes = []
            for b in range(beats * 2):
                if pat == "up":
                    ni = b % len(base)
                elif pat == "updown":
                    n = b % (len(base) * 2 - 2)
                    if n >= len(base):
                        n = len(base) * 2 - 2 - n
                    ni = n
                else:  # random
                    ni = b % len(base) if b % 3 else random.randint(0, len(base) - 1)
                pitch = root + base[ni]
                notes.append({
                    "pitch": pitch,
                    "start_time": b * 0.25,
                    "duration": 0.2,
                    "velocity": vel + random.randint(-5, 10),
                    "mute": False,
                })
            self.cmd("add_notes_to_clip", {"track_index": 7, "clip_index": scene_idx, "notes": notes})
            time.sleep(0.1)
            self.stats["clips_created"] += 1
        
        # Set scene launch modes
        self.log("Setting up scene triggering...")
        for scene_idx in range(len(SCENE_STRUCTURE)):
            self.cmd("set_clip_launch_mode", {"track_index": 0, "clip_index": scene_idx, "mode": 2})  # Trigger
            time.sleep(0.02)
        
        self.stats["scenes_created"] = len(SCENE_STRUCTURE)
        self.log(f"Content creation complete! {self.stats['clips_created']} clips, {self.stats['scenes_created']} scenes")
        return True
    
    # =========================================================================
    # STEP 3: SESSION TO ARRANGEMENT
    # =========================================================================
    
    def session_to_arrangement(self):
        """Step 3: Capture session into arrangement view"""
        self.log("\n" + "=" * 60)
        self.log("STEP 3: SESSION TO ARRANGEMENT")
        self.log("=" * 60)
        
        # First save current position
        current_pos = self.cmd("get_playhead_position")
        
        # Method 1: Use non-real-time capture
        self.log("Method 1: Non-real-time capture and insert...")
        total_bars = sum(SCENE_BARS)
        
        rc = self.cmd("capture_and_insert_arrangement", {
            "start_bar": 0,
            "length_bars": total_bars,
            "quantize": True,
        })
        
        if rc.get("status") == "success":
            self.log(f"  Captured {total_bars} bars to arrangement")
            self.stats["arrangement_bars"] = total_bars
        else:
            self.log(f"  Warning: capture_and_insert returned: {rc}")
        
        # Navigate to arrangement view
        self.cmd("set_arrangement_view_position", {"bar": 0, "beat": 0})
        self.cmd("set_arrangement_zoom", {"zoom_level": 0.5})
        self.log("  Arrangement view navigated to start, zoomed out")
        
        # Method 2: Real-time recording (alternative)
        # This requires playing through scenes
        self.log("Method 2: Real-time recording through scenes...")
        self.cmd("set_playhead_position", {"bar": 0, "beat": 0})
        time.sleep(0.5)
        
        # Start recording
        self.cmd("start_recording")
        time.sleep(0.3)
        self.cmd("start_playback")
        time.sleep(0.3)
        
        # Trigger scenes in sequence
        current_bar = 0
        for scene_idx in range(len(SCENE_STRUCTURE)):
            self.log(f"  Triggering scene {scene_idx}: {SCENE_STRUCTURE[scene_idx]}...")
            self.cmd("trigger_scene", {"scene_index": scene_idx})
            time.sleep(0.1)
            
            # Wait for scene duration
            scene_seconds = (SCENE_BARS[scene_idx] * BEATS_PER_BAR * 60.0) / BPM
            if scene_seconds > 1:
                self.log(f"  Waiting {scene_seconds:.1f}s for scene {scene_idx}...")
                time.sleep(scene_seconds - 0.5)  # Subtract a bit for command delay
        
        # Stop recording
        self.cmd("stop_recording")
        self.cmd("stop_playback")
        self.log("  Recording complete")
        
        # Restore position
        if current_pos.get("result"):
            bar = current_pos["result"].get("bar", 0)
            beat = current_pos["result"].get("beat", 0)
            self.cmd("set_playhead_position", {"bar": bar, "beat": beat})
        
        # Get arrangement clips
        clips = self.cmd("get_arrangement_clips")
        if clips.get("status") == "success":
            num_clips = len(clips.get("result", {}).get("arrangement_clips", []))
            self.log(f"  Arrangement now has {num_clips} clips")
        
        self.log("Session to arrangement conversion complete!")
        return True
    
    # =========================================================================
    # STEP 4: ARRANGE & EDIT
    # =========================================================================
    
    def arrange_and_edit(self):
        """Step 4: Structure the arrangement, add variations"""
        self.log("\n" + "=" * 60)
        self.log("STEP 4: ARRANGE & EDIT")
        self.log("=" * 60)
        
        # Calculate positions
        positions = []
        current = 0
        for i, bars in enumerate(SCENE_BARS):
            positions.append(current)
            current += bars
        
        self.log("Arrangement structure:")
        for i, (pos, name) in enumerate(zip(positions, SCENE_STRUCTURE)):
            self.log(f"  Bar {pos}: {name} ({SCENE_BARS[i]} bars)")
        
        # Add transitions - insert silence or duplicate sections
        self.log("\nAdding extensions and variations...")
        
        # Extend the intro
        self.log("  Extending intro...")
        self.cmd("insert_silence", {"position_bar": 0, "length_bars": 4})
        positions = [p + 4 for p in positions]
        
        # Add a build repeat before drop
        drop_idx = SCENE_STRUCTURE.index("Drop")
        if drop_idx > 0:
            build_start = positions[drop_idx - 1]
            build_length = SCENE_BARS[drop_idx - 1]
            drop_start = positions[drop_idx]
            self.log(f"  Adding build repeat before drop at bar {build_start}...")
            self.cmd("duplicate_time_range", {
                "start_bar": build_start + build_length // 2,
                "end_bar": build_start + build_length,
                "insert_position": drop_start - 4,
            })
            positions = [p + 4 if p >= drop_start else p for p in positions]
        
        # Add breakdown extension
        breakdown_idx = SCENE_STRUCTURE.index("Breakdown")
        if breakdown_idx > 0:
            bd_start = positions[breakdown_idx]
            bd_length = SCENE_BARS[breakdown_idx]
            self.log(f"  Extending breakdown at bar {bd_start}...")
            self.cmd("insert_silence", {"position_bar": bd_start + bd_length, "length_bars": 4})
            positions = [p + 4 if p >= bd_start + bd_length else p for p in positions]
        
        # Duplicate last verse for more energy
        verse2_idx = SCENE_STRUCTURE.index("Verse 2") if "Verse 2" in SCENE_STRUCTURE else len(SCENE_STRUCTURE) - 2
        if verse2_idx >= 0:
            v2_start = positions[verse2_idx]
            v2_length = SCENE_BARS[verse2_idx]
            outro_start = positions[-1]
            self.log(f"  Repeating Verse 2 at bar {v2_start}...")
            self.cmd("duplicate_time_range", {
                "start_bar": v2_start,
                "end_bar": v2_start + v2_length,
                "insert_position": v2_start + v2_length,
            })
            positions = [p + v2_length if p >= v2_start + v2_length else p for p in positions]
        
        # Get final arrangement info
        clips = self.cmd("get_arrangement_clips")
        if clips.get("status") == "success":
            arrangement_clips = clips.get("result", {}).get("arrangement_clips", [])
            self.log(f"\nArrangement now has {len(arrangement_clips)} clips")
            for clip in arrangement_clips[:10]:  # Show first 10
                self.log(f"  Track {clip.get('track_index')}, Clip {clip.get('clip_index')}: "
                        f"{clip.get('name')} at bar {clip.get('position', 0)/4.0:.1f}")
        
        # Consolidate clips for cleaner arrangement
        self.log("\nConsolidating clips...")
        self.cmd("consolidate_arrangement")
        time.sleep(1)
        
        self.log("Arrange and edit complete!")
        return True
    
    # =========================================================================
    # STEP 5: MIX AUTOMATION
    # =========================================================================
    
    def mix_automation(self):
        """Step 5: Add automation for mix dynamics"""
        self.log("\n" + "=" * 60)
        self.log("STEP 5: MIX AUTOMATION")
        self.log("=" * 60)
        
        # Calculate key positions
        positions = []
        current = 0
        for bars in SCENE_BARS:
            positions.append(current)
            current += bars
        total_bars = current
        
        # Adjust for our extensions
        total_bars += 12  # Account for added bars
        
        self.log(f"Total arrangement length: {total_bars} bars")
        
        # HALF TIME - Filter sweeps and transitions
        self.log("\nAdding filter automation...")
        for track_idx in [0, 1, 2, 3]:  # Drums, Bass, Chords, Lead
            # Filter sweep every 16 bars
            for bar_pos in range(0, total_bars, 16):
                end_bar = min(bar_pos + 12, total_bars - 1)
                if bar_pos < 8:  # Don't sweep in intro
                    continue
                
                self.cmd("create_filter_sweep", {
                    "track_index": track_idx,
                    "start_bar": bar_pos,
                    "end_bar": end_bar,
                    "start_freq": 100.0,
                    "end_freq": 5000.0,
                    "device_index": 0,
                    "parameter_index": 0,
                    "curve": "exponential",
                })
                self.stats["automation_points"] += 4  # Approximate
        
        # Volume automation
        self.log("\nAdding volume automation...")
        
        # Intro - fade in
        self.log("  Master volume fade in...")
        self.cmd("create_volume_automation_ramp", {
            "track_index": -1,  # Master
            "start_bar": 0,
            "end_bar": 8,
            "start_volume": 0.0,
            "end_volume": 0.8,
            "curve": "s_curve",
        })
        self.stats["automation_points"] += 8
        
        # Breakdown - volume drop
        breakdown_pos = positions[SCENE_STRUCTURE.index("Breakdown")] + 4 if "Breakdown" in SCENE_STRUCTURE else total_bars // 2
        self.log(f"  Volume drop at breakdown (bar {breakdown_pos})...")
        for track_idx in [0, 1]:  # Drums and Bass stay
            self.cmd("create_volume_automation_ramp", {
                "track_index": track_idx,
                "start_bar": breakdown_pos,
                "end_bar": breakdown_pos + 4,
                "start_volume": 1.0,
                "end_volume": 0.6,
                "curve": "linear",
            })
        for track_idx in [2, 3, 4, 6, 7]:  # Other tracks drop more
            self.cmd("create_volume_automation_ramp", {
                "track_index": track_idx,
                "start_bar": breakdown_pos,
                "end_bar": breakdown_pos + 4,
                "start_volume": 1.0,
                "end_volume": 0.3,
                "curve": "s_curve",
            })
        self.stats["automation_points"] += 16
        
        # Drop - volume spike
        drop_pos = positions[SCENE_STRUCTURE.index("Drop")] + 8 if "Drop" in SCENE_STRUCTURE else total_bars * 2 // 3
        self.log(f"  Volume spike at drop (bar {drop_pos})...")
        for track_idx in [0, 1, 5]:  # Drums, Bass, Percussion
            self.cmd("create_volume_automation_ramp", {
                "track_index": track_idx,
                "start_bar": drop_pos - 2,
                "end_bar": drop_pos,
                "start_volume": 0.8,
                "end_volume": 1.0,
                "curve": "s_curve",
            })
        self.stats["automation_points"] += 8
        
        # FX automation - rise before drop
        fx_pos = drop_pos - 4
        self.log(f"  FX sweep before drop (bar {fx_pos})...")
        self.cmd("create_volume_automation_ramp", {
            "track_index": 4,
            "start_bar": fx_pos,
            "end_bar": drop_pos,
            "start_volume": 0.1,
            "end_volume": 0.6,
            "curve": "exponential",
        })
        self.stats["automation_points"] += 4
        
        # Return track sends automation
        self.log("\nAdding return send automation...")
        rt = self.cmd("get_return_tracks").get("result", {}).get("return_tracks", [])
        reverb_idx = next((r.get("index") for r in rt if "Reverb" in r.get("name", "")), None)
        delay_idx = next((r.get("index") for r in rt if "Delay" in r.get("name", "")), None)
        
        if reverb_idx is not None:
            # More reverb in breakdown
            self.cmd("add_arrangement_track_automation", {
                "track_index": 2,  # Chords
                "automation_type": f"send_{reverb_idx}",
                "bar_position": breakdown_pos,
                "value": 0.6,
            })
            self.cmd("add_arrangement_track_automation", {
                "track_index": 6,  # Strings
                "automation_type": f"send_{reverb_idx}",
                "bar_position": breakdown_pos,
                "value": 0.7,
            })
            self.stats["automation_points"] += 2
        
        if delay_idx is not None:
            # Delay on lead in drop
            self.cmd("add_arrangement_track_automation", {
                "track_index": 3,  # Lead
                "automation_type": f"send_{delay_idx}",
                "bar_position": drop_pos,
                "value": 0.5,
            })
            self.cmd("add_arrangement_track_automation", {
                "track_index": 3,
                "automation_type": f"send_{delay_idx}",
                "bar_position": drop_pos + 4,
                "value": 0.2,
            })
            self.stats["automation_points"] += 2
        
        # Master volume outro fade
        self.log("\nAdding outro fade...")
        outro_start = positions[-1] + 4 if len(positions) > 0 else total_bars - 8
        self.cmd("create_volume_automation_ramp", {
            "track_index": -1,
            "start_bar": outro_start,
            "end_bar": total_bars,
            "start_volume": 0.85,
            "end_volume": 0.0,
            "curve": "s_curve",
        })
        self.stats["automation_points"] += 8
        
        self.log(f"Mix automation complete! Added {self.stats['automation_points']} automation points")
        return True
    
    # =========================================================================
    # STEP 6: POLISH
    # =========================================================================
    
    def polish(self):
        """Step 6: Final polish - master FX, EQ, compression"""
        self.log("\n" + "=" * 60)
        self.log("STEP 6: POLISH")
        self.log("=" * 60)
        
        # Master effects already loaded, but let's ensure they're in order
        self.log("Configuring master effects...")
        
        # Master compression settings
        self.log("  Setting master compression...")
        self.client.udp_command("set_device_parameter", {
            "track_index": -1,
            "device_index": 0,
            "parameter_index": 0,  # Threshold
            "value": 0.3,
        })
        self.client.udp_command("set_device_parameter", {
            "track_index": -1,
            "device_index": 0,
            "parameter_index": 1,  # Ratio
            "value": 0.5,
        })
        self.client.udp_command("set_device_parameter", {
            "track_index": -1,
            "device_index": 0,
            "parameter_index": 2,  # Attack
            "value": 0.2,
        })
        self.client.udp_command("set_device_parameter", {
            "track_index": -1,
            "device_index": 0,
            "parameter_index": 3,  # Release
            "value": 0.4,
        })
        
        # Master limiter
        self.log("  Setting master limiter...")
        self.client.udp_command("set_device_parameter", {
            "track_index": -1,
            "device_index": 1,
            "parameter_index": 0,  # Ceiling
            "value": 0.9,
        })
        self.client.udp_command("set_device_parameter", {
            "track_index": -1,
            "device_index": 1,
            "parameter_index": 1,  # Output
            "value": 0.95,
        })
        
        # Apply mix template
        self.log("\nApplying dub techno mix template...")
        self.cmd("apply_mix_automation_template", {
            "template_name": "dub_techno",
            "intensity": 0.8,
        })
        
        # Final polish
        self.log("\nRunning final polish...")
        self.cmd("polish_arrangement_mix", {
            "master_volume": 0.85,
            "apply_limiter": True,
            "apply_compression": True,
            "finalize_automation": True,
        })
        
        # Set final arrangement view
        total_bars = sum(SCENE_BARS) + 12
        self.cmd("set_arrangement_view_position", {"bar": 0, "beat": 0})
        self.cmd("set_arrangement_zoom", {"zoom_level": 0.8})
        
        self.log("Polish complete!")
        return True
    
    # =========================================================================
    # STEP 7: SAVE & READY FOR MANUAL FINE-TUNING
    # =========================================================================
    
    def save_and_ready(self):
        """Step 7: Save the project and prepare for manual editing"""
        self.log("\n" + "=" * 60)
        self.log("STEP 7: SAVE & READY FOR MANUAL FINE-TUNING")
        self.log("=" * 60)
        
        # Set playhead to start
        self.cmd("set_playhead_position", {"bar": 0, "beat": 0})
        self.cmd("set_playhead_position", {"bar": 0, "beat": 0})
        
        # Stop any playing clips
        self.cmd("stop_playback")
        
        # Print final statistics
        self.log("\n" + "=" * 60)
        self.log("FINAL STATISTICS")
        self.log("=" * 60)
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.log(f"Total time: {elapsed:.1f} seconds")
        self.log(f"Commands sent: {self.stats['commands_sent']}")
        self.log(f"Clips created: {self.stats['clips_created']}")
        self.log(f"Scenes created: {self.stats['scenes_created']}")
        self.log(f"Arrangement length: {self.stats['arrangement_bars']} bars")
        self.log(f"Automation points: {self.stats['automation_points']}")
        self.log(f"BPM: {BPM}")
        self.log(f"Tracks: {len(TRACK_CONFIG)}")
        
        self.log("\n" + "=" * 60)
        self.log("MIX READY FOR MANUAL FINE-TUNING!")
        self.log("=" * 60)
        self.log("\nNext steps:")
        self.log("1. Open Ableton Live")
        self.log("2. Switch to Arrangement View (Tab)")
        self.log("3. Review the arrangement structure")
        self.log("4. Fine-tune automation curves")
        self.log("5. Adjust individual notes and velocities")
        self.log("6. Export your mix (File > Export)")
        self.log("\nYou can also use the MCP server tools to:")
        self.log("- get_arrangement_clips: View all arrangement clips")
        self.log("- add_arrangement_automation_point: Add custom automation")
        self.log("- crop_arrangement_clip: Trim clips")
        self.log("- split_arrangement_clip: Split clips for editing")
        self.log("- consolidate_arrangement: Merge clips")
        
        # Save logs
        log_file = f"e2e_mix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, "w") as f:
            f.write(f"E2E Mix Producer Log\n")
            f.write(f"Started: {self.start_time}\n")
            f.write(f"Completed: {datetime.now()}\n")
            f.write(f"\n")
            for log_entry in self.logs:
                f.write(log_entry + "\n")
            f.write(f"\n\nFinal Statistics:\n")
            for key, value in self.stats.items():
                f.write(f"  {key}: {value}\n")
        
        self.log(f"\nLogs saved to: {log_file}")
        return True
    
    # =========================================================================
    # MAIN WORKFLOW
    # =========================================================================
    
    def run_full_workflow(self, start_step=1, end_step=7):
        """Run the complete end-to-end workflow"""
        self.log("\n" + "=" * 60)
        self.log("E2E MIX PRODUCER - FULL WORKFLOW")
        self.log("=" * 60)
        
        self.log(f"\nRunning steps {start_step} to {end_step}")
        
        steps = [
            (1, "Setup Session", self.setup_session),
            (2, "Create Content", self.create_content),
            (3, "Session to Arrangement", self.session_to_arrangement),
            (4, "Arrange & Edit", self.arrange_and_edit),
            (5, "Mix Automation", self.mix_automation),
            (6, "Polish", self.polish),
            (7, "Save & Ready", self.save_and_ready),
        ]
        
        for step_num, step_name, step_func in steps:
            if step_num < start_step:
                continue
            if step_num > end_step:
                break
            
            self.log(f"\n{'='*60}")
            self.log(f"STARTING STEP {step_num}: {step_name}")
            self.log(f"{'='*60}")
            
            try:
                result = step_func()
                if not result:
                    self.log(f"\nWARNING: Step {step_num} ({step_name}) did not complete successfully")
                    self.log("Continuing anyway...")
                else:
                    self.log(f"\nStep {step_num} ({step_name}) COMPLETE!")
            except Exception as e:
                self.log(f"\nERROR in Step {step_num} ({step_name}): {e}")
                self.log("Continuing anyway...")
        
        # Final summary
        self.save_and_ready()
        
        self.log("\n" + "=" * 60)
        self.log("WORKFLOW COMPLETE!")
        self.log("=" * 60)
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="E2E Mix Producer for Ableton Live MCP Extended")
    parser.add_argument("--start", type=int, default=1, help="Start from step number (1-7)")
    parser.add_argument("--end", type=int, default=7, help="End at step number (1-7)")
    parser.add_argument("--fast", action="store_true", help="Skip some time-consuming steps")
    args = parser.parse_args()
    
    producer = E2EMixProducer()
    
    try:
        start = args.start if 1 <= args.start <= 7 else 1
        end = args.end if 1 <= args.end <= 7 else 7
        
        if start > end:
            print("Error: start must be <= end")
            return 1
        
        producer.run_full_workflow(start_step=start, end_step=end)
        
        return 0
    except KeyboardInterrupt:
        producer.log("\nWorkflow interrupted by user")
        return 1
    except Exception as e:
        producer.log(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        producer.client.close()


if __name__ == "__main__":
    sys.exit(main())
