import socket
import json
import time

# ============================================================================
# FULLY AUTOMATED 2-HOUR DUB TECHNOPO SETUP & RECORDING
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


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


def fire_clip(track_index, clip_index):
    """Fire a specific clip"""
    send_command("fire_clip", {"track_index": track_index, "clip_index": clip_index})


def start_playback():
    """Start playback"""
    send_command("start_playback", {})


def stop_playback():
    """Stop playback"""
    send_command("stop_playback", {})


# ============================================================================
# TRACK NAMES
# ============================================================================
TRACK_NAMES = [
    "Kick",
    "Sub-bass",
    "Hi-hats",
    "Synth Pads",
    "FX",
    "Dub Delays",
]


# ============================================================================
# PRESET DEFINITIONS
# ============================================================================
PRESETS = [
    {
        "name": "Kick - Punchy",
        "device_uri": "Operator",
    },
    {
        "name": "Sub Bass - Deep",
        "device_uri": "Tension",
    },
    {
        "name": "Basic",
        "device_uri": "Drums/Drum Rack",
    },
    {
        "name": "Atmospheric",
        "device_uri": "Wavetable",
    },
    {
        "name": "FX - One Shot",
        "device_uri": "Instruments/Simpler",
    },
    {
        "name": "Dub Delays - Send",
        "device_uri": None,  # No instrument for send track
    },
]


