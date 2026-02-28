#!/usr/bin/env python3
"""DJ Live Performance - Variation 58
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
    print(f"[DJ] DJ LIVE V58 - Connected to {TCP_HOST}:{TCP_PORT}")

    # ========== EXECUTE USER COMMANDS ==========
    print("\n>> EXECUTING USER COMMANDS:")

    # 1. Fire clip track 1, clip 4 (Bass)
    print("  -> Fire Clip Track 1 (Bass), Clip 4")
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 4})
    print(f"    Result: {result.get('status', 'unknown')}")

    # 2. Fire clip track 4, clip 1
    print("  -> Fire Clip Track 4, Clip 1")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 1})
    print(f"    Result: {result.get('status', 'unknown')}")

    # 3. Set track 1 volume to 0.90 (Bass - main focus)
    print("  -> Set Track 1 (Bass) volume to 0.90")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.90})
    print(f"    Result: {result.get('status', 'unknown')}")

    # ========== CONTINUE MIX EVOLUTION ==========
    print("\n[MIX] CONTINUING EVOLUTION (Variation 58+):")

    # Lead track - keep controlled (max 0.5)
    print("\n  [LEAD] Track 2:")
    lead_volume = random.uniform(0.35, 0.5)
    print(f"    -> Set volume to {lead_volume:.2f} (max 0.5)")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 2, "volume": lead_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Drums - evolve volume
    print("\n  [DRUMS] Track 0:")
    drums_volume = random.uniform(0.72, 0.82)
    print(f"    -> Set volume to {drums_volume:.2f}")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 0, "volume": drums_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Stabs - keep at 0.45, rarely change
    print("\n  [STABS] Track 6:")
    stabs_volume = 0.45
    print(f"    -> Set volume to {stabs_volume:.2f} (fixed)")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 6, "volume": stabs_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Pad/Atmosphere - add texture
    print("\n  [PAD] Track 5:")
    pad_volume = random.uniform(0.55, 0.7)
    print(f"    -> Set volume to {pad_volume:.2f}")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 5, "volume": pad_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Keys/Chords - movement
    print("\n  [KEYS] Track 3:")
    keys_volume = random.uniform(0.55, 0.7)
    print(f"    -> Set volume to {keys_volume:.2f}")
    result = send_tcp(
        sock, "set_track_volume", {"track_index": 3, "volume": keys_volume}
    )
    print(f"      Result: {result.get('status', 'unknown')}")

    # Occasional clip evolution
    if random.random() < 0.35:  # 35% chance
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

    print("\n[OK] Mix evolution complete - Variation 58")
    print("[INFO] Bass prominent at 0.90 (main focus)")
    print("[INFO] Lead controlled at {:.2f} (max 0.5)".format(lead_volume))
    print("[INFO] Stabs at 0.45 (rarely changed)")
    print("[INFO] All patterns evolving...")

    sock.close()


if __name__ == "__main__":
    main()
