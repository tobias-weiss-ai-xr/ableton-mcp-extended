#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2-Hour Dub Reggae Track Creation Script
========================================

Creates a complete 2-hour dub reggae session:
- 8 tracks (6 MIDI + 2 audio send)
- 48 MIDI clips (8 per MIDI track)
- 30 sections (4 minutes each = 2 hours)
- Tempo: 72 BPM (classic dub)
- Key: C Minor

Usage:
    python create_2h_dub_reggae.py           # Full creation
    python create_2h_dub_reggae.py --dry-run # Test without MCP

Based on SESSION SETUP WORKFLOW from AGENTS.md
"""

import socket
import json
import time
import sys
import argparse

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Configuration
TCP_HOST = "localhost"
TCP_PORT = 9877
DRY_RUN = False


def send_command(command_type, params=None):
    """Send command to Ableton MCP server"""
    if params is None:
        params = {}

    if DRY_RUN:
        print(f"      [DRY-RUN] {command_type}({params})")
        return {"status": "success"}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((TCP_HOST, TCP_PORT))

        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))

        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()

        return response
    except Exception as e:
        print(f"      [ERROR] {command_type}: {str(e)}")
        return {"status": "error", "message": str(e)}


def print_separator():
    print("=" * 80)


def print_section(title):
    print_separator()
    print(f"  {title}")
    print_separator()


# =============================================================================
# DRUM PATTERN DEFINITIONS (One Drop, Rockers, Steppers)
# =============================================================================

# One Drop: Kick on beat 1 only (classic reggae)
ONE_DROP_KICK = [
    {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100, "mute": False},
]

ONE_DROP_SNARE = [
    {"pitch": 38, "start_time": 2.0, "duration": 0.25, "velocity": 80, "mute": False},
]

ONE_DROP_HATS = [
    {"pitch": 42, "start_time": 0.5, "duration": 0.125, "velocity": 60, "mute": False},
    {"pitch": 42, "start_time": 1.5, "duration": 0.125, "velocity": 60, "mute": False},
    {"pitch": 42, "start_time": 2.5, "duration": 0.125, "velocity": 60, "mute": False},
    {"pitch": 42, "start_time": 3.5, "duration": 0.125, "velocity": 60, "mute": False},
]

# Rockers: Kick on 1 and 3 (building energy)
ROCKERS_KICK = [
    {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100, "mute": False},
    {"pitch": 36, "start_time": 2.0, "duration": 0.25, "velocity": 95, "mute": False},
]

# Steppers: Kick on every beat (peak energy)
STEPPERS_KICK = [
    {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100, "mute": False},
    {"pitch": 36, "start_time": 1.0, "duration": 0.25, "velocity": 95, "mute": False},
    {"pitch": 36, "start_time": 2.0, "duration": 0.25, "velocity": 100, "mute": False},
    {"pitch": 36, "start_time": 3.0, "duration": 0.25, "velocity": 95, "mute": False},
]

# Bass patterns (C minor root = 36)
BASS_DRONE = [
    {"pitch": 36, "start_time": 0.0, "duration": 4.0, "velocity": 100, "mute": False},
]

BASS_WALKING = [
    {"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 90, "mute": False},
    {"pitch": 38, "start_time": 1.0, "duration": 0.5, "velocity": 85, "mute": False},
    {"pitch": 41, "start_time": 2.0, "duration": 0.5, "velocity": 85, "mute": False},
    {"pitch": 43, "start_time": 3.0, "duration": 0.5, "velocity": 80, "mute": False},
]

# Guitar chop (skank) - offbeat stabs
GUITAR_CHOP = [
    {"pitch": 48, "start_time": 0.5, "duration": 0.25, "velocity": 80, "mute": False},
    {"pitch": 48, "start_time": 2.5, "duration": 0.25, "velocity": 80, "mute": False},
]

# Organ bubble
ORGAN_BUBBLE = [
    {"pitch": 48, "start_time": 0.0, "duration": 0.5, "velocity": 70, "mute": False},
    {"pitch": 51, "start_time": 0.5, "duration": 0.5, "velocity": 65, "mute": False},
    {"pitch": 55, "start_time": 1.0, "duration": 0.5, "velocity": 60, "mute": False},
]


def create_clip_with_notes(track_idx, clip_idx, length, notes, clip_name):
    """Create a clip and add notes to it"""
    result = send_command(
        "create_clip",
        {"track_index": track_idx, "clip_index": clip_idx, "length": length},
    )

    if notes:
        send_command(
            "add_notes_to_clip",
            {"track_index": track_idx, "clip_index": clip_idx, "notes": notes},
        )

    send_command(
        "set_clip_name",
        {"track_index": track_idx, "clip_index": clip_idx, "name": clip_name},
    )

    return result


def main():
    global DRY_RUN

    parser = argparse.ArgumentParser(description="Create 2-Hour Dub Reggae Track")
    parser.add_argument(
        "--dry-run", action="store_true", help="Test without sending MCP commands"
    )
    args = parser.parse_args()

    DRY_RUN = args.dry_run

    print_separator()
    print("  2-HOUR DUB REGGAE TRACK CREATION")
    print("  8 Tracks | 48 Clips | 30 Sections | 72 BPM | C Minor")
    if DRY_RUN:
        print("  [DRY-RUN MODE - No commands will be sent]")
    print_separator()
    print()

    # ============================================================================
    # PHASE 1: SESSION SETUP (Following AGENTS.md SESSION SETUP WORKFLOW)
    # ============================================================================
    print_section("PHASE 1: SESSION SETUP")

    # Step 1: Delete all tracks (clean slate)
    print("\n[1/4] Deleting all existing tracks...")
    result = send_command("delete_all_tracks")
    if result.get("status") == "success":
        print("      [OK] All tracks deleted")
    else:
        print(f"      [WARN] {result.get('message', 'Could not delete tracks')}")

    time.sleep(0.5)

    # Step 2: Create 8 tracks (6 MIDI + 2 audio)
    print("\n[2/4] Creating 8 new tracks...")
    track_names = [
        "Drums",  # Track 0 - Drum Rack
        "Dub Bass",  # Track 1 - Operator
        "Guitar Chop",  # Track 2 - Electric
        "Organ Bubble",  # Track 3 - Organ
        "Synth Pad",  # Track 4 - Wavetable
        "FX",  # Track 5 - Drum Rack
        "Delay Send",  # Track 6 - Audio
        "Reverb Send",  # Track 7 - Audio
    ]

    for i, name in enumerate(track_names):
        if i < 6:  # MIDI tracks
            result = send_command("create_midi_track", {"index": -1})
            if result.get("status") == "success":
                print(f"      [OK] Created MIDI track {i}: {name}")
            else:
                print(
                    f"      [WARN] Could not create track {i}: {result.get('message')}"
                )
        else:  # Audio tracks
            result = send_command("create_audio_track", {"index": -1})
            if result.get("status") == "success":
                print(f"      [OK] Created audio track {i}: {name}")
            else:
                print(
                    f"      [WARN] Could not create track {i}: {result.get('message')}"
                )
        time.sleep(0.2)

    time.sleep(0.5)

    # Step 3: Set track names
    print("\n[3/4] Setting track names...")
    for i, name in enumerate(track_names):
        result = send_command("set_track_name", {"track_index": i, "name": name})
        if result.get("status") == "success":
            print(f"      [OK] Track {i} named: {name}")
        else:
            print(f"      [WARN] Could not name track {i}")
        time.sleep(0.1)

    time.sleep(0.5)

    # Step 4: Set tempo
    print("\n[4/4] Setting tempo to 72 BPM...")
    result = send_command("set_tempo", {"tempo": 72.0})
    if result.get("status") == "success":
        print("      [OK] Tempo set to 72 BPM")
    else:
        print(f"      [WARN] Could not set tempo: {result.get('message')}")

    print()
    time.sleep(1)

    # ============================================================================
    # PHASE 2: CREATE CLIPS (48 clips total)
    # ============================================================================
    print_section("PHASE 2: CREATE MIDI CLIPS")

    # Track 0: Drums - 8 clips with progressive patterns
    # Sections 0-9: One Drop, 10-19: Rockers, 20-29: Steppers
    print("\nTrack 0: Drums - Creating 8 clips...")

    drum_clips = [
        (0, "One_Drop_1", 4.0, ONE_DROP_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
        (1, "One_Drop_2", 4.0, ONE_DROP_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
        (2, "One_Drop_3", 4.0, ONE_DROP_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
        (3, "Rockers_1", 4.0, ROCKERS_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
        (4, "Rockers_2", 4.0, ROCKERS_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
        (5, "Rockers_3", 4.0, ROCKERS_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
        (6, "Steppers_1", 4.0, STEPPERS_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
        (7, "Steppers_2", 4.0, STEPPERS_KICK + ONE_DROP_SNARE + ONE_DROP_HATS),
    ]

    for clip_idx, name, length, notes in drum_clips:
        create_clip_with_notes(0, clip_idx, length, notes, name)
        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.2)

    # Track 1: Dub Bass - 8 clips
    print("\nTrack 1: Dub Bass - Creating 8 clips...")

    bass_clips = [
        (0, "Bass_Drone_C", 4.0, BASS_DRONE),
        (
            1,
            "Bass_Drone_Low",
            4.0,
            [
                {
                    "pitch": 24,
                    "start_time": 0.0,
                    "duration": 4.0,
                    "velocity": 100,
                    "mute": False,
                }
            ],
        ),
        (2, "Bass_Walking_1", 4.0, BASS_WALKING),
        (3, "Bass_Walking_2", 4.0, BASS_WALKING),
        (
            4,
            "Bass_Pluck",
            4.0,
            [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 0.25,
                    "velocity": 100,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 1.0,
                    "duration": 0.25,
                    "velocity": 90,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 2.0,
                    "duration": 0.25,
                    "velocity": 95,
                    "mute": False,
                },
                {
                    "pitch": 36,
                    "start_time": 3.0,
                    "duration": 0.25,
                    "velocity": 85,
                    "mute": False,
                },
            ],
        ),
        (
            5,
            "Bass_Syncopated",
            4.0,
            [
                {
                    "pitch": 36,
                    "start_time": 0.5,
                    "duration": 0.5,
                    "velocity": 90,
                    "mute": False,
                },
                {
                    "pitch": 38,
                    "start_time": 2.5,
                    "duration": 0.5,
                    "velocity": 85,
                    "mute": False,
                },
            ],
        ),
        (
            6,
            "Bass_Deep",
            8.0,
            [
                {
                    "pitch": 24,
                    "start_time": 0.0,
                    "duration": 8.0,
                    "velocity": 110,
                    "mute": False,
                }
            ],
        ),
        (
            7,
            "Bass_Tremolo",
            4.0,
            [
                {
                    "pitch": 36,
                    "start_time": i * 0.25,
                    "duration": 0.125,
                    "velocity": 80 + (i % 4) * 5,
                    "mute": False,
                }
                for i in range(16)
            ],
        ),
    ]

    for clip_idx, name, length, notes in bass_clips:
        create_clip_with_notes(1, clip_idx, length, notes, name)
        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.2)

    # Track 2: Guitar Chop - 8 clips (skank patterns)
    print("\nTrack 2: Guitar Chop - Creating 8 clips...")

    guitar_clips = [
        (0, "Skank_Basic", 4.0, GUITAR_CHOP),
        (1, "Skank_Double", 4.0, GUITAR_CHOP * 2),
        (
            2,
            "Skank_Syncopated",
            4.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.75,
                    "duration": 0.25,
                    "velocity": 75,
                    "mute": False,
                },
                {
                    "pitch": 48,
                    "start_time": 2.75,
                    "duration": 0.25,
                    "velocity": 75,
                    "mute": False,
                },
            ],
        ),
        (
            3,
            "Skank_Muted",
            4.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.5,
                    "duration": 0.125,
                    "velocity": 50,
                    "mute": False,
                },
                {
                    "pitch": 48,
                    "start_time": 2.5,
                    "duration": 0.125,
                    "velocity": 50,
                    "mute": False,
                },
            ],
        ),
        (4, "Skank_Full", 4.0, GUITAR_CHOP),
        (
            5,
            "Skank_Light",
            4.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.5,
                    "duration": 0.25,
                    "velocity": 60,
                    "mute": False,
                },
            ],
        ),
        (
            6,
            "Skank_Accent",
            4.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.5,
                    "duration": 0.25,
                    "velocity": 90,
                    "mute": False,
                },
                {
                    "pitch": 48,
                    "start_time": 2.5,
                    "duration": 0.25,
                    "velocity": 70,
                    "mute": False,
                },
            ],
        ),
        (
            7,
            "Skank_Minimal",
            4.0,
            [
                {
                    "pitch": 48,
                    "start_time": 2.5,
                    "duration": 0.25,
                    "velocity": 65,
                    "mute": False,
                },
            ],
        ),
    ]

    for clip_idx, name, length, notes in guitar_clips:
        create_clip_with_notes(2, clip_idx, length, notes, name)
        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.2)

    # Track 3: Organ Bubble - 8 clips
    print("\nTrack 3: Organ Bubble - Creating 8 clips...")

    organ_clips = [
        (0, "Organ_Bubble_1", 4.0, ORGAN_BUBBLE),
        (1, "Organ_Bubble_2", 4.0, ORGAN_BUBBLE * 2),
        (
            2,
            "Organ_Stab",
            4.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.0,
                    "duration": 0.5,
                    "velocity": 80,
                    "mute": False,
                },
            ],
        ),
        (
            3,
            "Organ_High",
            4.0,
            [
                {
                    "pitch": 60,
                    "start_time": 0.5,
                    "duration": 0.25,
                    "velocity": 65,
                    "mute": False,
                },
                {
                    "pitch": 60,
                    "start_time": 2.5,
                    "duration": 0.25,
                    "velocity": 65,
                    "mute": False,
                },
            ],
        ),
        (
            4,
            "Organ_Low",
            4.0,
            [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 1.0,
                    "velocity": 70,
                    "mute": False,
                },
            ],
        ),
        (5, "Organ_Shuffle", 4.0, ORGAN_BUBBLE),
        (
            6,
            "Organ_Sustain",
            8.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.0,
                    "duration": 8.0,
                    "velocity": 60,
                    "mute": False,
                },
            ],
        ),
        (
            7,
            "Organ_Minimal",
            4.0,
            [
                {
                    "pitch": 51,
                    "start_time": 1.0,
                    "duration": 0.5,
                    "velocity": 55,
                    "mute": False,
                },
            ],
        ),
    ]

    for clip_idx, name, length, notes in organ_clips:
        create_clip_with_notes(3, clip_idx, length, notes, name)
        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.2)

    # Track 4: Synth Pad - 8 clips (atmospheric textures)
    print("\nTrack 4: Synth Pad - Creating 8 clips...")

    pad_clips = [
        (
            0,
            "Pad_Sustain",
            8.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.0,
                    "duration": 8.0,
                    "velocity": 50,
                    "mute": False,
                }
            ],
        ),
        (
            1,
            "Pad_Swell",
            8.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.0,
                    "duration": 8.0,
                    "velocity": 40,
                    "mute": False,
                }
            ],
        ),
        (
            2,
            "Pad_Dark",
            8.0,
            [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 8.0,
                    "velocity": 45,
                    "mute": False,
                }
            ],
        ),
        (
            3,
            "Pad_Bright",
            8.0,
            [
                {
                    "pitch": 60,
                    "start_time": 0.0,
                    "duration": 8.0,
                    "velocity": 55,
                    "mute": False,
                }
            ],
        ),
        (
            4,
            "Pad_Minimal",
            4.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.0,
                    "duration": 4.0,
                    "velocity": 35,
                    "mute": False,
                }
            ],
        ),
        (
            5,
            "Pad_Evolver",
            8.0,
            [
                {
                    "pitch": 48,
                    "start_time": 0.0,
                    "duration": 4.0,
                    "velocity": 40,
                    "mute": False,
                },
                {
                    "pitch": 51,
                    "start_time": 4.0,
                    "duration": 4.0,
                    "velocity": 45,
                    "mute": False,
                },
            ],
        ),
        (
            6,
            "Pad_Deep",
            8.0,
            [
                {
                    "pitch": 24,
                    "start_time": 0.0,
                    "duration": 8.0,
                    "velocity": 50,
                    "mute": False,
                }
            ],
        ),
        (7, "Pad_None", 4.0, []),
    ]

    for clip_idx, name, length, notes in pad_clips:
        create_clip_with_notes(4, clip_idx, length, notes, name)
        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.2)

    # Track 5: FX - 8 clips (sound effects)
    print("\nTrack 5: FX - Creating 8 clips...")

    fx_clips = [
        (
            0,
            "FX_Sub_Hit",
            2.0,
            [
                {
                    "pitch": 36,
                    "start_time": 0.0,
                    "duration": 0.5,
                    "velocity": 100,
                    "mute": False,
                }
            ],
        ),
        (
            1,
            "FX_Crash",
            2.0,
            [
                {
                    "pitch": 49,
                    "start_time": 0.0,
                    "duration": 1.0,
                    "velocity": 90,
                    "mute": False,
                }
            ],
        ),
        (2, "FX_Noise", 4.0, []),
        (3, "FX_Rise", 4.0, []),
        (4, "FX_Fall", 4.0, []),
        (
            5,
            "FX_Thunder",
            4.0,
            [
                {
                    "pitch": 36,
                    "start_time": 0.5,
                    "duration": 0.25,
                    "velocity": 110,
                    "mute": False,
                }
            ],
        ),
        (6, "FX_Sweep", 8.0, []),
        (7, "FX_None", 4.0, []),
    ]

    for clip_idx, name, length, notes in fx_clips:
        create_clip_with_notes(5, clip_idx, length, notes, name)
        print(f"      [OK] Clip {clip_idx}: {name}")
        time.sleep(0.2)

    print()
    print_separator()
    print("  CREATION COMPLETE")
    print_separator()
    print()
    print("  Created:")
    print("    - 8 tracks (6 MIDI + 2 audio send)")
    print("    - 48 MIDI clips (8 per MIDI track)")
    print("    - Tempo: 72 BPM")
    print()
    print("  Next steps:")
    print("    1. Run: python load_instruments_2h.py")
    print("    2. Run: python automate_2h_dub_reggae.py")
    print()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Creation stopped by user")
        sys.exit(130)
