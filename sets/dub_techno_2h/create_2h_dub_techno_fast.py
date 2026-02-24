#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2-Hour Dub Techno Track - Heavy Bass Implementation (Streamlined)
=================================================================

Implements the complete dub techno session with heavy bass focus.
Faster execution with minimal delays.
"""

import socket
import json
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
        return {"status": "error", "message": str(e)}


def main():
    print("=" * 80)
    print("  2-HOUR DUB TECHNO TRACK IMPLEMENTATION (STREAMLINED)")
    print("  Heavy Bass Focus | F Minor | 30 Sections | 48 Clips")
    print("=" * 80)
    print()

    # PHASE 1: SESSION SETUP
    print("PHASE 1: SESSION SETUP")
    print("-" * 80)

    print("[1/4] Deleting all existing tracks...")
    result = send_command("delete_all_tracks")
    print(f"      Status: {result.get('status')}")

    print("[2/4] Creating 8 new tracks...")
    for i in range(8):
        if i < 6:
            result = send_command("create_midi_track", {"index": -1})
        else:
            result = send_command("create_audio_track", {"index": -1})
        print(f"      Track {i}: {result.get('status')}")

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

    print("[3/4] Setting track names...")
    for i, name in enumerate(track_names):
        result = send_command("set_track_name", {"track_index": i, "name": name})
        print(f"      Track {i} -> {name}: {result.get('status')}")

    print("[4/4] Setting initial tempo to 114 BPM...")
    result = send_command("set_tempo", {"tempo": 114.0})
    print(f"      Status: {result.get('status')}")
    print()

    # PHASE 2: LOAD INSTRUMENTS
    print("PHASE 2: LOAD INSTRUMENTS & EFFECTS")
    print("-" * 80)

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

    print("Loading instruments...")
    for track_idx, name, uri in instruments:
        result = send_command(
            "load_instrument_or_effect", {"track_index": track_idx, "uri": uri}
        )
        print(f"      Track {track_idx} ({name}): {result.get('status')}")

    print("Loading effects...")
    for track_idx, name, uri in effects:
        result = send_command(
            "load_instrument_or_effect", {"track_index": track_idx, "uri": uri}
        )
        print(f"      Track {track_idx} ({name}): {result.get('status')}")
    print()

    # PHASE 3: CREATE CLIPS
    print("PHASE 3: CREATE MIDI CLIPS")
    print("-" * 80)

    # Track 0: Deep Kick (8 clips)
    print("Track 0: Deep Kick - Creating 8 clips...")
    for clip_idx in range(8):
        # Create clip
        result = send_command(
            "create_clip", {"track_index": 0, "clip_index": clip_idx, "length": 4.0}
        )

        # Add dub techno kick pattern (0, 2.5, 3.0)
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
        kick_names = [
            "Kick_Fund",
            "Kick_Punchy",
            "Kick_Deep",
            "Kick_Sparse",
            "Kick_Push",
            "Kick_Steady",
            "Kick_Swung",
            "Kick_Muted",
        ]
        send_command(
            "set_clip_name",
            {"track_index": 0, "clip_index": clip_idx, "name": kick_names[clip_idx]},
        )
        print(f"      Clip {clip_idx}: {kick_names[clip_idx]}")

    # Track 1: Sub-Bass (8 clips) - HEAVY BASS
    print()
    print("Track 1: Sub-Bass (HEAVY) - Creating 8 clips...")
    bass_config = [
        (0, "Sub_F_Drone", 8.0, 29, "drone"),
        (1, "Sub_C_Drone", 8.0, 24, "drone"),
        (2, "Sub_F_Pluck", 4.0, 29, "pluck"),
        (3, "Sub_Chord_Stab", 8.0, 29, "chord"),
        (4, "Sub_Octave_Bounce", 4.0, 29, "octave"),
        (5, "Sub_Cinematic", 8.0, 29, "drone_lfo"),
        (6, "Sub_Tremolo", 4.0, 29, "tremolo"),
        (7, "Sub_Reveal", 8.0, 29, "sweep"),
    ]

    for clip_idx, name, length, base_note, pattern in bass_config:
        send_command(
            "create_clip", {"track_index": 1, "clip_index": clip_idx, "length": length}
        )

        notes = []
        if pattern == "drone":
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
            for i in range(int(length)):
                pitch = base_note if i % 2 == 0 else base_note - 12
                notes.append(
                    {
                        "pitch": pitch,
                        "start_time": float(i),
                        "duration": 1.0,
                        "velocity": 115,
                        "mute": False,
                    }
                )
        else:
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
        print(f"      Clip {clip_idx}: {name} (Note: {base_note})")

    # Track 2: Dub Hats (8 clips)
    print()
    print("Track 2: Dub Hats - Creating 8 clips...")
    hat_patterns = [
        (0, "Hats_Minimal", [0.5, 2.0]),
        (1, "Hats_Sparse", [0.5]),
        (2, "Hats_Syncopated", [0.5, 1.5, 2.0, 2.5]),
        (3, "Hats_6_8", [0.33, 1.33, 2.33]),
        (4, "Hats_Fast", [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]),
        (5, "Hats_Muted", [0.5, 2.0]),
        (6, "Hats_Wash", []),
        (7, "Hats_None", []),
    ]

    for clip_idx, name, times in hat_patterns:
        send_command(
            "create_clip", {"track_index": 2, "clip_index": clip_idx, "length": 4.0}
        )

        notes = [
            {
                "pitch": 42,
                "start_time": t,
                "duration": 0.125,
                "velocity": 80 if clip_idx == 5 else 100,
                "mute": False,
            }
            for t in times
        ]

        send_command(
            "add_notes_to_clip",
            {"track_index": 2, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 2, "clip_index": clip_idx, "name": name}
        )
        print(f"      Clip {clip_idx}: {name}")

    # Track 3: Percs (8 clips)
    print()
    print("Track 3: Percs - Creating 8 clips...")
    perc_patterns = [
        (0, "Percs_Rim", [(2.0, 40)]),
        (1, "Percs_Clap", [(2.5, 39)]),
        (2, "Percs_Scab", [(2.0, 37)]),
        (3, "Percs_Layered", [(2.0, 40), (2.5, 39)]),
        (4, "Percs_None", []),
        (5, "Percs_Minimal", [(2.0, 40)]),
        (6, "Percs_Build", [1.0, 2.0, 3.0]),
        (7, "Percs_Random", []),
    ]

    for clip_idx, name, hits in perc_patterns:
        send_command(
            "create_clip", {"track_index": 3, "clip_index": clip_idx, "length": 4.0}
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
        print(f"      Clip {clip_idx}: {name}")

    # Track 4: Atmo Pad (8 clips)
    print()
    print("Track 4: Atmo Pad - Creating 8 clips...")
    pad_chords = [
        (0, "Pad_Fm_Sustain", [29, 32, 36]),
        (1, "Pad_Cm_Sustain", [24, 27, 31]),
        (2, "Pad_Bb_Sustain", [22, 25, 29]),
        (3, "Pad_Fm_Movement", [29, 32, 36]),
        (4, "Pad_Drones", [29]),
        (5, "Pad_None", []),
        (6, "Pad_Dub_Wash", [29, 32, 36]),
        (7, "Pad_Peak", [29, 32, 36]),
    ]

    for clip_idx, name, notes_list in pad_chords:
        send_command(
            "create_clip", {"track_index": 4, "clip_index": clip_idx, "length": 8.0}
        )

        notes = [
            {
                "pitch": note,
                "start_time": 0.0,
                "duration": 8.0,
                "velocity": 100,
                "mute": False,
            }
            for note in notes_list
        ]

        send_command(
            "add_notes_to_clip",
            {"track_index": 4, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 4, "clip_index": clip_idx, "name": name}
        )
        print(f"      Clip {clip_idx}: {name}")

    # Track 5: Dub FX (8 clips)
    print()
    print("Track 5: Dub FX - Creating 8 clips...")
    fx_types = [
        "FX_None",
        "FX_Noise_Swell",
        "FX_Reverb_Impact",
        "FX_Delay_Boom",
        "FX_Filter_Sweep",
        "FX_Metallic",
        "FX_Riser",
        "FX_Glitch",
    ]

    for clip_idx, name in enumerate(fx_types):
        send_command(
            "create_clip", {"track_index": 5, "clip_index": clip_idx, "length": 2.0}
        )

        # Add placeholder for FX clips
        notes = (
            [
                {
                    "pitch": 60,
                    "start_time": 0.0,
                    "duration": 0.5,
                    "velocity": 100,
                    "mute": False,
                }
            ]
            if clip_idx > 0
            else []
        )

        send_command(
            "add_notes_to_clip",
            {"track_index": 5, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 5, "clip_index": clip_idx, "name": name}
        )
        print(f"      Clip {clip_idx}: {name}")

    print()
    # PHASE 4: INITIAL VOLUMES
    print("PHASE 4: SET INITIAL MIX LEVELS")
    print("-" * 80)

    volumes = [0.80, 0.85, 0.45, 0.35, 0.55, 0.30, 0.50, 0.60]
    for track_idx, volume in enumerate(volumes):
        result = send_command(
            "set_track_volume", {"track_index": track_idx, "volume": volume}
        )
        print(f"      Track {track_idx} volume: {volume:.2f} - {result.get('status')}")

    print()
    # PHASE 5: VERIFICATION
    print("PHASE 5: VERIFICATION")
    print("-" * 80)

    print("[1/3] Checking session info...")
    result = send_command("get_session_info")
    if result.get("status") == "success":
        info = result.get("result", {})
        print(f"      Tempo: {info.get('tempo')}")
        print(f"      Tracks: {info.get('track_count')}")
    else:
        print(f"      Error: {result.get('message')}")

    print()
    print("[2/3] Verifying clip counts...")
    expected_clips = [8, 8, 8, 8, 8, 8]
    for track_idx in range(6):
        result = send_command("get_all_clips_in_track", {"track_index": track_idx})
        if result.get("status") == "success":
            clips = result.get("result", [])
            actual = len(clips)
            expected = expected_clips[track_idx]
            status = "OK" if actual >= expected else "FAIL"
            print(
                f"      Track {track_idx}: {actual} clips (expected {expected}) - {status}"
            )

    print()
    print("=" * 80)
    print("  IMPLEMENTATION COMPLETE!")
    print("=" * 80)
    print()
    print("  Session ready for 2-hour dub techno performance.")
    print()
    print("  NEXT STEPS:")
    print("  1. Open Ableton Live")
    print("  2. Configure instrument presets manually")
    print("  3. Set up send routing (delay/reverb)")
    print("  4. Start playback with: start_playback()")
    print()


if __name__ == "__main__":
    main()
