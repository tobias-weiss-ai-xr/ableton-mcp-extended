#!/usr/bin/env python3
"""2-Hour automated mix showcasing all mixing tools.

Rotates through: bass_forward_mix, dub_drop, strip_and_build,
crossfader_sweep, send_sweep, effect_stab, parameter_lock, scene_transition.

Requires: 2h_mix_setup.py already run against Ableton Live + MCP.

Usage: python scripts/2h_mix_automation.py
"""

import socket
import json
import time
import random
import sys
from datetime import datetime, timedelta

HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_PORT = 9878

BPM = 126
DURATION_MINUTES = 120

# Track constants
DRUMS = [0, 1, 2, 3]
KICK, SNARE, HIHAT, CLAP = 0, 1, 2, 3
BASS = 4
CHORDS = 5
MELODY = 6
FX = 7

ALL_TRACKS = list(range(8))
PERC_TRACKS = DRUMS
MELODIC_TRACKS = [BASS, CHORDS, MELODY, FX]


def tcp(cmd, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, TCP_PORT))
    msg = json.dumps({"type": cmd, "params": params or {}})
    sock.sendall((msg + "\n").encode())
    resp = json.loads(sock.recv(65536).decode())
    sock.close()
    return resp


def udp(cmd, params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps({"type": cmd, "params": params}).encode(), (HOST, UDP_PORT))
    sock.close()


def beat_seconds(beats):
    return beats * 60.0 / BPM


# ── Mixing action primitives ─────────────────────────────────────────

def action_bass_forward(amount=0.7):
    """Boost bass, cut other melodic tracks."""
    bass_vol = 0.8 + amount * 0.15
    other_vol = 0.5 - amount * 0.15
    for t in MELODIC_TRACKS:
        v = bass_vol if t == BASS else other_vol
        udp("set_track_volume", {"track_index": t, "volume": v})
    # Bass filter - lower = more sub
    udp("set_device_parameter", {"track_index": BASS, "device_index": 0, "parameter_index": 10, "value": 0.3 - amount * 0.15})
    return f"bass_forward (amount={amount:.1f})"


def action_dub_drop(quick=False):
    """Filter slam + volume cut on drums, then return."""
    drop_val = 0.15
    return_val = 0.75
    dur = 4 if quick else 12
    steps = 4

    # INSTANT drop - close filters
    for t in PERC_TRACKS:
        udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": 2, "value": drop_val})
    udp("set_device_parameter", {"track_index": BASS, "device_index": 0, "parameter_index": 10, "value": drop_val})
    time.sleep(beat_seconds(1))

    # Gradual return
    for i in range(steps):
        t = (i + 1) / steps
        val = drop_val + (return_val - drop_val) * t
        for tr in PERC_TRACKS:
            udp("set_device_parameter", {"track_index": tr, "device_index": 0, "parameter_index": 2, "value": val})
        udp("set_device_parameter", {"track_index": BASS, "device_index": 0, "parameter_index": 10, "value": val})
        time.sleep(beat_seconds(dur / steps))

    return f"dub_drop (dur={dur}b)"


def action_strip_and_build(target_energy):
    """Strip tracks to low volume, then bring back per target energy."""
    # Strip
    for t in ALL_TRACKS:
        udp("set_track_volume", {"track_index": t, "volume": 0.2})
    time.sleep(beat_seconds(4))

    # Fire minimal kick + bass for stripped section
    udp("fire_clip", {"track_index": KICK, "clip_index": 0})
    udp("fire_clip", {"track_index": BASS, "clip_index": 0})
    time.sleep(beat_seconds(4))

    # Build back based on energy
    layers = int(target_energy * 6) + 1
    for i in range(layers):
        t_idx = ALL_TRACKS[min(i, len(ALL_TRACKS) - 1)]
        vol = 0.4 + (target_energy * 0.5)
        udp("set_track_volume", {"track_index": t_idx, "volume": vol})

        if t_idx in [SNARE, HIHAT, CLAP]:
            tcp("fire_clip", {"track_index": t_idx, "clip_index": i + 4})
        elif t_idx in [CHORDS, MELODY, FX]:
            tcp("fire_clip", {"track_index": t_idx, "clip_index": i + 4})

        time.sleep(beat_seconds(4))

    return f"strip_and_build (energy={target_energy:.1f})"


def action_crossfader_sweep():
    """Sweep crossfader from center to one side and back (TCP)."""
    for val in [0.0, -0.6, -1.0, -0.6, 0.0, 0.6, 1.0, 0.6, 0.0]:
        tcp("set_crossfader", {"value": val})
        time.sleep(beat_seconds(2))
    return "crossfader_sweep"


