#!/usr/bin/env python3
"""Continue evolving the DJ mix - Variations 20-25."""

import socket
import json
import time
import random

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(sock, command_type: str, params: dict = None) -> dict:
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

    variation = 20

    # Track mapping based on previous results:
    # 1 = Sub-Bass (main focus, 0.85-0.95)
    # 2 = Dub Hats
    # 3 = Percs (Lead, max 0.5)
    # 4 = Atmo Pad (Stabs, 0.45 fixed)
    # 5+ = other tracks

    print("=" * 60)
    print("CONTINUOUS MIX EVOLUTION")
    print("=" * 60)

    for cycle in range(6):  # Variations 20-25
        print(f"\n--- Variation {variation} ---")

        # Bass: always evolve (0.85-0.95)
        bass_vol = round(random.uniform(0.85, 0.95), 2)
        result = send_tcp(
            sock, "set_track_volume", {"track_index": 1, "volume": bass_vol}
        )
        print(f"  Bass vol: {bass_vol}")

        # Hats: moderate changes
        if random.random() < 0.6:
            hats_vol = round(random.uniform(0.45, 0.60), 2)
            result = send_tcp(
                sock, "set_track_volume", {"track_index": 2, "volume": hats_vol}
            )
            print(f"  Hats vol: {hats_vol}")

        # Lead/Percs: max 0.5
        if random.random() < 0.4:
            lead_vol = round(random.uniform(0.35, 0.50), 2)
            result = send_tcp(
                sock, "set_track_volume", {"track_index": 3, "volume": lead_vol}
            )
            print(f"  Lead vol: {lead_vol}")

        # Stabs: rarely change, fixed at 0.45
        if random.random() < 0.15:
            result = send_tcp(
                sock, "set_track_volume", {"track_index": 4, "volume": 0.45}
            )
            print(f"  Stabs vol: 0.45 (rare)")

        # Occasionally switch clips
        if random.random() < 0.2:
            clip = random.choice([0, 2, 4, 5, 6, 7])
            result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": clip})
            print(f"  Hats -> clip {clip}")

        if random.random() < 0.1:
            clip = random.choice([4, 5, 6, 7])
            result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": clip})
            print(f"  Bass -> clip {clip}")

        # Every 4th variation: bigger change
        if variation % 4 == 0:
            print("  *** BIG CHANGE ***")
            # Switch pad/stab clip
            clip = random.choice([0, 1, 2, 3])
            result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": clip})
            print(f"  Pad -> clip {clip}")

        variation += 1
        time.sleep(0.5)  # Small delay between variations

    sock.close()
    print()
    print("=" * 60)
    print(f"Evolution complete - now at Variation {variation}")
    print("=" * 60)


if __name__ == "__main__":
    main()
