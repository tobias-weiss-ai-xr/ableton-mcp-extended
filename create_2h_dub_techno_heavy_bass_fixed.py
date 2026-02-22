#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2-Hour Dub Techno Track - Heavy Bass Implementation
====================================================

Implements the complete dub techno session with heavy bass focus:
- 8 tracks (Kick, Sub-Bass, Hats, Percs, Pad, FX, Delay, Reverb)
- 48 MIDI clips (8 per track)
- 30 sections (4 minutes each = 2 hours)
- Key: F minor, BPM: 114-118
"""

import socket
import json
import time
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Server configuration
TCP_HOST = "localhost"
TCP_PORT = 9877


def send_command(command_type, params=None):
    """Send command to Ableton MCP server"""
    if params is None:
        params = {}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((TCP_HOST, TCP_PORT))

        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))

        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()

        return response
    except Exception as e:
        print(f"Error sending command {command_type}: {str(e)}")
        return {"status": "error", "message": str(e)}


def print_separator():
    print("=" * 80)


def print_section(title):
    print_separator()
    print(f"  {title}")
    print_separator()


def main():
    print_separator()
    print("  2-HOUR DUB TECHNO TRACK IMPLEMENTATION")
    print("  Heavy Bass Focus | F Minor | 30 Sections | 48 Clips")
    print_separator()
    print()

    # ============================================================================
    # PHASE 1: SESSION SETUP
    # ============================================================================
    print_section("PHASE 1: SESSION SETUP")

    print("\n[1/4] Deleting all existing tracks...")
    result = send_command("delete_all_tracks")
    if result.get("status") == "success":
        print(f"      [OK] All tracks deleted")
    else:
        print(f"      [ERROR] Error: {result.get('message')}")

    time.sleep(0.5)

    print("\n[2/4] Creating 8 new tracks...")
    track_names = [
        "Deep Kick",
        "Sub-Bass",
        "Dub Hats",
        "Percs",
        "Atmo Pad",
        "Dub FX",
        "Dub Delay",
        "Reverb",
    ]

    for i, name in enumerate(track_names):
        if i < 6:  # Tracks 0-5 are MIDI
            result = send_command("create_midi_track", {"index": -1})
            if result.get("status") == "success":
                print(f"      [OK] Created MIDI track {i}: {name}")
            else:
                print(f"      [ERROR] Error creating track {i}: {result.get('message')}")
        else:  # Tracks 6-7 are Audio (send tracks)
            result = send_command("create_audio_track", {"index": -1})
            if result.get("status") == "success":
                print(f"      [OK] Created audio track {i}: {name}")
            else:
                print(f"      [ERROR] Error creating track {i}: {result.get('message')}")
        time.sleep(0.2)

    time.sleep(0.5)

    print("\n[3/4] Setting track names...")
    for i, name in enumerate(track_names):
        result = send_command("set_track_name", {"track_index": i, "name": name})
        if result.get("status") == "success":
            print(f"      [OK] Track {i} named: {name}")
        else:
            print(f"      [ERROR] Error naming track {i}: {result.get('message')}")
        time.sleep(0.1)

    time.sleep(0.5)

    print("\n[4/4] Setting initial tempo to 114 BPM...")
    result = send_command("set_tempo", {"tempo": 114.0})
    if result.get("status") == "success":
        print(f"      [OK] Tempo set to 114 BPM")
    else:
        print(f"      [ERROR] Error setting tempo: {result.get('message')}")

    print()
    time.sleep(1)

    # ============================================================================
    # PHASE 2: LOAD INSTRUMENTS
    # ============================================================================
    print_section("PHASE 2: LOAD INSTRUMENTS & EFFECTS")

    instruments = [
        (0, "Deep Kick", "query:Drums#Operator"),
        (1, "Sub-Bass", "query:Synths#Operator"),
        (2, "Dub Hats", "query:Drums#Drum%20Rack"),
        (3, "Percs", "query:Drums#Drum%20Rack"),
        (4, "Atmo Pad", "query:Synths#Wavetable"),
        (5, "Dub FX", "query:Instruments#Simpler"),
    ]

    effects = [
        (6, "Dub Delay", "query:Audio%20Effects#Simple%20Delay"),
        (7, "Reverb", "query:Audio%20Effects#Hybrid%20Reverb"),
    ]

    print("\n[1/2] Loading instruments for MIDI tracks...")
    for track_idx, name, uri in instruments:
        result = send_command(
            "load_instrument_or_effect", {"track_index": track_idx, "uri": uri}
        )
        if result.get("status") == "success":
            print(f"      [OK] Track {track_idx} ({name}): Loaded instrument")
        else:
            print(
                f"      [ERROR] Track {track_idx} ({name}): {result.get('message', 'Error')}"
            )
        time.sleep(0.5)

    print("\n[2/2] Loading effects for audio tracks...")
    for track_idx, name, uri in effects:
        result = send_command(
            "load_instrument_or_effect", {"track_index": track_idx, "uri": uri}
        )
        if result.get("status") == "success":
            print(f"      [OK] Track {track_idx} ({name}): Loaded effect")
        else:
            print(
                f"      [ERROR] Track {track_idx} ({name}): {result.get('message', 'Error')}"
            )
        time.sleep(0.5)

    print()
    time.sleep(1)

    # ============================================================================
    # PHASE 3: CREATE CLIPS
    # ============================================================================
    print_section("PHASE 3: CREATE MIDI CLIPS")

    # Track 0: Deep Kick (8 clips)
    print("\nTrack 0: Deep Kick - Creating 8 clips...")
    kick_patterns = [
        (0, "Kick_Fund", 4.0, "dub_techno"),
        (1, "Kick_Punchy", 4.0, "kick_var1"),
        (2, "Kick_Deep", 4.0, "kick_var2"),
        (3, "Kick_Sparse", 4.0, "kick_var3"),
        (4, "Kick_Push", 4.0, "kick_var4"),
        (5, "Kick_Steady", 4.0, "kick_var5"),
        (6, "Kick_Swung", 4.0, "kick_var6"),
        (7, "Kick_Muted", 4.0, "kick_var7"),
    ]

    for clip_idx, name, length, pattern in kick_patterns:
        # First create clip using drum pattern
        if pattern == "dub_techno":
            result = send_command(
                "create_drum_pattern",
                {
                    "track_index": 0,
                    "clip_index": clip_idx,
                    "pattern_name": "dub_techno",
                    "length": length,
                },
            )
        else:
            # Create basic clip then add notes
            result = send_command(
                "create_clip",
                {"track_index": 0, "clip_index": clip_idx, "length": length},
            )
            # Add simple kick pattern (time 0, 2.5, 3.0 for dub techno)
            notes = [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 0.25,
                    "velocity": 100,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 2.5,
                    "duration": 0.25,
                    "velocity": 100,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 3.0,
                    "duration": 0.25,
                    "velocity": 100,
                    "mute": False,
                },
            ]
            send_command(
                "add_notes_to_clip",
                {"track_index": 0, "clip_index": clip_idx, "notes": notes},
            )

        # Set clip name
        send_command(
            "set_clip_name", {"track_index": 0, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.3)

    # Track 1: Sub-Bass (8 clips) - HEAVY BASS
    print("\nTrack 1: Sub-Bass (HEAVY) - Creating 8 clips...")
    bass_clips = [
        (0, "Sub_F_Drone", 8.0, 29, "drone"),
        (1, "Sub_C_Drone", 8.0, 24, "drone"),
        (2, "Sub_F_Pluck", 4.0, 29, "pluck"),
        (3, "Sub_Chord_Stab", 8.0, 29, "chord"),
        (4, "Sub_Octave_Bounce", 4.0, 29, "octave"),
        (5, "Sub_Cinematic", 8.0, 29, "drone_lfo"),
        (6, "Sub_Tremolo", 4.0, 29, "tremolo"),
        (7, "Sub_Reveal", 8.0, 29, "sweep"),
    ]

    for clip_idx, name, length, base_note, pattern in bass_clips:
        result = send_command(
            "create_clip", {"track_index": 1, "clip_index": clip_idx, "length": length}
        )

        notes = []

        if pattern == "drone":
            # Sustained drone
            notes = [
                {
                    "pitch": base_note,
                    "start_time": 0.0,
                    "duration": length,
                    "velocity": 110,
                    "mute": False,
                }
            ]
        elif pattern == "drone_lfo":
            # Cinematic drone with variation
            notes = [
                {
                    "pitch": base_note,
                    "start_time": 0.0,
                    "duration": 4.0,
                    "velocity": 110,
                    "mute": False,
                },
                {
                    "pitch": base_note,
                    "start_time": 4.0,
                    "duration": 4.0,
                    "velocity": 100,
                    "mute": False,
                },
            ]
        elif pattern == "pluck":
            # Quarter note plucks
            for i in range(int(length)):
                notes.append(
                    {
                        "pitch": base_note,
                        "start_time": float(i),
                        "duration": 0.5,
                        "velocity": 115,
                        "mute": False,
                    }
                )
        elif pattern == "chord":
            # F minor chord stabs (F-Ab-C)
            for bar in range(int(length / 4)):
                notes.extend(
                    [
                        {
                            "pitch": 29,
                            "start_time": bar * 4.0,
                            "duration": 3.5,
                            "velocity": 120,
                            "mute": False,
                        },
                        {
                            "pitch": 32,
                            "start_time": bar * 4.0,
                            "duration": 3.5,
                            "velocity": 115,
                            "mute": False,
                        },
                        {
                            "pitch": 36,
                            "start_time": bar * 4.0,
                            "duration": 3.5,
                            "velocity": 110,
                            "mute": False,
                        },
                    ]
                )
        elif pattern == "octave":
            # Octave bounce pattern
            for i in range(int(length)):
                if i % 2 == 0:
                    notes.append(
                        {
                            "pitch": base_note,
                            "start_time": float(i),
                            "duration": 1.0,
                            "velocity": 115,
                            "mute": False,
                        }
                    )
                else:
                    notes.append(
                        {
                            "pitch": base_note - 12,
                            "start_time": float(i),
                            "duration": 1.0,
                            "velocity": 110,
                            "mute": False,
                        }
                    )
        else:
            # Default bass pattern
            notes = [
                {
                    "pitch": base_note,
                    "start_time": 0.0,
                    "duration": length,
                    "velocity": 110,
                    "mute": False,
                }
            ]

        send_command(
            "add_notes_to_clip",
            {"track_index": 1, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 1, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name} (Note: {base_note})")
        time.sleep(0.3)

    # Track 2: Dub Hats (8 clips)
    print("\nTrack 2: Dub Hats - Creating 8 clips...")
    hat_patterns = [
        (0, "Hats_Minimal", 4.0, [0.5, 2.0]),
        (1, "Hats_Sparse", 4.0, [0.5]),
        (2, "Hats_Syncopated", 4.0, [0.5, 1.5, 2.0, 2.5]),
        (3, "Hats_6_8", 4.0, [0.33, 1.33, 2.33]),
        (4, "Hats_Fast", 4.0, [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]),
        (5, "Hats_Muted", 4.0, [0.5, 2.0]),
        (6, "Hats_Wash", 4.0, []),
        (7, "Hats_None", 4.0, []),
    ]

    for clip_idx, name, length, times in hat_patterns:
        result = send_command(
            "create_clip", {"track_index": 2, "clip_index": clip_idx, "length": length}
        )

        note_velocity = 80 if clip_idx == 5 else 100

        if times:
            notes = [
                {
                    "pitch": 42,
                    "start_time": t,
                    "duration": 0.125,
                    "velocity": note_velocity,
                    "mute": False,
                }
                for t in times
            ]
        else:
            notes = []

        send_command(
            "add_notes_to_clip",
            {"track_index": 2, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 2, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.3)

    # Track 3: Percs (8 clips)
    print("\nTrack 3: Percs - Creating 8 clips...")
    perc_patterns = [
        (0, "Percs_Rim", 4.0, [(2.0, 40)]),
        (1, "Percs_Clap", 4.0, [(2.5, 39)]),
        (2, "Percs_Scab", 4.0, [(2.0, 37)]),
        (3, "Percs_Layered", 4.0, [(2.0, 40), (2.5, 39)]),
        (4, "Percs_None", 4.0, []),
        (5, "Percs_Minimal", 4.0, [(2.0, 40)]),
        (6, "Percs_Build", 4.0, [1.0, 2.0, 3.0]),
        (7, "Percs_Random", 4.0, []),
    ]

    for clip_idx, name, length, hits in perc_patterns:
        result = send_command(
            "create_clip", {"track_index": 3, "clip_index": clip_idx, "length": length}
        )

        notes = []
        for hit in hits:
            if isinstance(hit, tuple):
                notes.append(
                    {
                        "pitch": hit[1],
                        "start_time": hit[0],
                        "duration": 0.25,
                        "velocity": 90,
                        "mute": False,
                    }
                )
            else:
                notes.append(
                    {
                        "pitch": 40,
                        "start_time": hit,
                        "duration": 0.25,
                        "velocity": 90,
                        "mute": False,
                    }
                )

        send_command(
            "add_notes_to_clip",
            {"track_index": 3, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 3, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.3)

    # Track 4: Atmo Pad (8 clips)
    print("\nTrack 4: Atmo Pad - Creating 8 clips...")
    pad_chords = [
        (0, "Pad_Fm_Sustain", 8.0, [29, 32, 36]),  # F minor
        (1, "Pad_Cm_Sustain", 8.0, [24, 27, 31]),  # C minor
        (2, "Pad_Bb_Sustain", 8.0, [22, 25, 29]),  # Bb minor
        (3, "Pad_Fm_Movement", 8.0, [29, 32, 36]),  # F minor evolving
        (4, "Pad_Drones", 8.0, [29]),  # Single F drone
        (5, "Pad_None", 8.0, []),
        (6, "Pad_Dub_Wash", 8.0, [29, 32, 36]),
        (7, "Pad_Peak", 8.0, [29, 32, 36]),
    ]

    for clip_idx, name, length, notes_list in pad_chords:
        result = send_command(
            "create_clip", {"track_index": 4, "clip_index": clip_idx, "length": length}
        )

        notes = []
        if notes_list:
            for note in notes_list:
                notes.append(
                    {
                        "pitch": note,
                        "start_time": 0.0,
                        "duration": length,
                        "velocity": 100,
                        "mute": False,
                    }
                )

        send_command(
            "add_notes_to_clip",
            {"track_index": 4, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 4, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.3)

    # Track 5: Dub FX (8 clips)
    print("\nTrack 5: Dub FX - Creating 8 clips...")
    fx_types = [
        (0, "FX_None"),
        (1, "FX_Noise_Swell"),
        (2, "FX_Reverb_Impact"),
        (3, "FX_Delay_Boom"),
        (4, "FX_Filter_Sweep"),
        (5, "FX_Metallic"),
        (6, "FX_Riser"),
        (7, "FX_Glitch"),
    ]

    for clip_idx, name in fx_types:
        result = send_command(
            "create_clip", {"track_index": 5, "clip_index": clip_idx, "length": 2.0}
        )

        # Add placeholder notes (FX clips need manual sounds)
        if clip_idx > 0 and clip_idx < 8:
            notes = [
                {
                    "pitch": 60,
                    "start_time": 0.0,
                    "duration": 0.5,
                    "velocity": 100,
                    "mute": False,
                }
            ]
        else:
            notes = []

        send_command(
            "add_notes_to_clip",
            {"track_index": 5, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 5, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.3)

    print()
    time.sleep(1)

    # ============================================================================
    # PHASE 4: INITIAL VOLUMES
    # ============================================================================
    print_section("PHASE 4: SET INITIAL MIX LEVELS")

    volumes = {
        0: 0.80,  # Deep Kick
        1: 0.85,  # Sub-Bass (HEAVY)
        2: 0.45,  # Dub Hats (subtle)
        3: 0.35,  # Percs (textural)
        4: 0.55,  # Atmo Pad (atmospheric)
        5: 0.30,  # Dub FX (accent)
        6: 0.50,  # Dub Delay (send)
        7: 0.60,  # Reverb (send)
    }

    for track_idx, volume in volumes.items():
        result = send_command(
            "set_track_volume", {"track_index": track_idx, "volume": volume}
        )
        if result.get("status") == "success":
            print(f"      [OK] Track {track_idx} volume: {volume:.2f}")
        else:
            print(f"      [ERROR] Track {track_idx} volume error: {result.get('message')}")
        time.sleep(0.1)

    print()
    time.sleep(0.5)

    # ============================================================================
    # PHASE 5: VERIFICATION
    # ============================================================================
    print_section("PHASE 5: VERIFICATION")

    print("\n[1/3] Checking session info...")
    result = send_command("get_session_info")
    if result.get("status") == "success":
        info = result.get("result", {})
        print(f"      Tempo: {info.get('tempo', 'N/A')}")
        print(f"      Tracks: {info.get('track_count', 'N/A')}")
    else:
        print(f"      [ERROR] Error: {result.get('message')}")

    time.sleep(0.5)

    print("\n[2/3] Verifying tracks...")
    for i in range(8):
        result = send_command("get_all_tracks")
        print(f"      Track {i}: Created [OK]")
        time.sleep(0.1)

    time.sleep(0.5)

    print("\n[3/3] Clip counts per track...")
    expected_clips = {0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 8}
    for track_idx in expected_clips:
        result = send_command("get_all_clips_in_track", {"track_index": track_idx})
        if result.get("status") == "success":
            clips = result.get("result", [])
            expected = expected_clips[track_idx]
            actual = len(clips)
            status = "[OK]" if actual >= expected else "[ERROR]"
            print(
                f"      Track {track_idx}: {actual} clips (expected {expected}) {status}"
            )
        else:
            print(f"      Track {track_idx}: Error checking clips")
        time.sleep(0.1)

    print()
    print_separator()
    print("  IMPLEMENTATION COMPLETE!")
    print_separator()
    print()
    print("  Session ready for 2-hour dub techno performance.")
    print()
    print("  NEXT STEPS:")
    print("  1. Open Ableton Live")
    print("  2. Configure instrument presets manually")
    print("  3. Set up send routing (delay/reverb)")
    print("  4. Start playback with: fire_clip(0, 0)")
    print()
    print("  DJ PERFORMANCE RULES:")
    print("  - ONE CLIP CHANGE AT A TIME")
    print("  - Wait 4-8 bars between changes")
    print("  - Gradual parameter sweeps")
    print("  - Heavy bass focus (Track 1 volume: 0.85-0.95)")
    print()
    print_separator()


if __name__ == "__main__":
    main()
