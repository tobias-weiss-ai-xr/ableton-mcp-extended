import socket
import json
import random

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return the response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


print("=" * 80)
print("CREATING 32-BAR UNIQUE NON-REPEATING DUB TECHNO PATTERNS")
print("=" * 80)
print(f"Tempo: 126 BPM")
print(f"Pattern length: 32 bars")
print(f"Each pattern evolves continuously with NO internal repetition")
print("=" * 80)

# Set tempo first
print("\nSetting tempo to 126 BPM...")
send_command("set_tempo", {"tempo": 126.0})
print("   [OK] Tempo set to 126 BPM")

random.seed(42)

# ============================================================================
# TRACK CREATION
# ============================================================================

# Track 0: Kick (create new track at the end)
print("\n[1/6] Creating Kick track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
kick_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": kick_track_index, "name": "Kick Unique 32bar"}
)
print(f"   [OK] Created Kick track (Track {kick_track_index})")

# Track 1: Sub-bass
print("[2/6] Creating Sub-bass track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
bass_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": bass_track_index, "name": "Sub-bass Unique 32bar"}
)
print(f"   [OK] Created Sub-bass track (Track {bass_track_index})")

# Track 2: Hi-hats
print("[3/6] Creating Hi-hat track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
hihat_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": hihat_track_index, "name": "Hi-hats Unique 32bar"}
)
print(f"   [OK] Created Hi-hat track (Track {hihat_track_index})")

# Track 3: Synth Pads
print("[4/6] Creating Synth Pads track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
pad_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name",
    {"track_index": pad_track_index, "name": "Synth Pads Unique 32bar"},
)
print(f"   [OK] Created Synth Pads track (Track {pad_track_index})")

# Track 4: FX
print("[5/6] Creating FX track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
fx_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name", {"track_index": fx_track_index, "name": "FX Unique 32bar"}
)
print(f"   [OK] Created FX track (Track {fx_track_index})")

# Track 5: Dub Delays (send track)
print("[6/6] Creating Dub Delays track...")
send_command("create_midi_track", {"index": -1})
session_info = send_command("get_session_info")
delay_track_index = session_info["result"]["track_count"] - 1
send_command(
    "set_track_name",
    {"track_index": delay_track_index, "name": "Dub Delays Unique 32bar"},
)
print(f"   [OK] Created Dub Delays track (Track {delay_track_index})")

print("\n" + "=" * 80)
print("ALL TRACKS CREATED")
print("=" * 80)

# ============================================================================
# KICK CLIPS - Non-repeating 32-bar patterns
# ============================================================================
print("\nCreating Kick clips (32 bars, non-repeating)...")


def create_unique_32bar_kick_pattern(seed):
    """Generate a 32-bar kick pattern with NO repetition"""
    random.seed(seed)
    notes = []

    for bar in range(32):
        bar_start = bar * 4.0

        # Unique kick pattern for each bar
        # Beat 1 always present (foundation)
        notes.append(
            {
                "pitch": 36,
                "start_time": bar_start,
                "duration": 0.25 + random.uniform(-0.02, 0.05),
                "velocity": 100 + random.randint(-5, 15),
                "mute": False,
            }
        )

        # Beat 2: 70% chance, unique placement
        if random.random() < 0.7:
            offset = random.choice([1.0, 0.97, 1.03])
            notes.append(
                {
                    "pitch": 36,
                    "start_time": bar_start + offset,
                    "duration": 0.2 + random.uniform(-0.01, 0.03),
                    "velocity": 95 + random.randint(-10, 10),
                    "mute": False,
                }
            )

        # Beat 3: 80% chance, unique placement
        if random.random() < 0.8:
            offset = random.choice([2.0, 1.97, 2.03])
            notes.append(
                {
                    "pitch": 36,
                    "start_time": bar_start + offset,
                    "duration": 0.22 + random.uniform(-0.02, 0.04),
                    "velocity": 98 + random.randint(-8, 12),
                    "mute": False,
                }
            )

        # Beat 4: varies by bar, never repeats pattern
        beat4_chance = 0.5 + (bar / 64.0)
        if random.random() < beat4_chance:
            offset = random.choice([3.0, 2.97, 3.03, 3.75])
            notes.append(
                {
                    "pitch": 36,
                    "start_time": bar_start + offset,
                    "duration": 0.18 + random.uniform(-0.01, 0.02),
                    "velocity": 90 + random.randint(-10, 15),
                    "mute": False,
                }
            )

        # Extra kicks: unique to each bar
        extra_count = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        for _ in range(extra_count):
            pos = random.choice([0.5, 1.5, 2.5, 3.5, 0.25, 0.75, 1.25, 1.75])
            notes.append(
                {
                    "pitch": 36,
                    "start_time": bar_start + pos,
                    "duration": 0.1 + random.uniform(0, 0.05),
                    "velocity": 70 + random.randint(-10, 10),
                    "mute": False,
                }
            )

    return sorted(notes, key=lambda x: x["start_time"])


