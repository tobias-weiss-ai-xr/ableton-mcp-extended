#!/usr/bin/env python3
"""
2-Hour Dub Techno Live Automation Script

This script automates a 2-hour dub techno playback session:
- 8 scenes, 15 minutes each = 120 minutes
- Filter sweeps, drops, and energy curves
- Scene progression with parameter automation

Usage:
1. Load the dub techno session in Ableton
2. Start this script: python live_dub_automation.py
3. The script will trigger Scene 1 and automate for 2 hours
4. Press Ctrl+C to stop

Architecture:
- TCP (port 9877) for reliable scene triggers
- UDP (port 9878) for high-frequency parameter changes
"""

import socket
import json
import time
import signal
import sys
from dataclasses import dataclass
from typing import List, Optional

# Configuration
TCP_HOST = "localhost"
TCP_PORT = 9877
UDP_HOST = "localhost"
UDP_PORT = 9878

BPM = 128
BEAT_DURATION = 60.0 / BPM  # ~0.469 seconds per beat
SCENE_DURATION_BEATS = 2250  # 15 minutes in beats (15 * 60 * 128 / 60 = 1920, rounded)
SCENE_DURATION_SECONDS = 15 * 60  # 15 minutes

# Scene configuration
SCENES = [
    {"index": 0, "name": "Opening", "key": "Am", "energy": 0.2},
    {"index": 1, "name": "First Beat", "key": "Am", "energy": 0.4},
    {"index": 2, "name": "Deep Groove", "key": "Dm", "energy": 0.6},
    {"index": 3, "name": "First Build", "key": "Dm", "energy": 0.8},
    {"index": 4, "name": "Breakdown", "key": "Em", "energy": 0.3},
    {"index": 5, "name": "Return", "key": "Em", "energy": 0.7},
    {"index": 6, "name": "Peak", "key": "Gm", "energy": 1.0},
    {"index": 7, "name": "Outro", "key": "Am", "energy": 0.1},
]

# Track device indices (from get_track_info)
# Each track has: GrainDelay (idx 1), GlueCompressor (idx 2), Saturator (idx 3), EQ8 (idx 4), Compressor (idx 5)
TRACK_DEVICES = {
    "drums": {
        "track_index": 0,
        "filter_device": 0,
        "filter_param": 0,
    },  # Drum rack filter
    "bass": {"track_index": 1, "filter_device": 4, "filter_param": 0},  # EQ8 filter
    "hats": {"track_index": 2, "filter_device": 4, "filter_param": 0},
    "chord": {"track_index": 3, "filter_device": 4, "filter_param": 0},
    "pad": {"track_index": 4, "filter_device": 4, "filter_param": 0},
    "percussion": {"track_index": 5, "filter_device": 4, "filter_param": 0},
}


@dataclass
class AutomationPoint:
    """A single automation point."""

    track_index: int
    device_index: int
    parameter_index: int
    value: float
    time_offset: float  # seconds from section start


class MCPClient:
    """Dual-protocol MCP client for Ableton control."""

    def __init__(self):
        self.tcp_socket: Optional[socket.socket] = None
        self.udp_socket: Optional[socket.socket] = None
        self.running = True

    def connect(self):
        """Connect to MCP servers."""
        # TCP for reliable operations
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((TCP_HOST, TCP_PORT))
        print(f"TCP connected to {TCP_HOST}:{TCP_PORT}")

        # UDP for high-frequency parameter changes
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"UDP socket ready for {UDP_HOST}:{UDP_PORT}")

    def disconnect(self):
        """Disconnect from servers."""
        if self.tcp_socket:
            self.tcp_socket.close()
        if self.udp_socket:
            self.udp_socket.close()

    def send_tcp(self, command_type: str, params: dict = None) -> dict:
        """Send command via TCP and wait for response."""
        message = {"type": command_type}
        if params:
            message["params"] = params

        self.tcp_socket.send(json.dumps(message).encode() + b"\n")
        response = self.tcp_socket.recv(8192).decode()
        return json.loads(response)

    def send_udp(self, command_type: str, params: dict):
        """Send fire-and-forget command via UDP."""
        message = {"type": command_type, "params": params}
        self.udp_socket.sendto(json.dumps(message).encode(), (UDP_HOST, UDP_PORT))

    def fire_scene(self, scene_index: int):
        """Trigger a scene via TCP."""
        response = self.send_tcp("fire_scene", {"scene_index": scene_index})
        print(f"Triggered scene {scene_index}: {response}")

    def set_parameter_udp(
        self, track_index: int, device_index: int, param_index: int, value: float
    ):
        """Set device parameter via UDP (high-frequency)."""
        self.send_udp(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": param_index,
                "value": max(0.0, min(1.0, value)),  # Clamp to valid range
            },
        )

    def set_track_volume_udp(self, track_index: int, volume: float):
        """Set track volume via UDP."""
        self.send_udp(
            "set_track_volume",
            {"track_index": track_index, "volume": max(0.0, min(1.0, volume))},
        )