def action_crossfader_assign_swap():
    """Swap track crossfader assignments."""
    assigns = [("A", None), ("B", None), (None, "A"), (None, "B")]
    for kick_a, snare_a in assigns:
        if kick_a:
            tcp("set_track_crossfade_assign", {"track_index": KICK, "value": kick_a})
        if snare_a:
            tcp("set_track_crossfade_assign", {"track_index": SNARE, "value": snare_a})
        time.sleep(beat_seconds(4))
    return "crossfader_assign_swap"


def action_send_sweep():
    """Sweep send amounts on melodic tracks."""
    send_idx = 0
    for val in [0.0, 0.2, 0.4, 0.6, 0.5, 0.3, 0.1, 0.0]:
        for t in MELODIC_TRACKS:
            udp("set_send_amount", {"track_index": t, "send_index": send_idx, "amount": val})
        time.sleep(beat_seconds(2))
    return f"send_sweep (send={send_idx})"


def action_effect_stab():
    """Quick reverb/delay burst on drums, then back."""
    for t in PERC_TRACKS:
        udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": 8, "value": 0.9})  # reverb
        udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": 6, "value": 0.7})  # delay
    time.sleep(beat_seconds(1))
    for t in PERC_TRACKS:
        udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": 8, "value": 0.3})
        udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": 6, "value": 0.2})
    time.sleep(beat_seconds(2))
    return "effect_stab"


def action_parameter_drift():
    """Random drift on drum parameters."""
    params = [2, 3, 6, 8]  # filter, overdrive, delay, reverb
    for p in params:
        for t in PERC_TRACKS:
            val = random.uniform(0.2, 0.8)
            udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": p, "value": val})
        time.sleep(beat_seconds(1))
    return "parameter_drift"


def action_scene_transition(target_scene):
    """Wash with reverb, fire scene, restore."""
    for t in PERC_TRACKS:
        udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": 8, "value": 0.8})
    time.sleep(beat_seconds(2))
    tcp("fire_scene", {"scene_index": target_scene})
    time.sleep(beat_seconds(2))
    for t in PERC_TRACKS:
        udp("set_device_parameter", {"track_index": t, "device_index": 0, "parameter_index": 8, "value": 0.3})
    return f"scene_transition -> {target_scene}"


def action_metering():
    """Read and log current levels."""
    levels = tcp("get_level_snapshot")
    if isinstance(levels, dict) and "result" in levels:
        data = levels["result"]
        if isinstance(data, dict) and "tracks" in data:
            track_infos = []
            for tr in data["tracks"][:4]:
                left = tr.get("output_meter_left", 0)
                right = tr.get("output_meter_right", 0)
                name = tr.get("name", f"T{tr.get('index', '?')}")
                track_infos.append(f"{name}: L={left:.2f} R={right:.2f}")
            return "metering: " + " | ".join(track_infos)
    return "metering: (no data)"


# ── Action registry ──────────────────────────────────────────────────

ACTIONS = [
    (action_bass_forward, 0.15, {"amount": 0.7}),
    (action_dub_drop, 0.12, {"quick": False}),
    (action_dub_drop, 0.08, {"quick": True}),
    (action_strip_and_build, 0.10, {"target_energy": 0.6}),
    (action_strip_and_build, 0.05, {"target_energy": 0.3}),
    (action_strip_and_build, 0.05, {"target_energy": 0.8}),
    (action_crossfader_sweep, 0.08, {}),
    (action_crossfader_assign_swap, 0.05, {}),
    (action_send_sweep, 0.08, {}),
    (action_effect_stab, 0.07, {}),
    (action_parameter_drift, 0.10, {}),
    (action_metering, 0.07, {}),
]

# Re-weight: ensure varied distribution
# Each action gets a random weight adjusted by its base
# We also add specialized crossfader assign actions


def energy_at_minute(minute):
    """Return target energy (0.0-1.0) based on elapsed minute."""
    total = DURATION_MINUTES
    # Arc: intro (0-15min), build (15-30), peak (30-60), break (60-75), build (75-90), outro (90-120)
    if minute < 15:
        return 0.2 + minute / 15 * 0.3  # 0.2 → 0.5
    elif minute < 30:
        return 0.5 + (minute - 15) / 15 * 0.2  # 0.5 → 0.7
    elif minute < 60:
        return 0.7 + (minute - 30) / 30 * 0.2  # 0.7 → 0.9
    elif minute < 75:
        return 0.9 - (minute - 60) / 15 * 0.4  # 0.9 → 0.5
    elif minute < 90:
        return 0.5 + (minute - 75) / 15 * 0.3  # 0.5 → 0.8
    else:
        return 0.8 - (minute - 90) / 30 * 0.7  # 0.8 → 0.1