kick_clips = []
for i in range(8):
    notes = create_unique_32bar_kick_pattern(100 + i)
    kick_clips.append({"notes": notes, "name": f"Kick Unique {i + 1}"})

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
# SUB-BASS CLIPS - Non-repeating 32-bar patterns
# ============================================================================
print("\nCreating Sub-bass clips (32 bars, non-repeating)...")


def create_unique_32bar_bass_pattern(seed, root_note):
    """Generate a 32-bar bass pattern with NO repetition"""
    random.seed(seed)
    notes = []

    current_note = root_note
    notes_per_bar = [
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        3,
        3,
        3,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        3,
        3,
        3,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
    ]

    for bar in range(32):
        bar_start = bar * 4.0
        num_notes = notes_per_bar[bar]

        note_duration = 4.0 / num_notes
        for i in range(num_notes):
            # Evolving note selection
            if bar < 8:
                # Simple evolution
                if i == 0:
                    pitch = root_note
                else:
                    pitch = random.choice([root_note, root_note - 12, root_note + 7])
            elif bar < 16:
                # More variety
                pitch_options = [
                    root_note,
                    root_note - 12,
                    root_note + 7,
                    root_note + 3,
                    root_note + 5,
                ]
                pitch = random.choice(pitch_options)
            elif bar < 24:
                # Complex evolution
                pitch_options = [
                    root_note,
                    root_note - 12,
                    root_note - 24,
                    root_note + 7,
                    root_note + 12,
                    root_note + 3,
                ]
                pitch = random.choice(pitch_options)
            else:
                # Fully evolving
                pitch_options = [root_note + x for x in [-24, -12, 0, 3, 5, 7, 10, 12]]
                pitch = random.choice(pitch_options)

            notes.append(
                {
                    "pitch": pitch,
                    "start_time": bar_start + i * note_duration,
                    "duration": note_duration - 0.01,
                    "velocity": 90 + random.randint(-10, 15),
                    "mute": False,
                }
            )

        # Occasional micro-variations
        if random.random() < 0.3:
            offset = random.uniform(0.01, 0.03)
            notes[-1]["start_time"] += offset
            notes[-1]["duration"] -= offset

    return sorted(notes, key=lambda x: x["start_time"])


bass_clips = []
roots = [36, 41, 43, 39]
for i in range(8):
    root = roots[i % len(roots)]
    notes = create_unique_32bar_bass_pattern(200 + i, root)
    bass_clips.append({"notes": notes, "name": f"Bass Unique {i + 1}"})

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
# HI-HAT CLIPS - Non-repeating 32-bar patterns
# ============================================================================
print("\nCreating Hi-hat clips (32 bars, non-repeating)...")


def create_unique_32bar_hihat_pattern(seed):
    """Generate a 32-bar hi-hat pattern with NO repetition"""
    random.seed(seed)
    notes = []

    for bar in range(32):
        bar_start = bar * 4.0

        # Density evolves through the 32 bars
        density = 0.3 + (bar / 32.0) * 0.7

        # Create unique pattern for this bar
        for beat in range(4):
            for sub in [0.25, 0.5, 0.75, 1.0]:
                pos = beat + sub
                if pos >= 4:
                    continue

                # Unique probability for each position
                prob = density * random.uniform(0.7, 1.3)
                if random.random() < prob:
                    # Varied pitch and velocity
                    pitch = random.choice([76, 77])
                    velocity = 55 + random.randint(-10, 20)
                    duration = 0.05 + random.uniform(0, 0.05)

                    notes.append(
                        {
                            "pitch": pitch,
                            "start_time": bar_start + pos,
                            "duration": duration,
                            "velocity": min(127, max(1, velocity)),
                            "mute": False,
                        }
                    )

        # Add occasional triplets (unique to each bar)
        if random.random() < 0.2:
            triplet_start = bar_start + random.choice([1.5, 2.5, 3.5])
            for i in range(3):
                notes.append(
                    {
                        "pitch": 76,
                        "start_time": triplet_start + i * 0.333,
                        "duration": 0.08,
                        "velocity": 60 + random.randint(-5, 10),
                        "mute": False,
                    }
                )

    return sorted(notes, key=lambda x: x["start_time"])


