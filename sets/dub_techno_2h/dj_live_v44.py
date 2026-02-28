#!/usr/bin/env python3
"""DJ Live Mix - Variation 44"""

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
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")

    # === INITIAL COMMANDS ===
    print("\n=== Executing Initial Commands ===")

    # Bass volume 0.88
    print("Setting track 1 volume to 0.88...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.88})
    print(f"  Result: {result}")

    # Fire lead clip
    print("Firing clip track 6, clip 1...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 1})
    print(f"  Result: {result}")

    # Fire stab clip
    print("Firing clip track 4, clip 3...")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 3})
    print(f"  Result: {result}")

    # Bass volume up to 0.92
    print("Setting track 1 volume to 0.92...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
    print(f"  Result: {result}")

    # Lead volume 0.42
    print("Setting track 6 volume to 0.42...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 6, "volume": 0.42})
    print(f"  Result: {result}")

    # === EVOLUTION LOOP ===
    print("\n=== Continuing Mix Evolution ===")

    # Rules:
    # - Bass (track 1): Volume 0.85-0.95 (main focus)
    # - Lead (track 6): Max volume 0.5
    # - Stabs (track 4): Volume 0.45, change rarely
    # - Evolve all patterns over time

    evolution_steps = [
        # Step 1: Bass swell
        {
            "cmd": "set_track_volume",
            "params": {"track_index": 1, "volume": 0.94},
            "desc": "Bass swell up",
        },
        {
            "cmd": "set_device_parameter",
            "params": {
                "track_index": 1,
                "device_index": 0,
                "parameter_index": 10,
                "value": 0.55,
            },
            "desc": "Bass filter open",
        },
        # Step 2: Lead texture
        {
            "cmd": "set_track_volume",
            "params": {"track_index": 6, "volume": 0.38},
            "desc": "Lead pull back",
        },
        {
            "cmd": "set_device_parameter",
            "params": {
                "track_index": 6,
                "device_index": 0,
                "parameter_index": 1,
                "value": 0.52,
            },
            "desc": "Lead filter adjust",
        },
        # Step 3: Stabs subtle
        {
            "cmd": "set_track_volume",
            "params": {"track_index": 4, "volume": 0.45},
            "desc": "Stabs level set",
        },
        # Step 4: Bass drive
        {
            "cmd": "set_device_parameter",
            "params": {
                "track_index": 1,
                "device_index": 0,
                "parameter_index": 12,
                "value": 0.35,
            },
            "desc": "Bass drive add",
        },
        # Step 5: Lead space
        {
            "cmd": "set_device_parameter",
            "params": {
                "track_index": 6,
                "device_index": 0,
                "parameter_index": 8,
                "value": 0.45,
            },
            "desc": "Lead reverb",
        },
        # Step 6: Bass return
        {
            "cmd": "set_track_volume",
            "params": {"track_index": 1, "volume": 0.90},
            "desc": "Bass settle",
        },
        {
            "cmd": "set_device_parameter",
            "params": {
                "track_index": 1,
                "device_index": 0,
                "parameter_index": 10,
                "value": 0.45,
            },
            "desc": "Bass filter close",
        },
        # Step 7: Lead emerge
        {
            "cmd": "set_track_volume",
            "params": {"track_index": 6, "volume": 0.45},
            "desc": "Lead emerge",
        },
        # Step 8: Bass focus
        {
            "cmd": "set_track_volume",
            "params": {"track_index": 1, "volume": 0.93},
            "desc": "Bass focus return",
        },
    ]

    for i, step in enumerate(evolution_steps):
        print(f"\nEvolution step {i + 1}/{len(evolution_steps)}: {step['desc']}")
        result = send_tcp(sock, step["cmd"], step["params"])
        print(f"  Result: {result}")
        time.sleep(2)  # 2 seconds between changes for breathing room

    print("\n=== Mix Evolution Complete ===")
    sock.close()


if __name__ == "__main__":
    main()
