#!/usr/bin/env python3
"""Dub-style evolution with builds and drops - Variations 36-50."""

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

    variation = 36

    print("=" * 60)
    print("DUB EVOLUTION - Variations 36-50")
    print("Building tension, dropping into space...")
    print("=" * 60)

    for cycle in range(15):
        print(f"\n--- Variation {variation} ---")

        # === BASS: Always main focus (0.85-0.95) ===
        bass_vol = round(random.uniform(0.85, 0.95), 2)
        send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
        print(f"  Bass vol: {bass_vol}")

        # === HATS: 0.4-0.6 ===
        if random.random() < 0.5:
            hats_vol = round(random.uniform(0.40, 0.58), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": hats_vol})
            print(f"  Hats vol: {hats_vol}")

        # === LEAD: max 0.5 ===
        if random.random() < 0.3:
            lead_vol = round(random.uniform(0.30, 0.50), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
            print(f"  Lead vol: {lead_vol}")

        # === STABS: fixed at 0.45, very rare changes ===
        if random.random() < 0.08:
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
            print(f"  Stabs vol: 0.45 (rare)")

        # === DUB DROP at variation 40 ===
        if variation == 40:
            print("  *** DUB DROP ***")
            # Drop everything down
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.70})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.30})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.25})
            print("  All elements dropped for space...")

        # === REBUILD after drop (41-43) ===
        if variation == 41:
            print("  *** REBUILD PHASE 1 ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.82})
            print("  Bass returning...")

        if variation == 42:
            print("  *** REBUILD PHASE 2 ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.88})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.45})
            print("  Bass + Hats returning...")

        if variation == 43:
            print("  *** REBUILD COMPLETE ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.52})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.40})
            print("  Full energy restored!")

        # === BUILD at variation 48 ===
        if variation == 48:
            print("  *** ENERGY BUILD ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.58})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.48})
            print("  Maximum energy!")

        # === Clip switching ===
        # Hats
        if random.random() < 0.15:
            clip = random.choice([0, 1, 2, 3, 4, 5])
            send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": clip})
            print(f"  Hats -> clip {clip}")

        # Bass
        if random.random() < 0.10:
            clip = random.choice([4, 5, 6, 7])
            send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": clip})
            print(f"  Bass -> clip {clip}")

        # Section changes
        if variation % 5 == 0 and variation not in [40, 45]:
            print("  *** SECTION ***")
            clip = random.choice([0, 1, 2, 3])
            send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": clip})
            print(f"  Pad -> clip {clip}")

        variation += 1
        time.sleep(0.25)

    sock.close()
    print()
    print("=" * 60)
    print(f"Dub evolution complete - now at Variation {variation}")
    print("Bass is the foundation, everything evolves around it")
    print("=" * 60)


if __name__ == "__main__":
    main()
