#!/usr/bin/env python3
"""Bass-Heavy DJ Performance with Real-Time Audio Analysis"""

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


# Clip definitions
DRUM_CLIPS = {"one_drop": [0, 1, 2], "rockers": [3, 4, 5], "steppers": [6, 7]}

BASS_CLIPS = {
    "deep": [6],  # Bass_Deep - HEAVY
    "drone_low": [1],  # Bass_Drone_Low - HEAVY
    "drone": [0],  # Bass_Drone_C
    "walking": [2, 3],  # Bass_Walking
    "pluck": [4],  # Bass_Pluck
    "syncopated": [5],  # Bass_Syncopated
    "tremolo": [7],  # Bass_Tremolo
}

GUITAR_CLIPS = {
    "basic": [0],
    "double": [1],
    "syncopated": [2],
    "muted": [3],
    "full": [4],
    "light": [5],
    "accent": [6],
    "minimal": [7],
}

ORGAN_CLIPS = {
    "bubble": [0, 1],
    "stab": [2],
    "high": [3],
    "low": [4],
    "shuffle": [5],
    "sustain": [6],
    "minimal": [7],
}

PAD_CLIPS = {
    "sustain": [0],
    "swell": [1],
    "dark": [2],
    "bright": [3],
    "minimal": [4],
    "evolver": [5],
    "deep": [6],
    "none": [7],
}

