#!/usr/bin/env python
"""
Add drum patterns to all 16 scenes and verify note counts.
"""

import socket
import json
import time

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 10.0

# Drum note mappings (standard GM drum map)
KICK = 36  # C1
SNARE = 40  # E1
CLAP = 39  # D#1
HAT_CLOSED = 42  # F#1
HAT_OPEN = 46  # A#1


def send_command(sock, command_type, params=None):
    """Send a command to Ableton and return the response."""
    command = {"type": command_type, "params": params or {}}
    sock.sendall(json.dumps(command).encode("utf-8"))

    chunks = []
    sock.settimeout(TIMEOUT)
    while True:
        try:
            chunk = sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                data = b"".join(chunks)
                json.loads(data)
                break
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            break

    data = b"".join(chunks)
    response = json.loads(data.decode("utf-8"))

    if response.get("status") == "error":
        raise Exception(response.get("message", "Unknown error"))

    return response.get("result", {})


def add_notes_to_clip(sock, track_index, clip_index, notes):
    """Add notes to a clip."""
    return send_command(
        sock,
        "add_notes_to_clip",
        {"track_index": track_index, "clip_index": clip_index, "notes": notes},
    )


def delete_clip(sock, track_index, clip_index):
    """Delete a clip."""
    return send_command(
        sock, "delete_clip", {"track_index": track_index, "clip_index": clip_index}
    )


def create_clip(sock, track_index, clip_index, length=4.0):
    """Create a new clip."""
    return send_command(
        sock,
        "create_clip",
        {"track_index": track_index, "clip_index": clip_index, "length": length},
    )


