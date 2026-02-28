#!/usr/bin/env python3
"""Continue evolving the DJ mix - Variations 26-35 with filter automation."""

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

    variation = 26

    print("=" * 60)
    print("DEEP EVOLUTION - Variations 26-35")
    print("=" * 60)

    for cycle in range(10):
        print(f"\n--- Variation {variation} ---")

        # Bass: always evolve (0.85-0.95) - MAIN FOCUS
        bass_vol = round(random.uniform(0.85, 0.95), 2)
        send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
        print(f"  Bass vol: {bass_vol}")

        # Occasionally add filter movement to bass
        if random.random() < 0.3:
            filter_val = round(random.uniform(0.35, 0.55), 2)
            send_tcp(
                sock,
                "set_device_parameter",
                {
                    "track_index": 1,
                    "device_index": 0,
                    "parameter_index": 10,  # Filter cutoff
                    "value": filter_val,
                },
            )
            print(f"  Bass filter: {filter_val}")

        # Hats: moderate changes (0.4-0.6)
        if random.random() < 0.5:
            hats_vol = round(random.uniform(0.42, 0.58), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": hats_vol})
            print(f"  Hats vol: {hats_vol}")

        # Lead/Percs: max 0.5
        if random.random() < 0.35:
            lead_vol = round(random.uniform(0.32, 0.50), 2)
            send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
            print(f"  Lead vol: {lead_vol}")

        # Stabs: rarely change, fixed at 0.45
        if random.random() < 0.1:
            send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})
            print(f"  Stabs vol: 0.45 (rare)")

        # Clip switching patterns
        # Hats clips: switch occasionally
        if random.random() < 0.18:
            clip = random.choice([0, 1, 2, 3, 4, 5])
            send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": clip})
            print(f"  Hats -> clip {clip}")

        # Bass clips: switch less often
        if random.random() < 0.12:
            clip = random.choice([4, 5, 6, 7])
            send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": clip})
            print(f"  Bass -> clip {clip}")

        # Big changes every 5 variations
        if variation % 5 == 0:
            print("  *** SECTION CHANGE ***")
            # Switch pad/stab
            clip = random.choice([0, 1, 2, 3])
            send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": clip})
            print(f"  Pad -> clip {clip}")

            # Maybe switch lead
            if random.random() < 0.5:
                clip = random.choice([0, 1, 2, 3])
                send_tcp(sock, "fire_clip", {"track_index": 3, "clip_index": clip})
                print(f"  Lead -> clip {clip}")

        # Energy builds: every 8th variation
        if variation % 8 == 0:
            print("  *** ENERGY BUILD ***")
            # Push bass up
            send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})
            # Hats up
            send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.55})
            print("  Pushing energy up")

        variation += 1
        time.sleep(0.3)

    sock.close()
    print()
    print("=" * 60)
    print(f"Deep evolution complete - now at Variation {variation}")
    print("Mix is rolling with bass focus!")
    print("=" * 60)


if __name__ == "__main__":
    main()
