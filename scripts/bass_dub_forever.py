#!/usr/bin/env python3
"""
BASS-HEAVY DUB MIXER - Runs Forever
Slow steady evolution with live parameter changes
Dub techno techniques: filter sweeps, delays, sub bass
"""

import socket
import json
import time
import random
import sys
import math

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


# Clip mappings
D = {
    "dub_4x4": 0,
    "dub_off": 1,
    "dub_sync": 2,
    "techno": 3,
    "break": 4,
    "dub_heavy": 5,
    "one_drop_var": 6,
    "rockers_var": 7,
    "steppers_var": 8,
    "minimal": 9,
    "one_drop_1": 10,
    "one_drop_2": 11,
    "one_drop_3": 12,
    "rockers_1": 13,
    "rockers_2": 14,
    "rockers_3": 15,
    "steppers_1": 16,
    "steppers_2": 17,
}
B = {
    "sub_hold": 0,
    "sub_pulse": 1,
    "am_walk": 2,
    "dm_oct": 3,
    "filtered": 4,
    "stabs": 5,
    "root_5th": 6,
    "glide": 7,
    "arpeg": 8,
    "sub_drop": 9,
    "drone_c": 10,
    "drone_low": 11,
    "walking_1": 12,
    "walking_2": 13,
    "pluck": 14,
    "syncopated": 15,
    "deep": 16,
    "tremolo": 17,
}
G = {
    "skank_2and4": 0,
    "skank_16th": 1,
    "skank_triplet": 2,
    "chord_am": 3,
    "chord_dm": 4,
    "chord_g": 5,
    "skank_heavy": 6,
    "skank_light": 7,
    "mute": 8,
    "skank_delay": 9,
    "basic": 10,
    "double": 11,
    "syncopated": 12,
    "muted": 13,
    "full": 14,
    "light": 15,
    "accent": 16,
    "minimal": 17,
}
O = {
    "bubble_am": 0,
    "bubble_dm": 1,
    "bubble_g": 2,
    "chord_am7": 3,
    "chord_dm7": 4,
    "stab_2and4": 5,
    "run_up": 6,
    "run_down": 7,
    "hold_am": 8,
    "bubble_var": 9,
    "bubble_1": 10,
    "bubble_2": 11,
    "stab": 12,
    "high": 13,
    "low": 14,
    "shuffle": 15,
    "sustain": 16,
    "minimal": 17,
}
P = {
    "am": 0,
    "dm": 1,
    "g": 2,
    "c": 3,
    "am7": 4,
    "dm7": 5,
    "sub_am": 6,
    "evolve": 7,
    "layer": 8,
    "breath": 9,
    "sustain": 10,
    "swell": 11,
    "dark": 12,
    "bright": 13,
    "minimal": 14,
    "evolver": 15,
    "deep": 16,
    "none": 17,
}
F = {
    "impact_h": 0,
    "impact_l": 1,
    "rise_4": 2,
    "rise_8": 3,
    "fall_4": 4,
    "noise": 5,
    "sweep_up": 6,
    "sweep_down": 7,
    "atmos": 8,
    "combo": 9,
    "sub_hit": 10,
    "crash": 11,
    "noise_orig": 12,
    "rise": 13,
    "fall": 14,
    "thunder": 15,
    "sweep": 16,
    "none": 17,
}

# Parameter indices for different tracks
PARAMS = {
    "drums_filter": (0, 0, 2),
    "drums_reverb": (0, 0, 8),
    "drums_delay": (0, 0, 6),
    "drums_overdrive": (0, 0, 3),
    "bass_filter": (1, 0, 170),
    "bass_res": (1, 0, 171),
}


def fire(t, c):
    send_udp("fire_clip", {"track_index": t, "clip_index": c})


def vol(t, v):
    send_udp("set_track_volume", {"track_index": t, "volume": v})


def param(name, v):
    t, d, p = PARAMS[name]
    send_udp(
        "set_device_parameter",
        {"track_index": t, "device_index": d, "parameter_index": p, "value": v},
    )


def lerp(a, b, t):
    return a + (b - a) * t


# Start analyzer
cfg = AudioAnalyzerConfig(
    sample_rate=44100,
    buffer_size=4096,
    analysis_features={
        "key": False,
        "bpm": False,
        "spectral": False,
        "loudness": False,
    },
)
az = AudioAnalyzer(cfg)
az._device_index = 109
az.start()
time.sleep(0.3)

send_tcp("start_playback")

# Initialize bass-heavy state
fire(0, D["steppers_1"])
fire(1, B["sub_hold"])
fire(2, G["minimal"])
fire(3, O["minimal"])
fire(4, P["sub_am"])
fire(5, F["none"])
vol(1, 0.9)
param("bass_filter", 0.15)

print("=" * 60)
print("  BASS-HEAVY DUB MIXER - Running Forever")
print("  Slow evolution + Live parameter automation")
print("=" * 60)

cycle = 0
theme = "sub_deep"  # Current theme
themes = ["sub_deep", "dub_groove", "chord_dub", "minimal_space", "full_dub"]

# Live parameter state
bass_filter_target = 0.15
drums_reverb_target = 30
energy = 0.6

