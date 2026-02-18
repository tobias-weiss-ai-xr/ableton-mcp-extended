import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return the response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


print("=" * 80)
print("CREATING 32-BAR EXTENDED DUB TECHNO PATTERNS")
print("=" * 80)
print(f"Tempo: 126 BPM")
print(f"Pattern length: 32 bars")
print(f"More elements per pattern for greater complexity")
print("=" * 80)

# Set tempo first
print("\nSetting tempo to 126 BPM...")
send_command("set_tempo", {"tempo": 126.0})
print("   [OK] Tempo set to 126 BPM")

# ============================================================================
# TRACK CREATION
# ============================================================================

# Track 0: Kick (create new track at the end)
print("\n[1/6] Creating Kick track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
kick_track_index = session_info["result"]["track_count"] - 1
send_command("set_track_name", {"track_index": kick_track_index, "name": "Kick 32bar"})
print(f"   [OK] Created Kick track (Track {kick_track_index})")

# Track 1: Sub-bass
print("[2/6] Creating Sub-bass track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
bass_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": bass_track_index, "name": "Sub-bass 32bar"}
)
print(f"   [OK] Created Sub-bass track (Track {bass_track_index})")

# Track 2: Hi-hats
print("[3/6] Creating Hi-hat track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
hihat_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": hihat_track_index, "name": "Hi-hats 32bar"}
)
print(f"   [OK] Created Hi-hat track (Track {hihat_track_index})")

# Track 3: Synth Pads
print("[4/6] Creating Synth Pads track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
pad_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": pad_track_index, "name": "Synth Pads 32bar"}
)
print(f"   [OK] Created Synth Pads track (Track {pad_track_index})")

# Track 4: FX
print("[5/6] Creating FX track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
fx_track_index = session_info["result"]["track_count"] - 1
send_command("set_track_name", {"track_index": fx_track_index, "name": "FX 32bar"})
print(f"   [OK] Created FX track (Track {fx_track_index})")

# Track 5: Dub Delays (send track)
print("[6/6] Creating Dub Delays track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
delay_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": delay_track_index, "name": "Dub Delays 32bar"}
)
print(f"   [OK] Created Dub Delays track (Track {delay_track_index})")

print("\n" + "=" * 80)
print("ALL TRACKS CREATED")
print("=" * 80)

# ============================================================================
# KICK CLIPS - Extended 32-bar patterns
# ============================================================================
print("\nCreating Kick clips (32 bars)...")


def create_32bar_kick_pattern(base_velocity=110, extra_kicks=None, missing_beats=None):
    """Generate a 32-bar kick pattern with variations"""
    notes = []
    for bar in range(32):
        bar_start = bar * 4.0

        # Add the four main beats per bar
        for beat in range(4):
            if missing_beats and bar in missing_beats and beat in [0, 2]:
                continue

            start = bar_start + beat

            # Add variation on velocity
            velocity = base_velocity
            if bar % 4 == 2:
                velocity += 5  # Bars 8-12 slightly louder
            elif bar % 4 == 3:
                velocity -= 5  # Bars 12-16 slightly softer

            # Add swing variation
            if bar % 8 in [3, 7]:
                start += 0.025  # Subtle swing

            notes.append(
                {
                    "pitch": 36,
                    "start_time": start,
                    "duration": 0.25,
                    "velocity": min(127, max(1, velocity)),
                    "mute": False,
                }
            )

    # Add extra kicks for specific bars
    if extra_kicks:
        for bar, positions in extra_kicks.items():
            bar_start = bar * 4.0
            for pos in positions:
                notes.append(
                    {
                        "pitch": 36,
                        "start_time": bar_start + pos,
                        "duration": 0.15,
                        "velocity": 95,
                        "mute": False,
                    }
                )

    return sorted(notes, key=lambda x: x["start_time"])


kick_clips = [
    {
        "notes": create_32bar_kick_pattern(110),
        "name": "Kick Basic 32bar",
    },
    {
        "notes": create_32bar_kick_pattern(
            110,
            extra_kicks={15: [1.75, 3.75], 23: [1.75, 3.75], 31: [1.75, 3.75]},
        ),
        "name": "Kick Syncopated 32bar",
    },
    {
        "notes": create_32bar_kick_pattern(
            115,
            missing_beats={16: None, 24: None},
        ),
        "name": "Kick Emphasis 32bar",
    },
    {
        "notes": create_32bar_kick_pattern(105),
        "name": "Kick Soft 32bar",
    },
    {
        "notes": create_32bar_kick_pattern(
            110,
            extra_kicks={8: [0.5, 1.5, 2.5, 3.5], 24: [0.5, 1.5, 2.5, 3.5]},
        ),
        "name": "Kick Doubletime 32bar",
    },
]

for clip_idx, clip_data in enumerate(kick_clips):
    send_command(
        "create_clip",
        {"track_index": kick_track_index, "clip_index": clip_idx, "length": 32.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": kick_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": kick_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(
        f"   [OK] Created Clip {clip_idx}: {clip_data['name']} ({len(clip_data['notes'])} notes)"
    )

# ============================================================================
# SUB-BASS CLIPS - Extended 32-bar patterns
# ============================================================================
print("\nCreating Sub-bass clips (32 bars)...")


def create_32bar_bass_pattern(root_note=36, variation="minimal"):
    """Generate a 32-bar bass pattern with evolution"""
    notes = []

    for bar in range(32):
        bar_start = bar * 4.0

        if variation == "minimal":
            # Simple drone with subtle changes
            velocity = 100 if bar % 8 < 4 else 95

            # Root note drone
            notes.append(
                {
                    "pitch": root_note,
                    "start_time": bar_start,
                    "duration": 4.0,
                    "velocity": velocity,
                    "mute": False,
                }
            )

            # Occasional octave drop
            if bar % 16 == 8:
                notes.append(
                    {
                        "pitch": root_note - 12,
                        "start_time": bar_start + 2.0,
                        "duration": 2.0,
                        "velocity": 90,
                        "mute": False,
                    }
                )

        elif variation == "evolving":
            # More movement and variation
            if bar % 8 == 0:
                # Root drone
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start,
                        "duration": 4.0,
                        "velocity": 100,
                        "mute": False,
                    }
                )
            elif bar % 8 == 1:
                # Root + 5th
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start,
                        "duration": 2.0,
                        "velocity": 100,
                        "mute": False,
                    }
                )
                notes.append(
                    {
                        "pitch": root_note + 7,
                        "start_time": bar_start + 2.0,
                        "duration": 2.0,
                        "velocity": 95,
                        "mute": False,
                    }
                )
            elif bar % 8 == 2:
                # Syncopated
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start,
                        "duration": 2.5,
                        "velocity": 100,
                        "mute": False,
                    }
                )
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start + 2.75,
                        "duration": 1.25,
                        "velocity": 95,
                        "mute": False,
                    }
                )
            else:
                # Minimal
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start,
                        "duration": 4.0,
                        "velocity": 95,
                        "mute": False,
                    }
                )

        elif variation == "complex":
            # Complex pattern with many changes
            if bar % 4 == 0:
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start,
                        "duration": 4.0,
                        "velocity": 100,
                        "mute": False,
                    }
                )
            elif bar % 4 == 1:
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start,
                        "duration": 1.0,
                        "velocity": 105,
                        "mute": False,
                    }
                )
                notes.append(
                    {
                        "pitch": root_note + 3,
                        "start_time": bar_start + 1.0,
                        "duration": 1.0,
                        "velocity": 95,
                        "mute": False,
                    }
                )
                notes.append(
                    {
                        "pitch": root_note + 5,
                        "start_time": bar_start + 2.0,
                        "duration": 1.0,
                        "velocity": 95,
                        "mute": False,
                    }
                )
                notes.append(
                    {
                        "pitch": root_note + 7,
                        "start_time": bar_start + 3.0,
                        "duration": 1.0,
                        "velocity": 90,
                        "mute": False,
                    }
                )
            elif bar % 4 == 2:
                notes.append(
                    {
                        "pitch": root_note - 12,
                        "start_time": bar_start,
                        "duration": 2.0,
                        "velocity": 90,
                        "mute": False,
                    }
                )
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start + 2.0,
                        "duration": 2.0,
                        "velocity": 100,
                        "mute": False,
                    }
                )
            else:
                notes.append(
                    {
                        "pitch": root_note,
                        "start_time": bar_start,
                        "duration": 2.0,
                        "velocity": 100,
                        "mute": False,
                    }
                )
                notes.append(
                    {
                        "pitch": root_note + 2,
                        "start_time": bar_start + 2.0,
                        "duration": 2.0,
                        "velocity": 95,
                        "mute": False,
                    }
                )

    return sorted(notes, key=lambda x: x["start_time"])


