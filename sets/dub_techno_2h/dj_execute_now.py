#!/usr/bin/env python3
"""Execute DJ commands immediately - proper MCP protocol format."""

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
    response = sock.recv(8192).decode()
    return json.loads(response)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10.0)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")
    print()

    # ===== INITIAL COMMANDS FROM USER =====
    print(">>> EXECUTING INITIAL COMMANDS <<<")

    # fire_clip track_index=1 clip_index=6
    print("fire_clip(track=1, clip=6)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 6})
    print(f"  Result: {result}")

    # set_track_volume track_index=1 volume=0.90
    print("set_track_volume(track=1, vol=0.90)...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.90})
    print(f"  Result: {result}")

    # fire_clip track_index=4 clip_index=3
    print("fire_clip(track=4, clip=3)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 3})
    print(f"  Result: {result}")

    # fire_clip track_index=2 clip_index=1
    print("fire_clip(track=2, clip=1)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 1})
    print(f"  Result: {result}")

    print()
    print(">>> INITIAL COMMANDS COMPLETE <<<")
    print()

    # ===== EVOLUTION CYCLE 1 (Variation 18) =====
    print(">>> EVOLUTION CYCLE 1 - Variation 18 <<<")

    # Bass: volume 0.85-0.95 (main focus)
    print("Bass evolution...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.88})
    print(f"  Bass volume 0.88: {result}")

    # Hats
    print("Hats evolution...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.52})
    print(f"  Hats volume 0.52: {result}")

    # Stabs: fixed at 0.45
    print("Stabs (fixed)...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
    print(f"  Stabs volume 0.45: {result}")

    print()
    print(">>> EVOLUTION CYCLE 2 - Variation 19 <<<")

    # Continue evolving bass
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
    print(f"  Bass volume 0.92: {result}")

    # Maybe switch hats clip
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": 3})
    print(f"  Hats clip 3: {result}")

    # Lead max 0.5
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.42})
    print(f"  Lead volume 0.42: {result}")

    sock.close()
    print()
    print("=" * 60)
    print("MIX EVOLVING - Variation now at 19")
    print("=" * 60)


if __name__ == "__main__":
    main()
