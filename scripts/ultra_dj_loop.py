#!/usr/bin/env python3
"""Continuous DJ Automation - Runs until /ulw"""

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


# All 18 clips per track
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


def fire(t, c):
    send_udp("fire_clip", {"track_index": t, "clip_index": c})


def vol(t, v):
    send_udp("set_track_volume", {"track_index": t, "volume": v})


def flt(v):
    send_udp(
        "set_device_parameter",
        {"track_index": 1, "device_index": 0, "parameter_index": 170, "value": v},
    )


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
print("ULTRAWORK DJ AUTOMATION - Running until /ulw")
print("=" * 50)

cycle = 0
energy = 0.5

try:
    while True:
        cycle += 1
        rms = az.get_analysis().get("rms", 0)
        roll = random.random()

        if energy < 0.3 or (roll < 0.15 and energy < 0.6):
            # BUILD
            print(f"[{cycle}] RMS:{rms:.2f} | BUILD | ", end="")
            fire(0, random.choice([D["minimal"], D["one_drop_var"], D["dub_4x4"]]))
            fire(1, random.choice([B["sub_hold"], B["sub_pulse"], B["filtered"]]))
            fire(2, G["minimal"])
            fire(3, O["minimal"])
            fire(4, random.choice([P["breath"], P["dark"], P["minimal"]]))
            flt(0.2)
            vol(1, 0.7)
            for i in range(4):
                flt(0.2 + 0.35 * (i / 3))
                time.sleep(1.5)
            energy = min(0.7, energy + 0.3)
            print(f"Energy -> {energy:.0%}")

        elif energy > 0.8 or (roll < 0.2 and energy > 0.6):
            # DROP
            print(f"[{cycle}] RMS:{rms:.2f} | DROP | ", end="")
            fire(0, random.choice([D["steppers_1"], D["steppers_2"], D["dub_heavy"]]))
            fire(1, random.choice([B["sub_drop"], B["drone_low"], B["deep"]]))
            fire(2, random.choice([G["skank_heavy"], G["chord_am"], G["full"]]))
            fire(3, random.choice([O["chord_am7"], O["hold_am"], O["bubble_am"]]))
            fire(4, random.choice([P["sub_am"], P["am7"], P["layer"]]))
            if random.random() > 0.6:
                fire(5, random.choice([F["impact_h"], F["combo"], F["thunder"]]))
                time.sleep(0.5)
                fire(5, F["none"])
            flt(0.15)
            vol(1, 0.9)
            time.sleep(6)
            energy = 0.4
            print(f"Energy -> {energy:.0%}")

        elif roll < 0.35:
            # GROOVE
            print(f"[{cycle}] RMS:{rms:.2f} | GROOVE | ", end="")
            fire(
                0,
                random.choice(
                    [D["rockers_1"], D["rockers_2"], D["rockers_3"], D["rockers_var"]]
                ),
            )
            fire(
                1,
                random.choice(
                    [B["walking_1"], B["walking_2"], B["am_walk"], B["root_5th"]]
                ),
            )
            fire(
                2,
                random.choice(
                    [G["skank_2and4"], G["basic"], G["double"], G["skank_light"]]
                ),
            )
            fire(
                3,
                random.choice(
                    [O["bubble_1"], O["bubble_am"], O["bubble_dm"], O["bubble_var"]]
                ),
            )
            fire(4, random.choice([P["am7"], P["dm7"], P["sustain"]]))
            flt(0.35)
            vol(1, 0.75)
            time.sleep(8)
            energy = 0.5 + random.uniform(-0.1, 0.2)
            print(f"Energy -> {energy:.0%}")

        elif roll < 0.5:
            # BASS HEAVY
            print(f"[{cycle}] RMS:{rms:.2f} | BASS | ", end="")
            fire(
                0,
                random.choice(
                    [D["steppers_1"], D["steppers_2"], D["steppers_var"], D["techno"]]
                ),
            )
            fire(
                1,
                random.choice(
                    [B["sub_hold"], B["sub_pulse"], B["drone_low"], B["deep"]]
                ),
            )
            fire(2, G["minimal"])
            fire(3, O["minimal"])
            fire(4, random.choice([P["sub_am"], P["dark"], P["deep"]]))
            flt(0.15)
            vol(1, 0.9)
            time.sleep(8)
            energy = 0.6 + random.uniform(0, 0.2)
            print(f"Energy -> {energy:.0%}")

        elif roll < 0.65:
            # FULL BAND
            print(f"[{cycle}] RMS:{rms:.2f} | FULL | ", end="")
            fire(
                0,
                random.choice(
                    [D["rockers_2"], D["steppers_1"], D["break"], D["techno"]]
                ),
            )
            fire(
                1, random.choice([B["syncopated"], B["glide"], B["arpeg"], B["pluck"]])
            )
            fire(
                2, random.choice([G["full"], G["chord_am"], G["chord_dm"], G["accent"]])
            )
            fire(
                3,
                random.choice(
                    [O["chord_am7"], O["chord_dm7"], O["shuffle"], O["sustain"]]
                ),
            )
            fire(4, random.choice([P["layer"], P["evolve"], P["bright"]]))
            if random.random() > 0.5:
                fire(5, random.choice([F["impact_l"], F["sub_hit"], F["crash"]]))
                time.sleep(0.3)
                fire(5, F["none"])
            flt(0.3)
            vol(1, 0.75)
            time.sleep(7)
            energy = 0.7 + random.uniform(0, 0.15)
            print(f"Energy -> {energy:.0%}")

        elif roll < 0.8:
            # RISE
            print(f"[{cycle}] RMS:{rms:.2f} | RISE | ", end="")
            fire(0, D["minimal"])
            fire(1, B["filtered"])
            fire(2, G["mute"])
            fire(3, O["minimal"])
            fire(4, P["breath"])
            fire(5, random.choice([F["rise_4"], F["rise_8"], F["sweep_up"]]))
            flt(0.2)
            vol(1, 0.6)
            for i in range(5):
                flt(0.2 + 0.4 * (i / 4))
                time.sleep(1.2)
            fire(5, F["none"])
            energy = 0.8
            print(f"Energy -> {energy:.0%}")

        else:
            # EVOLVE
            print(f"[{cycle}] RMS:{rms:.2f} | EVOLVE | ", end="")
            fire(0, random.choice([D["steppers_1"], D["rockers_1"], D["one_drop_1"]]))
            fire(1, random.choice([B["deep"], B["drone_c"], B["walking_1"]]))
            for _ in range(4):
                fire(
                    2, random.choice([G["skank_2and4"], G["skank_light"], G["minimal"]])
                )
                fire(3, random.choice([O["bubble_1"], O["minimal"], O["low"]]))
                flt(random.uniform(0.2, 0.5))
                vol(1, random.uniform(0.7, 0.85))
                time.sleep(3)
            energy = 0.5 + random.uniform(-0.2, 0.3)
            print(f"Energy -> {energy:.0%}")

except KeyboardInterrupt:
    print("\n[STOPPED] /ulw received")
finally:
    az.stop()
    print("Analyzer stopped")