# ============================================================================
# SECTION DEFINITIONS (30 sections, 4 minutes each)
# ============================================================================
sections = [
    # PHASE 1: INTRODUCTION (0:00 - 0:16)
    {
        "name": "Section 0 - Deep Intro",
        "description": "Minimal elements establish groove",
        "clips": [(0, 0), (1, 0), (2, 2), (3, 4), (4, 3), (5, 2)],
    },
    {
        "name": "Section 1 - Subtle Build",
        "description": "Adding slight variations, more delays",
        "clips": [(0, 0), (1, 0), (2, 0), (3, 4), (4, 3), (5, 0)],
    },
    {
        "name": "Section 2 - Atmosphere Enters",
        "description": "Synth pads create depth",
        "clips": [(0, 1), (1, 1), (2, 0), (3, 0), (4, 3), (5, 0)],
    },
    {
        "name": "Section 3 - First Build",
        "description": "Energy starts to rise",
        "clips": [(0, 1), (1, 2), (2, 0), (3, 0), (4, 1), (5, 0)],
    },
    # PHASE 2: HYPNOTIC GROOVE (0:16 - 0:32)
    {
        "name": "Section 4 - Hypnotic State",
        "description": "Full groove engaged",
        "clips": [(0, 2), (1, 2), (2, 1), (3, 0), (4, 3), (5, 1)],
    },
    {
        "name": "Section 5 - Slight Shift",
        "description": "Subtle evolution continues",
        "clips": [(0, 2), (1, 3), (2, 1), (3, 1), (4, 3), (5, 1)],
    },
    {
        "name": "Section 6 - Building Up",
        "description": "More energy in hi-hats",
        "clips": [(0, 2), (1, 3), (2, 1), (3, 2), (4, 3), (5, 1)],
    },
    {
        "name": "Section 7 - First Peak",
        "description": "Elements come together",
        "clips": [(0, 0), (1, 4), (2, 4), (3, 2), (4, 1), (5, 1)],
    },
    # PHASE 3: FIRST BUILD (0:32 - 0:48)
    {
        "name": "Section 8 - Intensify",
        "description": "Energy continues to rise",
        "clips": [(0, 3), (1, 4), (2, 5), (3, 2), (4, 0), (5, 2)],
    },
    {
        "name": "Section 9 - Peak Moments",
        "description": "Maximum energy so far",
        "clips": [(0, 3), (1, 5), (2, 5), (3, 3), (4, 0), (5, 3)],
    },
    {
        "name": "Section 10 - Plateau",
        "description": "Sustaining high energy",
        "clips": [(0, 3), (1, 5), (2, 5), (3, 3), (4, 0), (5, 3)],
    },
    {
        "name": "Section 11 - Last Peak",
        "description": "Final peak before breakdown",
        "clips": [(0, 3), (1, 6), (2, 6), (3, 4), (4, 0), (5, 4)],
    },
    # PHASE 4: BREAKDOWN (0:48 - 1:04)
    {
        "name": "Section 12 - Breakdown Start",
        "description": "Removing elements, creating space",
        "clips": [(0, 2), (1, 2), (2, 1), (3, 4), (4, 2), (5, 2)],
    },
    {
        "name": "Section 13 - Deep Space",
        "description": "Minimal atmosphere",
        "clips": [(0, 1), (1, 1), (2, 2), (3, 5), (4, 2), (5, 2)],
    },
    {
        "name": "Section 14 - Floating",
        "description": "Hypnotic minimal state",
        "clips": [(0, 1), (1, 0), (2, 2), (3, 5), (4, 3), (5, 2)],
    },
    {
        "name": "Section 15 - Return",
        "description": "Elements slowly return",
        "clips": [(0, 2), (1, 1), (2, 0), (3, 4), (4, 3), (5, 2)],
    },
    # PHASE 5: SECOND BUILD (1:04 - 1:20)
    {
        "name": "Section 16 - Build Again",
        "description": "Energy starts returning",
        "clips": [(0, 2), (1, 2), (2, 0), (3, 2), (4, 3), (5, 1)],
    },
    {
        "name": "Section 17 - More Layers",
        "description": "Adding elements back",
        "clips": [(0, 2), (1, 3), (2, 1), (3, 2), (4, 2), (5, 1)],
    },
    {
        "name": "Section 18 - Approaching",
        "description": "Building toward second peak",
        "clips": [(0, 3), (1, 4), (2, 1), (3, 3), (4, 2), (5, 2)],
    },
    {
        "name": "Section 19 - Peak",
        "description": "Second major peak",
        "clips": [(0, 3), (1, 5), (2, 5), (3, 3), (4, 1), (5, 3)],
    },
    # PHASE 6: JOURNEY (1:20 - 1:36)
    {
        "name": "Section 20 - Hypnotic Groove",
        "description": "Sustaining the groove",
        "clips": [(0, 2), (1, 2), (2, 1), (3, 2), (4, 3), (5, 1)],
    },
    {
        "name": "Section 21 - Deep Trance",
        "description": "Evolution in subtleties",
        "clips": [(0, 2), (1, 3), (2, 1), (3, 3), (4, 3), (5, 1)],
    },
    {
        "name": "Section 22 - Subtle Changes",
        "description": "Small variations",
        "clips": [(0, 2), (1, 3), (2, 0), (3, 3), (4, 2), (5, 2)],
    },
    {
        "name": "Section 23 - Continuing",
        "description": "Hypnotic journey continues",
        "clips": [(0, 2), (1, 2), (2, 1), (3, 2), (4, 3), (5, 1)],
    },
    # PHASE 7: FINAL PUSH (1:36 - 1:52)
    {
        "name": "Section 24 - Building Final",
        "description": "Energy rising again",
        "clips": [(0, 3), (1, 4), (2, 5), (3, 3), (4, 2), (5, 2)],
    },
    {
        "name": "Section 25 - More Intense",
        "description": "Maximum layers",
        "clips": [(0, 3), (1, 5), (2, 5), (3, 4), (4, 1), (5, 3)],
    },
    {
        "name": "Section 26 - Complex",
        "description": "Complex layers and rhythms",
        "clips": [(0, 3), (1, 6), (2, 6), (3, 4), (4, 0), (5, 4)],
    },
    {
        "name": "Section 27 - Peak",
        "description": "Final peak intensity",
        "clips": [(0, 3), (1, 6), (2, 6), (3, 5), (4, 0), (5, 4)],
    },
    # PHASE 8: WIND DOWN (1:52 - 2:00)
    {
        "name": "Section 28 - Fading",
        "description": "Stripping back elements",
        "clips": [(0, 2), (1, 3), (2, 1), (3, 4), (4, 2), (5, 2)],
    },
    {
        "name": "Section 29 - Fading Out",
        "description": "Minimal to end",
        "clips": [(0, 1), (1, 1), (2, 2), (3, 5), (4, 3), (5, 2)],
    },
]


