#!/usr/bin/env python3
"""Continue evolving - Variation 13 (Breakdown begins)."""

import socket
import json

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(sock, command_type: str, params: dict = None) -> dict:
    message = {"type": command_type}
    if params:
        message["params"] = params
    sock.send(json.dumps(message).encode() + b"\n")
    response = sock.recv(8192).decode()
    return json.loads(response)


def send_udp(command_type: str, params: dict):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = {"type": command_type, "params": params}
    sock.sendto(json.dumps(message).encode(), (TCP_HOST, 9878))
    sock.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print("=== EVOLVING MIX - VARIATION 13 (BREAKDOWN) ===\n")

    # 1. Bass - pull back slightly but keep focus
    print("1. Bass pullback...")
    send_udp("set_track_volume", {"track_index": 1, "volume": 0.88})

    # 2. Kick - sparse pattern
    print("2. Kick sparse...")
    result = send_tcp(sock, "fire_clip", {"track_index": 0, "clip_index": 0})
    print(f"   Kick: {result}")

    # 3. Lead pad - drop down, create space
    print("3. Lead pad space...")
    send_udp("set_track_volume", {"track_index": 6, "volume": 0.35})
    send_udp(
        "set_device_parameter",
        {
            "track_index": 6,
            "device_index": 0,
            "parameter_index": 2,
            "value": 0.4,  # Filter down for muffled sound
        },
    )

    # 4. Hats - minimal
    print("4. Hats minimal...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 0})
    print(f"   Hats: {result}")

    # 5. Percussion - drop out
    print("5. Percussion drop...")
    send_udp("set_track_volume", {"track_index": 3, "volume": 0.3})

    # 6. Stabs - bring in for breakdown atmosphere (rare change)
    print("6. Stabs breakdown texture...")
    result = send_tcp(sock, "fire_clip", {"track_index": 7, "clip_index": 3})
    print(f"   Stabs: {result}")
    send_udp("set_track_volume", {"track_index": 7, "volume": 0.40})

    # 7. Atmo pad - swell up for atmosphere
    print("7. Atmo swell...")
    send_udp("set_track_volume", {"track_index": 4, "volume": 0.65})
    send_udp(
        "set_device_parameter",
        {"track_index": 4, "device_index": 0, "parameter_index": 2, "value": 0.5},
    )

    # 8. Dub FX - more prominent in breakdown
    print("8. Dub FX up...")
    send_udp("set_track_volume", {"track_index": 5, "volume": 0.58})

    print("\n=== MIX EVOLVED TO VARIATION 13 (BREAKDOWN) ===")
    print("Bass: 0.88 | Lead: 0.35 | Stabs: 0.40")

    sock.close()


if __name__ == "__main__":
    main()
