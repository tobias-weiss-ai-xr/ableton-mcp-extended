import socket
import json
import time

# ============================================================================
# FULLY AUTOMATED 2-HOUR DUB TECHNOPO SETUP & RECORDING
# ============================================================================
# This script handles EVERYTHING:
# - Creates tracks
# - Loads instruments with presets
# - Configures send routing (prints instructions for manual setup)
# - Sets mix levels
# - Runs 2-hour automated playback
# ============================================================================

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return full response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


def get_session_info():
    """Get current session info"""
    return send_command("get_session_info")


def fire_clip(track_index, clip_index):
    """Fire a specific clip"""
    send_command(
        {"type": "fire_clip", "params": {"track_index": track_index, "clip_index": clip_index}}
    )


def start_playback():
    """Start playback"""
    send_command({"type": "start_playback", "params": {}})


def stop_playback():
    """Stop playback"""
    send_command({"type": "stop_playback", "params": {}})


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# ============================================================================
# PRESET DEFINITIONS (names as they appear in Ableton)
# ============================================================================
PRESETS = {
    "Kick": {
        "device_uri": "Operator",
        "preset_name": "Kick - Punchy",
    },
    "Sub-bass": {
        "device_uri": "Tension",
        "preset_name": "Sub Bass - Deep",
    },
    "Hi-hats": {
        "device_uri": "Drums/Drum Rack",
        "preset_name": "Basic",
        "drum_kit_path": "drums/acoustic/kit1",
    },
    "Synth Pads": {
        "device_uri": "Wavetable",
        "preset_name": "Atmospheric",
    },
    "FX": {
        "device_uri": "Instruments/Simpler",
        "preset_name": "FX - One Shot",
    },
    "Dub Delays": {
        "device_uri": "N/A",  # Send track, no instrument
        "preset_name": "N/A",
    },
}


# ============================================================================
# SEND ROUTING CONFIGURATION
# ============================================================================
# Send track indices (after creating 6 main tracks)
SEND_TRACKS = {
    "Reverb": 6,  # Will be created
    "Delay": 7,  # Will be created
}

# Send levels (normalized 0.0-1.0)
SEND_LEVELS = {
    0: {"Reverb": 0.0, "Delay": 0.0},      # Kick
    1: {"Reverb": 0.1, "Delay": 0.1},      # Sub-bass
    2: {"Reverb": 0.3, "Delay": 0.3},      # Hi-hats
    3: {"Reverb": 0.5, "Delay": 0.5},      # Synth Pads
    4: {"Reverb": 0.7, "Delay": 0.7},      # FX
    5: {"Reverb": 1.0, "Delay": 1.0},      # Dub Delays
}


# ============================================================================
# MIX LEVELS (normalized 0.0-1.0)
# ============================================================================
MIX_LEVELS = {
    0: 0.75,   # Kick (-6 dB)
    1: 0.6,    # Sub-bass (-3 dB)
    2: 0.3,    # Hi-hats (-12 dB)
    3: 0.15,   # Synth Pads (-18 dB)
    4: 0.2,    # FX (-15 dB)
    5: 0.25,   # Dub Delays (-12 dB)
}


