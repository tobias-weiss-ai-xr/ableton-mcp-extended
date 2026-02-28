#!/usr/bin/env python3
"""Continue DJ evolution - Variation 20 -> 21 -> 22"""

import socket
import json
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
    print(">>> EVOLUTION - Variation 21 <<<")

    # Bass: 0.85-0.95 (MAIN FOCUS)
    bass_vol = round(random.uniform(0.88, 0.94), 2)
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
    print(f"Bass: {bass_vol} -> {result.get('status', 'done')}")

    # Kick drums - punchy
    kick_vol = round(random.uniform(0.70, 0.80), 2)
    result = send_tcp(sock, "set_track_volume", {"track_index": 0, "volume": kick_vol})
    print(f"Kick: {kick_vol} -> {result.get('status', 'done')}")

    # Hats evolution
    hats_vol = round(random.uniform(0.55, 0.65), 2)
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": hats_vol})
    print(f"Hats: {hats_vol} -> {result.get('status', 'done')}")

    # Lead: MAX 0.5
    lead_vol = round(random.uniform(0.38, 0.48), 2)
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": lead_vol})
    print(f"Lead: {lead_vol} -> {result.get('status', 'done')}")

    print("\n>>> EVOLUTION - Variation 22 <<<")

    # Bass push
    bass_vol = round(random.uniform(0.90, 0.95), 2)
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_vol})
    print(f"Bass PUSH: {bass_vol} -> {result.get('status', 'done')}")

    # Switch pads clip for texture change
    clip_idx = random.choice([1, 3, 4, 6])
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": clip_idx})
    print(f"Pads clip {clip_idx}: {result.get('status', 'done')}")

    # FX swell
    fx_vol = round(random.uniform(0.35, 0.50), 2)
    result = send_tcp(sock, "set_track_volume", {"track_index": 5, "volume": fx_vol})
    print(f"FX: {fx_vol} -> {result.get('status', 'done')}")

    # Hats clip change
    hats_clip = random.choice([0, 2, 4])
    result = send_tcp(sock, "fire_clip", {"track_index": 2, "clip_index": hats_clip})
    print(f"Hats clip {hats_clip}: {result.get('status', 'done')}")

    sock.close()
    print("\n" + "=" * 50)
    print("MIX EVOLVING - Variation 22")
    print("Bass: DOMINANT | Lead: SUBTLE | Stabs: FIXED @0.45")
    print("=" * 50)


if __name__ == "__main__":
    main()
