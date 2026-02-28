#!/usr/bin/env python3
"""DJ Live Performance - Variation 53
Execute user commands and continue evolving the mix.
Rules:
- Bass: Volume 0.85-0.95 (main focus)
- Lead: Max volume 0.5
- Stabs: Volume 0.45, change rarely
- Evolve all patterns over time
"""

import socket
import json
import random

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(sock, command_type: str, params: dict = None) -> dict:
    """Send command via TCP and wait for response."""
    message = {"type": command_type}
    if params:
        message["params"] = params

    sock.send(json.dumps(message).encode() + b"\n")
    response = sock.recv(8192).decode()
    return json.loads(response)


def get_device_parameters(sock, track_index: int, device_index: int = 0) -> dict:
    """Get parameters for a track's device."""
    return send_tcp(
        sock,
        "get_device_parameters",
        {"track_index": track_index, "device_index": device_index},
    )


def set_device_parameter(
    sock, track_index: int, device_index: int, parameter_index: int, value: float
) -> dict:
    """Set a device parameter."""
    return send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "value": value,
        },
    )


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"[DJ] DJ LIVE V53 - Connected to {TCP_HOST}:{TCP_PORT}")

    # Execute user's commands
    print("\n>> EXECUTING USER COMMANDS:")

    # 1. Set track 6 volume to 0.45 (Stabs)
    print("  -> Set Track 6 (Stabs) volume to 0.45")
    result = send_tcp(sock, "set_track_volume", {"track_index": 6, "volume": 0.45})
    print(f"    Result: {result.get('status', 'unknown')}")

    # 2. Fire clip track 4, clip 0
    print("  -> Fire Clip Track 4, Clip 0")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 0})
    print(f"    Result: {result.get('status', 'unknown')}")

    # 3. Fire clip track 4, clip 1
    print("  -> Fire Clip Track 4, Clip 1")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 1})
    print(f"    Result: {result.get('status', 'unknown')}")

    print("\n[MIX] CONTINUING MIX EVOLUTION (Variation 52+):")

    # Bass track (assuming track 1) - keep it prominent
    print("\n  [BASS] Track 1:")
    bass_volume = random.uniform(0.88, 0.92)
    print(f"    -> Set volume to {bass_volume:.2f} (main focus)")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 1, "volume": bass_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Get bass device parameters and adjust filter
    params = get_device_parameters(sock, track_index=1, device_index=0)
    if params.get("status") == "success" and "parameters" in params:
        # Find filter cutoff parameter (usually around index 10 for bass)
        filter_cutoff = random.uniform(0.4, 0.6)
        print(f"    -> Adjust filter cutoff to {filter_cutoff:.2f}")
        result = set_device_parameter(sock, 1, 0, 10, filter_cutoff)
        print(f"      Result: {result.get('status', 'unknown')}")

    # Lead track (assuming track 2 or 3) - keep it controlled
    print("\n  [LEAD] Track 2:")
    lead_volume = random.uniform(0.4, 0.5)  # Max 0.5 as per rules
    print(f"    -> Set volume to {lead_volume:.2f} (max 0.5)")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 2, "volume": lead_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Adjust lead filter for movement
    params = get_device_parameters(sock, track_index=2, device_index=0)
    if params.get("status") == "success" and "parameters" in params:
        filter_value = random.uniform(0.3, 0.7)
        print(f"    -> Adjust filter to {filter_value:.2f}")
        result = set_device_parameter(sock, 2, 0, 1, filter_value)
        print(f"      Result: {result.get('status', 'unknown')}")

    # Stabs track (track 6) - already set to 0.45, adjust filter occasionally
    if random.random() < 0.3:  # Only 30% chance to change (change rarely)
        print("\n  [STABS] Track 6:")
        print("    -> Volume already at 0.45 (change rarely)")
        params = get_device_parameters(sock, track_index=6, device_index=0)
        if params.get("status") == "success" and "parameters" in params:
            filter_value = random.uniform(0.4, 0.6)
            print(f"    -> Adjust filter to {filter_value:.2f}")
            result = set_device_parameter(sock, 6, 0, 1, filter_value)
            print(f"      Result: {result.get('status', 'unknown')}")

    # Drums (track 0) - evolve the pattern
    print("\n  [DRUMS] Track 0:")
    params = get_device_parameters(sock, track_index=0, device_index=0)
    if params.get("status") == "success" and "parameters" in params:
        # Adjust filter cutoff (index 2)
        drum_filter = random.uniform(0.5, 0.8)
        print(f"    -> Set filter to {drum_filter:.2f}")
        result = set_device_parameter(sock, 0, 0, 2, drum_filter)
        print(f"      Result: {result.get('status', 'unknown')}")

        # Adjust reverb (index 8)
        reverb = random.uniform(0.1, 0.3)
        print(f"    -> Set reverb to {reverb:.2f}")
        result = set_device_parameter(sock, 0, 0, 8, reverb)
        print(f"      Result: {result.get('status', 'unknown')}")

    # Pad/Atmosphere (track 5 or similar)
    print("\n  [PAD/ATMOSPHERE] Track 5:")
    params = get_device_parameters(sock, track_index=5, device_index=0)
    if params.get("status") == "success" and "parameters" in params:
        # Adjust filter
        pad_filter = random.uniform(0.3, 0.6)
        print(f"    -> Set filter to {pad_filter:.2f}")
        result = set_device_parameter(sock, 5, 0, 1, pad_filter)
        print(f"      Result: {result.get('status', 'unknown')}")

        # Adjust mod/space
        mod = random.uniform(0.2, 0.5)
        print(f"    -> Set mod to {mod:.2f}")
        result = set_device_parameter(sock, 5, 0, 7, mod)
        print(f"      Result: {result.get('status', 'unknown')}")

    print("\n[OK] Mix evolution complete - Variation 52+")
    print("[INFO] Bass is prominent (0.88-0.92)")
    print("[INFO] Lead controlled (max 0.5)")
    print("[INFO] Stabs at 0.45 (changed rarely)")
    print("[INFO] All patterns evolving...")

    sock.close()


if __name__ == "__main__":
    main()
