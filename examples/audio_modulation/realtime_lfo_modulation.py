#!/usr/bin/env python3
"""
Real-Time LFO Modulation Example
----------------------------------

Dynamic LFO-driven parameter modulation: filter sweeps, vibrato, pulse-width.

Usage:
  python realtime_lfo_modulation.py
"""

import socket
import json
import time
import random

# Configuration
TCP_PORT = 9877
UDP_PORT = 9878
HOST = "localhost"
TARGET_TRACK = 2  # Synth or pad track
FILTER_DEVICE = 3  # Auto Filter on target track
PARAM_CUTOFF = 3  # Cutoff frequency parameter
SWEEP_RATE = 0.3  # 0.3 cycles per beat = 5 seconds for full sweep at 126 BPM


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


def main():
    print("🎛️ Real-Time LFO Modulation Example")
    print("📶 Instant filter cutoff moving with LFO")
    print("🎚️  Target: Track 2, Auto Filter cutoff\n")

    # Create LFO modulator
    print("🔮 Creating LFO modulator...")
    lfo_result = tcp_command(
        "create_lfo_modulator",
        {
            "track_index": TARGET_TRACK,
            "device_index": FILTER_DEVICE,
            "parameter_index": PARAM_CUTOFF,  # Cutoff frequency
            "rate": SWEEP_RATE,  # 0.3 cycles/beat
            "depth": 0.75,  # 75% modulation depth
            "waveform": "sine",  # Smooth sine wave
        },
    )

    if "modulator_id" not in lfo_result:
        error = lfo_result.get("error", "Unknown")
        print(f"❌ LFO creation failed: {error}")
        return False

    mod_id = lfo_result["modulator_id"]
    print(f"✅ LFO created (ID: {mod_id})")
    print(f"📊 Settings:")
    print(f"   • Rate: {SWEEP_RATE} cycles/beat")
    print(f"   • Depth: 75%")
    print(f"   • Waveform: Sine")
    print("\n🔊 The filter cutoff should now be modulating rhythmically!")
    print("LFO → Filter Cutoff (hear the wobble)")

    DURATION = 20  # Seconds for demo
    print(f"\n🔊 Demo running for {DURATION} seconds...")
    print("🎛️ Modulate parameters in real-time:")

    for i in range(DURATION):
        if i % 3 == 0:
            new_rate = random.uniform(0.2, 1.5)  # Random speed
            new_depth = random.uniform(0.5, 0.9)  # Random depth
            new_wave = random.choice(["sine", "triangle", "saw", "square"])

            tcp_command(
                "set_modulator_parameter",
                {"modulator_id": mod_id, "parameter": "rate", "value": new_rate},
            )
            tcp_command(
                "set_modulator_parameter",
                {"modulator_id": mod_id, "parameter": "depth", "value": new_depth},
            )
            tcp_command(
                "set_modulator_parameter",
                {"modulator_id": mod_id, "parameter": "waveform", "value": new_wave},
            )

            print(
                f"🔄 LFO Update: Speed={new_rate:.1f} | Depth={new_depth * 100:.0f}% | Wave={new_wave}",
                end="\r",
            )

        time.sleep(0.5)

    # Cleanup
    print("\n🧹 Cleaning up LFO...")
    tcp_command("remove_modulator", {"modulator_id": mod_id})
    print("✅ LFO removed - filter now static")


if __name__ == "__main__":
    main()