try:
    while True:
        cycle += 1
        rms = az.get_analysis().get("rms", 0)

        # Slow theme changes every 8-15 cycles
        if cycle % random.randint(8, 15) == 0:
            old_theme = theme
            theme = random.choice(themes)
            print(f"\n[THEME CHANGE] {old_theme} -> {theme}")

        print(f"[{cycle}] RMS:{rms:.2f} | Theme:{theme} | Energy:{energy:.0%}")

        # === LIVE PARAMETER AUTOMATION (always running) ===
        # Smooth parameter interpolation towards targets
        for _ in range(4):
            # Bass filter - slow movement
            current_bf = bass_filter_target
            bass_filter_target = 0.15 + 0.35 * (
                0.5 + 0.5 * math.sin(cycle * 0.1 + random.uniform(-0.1, 0.1))
            )
            param("bass_filter", lerp(current_bf, bass_filter_target, 0.3))

            # Drums reverb - breathing effect
            drums_reverb_target = 30 + 40 * (0.5 + 0.5 * math.sin(cycle * 0.05))
            param("drums_reverb", drums_reverb_target)

            # Bass volume micro-automation
            vol(1, 0.85 + 0.08 * math.sin(cycle * 0.15))

            time.sleep(2)

        # === THEME-SPECIFIC CLIP PATTERNS ===
        if theme == "sub_deep":
            print("  [SUB DEEP] Maximum bass pressure")
            fire(0, random.choice([D["steppers_1"], D["steppers_2"], D["dub_heavy"]]))
            fire(
                1,
                random.choice(
                    [B["sub_hold"], B["sub_pulse"], B["sub_drop"], B["drone_low"]]
                ),
            )
            fire(2, G["minimal"])
            fire(3, O["minimal"])
            fire(4, random.choice([P["sub_am"], P["dark"], P["deep"]]))
            vol(1, 0.92)
            energy = lerp(energy, 0.75, 0.3)

        elif theme == "dub_groove":
            print("  [DUB GROOVE] Classic dub feel")
            fire(0, random.choice([D["rockers_1"], D["rockers_2"], D["one_drop_1"]]))
            fire(1, random.choice([B["walking_1"], B["am_walk"], B["root_5th"]]))
            fire(2, random.choice([G["skank_2and4"], G["basic"], G["skank_light"]]))
            fire(3, random.choice([O["bubble_1"], O["bubble_am"], O["low"]]))
            fire(4, random.choice([P["am7"], P["sustain"]]))
            vol(1, 0.8)
            energy = lerp(energy, 0.5, 0.3)

        elif theme == "chord_dub":
            print("  [CHORD DUB] Harmonic layers")
            fire(0, random.choice([D["rockers_var"], D["steppers_var"]]))
            fire(1, random.choice([B["drone_c"], B["glide"]]))
            fire(2, random.choice([G["chord_am"], G["chord_dm"], G["chord_g"]]))
            fire(3, random.choice([O["chord_am7"], O["chord_dm7"], O["hold_am"]]))
            fire(4, random.choice([P["am7"], P["dm7"], P["layer"]]))
            vol(1, 0.78)
            energy = lerp(energy, 0.55, 0.3)

        elif theme == "minimal_space":
            print("  [MINIMAL SPACE] Sparse and atmospheric")
            fire(0, D["minimal"])
            fire(1, random.choice([B["filtered"], B["sub_hold"]]))
            fire(2, G["mute"])
            fire(3, O["minimal"])
            fire(4, random.choice([P["breath"], P["swell"], P["minimal"]]))
            if random.random() > 0.7:
                fire(5, random.choice([F["atmos"], F["sweep_up"]]))
                time.sleep(3)
                fire(5, F["none"])
            vol(1, 0.7)
            energy = lerp(energy, 0.25, 0.3)

        elif theme == "full_dub":
            print("  [FULL DUB] All elements")
            fire(0, random.choice([D["rockers_2"], D["steppers_1"], D["break"]]))
            fire(1, random.choice([B["syncopated"], B["deep"], B["walking_2"]]))
            fire(2, random.choice([G["full"], G["accent"], G["double"]]))
            fire(3, random.choice([O["shuffle"], O["sustain"], O["bubble_2"]]))
            fire(4, random.choice([P["evolve"], P["bright"], P["evolver"]]))
            if random.random() > 0.6:
                fire(5, random.choice([F["impact_l"], F["sub_hit"]]))
                time.sleep(0.5)
                fire(5, F["none"])
            vol(1, 0.82)
            energy = lerp(energy, 0.7, 0.3)

        # === SLOW FILTER SWEEPS ===
        print("  Filter sweep...")
        sweep_start = 0.15 if theme in ["sub_deep", "minimal_space"] else 0.3
        sweep_end = 0.6 if random.random() > 0.5 else 0.25

        for i in range(8):
            t = i / 7
            # Smooth sine curve for musical sweep
            curve = math.sin(t * math.pi / 2)
            param("bass_filter", lerp(sweep_start, sweep_end, curve))
            time.sleep(1.5)

        # === OCCASIONAL DROPS ===
        if random.random() > 0.85 and energy > 0.5:
            print("  [DROP!] Bass slam")
            fire(1, B["sub_drop"])
            vol(1, 0.95)
            param("bass_filter", 0.1)
            time.sleep(4)
            vol(1, 0.85)

        time.sleep(2)

except KeyboardInterrupt:
    print("\n[STOPPED]")
finally:
    az.stop()
