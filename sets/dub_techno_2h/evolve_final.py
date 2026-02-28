#!/usr/bin/env python3
"""Final push and journey - Variations 71-85."""

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

    variation = 71

    print("=" * 60)
    print("FINAL PUSH - Variations 71-85")
    print("Journey to the peak and beyond...")
    print("=" * 60)

    for cycle in range(15):
        print(f"\n--- Variation {variation} ---")

        # === BASS: Always main focus (0.85-0.95) ===
        bass_vol = round(random.uniform(0.87, 0.95), 2)
        send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
        print(f"  Bass vol: {bass_vol}")

        # Filter sweeps
        if random.random() < 0.3:
            filter_val = round(random.uniform(0.35, 0.55), 2)
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
        if random.random() < 0.4:
            hats_vol = round(random.uniform(0.44, 0.56), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": hats_vol})
            print(f"  Hats vol: {hats_vol}")

        # === LEAD: max 0.5 ===
        if random.random() < 0.3:
            lead_vol = round(random.uniform(0.34, 0.48), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
            print(f"  Lead vol: {lead_vol}")

        # === STABS: 0.45 fixed ===
        if random.random() < 0.05:
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
            print(f"  Stabs vol: 0.45")

        # === FINAL BUILD: 75-78 ===
        if variation == 75:
            print("  *** BUILD START ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.52})

        if variation == 76:
            print("  *** BUILDING ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.55})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.45})

        if variation == 77:
            print("  *** ALMOST THERE ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.57})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.48})

        # === FINAL PEAK: 78 ===
        if variation == 78:
            print("  *** FINAL PEAK ***")
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.58})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.50})
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
            print("  Maximum everything!")

        # === WIND DOWN: 80-85 ===
        if variation == 80:
            print("  *** WIND DOWN START ***")
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.35})
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.40})

        if variation == 82:
            print("  *** WINDING ***")
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.48})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.30})

        if variation == 84:
            print("  *** ALMOST GONE ***")
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.42})
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.25})
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.35})

        # === Clip switching ===
        if random.random() < 0.12:
            clip = random.choice([0, 1, 2, 3, 4, 5])
            send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": clip})
            print(f"  Hats -> clip {clip}")

        if random.random() < 0.08:
            clip = random.choice([4, 5, 6, 7])
            send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": clip})
            print(f"  Bass -> clip {clip}")

        variation += 1
        time.sleep(0.2)

    sock.close()
    print()
    print("=" * 60)
    print(f"Final push complete - now at Variation {variation}")
    print("Journey complete. Bass remains.")
    print("=" * 60)


if __name__ == "__main__":
    main()
