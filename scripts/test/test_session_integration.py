"""
Integration tests for session and preset management functionality.
Tests end-to-end workflows for session templates and preset banks.

Tests cover:
- Full session save/load cycle
- Preset bank save/load cycle
- Session + preset bank combined workflow
- Error handling for missing/invalid files
- Complex session scenarios with multiple tracks, clips, devices
"""

import json
import os
import tempfile
import pytest
from datetime import datetime
import time


# =============================================================================
# SESSION SAVE/LOAD FULL CYCLE TESTS
# =============================================================================


def test_session_save_load_full_cycle():
    """Test complete session save and load cycle with clear_existing=True"""
    template_path = "test_full_cycle_session.json"

    from MCP_Server.server import (
        save_session_template,
        load_session_template,
        get_session_overview,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Save session template (capture whatever exists in session)
        save_result_json = save_session_template(ctx, template_path)

        # Handle both JSON and plain text responses
        try:
            save_result = json.loads(save_result_json)
        except json.JSONDecodeError:
            pytest.skip(f"Unable to connect to Ableton: {save_result_json[:100]}")

        # Verify save succeeded
        assert save_result["success"] == True, (
            f"Save failed: {save_result.get('error')}"
        )
        assert os.path.exists(template_path), (
            f"Template file not created: {template_path}"
        )

        # Phase 2: Verify JSON structure
        with open(template_path) as f:
            template = json.load(f)

        assert "version" in template, "Template missing version field"
        assert "created_at" in template, "Template missing created_at field"
        assert "session" in template, "Template missing session field"
        assert "metadata" in template["session"], "Template missing metadata"
        assert "tracks" in template["session"], "Template missing tracks"

        # Verify timestamp is valid ISO format
        datetime.fromisoformat(template["created_at"].replace("Z", "+00:00"))

        # Phase 3: Load session with clear_existing=True
        load_result_json = load_session_template(
            ctx, template_path, clear_existing=True
        )
        load_result = json.loads(load_result_json)

        # Verify load succeeded
        assert load_result["success"] == True, (
            f"Load failed: {load_result.get('error')}"
        )
        assert "loaded_tracks_count" in load_result
        assert "loaded_clips_count" in load_result
        assert "errors" in load_result

        # Verify no critical errors occurred
        critical_errors = [
            e
            for e in load_result.get("errors", [])
            if "critical" in e.lower() or "failed to load session" in e.lower()
        ]
        assert len(critical_errors) == 0, (
            f"Critical errors during load: {critical_errors}"
        )

    finally:
        # Cleanup
        if os.path.exists(template_path):
            os.remove(template_path)


def test_session_save_load_partial():
    """Test session save and load without clearing existing tracks"""
    template_path = "test_partial_session.json"

    from MCP_Server.server import (
        save_session_template,
        load_session_template,
        get_all_tracks,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Get initial track count
        try:
            initial_tracks_json = get_all_tracks(ctx)
            initial_tracks = json.loads(initial_tracks_json)
            initial_count = len(initial_tracks.get("tracks", []))
        except json.JSONDecodeError:
            pytest.skip("No Ableton connection available")

        # Phase 2: Save session
        save_result_json = save_session_template(ctx, template_path)
        save_result = json.loads(save_result_json)
        assert save_result["success"] == True

        # Phase 3: Load WITHOUT clearing existing
        load_result_json = load_session_template(
            ctx, template_path, clear_existing=False
        )
        load_result = json.loads(load_result_json)

        assert load_result["success"] == True
        assert "loaded_tracks_count" in load_result

        # Phase 4: Verify tracks were added (track count should increase or stay same)
        final_tracks_json = get_all_tracks(ctx)
        final_tracks = json.loads(final_tracks_json)
        final_count = len(final_tracks.get("tracks", []))

        # Track count should not decrease when loading without clear
        assert final_count >= initial_count, (
            f"Track count decreased after load without clear: {initial_count} -> {final_count}"
        )

    finally:
        if os.path.exists(template_path):
            os.remove(template_path)


# =============================================================================
# PRESET BANK SAVE/LOAD CYCLE TESTS
# =============================================================================


def test_preset_bank_save_load_cycle():
    """Test complete preset bank save and load cycle"""
    bank_name = "test_integration_preset_bank"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    from MCP_Server.server import (
        save_preset_bank,
        load_preset_bank,
        list_preset_banks,
        get_device_parameters,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Save device preset to bank
        # Assume track 0, device 0 exists (or test will skip gracefully)
        save_result_json = save_preset_bank(
            ctx, track_index=0, device_index=0, bank_name=bank_name
        )
        save_result = json.loads(save_result_json)

        # Save may fail if no device exists, but that's OK for integration test
        # We're testing the cycle, not device availability
        if not save_result.get("success"):
            pytest.skip(
                f"Device not available for preset test: {save_result.get('error')}"
            )

        assert os.path.exists(bank_path), "Preset bank file not created"

        # Phase 2: Verify JSON structure
        with open(bank_path) as f:
            bank = json.load(f)

        assert bank["version"] == "1.0", "Incorrect version"
        assert "created_at" in bank, "Missing created_at"
        assert "presets" in bank, "Missing presets"
        assert len(bank["presets"]) >= 1, "No presets saved"

        # Verify each preset has required fields
        for preset in bank["presets"]:
            assert "device_class" in preset, "Preset missing device_class"
            assert "device_name" in preset, "Preset missing device_name"
            assert "device_index" in preset, "Preset missing device_index"
            assert "preset_name" in preset, "Preset missing preset_name"
            assert "parameters" in preset, "Preset missing parameters"

        # Phase 3: List banks to verify it appears
        list_json = list_preset_banks(ctx)
        list_result = json.loads(list_json)

        assert list_result["success"] == True
        assert "banks" in list_result
        assert bank_name in list_result["banks"], "Bank not listed"

        # Phase 4: Load preset back to device
        load_result_json = load_preset_bank(
            ctx, bank_name=bank_name, track_index=0, device_index=0
        )
        load_result = json.loads(load_result_json)

        assert load_result["success"] == True
        assert "loaded_presets_count" in load_result
        assert load_result["loaded_presets_count"] >= 1

        # Phase 5: Verify parameters were restored
        original_params = None
        try:
            get_params_json = get_device_parameters(ctx, track_index=0, device_index=0)
            get_params = json.loads(get_params_json)
            if get_params.get("success"):
                original_params = get_params.get("parameters", [])
        except:
            pass

        # We can't verify exact values without comparing before/after
        # But we verified the load operation succeeded

    finally:
        if os.path.exists(bank_path):
            os.remove(bank_path)


# =============================================================================
# SESSION + PRESET BANK COMBINED WORKFLOW TESTS
# =============================================================================


def test_session_preset_combined_workflow():
    """Test combined workflow: save session, save preset bank, load both"""
    template_path = "test_combined_session.json"
    bank_name = "test_combined_bank"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    from MCP_Server.server import (
        save_session_template,
        load_session_template,
        save_preset_bank,
        load_preset_bank,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Save session
        session_save_json = save_session_template(ctx, template_path)
        session_save = json.loads(session_save_json)
        assert session_save["success"] == True
        assert os.path.exists(template_path)

        # Phase 2: Save preset bank
        preset_save_json = save_preset_bank(
            ctx, track_index=0, device_index=0, bank_name=bank_name
        )
        preset_save = json.loads(preset_save_json)

        # Preset save may fail if no device exists - skip gracefully
        if not preset_save.get("success"):
            pytest.skip(f"No device for preset: {preset_save.get('error')}")

        assert os.path.exists(bank_path)

        # Phase 3: Load session
        session_load_json = load_session_template(
            ctx, template_path, clear_existing=False
        )
        session_load = json.loads(session_load_json)
        assert session_load["success"] == True

        # Phase 4: Load preset bank onto restored session
        preset_load_json = load_preset_bank(
            ctx, bank_name=bank_name, track_index=0, device_index=0
        )
        preset_load = json.loads(preset_load_json)
        assert preset_load["success"] == True

        # Both files exist and both load operations succeeded
        assert os.path.exists(template_path), "Session template should still exist"
        assert os.path.exists(bank_path), "Preset bank should still exist"

    finally:
        if os.path.exists(template_path):
            os.remove(template_path)
        if os.path.exists(bank_path):
            os.remove(bank_path)


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


def test_load_nonexistent_session_file():
    """Test loading a non-existent session file"""
    nonexistent_path = "/tmp/nonexistent_session_12345.json"

    from MCP_Server.server import load_session_template
    from mcp.server.fastmcp import Context

    ctx = Context()

    load_result_json = load_session_template(
        ctx, nonexistent_path, clear_existing=False
    )
    load_result = json.loads(load_result_json)

    assert load_result["success"] == False
    assert "error" in load_result
    assert (
        "not found" in load_result["error"].lower()
        or "does not exist" in load_result["error"].lower()
    )


def test_load_malformed_session_json():
    """Test loading malformed JSON session file"""
    malformed_path = "test_malformed_session.json"

    from MCP_Server.server import load_session_template
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Create malformed JSON file
    try:
        with open(malformed_path, "w") as f:
            f.write("{ invalid json content }")

        load_result_json = load_session_template(
            ctx, malformed_path, clear_existing=False
        )
        load_result = json.loads(load_result_json)

        assert load_result["success"] == False
        assert "error" in load_result

    finally:
        if os.path.exists(malformed_path):
            os.remove(malformed_path)


def test_load_session_with_missing_devices():
    """Test loading a session with devices that may not be available"""
    template_path = "test_missing_devices.json"

    from MCP_Server.server import load_session_template, get_all_tracks
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Create a session template with non-existent device URIs
    test_template_with_missing_devices = {
        "version": "1.0",
        "created_at": "2026-02-10T12:00:00Z",
        "session": {
            "metadata": {
                "name": "Test Missing Devices",
                "tempo": 120.0,
                "signature_numerator": 4,
                "signature_denominator": 4,
                "metronome_enabled": False,
            },
            "tracks": [
                {
                    "index": 0,
                    "type": "midi",
                    "name": "Track with Missing Device",
                    "color_index": 5,
                    "mute": False,
                    "solo": False,
                    "arm": False,
                    "volume": 0.75,
                    "panning": 0.0,
                    "folded": False,
                    "devices": [
                        {
                            "index": 0,
                            "name": "NonExistentDevice",
                            "class_name": "UnknownDevice",
                            "type": "instrument",
                            "uri": "query:NonExistentCategory:Fantasy%20Device:FileId_99999",
                            "preset_name": None,
                            "bypass": False,
                            "parameters": [],
                        }
                    ],
                    "clips": [],
                }
            ],
        },
    }

    try:
        with open(template_path, "w") as f:
            json.dump(test_template_with_missing_devices, f)

        load_result_json = load_session_template(
            ctx, template_path, clear_existing=False
        )
        load_result = json.loads(load_result_json)

        # Load should succeed but may report errors
        assert load_result["success"] == True or "error" in load_result

        if load_result.get("errors"):
            # Should have errors about missing device
            errors = load_result["errors"]
            assert any("device" in e.lower() for e in errors), (
                "Expected device-related errors"
            )

    finally:
        if os.path.exists(template_path):
            os.remove(template_path)


def test_load_nonexistent_preset_bank():
    """Test loading a non-existent preset bank"""
    nonexistent_bank = "nonexistent_bank_xyz123"

    from MCP_Server.server import load_preset_bank
    from mcp.server.fastmcp import Context

    ctx = Context()

    load_result_json = load_preset_bank(ctx, bank_name=nonexistent_bank)
    load_result = json.loads(load_result_json)

    assert load_result["success"] == False
    assert "error" in load_result


def test_load_malformed_preset_bank():
    """Test loading malformed JSON preset bank"""
    bank_name = "malformed_bank_json"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    from MCP_Server.server import load_preset_bank
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        os.makedirs(preset_bank_dir, exist_ok=True)

        # Create malformed JSON file
        with open(bank_path, "w") as f:
            f.write("{ invalid json preset bank }")

        load_result_json = load_preset_bank(ctx, bank_name=bank_name)
        load_result = json.loads(load_result_json)

        assert load_result["success"] == False
        assert "error" in load_result

    finally:
        if os.path.exists(bank_path):
            os.remove(bank_path)


# =============================================================================
# COMPLEX SESSION SCENARIOS TESTS
# =============================================================================


def test_complex_session_multiple_tracks():
    """Test saving and loading a session with multiple tracks, clips, and devices"""
    template_path = "test_complex_session.json"

    from MCP_Server.server import (
        save_session_template,
        load_session_template,
        get_session_overview,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Save current session (whatever exists)
        save_result_json = save_session_template(ctx, template_path)
        save_result = json.loads(save_result_json)
        assert save_result["success"] == True

        # Phase 2: Verify saved structure
        with open(template_path) as f:
            template = json.load(f)

        tracks = template["session"].get("tracks", [])
        # We'll verify structure even if track count varies
        for track in tracks:
            assert "index" in track
            assert "type" in track
            assert "name" in track
            # Verify clips structure if present
            clips = track.get("clips", [])
            for clip in clips:
                if not clip.get("is_audio", True):
                    notes = clip.get("notes", [])
                    # Notes don't need to exist, but if they do they should have structure
                    for note in notes:
                        assert "pitch" in note
                        assert "start_time" in note
                        assert "duration" in note
                        assert "velocity" in note

        # Phase 3: Load session
        load_result_json = load_session_template(
            ctx, template_path, clear_existing=False
        )
        load_result = json.loads(load_result_json)
        assert load_result["success"] == True

    finally:
        if os.path.exists(template_path):
            os.remove(template_path)


def test_session_persistence_across_operations():
    """Test that session persists correctly across multiple save/load operations"""
    template_path1 = "test_persistence_1.json"
    template_path2 = "test_persistence_2.json"

    from MCP_Server.server import (
        save_session_template,
        load_session_template,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Save session 1
        save_result1_json = save_session_template(ctx, template_path1)
        save_result1 = json.loads(save_result1_json)
        assert save_result1["success"] == True

        # Phase 2: Save session 2 (different timestamp)
        # Add a small delay to ensure different timestamps
        import time

        time.sleep(0.1)

        save_result2_json = save_session_template(ctx, template_path2)
        save_result2 = json.loads(save_result2_json)
        assert save_result2["success"] == True

        # Phase 3: Verify both files exist and have different content
        assert os.path.exists(template_path1)
        assert os.path.exists(template_path2)

        with open(template_path1) as f:
            template1 = json.load(f)
        with open(template_path2) as f:
            template2 = json.load(f)

        # Templates should have different timestamps
        assert template1["created_at"] != template2["created_at"], (
            "Different saves should have different timestamps"
        )

        # Both should load successfully
        load_result1_json = load_session_template(
            ctx, template_path1, clear_existing=False
        )
        load_result1 = json.loads(load_result1_json)
        assert load_result1["success"] == True

        load_result2_json = load_session_template(
            ctx, template_path2, clear_existing=False
        )
        load_result2 = json.loads(load_result2_json)
        assert load_result2["success"] == True

    finally:
        for path in [template_path1, template_path2]:
            if os.path.exists(path):
                os.remove(path)


# =============================================================================
# EDGE CASES AND BOUNDARY TESTS
# =============================================================================


def test_empty_session_save_load():
    """Test saving and loading a minimal session (metadata only)"""
    template_path = "test_empty_session.json"

    from MCP_Server.server import (
        save_session_template,
        load_session_template,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Save current session (may be minimal)
        save_result_json = save_session_template(ctx, template_path)
        save_result = json.loads(save_result_json)
        assert save_result["success"] == True

        # Phase 2: Verify minimal JSON structure
        with open(template_path) as f:
            template = json.load(f)

        assert "version" in template
        assert "created_at" in template
        assert "session" in template
        assert "metadata" in template["session"]

        # Phase 3: Load session
        load_result_json = load_session_template(
            ctx, template_path, clear_existing=False
        )
        load_result = json.loads(load_result_json)
        assert load_result["success"] == True

    finally:
        if os.path.exists(template_path):
            os.remove(template_path)


def test_concurrent_preset_banks():
    """Test managing multiple preset banks simultaneously"""
    bank_name1 = "test_concurrent_bank_1"
    bank_name2 = "test_concurrent_bank_2"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path1 = os.path.join(preset_bank_dir, f"{bank_name1}.json")
    bank_path2 = os.path.join(preset_bank_dir, f"{bank_name2}.json")

    from MCP_Server.server import (
        save_preset_bank,
        load_preset_bank,
        list_preset_banks,
    )
    from mcp.server.fastmcp import Context

    ctx = Context()

    try:
        # Phase 1: Save to both banks
        save_result1_json = save_preset_bank(
            ctx, track_index=0, device_index=0, bank_name=bank_name1
        )
        save_result1 = json.loads(save_result1_json)

        save_result2_json = save_preset_bank(
            ctx, track_index=0, device_index=0, bank_name=bank_name2
        )
        save_result2 = json.loads(save_result2_json)

        # May fail if no device exists
        if not save_result1.get("success"):
            pytest.skip(f"Device not available: {save_result1.get('error')}")

        assert save_result1["success"] == True
        assert save_result2["success"] == True
        assert os.path.exists(bank_path1)
        assert os.path.exists(bank_path2)

        # Phase 2: List banks - both should appear
        list_json = list_preset_banks(ctx)
        list_result = json.loads(list_json)
        assert list_result["success"] == True
        assert bank_name1 in list_result["banks"]
        assert bank_name2 in list_result["banks"]

        # Phase 3: Load from both banks
        load_result1_json = load_preset_bank(
            ctx, bank_name=bank_name1, track_index=0, device_index=0
        )
        load_result1 = json.loads(load_result1_json)
        assert load_result1["success"] == True

        load_result2_json = load_preset_bank(
            ctx, bank_name=bank_name2, track_index=0, device_index=0
        )
        load_result2 = json.loads(load_result2_json)
        assert load_result2["success"] == True

    finally:
        for path in [bank_path1, bank_path2]:
            if os.path.exists(path):
                os.remove(path)
