#!/usr/bin/env python3
"""
Unified Dub Mix Orchestrator for MCP Server
============================================

This script integrates the dub mixing logic from the `rework/` folder
with the MCP server's TCP/UDP protocol architecture.

Protocol:
- TCP (port 9877): Reliable commands with response
- UDP (port 9878): High-frequency parameter updates

Features:
- Scene sequencing
- Filter sweeps and automation
- Continuous dub mode
- Real-time parameter control

Original rework files:
- rework/dub_mix_orchestrator.py (HTTP protocol - replaced with MCP TCP)
- rework/dub_controller.py (OSC protocol - replaced with MCP UDP)
- rework/dub_mix_osc.py (pythonosc - replaced with MCP)
- rework/dub_mix_udp.py (OSC-style UDP - replaced with MCP UDP)
"""

import socket
import json
import time
# import random  # unused
# import threading  # unused
from typing import Optional, Dict, List, Any

# MCP Server Configuration
TCP_HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_HOST = "127.0.0.1"
UDP_PORT = 9878


class MCPClient:
    """MCP protocol client for Ableton Live communication."""

    def __init__(
        self,
        tcp_host: str = TCP_HOST,
        tcp_port: int = TCP_PORT,
        udp_host: str = UDP_HOST,
        udp_port: int = UDP_PORT,
    ):
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.udp_host = udp_host
        self.udp_port = udp_port

        # Create sockets
        self.tcp_sock: Optional[socket.socket] = None
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def tcp_connect(self) -> bool:
        """Establish TCP connection."""
        try:
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_sock.connect((self.tcp_host, self.tcp_port))
            self.tcp_sock.settimeout(10.0)
            return True
        except Exception as e:
            print(f"TCP connection failed: {e}")
            return False

    def tcp_close(self):
        """Close TCP connection."""
        if self.tcp_sock:
            self.tcp_sock.close()
            self.tcp_sock = None

    def send_tcp(self, command: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Send TCP command and wait for response.

        Args:
            command: MCP command name
            params: Command parameters

        Returns:
            Response dict or None on failure
        """
        if params is None:
            params = {}

        msg = {"type": command, "params": params}

        try:
            if not self.tcp_sock:
                self.tcp_connect()

            self.tcp_sock.send(json.dumps(msg).encode("utf-8"))
            response = self.tcp_sock.recv(8192).decode("utf-8")
            return json.loads(response)
        except Exception as e:
            print(f"TCP command failed ({command}): {e}")
            self.tcp_close()
            return None

    def send_udp(self, command: str, params: Dict[str, Any] = None) -> bool:
        """
        Send UDP command (fire-and-forget).

        Args:
            command: MCP command name (must be UDP-eligible)
            params: Command parameters

        Returns:
            True if sent successfully
        """
        if params is None:
            params = {}

        msg = {"type": command, "params": params}

        try:
            self.udp_sock.sendto(
                json.dumps(msg).encode("utf-8"), (self.udp_host, self.udp_port)
            )
            return True
        except Exception as e:
            print(f"UDP command failed ({command}): {e}")
            return False


class DubOrchestrator:
    """
    Unified Dub Mix Controller using MCP protocol.

    Integrates logic from rework/ folder with MCP TCP/UDP architecture.
    """

    def __init__(self, mcp_client: MCPClient = None):
        self.mcp = mcp_client or MCPClient()
        self.running = False
        self.current_scene = 0

        # Track mappings (customize for your session)
        self.tracks = {
            "drums": 0,
            "bass": 1,
            "guitar": 2,
            "organ": 3,
            "pad": 4,
            "fx": 5,
        }

        # Device mappings (customize for your session)
        self.devices = {
            "drums_filter": {"track": 0, "device": 0, "cutoff_param": 2},
            "bass_filter": {"track": 1, "device": 0, "cutoff_param": 170},
            "pad_filter": {"track": 4, "device": 0, "cutoff_param": 0},
        }

    def check_connection(self) -> bool:
        """Verify MCP connection to Ableton."""
        result = self.mcp.send_tcp("get_session_overview")
        if result and "result" in result:
            data = result.get("result", {})
            if "tracks" in data or isinstance(data, dict):
                print("✓ MCP connection established")
                return True
        print("✗ MCP connection failed")
        return False

    def get_session_info(self) -> Optional[Dict]:
        """Get current session information."""
        result = self.mcp.send_tcp("get_session_overview")
        if result and "result" in result:
            return result["result"]
        return None

    # ========== Transport Control ==========

    def start_playback(self):
        """Start Ableton playback."""
        self.mcp.send_tcp("start_playback")
        print("▶ Playback started")

    def stop_playback(self):
        """Stop Ableton playback."""
        self.mcp.send_tcp("stop_playback")
        print("⏹ Playback stopped")

    def set_tempo(self, bpm: float):
        """Set session tempo."""
        self.mcp.send_tcp("set_tempo", {"tempo": bpm})
        print(f"♩ Tempo set to {bpm} BPM")

    # ========== Scene Control ==========

    def trigger_scene(self, scene_index: int):
        """Trigger a scene by index."""
        self.mcp.send_tcp("trigger_scene", {"scene_index": scene_index})
        self.current_scene = scene_index
        print(f"🎬 Scene {scene_index} triggered")

    def trigger_scene_sequence(self, scenes: List[int], delay_beats: float = 4.0):
        """
        Trigger scenes in sequence.

        Args:
            scenes: List of scene indices
            delay_beats: Delay between scenes in beats
        """
        for scene_idx in scenes:
            self.trigger_scene(scene_idx)
            time.sleep(delay_beats * (60.0 / self._get_tempo()))

    def _get_tempo(self) -> float:
        """Get current tempo from session."""
        info = self.get_session_info()
        if info:
            return info.get("tempo", 120.0)
        return 120.0

    # ========== Clip Control ==========

    def fire_clip(self, track_index: int, clip_index: int, use_udp: bool = True):
        """Fire a clip."""
        if use_udp:
            self.mcp.send_udp(
                "fire_clip", {"track_index": track_index, "clip_index": clip_index}
            )
        else:
            self.mcp.send_tcp(
                "fire_clip", {"track_index": track_index, "clip_index": clip_index}
            )
        print(f"🎵 Clip fired: Track {track_index}, Clip {clip_index}")

    def stop_clip(self, track_index: int, clip_index: int):
        """Stop a clip."""
        self.mcp.send_tcp(
            "stop_clip", {"track_index": track_index, "clip_index": clip_index}
        )

    # ========== Volume Control ==========

    def set_track_volume(self, track_index: int, volume: float, use_udp: bool = True):
        """
        Set track volume (normalized 0.0-1.0).

        Args:
            track_index: Track index
            volume: Normalized volume (0.0 = silent, 1.0 = full)
            use_udp: Use UDP for low-latency update
        """
        if use_udp:
            self.mcp.send_udp(
                "set_track_volume", {"track_index": track_index, "volume": volume}
            )
        else:
            self.mcp.send_tcp(
                "set_track_volume", {"track_index": track_index, "volume": volume}
            )

    def set_master_volume(self, volume: float, use_udp: bool = True):
        """Set master volume."""
        if use_udp:
            self.mcp.send_udp("set_master_volume", {"volume": volume})
        else:
            self.mcp.send_tcp("set_master_volume", {"volume": volume})

    # ========== Mute/Solo Control ==========

    def mute_track(self, track_index: int, mute: bool = True, use_udp: bool = True):
        """Mute or unmute a track."""
        if use_udp:
            self.mcp.send_udp(
                "set_track_mute", {"track_index": track_index, "mute": mute}
            )
        else:
            self.mcp.send_tcp(
                "set_track_mute", {"track_index": track_index, "mute": mute}
            )

    def solo_track(self, track_index: int, solo: bool = True, use_udp: bool = True):
        """Solo or unsolo a track."""
        if use_udp:
            self.mcp.send_udp(
                "set_track_solo", {"track_index": track_index, "solo": solo}
            )
        else:
            self.mcp.send_tcp(
                "set_track_solo", {"track_index": track_index, "solo": solo}
            )

    # ========== Parameter Control ==========

    def set_device_parameter(
        self,
        track_index: int,
        device_index: int,
        parameter_index: int,
        value: float,
        use_udp: bool = True,
    ):
        """
        Set device parameter (normalized 0.0-1.0).

        Args:
            track_index: Track index
            device_index: Device index on track
            parameter_index: Parameter index
            value: Normalized value (0.0-1.0)
            use_udp: Use UDP for low-latency update
        """
        if use_udp:
            self.mcp.send_udp(
                "set_device_parameter",
                {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": parameter_index,
                    "value": value,
                },
            )
        else:
            self.mcp.send_tcp(
                "set_device_parameter",
                {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": parameter_index,
                    "value": value,
                },
            )

    # ========== Filter Automation (from rework/dub_mix_orchestrator.py) ==========

    def filter_sweep(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
        start_value: float,
        end_value: float,
        duration_beats: float = 16.0,
        steps: int = 16,
    ):
        """
        Perform a filter sweep on a track.

        Args:
            track_index: Track index
            device_index: Device index
            param_index: Filter cutoff parameter index
            start_value: Starting normalized value (0.0-1.0)
            end_value: Ending normalized value (0.0-1.0)
            duration_beats: Duration in beats
            steps: Number of steps for smooth transition
        """
        tempo = self._get_tempo()
        step_duration = (duration_beats * 60.0 / tempo) / steps

        for i in range(steps + 1):
            progress = i / steps
            value = start_value + (end_value - start_value) * progress
            self.set_device_parameter(track_index, device_index, param_index, value)
            time.sleep(step_duration)

        print(f"🌊 Filter sweep complete: {start_value:.2f} → {end_value:.2f}")

    def filter_buildup(
        self,
        track_indices: List[int],
        device_index: int,
        param_index: int,
        start_value: float = 0.3,
        end_value: float = 0.9,
        duration_beats: float = 16.0,
        steps: int = 16,
    ):
        """
        Apply filter buildup across multiple tracks.

        Uses MCP's apply_filter_buildup for optimized performance.
        """
        self.mcp.send_tcp(
            "apply_filter_buildup",
            {
                "track_indices": track_indices,
                "device_index": device_index,
                "parameter_index": param_index,
                "start_value": start_value,
                "end_value": end_value,
                "duration_beats": duration_beats,
                "steps": steps,
            },
        )
        print(f"📈 Filter buildup started on {len(track_indices)} tracks")

    def apply_drop(
        self,
        track_indices: List[int],
        device_index: int,
        param_index: int,
        drop_value: float = 0.2,
        return_value: float = 0.8,
        drop_instant: bool = True,
    ):
        """
        Apply a drop effect to specified tracks.

        Uses MCP's apply_drop for optimized performance.
        """
        self.mcp.send_tcp(
            "apply_drop",
            {
                "track_indices": track_indices,
                "device_index": device_index,
                "parameter_index": param_index,
                "drop_value": drop_value,
                "return_value": return_value,
                "drop_instant": drop_instant,
            },
        )
        print(f"📉 Drop applied to {len(track_indices)} tracks")

    # ========== Energy Curve (from rework/) ==========

    def apply_energy_curve(
        self,
        parameter_changes: List[Dict],
        duration_beats: float = 32.0,
        steps: int = 32,
    ):
        """
        Gradually change multiple parameters over time.

        Args:
            parameter_changes: List of dicts with track_index, device_index,
                              parameter_index, start_value, end_value
            duration_beats: Total duration in beats
            steps: Number of steps for smooth transition
        """
        self.mcp.send_tcp(
            "apply_energy_curve",
            {
                "parameter_changes": parameter_changes,
                "duration_beats": duration_beats,
                "steps": steps,
            },
        )
        print(f"⚡ Energy curve applied: {len(parameter_changes)} parameters")

    # ========== Continuous Dub Mode (from rework/dub_mix_orchestrator.py) ==========

    def continuous_dub_mode(
        self, iterations: int = None, scene_delay_beats: float = 16.0
    ):
        """
        Run continuous dub mixing loop.

        Args:
            iterations: Number of iterations (None = infinite)
            scene_delay_beats: Delay between scene changes in beats
        """
        print("\n🎛️ STARTING CONTINUOUS DUB MIX MODE 🎛️")
        print("=" * 60)

        self.running = True
        loop_count = 0

        # Scene sequence pattern
        scenes = [0, 1, 2, 3, 4, 5, 6, 7]

        try:
            while self.running:
                loop_count += 1
                if iterations and loop_count > iterations:
                    break

                print(f"\n[🔄 Dub Loop {loop_count} - {time.strftime('%H:%M:%S')}]")

                # Check connection
                if not self.check_connection():
                    print("⚠ Re-establishing connection...")
                    time.sleep(5)
                    continue

                # Phase 1: Scene transitions
                print("  → Triggering scene sequence...")
                tempo = self._get_tempo()
                scene_delay_sec = scene_delay_beats * 60.0 / tempo

                for scene_idx in scenes:
                    if not self.running:
                        break
                    self.trigger_scene(scene_idx)
                    time.sleep(scene_delay_sec)

                # Phase 2: Filter sweeps
                print("  → Applying filter sweeps...")
                self._run_filter_sweeps()

                # Phase 3: Volume dynamics
                print("  → Applying volume dynamics...")
                self._run_volume_dynamics()

                # Brief pause before next iteration
                time.sleep(2)

        except KeyboardInterrupt:
            print("\n\n🛑 Dub mix stopped by user")
        finally:
            self.running = False

    def _run_filter_sweeps(self):
        """Run filter sweep patterns."""
        # Sweep pads from dark to bright
        if "pad_filter" in self.devices:
            d = self.devices["pad_filter"]
            self.filter_sweep(
                d["track"],
                d["device"],
                d["cutoff_param"],
                start_value=0.3,
                end_value=0.8,
                duration_beats=16.0,
                steps=16,
            )
            time.sleep(1)
            # Return sweep
            self.filter_sweep(
                d["track"],
                d["device"],
                d["cutoff_param"],
                start_value=0.8,
                end_value=0.3,
                duration_beats=8.0,
                steps=8,
            )

    def _run_volume_dynamics(self):
        """Run volume automation patterns."""
        # Bass emphasis
        self.set_track_volume(self.tracks["bass"], 0.9)
        self.set_track_volume(self.tracks["drums"], 0.7)
        time.sleep(4)

        # Bring back drums
        self.set_track_volume(self.tracks["drums"], 0.85)
        time.sleep(4)

    def stop(self):
        """Stop continuous dub mode."""
        self.running = False


# ========== Convenience Functions ==========


def build_dub_session(mcp: MCPClient):
    """Initialize a dub mix session structure."""
    print("\n[1/5] Setting dub tempo")
    mcp.send_tcp("set_tempo", {"tempo": 75.0})

    print("[2/5] Creating tracks")
    # Create MIDI tracks
    for i in range(6):
        mcp.send_tcp("create_midi_track", {"index": -1})

    print("[3/5] Naming tracks")
    track_names = ["Drums", "Bass", "Guitar_Skank", "Organ", "Pad", "FX"]
    for i, name in enumerate(track_names):
        mcp.send_tcp("set_track_name", {"track_index": i, "name": name})

    print("[4/5] Loading instruments")
    # Load drum kit on track 0
    mcp.send_tcp(
        "load_instrument_or_effect",
        {"track_index": 0, "uri": "query:Drums#Drum%20Rack"},
    )

    print("[5/5] Creating initial clips")
    # Create drum pattern
    mcp.send_tcp(
        "create_drum_pattern",
        {"track_index": 0, "clip_index": 0, "pattern_name": "one_drop", "length": 4.0},
    )

    print("\n✅ Dub session structure ready!")


def quick_dub_loop(iterations: int = 5):
    """Quick start: Run a short dub loop."""
    orchestrator = DubOrchestrator()

    if not orchestrator.check_connection():
        print("Failed to connect to MCP server")
        return

    orchestrator.start_playback()
    orchestrator.continuous_dub_mode(iterations=iterations)
    orchestrator.stop_playback()


# ========== Main Entry Point ==========

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Unified Dub Mix Orchestrator for MCP")
    parser.add_argument("--build", action="store_true", help="Build new dub session")
    parser.add_argument(
        "--loop", type=int, default=None, help="Run N iterations (default: infinite)"
    )
    parser.add_argument("--tempo", type=float, default=75.0, help="Set tempo")
    parser.add_argument("--test", action="store_true", help="Test connection only")

    args = parser.parse_args()

    print("=" * 60)
    print("DUB MIX ORCHESTRATOR - MCP VERSION")
    print("TCP: 9877 | UDP: 9878")
    print("=" * 60)

    mcp = MCPClient()

    if args.test:
        if mcp.tcp_connect():
            print("✓ MCP connection test successful")
            mcp.tcp_close()
        else:
            print("✗ MCP connection test failed")
        exit(0)

    if args.build:
        build_dub_session(mcp)
        exit(0)

    # Run continuous dub mode
    orchestrator = DubOrchestrator(mcp)

    if not orchestrator.check_connection():
        print("Failed to connect to MCP server. Is Ableton running with MCP script?")
        exit(1)

    orchestrator.set_tempo(args.tempo)
    orchestrator.start_playback()

    try:
        orchestrator.continuous_dub_mode(iterations=args.loop)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
    finally:
        orchestrator.stop_playback()
        mcp.tcp_close()

    print("\n✅ Dub mix completed")
