"""
Dub Reggae Beat Generator

Creates a classic dub reggae beat with:
- One-drop drum rhythm (kick on 1&3, snare accent on 3)
- Heavy bassline with root/fifth emphasis
- Skank guitar/keys on offbeats (2&4)
- 4 sections: Intro, Verse, Chorus, Drop (8 bars each)
- 75 BPM tempo (classic reggae feel)

Usage:
    python dub_reggae_beat.py
"""

import socket
import json
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

TEMPO = 75.0
SECTIONS = ["Intro", "Verse", "Chorus", "Drop"]
BARS_PER_SECTION = 8
TOTAL_BARS = len(SECTIONS) * BARS_PER_SECTION  # 32 bars total

# MIDI pitches
KICK = 36
SNARE = 38
RIMSHOT = 37
HIHAT_CLOSED = 42
HIHAT_OPEN = 46
BASS_ROOT = 36  # C2
BASS_FIFTH = 43  # G2
SKANK_CHORD_ROOT = 48  # C3
PERC_SHAKER = 70

# Track indices (will be created in order)
TRACKS = {
    "Drums": 0,
    "Bass": 1,
    "Skank": 2,
    "HiHats": 3,
    "Percussion": 4,
}

# ============================================================================
# SOCKET COMMUNICATION
# ============================================================================


def send_command(sock, cmd_type, params=None):
    """Send command and return response"""
    command = {"type": cmd_type, "params": params or {}}
    sock.send(json.dumps(command).encode("utf-8"))
    response = json.loads(sock.recv(8192).decode("utf-8"))
    return response


# ============================================================================
# PATTERN GENERATORS
# ============================================================================


def get_drum_pattern(start_bar, bars=8):
    """Generate one-drop drum pattern"""
    notes = []

    for bar in range(bars):
        beat = start_bar + (bar * 4)

        # One-drop pattern: kick on 1 and 3, snare accent on 3
        # Variation: add ghost kicks on offbeats for dub feel

        # Kick on beat 1 (strong)
        notes.append(
            {"pitch": KICK, "start_time": beat, "duration": 0.5, "velocity": 120}
        )

        # Kick on beat 3 (medium)
        notes.append(
            {"pitch": KICK, "start_time": beat + 2.0, "duration": 0.5, "velocity": 100}
        )

        # Snare/rim on beat 3 (strong accent - one-drop characteristic)
        notes.append(
            {
                "pitch": RIMSHOT,
                "start_time": beat + 2.0,
                "duration": 0.25,
                "velocity": 110,
            }
        )

        # Variation: add rimshot on beat 2 in bars 4 and 8
        if bar in [3, 7]:
            notes.append(
                {
                    "pitch": RIMSHOT,
                    "start_time": beat + 1.0,
                    "duration": 0.25,
                    "velocity": 80,
                }
            )

    return notes


def get_bass_pattern(start_bar, bars=8):
    """Generate dub reggae bassline - heavy root with syncopation"""
    notes = []

    for bar in range(bars):
        beat = start_bar + (bar * 4)

        # Section variations
        if bar < 2:
            # Intro: Simple root on beat 1
            notes.append(
                {
                    "pitch": BASS_ROOT,
                    "start_time": beat,
                    "duration": 2.0,
                    "velocity": 110,
                }
            )
        elif bar < 4:
            # Build: Root on 1, fifth on 3
            notes.append(
                {
                    "pitch": BASS_ROOT,
                    "start_time": beat,
                    "duration": 1.5,
                    "velocity": 105,
                }
            )
            notes.append(
                {
                    "pitch": BASS_FIFTH,
                    "start_time": beat + 2.0,
                    "duration": 1.5,
                    "velocity": 100,
                }
            )
        elif bar < 6:
            # Syncopated: Root with offbeat
            notes.append(
                {
                    "pitch": BASS_ROOT,
                    "start_time": beat,
                    "duration": 1.0,
                    "velocity": 110,
                }
            )
            notes.append(
                {
                    "pitch": BASS_ROOT,
                    "start_time": beat + 1.5,
                    "duration": 0.5,
                    "velocity": 90,
                }
            )
            notes.append(
                {
                    "pitch": BASS_FIFTH,
                    "start_time": beat + 2.5,
                    "duration": 1.0,
                    "velocity": 100,
                }
            )
        else:
            # Drop: Heavy root with slides
            notes.append(
                {
                    "pitch": BASS_ROOT,
                    "start_time": beat,
                    "duration": 3.0,
                    "velocity": 115,
                }
            )
            notes.append(
                {
                    "pitch": BASS_FIFTH,
                    "start_time": beat + 3.5,
                    "duration": 0.5,
                    "velocity": 95,
                }
            )

    return notes