FX_CLIPS = {
    "sub_hit": [0],
    "crash": [1],
    "noise": [2],
    "rise": [3],
    "fall": [4],
    "thunder": [5],
    "sweep": [6],
    "none": [7],
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


def fire_clip(track, clip):
    send_udp("fire_clip", {"track_index": track, "clip_index": clip})


# Bass-heavy performance patterns
def pattern_bass_drop_build(analyzer):
    """Heavy bass drop with buildup"""
    print("[BASS DROP BUILD] Building tension...")

    # Start with minimal elements
    fire_clip(0, random.choice(DRUM_CLIPS["one_drop"]))  # Sparse drums
    fire_clip(1, random.choice(BASS_CLIPS["deep"]))  # Deep bass
    fire_clip(4, random.choice(PAD_CLIPS["dark"]))  # Dark pad

    # Build filter on bass over 8 steps
    for i in range(8):
        t = i / 7
        bass_filter = 0.2 + 0.5 * t  # Open bass filter
        set_param(1, 0, 170, bass_filter)
        set_param(1, 0, 171, 0.2 + 0.3 * t)  # Resonance up

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  Build {i + 1}/8 | RMS: {rms:.3f} | Bass Filter: {bass_filter:.2f}")
        time.sleep(1.5)

    # DROP - switch to heavy steppers
    print("  [DROP!] Switching to heavy mode!")
    fire_clip(0, random.choice(DRUM_CLIPS["steppers"]))
    fire_clip(1, random.choice(BASS_CLIPS["drone_low"]))

    # Slam filters closed
    set_param(1, 0, 170, 0.15)  # Very low filter = MAX BASS
    set_volume(1, 0.85)  # Boost bass volume

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  DROPPED! RMS: {rms:.3f}")
    time.sleep(4)

    # Slow return
    for i in range(6):
        t = i / 5
        set_param(1, 0, 170, 0.15 + 0.4 * t)
        set_volume(1, 0.75 - 0.1 * t)
        time.sleep(2)

    return 0.7


def pattern_dub_steppers(analyzer):
    """Classic dub steppers with heavy bass"""
    print("[DUB STEPPERS] Heavy bass groove...")

    # Steppers drums + deep bass
    fire_clip(0, random.choice(DRUM_CLIPS["steppers"]))
    fire_clip(1, random.choice(BASS_CLIPS["deep"]))
    fire_clip(2, random.choice(GUITAR_CLIPS["minimal"]))
    fire_clip(3, random.choice(ORGAN_CLIPS["minimal"]))

    # Hold with subtle bass variations
    for i in range(6):
        bass_filter = random.uniform(0.2, 0.4)
        bass_res = random.uniform(0.15, 0.35)
        set_param(1, 0, 170, bass_filter)
        set_param(1, 0, 171, bass_res)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  Steppers {i + 1}/6 | RMS: {rms:.3f}")
        time.sleep(3)

    return 0.6


def pattern_bass_evolution(analyzer):
    """Evolve through different bass patterns"""
    print("[BASS EVOLUTION] Cycling bass patterns...")

    bass_patterns = ["deep", "drone_low", "drone", "syncopated"]

    for i, pattern in enumerate(bass_patterns):
        clip = random.choice(BASS_CLIPS[pattern])
        fire_clip(1, clip)

        # Adjust filter based on pattern
        if pattern in ["deep", "drone_low"]:
            bass_filter = random.uniform(0.15, 0.3)  # Low = more bass
            set_volume(1, 0.8)
        else:
            bass_filter = random.uniform(0.4, 0.6)
            set_volume(1, 0.7)

        set_param(1, 0, 170, bass_filter)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  {pattern.upper()} | RMS: {rms:.3f} | Filter: {bass_filter:.2f}")
        time.sleep(4)

    return 0.55


def pattern_full_bass_assault(analyzer):
    """All elements with heavy bass focus"""
    print("[FULL BASS ASSAULT] All tracks, bass-forward...")

    # Fire all tracks
    fire_clip(0, random.choice(DRUM_CLIPS["steppers"]))
    fire_clip(1, random.choice(BASS_CLIPS["drone_low"]))
    fire_clip(2, random.choice(GUITAR_CLIPS["full"]))
    fire_clip(3, random.choice(ORGAN_CLIPS["bubble"]))
    fire_clip(4, random.choice(PAD_CLIPS["deep"]))

    # Bass forward in mix
    set_volume(1, 0.85)
    set_volume(0, 0.65)  # Drums back
    set_volume(2, 0.55)  # Guitar back
    set_volume(3, 0.5)  # Organ back
    set_volume(4, 0.45)  # Pad back

    # Keep bass filter low
    set_param(1, 0, 170, 0.2)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  ALL IN | RMS: {rms:.3f}")

    # Evolve for 20 seconds
    for i in range(5):
        bass_filter = random.uniform(0.15, 0.35)
        set_param(1, 0, 170, bass_filter)

        # Occasionally tweak other elements
        if random.random() > 0.5:
            set_volume(2, random.uniform(0.4, 0.6))
        if random.random() > 0.5:
            set_volume(3, random.uniform(0.35, 0.55))

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  Evolving {i + 1}/5 | RMS: {rms:.3f}")
        time.sleep(4)

    return 0.8


def pattern_strip_to_bass(analyzer):
    """Strip everything except bass and minimal drums"""
    print("[STRIP TO BASS] Minimal mode...")

    # Minimal drums + bass only
    fire_clip(0, random.choice(DRUM_CLIPS["one_drop"]))
    fire_clip(1, random.choice(BASS_CLIPS["deep"]))
    fire_clip(2, 7)  # Minimal/silent
    fire_clip(3, 7)  # Minimal/silent
    fire_clip(4, 7)  # Minimal/silent

    # Bass prominent
    set_volume(1, 0.85)
    set_volume(0, 0.5)

    # Low filter for sub bass
    set_param(1, 0, 170, 0.15)
    set_param(1, 0, 171, 0.25)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  BASS ONLY | RMS: {rms:.3f}")
    time.sleep(8)

    return 0.3


def pattern_bass_fx_combo(analyzer):
    """Bass with FX hits"""
    print("[BASS + FX] Adding effects...")

    fire_clip(1, random.choice(BASS_CLIPS["deep"]))

    # Hit FX
    fx_sounds = ["sub_hit", "thunder", "sweep"]
    for fx in fx_sounds:
        fire_clip(5, random.choice(FX_CLIPS[fx]))
        time.sleep(0.5)

    rms = analyzer.get_analysis().get("rms", 0)
    print(f"  FX HIT | RMS: {rms:.3f}")

    time.sleep(6)
    fire_clip(5, 7)  # FX off

    return 0.5


def pattern_reggae_bass(analyzer):
    """Classic reggae/dub bass feel"""
    print("[REGGAE BASS] One drop feel...")

    fire_clip(0, random.choice(DRUM_CLIPS["one_drop"]))
    fire_clip(1, random.choice(BASS_CLIPS["walking"]))
    fire_clip(2, random.choice(GUITAR_CLIPS["basic"]))

    # Balanced mix, bass forward
    set_volume(1, 0.75)
    set_volume(0, 0.6)
    set_volume(2, 0.55)

    # Moderate bass filter
    set_param(1, 0, 170, 0.45)

    for i in range(4):
        # Subtle bass movement
        bass_filter = 0.4 + random.uniform(-0.1, 0.1)
        set_param(1, 0, 170, bass_filter)

        rms = analyzer.get_analysis().get("rms", 0)
        print(f"  Reggae feel {i + 1}/4 | RMS: {rms:.3f}")
        time.sleep(4)

    return 0.5


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
    print("  BASS-HEAVY DJ PERFORMANCE")
    print("  Real-Time Audio Analysis")
    print("=" * 60)
    print()

    # Initialize bass-heavy state
    print("[INIT] Setting up bass-heavy state...")
    fire_clip(0, 6)  # Steppers drums
    fire_clip(1, 6)  # Deep bass
    fire_clip(2, 7)  # Minimal guitar
    fire_clip(3, 7)  # Minimal organ
    fire_clip(4, 6)  # Deep pad
    fire_clip(5, 7)  # FX off

    set_volume(1, 0.8)  # Bass boosted
    set_param(1, 0, 170, 0.25)  # Low filter for bass

    print("Ready! Starting performance...\n")

    cycle = 0
    energy = 0.5

    patterns = [
        ("bass_drop", pattern_bass_drop_build),
        ("steppers", pattern_dub_steppers),
        ("evolution", pattern_bass_evolution),
        ("full", pattern_full_bass_assault),
        ("strip", pattern_strip_to_bass),
        ("fx", pattern_bass_fx_combo),
        ("reggae", pattern_reggae_bass),
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
            if energy < 0.35:
                # Low energy - build up with bass
                energy = pattern_bass_drop_build(analyzer)
            elif energy > 0.7:
                # High energy - strip back
                energy = pattern_strip_to_bass(analyzer)
            else:
                # Medium - choose randomly weighted toward bass
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