print("FULLY AUTOMATED 2-HOUR DUB TECHNOPO SETUP")
print("=" * 80)

# [1] Clean session and set tempo
print("[1/8] Cleaning session and setting tempo to 126 BPM...")
try:
    delete_result = send_command("delete_all_tracks")
    print("  [OK] Deleted " + str(delete_result["result"]["deleted_count"]) + " tracks")
except Exception as e:
    print(f"  [WARNING] Could not delete tracks: {str(e)}")
time.sleep(0.5)

send_command({"type": "set_tempo", "params": {"tempo": 126.0}})
print("  [OK] Tempo set to 126 BPM")
time.sleep(0.5)

# [2] Create 6 tracks
print("[2/8] Creating 6 main tracks...")
for i in range(6):
    send_command({"type": "create_midi_track", "params": {"index": i}})
print("  [OK] 6 tracks created (indices 0-5)")
time.sleep(0.5)

# [3] Set track names
print("[3/8] Setting track names...")
for i, name in enumerate(TRACK_NAMES):
    send_command({"type": "set_track_name", "params": {"track_index": i, "name": name}})
    print("  [OK] Track " + str(i) + ": " + name)
time.sleep(0.5)

# [4] Load instruments with presets
print("[4/8] Loading instruments with presets...")
for track_index in range(6):
    preset = PRESETS[track_index]
    preset_name = preset["name"]
    device_uri = preset.get("device_uri")

    if device_uri:
        print("  Loading " + preset_name + " on Track " + str(track_index) + "...")
        try:
            load_result = send_command(
                "load_browser_item",
                {"track_index": track_index, "item_uri": device_uri},
            )
            if load_result.get("loaded"):
                print("  [OK] Device loaded")

                # Try to load preset if available
                if preset_name != "Dub Delays - Send":
                    try:
                        preset_result = send_command(
                            "load_instrument_preset",
                            {
                                "track_index": track_index,
                                "device_index": 0,
                                "preset_name": preset_name,
                            },
                        )
                        if preset_result.get("loaded"):
                            print("  [OK] Preset loaded")
                        else:
                            available = preset_result.get("available_presets", [])
                            if available:
                                print(
                                    "  [INFO] Available presets (showing first 5): "
                                    + ", ".join(available[:5])
                                )
                    except Exception as e:
                        pass  # Preset loading failed silently
        except Exception as e:
            print("  [WARNING] " + str(e))
    else:
        print("  [INFO] Track 5 (Dub Delays) - no instrument to load")

time.sleep(1.0)

# [5] Create send tracks
print("[5/8] Creating 2 send tracks (Reverb + Delay)...")
send_command("create_midi_track", {"index": 6})
send_command("set_track_name", {"track_index": 6, "name": "Reverb Send"})
time.sleep(0.3)
send_command("create_midi_track", {"index": 7})
send_command("set_track_name", {"track_index": 7, "name": "Delay Send"})
print("  [OK] 2 send tracks created (indices 6-7)")
time.sleep(0.3)

# [6] Load send devices
print("[6/8] Loading send devices...")
try:
    send_command(
        "load_browser_item",
        {"track_index": 6, "item_uri": "Audio Effects/Hybrid Reverb"},
    )
    print("  [OK] Hybrid Reverb loaded on Track 6")
except Exception as e:
    print(f"  [ERROR] Could not load Hybrid Reverb: {str(e)}")