class DubTechnoAutomation:
    """Main automation controller."""

    def __init__(self, client: MCPClient):
        self.client = client
        self.start_time = 0
        self.current_scene = -1

    def progress_bar(self, progress: float, width: int = 40) -> str:
        """Generate a visual progress bar."""
        filled = int(width * progress)
        empty = width - filled
        return f"[{'=' * filled}{'-' * empty}] {progress * 100:.1f}%"

    def format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def filter_sweep_build(
        self,
        tracks: List[str],
        start_value: float,
        end_value: float,
        duration_seconds: float,
        steps: int = 50,
    ):
        """
        Gradually sweep filter cutoff across multiple tracks.

        Args:
            tracks: List of track names (e.g., ["drums", "bass", "chord"])
            start_value: Starting normalized value (0.0-1.0)
            end_value: Ending normalized value (0.0-1.0)
            duration_seconds: Duration of sweep
            steps: Number of steps in the sweep
        """
        step_duration = duration_seconds / steps
        value_step = (end_value - start_value) / steps

        for i in range(steps):
            value = start_value + (value_step * i)
            for track_name in tracks:
                device = TRACK_DEVICES.get(track_name)
                if device:
                    self.client.set_parameter_udp(
                        device["track_index"],
                        device["filter_device"],
                        device["filter_param"],
                        value,
                    )
            time.sleep(step_duration)

    def dub_drop(
        self,
        tracks: List[str],
        drop_value: float = 0.1,
        return_value: float = 0.5,
        drop_duration: float = 2.0,
        return_duration: float = 10.0,
    ):
        """
        Perform a dub-style drop: filters close suddenly, then gradually reopen.

        Args:
            tracks: List of track names to affect
            drop_value: Filter value during drop (low = closed filter)
            return_value: Filter value to return to
            drop_duration: How fast to drop (seconds)
            return_duration: How slow to return (seconds)
        """
        # Quick drop
        for track_name in tracks:
            device = TRACK_DEVICES.get(track_name)
            if device:
                self.client.set_parameter_udp(
                    device["track_index"],
                    device["filter_device"],
                    device["filter_param"],
                    drop_value,
                )

        time.sleep(drop_duration)

        # Gradual return
        self.filter_sweep_build(
            tracks, drop_value, return_value, return_duration, steps=30
        )

    def energy_curve(
        self, track_volumes: dict, duration_seconds: float, steps: int = 100
    ):
        """
        Apply energy curve to track volumes.

        Args:
            track_volumes: Dict mapping track_index to (start_vol, end_vol)
            duration_seconds: Duration of curve
            steps: Number of steps
        """
        step_duration = duration_seconds / steps

        for i in range(steps):
            progress = i / steps
            for track_index, (start_vol, end_vol) in track_volumes.items():
                value = start_vol + (end_vol - start_vol) * progress
                self.client.set_track_volume_udp(track_index, value)
            time.sleep(step_duration)

    def run_section(self, scene_index: int):
        """Run automation for one 15-minute section."""
        scene = SCENES[scene_index]
        energy = scene["energy"]

        print(f"\n{'=' * 60}")
        print(f"SECTION {scene_index + 1}/8: {scene['name']}")
        print(f"Key: {scene['key']} | Energy: {energy * 100:.0f}%")
        print(f"{'=' * 60}")

        # Trigger the scene
        self.client.fire_scene(scene_index)
        self.current_scene = scene_index
        section_start = time.time()

        # Set initial volumes based on energy
        base_volume = 0.5 + (energy * 0.35)  # 0.5 to 0.85
        for i in range(6):
            self.client.set_track_volume_udp(i, base_volume)

        # Section-specific automation
        elapsed = 0

        # Every 2 minutes, do some automation
        while elapsed < SCENE_DURATION_SECONDS and self.client.running:
            # Calculate progress
            elapsed = time.time() - section_start
            progress = elapsed / SCENE_DURATION_SECONDS

            # Print progress
            print(
                f"\r{self.progress_bar(progress)} | {self.format_time(elapsed)} / {self.format_time(SCENE_DURATION_SECONDS)}",
                end="",
            )

            # Automation patterns based on scene type
            if scene_index in [0, 7]:  # Opening/Outro - subtle evolution
                if elapsed % 120 < 1:  # Every 2 minutes
                    self.filter_sweep_build(
                        ["pad", "chord"],
                        0.4 + (progress * 0.3),
                        0.5 + (progress * 0.3),
                        30.0,
                        steps=20,
                    )

            elif scene_index in [3, 6]:  # Builds - filter sweeps
                if elapsed % 60 < 1:  # Every minute
                    build_progress = (elapsed % 60) / 60
                    self.filter_sweep_build(
                        ["drums", "bass", "chord"],
                        0.3 + (build_progress * 0.4),
                        0.6 + (build_progress * 0.3),
                        15.0,
                        steps=30,
                    )

            elif scene_index == 4:  # Breakdown - drop and return
                if elapsed < 5:  # Start with drop
                    self.dub_drop(
                        ["drums", "bass", "hats"],
                        drop_value=0.1,
                        return_value=0.4,
                        drop_duration=1.0,
                        return_duration=30.0,
                    )

            else:  # Standard sections - gentle evolution
                if elapsed % 90 < 1:  # Every 90 seconds
                    self.filter_sweep_build(["chord", "pad"], 0.4, 0.6, 20.0, steps=15)

            # Sleep a bit to avoid CPU thrash
            time.sleep(0.5)

        print()  # New line after progress bar

    def run_2_hours(self):
        """Run the full 2-hour automation."""
        print("\n" + "=" * 60)
        print("2-HOUR DUB TECHNO AUTOMATION")
        print("=" * 60)
        print(f"Starting at: {time.strftime('%H:%M:%S')}")
        print(
            f"Expected end: {time.strftime('%H:%M:%S', time.localtime(time.time() + 2 * 60 * 60))}"
        )
        print("\nPress Ctrl+C to stop\n")

        self.start_time = time.time()

        try:
            for scene_index in range(8):
                if not self.client.running:
                    break
                self.run_section(scene_index)

            print("\n" + "=" * 60)
            print("2-HOUR AUTOMATION COMPLETE!")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\nAutomation stopped by user")

        total_elapsed = time.time() - self.start_time
        print(f"Total runtime: {self.format_time(total_elapsed)}")


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    print("\n\nReceived interrupt signal, stopping...")
    sys.exit(0)


def main():
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    client = MCPClient()

    try:
        client.connect()

        # Verify connection
        response = client.send_tcp("get_session_info", {})
        print(
            f"Session: {response.get('track_count', '?')} tracks, {response.get('tempo', '?')} BPM"
        )

        # Start automation
        automation = DubTechnoAutomation(client)
        automation.run_2_hours()

    except ConnectionRefusedError:
        print("ERROR: Could not connect to MCP server")
        print("Make sure Ableton is running with the MCP Remote Script loaded")
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
