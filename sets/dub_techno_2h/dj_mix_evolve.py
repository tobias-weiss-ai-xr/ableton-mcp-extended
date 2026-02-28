#!/usr/bin/env python3
"""
DJ Mix Evolution Script - Continues the mix with evolving patterns
Executes initial commands then evolves parameters over time
"""

import socket
import time
import random
import json

# MCP Server settings
TCP_HOST = "127.0.0.1"
TCP_PORT = 9877

# Track mapping (adjust based on your session)
TRACKS = {"kick": 0, "bass": 1, "hats": 2, "lead": 3, "stabs": 4, "pad": 5, "fx": 6}

# Current state
current_variation = 17


def send_tcp_command(command: str, params: dict = None) -> dict:
    """Send command to MCP server via TCP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)
            sock.connect((TCP_HOST, TCP_PORT))

            if params:
                message = f"{command} {json.dumps(params)}"
            else:
                message = command

            sock.sendall((message + "\n").encode())
            response = sock.recv(4096).decode().strip()

            try:
                return json.loads(response)
            except:
                return {"raw": response}
    except Exception as e:
        return {"error": str(e)}


def fire_clip(track_index: int, clip_index: int):
    """Fire a clip"""
    result = send_tcp_command(
        "fire_clip", {"track_index": track_index, "clip_index": clip_index}
    )
    print(f"  fire_clip(track={track_index}, clip={clip_index}) -> {result}")
    return result


def set_track_volume(track_index: int, volume: float):
    """Set track volume (0.0-1.0 normalized)"""
    result = send_tcp_command(
        "set_track_volume", {"track_index": track_index, "volume": volume}
    )
    print(f"  set_track_volume(track={track_index}, vol={volume:.2f}) -> {result}")
    return result


def set_device_parameter(
    track_index: int, device_index: int, parameter_index: int, value: float
):
    """Set device parameter"""
    result = send_tcp_command(
        "set_device_parameter",
        {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "value": value,
        },
    )
    return result


def evolve_bass():
    """Evolve bass parameters - main focus, volume 0.85-0.95"""
    track = TRACKS["bass"]

    # Random volume adjustment within allowed range
    vol = random.uniform(0.85, 0.95)
    set_track_volume(track, vol)

    # Occasionally tweak filter (parameter 10 on bass synth)
    if random.random() < 0.3:
        filter_val = random.uniform(0.3, 0.6)
        set_device_parameter(track, 0, 10, filter_val)
        print(f"  Bass filter -> {filter_val:.2f}")


def evolve_lead():
    """Evolve lead - max volume 0.5"""
    track = TRACKS["lead"]

    # Keep volume low
    vol = random.uniform(0.3, 0.5)
    set_track_volume(track, vol)

    # Tweak filter occasionally
    if random.random() < 0.2:
        filter_val = random.uniform(0.4, 0.7)
        set_device_parameter(track, 0, 1, filter_val)
        print(f"  Lead filter -> {filter_val:.2f}")


def evolve_stabs():
    """Evolve stabs - volume 0.45, change rarely"""
    track = TRACKS["stabs"]

    # Keep volume fixed at 0.45
    set_track_volume(track, 0.45)

    # Very rarely change parameters
    if random.random() < 0.1:
        filter_val = random.uniform(0.3, 0.5)
        set_device_parameter(track, 0, 1, filter_val)
        print(f"  Stabs filter -> {filter_val:.2f}")


def evolve_hats():
    """Evolve hi-hats"""
    track = TRACKS["hats"]

    # Vary volume slightly
    vol = random.uniform(0.4, 0.6)
    set_track_volume(track, vol)

    # Often tweak decay/filter
    if random.random() < 0.5:
        filter_val = random.uniform(0.3, 0.7)
        set_device_parameter(track, 0, 2, filter_val)
        print(f"  Hats filter -> {filter_val:.2f}")


def evolve_pad():
    """Evolve pad textures"""
    track = TRACKS["pad"]

    # Subtle volume changes
    vol = random.uniform(0.35, 0.5)
    set_track_volume(track, vol)

    # Often modulate filter and space
    if random.random() < 0.4:
        filter_val = random.uniform(0.3, 0.6)
        set_device_parameter(track, 0, 1, filter_val)
        print(f"  Pad filter -> {filter_val:.2f}")


def evolve_fx():
    """Evolve FX track"""
    track = TRACKS["fx"]

    # Vary FX level
    vol = random.uniform(0.2, 0.4)
    set_track_volume(track, vol)


def maybe_switch_clip(track_name: str, clip_options: list, probability: float = 0.15):
    """Occasionally switch clips"""
    if random.random() < probability:
        track = TRACKS[track_name]
        clip = random.choice(clip_options)
        fire_clip(track, clip)
        return True
    return False


def main():
    global current_variation

    print("=" * 60)
    print("DJ MIX EVOLUTION")
    print("=" * 60)
    print(f"Starting variation: {current_variation}")
    print()

    # ===== INITIAL COMMANDS FROM USER =====
    print(">>> EXECUTING INITIAL COMMANDS <<<")

    # fire_clip track_index=1 clip_index=6
    fire_clip(1, 6)

    # set_track_volume track_index=1 volume=0.90
    set_track_volume(1, 0.90)

    # fire_clip track_index=4 clip_index=3
    fire_clip(4, 3)

    # fire_clip track_index=2 clip_index=1
    fire_clip(2, 1)

    print()
    print(">>> INITIAL COMMANDS COMPLETE - CONTINUING EVOLUTION <<<")
    print()

    # ===== CONTINUE EVOLVING =====
    cycle = 0
    while True:
        cycle += 1
        current_variation += 1

        print(f"\n--- Variation {current_variation} (Cycle {cycle}) ---")

        # Always evolve bass (main focus)
        evolve_bass()

        # Regularly evolve other elements
        evolve_hats()
        evolve_pad()

        # Occasionally evolve lead
        if random.random() < 0.3:
            evolve_lead()

        # Rarely change stabs
        if random.random() < 0.15:
            evolve_stabs()

        # Sometimes evolve FX
        if random.random() < 0.25:
            evolve_fx()

        # Occasionally switch clips
        if maybe_switch_clip("hats", [0, 1, 2, 3, 4, 5], 0.1):
            print("  Switched hats clip")

        if maybe_switch_clip("pad", [0, 1, 2, 3, 4, 5, 6, 7], 0.08):
            print("  Switched pad clip")

        if maybe_switch_clip("lead", [0, 1, 2, 3], 0.05):
            print("  Switched lead clip")

        # Every 8 variations, do a bigger change
        if current_variation % 8 == 0:
            print("\n  *** BIG CHANGE ***")
            # Switch bass pattern
            bass_clip = random.choice([4, 5, 6, 7])
            fire_clip(TRACKS["bass"], bass_clip)
            print(f"  Bass pattern -> clip {bass_clip}")

        # Every 16 variations, reset energy
        if current_variation % 16 == 0:
            print("\n  === ENERGY RESET ===")
            # Drop filters then bring back
            for track_name in ["bass", "hats", "pad"]:
                track = TRACKS[track_name]
                set_device_parameter(track, 0, 1, 0.2)  # Filter down
            print("  All filters down for buildup...")

        # Wait between variations (8-16 beats at 126 BPM ≈ 15-30 seconds)
        wait_time = random.uniform(12, 25)
        print(f"\n  Waiting {wait_time:.1f}s until next variation...")
        time.sleep(wait_time)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n>>> DJ MIX STOPPED <<<")
        print("Graceful exit.")