def get_skank_pattern(start_bar, bars=8):
    """Generate skank rhythm - chords on offbeats 2 and 4"""
    notes = []

    # Chord tones: root, third, fifth
    chord_tones = [SKANK_CHORD_ROOT, SKANK_CHORD_ROOT + 4, SKANK_CHORD_ROOT + 7]

    for bar in range(bars):
        beat = start_bar + (bar * 4)

        # Skank on beats 2 and 4 (offbeat feel)
        for tone in chord_tones:
            # Beat 2 skank
            notes.append(
                {
                    "pitch": tone,
                    "start_time": beat + 1.0,
                    "duration": 0.5,
                    "velocity": 85,
                }
            )
            # Beat 4 skank
            notes.append(
                {
                    "pitch": tone,
                    "start_time": beat + 3.0,
                    "duration": 0.5,
                    "velocity": 80,
                }
            )

    return notes


def get_hihat_pattern(start_bar, bars=8):
    """Generate hi-hat pattern - 8th notes with offbeat accents"""
    notes = []

    for bar in range(bars):
        beat = start_bar + (bar * 4)

        # 8th note pattern
        for i in range(8):
            note_beat = beat + (i * 0.5)

            # Offbeats (1.5, 2.5, 3.5, 4.5) get accent
            is_offbeat = i % 2 == 1
            velocity = 75 if is_offbeat else 60

            # Open hat on beat 4 in bars 4 and 8
            pitch = HIHAT_OPEN if (i == 6 and bar in [3, 7]) else HIHAT_CLOSED

            notes.append(
                {
                    "pitch": pitch,
                    "start_time": note_beat,
                    "duration": 0.25 if pitch == HIHAT_CLOSED else 0.5,
                    "velocity": velocity,
                }
            )

    return notes


def get_percussion_pattern(start_bar, bars=8):
    """Generate percussion - shaker pattern"""
    notes = []

    for bar in range(bars):
        beat = start_bar + (bar * 4)

        # Shaker on 16th notes with accents
        for i in range(16):
            note_beat = beat + (i * 0.25)

            # Accent on downbeats
            velocity = 70 if i % 4 == 0 else 50

            notes.append(
                {
                    "pitch": PERC_SHAKER,
                    "start_time": note_beat,
                    "duration": 0.125,
                    "velocity": velocity,
                }
            )

    return notes


# ============================================================================
# TRACK CREATION
# ============================================================================


def create_tracks(sock):
    """Create all tracks for dub reggae beat"""
    print("\n[1/4] Creating tracks...")

    track_names = list(TRACKS.keys())
    for i, name in enumerate(track_names):
        response = send_command(sock, "create_midi_track", {"index": -1})
        if response.get("status") != "success":
            print(f"   [ERROR] Failed to create {name}")
            return False

        send_command(sock, "set_track_name", {"track_index": i, "name": f"Dub_{name}"})
        print(f"   [OK] Created {name}")

    return True


# ============================================================================
# CLIP CREATION
# ============================================================================


