#!/usr/bin/env python3
"""
DUB REGGAE 2-HOUR LIVE PERFORMANCE AUTOMATION

Session: 4 tracks (Drums, Bass, Rhythm_Skank, Horns_Melody)
Tempo: 75 BPM
Duration: 120 minutes (2 hours)
Clips: 8 per track (32 total)

Features:
- Automatic clip switching with variation
- Volume automation (dub drops, builds)
- Effect parameter automation (GrainDelay, Saturator)
- Send automation (Reverb, Delay)
- Scene-based progression
"""

import socket
import json
import random
import time
import math
from typing import List, Dict, Optional, Any
import threading
import sys

# Configuration
TCP_HOST = "localhost"
TCP_PORT = 9877
UDP_HOST = "localhost"
UDP_PORT = 9878

# Track indices
TRACKS = {
    "drums": 0,
    "bass": 1,
    "skank": 2,
    "horns": 3,
}

# Device indices per track
DEVICES = {
    "drums": {
        "grain_delay": 1,  # "Five"
        "saturator": 3,  # "A Bit Warmer"
    },
    "bass": {
        "grain_delay": 1,  # "Five"
    },
    "skank": {
        "grain_delay": 1,  # "Five"
        "saturator": 3,  # "A Bit Warmer"
    },
    "horns": {
        "saturator": 1,  # "A Bit Warmer"
    },
}

# Send indices (return tracks)
SENDS = {
    "reverb": 0,  # A-Reverb
    "delay": 1,  # B-Delay
}

# Performance sections (2 hours = 8 sections × 15 minutes)
SECTIONS = [
    {
        "name": "Roots Intro",
        "duration_minutes": 15,
        "energy": 0.4,
        "clip_pattern": [0, 0, 1, 0, 2, 0, 1, 0],  # Drums pattern
        "bass_pattern": [0, 0, 1, 0, 2, 0, 1, 0],
        "skank_pattern": [0, 0, 0, 1, 0, 0, 1, 0],
        "horn_pattern": [0, 1, 0, 2, 0, 1, 0, 0],
        "reverb_send": 0.3,
        "delay_send": 0.4,
    },
    {
        "name": "Conscious Vibes",
        "duration_minutes": 15,
        "energy": 0.5,
        "clip_pattern": [1, 1, 2, 1, 3, 1, 2, 1],
        "bass_pattern": [1, 1, 2, 1, 3, 1, 2, 1],
        "skank_pattern": [0, 1, 0, 2, 0, 1, 0, 3],
        "horn_pattern": [1, 2, 1, 3, 1, 2, 1, 0],
        "reverb_send": 0.35,
        "delay_send": 0.45,
    },
    {
        "name": "Dub Builders",
        "duration_minutes": 15,
        "energy": 0.65,
        "clip_pattern": [2, 3, 2, 4, 2, 3, 2, 5],
        "bass_pattern": [2, 3, 2, 4, 2, 3, 2, 5],
        "skank_pattern": [1, 2, 1, 4, 1, 2, 1, 5],
        "horn_pattern": [2, 3, 2, 4, 2, 3, 2, 5],
        "reverb_send": 0.4,
        "delay_send": 0.5,
    },
    {
        "name": "Heavy Dub",
        "duration_minutes": 15,
        "energy": 0.8,
        "clip_pattern": [5, 6, 5, 7, 5, 6, 5, 4],
        "bass_pattern": [4, 5, 4, 6, 4, 5, 4, 7],
        "skank_pattern": [4, 5, 4, 6, 4, 5, 4, 7],
        "horn_pattern": [4, 5, 4, 6, 4, 5, 4, 7],
        "reverb_send": 0.5,
        "delay_send": 0.55,
    },
    {
        "name": "Steppers Deep",
        "duration_minutes": 15,
        "energy": 0.75,
        "clip_pattern": [2, 5, 2, 6, 2, 5, 2, 7],
        "bass_pattern": [2, 4, 2, 5, 2, 4, 2, 6],
        "skank_pattern": [2, 4, 2, 5, 2, 4, 2, 6],
        "horn_pattern": [2, 4, 2, 5, 2, 4, 2, 6],
        "reverb_send": 0.45,
        "delay_send": 0.5,
    },
    {
        "name": "Dub Breakdown",
        "duration_minutes": 15,
        "energy": 0.5,
        "clip_pattern": [3, 0, 4, 0, 3, 0, 4, 0],
        "bass_pattern": [6, 0, 7, 0, 6, 0, 7, 0],
        "skank_pattern": [6, 7, 6, 7, 6, 7, 6, 7],
        "horn_pattern": [5, 6, 5, 6, 5, 6, 5, 6],
        "reverb_send": 0.6,
        "delay_send": 0.65,
    },
    {
        "name": "Climax Dub",
        "duration_minutes": 15,
        "energy": 0.9,
        "clip_pattern": [7, 5, 7, 6, 7, 5, 7, 6],
        "bass_pattern": [4, 5, 4, 6, 4, 5, 4, 6],
        "skank_pattern": [4, 5, 4, 6, 4, 5, 4, 6],
        "horn_pattern": [7, 4, 7, 5, 7, 4, 7, 5],
        "reverb_send": 0.55,
        "delay_send": 0.6,
    },
    {
        "name": "Spiritual Out",
        "duration_minutes": 15,
        "energy": 0.3,
        "clip_pattern": [0, 3, 0, 3, 0, 3, 0, 3],
        "bass_pattern": [2, 7, 2, 7, 2, 7, 2, 7],
        "skank_pattern": [6, 7, 6, 7, 6, 7, 6, 7],
        "horn_pattern": [5, 6, 5, 6, 5, 6, 5, 6],
        "reverb_send": 0.7,
        "delay_send": 0.75,
    },
]


