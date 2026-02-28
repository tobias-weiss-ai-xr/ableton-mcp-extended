#!/usr/bin/env python3
"""DJ Live Performance - Variation 53 (Simplified)
Execute user commands and continue evolving the mix.
Rules:
- Bass: Volume 0.85-0.95 (main focus)
- Lead: Max volume 0.5
- Stabs: Volume 0.45, change rarely
- Evolve all patterns over time
"""

import socket
import json
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
    try:
        return json.loads(response)
    except:
        return {"status": "error", "message": "JSON parse failed"}


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"[DJ] DJ LIVE V53 - Connected to {TCP_HOST}:{TCP_PORT}")

    # Execute user's commands
    print("\n>> EXECUTING USER COMMANDS:")

    # 1. Set track 6 volume to 0.45 (Stabs)
    print("  -> Set Track 6 (Stabs) volume to 0.45")
    result = send_tcp(sock, "set_track_volume", {"track_index": 6, "volume": 0.45})
    print(f"    Result: {result.get('status', 'unknown')}")

    # 2. Fire clip track 4, clip 0
    print("  -> Fire Clip Track 4, Clip 0")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 0})
    print(f"    Result: {result.get('status', 'unknown')}")

    # 3. Fire clip track 4, clip 1
    print("  -> Fire Clip Track 4, Clip 1")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 1})
    print(f"    Result: {result.get('status', 'unknown')}")

    print("\n[MIX] CONTINUING MIX EVOLUTION (Variation 52+):")

    # Bass track - keep it prominent (0.85-0.95 range)
    print("\n  [BASS] Track 1:")
    bass_volume = random.uniform(0.88, 0.92)
    print(f"    -> Set volume to {bass_volume:.2f} (main focus)")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 1, "volume": bass_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Lead track - keep it controlled (max 0.5)
    print("\n  [LEAD] Track 2:")
    lead_volume = random.uniform(0.4, 0.5)
    print(f"    -> Set volume to {lead_volume:.2f} (max 0.5)")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 2, "volume": lead_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Drums - adjust volume for evolution
    print("\n  [DRUMS] Track 0:")
    drums_volume = random.uniform(0.75, 0.85)
    print(f"    -> Set volume to {drums_volume:.2f}")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 0, "volume": drums_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Pad/Atmosphere - adjust for texture
    print("\n  [PAD] Track 5:")
    pad_volume = random.uniform(0.5, 0.7)
    print(f"    -> Set volume to {pad_volume:.2f}")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 5, "volume": pad_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Keys/Chords - add movement
    print("\n  [KEYS] Track 3:")
    keys_volume = random.uniform(0.6, 0.75)
    print(f"    -> Set volume to {keys_volume:.2f}")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 3, "volume": keys_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Occasional clip changes for evolution
    if random.random() < 0.4:  # 40% chance to switch a clip
        track_to_change = random.choice([0, 3, 5])  # Drums, Keys, or Pad
        clip_to_fire = random.randint(0, 5)
        print(
            f"\n  [EVOLUTION] Fire new clip on Track {track_to_change}, Clip {clip_to_fire}"
        )
        result = send_tcp(
            sock,
            "fire_clip",
            {"track_index": track_to_change, "clip_index": clip_to_fire},
        )
        print(f"    Result: {result.get('status', 'unknown')}")

    print("\n[OK] Mix evolution complete - Variation 52+")
    print("[INFO] Bass is prominent (0.88-0.92)")
    print("[INFO] Lead controlled (max 0.5)")
    print("[INFO] Stabs at 0.45 (changed rarely)")
    print("[INFO] All patterns evolving...")

    sock.close()


if __name__ == "__main__":
    main()
