#!/usr/bin/env python3
"""Continue evolving - Variation 14 (Return)."""

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
    print("=== EVOLVING MIX - VARIATION 14 (RETURN) ===\n")

    # 1. Bass - bring back up
    print("1. Bass return...")
    send_udp("set_track_volume", {"track_index": 1, "volume": 0.90})
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 5})
    print(f"   Bass: {result}")

    # 2. Kick - driving return
    print("2. Kick return...")
    result = send_tcp(sock, "fire_clip", {"track_index": 0, "clip_index": 5})
    print(f"   Kick: {result}")

    # 3. Lead pad - filter opening
    print("3. Lead pad opening...")
    send_udp("set_track_volume", {"track_index": 6, "volume": 0.42})
    send_udp(
        "set_device_parameter",
        {"track_index": 6, "device_index": 0, "parameter_index": 2, "value": 0.55},
    )

    # 4. Hats - driving pattern
    print("4. Hats driving return...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 4})
    print(f"   Hats: {result}")

    # 5. Percussion - bring back
    print("5. Percussion return...")
    send_udp("set_track_volume", {"track_index": 3, "volume": 0.48})
    result = send_tcp(sock, "fire_clip", {"track_index": 3, "clip_index": 4})
    print(f"   Perc: {result}")

    # 6. Stabs - hold (rare changes)
    print("6. Stabs: holding position")

    # 7. Atmo - settle
    print("7. Atmo settle...")
    send_udp("set_track_volume", {"track_index": 4, "volume": 0.55})

    # 8. Dub FX - maintain
    print("8. Dub FX maintain...")
    send_udp("set_track_volume", {"track_index": 5, "volume": 0.52})

    print("\n=== MIX EVOLVED TO VARIATION 14 (RETURN) ===")
    print("Bass: 0.90 | Lead: 0.42 | Stabs: 0.40")

    sock.close()


if __name__ == "__main__":
    main()