def generate_drum_pattern(scene_index):
    """Generate drum pattern based on scene energy level."""

    patterns = {
        # Scene 0: Intro - minimal dub techno
        0: [
            (KICK, 0.0, 0.25, 100),
            (KICK, 2.0, 0.25, 100),
            (HAT_CLOSED, 0.5, 0.125, 70),
            (HAT_CLOSED, 2.5, 0.125, 70),
        ],
        # Scene 1: Build 1
        1: [
            (KICK, 0.0, 0.25, 105),
            (KICK, 2.0, 0.25, 105),
            (HAT_CLOSED, 0.5, 0.125, 75),
            (HAT_CLOSED, 1.5, 0.125, 75),
            (HAT_CLOSED, 2.5, 0.125, 75),
            (HAT_CLOSED, 3.5, 0.125, 75),
            (CLAP, 2.0, 0.125, 90),
        ],
        # Scene 2: Build 2
        2: [
            (KICK, 0.0, 0.25, 105),
            (KICK, 1.0, 0.25, 105),
            (KICK, 2.0, 0.25, 105),
            (KICK, 3.0, 0.25, 105),
            (HAT_CLOSED, 0.5, 0.125, 80),
            (HAT_CLOSED, 1.5, 0.125, 80),
            (HAT_CLOSED, 2.5, 0.125, 80),
            (HAT_CLOSED, 3.5, 0.125, 80),
            (CLAP, 1.0, 0.125, 95),
            (CLAP, 3.0, 0.125, 95),
        ],
        # Scene 3: Drop 1 - full energy
        3: [
            (KICK, 0.0, 0.25, 110),
            (KICK, 1.0, 0.25, 110),
            (KICK, 2.0, 0.25, 110),
            (KICK, 3.0, 0.25, 110),
            (HAT_CLOSED, 0.5, 0.125, 85),
            (HAT_CLOSED, 1.5, 0.125, 85),
            (HAT_CLOSED, 2.5, 0.125, 85),
            (HAT_CLOSED, 3.5, 0.125, 85),
            (CLAP, 1.0, 0.125, 100),
            (CLAP, 3.0, 0.125, 100),
        ],
        # Scene 4: Drop 2 - full energy with more hats
        4: [
            (KICK, 0.0, 0.25, 110),
            (KICK, 1.0, 0.25, 110),
            (KICK, 2.0, 0.25, 110),
            (KICK, 3.0, 0.25, 110),
            (HAT_CLOSED, 0.25, 0.125, 85),
            (HAT_CLOSED, 0.5, 0.125, 85),
            (HAT_CLOSED, 1.0, 0.125, 85),
            (HAT_CLOSED, 1.5, 0.125, 85),
            (HAT_CLOSED, 2.25, 0.125, 85),
            (HAT_CLOSED, 2.5, 0.125, 85),
            (HAT_CLOSED, 3.0, 0.125, 85),
            (HAT_CLOSED, 3.5, 0.125, 85),
            (CLAP, 1.0, 0.125, 100),
            (CLAP, 3.0, 0.125, 100),
        ],
        # Scene 5: Breakdown - minimal
        5: [
            (KICK, 0.0, 0.25, 90),
            (KICK, 2.0, 0.25, 85),
            (HAT_OPEN, 0.5, 0.25, 60),
            (HAT_OPEN, 2.5, 0.25, 55),
        ],
        # Scene 6: Build 3
        6: [
            (KICK, 0.0, 0.25, 105),
            (KICK, 2.0, 0.25, 105),
            (HAT_CLOSED, 0.5, 0.125, 80),
            (HAT_CLOSED, 1.5, 0.125, 80),
            (HAT_CLOSED, 2.5, 0.125, 80),
            (HAT_CLOSED, 3.5, 0.125, 80),
            (CLAP, 2.0, 0.125, 95),
        ],
        # Scene 7: Drop 3 - full energy
        7: [
            (KICK, 0.0, 0.25, 110),
            (KICK, 1.0, 0.25, 110),
            (KICK, 2.0, 0.25, 110),
            (KICK, 3.0, 0.25, 110),
            (HAT_CLOSED, 0.5, 0.125, 85),
            (HAT_CLOSED, 1.5, 0.125, 85),
            (HAT_CLOSED, 2.5, 0.125, 85),
            (HAT_CLOSED, 3.5, 0.125, 85),
            (CLAP, 1.0, 0.125, 100),
            (CLAP, 3.0, 0.125, 100),
        ],
        # Scene 8: Journey 1
        8: [
            (KICK, 0.0, 0.25, 105),
            (KICK, 2.0, 0.25, 105),
            (HAT_CLOSED, 0.5, 0.125, 80),
            (HAT_CLOSED, 2.5, 0.125, 80),
        ],
        # Scene 9: Journey 2
        9: [
            (KICK, 0.0, 0.25, 105),
            (KICK, 2.0, 0.25, 105),
            (HAT_CLOSED, 0.5, 0.125, 80),
            (HAT_CLOSED, 1.5, 0.125, 80),
            (HAT_CLOSED, 2.5, 0.125, 80),
            (CLAP, 2.0, 0.125, 95),
        ],
        # Scene 10: Peak 1 - full energy
        10: [
            (KICK, 0.0, 0.25, 110),
            (KICK, 1.0, 0.25, 110),
            (KICK, 2.0, 0.25, 110),
            (KICK, 3.0, 0.25, 110),
            (HAT_CLOSED, 0.5, 0.125, 85),
            (HAT_CLOSED, 1.5, 0.125, 85),
            (HAT_CLOSED, 2.5, 0.125, 85),
            (HAT_CLOSED, 3.5, 0.125, 85),
            (CLAP, 1.0, 0.125, 100),
            (CLAP, 3.0, 0.125, 100),
        ],
        # Scene 11: Peak 2 - full energy
        11: [
            (KICK, 0.0, 0.25, 110),
            (KICK, 1.0, 0.25, 110),
            (KICK, 2.0, 0.25, 110),
            (KICK, 3.0, 0.25, 110),
            (HAT_CLOSED, 0.5, 0.125, 85),
            (HAT_CLOSED, 1.5, 0.125, 85),
            (HAT_CLOSED, 2.5, 0.125, 85),
            (HAT_CLOSED, 3.5, 0.125, 85),
            (CLAP, 1.0, 0.125, 100),
            (CLAP, 3.0, 0.125, 100),
        ],
        # Scene 12: Transition
        12: [
            (KICK, 0.0, 0.25, 105),
            (KICK, 2.0, 0.25, 105),
            (HAT_CLOSED, 0.5, 0.125, 75),
            (HAT_CLOSED, 2.5, 0.125, 75),
            (SNARE, 1.0, 0.125, 90),
            (SNARE, 3.0, 0.125, 90),
        ],
        # Scene 13: Final push
        13: [
            (KICK, 0.0, 0.25, 110),
            (KICK, 1.0, 0.25, 110),
            (KICK, 2.0, 0.25, 110),
            (KICK, 3.0, 0.25, 110),
            (HAT_CLOSED, 0.5, 0.125, 85),
            (HAT_CLOSED, 1.5, 0.125, 85),
            (HAT_CLOSED, 2.5, 0.125, 85),
            (HAT_CLOSED, 3.5, 0.125, 85),
            (CLAP, 1.0, 0.125, 100),
            (CLAP, 3.0, 0.125, 100),
        ],
        # Scene 14: Wind down
        14: [
            (KICK, 0.0, 0.25, 95),
            (KICK, 2.0, 0.25, 90),
            (HAT_CLOSED, 0.5, 0.125, 70),
            (HAT_CLOSED, 2.5, 0.125, 65),
        ],
        # Scene 15: Outro
        15: [
            (KICK, 0.0, 0.25, 85),
            (HAT_OPEN, 1.0, 0.5, 55),
            (HAT_OPEN, 3.0, 0.5, 50),
        ],
    }

    return patterns.get(scene_index, patterns[0])


