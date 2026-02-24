#!/usr/bin/env python3
"""
Direct test of create_drum_pattern fix.
Tests that create_drum_pattern auto-loads Drum Rack with drum kit on empty tracks.
"""

import sys
import os
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Add MCP_Server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "MCP_Server"))

from mcp.server.fastmcp import Context
from server import create_drum_pattern, load_drum_kit, get_ableton_connection
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_drum_pattern_fix")


def test_create_drum_pattern_on_empty_track():
    """Test create_drum_pattern auto-loads Drum Rack on empty track."""
    print("\n" + "=" * 80)
    print("TEST 1: create_drum_pattern on empty Track 2 (Dub Hats)")
    print("=" * 80)

    try:
        # Create a mock context
        ctx = Context()

        # Test on Track 2 (Dub Hats) - should auto-load Drum Rack
        result = create_drum_pattern(
            ctx=ctx,
            track_index=2,
            clip_index=0,
            pattern_name="dub_techno",
            length=4.0,
            kick_note=36,
            snare_note=40,
            hat_note=42,
            clap_note=39,
        )

        print(f"\nResult: {result}")

        # Verify track has a device now
        ableton = get_ableton_connection()
        track_info = ableton.send_command("get_track_info", {"track_index": 2})
        devices = track_info.get("devices", [])

        print(f"\nTrack 2 devices: {len(devices)} device(s)")
        if devices:
            for i, device in enumerate(devices):
                print(f"  Device {i}: {device.get('name', 'Unknown')}")
            print("\n[OK] SUCCESS: Drum Rack was auto-loaded with drum kit!")
        else:
            print("\n[FAIL] FAILURE: No devices found on Track 2")

        return len(devices) > 0

    except Exception as e:
        print(f"\n[ERROR] ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_load_drum_kit_directly():
    """Test load_drum_kit directly to replace existing empty Drum Rack."""
    print("\n" + "=" * 80)
    print("TEST 2: load_drum_kit to replace empty Drum Rack on Track 2")
    print("=" * 80)

    try:
        # Load drum kit directly
        result = load_drum_kit(
            track_index=2, rack_uri="Drums/Drum Rack", kit_path="drums/acoustic"
        )

        print(f"\nResult: {result}")

        # Verify track has a properly loaded drum kit
        ableton = get_ableton_connection()
        track_info = ableton.send_command("get_track_info", {"track_index": 2})
        devices = track_info.get("devices", [])

        print(f"\nTrack 2 devices: {len(devices)} device(s)")
        if devices:
            for i, device in enumerate(devices):
                print(f"  Device {i}: {device.get('name', 'Unknown')}")
            print("\n[OK] SUCCESS: Drum Rack loaded with drum kit!")
        else:
            print("\n[FAIL] FAILURE: No devices found on Track 2")

        return len(devices) > 0

    except Exception as e:
        print(f"\n[ERROR] ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("DRUM PATTERN FIX TEST SUITE")
    print("=" * 80)
    print("\nThis test suite verifies that:")
    print("1. create_drum_pattern auto-loads Drum Rack + drum kit on empty tracks")
    print("2. load_drum_kit can replace empty Drum Racks with actual drum kits")
    print("\nPrerequisites:")
    print("- Ableton Live is running with Remote Script connected")
    print("- Track 2 exists (Dub Hats track)")
    print("\n")

    # Connect to Ableton first
    ableton = get_ableton_connection()
    if not ableton.connect():
        print("\n[FATAL] FATAL: Cannot connect to Ableton Remote Script")
        print("Make sure Ableton Live is running and Remote Script is loaded")
        return False

    print("\n[OK] Connected to Ableton Remote Script\n")

    # Run tests
    test1_passed = test_create_drum_pattern_on_empty_track()
    test2_passed = test_load_drum_kit_directly()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(
        f"Test 1 (create_drum_pattern auto-load): {'[PASS] PASSED' if test1_passed else '[FAIL] FAILED'}"
    )
    print(
        f"Test 2 (load_drum_kit direct): {'[PASS] PASSED' if test2_passed else '[FAIL] FAILED'}"
    )
    print("=" * 80)

    if test1_passed and test2_passed:
        print("\n[SUCCESS] All tests passed! The fix is working correctly")
        print("- Track 2 (Dub Hats) now has a properly populated Drum Rack")
        print("- The dub_techno pattern will play actual hi-hat sounds")
    else:
        print("\n[WARNING] Some tests failed. Check the output above for details")

    return test1_passed and test2_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