class DubReggaeLive:
    def __init__(self):
        self.tcp_socket = None
        self.udp_socket = None
        self.running = True
        self.current_section = 0
        self.start_time = None
        self.clip_index = {0: 0, 1: 0, 2: 0, 3: 0}  # Track current clip per track

    def connect(self):
        """Connect to Ableton MCP server"""
        print("🔌 Connecting to Ableton MCP...")

        # TCP connection
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.tcp_socket.connect((TCP_HOST, TCP_PORT))
            print(f"✅ TCP connected to {TCP_HOST}:{TCP_PORT}")
        except Exception as e:
            print(f"❌ TCP connection failed: {e}")
            return False

        # UDP connection
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"✅ UDP ready on {UDP_HOST}:{UDP_PORT}")

        return True

    def send_tcp_command(
        self, command_type: str, params: Dict = None
    ) -> Optional[Dict]:
        """Send TCP command and get response"""
        if params is None:
            params = {}

        command = {"type": command_type, "params": params}

        try:
            self.tcp_socket.sendall((json.dumps(command) + "\n").encode())
            response = b""
            while True:
                chunk = self.tcp_socket.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"\n" in chunk:
                    break
            return json.loads(response.decode().strip())
        except Exception as e:
            print(f"❌ TCP error: {e}")
            return None

    def send_udp_command(self, command_type: str, params: Dict = None):
        """Send UDP command (fire and forget)"""
        if params is None:
            params = {}

        command = {"type": command_type, "params": params}

        try:
            self.udp_socket.sendto(json.dumps(command).encode(), (UDP_HOST, UDP_PORT))
        except Exception as e:
            print(f"❌ UDP error: {e}")

    def fire_clip(self, track_index: int, clip_index: int):
        """Fire a clip on a track"""
        self.send_tcp_command(
            "fire_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        self.clip_index[track_index] = clip_index

    def set_track_volume(self, track_index: int, volume: float):
        """Set track volume (0.0-1.0)"""
        self.send_udp_command(
            "set_track_volume", {"track_index": track_index, "volume": volume}
        )

    def set_device_parameter(
        self, track_index: int, device_index: int, parameter_index: int, value: float
    ):
        """Set device parameter via UDP"""
        self.send_udp_command(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "value": value,
            },
        )

    def set_send_amount(self, track_index: int, send_index: int, amount: float):
        """Set send amount to return track"""
        self.send_tcp_command(
            "set_send_amount",
            {"track_index": track_index, "send_index": send_index, "amount": amount},
        )

    def get_elapsed_minutes(self) -> float:
        """Get elapsed time in minutes"""
        if self.start_time is None:
            return 0
        return (time.time() - self.start_time) / 60

    def get_current_section(self) -> int:
        """Determine current section based on elapsed time"""
        elapsed = self.get_elapsed_minutes()
        cumulative = 0
        for i, section in enumerate(SECTIONS):
            cumulative += section["duration_minutes"]
            if elapsed < cumulative:
                return i
        return len(SECTIONS) - 1

    def apply_dub_drop(self, tracks: List[int], duration_beats: float = 8):
        """Apply dub drop to specified tracks"""
        for track in tracks:
            # Quick volume drop
            self.set_track_volume(track, 0.3)

        time.sleep(duration_beats * 60 / 75)  # Convert beats to seconds

        for track in tracks:
            # Return volume
            self.set_track_volume(track, 0.8)

    def apply_dub_build(self, tracks: List[int], duration_beats: float = 16):
        """Apply dub build to specified tracks"""
        steps = 16
        for i in range(steps):
            progress = i / steps
            for track in tracks:
                volume = 0.3 + (0.5 * progress)
                self.set_track_volume(track, volume)
            time.sleep((duration_beats / steps) * 60 / 75)

    def vary_grain_delay(self, track_index: int, device_index: int):
        """Randomly vary GrainDelay parameters"""
        # Spray (param 1): 0.0-0.3
        self.set_device_parameter(track_index, device_index, 1, random.uniform(0, 0.3))
        # Feedback (param 5): 0.0-0.6
        self.set_device_parameter(
            track_index, device_index, 5, random.uniform(0.1, 0.6)
        )
        # DryWet (param 6): 0.3-0.7
        self.set_device_parameter(
            track_index, device_index, 6, random.uniform(0.3, 0.7)
        )

    def vary_saturator(self, track_index: int, device_index: int, intensity: float):
        """Vary saturator based on intensity"""
        # Drive (param 1): 0.4-0.8 based on intensity
        drive = 0.4 + (0.4 * intensity)
        self.set_device_parameter(track_index, device_index, 1, drive)
        # Dry/Wet (param 11): 0.4-0.8
        drywet = 0.4 + (0.4 * intensity)
        self.set_device_parameter(track_index, device_index, 11, drywet)

    def switch_clips_for_section(self, section: Dict):
        """Switch clips based on section pattern"""
        track_patterns = {
            0: section["clip_pattern"],  # Drums
            1: section["bass_pattern"],  # Bass
            2: section["skank_pattern"],  # Skank
            3: section["horn_pattern"],  # Horns
        }

        for track_idx, pattern in track_patterns.items():
            # Get next clip from pattern with some randomness
            if random.random() < 0.2:  # 20% chance of random clip
                clip_idx = random.randint(0, 7)
            else:
                pattern_pos = int(self.get_elapsed_minutes() * 4) % len(pattern)
                clip_idx = pattern[pattern_pos]

            if clip_idx != self.clip_index[track_idx]:
                self.fire_clip(track_idx, clip_idx)

    def update_sends_for_section(self, section: Dict):
        """Update send amounts based on section"""
        for track_idx in range(4):
            self.set_send_amount(track_idx, SENDS["reverb"], section["reverb_send"])
            self.set_send_amount(track_idx, SENDS["delay"], section["delay_send"])

    def run_automation_cycle(self):
        """Run one automation cycle (every 30 seconds)"""
        current_section_idx = self.get_current_section()
        section = SECTIONS[current_section_idx]

        # Check for section change
        if current_section_idx != self.current_section:
            print(f"\n🎵 Section changed: {section['name']}")
            self.current_section = current_section_idx
            self.update_sends_for_section(section)

        # Random clip switching (30% chance per track)
        for track_idx in range(4):
            if random.random() < 0.3:
                new_clip = random.randint(0, 7)
                if new_clip != self.clip_index[track_idx]:
                    self.fire_clip(track_idx, new_clip)
                    print(f"  🎶 Track {track_idx}: Switched to clip {new_clip}")

        # Random dub effects (10% chance)
        if random.random() < 0.1:
            tracks_to_drop = random.sample([0, 1, 2, 3], random.randint(1, 3))
            print(f"  💧 Dub drop on tracks: {tracks_to_drop}")
            threading.Thread(target=self.apply_dub_drop, args=(tracks_to_drop,)).start()

        # Vary effects (50% chance)
        if random.random() < 0.5:
            for track_name, devices in DEVICES.items():
                track_idx = TRACKS[track_name]
                if "grain_delay" in devices:
                    self.vary_grain_delay(track_idx, devices["grain_delay"])
                if "saturator" in devices:
                    self.vary_saturator(
                        track_idx, devices["saturator"], section["energy"]
                    )

        # Volume automation based on energy
        for track_idx in range(4):
            base_volume = 0.6 + (0.3 * section["energy"])
            variation = random.uniform(-0.1, 0.1)
            self.set_track_volume(track_idx, base_volume + variation)

    def print_progress(self):
        """Print progress bar"""
        elapsed = self.get_elapsed_minutes()
        total = 120  # 2 hours
        progress = min(elapsed / total, 1.0)

        bar_length = 40
        filled = int(bar_length * progress)
        bar = "=" * filled + "-" * (bar_length - filled)

        section = SECTIONS[self.current_section]
        print(
            f"\r[{bar}] {progress * 100:.1f}% | {elapsed:.1f}/{total}min | {section['name']}",
            end="",
        )

    def run(self):
        """Main automation loop"""
        print("\n" + "=" * 60)
        print("🎵 DUB REGGAE 2-HOUR LIVE PERFORMANCE")
        print("=" * 60)
        print(f"Tracks: 4 | Clips: 32 | BPM: 75 | Duration: 120 min")
        print("=" * 60 + "\n")

        if not self.connect():
            print("❌ Failed to connect to Ableton")
            return

        self.start_time = time.time()

        # Initial setup
        print("🎚️ Setting initial levels...")
        for track_idx in range(4):
            self.set_track_volume(track_idx, 0.7)

        # Start first clips
        print("🔥 Starting initial clips...")
        for track_idx in range(4):
            self.fire_clip(track_idx, 0)

        print("\n🎵 Performance started! Press Ctrl+C to stop.\n")

        try:
            cycle_count = 0
            while self.running and self.get_elapsed_minutes() < 120:
                self.run_automation_cycle()
                self.print_progress()

                cycle_count += 1

                # Wait 30 seconds between cycles
                time.sleep(30)

        except KeyboardInterrupt:
            print("\n\n⏹️ Performance stopped by user")

        print(f"\n\n📊 Performance complete!")
        print(f"Duration: {self.get_elapsed_minutes():.1f} minutes")
        print(f"Automation cycles: {cycle_count}")

        # Cleanup
        self.tcp_socket.close()
        self.udp_socket.close()
        print("🔌 Disconnected from Ableton")


if __name__ == "__main__":
    # Fix Windows console encoding for emojis
    import sys
    import io

    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    performance = DubReggaeLive()
    performance.run()
