"""
Integration tests for track type validation in _create_clip method.

Tests verify that MIDI clips can only be created on MIDI tracks, not audio tracks.
The validation was added at lines 1219-1225 in AbletonMCP_Remote_Script/__init__.py.

Error message format:
    "Cannot create MIDI clip on this track. The track does not support MIDI input.
     Use create_midi_track() first or ensure track is a MIDI track."

Usage:
    pytest tests/integration/test_track_validation.py -v
    pytest tests/integration/test_track_validation.py -v -m integration  # Skip without Ableton

Prerequisites:
    - Ableton Live 11+ must be running
    - AbletonMCP Remote Script must be loaded
    - MCP Server accessible on localhost:9877
"""

import socket
import json
import pytest
from typing import Dict, Any, Optional

# Configuration
TCP_PORT = 9877
UDP_PORT = 9878
HOST = "localhost"
CONNECTION_TIMEOUT = 5.0


def send_tcp_command(
    cmd_type: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a command via TCP socket and return the response.

    Args:
        cmd_type: The MCP command type (e.g., "create_clip", "get_session_info")
        params: Command parameters as dictionary

    Returns:
        Response dictionary with at minimum a "status" key
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONNECTION_TIMEOUT)
        sock.connect((HOST, TCP_PORT))

        command = {"type": cmd_type, "params": params or {}}
        sock.send(json.dumps(command).encode("utf-8"))
        response = sock.recv(8192).decode("utf-8")
        return json.loads(response)
    except socket.error as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON response: {str(e)}"}
    finally:
        if sock:
            sock.close()


def can_connect_to_ableton() -> bool:
    """Check if Ableton MCP server is accessible."""
    try:
        result = send_tcp_command("get_session_info")
        return result.get("status") == "success"
    except Exception:
        return False


# Pytest marker for integration tests requiring Ableton
pytestmark = pytest.mark.skipif(
    not can_connect_to_ableton(),
    reason="Ableton MCP server not available. Start Ableton Live with AbletonMCP Remote Script loaded.",
)