def create_section_clips(sock, section_idx, section_name):
    """Create clips for a section"""
    start_bar = section_idx * BARS_PER_SECTION

    print(
        f"\n[2/4] Creating {section_name} section (bars {start_bar}-{start_bar + BARS_PER_SECTION - 1})..."
    )

    # Track 0: Drums
    drum_notes = get_drum_pattern(start_bar, BARS_PER_SECTION)
    create_clip_with_notes(
        sock, 0, section_idx, drum_notes, section_name, BARS_PER_SECTION
    )

    # Track 1: Bass
    bass_notes = get_bass_pattern(start_bar, BARS_PER_SECTION)
    create_clip_with_notes(
        sock, 1, section_idx, bass_notes, section_name, BARS_PER_SECTION
    )

    # Track 2: Skank
    skank_notes = get_skank_pattern(start_bar, BARS_PER_SECTION)
    create_clip_with_notes(
        sock, 2, section_idx, skank_notes, section_name, BARS_PER_SECTION
    )

    # Track 3: HiHats
    hihat_notes = get_hihat_pattern(start_bar, BARS_PER_SECTION)
    create_clip_with_notes(
        sock, 3, section_idx, hihat_notes, section_name, BARS_PER_SECTION
    )

    # Track 4: Percussion
    perc_notes = get_percussion_pattern(start_bar, BARS_PER_SECTION)
    create_clip_with_notes(
        sock, 4, section_idx, perc_notes, section_name, BARS_PER_SECTION
    )

    print(f"   [OK] {section_name} complete")


def create_clip_with_notes(sock, track_idx, clip_idx, notes, section_name, length):
    """Create a clip and add notes"""
    # Create clip
    send_command(
        sock,
        "create_clip",
        {"track_index": track_idx, "clip_index": clip_idx, "length": length},
    )

    # Add notes
    if notes:
        send_command(
            sock,
            "add_notes_to_clip",
            {"track_index": track_idx, "clip_index": clip_idx, "notes": notes},
        )

    # Name clip
    send_command(
        sock,
        "set_clip_name",
        {
            "track_index": track_idx,
            "clip_index": clip_idx,
            "name": f"{section_name}_{list(TRACKS.keys())[track_idx]}",
        },
    )


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Create dub reggae beat"""
    print("\n" + "=" * 60)
    print("DUB REGGAE BEAT GENERATOR")
    print("=" * 60)
    print(f"Tempo: {TEMPO} BPM")
    print(f"Sections: {SECTIONS}")
    print(f"Total bars: {TOTAL_BARS}")
    print("=" * 60)

    # Connect to Ableton
    print("\n[1/4] Connecting to Ableton...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(("localhost", 9877))
        print("   [OK] Connected to Ableton")
    except Exception as e:
        print(f"   [ERROR] Connection failed: {e}")
        print("   [TIP] Make sure Ableton is running with Remote Script loaded")
        return

    # Check session
    session_info = send_command(sock, "get_session_info")
    if session_info.get("status") != "success":
        print("   [ERROR] Failed to get session info")
        sock.close()
        return

    print(f"   [OK] Session has {session_info['result']['track_count']} tracks")

    # Set tempo
    print(f"\n[2/4] Setting tempo to {TEMPO} BPM...")
    send_command(sock, "set_tempo", {"tempo": TEMPO})
    print(f"   [OK] Tempo set")

    # Create tracks
    if not create_tracks(sock):
        sock.close()
        return

    time.sleep(0.5)

    # Create clips for each section
    print("\n[3/4] Creating clips...")
    for i, section in enumerate(SECTIONS):
        create_section_clips(sock, i, section)
        time.sleep(0.2)

    # Summary
    print("\n" + "=" * 60)
    print("DUB REGGAE BEAT CREATED")
    print("=" * 60)
    print(f"\nTracks created:")
    for name, idx in TRACKS.items():
        print(f"   - Dub_{name} (Track {idx})")

    print(f"\nSections:")
    for section in SECTIONS:
        print(f"   - {section}: {BARS_PER_SECTION} bars")

    print(f"\nCharacteristics:")
    print("   - One-drop drum rhythm (kick on 1&3, snare on 3)")
    print("   - Heavy bassline with root/fifth")
    print("   - Skank chords on offbeats (2&4)")
    print("   - 8th note hi-hats with offbeat accents")
    print("   - Shaker percussion")

    print(f"\nTotal: {TOTAL_BARS} bars ({TOTAL_BARS * 4} beats)")
    print(f"At {TEMPO} BPM: ~{(TOTAL_BARS * 4) / TEMPO * 60:.0f} seconds")

    print("\n[4/4] Done! Fire clips in Ableton to play.")
    print("=" * 60)

    sock.close()


if __name__ == "__main__":
    main()
