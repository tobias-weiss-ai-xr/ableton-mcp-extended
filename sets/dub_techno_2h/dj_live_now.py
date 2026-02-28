#!/usr/bin/env python3
"""Live DJ execution - Variation 18 -> 19 -> 20"""

import socket
import json
import time
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
    sock.settimeout(10.0)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")
    print()

    # ===== USER COMMANDS =====
    print(">>> EXECUTING USER COMMANDS <<<")

    # set_master_volume volume=0.82
    print("set_master_volume(0.82)...")
    result = send_tcp(sock, "set_master_volume", {"volume": 0.82})
    print(f"  Result: {result}")

    # fire_clip track_index=6 clip_index=5
    print("fire_clip(track=6, clip=5)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 5})
    print(f"  Result: {result}")

    # set_track_volume track_index=2 volume=0.55 -> 0.60 (evolution)
    print("set_track_volume(track=2, vol=0.55)...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.55})
    print(f"  Result: {result}")

    print("set_track_volume(track=2, vol=0.60)...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.60})
    print(f"  Result: {result}")

    # fire_clip track_index=4 clip_index=0
    print("fire_clip(track=4, clip=0)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 0})
    print(f"  Result: {result}")

    print()
    print(">>> USER COMMANDS COMPLETE <<<")
    print()

    # ===== EVOLUTION - Variation 18 -> 19 =====
    print(">>> EVOLUTION CYCLE 1 - Variation 19 <<<")

    # Bass: 0.85-0.95 (main focus)
    bass_vol = round(random.uniform(0.85, 0.95), 2)
    print(f"Bass volume {bass_vol}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
    print(f"  Result: {result}")

    # Lead: max 0.5
    lead_vol = round(random.uniform(0.35, 0.50), 2)
    print(f"Lead volume {lead_vol}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
    print(f"  Result: {result}")

    # Stabs: 0.45 (fixed, rarely change)
    print("Stabs volume 0.45...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
    print(f"  Result: {result}")

    print()
    print(">>> EVOLUTION CYCLE 2 - Variation 20 <<<")

    # Continue evolving bass
    bass_vol = round(random.uniform(0.85, 0.95), 2)
    print(f"Bass volume {bass_vol}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
    print(f"  Result: {result}")

    # Evolve hats/hihats
    hats_vol = round(random.uniform(0.50, 0.65), 2)
    print(f"Hats volume {hats_vol}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": hats_vol})
    print(f"  Result: {result}")

    # Maybe switch pads clip
    print("fire_clip(track=6, clip=2)...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 2})
    print(f"  Result: {result}")

    # FX track subtle
    fx_vol = round(random.uniform(0.30, 0.45), 2)
    print(f"FX volume {fx_vol}...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 5, "volume": fx_vol})
    print(f"  Result: {result}")

    sock.close()
    print()
    print("=" * 60)
    print("MIX EVOLVING - Variation now at 20")
    print("Bass: PUNCHY | Lead: SUBTLE | Stabs: FIXED")
    print("=" * 60)


if __name__ == "__main__":
    main()
