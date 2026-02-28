#!/usr/bin/env python3
"""Continue evolving - Variation 16 (Deep Journey)."""

import socket
import json

TCP_HOST = "localhost"
TCP_PORT = 9877
UDP_PORT = 9878


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
    sock.sendto(json.dumps(message).encode(), (TCP_HOST, UDP_PORT))
    sock.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print("=== EVOLVING MIX - VARIATION 16 (DEEP JOURNEY) ===\n")

    # 1. Bass - drop slightly for deeper feel (rule: 0.85-0.95)
    print("1. Bass going deeper (0.88)...")
    send_udp("set_track_volume", {"track_index": 1, "volume": 0.88})
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 7})
    print(f"   Bass: {result}")

    # 2. Kick - deeper pattern
    print("2. Kick deeper...")
    result = send_tcp(sock, "fire_clip", {"track_index": 0, "clip_index": 7})
    print(f"   Kick: {result}")

    # 3. Lead pad - keep under 0.5, close filter for mystery (rule: max 0.5)
    print("3. Lead pad closing filter for mystery...")
    send_udp("set_track_volume", {"track_index": 6, "volume": 0.42})
    send_udp(
        "set_device_parameter",
        {"track_index": 6, "device_index": 0, "parameter_index": 2, "value": 0.40},
    )

    # 4. Hats - sparse pattern for space
    print("4. Hats sparse...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 6})
    print(f"   Hats: {result}")

    # 5. Percussion - subtle
    print("5. Percussion subtle...")
    send_udp("set_track_volume", {"track_index": 3, "volume": 0.45})
    result = send_tcp(sock, "fire_clip", {"track_index": 3, "clip_index": 6})
    print(f"   Perc: {result}")

    # 6. Stabs - maintain 0.45 (rule: 0.45, change rarely)
    print("6. Stabs maintained at 0.45...")
    send_udp("set_track_volume", {"track_index": 7, "volume": 0.45})

    # 7. Atmo - increase for atmosphere
    print("7. Atmo increased...")
    send_udp("set_track_volume", {"track_index": 4, "volume": 0.55})

    # 8. Dub FX - more prominent
    print("8. Dub FX more prominent...")
    send_udp("set_track_volume", {"track_index": 5, "volume": 0.52})
    send_udp(
        "set_device_parameter",
        {"track_index": 5, "device_index": 0, "parameter_index": 8, "value": 0.50},
    )

    print("\n=== MIX EVOLVED TO VARIATION 16 (DEEP JOURNEY) ===")
    print("Bass: 0.88 | Lead: 0.42 | Stabs: 0.45 | Master: 0.85")
    print("\nAll volumes within target ranges:")
    print("- Bass: 0.85-0.95")
    print("- Lead: max 0.5")
    print("- Stabs: 0.45")

    sock.close()


if __name__ == "__main__":
    main()
