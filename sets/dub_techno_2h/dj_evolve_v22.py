#!/usr/bin/env python3
"""Continue evolving the DJ mix - variation 22."""

import socket
import json
import time
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


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")
    print("=== Variation 22 - Evolving Mix ===\n")

    # Bass should be main focus (0.85-0.95)
    # Track 1 is Sub-Bass based on previous output
    bass_volume = 0.92  # High in range for main focus
    print(f"Setting Bass (track 1) volume to {bass_volume}...")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 1, "volume": bass_volume}
    )
    print(f"  Result: {result}")

    # Lead tracks - max 0.5
    # Assuming track 6 or 7 might be lead based on dub techno structure
    lead_volume = 0.45  # Just under max
    print(f"Setting Lead (track 6) volume to {lead_volume}...")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 6, "volume": lead_volume}
    )
    print(f"  Result: {result}")

    # Stabs - 0.45, change rarely
    # Track 4 might be stabs/pads
    stabs_volume = 0.45
    print(f"Setting Stabs (track 4) volume to {stabs_volume}...")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 4, "volume": stabs_volume}
    )
    print(f"  Result: {result}")

    # Evolve device parameters on key tracks
    # Drums filter sweep - track 0
    print("\nEvolving device parameters...")

    # Drums - open filter slightly (0.5 -> 0.65)
    print("Opening drums filter...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 2,  # Filter cutoff
            "value": 0.65,
        },
    )
    print(f"  Result: {result}")

    # Bass - slight filter tweak (keep it focused)
    print("Tweaking bass filter...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 10,  # Filter cutoff
            "value": 0.55,
        },
    )
    print(f"  Result: {result}")

    # Pad - add some space/reverb feel
    print("Adding space to pad...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 7,
            "device_index": 0,
            "parameter_index": 8,  # Reverb/Space
            "value": 0.45,
        },
    )
    print(f"  Result: {result}")

    # Keys - slight echo
    print("Adding echo to keys...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 6,
            "device_index": 0,
            "parameter_index": 3,  # Echo
            "value": 0.35,
        },
    )
    print(f"  Result: {result}")

    sock.close()
    print("\n=== Mix evolved successfully! ===")
    print("Current state:")
    print("  - Bass: 0.92 (main focus)")
    print("  - Lead: 0.45 (under max)")
    print("  - Stabs: 0.45 (stable)")
    print("  - Filters opening for build")


if __name__ == "__main__":
    main()
