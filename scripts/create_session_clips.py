#!/usr/bin/env python3
"""Create MIDI clips on all 8 tracks in the current Ableton session.

Follows DJ skill principle: ONE CLIP CHANGE AT A TIME.
Uses TCP port 9877 for reliable operations.
"""

import socket
import json
import time

TCP_HOST = "localhost"
TCP_PORT = 9877
TIMEOUT = 5.0


def send_command(sock: socket.socket, command: dict) -> dict:
    """Send a command and receive response."""
    try:
        sock.send(json.dumps(command).encode("utf-8"))
        response = sock.recv(16384).decode("utf-8")
        return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    print("=" * 60)
    print("Creating MIDI clips on 8 tracks (DJ mode: one at a time)")
    print("=" * 60)

    # Create socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    try:
        sock.connect((TCP_HOST, TCP_PORT))
        print(f"[OK] Connected to MCP server on {TCP_HOST}:{TCP_PORT}")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        print("Make sure Ableton Live is running with MCP Remote Script loaded.")
        return

    # Step 1: Verify session state
    print("\n--- Step 1: Verify session state ---")
    response = send_command(sock, {"type": "get_session_info", "params": {}})
    if response.get("status") == "success":
        data = response.get("data", {})
        print(f"  Tempo: {data.get('tempo')} BPM")
        print(f"  Tracks: {data.get('num_tracks')}")
        print(f"  Scenes: {data.get('num_scenes')}")
    else:
        print(f"  [WARNING] Could not get session info: {response.get('message')}")

    # Set tempo to 75 BPM
    print("\n--- Setting tempo to 75 BPM ---")
    response = send_command(sock, {"type": "set_tempo", "params": {"tempo": 75}})
    if response.get("status") == "success":
        print("  [OK] Tempo set to 75 BPM")
    else:
        print(f"  [WARNING] Could not set tempo: {response.get('message')}")

    # Track 0: Drums - Dub techno pattern
    print("\n--- Track 0 (Drums): Creating dub techno drum pattern ---")
    response = send_command(
        sock,
        {
            "type": "create_drum_pattern",
            "params": {
                "track_index": 0,
                "clip_index": 0,
                "pattern_name": "dub_techno",
                "length": 4,
            },
        },
    )
    if response.get("status") == "success":
        print("  [OK] Dub techno drum pattern created")
    else:
        print(f"  [WARNING] Could not create drum pattern: {response.get('message')}")
        # Fallback: create clip manually
        print("  [FALLBACK] Creating manual kick pattern...")
        response = send_command(
            sock,
            {
                "type": "create_clip",
                "params": {"track_index": 0, "clip_index": 0, "length": 4.0},
            },
        )
        if response.get("status") == "success":
            # Add basic kick pattern
            notes = [
                {"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 100},
                {"pitch": 36, "start_time": 1.0, "duration": 0.5, "velocity": 100},
                {"pitch": 36, "start_time": 2.0, "duration": 0.5, "velocity": 100},
                {"pitch": 36, "start_time": 3.0, "duration": 0.5, "velocity": 100},
                {"pitch": 38, "start_time": 1.0, "duration": 0.25, "velocity": 80},
                {"pitch": 38, "start_time": 3.0, "duration": 0.25, "velocity": 80},
            ]
            response = send_command(
                sock,
                {
                    "type": "add_notes_to_clip",
                    "params": {"track_index": 0, "clip_index": 0, "notes": notes},
                },
            )
            if response.get("status") == "success":
                print("  [OK] Manual kick/snare pattern created")

    time.sleep(0.1)

    # Track 1: Bass - Root notes on 1 and 3 (C2 = MIDI 36)
    print("\n--- Track 1 (Bass): Creating bass line ---")
    response = send_command(
        sock,
        {
            "type": "create_clip",
            "params": {"track_index": 1, "clip_index": 0, "length": 4.0},
        },
    )
    if response.get("status") == "success":
        print("  [OK] Clip created")
        # C2 = 36, add root notes on beats 1 and 3
        bass_notes = [
            {"pitch": 36, "start_time": 0.0, "duration": 1.75, "velocity": 90},
            {"pitch": 36, "start_time": 2.0, "duration": 1.75, "velocity": 90},
        ]
        response = send_command(
            sock,
            {
                "type": "add_notes_to_clip",
                "params": {"track_index": 1, "clip_index": 0, "notes": bass_notes},
            },
        )
        if response.get("status") == "success":
            print("  [OK] Bass notes added (C2 on beats 1 and 3)")
        else:
            print(f"  [WARNING] Could not add bass notes: {response.get('message')}")
    else:
        print(f"  [WARNING] Could not create bass clip: {response.get('message')}")

    time.sleep(0.1)

    # Track 2: FX_Risers - Ascending pattern
    print("\n--- Track 2 (FX_Risers): Creating riser pattern ---")
    response = send_command(
        sock,
        {
            "type": "create_clip",
            "params": {"track_index": 2, "clip_index": 0, "length": 4.0},
        },
    )
    if response.get("status") == "success":
        print("  [OK] Clip created")
        # Ascending notes for riser effect (C3 to C5)
        riser_notes = [
            {"pitch": 48, "start_time": 0.0, "duration": 0.5, "velocity": 60},
            {"pitch": 51, "start_time": 0.5, "duration": 0.5, "velocity": 65},
            {"pitch": 55, "start_time": 1.0, "duration": 0.5, "velocity": 70},
            {"pitch": 58, "start_time": 1.5, "duration": 0.5, "velocity": 75},
            {"pitch": 60, "start_time": 2.0, "duration": 0.5, "velocity": 80},
            {"pitch": 63, "start_time": 2.5, "duration": 0.5, "velocity": 85},
            {"pitch": 67, "start_time": 3.0, "duration": 0.5, "velocity": 90},
            {"pitch": 72, "start_time": 3.5, "duration": 0.5, "velocity": 100},
        ]
        response = send_command(
            sock,
            {
                "type": "add_notes_to_clip",
                "params": {"track_index": 2, "clip_index": 0, "notes": riser_notes},
            },
        )
        if response.get("status") == "success":
            print("  [OK] Riser notes added (C3 ascending to C5)")
        else:
            print(f"  [WARNING] Could not add riser notes: {response.get('message')}")
    else:
        print(f"  [WARNING] Could not create riser clip: {response.get('message')}")

    time.sleep(0.1)

    # Track 3: Pad_Atmos - C minor sustained chord
    print("\n--- Track 3 (Pad_Atmos): Creating C minor pad chord ---")
    response = send_command(
        sock,
        {
            "type": "create_clip",
            "params": {"track_index": 3, "clip_index": 0, "length": 4.0},
        },
    )
    if response.get("status") == "success":
        print("  [OK] Clip created")
        # C minor chord: C3=48, Eb3=51, G3=55
        pad_notes = [
            {"pitch": 48, "start_time": 0.0, "duration": 4.0, "velocity": 70},
            {"pitch": 51, "start_time": 0.0, "duration": 4.0, "velocity": 70},
            {"pitch": 55, "start_time": 0.0, "duration": 4.0, "velocity": 70},
        ]
        response = send_command(
            sock,
            {
                "type": "add_notes_to_clip",
                "params": {"track_index": 3, "clip_index": 0, "notes": pad_notes},
            },
        )
        if response.get("status") == "success":
            print("  [OK] C minor chord added (C-Eb-G)")
        else:
            print(f"  [WARNING] Could not add pad notes: {response.get('message')}")
    else:
        print(f"  [WARNING] Could not create pad clip: {response.get('message')}")

    time.sleep(0.1)

    # Track 4: Rhythm_Skank - Reggae offbeat pattern
    print("\n--- Track 4 (Rhythm_Skank): Creating reggae skank ---")
    response = send_command(
        sock,
        {
            "type": "create_clip",
            "params": {"track_index": 4, "clip_index": 0, "length": 4.0},
        },
    )
    if response.get("status") == "success":
        print("  [OK] Clip created")
        # C minor chord offbeats: beats 2 and 4 (offbeat skank)
        skank_notes = [
            {"pitch": 48, "start_time": 0.5, "duration": 0.4, "velocity": 80},
            {"pitch": 51, "start_time": 0.5, "duration": 0.4, "velocity": 80},
            {"pitch": 55, "start_time": 0.5, "duration": 0.4, "velocity": 80},
            {"pitch": 48, "start_time": 1.5, "duration": 0.4, "velocity": 80},
            {"pitch": 51, "start_time": 1.5, "duration": 0.4, "velocity": 80},
            {"pitch": 55, "start_time": 1.5, "duration": 0.4, "velocity": 80},
            {"pitch": 48, "start_time": 2.5, "duration": 0.4, "velocity": 80},
            {"pitch": 51, "start_time": 2.5, "duration": 0.4, "velocity": 80},
            {"pitch": 55, "start_time": 2.5, "duration": 0.4, "velocity": 80},
            {"pitch": 48, "start_time": 3.5, "duration": 0.4, "velocity": 80},
            {"pitch": 51, "start_time": 3.5, "duration": 0.4, "velocity": 80},
            {"pitch": 55, "start_time": 3.5, "duration": 0.4, "velocity": 80},
        ]
        response = send_command(
            sock,
            {
                "type": "add_notes_to_clip",
                "params": {"track_index": 4, "clip_index": 0, "notes": skank_notes},
            },
        )
        if response.get("status") == "success":
            print("  [OK] Reggae skank added (offbeats)")
        else:
            print(f"  [WARNING] Could not add skank notes: {response.get('message')}")
    else:
        print(f"  [WARNING] Could not create skank clip: {response.get('message')}")

    time.sleep(0.1)

    # Track 5: Horns_Melody - Simple melody
    print("\n--- Track 5 (Horns_Melody): Creating simple melody ---")
    response = send_command(
        sock,
        {
            "type": "create_clip",
            "params": {"track_index": 5, "clip_index": 0, "length": 4.0},
        },
    )
    if response.get("status") == "success":
        print("  [OK] Clip created")
        # Simple C minor melody
        melody_notes = [
            {"pitch": 55, "start_time": 0.0, "duration": 0.5, "velocity": 85},  # G
            {"pitch": 55, "start_time": 0.5, "duration": 0.5, "velocity": 85},  # G
            {"pitch": 51, "start_time": 1.0, "duration": 1.0, "velocity": 85},  # Eb
            {"pitch": 48, "start_time": 2.0, "duration": 0.5, "velocity": 85},  # C
            {"pitch": 51, "start_time": 2.5, "duration": 0.5, "velocity": 85},  # Eb
            {"pitch": 55, "start_time": 3.0, "duration": 1.0, "velocity": 85},  # G
        ]
        response = send_command(
            sock,
            {
                "type": "add_notes_to_clip",
                "params": {"track_index": 5, "clip_index": 0, "notes": melody_notes},
            },
        )
        if response.get("status") == "success":
            print("  [OK] Horns melody added")
        else:
            print(f"  [WARNING] Could not add melody notes: {response.get('message')}")
    else:
        print(f"  [WARNING] Could not create melody clip: {response.get('message')}")

    time.sleep(0.1)

    # Track 6: Percussion - 4-bar pattern
    print("\n--- Track 6 (Percussion): Creating percussion pattern ---")
    response = send_command(
        sock,
        {
            "type": "create_clip",
            "params": {"track_index": 6, "clip_index": 0, "length": 4.0},
        },
    )
    if response.get("status") == "success":
        print("  [OK] Clip created")
        # Percussion pattern using various drum rack pads
        # Common percussion: shaker=70, tambourine=71, conga=75-76, cowbell=56
        percussion_notes = [
            {
                "pitch": 70,
                "start_time": 0.25,
                "duration": 0.25,
                "velocity": 70,
            },  # shaker
            {"pitch": 70, "start_time": 0.75, "duration": 0.25, "velocity": 70},
            {"pitch": 70, "start_time": 1.25, "duration": 0.25, "velocity": 70},
            {"pitch": 70, "start_time": 1.75, "duration": 0.25, "velocity": 70},
            {"pitch": 70, "start_time": 2.25, "duration": 0.25, "velocity": 70},
            {"pitch": 70, "start_time": 2.75, "duration": 0.25, "velocity": 70},
            {"pitch": 70, "start_time": 3.25, "duration": 0.25, "velocity": 70},
            {"pitch": 70, "start_time": 3.75, "duration": 0.25, "velocity": 70},
            {
                "pitch": 75,
                "start_time": 1.0,
                "duration": 0.25,
                "velocity": 75,
            },  # conga low
            {
                "pitch": 76,
                "start_time": 3.0,
                "duration": 0.25,
                "velocity": 75,
            },  # conga high
        ]
        response = send_command(
            sock,
            {
                "type": "add_notes_to_clip",
                "params": {
                    "track_index": 6,
                    "clip_index": 0,
                    "notes": percussion_notes,
                },
            },
        )
        if response.get("status") == "success":
            print("  [OK] Percussion pattern added")
        else:
            print(
                f"  [WARNING] Could not add percussion notes: {response.get('message')}"
            )
    else:
        print(
            f"  [WARNING] Could not create percussion clip: {response.get('message')}"
        )

    time.sleep(0.1)

    # Track 7: Vocal_Chops - Simple pattern
    print("\n--- Track 7 (Vocal_Chops): Creating simple pattern ---")
    response = send_command(
        sock,
        {
            "type": "create_clip",
            "params": {"track_index": 7, "clip_index": 0, "length": 4.0},
        },
    )
    if response.get("status") == "success":
        print("  [OK] Clip created")
        # Simple staccato pattern for vocal chops
        # Using middle C area for Simpler
        vocal_notes = [
            {"pitch": 60, "start_time": 0.0, "duration": 0.25, "velocity": 90},
            {"pitch": 62, "start_time": 1.0, "duration": 0.25, "velocity": 85},
            {"pitch": 60, "start_time": 2.0, "duration": 0.25, "velocity": 90},
            {"pitch": 65, "start_time": 3.0, "duration": 0.25, "velocity": 85},
        ]
        response = send_command(
            sock,
            {
                "type": "add_notes_to_clip",
                "params": {"track_index": 7, "clip_index": 0, "notes": vocal_notes},
            },
        )
        if response.get("status") == "success":
            print("  [OK] Vocal chops pattern added")
        else:
            print(f"  [WARNING] Could not add vocal notes: {response.get('message')}")
    else:
        print(f"  [WARNING] Could not create vocal clip: {response.get('message')}")

    time.sleep(0.1)

    # Set all track volumes to 0.7
    print("\n--- Setting all track volumes to 0.7 ---")
    for track_idx in range(8):
        response = send_command(
            sock,
            {
                "type": "set_track_volume",
                "params": {"track_index": track_idx, "volume": 0.7},
            },
        )
        if response.get("status") == "success":
            print(f"  [OK] Track {track_idx} volume set to 0.7")
        else:
            print(
                f"  [WARNING] Could not set track {track_idx} volume: {response.get('message')}"
            )
        time.sleep(0.05)

    # Final verification
    print("\n--- Final verification ---")
    response = send_command(sock, {"type": "get_session_info", "params": {}})
    if response.get("status") == "success":
        data = response.get("data", {})
        print(f"  Tempo: {data.get('tempo')} BPM")
        print(f"  Tracks: {data.get('num_tracks')}")

    sock.close()
    print("\n" + "=" * 60)
    print("[DONE] All clips created on 8 tracks!")
    print("=" * 60)


if __name__ == "__main__":
    main()