bass_clips = [
    {
        "notes": create_32bar_bass_pattern(36, "minimal"),
        "name": "Bass Minimal Drone 32bar",
    },
    {
        "notes": create_32bar_bass_pattern(41, "evolving"),
        "name": "Bass Evolving 32bar",
    },
    {
        "notes": create_32bar_bass_pattern(36, "complex"),
        "name": "Bass Complex 32bar",
    },
    {
        "notes": create_32bar_bass_pattern(43, "minimal"),
        "name": "Bass G Drone 32bar",
    },
]

for clip_idx, clip_data in enumerate(bass_clips):
    send_command(
        "create_clip",
        {"track_index": bass_track_index, "clip_index": clip_idx, "length": 32.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": bass_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": bass_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(
        f"   [OK] Created Clip {clip_idx}: {clip_data['name']} ({len(clip_data['notes'])} notes)"
    )

# ============================================================================
# HI-HAT CLIPS - Extended 32-bar patterns
# ============================================================================
print("\nCreating Hi-hat clips (32 bars)...")


def create_32bar_hihat_pattern(density="sparse", swing=False):
    """Generate a 32-bar hi-hat pattern with varying density"""
    notes = []

    for bar in range(32):
        bar_start = bar * 4.0

        # Build up density every 8 bars
        density_factor = min(1.0, (bar % 8) / 4.0) if bar % 16 < 8 else 1.0

        if density == "sparse":
            # Sparse offbeat pattern
            if bar % 4 < 2:
                for beat in [0.5, 1.5, 2.5, 3.5]:
                    if density_factor >= 0.5 or bar % 8 in [0, 1]:
                        pos = beat + (0.05 if swing and bar % 4 == 1 else 0)
                        notes.append(
                            {
                                "pitch": 76,
                                "start_time": bar_start + pos,
                                "duration": 0.1,
                                "velocity": 65 + (bar % 4) * 2,
                                "mute": False,
                            }
                        )

        elif density == "medium":
            # Medium density with 8ths
            if bar % 2 == 0:
                for beat in [0.5, 1.5, 2.5, 3.5]:
                    notes.append(
                        {
                            "pitch": 76,
                            "start_time": bar_start + beat,
                            "duration": 0.1,
                            "velocity": 68 + (bar % 8) * 3,
                            "mute": False,
                        }
                    )
            else:
                for pos in [0.5, 1.0, 1.5, 2.5, 3.0, 3.5]:
                    swing_offset = 0.025 if swing and pos in [0.5, 1.5, 2.5, 3.5] else 0
                    notes.append(
                        {
                            "pitch": 76,
                            "start_time": bar_start + pos + swing_offset,
                            "duration": 0.08,
                            "velocity": 65,
                            "mute": False,
                        }
                    )

        elif density == "dense":
            # Dense 16th notes with variation
            if bar % 16 < 8:
                for i in range(16):
                    pos = i * 0.25
                    if pos not in [0, 4, 8, 12]:  # Skip beats
                        notes.append(
                            {
                                "pitch": 76,
                                "start_time": bar_start + pos,
                                "duration": 0.05,
                                "velocity": 60 + (i % 4) * 3,
                                "mute": False,
                            }
                        )
            else:
                for pos in [0.5, 0.75, 1.5, 1.75, 2.5, 2.75, 3.5, 3.75]:
                    notes.append(
                        {
                            "pitch": 76,
                            "start_time": bar_start + pos,
                            "duration": 0.05,
                            "velocity": 62 + (pos % 1) * 5,
                            "mute": False,
                        }
                    )

        elif density == "evolving":
            # Evolving density through the pattern
            local_density = min(0.5, bar / 32.0) + 0.3

            if local_density > 0.4:
                for pos in [0.5, 1.5, 2.5, 3.5]:
                    notes.append(
                        {
                            "pitch": 76,
                            "start_time": bar_start + pos,
                            "duration": 0.1,
                            "velocity": 65 + bar % 5,
                            "mute": False,
                        }
                    )

            if local_density > 0.5 and bar % 4 in [2, 3]:
                for pos in [1.0, 3.0]:
                    notes.append(
                        {
                            "pitch": 76,
                            "start_time": bar_start + pos,
                            "duration": 0.05,
                            "velocity": 60,
                            "mute": False,
                        }
                    )

            if local_density > 0.6 and bar % 8 in [4, 5, 6, 7]:
                for pos in [0.75, 1.75, 2.75, 3.75]:
                    notes.append(
                        {
                            "pitch": 76,
                            "start_time": bar_start + pos,
                            "duration": 0.05,
                            "velocity": 58,
                            "mute": False,
                        }
                    )

    return sorted(notes, key=lambda x: x["start_time"])


hihat_clips = [
    {
        "notes": create_32bar_hihat_pattern("sparse", False),
        "name": "Hi-hat Sparse 32bar",
    },
    {
        "notes": create_32bar_hihat_pattern("medium", True),
        "name": "Hi-hat Medium Swing 32bar",
    },
    {
        "notes": create_32bar_hihat_pattern("dense", False),
        "name": "Hi-hat Dense 32bar",
    },
    {
        "notes": create_32bar_hihat_pattern("evolving", True),
        "name": "Hi-hat Evolving 32bar",
    },
]

for clip_idx, clip_data in enumerate(hihat_clips):
    send_command(
        "create_clip",
        {"track_index": hihat_track_index, "clip_index": clip_idx, "length": 32.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": hihat_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": hihat_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(
        f"   [OK] Created Clip {clip_idx}: {clip_data['name']} ({len(clip_data['notes'])} notes)"
    )

# ============================================================================
# SYNTH PADS CLIPS - Extended 32-bar patterns
# ============================================================================
print("\nCreating Synth Pads clips (32 bars)...")


def create_32bar_pad_pattern(chord_type="minor", evolution="gradual"):
    """Generate a 32-bar pad pattern with chord evolution"""
    notes = []

    chords = {
        "minor": [(48, 51, 55), (53, 56, 60), (55, 58, 62), (51, 55, 58)],
        "major": [(48, 52, 55), (53, 57, 60), (55, 59, 62), (52, 55, 59)],
        "diminished": [(48, 51, 54), (51, 54, 57), (54, 57, 60), (48, 54, 57)],
    }

    chord_sequence = chords[chord_type]

    for bar in range(32):
        bar_start = bar * 4.0

        # Determine which chord to use
        chord_idx = (bar // 8) % len(chord_sequence)
        chord = chord_sequence[chord_idx]

        # Add chord notes with subtle variations
        for note_pitch in chord:
            # Velocity evolution
            velocity = 50 + (bar % 4) * 3

            if evolution == "gradual":
                # Slow evolution
                if bar % 16 == 8:
                    velocity += 5

            # Add the chord
            notes.append(
                {
                    "pitch": note_pitch,
                    "start_time": bar_start,
                    "duration": 4.0,
                    "velocity": velocity,
                    "mute": False,
                }
            )

        # Add additional notes for evolution
        if evolution == "gradual":
            if bar % 8 == 4 and bar > 8:
                # Add 7th for tension
                notes.append(
                    {
                        "pitch": chord[2] + 2,
                        "start_time": bar_start + 2.0,
                        "duration": 2.0,
                        "velocity": 40,
                        "mute": False,
                    }
                )

            if bar % 16 == 12:
                # Add high drone
                notes.append(
                    {
                        "pitch": chord[0] + 24,
                        "start_time": bar_start,
                        "duration": 4.0,
                        "velocity": 35,
                        "mute": False,
                    }
                )

        elif evolution == "dynamic":
            # More dynamic changes
            if bar % 4 == 0:
                # Full chord
                pass
            elif bar % 4 == 1:
                # Remove top note
                notes[-1]["duration"] = 1.0
            elif bar % 4 == 2:
                # Add 7th
                notes.append(
                    {
                        "pitch": chord[2] + 2,
                        "start_time": bar_start + 1.0,
                        "duration": 3.0,
                        "velocity": 45,
                        "mute": False,
                    }
                )
            else:
                # Minimal
                for note in notes[-3:]:
                    note["duration"] = 2.0
                notes.append(
                    {
                        "pitch": chord[0],
                        "start_time": bar_start + 2.0,
                        "duration": 2.0,
                        "velocity": 50,
                        "mute": False,
                    }
                )

    return sorted(notes, key=lambda x: x["start_time"])


pad_clips = [
    {
        "notes": create_32bar_pad_pattern("minor", "gradual"),
        "name": "Pad Minor Gradual 32bar",
    },
    {
        "notes": create_32bar_pad_pattern("major", "gradual"),
        "name": "Pad Major Gradual 32bar",
    },
    {
        "notes": create_32bar_pad_pattern("minor", "dynamic"),
        "name": "Pad Minor Dynamic 32bar",
    },
    {
        "notes": create_32bar_pad_pattern("diminished", "gradual"),
        "name": "Pad Diminished 32bar",
    },
]

for clip_idx, clip_data in enumerate(pad_clips):
    send_command(
        "create_clip",
        {"track_index": pad_track_index, "clip_index": clip_idx, "length": 32.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": pad_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": pad_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(
        f"   [OK] Created Clip {clip_idx}: {clip_data['name']} ({len(clip_data['notes'])} notes)"
    )

# ============================================================================
# FX CLIPS - Extended 32-bar patterns
# ============================================================================
print("\nCreating FX clips (32 bars)...")


def create_32bar_fx_pattern(fx_type="sweep", frequency="regular"):
    """Generate a 32-bar FX pattern with varying frequency"""
    notes = []

    if fx_type == "sweep":
        # Noise sweeps
        positions = []
        if frequency == "regular":
            positions = list(range(4, 32, 4))  # Every 4 bars
        elif frequency == "frequent":
            positions = list(range(2, 32, 2))  # Every 2 bars
        elif frequency == "sparse":
            positions = [8, 16, 24, 31]  # Occasional

        for bar in positions:
            bar_start = bar * 4.0
            notes.append(
                {
                    "pitch": 60,
                    "start_time": bar_start + 3.0,
                    "duration": 1.0,
                    "velocity": 70 + (bar % 8) * 5,
                    "mute": False,
                }
            )

    elif fx_type == "impact":
        # Impacts and hits
        positions = []
        if frequency == "regular":
            positions = [0, 8, 16, 24]
        elif frequency == "frequent":
            positions = [0, 4, 8, 12, 16, 20, 24, 28]
        elif frequency == "sparse":
            positions = [0, 16]

        for bar in positions:
            bar_start = bar * 4.0
            notes.append(
                {
                    "pitch": 60,
                    "start_time": bar_start,
                    "duration": 0.2,
                    "velocity": 90 + (bar % 16) * 2,
                    "mute": False,
                }
            )

    elif fx_type == "riser":
        # Risers and buildups
        positions = [6, 14, 22, 30]  # Before section changes

        for bar in positions:
            bar_start = bar * 4.0
            duration = 2.0
            notes.append(
                {
                    "pitch": 60,
                    "start_time": bar_start + 2.0,
                    "duration": duration,
                    "velocity": 75 + bar % 10,
                    "mute": False,
                }
            )

    elif fx_type == "sub_drop":
        # Sub drops
        positions = [7, 15, 23, 31]

        for bar in positions:
            bar_start = bar * 4.0
            notes.append(
                {
                    "pitch": 24,
                    "start_time": bar_start + 3.75,
                    "duration": 0.25,
                    "velocity": 85 + bar % 8,
                    "mute": False,
                }
            )

    elif fx_type == "mixed":
        # Mix of different FX
        # Sweeps
        for bar in [4, 12, 20, 28]:
            bar_start = bar * 4.0
            notes.append(
                {
                    "pitch": 60,
                    "start_time": bar_start + 3.0,
                    "duration": 1.0,
                    "velocity": 70,
                    "mute": False,
                }
            )

        # Impacts
        for bar in [0, 16]:
            bar_start = bar * 4.0
            notes.append(
                {
                    "pitch": 60,
                    "start_time": bar_start,
                    "duration": 0.2,
                    "velocity": 100,
                    "mute": False,
                }
            )

        # Risers
        for bar in [6, 14, 22, 30]:
            bar_start = bar * 4.0
            notes.append(
                {
                    "pitch": 60,
                    "start_time": bar_start + 2.0,
                    "duration": 2.0,
                    "velocity": 80,
                    "mute": False,
                }
            )

        # Sub drops
        for bar in [7, 15, 23, 31]:
            bar_start = bar * 4.0
            notes.append(
                {
                    "pitch": 24,
                    "start_time": bar_start + 3.75,
                    "duration": 0.25,
                    "velocity": 90,
                    "mute": False,
                }
            )

    return sorted(notes, key=lambda x: x["start_time"])


fx_clips = [
    {
        "notes": create_32bar_fx_pattern("sweep", "regular"),
        "name": "FX Sweep Regular 32bar",
    },
    {
        "notes": create_32bar_fx_pattern("impact", "frequent"),
        "name": "FX Impact Frequent 32bar",
    },
    {
        "notes": create_32bar_fx_pattern("riser", "regular"),
        "name": "FX Riser 32bar",
    },
    {
        "notes": create_32bar_fx_pattern("mixed", "regular"),
        "name": "FX Mixed 32bar",
    },
    {
        "notes": create_32bar_fx_pattern("sub_drop", "regular"),
        "name": "FX Sub Drop 32bar",
    },
]

for clip_idx, clip_data in enumerate(fx_clips):
    send_command(
        "create_clip",
        {"track_index": fx_track_index, "clip_index": clip_idx, "length": 32.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": fx_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": fx_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(
        f"   [OK] Created Clip {clip_idx}: {clip_data['name']} ({len(clip_data['notes'])} notes)"
    )

# ============================================================================
# DUB DELAYS CLIPS - Extended 32-bar patterns
# ============================================================================
print("\nCreating Dub Delays clips (32 bars)...")


def create_32bar_delay_pattern(intensity="moderate", pattern="quarter"):
    """Generate a 32-bar delay pattern"""
    notes = []

    if pattern == "quarter":
        # Quarter note delays
        positions = [0.5, 1.5, 2.5, 3.5]
    elif pattern == "eighth":
        # Eighth note delays
        positions = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    elif pattern == "mixed":
        # Mixed pattern
        positions = [0.5, 1.5, 2.5, 3.5, 1.0, 3.0]
    else:
        positions = [0.5, 1.5, 2.5, 3.5]

    for bar in range(32):
        bar_start = bar * 4.0

        # Skip some bars based on intensity
        if intensity == "sparse":
            if bar % 4 not in [0, 1]:
                continue
        elif intensity == "moderate":
            if bar % 4 == 3:
                continue
        elif intensity == "intense":
            pass  # All bars

        # Add delay notes
        base_velocity = 75 + (bar % 8) * 3

        for pos in positions:
            if intensity == "intense" or (
                intensity == "moderate" and pos not in [1.0, 3.0]
            ):
                notes.append(
                    {
                        "pitch": 36,
                        "start_time": bar_start + pos,
                        "duration": 0.1,
                        "velocity": base_velocity,
                        "mute": False,
                    }
                )

        # Add buildup in final 4 bars
        if bar >= 28 and intensity != "sparse":
            for pos in [0.25, 0.75, 1.25, 1.75]:
                notes.append(
                    {
                        "pitch": 36,
                        "start_time": bar_start + pos,
                        "duration": 0.05,
                        "velocity": base_velocity + 5,
                        "mute": False,
                    }
                )

    return sorted(notes, key=lambda x: x["start_time"])


delay_clips = [
    {
        "notes": create_32bar_delay_pattern("moderate", "quarter"),
        "name": "Delay Moderate 32bar",
    },
    {
        "notes": create_32bar_delay_pattern("intense", "eighth"),
        "name": "Delay Intense 32bar",
    },
    {
        "notes": create_32bar_delay_pattern("sparse", "quarter"),
        "name": "Delay Sparse 32bar",
    },
    {
        "notes": create_32bar_delay_pattern("intense", "mixed"),
        "name": "Delay Mixed Intense 32bar",
    },
]

for clip_idx, clip_data in enumerate(delay_clips):
    send_command(
        "create_clip",
        {"track_index": delay_track_index, "clip_index": clip_idx, "length": 32.0},
    )
    send_command(
        "add_notes_to_clip",
        {
            "track_index": delay_track_index,
            "clip_index": clip_idx,
            "notes": clip_data["notes"],
        },
    )
    send_command(
        "set_clip_name",
        {
            "track_index": delay_track_index,
            "clip_index": clip_idx,
            "name": clip_data["name"],
        },
    )
    print(
        f"   [OK] Created Clip {clip_idx}: {clip_data['name']} ({len(clip_data['notes'])} notes)"
    )

print("\n" + "=" * 80)
print("ALL CLIPS CREATED")
print("=" * 80)
print(f"\nSummary:")
print(f"  Track {kick_track_index} (Kick 32bar):        {len(kick_clips)} clips")
print(f"  Track {bass_track_index} (Sub-bass 32bar):    {len(bass_clips)} clips")
print(f"  Track {hihat_track_index} (Hi-hats 32bar):     {len(hihat_clips)} clips")
print(f"  Track {pad_track_index} (Synth Pads 32bar):  {len(pad_clips)} clips")
print(f"  Track {fx_track_index} (FX 32bar):          {len(fx_clips)} clips")
print(f"  Track {delay_track_index} (Dub Delays 32bar):  {len(delay_clips)} clips")
print(
    f"  Total clips:           {len(kick_clips) + len(bass_clips) + len(hihat_clips) + len(pad_clips) + len(fx_clips) + len(delay_clips)} clips"
)
print(f"  All clips: 32 bars each")
print(f"  Increased complexity with more notes per pattern")

print("\n" + "=" * 80)
print("CREATION COMPLETE!")
print("=" * 80)
print("\nNext steps:")
print("  1. Load instruments and sounds on each track")
print("  2. Add effects (reverb, delay, filters)")
print("  3. Use these clips for longer musical sections")
print("  4. Each clip provides ~1 minute at 126 BPM")
print("\n")

s.close()