hihat_clips = []
for i in range(8):
    notes = create_unique_32bar_hihat_pattern(300 + i)
    hihat_clips.append({"notes": notes, "name": f"Hi-hat Unique {i + 1}"})

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
# SYNTH PAD CLIPS - Non-repeating 32-bar patterns
# ============================================================================
print("\nCreating Synth Pad clips (32 bars, non-repeating)...")


def create_unique_32bar_pad_pattern(seed, chord_progression):
    """Generate a 32-bar pad pattern with NO repetition"""
    random.seed(seed)
    notes = []

    for bar in range(32):
        bar_start = bar * 4.0

        # Select chord from progression (evolving selection)
        chord_idx = bar % len(chord_progression)
        chord = chord_progression[chord_idx]

        # Add chord notes with unique durations per bar
        num_notes = len(chord)
        base_duration = 4.0 / num_notes

        for i, pitch in enumerate(chord):
            # Unique duration for this bar
            duration = base_duration * random.uniform(0.8, 1.2)
            start = bar_start + i * base_duration

            notes.append(
                {
                    "pitch": pitch,
                    "start_time": start,
                    "duration": duration,
                    "velocity": 40 + random.randint(0, 20),
                    "mute": False,
                }
            )

        # Add evolving 7th extensions
        if bar >= 8 and random.random() < 0.4:
            extension = chord[2] + random.choice([2, 4])
            notes.append(
                {
                    "pitch": extension,
                    "start_time": bar_start + random.uniform(1.0, 3.0),
                    "duration": random.uniform(1.0, 2.0),
                    "velocity": 30 + random.randint(0, 10),
                    "mute": False,
                }
            )

        # Add high drone in later bars
        if bar >= 16 and random.random() < 0.3:
            notes.append(
                {
                    "pitch": chord[0] + 24,
                    "start_time": bar_start,
                    "duration": 4.0,
                    "velocity": 25 + random.randint(0, 10),
                    "mute": False,
                }
            )

    return sorted(notes, key=lambda x: x["start_time"])


pad_progressions = [
    [(48, 51, 55), (53, 56, 60), (55, 58, 62), (51, 55, 58)],
    [(53, 56, 60), (55, 58, 62), (48, 51, 55), (53, 56, 60)],
    [(55, 58, 62), (51, 55, 58), (53, 56, 60), (55, 58, 62)],
    [(48, 50, 55), (53, 55, 60), (55, 57, 62), (51, 53, 58)],
]

pad_clips = []
for i in range(8):
    prog = pad_progressions[i % len(pad_progressions)]
    notes = create_unique_32bar_pad_pattern(400 + i, prog)
    pad_clips.append({"notes": notes, "name": f"Pad Unique {i + 1}"})

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
# FX CLIPS - Non-repeating 32-bar patterns
# ============================================================================
print("\nCreating FX clips (32 bars, non-repeating)...")


def create_unique_32bar_fx_pattern(seed, fx_type):
    """Generate a 32-bar FX pattern with NO repetition"""
    random.seed(seed)
    notes = []

    fx_types = {
        "sweep": {"pitch": 60, "base_duration": 1.0},
        "impact": {"pitch": 60, "base_duration": 0.2},
        "riser": {"pitch": 60, "base_duration": 2.0},
        "sub": {"pitch": 24, "base_duration": 0.3},
    }

    fx_config = fx_types[fx_type]

    # Create unique FX placement throughout 32 bars
    for bar in range(32):
        bar_start = bar * 4.0

        # Frequency increases in later bars
        freq = 0.2 + (bar / 32.0) * 0.6

        if random.random() < freq:
            # Unique position within bar
            pos = random.uniform(0, 3.5)

            # Evolving duration and velocity
            duration = fx_config["base_duration"] * random.uniform(0.5, 1.5)
            velocity = 70 + random.randint(-20, 30)

            notes.append(
                {
                    "pitch": fx_config["pitch"],
                    "start_time": bar_start + pos,
                    "duration": duration,
                    "velocity": min(127, max(1, velocity)),
                    "mute": False,
                }
            )

        # Add clustered FX in bars 24-31
        if bar >= 24 and random.random() < 0.4:
            for _ in range(random.randint(1, 3)):
                pos = random.uniform(0, 3.5)
                notes.append(
                    {
                        "pitch": fx_config["pitch"],
                        "start_time": bar_start + pos,
                        "duration": fx_config["base_duration"] * 0.5,
                        "velocity": 60 + random.randint(-10, 20),
                        "mute": False,
                    }
                )

    return sorted(notes, key=lambda x: x["start_time"])


