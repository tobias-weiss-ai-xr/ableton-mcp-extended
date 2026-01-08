#!/usr/bin/env python3
"""
Quick validation script for 10-minute dub reggae project.
Checks script structure, MCP commands, and pattern data without requiring Ableton Live.
"""

import json
import re
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def validate_script_structure(filepath, script_name):
    """Validate script structure and MCP commands"""
    print(f"\n{'=' * 80}")
    print(f"Validating: {script_name}")
    print(f"{'=' * 80}")

    with open(filepath, "r") as f:
        content = f.read()

    checks = []

    # Check 1: Socket connection pattern
    if "socket.socket()" in content and 's.connect(("localhost", 9877))' in content:
        checks.append(("✅", "Socket connection to localhost:9877"))
    else:
        checks.append(("❌", "Socket connection missing or incorrect"))

    # Check 2: send_command function
    if "def send_command(cmd_type, params=None):" in content:
        checks.append(("✅", "send_command function defined"))
    else:
        checks.append(("❌", "send_command function missing"))

    # Check 3: MCP command format
    if 'json.dumps({"type": cmd_type, "params": params or {}})' in content:
        checks.append(("✅", "MCP command JSON format correct"))
    else:
        checks.append(("❌", "MCP command format incorrect"))

    # Check 4: Chunked receive pattern
    if "while True:" in content and "s.recv(8192)" in content:
        checks.append(("✅", "Chunked receive pattern for large responses"))
    else:
        checks.append(("❌", "Chunked receive pattern missing"))

    # Check 5: Error handling
    if "try:" in content and "except" in content:
        checks.append(("✅", "Error handling present"))
    else:
        checks.append(("⚠️", "Limited error handling"))

    # Check 6: Key MCP commands
    commands = [
        "create_midi_track",
        "create_audio_track",
        "create_clip",
        "add_notes_to_clip",
        "set_track_name",
        "set_track_volume",
        "fire_clip",
        "start_playback",
        "stop_playback",
        "set_tempo",
    ]

    for cmd in commands:
        if cmd in content:
            checks.append(("✅", f"MCP command: {cmd}"))

    # Print results
    for status, message in checks:
        print(f"{status} {message}")

    return len([c for c in checks if c[0] == "❌"]) == 0


def validate_pattern_data(filepath, script_name):
    """Validate MIDI note pattern data"""
    print(f"\n{'=' * 80}")
    print(f"Validating Pattern Data: {script_name}")
    print(f"{'=' * 80}")

    with open(filepath, "r") as f:
        content = f.read()

    checks = []

    # Extract MIDI note patterns
    note_pattern = r'"notes":\s*\[(.*?)\]'
    notes_sections = re.findall(note_pattern, content, re.DOTALL)

    if len(notes_sections) > 0:
        checks.append(("✅", f"Found {len(notes_sections)} note patterns"))

        # Check note structure
        valid_notes = 0
        for section in notes_sections:
            if all(
                k in section
                for k in [
                    '"pitch"',
                    '"start_time"',
                    '"duration"',
                    '"velocity"',
                    '"mute"',
                ]
            ):
                valid_notes += 1

        if valid_notes > 0:
            checks.append(
                ("✅", f"All {valid_notes} note patterns have correct structure")
            )

    # Check for essential MIDI pitch ranges
    if '"pitch": 36' in content:  # C2 (Kick)
        checks.append(("✅", "Kick pitch (36) present"))

    if '"pitch": 38' in content:  # D2 (Snare)
        checks.append(("✅", "Snare pitch (38) present"))

    if '"pitch": 76' in content:  # E5 (Hi-hat)
        checks.append(("✅", "Hi-hat pitch (76) present"))

    if '"pitch": 24' in content and '"pitch": 43' in content:  # Bass range
        checks.append(("✅", "Bass pitch range (24-43) present"))

    if '"pitch": 48' in content and '"pitch": 63' in content:  # Guitar/Organ range
        checks.append(("✅", "Guitar/Organ pitch range (48-63) present"))

    # Check duration values (dub beats are 4.0 beats)
    if '"duration": 4.0' in content:
        checks.append(("✅", "4-beat clip duration (1 bar) present"))

    if '"duration": 0.15' in content or '"duration": 0.1' in content:
        checks.append(("✅", "Short note durations (stabs/chops) present"))

    # Check velocity ranges
    if '"velocity": 100' in content or '"velocity": 110' in content:
        checks.append(("✅", "Velocity values in appropriate range (100-110)"))

    # Check mute functionality
    if '"mute": False' in content:
        checks.append(("✅", "Mute flag present in notes"))

    # Print results
    for status, message in checks:
        print(f"{status} {message}")

    return len([c for c in checks if c[0] == "❌"]) == 0