def pick_action(current_energy):
    """Pick action weighted by energy compatibility."""
    # Adjust weights based on energy
    weighted = []
    for func, base_weight, kwargs in ACTIONS:
        w = base_weight
        name = func.__name__
        # High energy: favor drops, strips
        if current_energy > 0.7:
            if "drop" in name or "strip" in name or "crossfader" in name:
                w *= 1.5
        # Low energy: favor builds, drifts, sweeps
        elif current_energy < 0.4:
            if "build" in name or "drift" in name or "send" in name:
                w *= 1.5
        # Medium: favor transitions
        else:
            if "transition" in name or "forward" in name or "metering" in name:
                w *= 1.3
        weighted.append((func, kwargs, w))

    total = sum(w for _, _, w in weighted)
    r = random.uniform(0, total)
    cumulative = 0
    for func, kwargs, w in weighted:
        cumulative += w
        if r <= cumulative:
            return func, kwargs
    return weighted[-1][0], weighted[-1][1]


def main():
    print("=" * 60)
    print("  2-HOUR MIX AUTOMATION")
    print(f"  {BPM} BPM | {DURATION_MINUTES} minutes | 8 tracks")
    print("  Showcasing: bass_forward, dub_drop, strip_and_build,")
    print("  crossfader_sweep, send_sweep, effect_stab, parameter_drift")
    print("=" * 60)

    # Start playback
    print("\n[START] Starting playback...")
    tcp("start_playback")
    time.sleep(1)

    # Fire initial clips (scene 0 = Intro)
    print("[INIT] Firing scene 0...")
    tcp("fire_scene", {"scene_index": 0})
    time.sleep(2)

    # Fire clips for all tracks at scene 0
    for t in ALL_TRACKS:
        tcp("fire_clip", {"track_index": t, "clip_index": 0})

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=DURATION_MINUTES)
    actions_taken = 0
    last_scene = 0
    current_energy = 0.2

    print(f"\n[MIX START] {start_time.strftime('%H:%M:%S')}")
    print(f"[MIX END]   {end_time.strftime('%H:%M:%S')}")
    print(f"[DURATION]  {DURATION_MINUTES} minutes\n")

    try:
        while datetime.now() < end_time:
            elapsed = (datetime.now() - start_time).total_seconds() / 60.0
            remaining = (end_time - datetime.now()).total_seconds() / 60.0
            current_energy = energy_at_minute(elapsed)

            # Every ~5 min: fire next scene to advance arrangement
            scene_idx = min(int(elapsed / 5), 23)
            if scene_idx != last_scene:
                print(f"\n  [SCENE] -> {scene_idx} ({datetime.now().strftime('%H:%M:%S')})")
                tcp("fire_scene", {"scene_index": scene_idx})
                last_scene = scene_idx

            # Pick and execute action
            func, kwargs = pick_action(current_energy)
            actions_taken += 1

            # Log
            timestamp = datetime.now().strftime('%H:%M:%S')
            result = func(**kwargs)
            elapsed_min = int(elapsed)
            remaining_min = int(remaining)
            pct = (elapsed / DURATION_MINUTES) * 100

            print(f"  [{timestamp}] +{elapsed_min}m (E:{current_energy:.1f}) [{pct:3.0f}%] {result}")

            # Wait 30-120 seconds before next action
            wait_time = random.uniform(30, 90)
            # Adjust wait based on energy - more action at high/low points
            if current_energy > 0.8 or current_energy < 0.3:
                wait_time *= 0.7  # shorter waits at extremes
            wait_time = max(20, min(wait_time, 120))

            # Sleep in small chunks for responsive Ctrl+C
            for _ in range(int(wait_time)):
                if datetime.now() >= end_time:
                    break
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[STOP] Mix ended by user")

    elapsed_total = (datetime.now() - start_time).total_seconds() / 60.0
    print(f"\n{'=' * 60}")
    print(f"  MIX COMPLETE")
    print(f"  Duration: {elapsed_total:.0f} minutes")
    print(f"  Actions: {actions_taken}")
    print(f"  Avg action interval: {elapsed_total / max(actions_taken, 1):.1f} min")
    print(f"{'=' * 60}")

    # Fade out
    print("\n[FADEOUT] Gradually lowering volumes...")
    for step in range(10):
        t = 1.0 - (step / 9)
        for tr in ALL_TRACKS:
            udp("set_track_volume", {"track_index": tr, "volume": t * 0.7})
        time.sleep(2)
    tcp("stop_playback")
    print("[DONE] Playback stopped. Goodbye!")


if __name__ == "__main__":
    main()
