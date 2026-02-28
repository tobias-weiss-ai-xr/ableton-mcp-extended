#!/usr/bin/env python3
"""Scene-Based DJ Performance with Real-Time Audio Analysis"""

import socket
import json
import time
import random
import sys

sys.path.insert(0, ".")
from MCP_Server.audio_analysis import AudioAnalyzer, AudioAnalyzerConfig


def send_tcp(cmd, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 9877))
    sock.sendall((json.dumps({"type": cmd, "params": params or {}}) + "\n").encode())
    resp = json.loads(sock.recv(65536).decode())
    sock.close()
    return resp


def send_udp(cmd, params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(
        json.dumps({"type": cmd, "params": params}).encode(), ("127.0.0.1", 9878)
    )
    sock.close()


# Scene definitions
SCENES = {
    "INTRO_Minimal": 0,
    "GROOVE_Dub": 1,
    "HEAVY_Bass": 2,
    "FULL_Band": 3,
    "DROP_Dub": 4,
    "REGGAE_Feel": 5,
    "STEPPERS_Heavy": 6,
    "BREAKDOWN": 7,
    "BUILD_Up": 8,
    "CLIMAX": 9,
}


# Parameter setters
def set_param(track, device, param, value):
    send_udp(
        "set_device_parameter",
        {
            "track_index": track,
            "device_index": device,
            "parameter_index": param,
            "value": value,
        },
    )


def set_volume(track, vol):
    send_udp("set_track_volume", {"track_index": track, "volume": vol})


def fire_scene(name):
    idx = SCENES.get(name, 0)
    send_udp("fire_clip", {"track_index": -1, "clip_index": idx})  # -1 triggers scene
    print(f"  >>> SCENE: {name}")


def fire_scene_tcp(name):
    """Fire scene via TCP for reliability"""
    idx = SCENES.get(name, 0)
    result = send_tcp("fire_scene", {"scene_index": idx})
    print(f"  >>> SCENE: {name}")
    return result


# Performance patterns using scenes
def pattern_intro_to_groove(analyzer):
    """Start minimal, build to groove"""
    print("[JOURNEY] Intro -> Groove -> Heavy")

    fire_scene_tcp("INTRO_Minimal")
    set_volume(1, 0.7)  # Bass moderate
    time.sleep(8)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  INTRO | RMS: {rms:.3f}")

    fire_scene_tcp("GROOVE_Dub")
    time.sleep(8)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  GROOVE | RMS: {rms:.3f}")

    fire_scene_tcp("HEAVY_Bass")
    set_volume(1, 0.85)  # Bass boosted
    time.sleep(8)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  HEAVY | RMS: {rms:.3f}")

    return 0.7


def pattern_dub_journey(analyzer):
    """Classic dub progression"""
    print("[DUB JOURNEY] Full band -> Drop -> Build")

    fire_scene_tcp("FULL_Band")
    time.sleep(12)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  FULL BAND | RMS: {rms:.3f}")

    # Drop
    fire_scene_tcp("DROP_Dub")
    set_param(1, 0, 170, 0.15)  # Bass filter low
    time.sleep(8)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  DROP | RMS: {rms:.3f}")

    # Build
    fire_scene_tcp("BUILD_Up")
    for i in range(8):
        t = i / 7
        set_param(1, 0, 170, 0.15 + 0.5 * t)  # Open bass filter
        time.sleep(1)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  BUILD COMPLETE | RMS: {rms:.3f}")

    return 0.8


def pattern_reggae_to_steppers(analyzer):
    """Reggae feel building to steppers"""
    print("[REGGAE -> STEPPERS] Building energy")

    fire_scene_tcp("REGGAE_Feel")
    set_volume(1, 0.7)
    time.sleep(10)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  REGGAE | RMS: {rms:.3f}")

    fire_scene_tcp("STEPPERS_Heavy")
    set_volume(1, 0.85)
    time.sleep(10)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  STEPPERS | RMS: {rms:.3f}")

    return 0.75


def pattern_breakdown_climax(analyzer):
    """Breakdown to climax"""
    print("[BREAKDOWN -> CLIMAX] Tension and release")

    fire_scene_tcp("BREAKDOWN")
    set_volume(1, 0.6)
    time.sleep(12)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  BREAKDOWN | RMS: {rms:.3f}")

    # Build to climax
    fire_scene_tcp("BUILD_Up")
    for i in range(6):
        t = i / 5
        set_volume(1, 0.6 + 0.25 * t)
        time.sleep(1.5)

    fire_scene_tcp("CLIMAX")
    set_volume(1, 0.85)
    time.sleep(8)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  CLIMAX | RMS: {rms:.3f}")

    return 0.9


def pattern_random_scene_hop(analyzer):
    """Random scene transitions"""
    print("[RANDOM HOP] Surprise transitions")

    scene_list = list(SCENES.keys())

    for i in range(4):
        scene = random.choice(scene_list)
        fire_scene_tcp(scene)

        # Adjust bass based on scene
        if "HEAVY" in scene or "DROP" in scene:
            set_volume(1, 0.85)
            set_param(1, 0, 170, 0.2)
        elif "INTRO" in scene or "BREAKDOWN" in scene:
            set_volume(1, 0.6)
            set_param(1, 0, 170, 0.4)
        else:
            set_volume(1, 0.75)
            set_param(1, 0, 170, 0.5)

        time.sleep(6)
        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  {scene} | RMS: {rms:.3f}")

    return 0.5


def pattern_bass_scenes(analyzer):
    """Focus on bass-heavy scenes"""
    print("[BASS FOCUS] Heavy scenes only")

    bass_scenes = ["HEAVY_Bass", "STEPPERS_Heavy", "DROP_Dub"]

    for scene in bass_scenes:
        fire_scene_tcp(scene)
        set_volume(1, 0.85)
        set_param(1, 0, 170, random.uniform(0.15, 0.3))
        time.sleep(8)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  {scene} | RMS: {rms:.3f}")

    return 0.7


def pattern_strip_and_build(analyzer):
    """Strip to minimal, then build"""
    print("[STRIP & BUILD] Minimal to full")

    # Strip to intro
    fire_scene_tcp("INTRO_Minimal")
    for track in range(6):
        set_volume(track, 0.4)
    set_volume(1, 0.7)  # Keep bass
    time.sleep(8)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  STRIPPED | RMS: {rms:.3f}")

    # Gradually bring in elements
    scenes = ["GROOVE_Dub", "FULL_Band", "CLIMAX"]
    for scene in scenes:
        fire_scene_tcp(scene)
        for track in range(6):
            current_vol = 0.4 + random.uniform(0.1, 0.3)
            set_volume(track, min(current_vol, 0.85))
        set_volume(1, 0.85)  # Always bass forward
        time.sleep(8)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  {scene} | RMS: {rms:.3f}")

    return 0.85


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
    analyzer._device_index = 109
    analyzer.start()
    time.sleep(0.5)

    print("=" * 60)
    print("  SCENE-BASED DJ PERFORMANCE")
    print("  Real-Time Audio Analysis")
    print("=" * 60)
    print()

    print("Available Scenes:")
    for name, idx in SCENES.items():
        print(f"  {idx}: {name}")
    print()

    # Initialize
    print("[INIT] Starting with INTRO_Minimal...")
    fire_scene_tcp("INTRO_Minimal")
    set_volume(1, 0.75)
    time.sleep(2)

    cycle = 0
    energy = 0.5

    patterns = [
        ("intro_groove", pattern_intro_to_groove),
        ("dub_journey", pattern_dub_journey),
        ("reggae_steppers", pattern_reggae_to_steppers),
        ("breakdown_climax", pattern_breakdown_climax),
        ("random_hop", pattern_random_scene_hop),
        ("bass_focus", pattern_bass_scenes),
        ("strip_build", pattern_strip_and_build),
    ]

    try:
        while True:
            cycle += 1
            print(f"\n{'=' * 50}")
            print(f"  CYCLE {cycle} | Energy: {energy:.0%}")
            print(f"{'=' * 50}")

            rms = analyzer.get_analysis().get("rms", 0)
            print(f"Current RMS: {rms:.3f}\n")

            # Choose pattern based on energy
            if energy < 0.4:
                # Low energy - build up
                energy = pattern_intro_to_groove(analyzer)
            elif energy > 0.8:
                # High energy - break down
                energy = pattern_breakdown_climax(analyzer)
            else:
                # Medium - random choice
                name, func = random.choice(patterns)
                energy = func(analyzer)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[STOP] Performance ended")
        print(f"Stats: {cycle} cycles")
    finally:
        analyzer.stop()
        print("Analyzer stopped")


if __name__ == "__main__":
    main()
