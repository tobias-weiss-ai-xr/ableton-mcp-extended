#!/usr/bin/env python3
"""Hypnotic evolution - Variations 51-70."""

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

    variation = 51

    print("=" * 60)
    print("HYPNOTIC EVOLUTION - Variations 51-70")
    print("Deep, rolling, hypnotic...")
    print("=" * 60)

    for cycle in range(20):
        print(f"\n--- Variation {variation} ---")

        # === BASS: Always main focus (0.85-0.95) ===
        bass_vol = round(random.uniform(0.86, 0.94), 2)
        send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
        print(f"  Bass vol: {bass_vol}")

        # Filter modulation on bass for hypnotic feel
        if random.random() < 0.25:
            filter_val = round(random.uniform(0.38, 0.52), 2)
            send_tcp(
                sock,
                "set_device_parameter",
                {
                    "track_index": 1,
                    "device_index": 0,
                    "parameter_index": 10,
                    "value": filter_val,
                },
            )
            print(f"  Bass filter: {filter_val}")

        # === HATS: 0.42-0.58 ===
        if random.random() < 0.45:
            hats_vol = round(random.uniform(0.42, 0.56), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": hats_vol})
            print(f"  Hats vol: {hats_vol}")

        # === LEAD: max 0.5, subtle ===
        if random.random() < 0.25:
            lead_vol = round(random.uniform(0.32, 0.48), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
            print(f"  Lead vol: {lead_vol}")

        # === STABS: 0.45 fixed, very rare ===
        if random.random() < 0.06:
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
            print(f"  Stabs vol: 0.45")

        # === MINI DROPS at 55, 62, 68 ===
        if variation in [55, 62, 68]:
            print("  *** MINI DROP ***")
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.32})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.25})
            # Bass stays strong
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.88})
            print("  Hats/Lead dropped, bass rolling...")

        # === RECOVERY after mini drops ===
        if variation in [56, 63, 69]:
            print("  *** RECOVERY ***")
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.50})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.40})
            print("  Elements returning...")

        # === PEAK at 60 ===
        if variation == 60:
            print("  *** PEAK ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.56})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.48})
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
            print("  Maximum intensity!")

        # === Clip switching ===
        if random.random() < 0.12:
            clip = random.choice([0, 1, 2, 3, 4, 5])
            send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": clip})
            print(f"  Hats -> clip {clip}")

        if random.random() < 0.08:
            clip = random.choice([4, 5, 6, 7])
            send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": clip})
            print(f"  Bass -> clip {clip}")

        if random.random() < 0.05:
            clip = random.choice([0, 1, 2, 3])
            send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": clip})
            print(f"  Pad -> clip {clip}")

        variation += 1
        time.sleep(0.2)

    sock.close()
    print()
    print("=" * 60)
    print(f"Hypnotic evolution complete - now at Variation {variation}")
    print("Rolling deep, bass is king")
    print("=" * 60)


if __name__ == "__main__":
    main()
