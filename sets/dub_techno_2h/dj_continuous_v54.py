#!/usr/bin/env python3
"""DJ Live Performance - Continuous Evolution
Keep the mix evolving continuously with the rules:
- Bass: Volume 0.85-0.95 (main focus)
- Lead: Max volume 0.5
- Stabs: Volume 0.45, change rarely
- Evolve all patterns over time
"""

import socket
import json
import random
import time

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(sock, command_type: str, params: dict = None) -> dict:
    """Send command via TCP and wait for response."""
    message = {"type": command_type}
    if params:
        message["params"] = params

    sock.send(json.dumps(message).encode() + b"\n")
    response = sock.recv(8192).decode()
    try:
        return json.loads(response)
    except:
        return {"status": "error", "message": "JSON parse failed"}


def evolve_mix(sock, iteration):
    """Evolve the mix for one iteration."""
    print(f"\n{'=' * 60}")
    print(f"[ITERATION {iteration}] Mix Evolution")
    print(f"{'=' * 60}")

    # Bass - always prominent (0.85-0.95)
    bass_volume = random.uniform(0.87, 0.93)
    print(f"[BASS] Volume: {bass_volume:.2f}")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": bass_volume})

    # Lead - controlled (max 0.5)
    lead_volume = random.uniform(0.38, 0.48)
    print(f"[LEAD] Volume: {lead_volume:.2f}")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": lead_volume})

    # Stabs - change rarely (only 15% of time)
    if random.random() < 0.15:
        print(f"[STABS] Adjusting (rare change)")
        send_tcp(sock, "set_track_volume", {"track_index": 6, "volume": 0.45})
        # Maybe fire a different stab clip
        if random.random() < 0.5:
            clip = random.randint(0, 3)
            send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": clip})
            print(f"  -> Fired clip {clip}")

    # Drums - evolve
    drums_volume = random.uniform(0.72, 0.82)
    print(f"[DRUMS] Volume: {drums_volume:.2f}")
    send_tcp(sock, "set_track_volume", {"track_index": 0, "volume": drums_volume})

    # Pad - texture evolution
    pad_volume = random.uniform(0.48, 0.68)
    print(f"[PAD] Volume: {pad_volume:.2f}")
    send_tcp(sock, "set_track_volume", {"track_index": 5, "volume": pad_volume})

    # Keys - movement
    keys_volume = random.uniform(0.58, 0.73)
    print(f"[KEYS] Volume: {keys_volume:.2f}")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": keys_volume})

    # Occasional clip evolution (25% chance)
    if random.random() < 0.25:
        track = random.choice([0, 3, 5, 4])
        clip = random.randint(0, 5)
        print(f"\n[EVOLUTION] Switching clip: Track {track}, Clip {clip}")
        result = send_tcp(sock, "fire_clip", {"track_index": track, "clip_index": clip})
        print(f"  Result: {result.get('status', 'unknown')}")

    # Occasional build/drop (10% chance)
    if random.random() < 0.10:
        print("\n[BUILD] Creating a build...")
        # Increase drums and pad
        send_tcp(sock, "set_track_volume", {"track_index": 0, "volume": 0.88})
        send_tcp(sock, "set_track_volume", {"track_index": 5, "volume": 0.78})
        time.sleep(2)
        print("[DROP] Dropping...")
        # Drop back
        send_tcp(sock, "set_track_volume", {"track_index": 0, "volume": 0.72})
        send_tcp(sock, "set_track_volume", {"track_index": 5, "volume": 0.52})

    print(f"\n[STATUS] Iteration {iteration} complete")
    print(f"  Bass: {bass_volume:.2f} (prominent)")
    print(f"  Lead: {lead_volume:.2f} (controlled)")
    print(f"  Stabs: 0.45 (rarely changed)")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"[DJ] CONTINUOUS EVOLUTION - Connected to {TCP_HOST}:{TCP_PORT}")
    print(f"[DJ] Starting continuous mix evolution...")
    print(f"[DJ] Rules:")
    print(f"  - Bass: 0.85-0.95 (main focus)")
    print(f"  - Lead: Max 0.5")
    print(f"  - Stabs: 0.45, change rarely")
    print(f"  - Evolve all patterns over time")
    print(f"\n[DJ] Press Ctrl+C to stop\n")

    iteration = 1
    try:
        while True:
            evolve_mix(sock, iteration)
            iteration += 1

            # Wait between evolutions (8-16 seconds)
            wait_time = random.uniform(8, 16)
            print(f"\n[WAIT] Next evolution in {wait_time:.1f} seconds...")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print(f"\n\n[STOP] Stopping after {iteration - 1} iterations")
        print("[OK] Mix evolution stopped gracefully")

    sock.close()


if __name__ == "__main__":
    main()
