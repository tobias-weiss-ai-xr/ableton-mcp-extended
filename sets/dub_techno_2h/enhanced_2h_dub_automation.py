#!/usr/bin/env python3
"""
ENHANCED 2-HOUR DUB TECHNO AUTOMATION

This script creates a POWERFUL dub techno performance with:
- DEEP constant bass (0.9 volume, NEVER modulated)
- Rich Wavetable synthesis (oscillator sweeps, filter wobbles, LFO rhythms)
- Real-time evolving textures
- Automatic scene progression

Duration: 120 minutes (8 scenes × 15 minutes)
Total scenes: 8
BPM: 128
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

# Wavetable parameter indices
WAVETABLE_PARAMS = {
    "osc1_position": 4,
    "osc2_position": 12,
    "filter1_freq": 26,
    "filter1_reso": 27,
    "filter2_freq": 35,
    "filter2_reso": 36,
    "lfo1_shape": 70,
    "lfo1_amount": 71,
    "lfo1_rate": 75,
    "lfo2_shape": 79,
    "lfo2_amount": 80,
    "lfo2_rate": 84,
    "amp_attack": 39,
    "amp_decay": 40,
    "amp_sustain": 45,
    "amp_release": 41,
    "unison": 89,
    "volume": 92,
}

# Dub techno scene progression
SCENES = [
    {
        "index": 0,
        "name": "Opening",
        "key": "Am",
        "root": 57,  # A3
        "energy": 0.3,
        "filter_freq": 0.3,
        "filter_reso": 0.4,
        "lfo_rate": 0.2,
        "density": 0.4,
    },
    {
        "index": 1,
        "name": "First Beat",
        "key": "Am",
        "root": 57,
        "energy": 0.5,
        "filter_freq": 0.45,
        "filter_reso": 0.5,
        "lfo_rate": 0.25,
        "density": 0.6,
    },
    {
        "index": 2,
        "name": "Deep Groove",
        "key": "Dm",
        "root": 62,  # D3
        "energy": 0.7,
        "filter_freq": 0.6,
        "filter_reso": 0.55,
        "lfo_rate": 0.3,
        "density": 0.8,
    },
    {
        "index": 3,
        "name": "First Build",
        "key": "Dm",
        "root": 62,
        "energy": 0.85,
        "filter_freq": 0.75,
        "filter_reso": 0.6,
        "lfo_rate": 0.35,
        "density": 0.9,
    },
    {
        "index": 4,
        "name": "Breakdown",
        "key": "Em",
        "root": 64,  # E3
        "energy": 0.4,
        "filter_freq": 0.2,
        "filter_reso": 0.5,
        "lfo_rate": 0.15,
        "density": 0.3,
    },
    {
        "index": 5,
        "name": "Return",
        "key": "Em",
        "root": 64,
        "energy": 0.7,
        "filter_freq": 0.6,
        "filter_reso": 0.5,
        "lfo_rate": 0.3,
        "density": 0.7,
    },
    {
        "index": 6,
        "name": "Peak",
        "key": "Gm",
        "root": 67,  # G3
        "energy": 1.0,
        "filter_freq": 0.9,
        "filter_reso": 0.7,
        "lfo_rate": 0.4,
        "density": 1.0,
    },
    {
        "index": 7,
        "name": "Outro",
        "key": "Am",
        "root": 57,
        "energy": 0.2,
        "filter_freq": 0.15,
        "filter_reso": 0.3,
        "lfo_rate": 0.1,
        "density": 0.2,
    },
]

# Fixed volumes - BASS STAYS CONSTANT AT 0.9
VOLUMES = {
    0: 0.65,  # Drums
    1: 0.90,  # Bass - DEEP! CONSTANT! NO MODULATION!
    2: 0.45,  # Hats
    3: 0.25,  # Chord
    4: 0.20,  # Pad
    5: 0.40,  # Percussion
    6: 0.60,  # 64 Pads Dub Kit
}


class MCPClient:
    """Dual-protocol MCP client for Ableton control."""

    def __init__(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.connect((TCP_HOST, TCP_PORT))
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.tcp.close()
        self.udp.close()

    def send_tcp(self, cmd: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send reliable TCP command (request/response)."""
        msg = {"type": cmd, "params": params}
        self.tcp.send(json.dumps(msg).encode() + b"\n")
        response = self.tcp.recv(8192).decode()
        return json.loads(response)

    def send_udp(self, cmd: str, params: Dict[str, Any]):
        """Send fire-and-forget UDP command (no response)."""
        msg = {"type": cmd, "params": params}
        self.udp.sendto(json.dumps(msg).encode(), (UDP_HOST, UDP_PORT))

    def get_wavetable_device(self, track_index: int) -> Optional[int]:
        """Find Wavetable device on track."""
        response = self.send_tcp("get_track_info", {"track_index": track_index})
        devices = response.get("result", {}).get("devices", [])
        for device in devices:
            if "Wavetable" in device.get("name", ""):
                return device.get("index")
        return None

    def set_wavetable_position(
        self, track_index: int, oscillator: int, position: float
    ):
        """Set Wavetable oscillator position (shape)."""
        device_index = self.get_wavetable_device(track_index)
        if device_index is None:
            return

        param_index = (
            WAVETABLE_PARAMS["osc1_position"]
            if oscillator == 1
            else WAVETABLE_PARAMS["osc2_position"]
        )
        self.send_udp(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": param_index,
                "value": position,
            },
        )

    def wavetable_filter_sweep(
        self,
        track_index: int,
        start_freq: float,
        end_freq: float,
        duration: float = 60.0,
        filter_num: int = 1,
    ):
        """Filter frequency sweep over time."""
        device_index = self.get_wavetable_device(track_index)
        if device_index is None:
            return

        freq_param = (
            WAVETABLE_PARAMS["filter1_freq"]
            if filter_num == 1
            else WAVETABLE_PARAMS["filter2_freq"]
        )
        steps = 50
        step_duration = duration / steps

        for i in range(steps):
            progress = i / steps
            freq = start_freq + (end_freq - start_freq) * progress
            self.send_udp(
                "set_device_parameter",
                {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": freq_param,
                    "value": freq,
                },
            )
            time.sleep(step_duration)

    def set_wavetable_lfo(
        self, track_index: int, lfo_num: int, shape: int, amount: float, rate: float
    ):
        """Configure Wavetable LFO parameters."""
        device_index = self.get_wavetable_device(track_index)
        if device_index is None:
            return

        base = (
            WAVETABLE_PARAMS["lfo1_shape"]
            if lfo_num == 1
            else WAVETABLE_PARAMS["lfo2_shape"]
        )
        shape_param = base
        amount_param = base + 1
        rate_param = base + 5

        self.send_udp(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": shape_param,
                "value": float(shape),
            },
        )
        self.send_udp(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": amount_param,
                "value": amount,
            },
        )
        self.send_udp(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": rate_param,
                "value": rate,
            },
        )

    def dub_drop(
        self, tracks: List[int], drop_value: float = 0.05, return_duration: float = 10.0
    ):
        """Dub-style filter drop."""
        for track in tracks:
            device_index = self.get_wavetable_device(track)
            if device_index is not None:
                self.send_udp(
                    "set_device_parameter",
                    {
                        "track_index": track,
                        "device_index": device_index,
                        "parameter_index": WAVETABLE_PARAMS["filter1_freq"],
                        "value": drop_value,
                    },
                )

        time.sleep(return_duration)

        for track in tracks:
            device_index = self.get_wavetable_device(track)
            if device_index is not None:
                scene = next(
                    (s for s in SCENES if s["index"] == current_scene), SCENES[-1]
                )
                self.send_udp(
                    "set_device_parameter",
                    {
                        "track_index": track,
                        "device_index": device_index,
                        "parameter_index": WAVETABLE_PARAMS["filter1_freq"],
                        "value": scene["filter_freq"],
                    },
                )


