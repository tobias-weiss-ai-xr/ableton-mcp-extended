#!/usr/bin/env python3
"""Continue DJ evolution - Variations 49-64."""

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

    print("\n=== Deep Hypnotic Phase (Variations 49-64) ===")

    # Hypnotic dub phase - slow, subtle movements
    print("\n--- HYPNOTIC DRIFT ---")

    # V49: Bass anchors
    print("V49: Bass anchor 0.91...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.91})

    # V50: Lead whispers
    print("V50: Lead whisper 0.38...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.38})

    # V51: Hats float
    print("V51: Hats float 0.57...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.57})

    # V52: Stabs stable (no change - rare)
    print("V52: Stabs stable at 0.44...")

    print("\n--- SUBTLE RISE ---")

    # V53: Bass grows
    print("V53: Bass grows to 0.93...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.93})

    # V54: Lead emerges
    print("V54: Lead emerges 0.42...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.42})

    # V55: Hats brighten
    print("V55: Hats brighten 0.63...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.63})

    # V56: Bass peak
    print("V56: Bass peak 0.95...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})

    print("\n--- TENSION ---")

    # V57: Lead tension
    print("V57: Lead tension 0.48...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.48})

    # V58: Hats sharp
    print("V58: Hats sharp 0.65...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.65})

    # V59: Bass holds peak
    print("V59: Bass holds 0.94...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})

    # V60: Filter sweep down
    print("V60: Filter sweep for tension...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 2, "value": 0.38},
    )

    print("\n--- RESOLUTION ---")

    # V61: Bass returns
    print("V61: Bass returns 0.92...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})

    # V62: Lead settles
    print("V62: Lead settles 0.44...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.44})

    # V63: Hats groove
    print("V63: Hats groove 0.60...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.60})

    # V64: Stabs rare change
    print("V64: Stabs shift to 0.46...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.46})

    # Final texture
    print("V64b: Final texture adjustment...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {"track_index": 1, "device_index": 0, "parameter_index": 10, "value": 0.48},
    )

    sock.close()
    print("\n=== Hypnotic phase complete! Variation 64 ===")
    print("Mix status: Bass 0.92 | Lead 0.44 | Hats 0.60 | Stabs 0.46")


if __name__ == "__main__":
    main()
