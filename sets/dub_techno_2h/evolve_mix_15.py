#!/usr/bin/env python3
"""Continue evolving - Variation 15 (Peak Return)."""

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
    print("=== EVOLVING MIX - VARIATION 15 (PEAK RETURN) ===\n")

    # 1. Bass - push to upper limit
    print("1. Bass to upper limit...")
    send_udp("set_track_volume", {"track_index": 1, "volume": 0.95})
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 6})
    print(f"   Bass: {result}")

    # 2. Kick - peak pattern
    print("2. Kick peak...")
    result = send_tcp(sock, "fire_clip", {"track_index": 0, "clip_index": 6})
    print(f"   Kick: {result}")

    # 3. Lead pad - keep under 0.5, filter up
    print("3. Lead pad peak...")
    send_udp("set_track_volume", {"track_index": 6, "volume": 0.48})
    send_udp(
        "set_device_parameter",
        {"track_index": 6, "device_index": 0, "parameter_index": 2, "value": 0.65},
    )

    # 4. Hats - full energy
    print("4. Hats full energy...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 5})
    print(f"   Hats: {result}")

    # 5. Percussion - full
    print("5. Percussion full...")
    send_udp("set_track_volume", {"track_index": 3, "volume": 0.52})
    result = send_tcp(sock, "fire_clip", {"track_index": 3, "clip_index": 5})
    print(f"   Perc: {result}")

    # 6. Stabs - restore to target 0.45 (rare change, but back to target)
    print("6. Stabs restored to target...")
    send_udp("set_track_volume", {"track_index": 7, "volume": 0.45})
    result = send_tcp(sock, "fire_clip", {"track_index": 7, "clip_index": 4})
    print(f"   Stabs: {result}")

    # 7. Atmo - supporting role
    print("7. Atmo support...")
    send_udp("set_track_volume", {"track_index": 4, "volume": 0.50})

    # 8. Dub FX - subtle
    print("8. Dub FX subtle...")
    send_udp("set_track_volume", {"track_index": 5, "volume": 0.48})

    print("\n=== MIX EVOLVED TO VARIATION 15 (PEAK RETURN) ===")
    print("Bass: 0.95 | Lead: 0.48 | Stabs: 0.45")
    print("\nAll volumes within target ranges:")
    print("- Bass: 0.85-0.95 ✓")
    print("- Lead: max 0.5 ✓")
    print("- Stabs: 0.45 ✓")

    sock.close()


if __name__ == "__main__":
    main()