try:
    send_command(
        "load_browser_item",
        {"track_index": 7, "item_uri": "Audio Effects/Simple Delay"},
    )
    print("  [OK] Simple Delay loaded on Track 7")
except Exception as e:
    print(f"  [ERROR] Could not load Simple Delay: {str(e)}")

time.sleep(0.5)

# [7] Set mix levels (normalized values)
print("[7/8] Setting initial mix levels...")
MIX_LEVELS = [
    0.75,
    0.60,
    0.30,
    0.15,
    0.20,
    0.25,
]  # Kick, Sub-bass, Hi-hats, Pads, FX, Delays
for track_index in range(6):
    volume = MIX_LEVELS[track_index]
    send_command(
        "set_track_volume",
        {"track_index": track_index, "volume": volume},
    )
    print(
        "  [OK] Track "
        + str(track_index)
        + " ("
        + TRACK_NAMES[track_index]
        + "): volume = "
        + str(volume)
    )

# Set send tracks
send_command(
    "set_track_volume", {"track_index": 6, "volume": 0.25}
)  # Reverb Send: -12 dB
send_command(
    "set_track_volume", {"track_index": 7, "volume": 0.20}
)  # Delay Send: -14 dB

print("  [OK] Send levels set")
time.sleep(0.5)

# [8] Manual instructions
print_section("MANUAL CONFIGURATION REQUIRED")

print("\nCRITICAL: The following MUST be done manually in Ableton Live:")
print()

print("1. SEND ROUTING (5-10 minutes - MOST IMPORTANT):")
print("-" * 80)
print("   For each main track (0-5), create sends to Tracks 6 & 7:")
print("   Track 0 (Kick):     -> Track 6: 0%,  -> Track 7: 0%")
print("   Track 1 (Sub-bass): -> Track 6: 10%,  -> Track 7: 10%")
print("   Track 2 (Hi-hats): -> Track 6: 30%,  -> Track 7: 30%")
print("   Track 3 (Pads):     -> Track 6: 50%,  -> Track 7: 50%")
print("   Track 4 (FX):       -> Track 6: 70%,  -> Track 7: 70%")
print("   Track 5 (Delays):   -> Track 6: 100%, -> Track 7: 100%")
print()
print("   HOW TO CREATE SENDS IN ABLETON:")
print("     a. Click on track 0 to select it")
print("     b. Click track's 'Sends' button (below the clip matrix)")
print("     c. Click 'Audio To' dropdown menu")
print("     d. Select '6 - Reverb Send'")
print("     e. Adjust Reverb send level knob")
print("     f. Click '+' button (next to sends dropdown)")
print("     g. Select '7 - Delay Send'")
print("     h. Adjust Delay send level knob")
print()
print("2. VERIFY PRESETS (2-3 minutes):")
print("-" * 80)
print("   Double-click each instrument device to verify presets")
print("   If preset didn't load, open device and browse to it")
print("   For Operator (Track 0): Create punchy kick")
print("   For Tension (Track 1): Create deep sub sound")
print("   For Drum Rack (Track 2): Hi-hat samples loaded")
print("   For Wavetable (Track 3): Choose atmospheric pad")
print("   For Simpler (Track 4): Load FX samples")
print()
print("3. CONFIGURE SEND DEVICES (3-5 minutes):")
print("-" * 80)
print("   Track 6 (Reverb Send):")
print("     - Double-click Hybrid Reverb")
print("     - Set Size: Large (50-80%)")
print("     - Set Decay: Long (3-5 seconds)")
print("     - Set High Cut: ~4000 Hz")
print("     - Wet/Dry: 100%")
print()
print("   Track 7 (Delay Send):")
print("     - Double-click Simple Delay")
print("     - Sync: On")
print("     - Time: 1/4 or 1/8 note")
print("     - Feedback: 40-60%")
print("     - Wet/Dry: 100%")
print()
print("4. ADJUST MIX LEVELS (1-2 minutes):")
print("-" * 80)
print("   All levels set to:")
for i, volume in enumerate(MIX_LEVELS):
    db_level = int(-20 * (1 - volume)) if volume < 1.0 else int(-20 * (volume - 1.0))
    print(
        "     Track "
        + str(i)
        + " ("
        + TRACK_NAMES[i]
        + "): "
        + str(volume)
        + " ("
        + str(db_level)
        + " dB)"
    )