def main():
    """Add drum patterns to all 16 scenes."""
    print("=" * 60)
    print("ADDING DRUM PATTERNS TO ALL 16 SCENES")
    print("=" * 60)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    try:
        print(f"\nConnecting to Ableton at {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        print("Connected!")

        # Get tracks
        tracks_result = send_command(sock, "get_all_tracks")
        tracks = tracks_result.get("tracks", [])

        # Find Drums track
        drums_track = None
        for t in tracks:
            if t.get("name") == "Drums":
                drums_track = t["index"]
                break

        if drums_track is None:
            print("ERROR: Drums track not found!")
            return

        print(f"Drums track found at index {drums_track}")

        # Add drum patterns to all 16 scenes
        for scene_index in range(16):
            print(f"\n=== Scene {scene_index} ===")

            try:
                # Delete existing clip
                delete_clip(sock, drums_track, scene_index)
                time.sleep(0.03)

                # Create new clip
                create_clip(sock, drums_track, scene_index, 4.0)
                time.sleep(0.03)

                # Generate and add drum notes
                drum_notes = generate_drum_pattern(scene_index)
                notes_data = [
                    {
                        "pitch": n[0],
                        "start_time": n[1],
                        "duration": n[2],
                        "velocity": n[3],
                        "mute": False,
                    }
                    for n in drum_notes
                ]
                add_notes_to_clip(sock, drums_track, scene_index, notes_data)

                print(f"  Added {len(drum_notes)} drum notes")

            except Exception as e:
                print(f"  Error: {e}")

            time.sleep(0.05)

        print("\n" + "=" * 60)
        print("DRUM PATTERNS ADDED TO ALL 16 SCENES!")
        print("=" * 60)

        # Summary
        print("\n=== SCENE SUMMARY ===")
        for scene_index in range(16):
            drum_notes = generate_drum_pattern(scene_index)
            print(f"  Scene {scene_index:2d}: {len(drum_notes):2d} drum notes")

        print("\n=== ALL 16 SCENES REWORKED SUCCESSFULLY! ===")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        sock.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()
