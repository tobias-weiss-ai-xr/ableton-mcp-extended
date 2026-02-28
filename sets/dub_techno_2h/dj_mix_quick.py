#!/usr/bin/env python3
"""
DJ Mix - Execute initial commands and a few evolution cycles
"""

import socket
import time
import random
import json

TCP_HOST = "127.0.0.1"
TCP_PORT = 9877


def send_tcp_command(command: str, params: dict = None) -> dict:
    """Send command to MCP server via TCP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)
            sock.connect((TCP_HOST, TCP_PORT))

            if params:
                message = f"{command} {json.dumps(params)}"
            else:
                message = command

            sock.sendall((message + "\n").encode())
            response = sock.recv(4096).decode().strip()

            try:
                return json.loads(response)
            except:
                return {"raw": response}
    except Exception as e:
        return {"error": str(e)}


def fire_clip(track_index: int, clip_index: int):
    result = send_tcp_command(
        "fire_clip", {"track_index": track_index, "clip_index": clip_index}
    )
    print(f"  fire_clip(track={track_index}, clip={clip_index}) -> {result}")
    return result


def set_track_volume(track_index: int, volume: float):
    result = send_tcp_command(
        "set_track_volume", {"track_index": track_index, "volume": volume}
    )
    print(f"  set_track_volume(track={track_index}, vol={volume:.2f}) -> {result}")
    return result


def set_device_parameter(
    track_index: int, device_index: int, parameter_index: int, value: float
):
    result = send_tcp_command(
        "set_device_parameter",
        {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "value": value,
        },
    )
    return result


print("=" * 60)
print("DJ MIX - EXECUTING COMMANDS")
print("=" * 60)
print()

# ===== INITIAL COMMANDS FROM USER =====
print(">>> INITIAL COMMANDS <<<")

# fire_clip track_index=1 clip_index=6
fire_clip(1, 6)

# set_track_volume track_index=1 volume=0.90
set_track_volume(1, 0.90)

# fire_clip track_index=4 clip_index=3
fire_clip(4, 3)

# fire_clip track_index=2 clip_index=1
fire_clip(2, 1)

print()
print(">>> INITIAL COMMANDS COMPLETE <<<")
print()

# ===== FIRST EVOLUTION CYCLE =====
print(">>> EVOLUTION CYCLE 1 (Variation 18) <<<")

# Evolve bass (main focus, 0.85-0.95)
set_track_volume(1, 0.88)
set_device_parameter(1, 0, 10, 0.45)  # Bass filter
print("  Bass: volume=0.88, filter=0.45")

# Evolve hats
set_track_volume(2, 0.52)
set_device_parameter(2, 0, 2, 0.55)
print("  Hats: volume=0.52, filter=0.55")

# Keep stabs at 0.45
set_track_volume(4, 0.45)
print("  Stabs: volume=0.45 (fixed)")

print()
print(">>> EVOLUTION CYCLE 2 (Variation 19) <<<")

# Continue evolving
set_track_volume(1, 0.92)
set_device_parameter(1, 0, 10, 0.50)
print("  Bass: volume=0.92, filter=0.50")

set_track_volume(2, 0.48)
print("  Hats: volume=0.48")

# Maybe fire new hat clip
fire_clip(2, 3)

print()
print("=" * 60)
print("MIX EVOLVING - Script complete, mix continues in Ableton")
print("Variation now at: 19")
print("=" * 60)