def progress_bar(progress, width=40):
    """Generate visual progress bar."""
    filled = int(width * progress)
    empty = width - filled
    return f"[{'=' * filled}{'-' * empty}] {progress * 100:.1f}%"


def format_time(seconds):
    """Format seconds as HH:MM."""
    mins, secs = int(seconds // 60), int(seconds % 60)
    return f"{mins:02d}:{(secs // 10) * 10:02d}"  # Round to 10-second intervals


class WavetableAutomation(threading.Thread):
    """Thread for continuous Wavetable modulation."""

    def __init__(self, client, track_index):
        super().__init__()
        self.daemon = True
        self.client = client
        self.track_index = track_index
        self.running = True
        self.scene = 0

    def update_scene(self, scene_index):
        """Update current scene parameters."""
        self.scene = scene_index

    def run(self):
        """Continuous modulation loop."""
        while self.running:
            scene_params = SCENES[self.scene]
            start_time = time.time()
            elapsed = 0

            # Scene-specific LFO setup
            self.client.set_wavetable_lfo(
                self.track_index,
                1,  # LFO1
                shape=1,  # Triangle
                amount=0.5,
                rate=scene_params["lfo_rate"],
            )

            # Oscillator movement
            while elapsed < 60 and self.running:
                elapsed = time.time() - start_time
                progress = elapsed / 60.0

                # Wavetable position sweep
                osc_pos = 0.1 + 0.8 * abs(math.sin(elapsed * 0.05 + self.scene))
                self.client.set_wavetable_position(
                    self.track_index,
                    1,  # Osc1
                    osc_pos,
                )

                # Subtle filter movement
                filter_freq = scene_params["filter_freq"] + 0.1 * math.sin(
                    elapsed * 0.1
                )
                self.client.send_udp(
                    "set_device_parameter",
                    {
                        "track_index": self.track_index,
                        "device_index": 0,  # Wavetable device
                        "parameter_index": WAVETABLE_PARAMS["filter1_freq"],
                        "value": filter_freq,
                    },
                )

                time.sleep(0.05)  # ~20 updates/second

            # Between scenes
            time.sleep(1)

    def shutdown(self):
        """Stop modulation loop."""
        self.running = False


def main():
    print("=" * 80)
    print("ENHANCED 2-HOUR DUB TECHNO LIVE PERFORMANCE")
    print("=" * 80)
    print()
    print(f"Created by Sisyphus with Ableton MCP")
    print(f"Started at: {time.strftime('%H:%M:%S')}")
    print(
        f"Expected end: {time.strftime('%H:%M:%S', time.localtime(time.time() + 2 * 60 * 60))}"
    )
    print()
    print("Track Volumes:")
    print(f"  1. Drums: {VOLUMES[0]}")
    print(f"  2. Bass: {VOLUMES[1]} (DEEP CONSTANT)")
    print(f"  3. Hats: {VOLUMES[2]}")
    print(f"  4. Chord: {VOLUMES[3]}")
    print(f"  5. Pad: {VOLUMES[4]}")
    print(f"  6. Percussion: {VOLUMES[5]}")
    print(f"  7. 64 Pads: {VOLUMES[6]}")
    print()

    with MCPClient() as client:
        # Initial setup
        print("🔁 Initializing session...")
        session_info = client.send_tcp("get_session_info", {})
        print(
            f"  Session: {session_info.get('result', {}).get('track_count', '?')} tracks, {session_info.get('result', {}).get('tempo', '?')} BPM"
        )

        # Ensure bass is UNMUTED and CONSTANT
        client.send_udp("set_track_volume", {"track_index": 1, "volume": 0.9})
        client.send_udp("set_track_mute", {"track_index": 1, "mute": False})
        print("  Bass volume locked at 0.9")

        # Start Wavetable automation thread
        wt_track_index = 3  # Chord track
        wavetable_automation = WavetableAutomation(client, wt_track_index)
        wavetable_automation.start()
        print(f"  Wavetable modulation started on track {wt_track_index}")

        # Fire first scene
        print("🎹 Firing scene 1...")
        for track in range(7):
            client.send_tcp("fire_clip", {"track_index": track, "clip_index": 0})
        client.send_tcp("start_playback", {})

        start_time = time.time()
        current_scene = 0

        try:
            for scene in SCENES:
                scene_index = scene["index"]
                print(
                    f"\\n🎶 SCENE {scene_index + 1}/8: {scene['name']} ({scene['key']})"
                )
                print(
                    f"  Energy: {scene['energy'] * 100:.0f}% | Density: {scene['density'] * 100:.0f}%"
                )
                print(f"  Filter: {scene['filter_freq']:.2f}")

                # Update automation thread
                wavetable_automation.update_scene(scene_index)

                # Fire scene (except first already fired)
                if scene_index > 0:
                    for track in range(7):
                        client.send_tcp(
                            "fire_clip",
                            {"track_index": track, "clip_index": scene_index},
                        )

                scene_start_time = time.time()
                elapsed_seconds = 0

                # Scene-specific processing
                while elapsed_seconds < 900:  # 15 minutes per scene
                    elapsed_seconds = time.time() - scene_start_time
                    total_seconds = time.time() - start_time
                    progress = elapsed_seconds / 900.0

                    # Progress bar
                    if int(elapsed_seconds) % 10 == 0:
                        elapsed_min = int(elapsed_seconds / 60)
                        total_min = int((elapsed_seconds + scene_index * 900) / 60)
                        print(
                            f"\\r🕐 {progress_bar(progress)} {format_time(elapsed_seconds)} / 15:00 | Scene: {scene['name']} | {total_min} min",
                            end="",
                        )

                    # === REAL-TIME MODULATION ===

                    # 1. Volume automation (non-bass tracks only)
                    if int(elapsed_seconds) % 5 == 0:
                        for track, volume in VOLUMES.items():
                            if track == 1:  # Skip bass - CONSTANT 0.9
                                client.send_udp(
                                    "set_track_volume",
                                    {"track_index": 1, "volume": 0.9},
                                )
                                continue

                            # Add subtle variation
                            variation = 0.05 * math.sin(total_seconds * 0.1 + track)
                            modulated_vol = max(0.0, min(1.0, volume + variation))
                            client.send_udp(
                                "set_track_volume",
                                {"track_index": track, "volume": modulated_vol},
                            )

                    # 2. Panning movement on hats
                    if int(elapsed_seconds) % 3 == 0:
                        pan = 0.2 * math.sin(total_seconds * 0.07)
                        client.send_udp(
                            "set_track_pan",
                            {
                                "track_index": 2,  # Hats
                                "pan": pan,
                            },
                        )

                    # 3. Scene transitions
                    if int(elapsed_seconds) % 20 == 0 and elapsed_seconds > 10:
                        next_scene = scene_index + 1
                        if (
                            next_scene < len(SCENES) and elapsed_seconds > 880
                        ):  # Start transition after 14:40
                            for track in [0, 2, 3, 4, 5, 6]:  # Skip bass
                                client.send_tcp(
                                    "fire_clip",
                                    {"track_index": track, "clip_index": next_scene},
                                )

                    # 4. Periodic dub effects
                    if (
                        scene_index >= 2 and int(elapsed_seconds) % 120 < 1
                    ):  # Every 2 minutes
                        drop_tracks = [3, 4] if scene["energy"] > 0.6 else [3]
                        client.dub_drop(
                            drop_tracks, drop_value=0.05, return_duration=8.0
                        )

                    # 5. 64 Pads Dub Kit variation
                    if int(elapsed_seconds) % 7 == 0:
                        pad_vol = VOLUMES[6] + 0.08 * math.sin(total_seconds * 0.05)
                        client.send_udp(
                            "set_track_volume",
                            {"track_index": 6, "volume": max(0.3, min(0.8, pad_vol))},
                        )

                    time.sleep(0.98)  # Slightly under 1 second for synced updates

                # Scene transition timing
                print(
                    f"\\n🎼 Scene {scene_index + 1} completed: {elapsed_seconds // 60:.0f} minutes"
                )
                current_scene += 1

        except KeyboardInterrupt:
            print("\\n🚨 Live performance interrupted!")

        except Exception as e:
            print(f"\\n🚨 Error: {str(e)}")
            import traceback

            traceback.print_exc()

        finally:
            # Graceful shutdown
            print("\\n🔄 Shutting down automation threads...")
            wavetable_automation.shutdown()

            print("🎚️  Fade out...")
            for i in range(30):
                vol = 0.75 - (i * 0.025)
                client.send_udp("set_master_volume", {"volume": max(0, vol)})
                time.sleep(1)

            client.send_tcp("stop_playback", {})

            total_time_minutes = (time.time() - start_time) / 60
            print("\\n" + "=" * 80)
            print("2-HOUR PERFORMANCE COMPLETE!")
            print(f"Duration: {total_time_minutes:.1f} minutes")
            print(f"Ended at: {time.strftime('%H:%M:%S')}")
            print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n🚨 Live performance aborted.")
        sys.exit(0)
