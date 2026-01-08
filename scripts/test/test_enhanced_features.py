"""
Test script for all enhanced MCP server features
Tests all new automation capabilities
"""

import socket
import json
import time


def send_command(cmd_type, params=None):
    """Send a command and return full response"""
    s = socket.socket()
    s.connect(("localhost", 9877))
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))

    data = b""
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue
    s.close()
    return json.loads(data.decode("utf-8"))


def test_result(test_name, result):
    """Print test result"""
    status = "✓ PASS" if result.get("status") == "success" else "✗ FAIL"
    print(f"{status} | {test_name}")
    if result.get("status") == "error":
        print(f"         Error: {result.get('message', 'Unknown error')}")
    return result.get("status") == "success"


def main():
    print("=" * 60)
    print("TESTING ENHANCED MCP SERVER FEATURES")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    # ============================================================================
    # TRACK MANAGEMENT TESTS
    # ============================================================================
    print("1. TRACK MANAGEMENT")
    print("-" * 60)

    try:
        result = send_command("get_all_tracks")
        if test_result("Get all tracks", result):
            tracks = result.get("result", {}).get("tracks", [])
            print(f"         Found {len(tracks)} tracks")
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Get all tracks")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("get_master_track_info")
        if test_result("Get master track info", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Get master track info")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("get_return_tracks")
        if test_result("Get return tracks", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Get return tracks")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # SCENE MANAGEMENT TESTS
    # ============================================================================
    print("2. SCENE MANAGEMENT")
    print("-" * 60)

    try:
        result = send_command("get_all_scenes")
        if test_result("Get all scenes", result):
            scenes = result.get("result", {}).get("scenes", [])
            print(f"         Found {len(scenes)} scenes")
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Get all scenes")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("create_scene", {"index": -1})
        if test_result("Create scene", result):
            scene_idx = result.get("result", {}).get("scene_index", -1)
            passed += 1

            # Test rename scene
            result = send_command(
                "set_scene_name", {"scene_index": scene_idx, "name": "Test Scene"}
            )
            if test_result("Set scene name", result):
                passed += 1
            else:
                failed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Create scene")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # CLIP MANAGEMENT TESTS
    # ============================================================================
    print("3. CLIP MANAGEMENT")
    print("-" * 60)

    try:
        result = send_command("create_midi_track", {"index": -1})
        if test_result("Create MIDI track", result):
            track_idx = result.get("result", {}).get("index", -1)
            passed += 1

            # Create a clip
            result = send_command(
                "create_clip",
                {"track_index": track_idx, "clip_index": 0, "length": 4.0},
            )
            if test_result("Create clip", result):
                passed += 1

                # Test get all clips
                result = send_command(
                    "get_all_clips_in_track", {"track_index": track_idx}
                )
                if test_result("Get all clips in track", result):
                    passed += 1

                    # Set clip name
                    result = send_command(
                        "set_clip_name",
                        {
                            "track_index": track_idx,
                            "clip_index": 0,
                            "name": "Test Clip",
                        },
                    )
                    if test_result("Set clip name", result):
                        passed += 1
                    else:
                        failed += 1
            else:
                failed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Create clip")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # CLIP MANIPULATION TESTS
    # ============================================================================
    print("4. CLIP MANIPULATION")
    print("-" * 60)

    try:
        result = send_command(
            "quantize_clip", {"track_index": track_idx, "clip_index": 0, "amount": 1.0}
        )
        if test_result("Quantize clip", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Quantize clip")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command(
            "transpose_clip",
            {"track_index": track_idx, "clip_index": 0, "semitones": 2},
        )
        if test_result("Transpose clip", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Transpose clip")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command(
            "set_clip_loop",
            {
                "track_index": track_idx,
                "clip_index": 0,
                "loop_start": 0.0,
                "loop_length": 4.0,
            },
        )
        if test_result("Set clip loop", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Set clip loop")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # NOTE MANIPULATION TESTS
    # ============================================================================
    print("5. NOTE MANIPULATION")
    print("-" * 60)

    try:
        result = send_command(
            "add_notes_to_clip",
            {
                "track_index": track_idx,
                "clip_index": 0,
                "notes": [
                    {
                        "pitch": 60,
                        "start_time": 0.0,
                        "duration": 0.25,
                        "velocity": 100,
                        "mute": False,
                    },
                    {
                        "pitch": 64,
                        "start_time": 1.0,
                        "duration": 0.25,
                        "velocity": 90,
                        "mute": False,
                    },
                ],
            },
        )
        if test_result("Add notes to clip", result):
            passed += 1

            # Get notes
            result = send_command(
                "get_clip_notes", {"track_index": track_idx, "clip_index": 0}
            )
            if test_result("Get clip notes", result):
                note_count = result.get("result", {}).get("count", 0)
                print(f"         Clip has {note_count} notes")
                passed += 1

                # Set note velocity
                result = send_command(
                    "set_note_velocity",
                    {
                        "track_index": track_idx,
                        "clip_index": 0,
                        "note_indices": [0, 1],
                        "velocity": 80,
                    },
                )
                if test_result("Set note velocity", result):
                    passed += 1
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Add notes to clip")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # SESSION CONTROL TESTS
    # ============================================================================
    print("6. SESSION CONTROL")
    print("-" * 60)

    try:
        result = send_command("set_time_signature", {"numerator": 4, "denominator": 4})
        if test_result("Set time signature", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Set time signature")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("set_metronome", {"enabled": True})
        if test_result("Set metronome", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Set metronome")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("undo")
        if test_result("Undo", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Undo")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("redo")
        if test_result("Redo", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Redo")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # ARRANGEMENT TESTS
    # ============================================================================
    print("7. ARRANGEMENT CONTROL")
    print("-" * 60)

    try:
        result = send_command("get_playhead_position")
        if test_result("Get playhead position", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Get playhead position")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command(
            "set_loop", {"start_bar": 1, "end_bar": 17, "enabled": True}
        )
        if test_result("Set loop", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Set loop")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("create_locator", {"bar": 1, "name": "Test Locator"})
        if test_result("Create locator", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Create locator")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # DEVICE CONTROL TESTS
    # ============================================================================
    print("8. DEVICE CONTROL")
    print("-" * 60)

    try:
        result = send_command("set_track_pan", {"track_index": track_idx, "pan": 0.0})
        if test_result("Set track pan", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Set track pan")
        print(f"         Exception: {e}")
        failed += 1

    try:
        result = send_command("set_master_volume", {"volume": 0.75})
        if test_result("Set master volume", result):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ FAIL | Set master volume")
        print(f"         Exception: {e}")
        failed += 1

    print()

    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests run: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed / (passed + failed) * 100):.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