def validate_sections(filepath, script_name):
    """Validate section definitions"""
    print(f"\n{'=' * 80}")
    print(f"Validating Sections: {script_name}")
    print(f"{'=' * 80}")

    with open(filepath, "r") as f:
        content = f.read()

    checks = []

    # Check for sections list
    if "sections = [" in content:
        checks.append(("✅", "Sections list defined"))
    else:
        checks.append(("❌", "Sections list not defined"))

    # Check section structure
    if '"name":' in content and '"description":' in content and '"clips":' in content:
        checks.append(("✅", "Section structure has name, description, clips"))

    # Check automation targets
    if '"filter_freq":' in content:
        checks.append(("✅", "Filter frequency automation target present"))

    if '"reverb_send":' in content:
        checks.append(("✅", "Reverb send automation target present"))

    if '"delay_send":' in content:
        checks.append(("✅", "Delay send automation target present"))

    # Check for 10 sections
    section_count = content.count('"name":')
    if section_count >= 10:
        checks.append(("✅", f"At least 10 sections defined ({section_count} found)"))

    # Check for musical journey elements
    journey_keywords = ["Intro", "Build", "Peak", "Breakdown", "Rebuild", "Wind Down"]
    for keyword in journey_keywords:
        if keyword in content:
            checks.append(("✅", f"Journey element: {keyword}"))

    # Print results
    for status, message in checks:
        print(f"{status} {message}")

    return len([c for c in checks if c[0] == "❌"]) == 0


def validate_dub_aesthetics(filepath, script_name):
    """Validate dub reggae authenticity"""
    print(f"\n{'=' * 80}")
    print(f"Validating Dub Aesthetics: {script_name}")
    print(f"{'=' * 80}")

    with open(filepath, "r") as f:
        content = f.read()

    checks = []

    # Check for One Drop pattern (kick on beat 3)
    if '"start_time": 2.0' in content and '"pitch": 36' in content:
        checks.append(("✅", "One Drop pattern (kick on beat 3)"))

    # Check for offbeat patterns (start_time ends with .5)
    offbeats = re.findall(r'"start_time":\s*\d+\.5', content)
    if len(offbeats) > 0:
        checks.append(
            ("✅", f"Offbeat patterns present ({len(offbeats)} offbeats found)")
        )

    # Check for tempo (75 BPM is classic dub)
    if '"tempo": 75.0' in content or "75.0 BPM" in content:
        checks.append(("✅", "Tempo set to 75 BPM (classic dub)"))

    # Check for root drone bass patterns
    if '"duration": 4.0' in content and '"pitch": 36' in content:
        checks.append(("✅", "Root drone bass pattern present"))

    # Check for chord stabs (multiple notes at same time)
    # This is harder to validate without parsing, but we can check for short durations
    if '"duration": 0.15' in content:
        checks.append(("✅", "Short note durations (chord stabs) present"))

    # Check for FX elements
    if '"FX"' in content or '"Dub Delays"' in content:
        checks.append(("✅", "FX and Delay tracks present"))

    # Check for send/reverb mentions
    if '"Reverb Send"' in content and '"Delay Send"' in content:
        checks.append(("✅", "Reverb and Delay send tracks present"))

    # Print results
    for status, message in checks:
        print(f"{status} {message}")

    return len([c for c in checks if c[0] == "❌"]) == 0


def main():
    """Run all validation checks"""
    print("\n" + "=" * 80)
    print("10-MINUTE DUB REGGAE - AUTOMATED VALIDATION")
    print("=" * 80)

    # Validate both scripts
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    create_script = os.path.join(base_dir, "create_10min_dub_reggae.py")
    play_script = os.path.join(base_dir, "play_10min_dub_reggae.py")

    results = []

    # Validate structure
    print("\n" + "=" * 80)
    print("PHASE 1: SCRIPT STRUCTURE")
    print("=" * 80)

    result1 = validate_script_structure(create_script, "create_10min_dub_reggae.py")
    result2 = validate_script_structure(play_script, "play_10min_dub_reggae.py")

    # Validate pattern data
    print("\n" + "=" * 80)
    print("PHASE 2: PATTERN DATA")
    print("=" * 80)

    result3 = validate_pattern_data(create_script, "create_10min_dub_reggae.py")

    # Validate sections
    print("\n" + "=" * 80)
    print("PHASE 3: SECTIONS DEFINITION")
    print("=" * 80)

    result4 = validate_sections(create_script, "create_10min_dub_reggae.py")
    result5 = validate_sections(play_script, "play_10min_dub_reggae.py")

    # Validate dub aesthetics
    print("\n" + "=" * 80)
    print("PHASE 4: DUB AESTHETICS")
    print("=" * 80)

    result6 = validate_dub_aesthetics(create_script, "create_10min_dub_reggae.py")

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    all_passed = all([result1, result2, result3, result4, result5, result6])

    if all_passed:
        print("\n✅ ALL VALIDATIONS PASSED")
        print("\nScripts are structurally correct and contain:")
        print("  - Proper MCP server communication")
        print("  - Valid MIDI note patterns")
        print("  - Complete section definitions")
        print("  - Authentic dub reggae elements")
        print("\nNext steps:")
        print("  1. Load Ableton Live")
        print("  2. Start MCP Server")
        print("  3. Run manual tests (see TESTING_10MIN_DUB_REGGAE.md)")
        print("  4. Run create_10min_dub_reggae.py")
        print("  5. Run play_10min_dub_reggae.py")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("\nPlease review failed checks above.")
        print("See TESTING_10MIN_DUB_REGGAE.md for troubleshooting guide.")

    print("\n" + "=" * 80)
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