# ============================================================================
# SECTION DEFINITIONS
# ============================================================================
sections = [
    {
        "name": "Section 0 - Deep Intro",
        "description": "Minimal elements establish groove",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 0),  # Bass: Root Drone
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 1 - Subtle Build",
        "description": "Adding slight variations, more delays",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 0),  # Bass: Root Drone
            (2, 0),  # Hi-hat: Offbeats
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 2 - Atmosphere Enters",
        "description": "Synth pads create depth",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 1),  # Bass: Octave Drop
            (2, 0),  # Hi-hat: Offbeats
            (3, 0),  # Pad: Cm
            (4, 3),  # FX: Silent
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 3 - First Build",
        "description": "Energy starts to rise",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 2),  # Bass: Syncopated
            (2, 0),  # Hi-hat: Offbeats
            (3, 0),  # Pad: Cm
            (4, 1),  # FX: Impact
            (5, 0),  # Delay: Regular
        ],
    },
    # Sections 4-7: Hypnotic groove
    {
        "name": "Section 4 - Hypnotic State",
        "description": "Full groove engaged",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 2),  # Bass: Syncopated
            (2, 1),  # Hi-hat: Active
            (3, 0),  # Pad: Cm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 5 - Slight Shift",
        "description": "Subtle evolution continues",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 1),  # Pad: Fm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 6 - Building Up",
        "description": "More energy in hi-hats",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 2),  # Pad: Gm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 7 - First Peak",
        "description": "Elements come together",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 4),  # Bass: Staccato
            (2, 4),  # Hi-hat: 16ths
            (3, 2),  # Pad: Gm
            (4, 2),  # FX: Reverse
            (5, 2),  # Delay: Minimal
        ],
    },
    # Sections 8-11: First buildup and peak
    {
        "name": "Section 8 - Buildup Begins",
        "description": "Starting first major buildup",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 4),  # Bass: Staccato
            (2, 5),  # Hi-hat: Open
            (3, 2),  # Pad: Gm
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 9 - Rising Higher",
        "description": "Intensity increases",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 5),  # Bass: F Drone
            (2, 4),  # Hi-hat: 16ths
            (3, 3),  # Pad: Eb
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 10 - Approaching Peak",
        "description": "Almost at first peak",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 5),  # Bass: F Drone
            (2, 4),  # Hi-hat: 16ths
            (3, 3),  # Pad: Eb
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 11 - Peak 1",
        "description": "First major peak reached",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 6),  # Bass: G Drone
            (2, 7),  # Hi-hat: 2 and 4
            (3, 0),  # Pad: Cm
            (4, 7),  # FX: Riser
            (5, 6),  # Delay: Tail
        ],
    },
    # Sections 12-15: Breakdown
    {
        "name": "Section 12 - Start Breakdown",
        "description": "Removing elements for space",
        "clips": [
            (0, 3),  # Kick: Half
            (1, 4),  # Bass: Staccato
            (2, 3),  # Hi-hat: Silent
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 13 - Minimal State",
        "description": "Very stripped back",
        "clips": [
            (0, 5),  # Kick: Sparse
            (1, 0),  # Bass: Root Drone
            (2, 3),  # Hi-hat: Silent
            (3, 4),  # Pad: Minimal
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 14 - Atmospheric",
        "description": "Focus on pads and atmosphere",
        "clips": [
            (0, 5),  # Kick: Sparse
            (1, 0),  # Bass: Root Drone
            (2, 3),  # Hi-hat: Silent
            (3, 5),  # Pad: Silent
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 15 - Deep Space",
        "description": "Maximum atmosphere, minimal elements",
        "clips": [
            (0, 7),  # Kick: Soft
            (1, 0),  # Bass: Root Drone
            (2, 3),  # Hi-hat: Silent
            (3, 7),  # Pad: High Drone
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
    # Sections 16-19: Second buildup
    {
        "name": "Section 16 - Elements Return",
        "description": "Elements slowly return",
        "clips": [
            (0, 3),  # Kick: Half
            (1, 2),  # Bass: Syncopated
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 5),  # FX: Noise Build
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 17 - Building Again",
        "description": "Second buildup begins",
        "clips": [
            (0, 4),  # Kick: Syncopated
            (1, 3),  # Bass: Rising
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 5),  # FX: Noise Build
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 18 - Gathering Momentum",
        "description": "Energy building up again",
        "clips": [
            (0, 4),  # Kick: Syncopated
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 4),  # Pad: Minimal
            (4, 5),  # FX: Noise Build
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 19 - Peak 2 Approaching",
        "description": "Reaching second peak",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 4),  # Pad: Minimal
            (4, 7),  # FX: Riser
            (5, 4),  # Delay: Echo Build
        ],
    },
    # Sections 20-23: Journey
    {
        "name": "Section 20 - Peak 2",
        "description": "Second major peak",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 2),  # Bass: Syncopated
            (2, 1),  # Hi-hat: Active
            (3, 1),  # Pad: Fm
            (4, 3),  # FX: Silent
            (5, 6),  # Delay: Tail
        ],
    },
    {
        "name": "Section 21 - Sustained Energy",
        "description": "Maintaining peak energy",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 2),  # Bass: Syncopated
            (2, 1),  # Hi-hat: Active
            (3, 1),  # Pad: Fm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 22 - Subtle Evolution",
        "description": "Gentle variations in the groove",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 3),  # Bass: Rising
            (2, 0),  # Hi-hat: Offbeats
            (3, 2),  # Pad: Gm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 23 - Continuing Journey",
        "description": "Deep hypnotic state continues",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 6),  # Bass: G Drone
            (2, 6),  # Hi-hat: Swung
            (3, 2),  # Pad: Gm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    # Sections 24-27: Final push
    {
        "name": "Section 24 - Final Buildup",
        "description": "Building to final peak",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 4),  # Bass: Staccato
            (2, 4),  # Hi-hat: 16ths
            (3, 0),  # Pad: Cm
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 25 - Maximum Energy",
        "description": "Highest energy state",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 5),  # Bass: F Drone
            (2, 4),  # Hi-hat: 16ths
            (3, 3),  # Pad: Eb
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 26 - Peak 3",
        "description": "Third and final peak",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 7),  # Bass: Alternating
            (2, 7),  # Hi-hat: 2 and 4
            (3, 6),  # Pad: Cm7
            (4, 7),  # FX: Riser
            (5, 5),  # Delay: Stutter
        ],
    },
    {
        "name": "Section 27 - Holding Peak",
        "description": "Sustaining maximum energy",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 3),  # Bass: Rising
            (2, 7),  # Hi-hat: 2 and 4
            (3, 6),  # Pad: Cm7
            (4, 1),  # FX: Impact
            (5, 5),  # Delay: Stutter
        ],
    },
    # Sections 28-29: Wind down
    {
        "name": "Section 28 - Starting to Fade",
        "description": "Beginning to strip elements back",
        "clips": [
            (0, 5),  # Kick: Sparse
            (1, 4),  # Bass: Staccato
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 29 - Final Fade Out",
        "description": "Gently fading to silence",
        "clips": [
            (0, 7),  # Kick: Soft
            (1, 4),  # Bass: Staccato
            (2, 3),  # Hi-hat: Silent
            (3, 5),  # Pad: Silent
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
]


# ============================================================================
# SETUP PHASE 1: CLEAN SESSION
# ============================================================================

print_section("FULLY AUTOMATED 2-HOUR DUB TECHNOPO SETUP")

# [1] Check existing session
print("[1/8] Checking current session...")
session = get_session_info()
result = session["result"]

if result["track_count"] > 0:
    print("  Found " + str(result["track_count"]) + " existing tracks - deleting...")
    try:
        delete_result = send_command("delete_all_tracks")
        print("  [OK] Deleted " + str(delete_result["result"]["deleted_count"]) + " tracks")
        time.sleep(0.5)
    except Exception as e:
        print("  [WARNING] Could not delete: " + str(e))
        print("  Continuing anyway (you may have duplicate tracks)")
else:
    print("  [OK] Clean session - no existing tracks")

# [2] Set tempo
print("[2/8] Setting tempo to 126 BPM...")
send_command({"type": "set_tempo", "params": {"tempo": 126.0}})
print("  [OK] Tempo set")
time.sleep(0.5)

# [3] Create 6 tracks
print("[3/8] Creating 6 tracks...")
for i in range(6):
    send_command({"type": "create_midi_track", "params": {"index": i}})
print("  [OK] 6 tracks created")
time.sleep(0.5)

# [4] Set track names
track_names = ["Kick", "Sub-bass", "Hi-hats", "Synth Pads", "FX", "Dub Delays"]
print("[4/8] Setting track names...")
for i, name in enumerate(track_names):
    send_command({"type": "set_track_name", "params": {"track_index": i, "name": name}})
    print("  [OK] Track " + str(i) + ": " + name)
time.sleep(0.5)

# [5] Load instruments with presets
print("[5/8] Loading instruments with presets...")
for track_index, track_name in enumerate(track_names):
    preset = PRESETS.get(track_name, {})

    if preset.get("preset_name") != "N/A":
        device_uri = preset["device_uri"]

        # Try to load device
        print("  Loading " + preset["preset_name"] + " on Track " + str(track_index) + "...")
        try:
            load_result = send_command(
                {"type": "load_instrument_or_effect", "params": {"track_index": track_index, "uri": device_uri}},
            )

            if load_result.get("status") == "success":
                print("  [OK] Device loaded")

                # Now try to load preset
                if preset["preset_name"] != "N/A":
                    preset_load_result = send_command(
                        {"type": "load_instrument_preset", "params": {"track_index": track_index, "device_index": 0, "preset_name": preset["preset_name"]}},
                    )

                    if preset_load_result.get("loaded", False):
                        print("  [OK] Preset '" + preset["preset_name"] + "' loaded")
                    else:
                        print("  [WARNING] Preset '" + preset["preset_name"] + "' not found")
                        # List available presets
                        available = preset_load_result.get("available_presets", [])
                        if available:
                            print("  Available presets: " + ", ".join(available[:5]) + "...")
            except Exception as e:
                print("  [ERROR] " + str(e))
    else:
        print("  [INFO] " + track_name + ": Send track (no preset)")

time.sleep(1.0)

# [6] Create send tracks
print("[6/8] Creating send tracks (Reverb + Delay)...")
send_command({"type": "create_midi_track", "params": {"index": 6}})
send_command({"type": "set_track_name", "params": {"track_index": 6, "name": "Reverb Send"}})
time.sleep(0.3)

send_command({"type": "create_midi_track", "params": {"index": 7}})
send_command({"type": "set_track_name", "params": {"track_index": 7, "name": "Delay Send"}})
time.sleep(0.3)

# [7] Load send devices
print("[7/8] Loading send devices...")
print("  Loading Hybrid Reverb on Track 6...")
send_command(
    {
        "type": "load_instrument_or_effect",
        "params": {"track_index": 6, "uri": "Audio Effects/Hybrid Reverb"},
    }
)
time.sleep(0.3)

print("  Loading Simple Delay on Track 7...")
send_command(
    {
        "type": "load_instrument_or_effect",
        "params": {"track_index": 7, "uri": "Audio Effects/Simple Delay"},
    }
)
print("  [OK] Send devices loaded")

# [8] Configure send routing (INSTRUCTIONS)
print_section("MANUAL CONFIGURATION REQUIRED")

print("\nThe following MUST be done manually in Ableton Live:")
print()

print("1. SEND ROUTING (CRITICAL - 5-10 minutes):")
print("-" * 80)
print("   For each track (0-5), create sends to Track 6 & 7:")
print()
print("   How to create sends:")
print("     a. Click on track to select it")
print("     b. Click track's 'Sends' button")
print("     c. Click 'Audio To' dropdown -> select 'Reverb Send'")
print("     d. Adjust send level knob")
print("     e. Click '+' to add second send -> select 'Delay Send'")
print("     f. Adjust second send level knob")
print()
print("   Send levels to configure:")
for track_idx in range(6):
    reverb_send = SEND_LEVELS[track_idx]["Reverb"] * 100
    delay_send = SEND_LEVELS[track_idx]["Delay"] * 100
    print("    Track " + str(track_idx) + " (" + track_names[track_idx] + "):")
    print("      -> Reverb Send: " + str(reverb_send) + "%")
    print("      -> Delay Send: " + str(delay_send) + "%")

print("-" * 80)

# [9] Set mix levels
print("[9/8] Setting mix levels...")
for track_idx in range(6):
    volume = MIX_LEVELS[track_idx]
    send_command({"type": "set_track_volume", "params": {"track_index": track_idx, "volume": volume}})
    print("  [OK] Track " + str(track_idx) + " (" + track_names[track_idx] + "): volume = " + str(volume))

# Set send track levels
send_command({"type": "set_track_volume", "params": {"track_index": 6, "volume": 0.25}})
send_command({"type": "set_track_volume", "params": {"track_index": 7, "volume": 0.2}})

time.sleep(1.0)

# [10] Manual configuration summary
print_section("AUTOMATED SETUP COMPLETE")

print("\nManual configuration required in Ableton Live:")
print()
print("1. SEND ROUTING (CRITICAL - 5-10 minutes):")
print("-" * 80)
print("   For each track (0-5), create sends to Track 6 & 7:")
print("   Use the send levels shown above")
print()
print("2. VERIFY PRESETS (1-2 minutes):")
print("-" * 80)
print("   Open each track's instrument device")
print("   Verify preset loaded correctly")
print("   If preset not found, browse Ableton's browser and load manually")
print()
print("3. ADJUST SEND DEVICES (5 minutes):")
print("-" * 80)
print("   Track 6 (Reverb Send):")
print("     - Set Size to Large (50-80%)")
print("     - Set Decay to Long (3-5 seconds)")
print("     - Set High Cut to ~4000 Hz")
print("     - Wet/Dry: 100%")
print()
print("   Track 7 (Delay Send):")
print("     - Sync: On")
print("     - Time: 1/4 note or 1/8 note")
print("     - Feedback: 40-60%")
print("     - Wet/Dry: 100%")
print()
print("4. ADJUST MIX LEVELS (2-3 minutes):")
print("-" * 80)
print("   All levels have been set to:")
for track_idx in range(6):
    volume = MIX_LEVELS[track_idx]
    db_level = -20 * (1 - volume) if volume < 1.0 else 20 * (volume - 1.0)
    print("     Track " + str(track_idx) + " (" + track_names[track_idx] + "): " + str(volume) + " (" + str(db_level) + " dB)")

print("   Set Master volume to 0.0 dB")
print()
print("5. ENABLE RECORDING:")
print("-" * 80)
print("   OPTION A: Master Recording")
print("     a. Press Shift+R to arm Master for recording")
print("     b. Master track will glow red")
print("     c. Press Record button (or R key)")
print()
print("   OPTION B: Live Export")
print("     a. File -> Export Audio/Video")
print("     b. Select 'Master' as source")
print("     c. Set format: WAV (best quality) or MP3")
print("     d. Set duration: 2:00:00")
print("     e. Click 'Export'")
print("     f. This script will run while Ableton exports")
print()
print("6. SAVE PROJECT:")
print("-" * 80)
print("   Press Ctrl+S to save project")
print("   This ensures all automation is saved")
print()
print("Recording file will be named: dubking.mp3")
print("Location: Ableton Exports folder")
print()
print("=" * 80)

# ============================================================================
# RECORDING PHASE: 2-HOUR AUTOMATION
# ============================================================================

ready = input("\nPress Enter when ready to start 2-hour recording (with sends configured): ").strip()

if ready.lower() == 'y':
    print_section("STARTING 2-HOUR PLAYBACK AUTOMATION")
    print()

    # Fire initial clips for Section 0
    print("\n[00:00] Section 0 - Deep Intro")
    section = sections[0]
    for track_index, clip_index in section["clips"]:
        fire_clip(track_index, clip_index)

    # Start playback
    start_playback()
    print("  [OK] Playback started")
    time.sleep(1)

    # Progress through all sections
    for section_idx in range(1, 30):
        section = sections[section_idx]
        elapsed_minutes = section_idx * 4
        hours = elapsed_minutes // 60
        minutes = elapsed_minutes % 60

        # Calculate progress
        progress = section_idx / 30
        bar_length = 40
        filled = int(bar_length * progress)
        progress_bar = "[" + "=" * filled + "-" * (bar_length - filled) + "]"

        print("\n" + progress_bar + " " + str(progress * 100) + "%")
        print("[" + str(hours).zfill(2) + ":" + str(minutes).zfill(2) + "] Section " + str(section_idx) + " - " + section["name"])
        print("  Description: " + section["description"])

        # Fire clips for this section
        for track_index, clip_index in section["clips"]:
            fire_clip(track_index, clip_index)

        print("  [OK] Clips fired")

        # Wait 4 minutes for this section (240 seconds)
        for remaining in range(240, 0, -60):
            minutes_left = remaining // 60
            if minutes_left > 0:
                time.sleep(60)
            else:
                time.sleep(remaining)
                break

    # Final section complete
    final_progress = 1.0
    progress_bar = "[" + "=" * 40 + "]"
    print("\n" + progress_bar + " " + str(final_progress * 100) + "%")
    print("\n" + "=" * 80)
    print("2-HOUR PLAYBACK COMPLETE!")
    print("=" * 80)
    print()
    print("All 30 sections have been played.")
    print("Total duration: 2 hours (120 minutes)")
    print()
    print("Your recording in Ableton should now contain the full 2-hour track.")
    print()
    print("NEXT STEPS:")
    print("  1. Stop recording in Ableton")
    print("  2. Check that dubking.mp3 was created in Exports folder")
    print("  3. Listen back to verify quality")
else:
    print("\nSetup paused. Run this script again when you're ready.")
    print()
    print("Remember to:")
    print("  1. Create send routing in Ableton (5-10 minutes)")
    print("  2. Verify presets (1-2 minutes)")
    print("  3. Adjust mix levels (2-3 minutes)")
    print("  4. Save project (Ctrl+S)")
    print("  5. Enable recording (Shift+R or File > Export)")
    print("  6. Run this script again and press Enter")

s.close()
