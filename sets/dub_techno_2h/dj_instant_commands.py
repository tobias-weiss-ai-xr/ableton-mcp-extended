#!/usr/bin/env python3
"""Execute DJ commands and continue evolving the mix."""

import socket
import json
import random
import time

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

    # Execute the requested clip fires
    print("\n=== FIRING CLIPS ===")

    print("1. Firing clip track 1, clip 5 (Bass)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 5})
    print(f"   Result: {result}")

    print("2. Firing clip track 6, clip 0...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 0})
    print(f"   Result: {result}")

    print("3. Firing clip track 6, clip 4...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 4})
    print(f"   Result: {result}")

    # Apply volume rules
    print("\n=== APPLYING VOLUME RULES ===")

    # Bass (track 1): 0.85-0.95
    bass_volume = random.uniform(0.85, 0.95)
    print(f"Setting Bass (track 1) volume to {bass_volume:.2f}...")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 1, "volume": bass_volume}
    )
    print(f"   Result: {result}")

    # Lead (track 6?): Max 0.5
    lead_volume = random.uniform(0.35, 0.50)
    print(f"Setting Lead (track 6) volume to {lead_volume:.2f}...")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 6, "volume": lead_volume}
    )
    print(f"   Result: {result}")

    # Continue evolving - apply filter sweeps and parameter changes
    print('\n=== EVOLVING MIX (Variation 60") ===')

    # Get current device parameters for drums (track 0)
    print("Getting drums parameters...")
    result = send_tcp(
        sock, "get_device_parameters", {"track_index": 0, "device_index": 0}
    )
    print(
        f"   Drums params available: {len(result.get('result', {}).get('parameters', []))} params"
    )

    # Apply filter sweep to drums
    drums_filter = random.uniform(0.4, 0.7)
    print(f"Setting drums filter cutoff to {drums_filter:.2f}...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 2,  # Filter cutoff
            "value": drums_filter,
        },
    )
    print(f"   Result: {result}")

    # Apply reverb to drums
    drums_reverb = random.uniform(0.2, 0.5)
    print(f"Setting drums reverb to {drums_reverb:.2f}...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 8,  # Reverb
            "value": drums_reverb,
        },
    )
    print(f"   Result: {result}")

    # Bass filter evolution
    bass_filter = random.uniform(0.3, 0.6)
    print(f"Setting bass filter to {bass_filter:.2f}...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 10,  # Filter cutoff
            "value": bass_filter,
        },
    )
    print(f"   Result: {result}")

    # Pad/keys filter evolution (track 2 or 3)
    pad_filter = random.uniform(0.4, 0.8)
    print(f"Setting pad filter to {pad_filter:.2f}...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 2,
            "device_index": 0,
            "parameter_index": 1,  # Filter cutoff
            "value": pad_filter,
        },
    )
    print(f"   Result: {result}")

    sock.close()
    print("\n=== DJ COMMANDS COMPLETE ===")
    print("Mix is evolving. Bass is prominent, lead is subtle, stabs are minimal.")


if __name__ == "__main__":
    main()