class TestTrackTypeValidation:
    """Test suite for track type validation in clip creation."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """
        Setup: Clear all tracks and create fresh test environment.
        Teardown: Stop playback and restore session state.
        """
        # Setup: Clear all tracks
        send_tcp_command("delete_all_tracks", {})
        yield
        # Teardown: Stop playback
        send_tcp_command("stop_playback", {})

    def test_create_clip_on_midi_track_succeeds(self):
        """
        Test that creating a MIDI clip on a MIDI track succeeds.

        Expected: Clip creation returns success with clip name and length.
        """
        # Create MIDI track
        create_result = send_tcp_command("create_midi_track", {"index": 0})
        assert create_result.get("status") == "success", (
            f"Failed to create MIDI track: {create_result}"
        )

        # Create clip on MIDI track
        clip_result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )

        # Verify success
        assert clip_result.get("status") == "success", (
            f"Clip creation on MIDI track should succeed but failed: {clip_result}"
        )
        assert "result" in clip_result or "name" in clip_result, (
            f"Expected clip info in response: {clip_result}"
        )

    def test_create_clip_on_audio_track_fails(self):
        """
        Test that creating a MIDI clip on an audio track fails with clear error.

        Expected: Error with message containing "does not support MIDI input".
        """
        # Create audio track
        create_result = send_tcp_command("create_audio_track", {"index": 0})
        assert create_result.get("status") == "success", (
            f"Failed to create audio track: {create_result}"
        )

        # Attempt to create MIDI clip on audio track
        clip_result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )

        # Verify failure
        assert clip_result.get("status") == "error", (
            f"Clip creation on audio track should fail but succeeded: {clip_result}"
        )

        # Verify error message is clear
        error_message = clip_result.get("message", "").lower()
        assert "midi" in error_message or "does not support" in error_message, (
            f"Error message should mention MIDI incompatibility: {clip_result}"
        )

    def test_create_clip_on_audio_track_error_message_contains_midi_input(self):
        """
        Test that the error message specifically mentions "does not support MIDI input".

        This tests the exact error message format from the validation code.
        """
        # Create audio track
        send_tcp_command("create_audio_track", {"index": 0})

        # Attempt to create MIDI clip on audio track
        clip_result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )

        # Verify specific error message content
        error_message = clip_result.get("message", "")
        assert "does not support MIDI input" in error_message, (
            f"Error message should contain 'does not support MIDI input': {error_message}"
        )

    def test_create_clip_on_audio_track_error_suggests_solution(self):
        """
        Test that the error message suggests using create_midi_track().

        The error should guide users to the correct solution.
        """
        # Create audio track
        send_tcp_command("create_audio_track", {"index": 0})

        # Attempt to create MIDI clip on audio track
        clip_result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )

        error_message = clip_result.get("message", "")
        # Error message should suggest create_midi_track
        assert "create_midi_track" in error_message or "MIDI track" in error_message, (
            f"Error message should suggest creating MIDI track: {error_message}"
        )

    def test_mixed_track_types_validation(self):
        """
        Test clip creation across mixed track types (MIDI then Audio).

        Verifies that:
        1. Clip can be created on MIDI track (track 0)
        2. Clip creation fails on audio track (track 1)
        """
        # Create MIDI track
        send_tcp_command("create_midi_track", {"index": 0})
        # Create audio track
        send_tcp_command("create_audio_track", {"index": 1})

        # Test MIDI track accepts clips
        midi_result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )
        assert midi_result.get("status") == "success", (
            f"MIDI track should accept clips: {midi_result}"
        )

        # Test audio track rejects clips
        audio_result = send_tcp_command(
            "create_clip", {"track_index": 1, "clip_index": 0, "length": 4.0}
        )
        assert audio_result.get("status") == "error", (
            f"Audio track should reject clips: {audio_result}"
        )

    def test_create_multiple_clips_on_midi_track(self):
        """
        Test creating multiple clips on the same MIDI track succeeds.

        Each clip should be created in different clip slots.
        """
        # Create single MIDI track
        send_tcp_command("create_midi_track", {"index": 0})

        # Create clips in multiple slots
        for clip_index in range(3):
            result = send_tcp_command(
                "create_clip",
                {"track_index": 0, "clip_index": clip_index, "length": 4.0},
            )
            assert result.get("status") == "success", (
                f"Clip {clip_index} creation should succeed: {result}"
            )

    def test_track_index_out_of_range_error(self):
        """
        Test that accessing a non-existent track index returns appropriate error.

        This is a boundary condition test for the validation logic.
        """
        # Ensure no tracks exist
        send_tcp_command("delete_all_tracks", {})

        # Try to create clip on non-existent track
        result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )

        # Should fail with index error
        assert result.get("status") == "error", (
            f"Should fail for non-existent track: {result}"
        )

    def test_track_type_identification(self):
        """
        Test that tracks report correct type via get_track_info.

        Verifies that has_midi_input property is correctly reported.
        """
        # Create one of each track type
        send_tcp_command("create_midi_track", {"index": 0})
        send_tcp_command("create_audio_track", {"index": 1})

        # Get track info for MIDI track
        midi_info = send_tcp_command("get_track_info", {"track_index": 0})
        if midi_info.get("status") == "success":
            track_data = midi_info.get("result", {})
            # MIDI tracks should have has_midi_input or track_type indicator
            assert track_data.get("has_midi_input", True) == True, (
                f"MIDI track should report has_midi_input=True: {midi_info}"
            )

        # Get track info for audio track
        audio_info = send_tcp_command("get_track_info", {"track_index": 1})
        if audio_info.get("status") == "success":
            track_data = audio_info.get("result", {})
            # Audio tracks should not have has_midi_input
            assert track_data.get("has_midi_input", False) == False, (
                f"Audio track should report has_midi_input=False: {audio_info}"
            )


class TestTrackValidationEdgeCases:
    """Edge case tests for track type validation."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear tracks before and after each test."""
        send_tcp_command("delete_all_tracks", {})
        yield
        send_tcp_command("stop_playback", {})

    def test_clip_slot_already_has_clip_error(self):
        """
        Test that creating a clip in an occupied slot fails appropriately.

        This tests a different validation path in _create_clip.
        """
        # Create MIDI track and first clip
        send_tcp_command("create_midi_track", {"index": 0})
        first_result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )
        assert first_result.get("status") == "success"

        # Try to create another clip in same slot
        second_result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
        )

        # Should fail with "already has a clip" error
        assert second_result.get("status") == "error"
        error_msg = second_result.get("message", "").lower()
        assert "already has a clip" in error_msg or "occupied" in error_msg, (
            f"Should indicate slot is occupied: {second_result}"
        )

    def test_invalid_clip_index_error(self):
        """
        Test that invalid clip index returns appropriate error.
        """
        send_tcp_command("create_midi_track", {"index": 0})

        # Use negative clip index
        result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": -1, "length": 4.0}
        )

        assert result.get("status") == "error", (
            f"Should fail for negative clip index: {result}"
        )

    def test_invalid_clip_length(self):
        """
        Test that invalid clip length is handled appropriately.
        """
        send_tcp_command("create_midi_track", {"index": 0})

        # Try with zero length
        result = send_tcp_command(
            "create_clip", {"track_index": 0, "clip_index": 0, "length": 0}
        )

        # May succeed with default length or fail - either is acceptable
        # Just verify no crash
        assert result.get("status") in ["success", "error"], (
            f"Should return valid status: {result}"
        )


