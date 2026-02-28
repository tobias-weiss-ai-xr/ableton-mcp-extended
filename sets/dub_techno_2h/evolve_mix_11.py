#!/usr/bin/env python3
"""Continue evolving - Variation 11."""

import socket
import json
import time

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
    print("=== EVOLVING MIX - VARIATION 11 ===\n")

    # 1. Bass filter modulation - keep it alive
    print("1. Bass filter modulation...")
    send_udp(
        "set_device_parameter",
        {"track_index": 1, "device_index": 0, "parameter_index": 2, "value": 0.65},
    )

    # 2. New atmosphere pad texture
    print("2. Atmo pad shift...")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 2})
    print(f"   Atmo: {result}")

    # 3. Lead pad - subtle volume increase (staying under 0.5)
    print("3. Lead pad presence up...")
    send_udp("set_track_volume", {"track_index": 6, "volume": 0.45})

    # 4. Dub FX new pattern
    print("4. Dub FX variation...")
    result = send_tcp(sock, "fire_clip", {"track_index": 5, "clip_index": 1})
    print(f"   FX: {result}")

    # 5. Kick variation for energy
    print("5. Kick variation...")
    result = send_tcp(sock, "fire_clip", {"track_index": 0, "clip_index": 3})
    print(f"   Kick: {result}")

    # 6. Bass pattern switch (main focus)
    print("6. Bass pattern evolution...")
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 3})
    print(f"   Bass: {result}")
    # Ensure bass stays in target range
    send_udp("set_track_volume", {"track_index": 1, "volume": 0.91})

    # 7. Hats back to original with twist
    print("7. Hats pattern...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 2})
    print(f"   Hats: {result}")

    print("\n=== MIX EVOLVED TO VARIATION 11 ===")
    print("Bass: 0.91 | Lead: 0.45 | Stabs: 0.45")

    sock.close()


if __name__ == "__main__":
    main()
