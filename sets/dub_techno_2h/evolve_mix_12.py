#!/usr/bin/env python3
"""Continue evolving - Variation 12."""

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
    print("=== EVOLVING MIX - VARIATION 12 ===\n")

    # 1. Bass - push to upper limit for peak energy
    print("1. Bass to peak...")
    send_udp("set_track_volume", {"track_index": 1, "volume": 0.94})

    # 2. New bass pattern
    print("2. Bass pattern peak...")
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 4})
    print(f"   Bass: {result}")

    # 3. Kick pattern
    print("3. Kick peak pattern...")
    result = send_tcp(sock, "fire_clip", {"track_index": 0, "clip_index": 4})
    print(f"   Kick: {result}")

    # 4. Lead pad - subtle movement (keep under 0.5)
    print("4. Lead pad subtle...")
    send_udp("set_track_volume", {"track_index": 6, "volume": 0.48})
    send_udp(
        "set_device_parameter",
        {"track_index": 6, "device_index": 0, "parameter_index": 2, "value": 0.6},
    )

    # 5. Percussion build
    print("5. Percussion build...")
    result = send_tcp(sock, "fire_clip", {"track_index": 3, "clip_index": 3})
    print(f"   Perc: {result}")

    # 6. Hats driving
    print("6. Hats driving...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 3})
    print(f"   Hats: {result}")

    # 7. Stabs - NO CHANGE (change rarely)
    print("7. Stabs: holding at 0.45 (rare changes)")

    # 8. Atmo pad filter up
    print("8. Atmo filter sweep...")
    send_udp(
        "set_device_parameter",
        {"track_index": 4, "device_index": 0, "parameter_index": 2, "value": 0.7},
    )

    print("\n=== MIX EVOLVED TO VARIATION 12 ===")
    print("Bass: 0.94 | Lead: 0.48 | Stabs: 0.45")

    sock.close()


if __name__ == "__main__":
    main()
