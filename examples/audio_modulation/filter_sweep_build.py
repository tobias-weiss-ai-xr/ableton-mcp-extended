#!/usr/bin/env python3
"""
Filter Sweep Buildup Example
--------------------------------

Creates the classic DJ buildup effect: slowly opening filter cutoff
to reveal more frequency content over 8-16 bars.

Usage:
  python filter_sweep_build.py
"""

import socket
import json
import time

# Configuration
TCP_PORT = 9877
UDP_PORT = 9878
HOST = "localhost"
TARGET_TRACK = 2  # Synth/Pad track
DEVICE_INDEX = 3  # Auto Filter/EQ device
PARAM_CUTOFF = 3  # Cutoff parameter (typical)
SWEEP_BARS = 16  # Duration in bars
STEPS = 128  # Smoothness (higher = smoother)


def tcp_command(cmd_type: str, params: dict) -> dict:
    """Send command via TCP and return response."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((HOST, TCP_PORT))

        cmd = {"type": cmd_type, "params": params}
        sock.send(json.dumps(cmd).encode("utf-8"))
        response = sock.recv(8192).decode("utf-8")
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}
    finally:
        if sock:
            sock.close()


def udp_command(cmd_type: str, params: dict):
    """Send real-time parameter update via UDP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cmd = {"type": cmd_type, "params": params}
        sock.sendto(json.dumps(cmd).encode("utf-8"), (HOST, UDP_PORT))
    except Exception as e:
        print(f"UDP send failed: {str(e)}")


def main():
    print("🎛️ Filter Sweep Buildup Example")
    print("⭐ Target Track 2 (Auto Filter cutoff)")

    # Verify environment
    result = tcp_command("get_track_info", {"track_index": TARGET_TRACK})
    if "error" in result:
        print(f"❌ Track {TARGET_TRACK} not available. Create audio/midi track first.")
        return

    print(f"📊 Starting buildup ({SWEEP_BARS} bars, {STEPS} steps)...")
    print("🔊 Listen as the filter opens from rumble to full brightness\n")

    # Linear sweep: closed → fully open filter cutoff
    for i in range(STEPS):
        # Normalized values: 0.1 = 200Hz, 0.7 = 2000Hz, 0.99 = full open
        cutoff_value = 0.1 + (i / STEPS) * 0.85  # 0.1 → 0.95"]

        # Optional: increase resonance as cutoff opens
        resonance_value = 0.3 + (i / STEPS) * 0.5  # 0.3 → 0.8

        # Send UDP commands (fire-and-forget = ultra low latency)
        udp_command(
            "set_audio_effect_parameter",
            {
                "track_index": TARGET_TRACK,
                "device_index": DEVICE_INDEX,
                "parameter_index": PARAM_CUTOFF,  # Cutoff
                "value": cutoff_value,
            },
        )

        # Only update resonance every 4th step (less CPU load)
        if i % 4 == 0:
            udp_command(
                "set_audio_effect_parameter",
                {
                    "track_index": TARGET_TRACK,
                    "device_index": DEVICE_INDEX,
                    "parameter_index": 4,  # Resonance (typical)
                    "value": resonance_value,
                },
            )

        # Bar timing at 126 BPM (~1.25 seconds / 4-beat bar)
        time.sleep((SWEEP_BARS * 2.0) / STEPS / 126.0)  # seconds

        # Progress visualizer
        print(
            f"🎚️ Progress: [{'=' * (i // 8)}{' ' * (16 - i // 8)}] {i * 100 / STEPS:.1f}%",
            end="\r",
        )

    # Final state
    udp_command(
        "set_audio_effect_parameter",
        {
            "track_index": TARGET_TRACK,
            "device_index": DEVICE_INDEX,
            "parameter_index": PARAM_CUTOFF,
            "value": 0.98,  # Fully open
        },
    )

    print("\n✅ Filter sweep animation complete (filter 100% open)")
    print("👂 Notice the energy build from sub-bass to full texture")


if __name__ == "__main__":
    main()
