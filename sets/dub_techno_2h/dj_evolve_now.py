#!/usr/bin/env python3
"""Execute DJ commands and continue evolving the mix - Variation 24."""

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


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")

    # === EXECUTE USER'S COMMANDS ===
    print("\n=== Executing requested volume commands ===")

    print("Setting track 1 volume to 0.92 (bass focus)...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
    print(f"  Result: {result}")

    print("Setting track 2 volume to 0.55...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.55})
    print(f"  Result: {result}")

    print("Setting track 2 volume to 0.60...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.60})
    print(f"  Result: {result}")

    # === CONTINUE EVOLVING THE MIX ===
    print("\n=== Evolving the mix (Variation 24+) ===")

    # Variation 25: Slight bass adjustment (keep in 0.85-0.95 range)
    bass_vol = random.uniform(0.88, 0.94)
    print(f"Variation 25: Bass volume to {bass_vol:.2f}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
    print(f"  Result: {result}")

    # Variation 26: Evolve lead elements (max 0.5)
    lead_vol = random.uniform(0.35, 0.50)
    print(f"Variation 26: Lead volume to {lead_vol:.2f}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
    print(f"  Result: {result}")

    # Variation 27: Stabs stay at 0.45 (change rarely - skip this time)
    print("Variation 27: Stabs holding at 0.45 (rarely changed)")

    # Variation 28: Bass back to strong position
    bass_vol = random.uniform(0.90, 0.95)
    print(f"Variation 28: Bass emphasis to {bass_vol:.2f}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
    print(f"  Result: {result}")

    # Variation 29: Subtle lead movement
    lead_vol = random.uniform(0.40, 0.48)
    print(f"Variation 29: Lead subtle movement to {lead_vol:.2f}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
    print(f"  Result: {result}")

    # Variation 30: Filter sweep on drums for texture
    print("Variation 30: Adding texture with filter adjustments...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 2,  # Filter cutoff
            "value": random.uniform(0.45, 0.65),
        },
    )
    print(f"  Drums filter: {result}")

    # Variation 31: Bass filter movement
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 10,  # Bass filter
            "value": random.uniform(0.35, 0.55),
        },
    )
    print(f"  Bass filter: {result}")

    # Variation 32: Pad space
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 2,
            "device_index": 0,
            "parameter_index": 1,  # Pad filter
            "value": random.uniform(0.40, 0.60),
        },
    )
    print(f"  Pad filter: {result}")

    sock.close()
    print("\n=== Mix evolution complete! Current variation: 32 ===")


if __name__ == "__main__":
    main()