print()
print("   Master: 0.0 (0 dB)")
print()
print("5. ENABLE RECORDING:")
print("-" * 80)
print("   OPTION A: Master Recording")
print("     - Press Shift+R to arm Master track")
print("     - Master track will glow red")
print("     - Press Record button (or R key)")
print()
print("   OPTION B: Live Export (RECOMMENDED):")
print("     - File > Export Audio/Video")
print("     - Select 'Master' as source")
print("     - Set format: WAV (best quality) or MP3")
print("     - Set duration: 2:00:00")
print("     - Click 'Export'")
print("     - Script will run while Ableton exports automatically")
print()
print("6. SAVE PROJECT:")
print("-" * 80)
print("   Press Ctrl+S to save project")
print("   Ensures all automation is preserved")
print()
print("Recording file will be named: dubking.mp3")
print("Location: Ableton Exports folder")
print("=" * 80)

# ============================================================================
# RECORDING PHASE: 2-HOUR AUTOMATION
# ============================================================================

ready = input(
    "\nEnter 'y' to start 2-hour recording (after manual setup is complete): "
).strip()

run_automation = ready.lower() in ["y", "yes"]

if run_automation:
    print_section("STARTING 2-HOUR PLAYBACK AUTOMATION")
    print()

    # Fire initial clips for Section 0
    print("[00:00] Section 0 - Deep Intro")
    section = sections[0]
    for track_index, clip_index in section["clips"]:
        fire_clip(track_index, clip_index)

    # Start playback
    start_playback()
    print("  [OK] Playback started")
    time.sleep(1)

    # Progress through all sections (30 sections, 4 minutes each)
    for section_idx in range(1, 30):
        section = sections[section_idx]
        elapsed_minutes = section_idx * 4
        hours = elapsed_minutes // 60
        minutes = elapsed_minutes % 60

        # Calculate progress
        progress = section_idx / 30.0
        bar_length = 40
        filled = int(bar_length * progress)
        progress_bar = "[" + "=" * filled + "-" * (bar_length - filled) + "]"

        print("\n" + progress_bar + " " + str(progress * 100.0) + "%")
        print(
            "["
            + str(hours).zfill(2)
            + ":"
            + str(minutes).zfill(2)
            + "] Section "
            + str(section_idx)
            + " - "
            + section["name"]
        )
        print("  Description: " + section["description"])

        # Fire clips for this section
        for track_index, clip_index in section["clips"]:
            fire_clip(track_index, clip_index)

        print("  [OK] Clips fired")

        # Wait 4 minutes for this section
        remaining_seconds = 240
        while remaining_seconds > 0:
            sleep_time = min(60, remaining_seconds)
            time.sleep(sleep_time)
            remaining_seconds -= sleep_time

    # Final section complete
    final_progress = 100.0
    progress_bar = "[" + "=" * 40 + "]"
    print("\n" + progress_bar + " " + str(final_progress) + "%")
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
    print()
    print("Press Enter to close connection...")
    input()
else:
    print(
        "\nSetup paused. Run this script again when manual configuration is complete."
    )
    print()
    print("Remember to:")
    print("  1. Create send routing (5-10 minutes) - most critical for dub atmosphere!")
    print("  2. Verify presets (2-3 minutes)")
    print("  3. Adjust mix levels (1-2 minutes)")
    print("  4. Save project (Ctrl+S)")
    print("  5. Enable recording (Shift+R or File > Export)")
    print("  6. Run this script again and press 'y'")

# Close socket connection
s.close()
print("\n[OK] Connection closed")