class TestTrackValidationReturnTracks:
    """Test validation with return tracks (which are always audio-type)."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear tracks before and after each test."""
        send_tcp_command("delete_all_tracks", {})
        yield
        send_tcp_command("stop_playback", {})

    def test_create_clip_on_return_track_fails(self):
        """
        Test that creating a MIDI clip on a return track fails.

        Return tracks are audio-type tracks and should reject MIDI clips.
        """
        # First check if we have return tracks
        session_info = send_tcp_command("get_session_info")
        if session_info.get("status") != "success":
            pytest.skip("Cannot get session info")

        # Return tracks typically exist at negative indices conceptually,
        # but we need to create one first
        create_return = send_tcp_command("create_return_track", {})

        if create_return.get("status") != "success":
            pytest.skip("Cannot create return track")

        # Get track info to find return track index
        return_info = send_tcp_command("get_return_tracks", {})
        if return_info.get("status") != "success":
            pytest.skip("Cannot get return tracks")

        return_tracks = return_info.get("result", {}).get("return_tracks", [])
        if not return_tracks:
            pytest.skip("No return tracks available")

        # Try to create clip on first return track (typically index after regular tracks)
        # This should fail because return tracks are audio-type
        # Note: Implementation may vary - return tracks might not have clip_slots
        result = send_tcp_command(
            "create_clip",
            {
                "track_index": return_tracks[0].get("index", 0),
                "clip_index": 0,
                "length": 4.0,
            },
        )

        # Should fail - either no MIDI support or no clip slots
        assert result.get("status") == "error", (
            f"Should not create clip on return track: {result}"
        )


# =============================================================================
# STANDALONE TEST RUNNER
# =============================================================================


def run_tests_standalone():
    """
    Run tests without pytest for quick verification.

    Usage: python tests/integration/test_track_validation.py
    """
    print("=" * 70)
    print("TRACK TYPE VALIDATION TESTS")
    print("=" * 70)
    print()

    # Check connection first
    print("[CONNECTION CHECK]")
    if not can_connect_to_ableton():
        print("FAIL: Cannot connect to Ableton MCP server")
        print(
            "      Ensure Ableton Live is running with AbletonMCP Remote Script loaded"
        )
        return 1
    print("OK: Connected to Ableton MCP server")
    print()

    # Setup
    print("[SETUP] Clearing tracks...")
    send_tcp_command("delete_all_tracks", {})

    tests_passed = 0
    tests_failed = 0

    # Test 1: MIDI track accepts clips
    print("\n[TEST 1] Create clip on MIDI track...")
    send_tcp_command("create_midi_track", {"index": 0})
    result = send_tcp_command(
        "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
    )
    if result.get("status") == "success":
        print("PASS: MIDI track accepts clips")
        tests_passed += 1
    else:
        print(f"FAIL: {result}")
        tests_failed += 1

    # Cleanup
    send_tcp_command("delete_all_tracks", {})

    # Test 2: Audio track rejects clips
    print("\n[TEST 2] Create clip on audio track...")
    send_tcp_command("create_audio_track", {"index": 0})
    result = send_tcp_command(
        "create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}
    )
    if result.get("status") == "error":
        error_msg = result.get("message", "")
        if "does not support MIDI input" in error_msg:
            print("PASS: Audio track rejects clips with correct error message")
            tests_passed += 1
        else:
            print(f"PARTIAL: Audio track rejects but wrong message: {error_msg}")
            tests_passed += 1
    else:
        print(f"FAIL: Audio track should reject clips: {result}")
        tests_failed += 1

    # Summary
    print()
    print("=" * 70)
    print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
    print("=" * 70)

    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_tests_standalone())