fx_clips = []
fx_types = ["sweep", "impact", "riser", "sub"]
for i in range(8):
    fx_type = fx_types[i % len(fx_types)]
    notes = create_unique_32bar_fx_pattern(500 + i, fx_type)
    fx_clips.append({"notes": notes, "name": f"FX Unique {i + 1}"})

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
# DUB DELAYS CLIPS - Non-repeating 32-bar patterns
# ============================================================================
print("\nCreating Dub Delays clips (32 bars, non-repeating)...")


def create_unique_32bar_delay_pattern(seed):
    """Generate a 32-bar delay pattern with NO repetition"""
    random.seed(seed)
    notes = []

    for bar in range(32):
        bar_start = bar * 4.0

        # Density evolves
        density = 0.3 + (bar / 32.0) * 0.5

        # Unique delay pattern for each bar
        for beat in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
            if random.random() < density:
                # Unique timing offset
                offset = random.uniform(-0.02, 0.02)

                notes.append(
                    {
                        "pitch": 36,
                        "start_time": bar_start + beat + offset,
                        "duration": 0.1 + random.uniform(0, 0.05),
                        "velocity": 70 + random.randint(-10, 15),
                        "mute": False,
                    }
                )

        # Add occasional rapid delays (stutter)
        if random.random() < 0.15:
            stutter_start = bar_start + random.choice([2.0, 2.5, 3.0])
            for i in range(random.randint(2, 5)):
                notes.append(
                    {
                        "pitch": 36,
                        "start_time": stutter_start + i * 0.125,
                        "duration": 0.05,
                        "velocity": 65 + random.randint(-5, 10),
                        "mute": False,
                    }
                )

        # Long delay tail in bars 28-31
        if bar >= 28 and random.random() < 0.5:
            notes.append(
                {
                    "pitch": 36,
                    "start_time": bar_start + 3.5,
                    "duration": 0.15,
                    "velocity": 80 + random.randint(-5, 10),
                    "mute": False,
                }
            )

    return sorted(notes, key=lambda x: x["start_time"])


delay_clips = []
for i in range(8):
    notes = create_unique_32bar_delay_pattern(600 + i)
    delay_clips.append({"notes": notes, "name": f"Delay Unique {i + 1}"})

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
print(f"  Track {kick_track_index} (Kick Unique 32bar):        {len(kick_clips)} clips")
print(f"  Track {bass_track_index} (Sub-bass Unique 32bar):    {len(bass_clips)} clips")
print(
    f"  Track {hihat_track_index} (Hi-hats Unique 32bar):     {len(hihat_clips)} clips"
)
print(f"  Track {pad_track_index} (Synth Pads Unique 32bar):  {len(pad_clips)} clips")
print(f"  Track {fx_track_index} (FX Unique 32bar):          {len(fx_clips)} clips")
print(
    f"  Track {delay_track_index} (Dub Delays Unique 32bar):  {len(delay_clips)} clips"
)
print(
    f"  Total clips:           {len(kick_clips) + len(bass_clips) + len(hihat_clips) + len(pad_clips) + len(fx_clips) + len(delay_clips)} clips"
)
print(f"  All clips: 32 bars each")
print(f"  Each pattern has NO internal repetition - unique evolution throughout")

print("\n" + "=" * 80)
print("CREATION COMPLETE!")
print("=" * 80)
print("\nNext steps:")
print("  1. Load instruments and sounds on each track")
print("  2. Add effects (reverb, delay, filters)")
print("  3. Use these unique 32-bar clips for extended musical sections")
print("  4. Each clip provides ~1 minute at 126 BPM with continuous evolution")
print("\n")

s.close()
