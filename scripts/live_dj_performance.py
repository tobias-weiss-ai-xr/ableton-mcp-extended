#!/usr/bin/env python3
"""Live DJ Performance with Real-Time Audio Analysis"""

import socket
import json
import time
import random
import sys

# Add parent directory to path for imports
sys.path.insert(0, ".")
from MCP_Server.audio_analysis import AudioAnalyzer, AudioAnalyzerConfig


# MCP Communication
def send_tcp(command_type, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 9877))
    msg = json.dumps({"type": command_type, "params": params or {}})
    sock.sendall((msg + "\n").encode())
    response = sock.recv(65536).decode()
    sock.close()
    return json.loads(response)


def send_udp(command_type, params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = json.dumps({"type": command_type, "params": params})
    sock.sendto(msg.encode(), ("127.0.0.1", 9878))
    sock.close()


# Parameter setters
def set_drums_filter(val):
    send_udp(
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 2, "value": int(val)},
    )


def set_drums_reverb(val):
    send_udp(
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 8, "value": int(val)},
    )


def set_drums_delay(val):
    send_udp(
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 6, "value": int(val)},
    )


def set_drums_overdrive(val):
    send_udp(
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 3, "value": int(val)},
    )


def set_bass_filter(val):
    send_udp(
        "set_device_parameter",
        {"track_index": 1, "device_index": 0, "parameter_index": 170, "value": val},
    )


def set_bass_res(val):
    send_udp(
        "set_device_parameter",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 171,
            "value": min(val, 1.0),
        },
    )


# Performance patterns
def pattern_filter_buildup(analyzer, duration=12):
    print(f"[BUILD-UP] {duration}s filter sweep...")
    steps = 8
    for i in range(steps):
        t = i / (steps - 1)
        curve = t * t  # Exponential feel
        drums_f = 50 + 77 * curve
        bass_f = 0.3 + 0.7 * curve
        reverb = 20 + 50 * curve

        set_drums_filter(drums_f)
        set_bass_filter(bass_f)
        set_drums_reverb(reverb)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  [{i + 1}/{steps}] RMS: {rms:.3f}")
        time.sleep(duration / steps)
    return 0.8  # High energy after build


def pattern_dub_drop(analyzer, instant=True):
    print(f"[DROP] {'Instant' if instant else 'Gradual'} dub drop!")

    if instant:
        set_drums_filter(40)
        set_bass_filter(0.2)
        set_drums_reverb(80)
        set_drums_delay(70)
        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  DROP! RMS: {rms:.3f}")
        time.sleep(4)
    else:
        for i in range(6):
            t = i / 5
            set_drums_filter(100 - 60 * t)
            set_bass_filter(0.8 - 0.6 * t)
            rms = analyzer.get_analysis().get("rms", 0)
            print(f"  [{i + 1}/6] RMS: {rms:.3f}")
            time.sleep(1)

    # Slow return
    print("  [RETURN] Bringing back...")
    for i in range(5):
        t = i / 4
        set_drums_filter(40 + 60 * t)
        set_bass_filter(0.2 + 0.6 * t)
        set_drums_reverb(80 - 40 * t)
        time.sleep(2)
    return 0.6


def pattern_hypnotic(analyzer, duration=16):
    print(f"[HYPNOTIC] {duration}s sustained groove...")
    steps = int(duration / 4)
    for i in range(steps):
        drums_f = 70 + random.uniform(-10, 10)
        bass_f = 0.6 + random.uniform(-0.1, 0.1)
        reverb = 40 + random.uniform(-10, 10)

        set_drums_filter(drums_f)
        set_bass_filter(bass_f)
        set_drums_reverb(reverb)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  [{i + 1}/{steps}] RMS: {rms:.3f}")
        time.sleep(4)
    return 0.5


def pattern_rapid_evolve(analyzer, duration=12):
    print(f"[EVOLVE] {duration}s rapid automation...")
    steps = int(duration / 2)
    for i in range(steps):
        drums_f = random.randint(60, 120)
        bass_f = random.uniform(0.4, 0.9)
        reverb = random.randint(25, 65)
        delay = random.randint(0, 50)
        overdrive = random.randint(5, 25)

        set_drums_filter(drums_f)
        set_bass_filter(bass_f)
        set_drums_reverb(reverb)
        set_drums_delay(delay)
        set_drums_overdrive(overdrive)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  [{i + 1}/{steps}] RMS: {rms:.3f} | D.Flt={drums_f} D.Rvb={reverb}")
        time.sleep(2)
    return 0.5 + (drums_f - 90) / 100


def pattern_effect_stab(analyzer):
    print("[STAB] Quick effect stab!")
    set_drums_reverb(100)
    set_drums_delay(80)
    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  Stab! RMS: {rms:.3f}")
    time.sleep(0.5)
    set_drums_reverb(40)
    set_drums_delay(20)
    time.sleep(1)
    return 0.5


def fire_drum_pattern(idx):
    print(f"[CLIP] Switching drums to pattern {idx}")
    send_udp("fire_clip", {"track_index": 0, "clip_index": idx})


def main():
    # Start audio analyzer
    config = AudioAnalyzerConfig(
        sample_rate=44100,
        buffer_size=4096,
        analysis_features={
            "key": False,
            "bpm": False,
            "spectral": False,
            "loudness": False,
        },
    )
    analyzer = AudioAnalyzer(config)
    analyzer._device_index = 109  # Voicemeeter Out 6
    analyzer.start()
    time.sleep(0.5)

    print("=" * 60)
    print("  LIVE DJ PERFORMANCE WITH REAL-TIME AUDIO ANALYSIS")
    print("  Dub Techno / Deep House Style")
    print("=" * 60)
    print()

    cycle = 0
    energy = 0.5

    patterns = [
        ("buildup", pattern_filter_buildup, {"duration": 10}),
        ("hypnotic", pattern_hypnotic, {"duration": 12}),
        ("evolve", pattern_rapid_evolve, {"duration": 10}),
        ("drop", pattern_dub_drop, {"instant": True}),
    ]

    try:
        print("Starting continuous DJ performance...")
        print("Press Ctrl+C to stop\n")

        while True:
            cycle += 1
            print(f"\n{'=' * 50}")
            print(f"  CYCLE {cycle} | Energy: {energy:.0%}")
            print(f"{'=' * 50}")

            rms = analyzer.get_analysis().get("rms", 0)
            print(f"Current RMS: {rms:.3f}\n")

            # Select pattern based on energy
            if energy < 0.4:
                energy = pattern_filter_buildup(analyzer, duration=12)
            elif energy > 0.7:
                energy = pattern_dub_drop(analyzer, instant=random.random() > 0.5)
            else:
                name, func, kwargs = random.choice(patterns)
                energy = func(analyzer, **kwargs)

            # Occasional clip switch
            if random.random() > 0.7:
                fire_drum_pattern(random.randint(0, 5))

            # Occasional effect stab
            if random.random() > 0.8:
                energy = pattern_effect_stab(analyzer)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[STOP] Performance ended by user")
        print(f"Final stats: {cycle} cycles completed")
    finally:
        analyzer.stop()
        print("Audio analyzer stopped. Goodbye!")


if __name__ == "__main__":
    main()
