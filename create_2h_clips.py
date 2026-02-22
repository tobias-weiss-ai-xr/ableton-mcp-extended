#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create 48 Clips for 2-Hour Dub Techno Mix
==========================================

Creates 8 clips per track for a 6-track dub techno session:
- Track 0: Deep Kick (Operator)
- Track 1: Sub-Bass (Operator)
- Track 2: Dub Hats (32 Pad Kit Jazz)
- Track 3: Percs (32 Pad Kit Rock)
- Track 4: Atmo Pad (Wavetable)
- Track 5: Dub FX (Simpler)

Total: 48 clips ready for 2-hour live mix
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
    print("  2-HOUR DUB TECHNO - CREATE 48 CLIPS")
    print("  6 Tracks x 8 Clips = 48 Total")
    print_separator()
    print()

    # ============================================================================
    # TRACK 0: DEEP KICK (8 clips)
    # ============================================================================
    print_section("TRACK 0: DEEP KICK - Creating 8 clips...")

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
        # Create clip
        result = send_command(
            "create_clip",
            {"track_index": 0, "clip_index": clip_idx, "length": length},
        )

        # Dub techno kick: hits on 1, skip 2, skip 3, hit on 4
        # Pattern: 0.0 (downbeat) and 3.0 (pickup to next bar)
        notes = [
            {
                "pitch": 36,
                "start_time": 0.0,
                "duration": 0.25,
                "velocity": 110,
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

        # Add variations for some patterns
        if pattern == "kick_var1":  # Punchy - add 2.5 hit
            notes.append(
                {
                    "pitch": 36,
                    "start_time": 2.5,
                    "duration": 0.25,
                    "velocity": 95,
                    "mute": False,
                }
            )
        elif pattern == "kick_var2":  # Deep - longer first note
            notes[0]["duration"] = 0.5
        elif pattern == "kick_var3":  # Sparse - only downbeat
            notes = [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 0.25,
                    "velocity": 110,
                    "mute": False,
                }
            ]
        elif pattern == "kick_var4":  # Push - add 1.5 and 2.5
            notes.extend(
                [
                    {
                        "pitch": 36,
                        "start_time": 1.5,
                        "duration": 0.25,
                        "velocity": 90,
                        "mute": False,
                    },
                    {
                        "pitch": 36,
                        "start_time": 2.5,
                        "duration": 0.25,
                        "velocity": 95,
                        "mute": False,
                    },
                ]
            )
        elif pattern == "kick_var5":  # Steady 4/4
            notes = [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 0.25,
                    "velocity": 110,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 1.0,
                    "duration": 0.25,
                    "velocity": 105,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 2.0,
                    "duration": 0.25,
                    "velocity": 105,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 3.0,
                    "duration": 0.25,
                    "velocity": 105,
                    "mute": False,
                },
            ]
        elif pattern == "kick_var6":  # Swung - offset times
            notes = [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 0.25,
                    "velocity": 110,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 2.33,
                    "duration": 0.25,
                    "velocity": 100,
                    "mute": False,
                },
            ]
        elif pattern == "kick_var7":  # Muted - lower velocity
            for n in notes:
                n["velocity"] = 70

        send_command(
            "add_notes_to_clip",
            {"track_index": 0, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 0, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.3)

    # ============================================================================
    # TRACK 1: SUB-BASS (8 clips) - HEAVY BASS
    # ============================================================================
    print_section("TRACK 1: SUB-BASS - Creating 8 clips...")

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
        elif pattern == "tremolo":
            # Rapid 16th note tremolo
            for i in range(int(length * 4)):
                notes.append(
                    {
                        "pitch": base_note,
                        "start_time": float(i) * 0.25,
                        "duration": 0.2,
                        "velocity": 100,
                        "mute": False,
                    }
                )
        elif pattern == "sweep":
            # Slow reveal sweep
            notes = [
                {
                    "pitch": base_note,
                    "start_time": 0.0,
                    "duration": length,
                    "velocity": 80,
                    "mute": False,
                }
            ]
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

    # ============================================================================
    # TRACK 2: DUB HATS (8 clips)
    # ============================================================================
    print_section("TRACK 2: DUB HATS - Creating 8 clips...")

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

        note_velocity = 70 if clip_idx == 5 else 100  # Muted hat has lower velocity

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

    # ============================================================================
    # TRACK 3: PERCS (8 clips)
    # ============================================================================
    print_section("TRACK 3: PERCS - Creating 8 clips...")

    perc_patterns = [
        (0, "Percs_Rim", 4.0, [(2.0, 40)]),  # Rim shot on beat 2
        (1, "Percs_Clap", 4.0, [(2.5, 39)]),  # Clap on 2.5
        (2, "Percs_Scab", 4.0, [(2.0, 37)]),  # Side stick on 2
        (3, "Percs_Layered", 4.0, [(2.0, 40), (2.5, 39)]),  # Rim + Clap
        (4, "Percs_None", 4.0, []),  # Silence
        (5, "Percs_Minimal", 4.0, [(2.0, 40)]),  # Single rim
        (6, "Percs_Build", 4.0, [(1.0, 40), (2.0, 40), (3.0, 40)]),  # Building hits
        (7, "Percs_Random", 4.0, [(0.5, 37), (1.75, 39), (3.25, 40)]),  # Scattered
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

    # ============================================================================
    # TRACK 4: ATMO PAD (8 clips)
    # ============================================================================
    print_section("TRACK 4: ATMO PAD - Creating 8 clips...")

    pad_chords = [
        (0, "Pad_Fm_Sustain", 8.0, [29, 32, 36]),  # F minor
        (1, "Pad_Cm_Sustain", 8.0, [24, 27, 31]),  # C minor
        (2, "Pad_Bb_Sustain", 8.0, [22, 25, 29]),  # Bb minor
        (3, "Pad_Fm_Movement", 8.0, [29, 32, 36]),  # F minor evolving
        (4, "Pad_Drones", 8.0, [29]),  # Single F drone
        (5, "Pad_None", 8.0, []),  # Silence
        (6, "Pad_Dub_Wash", 8.0, [29, 32, 36]),  # F minor washed out
        (7, "Pad_Peak", 8.0, [29, 32, 36, 41]),  # F minor + 9th (peak)
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
                        "velocity": 85,
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

    # ============================================================================
    # TRACK 5: DUB FX (8 clips)
    # ============================================================================
    print_section("TRACK 5: DUB FX - Creating 8 clips...")

    fx_types = [
        (0, "FX_None", 4.0, []),
        (
            1,
            "FX_Noise_Swell",
            4.0,
            [{"pitch": 60, "start": 0.0, "dur": 2.0, "vel": 100}],
        ),
        (
            2,
            "FX_Reverb_Impact",
            2.0,
            [{"pitch": 48, "start": 0.0, "dur": 1.0, "vel": 120}],
        ),
        (
            3,
            "FX_Delay_Boom",
            2.0,
            [{"pitch": 36, "start": 0.0, "dur": 1.5, "vel": 110}],
        ),
        (
            4,
            "FX_Filter_Sweep",
            4.0,
            [{"pitch": 72, "start": 0.5, "dur": 3.0, "vel": 90}],
        ),
        (5, "FX_Metallic", 2.0, [{"pitch": 84, "start": 0.0, "dur": 0.5, "vel": 100}]),
        (6, "FX_Riser", 4.0, [{"pitch": 60, "start": 0.0, "dur": 4.0, "vel": 110}]),
        (
            7,
            "FX_Glitch",
            2.0,
            [
                {"pitch": 67, "start": 0.25, "dur": 0.25, "vel": 100},
                {"pitch": 72, "start": 0.75, "dur": 0.25, "vel": 100},
            ],
        ),
    ]

    for clip_idx, name, length, fx_notes in fx_types:
        result = send_command(
            "create_clip", {"track_index": 5, "clip_index": clip_idx, "length": length}
        )

        notes = []
        for fx_note in fx_notes:
            notes.append(
                {
                    "pitch": fx_note["pitch"],
                    "start_time": fx_note["start"],
                    "duration": fx_note["dur"],
                    "velocity": fx_note["vel"],
                    "mute": False,
                }
            )

        send_command(
            "add_notes_to_clip",
            {"track_index": 5, "clip_index": clip_idx, "notes": notes},
        )
        send_command(
            "set_clip_name", {"track_index": 5, "clip_index": clip_idx, "name": name}
        )

        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.3)

    # ============================================================================
    # VERIFICATION
    # ============================================================================
    print_section("VERIFICATION")

    print("\nChecking clip counts per track...")
    expected_clips = {0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 8}

    total_clips = 0
    for track_idx in expected_clips:
        result = send_command("get_all_clips_in_track", {"track_index": track_idx})
        if result.get("status") == "success":
            clips = result.get("result", [])
            expected = expected_clips[track_idx]
            actual = len(clips)
            total_clips += actual
            status = "[OK]" if actual >= expected else "[WARN]"
            print(
                f"      Track {track_idx}: {actual} clips (expected {expected}) {status}"
            )
        else:
            print(f"      Track {track_idx}: Error checking clips")
        time.sleep(0.1)

    print()
    print_separator()
    print("  CLIP CREATION COMPLETE!")
    print_separator()
    print()
    print(f"  Total clips created: {total_clips}/48")
    print()
    print("  Session ready for 2-hour dub techno mix!")
    print()
    print("  NEXT STEPS:")
    print("  1. Load samples into Simpler on Track 5 (Dub FX)")
    print("  2. Configure Wavetable presets on Track 4 (Atmo Pad)")
    print("  3. Set up send routing (delay/reverb) if needed")
    print("  4. Start playback: fire_clip(track_index, clip_index)")
    print()
    print("  DJ PERFORMANCE TIPS:")
    print("  - Change ONE clip at a time")
    print("  - Wait 4-8 bars between changes")
    print("  - Use gradual parameter sweeps")
    print("  - Heavy bass focus (Track 1 volume: 0.85-0.95)")
    print()
    print_separator()


if __name__ == "__main__":
    main()
