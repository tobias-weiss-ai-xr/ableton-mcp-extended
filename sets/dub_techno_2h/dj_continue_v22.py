#!/usr/bin/env python3
"""Continue evolving DJ mix - variation 22+ with proper automation."""

import socket
import json

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(sock, command_type: str, params: dict = None) -> dict:
    """Send command via TCP and wait for response."""
    message = {"type": command_type}
    if params:
        message["params"] = params

    sock.send(json.dumps(message).encode() + b"\n")
    sock.settimeout(5.0)
    response = sock.recv(8192)
    return json.loads(response.decode())


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")
    print("=== Variation 22+ - Continued Evolution ===\n")

    # Ensure bass is at main focus level (0.85-0.95)
    print("Ensuring Bass focus...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.91})
    print(f"  Bass: {result}")

    # Slight variation on drums - Tone parameter
    print("Evolving drums tone...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 8,  # Tone
            "value": 0.55,
        },
    )
    print(f"  Drums Tone: {result}")

    # Fire a different clip on track 6 for variation
    print("Switching lead pad pattern...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 2})
    print(f"  Lead Pad: {result}")

    # Small volume adjustment on drums
    print("Adjusting drums volume...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 0, "volume": 0.72})
    print(f"  Drums: {result}")

    # Fire variation on track 4
    print("Firing atmo pad variation...")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 1})
    print(f"  Atmo Pad: {result}")

    sock.close()
    print("\n=== Mix Evolution Complete ===")
    print("Current state:")
    print("  - Bass: 0.91 (main focus)")
    print("  - Lead: 0.45 (under max)")
    print("  - Stabs/Atmo: 0.45 (stable)")
    print("  - Drums: 0.72 (driving)")
    print("  - Patterns evolving...")


if __name__ == "__main__":
    main()
