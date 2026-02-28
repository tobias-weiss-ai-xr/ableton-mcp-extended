#!/usr/bin/env python3
"""Evolve the mix - Variation 10."""

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
    """Send via UDP for fast parameter changes."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = {"type": command_type, "params": params}
    sock.sendto(json.dumps(message).encode(), (TCP_HOST, 9878))
    sock.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print("=== EVOLVING MIX - VARIATION 10 ===\n")

    # 1. Keep bass strong (Track 1) - bump to 0.93 for more presence
    print("1. Boosting bass presence...")
    send_udp("set_track_volume", {"track_index": 1, "volume": 0.93})

    # 2. Fire new kick pattern on Track 0 (variation 10 uses clip 2)
    print("2. Switching kick pattern...")
    result = send_tcp(sock, "fire_clip", {"track_index": 0, "clip_index": 2})
    print(f"   Kick: {result}")

    # 3. Bring in new bass pattern
    print("3. New bass pattern...")
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 2})
    print(f"   Bass: {result}")

    # 4. Lead pad - keep low, slight filter modulation
    print("4. Lead pad filter sweep...")
    send_udp(
        "set_device_parameter",
        {
            "track_index": 6,
            "device_index": 0,
            "parameter_index": 2,  # Filter cutoff
            "value": 0.55,
        },
    )

    # 5. Hats variation - bring new pattern
    print("5. Hats variation...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 1})
    print(f"   Hats: {result}")

    # 6. Stabs - rare change, but variation 10 calls for new stab
    print("6. New chord stab (rare change)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 7, "clip_index": 2})
    print(f"   Stabs: {result}")
    send_udp("set_track_volume", {"track_index": 7, "volume": 0.45})

    # 7. Percussion variation
    print("7. Percussion evolution...")
    result = send_tcp(sock, "fire_clip", {"track_index": 3, "clip_index": 2})
    print(f"   Perc: {result}")

    # 8. FX - dub atmosphere
    print("8. Dub FX adjustment...")
    send_udp("set_track_volume", {"track_index": 5, "volume": 0.52})

    print("\n=== MIX EVOLVED TO VARIATION 10 ===")
    print("Bass: 0.93 | Lead: 0.42 | Stabs: 0.45")

    sock.close()


if __name__ == "__main__":
    main()
