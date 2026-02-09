"""
Tests for preset bank management functionality.
Tests save_preset_bank, load_preset_bank, and list_preset_banks MCP tools.
"""

import json
import os
import tempfile
import pytest
from datetime import datetime


# ============================================================================
# LIST PRESET BANKS TESTS
# ============================================================================


def test_list_preset_banks_empty():
    """Test listing when no preset banks exist"""
    from MCP_Server.server import list_preset_banks
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Call the function - should return empty list
    result_json = list_preset_banks(ctx)
    result = json.loads(result_json)

    # Verify success
    assert result["success"] == True
    assert "banks" in result
    assert isinstance(result["banks"], list)


# ============================================================================
# SAVE PRESET BANK TESTS
# ============================================================================


def test_save_preset_bank_single_device():
    """Test saving a single device preset to bank"""
    bank_name = "test_single_device_bank"

    # This will fail because save_preset_bank doesn't exist yet
    from MCP_Server.server import save_preset_bank
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Call the function - should create bank with one device preset
    result_json = save_preset_bank(
        ctx, track_index=0, device_index=0, bank_name=bank_name
    )
    result = json.loads(result_json)

    # Verify success
    assert result["success"] == True
    assert "message" in result

    # Clean up
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")
    if os.path.exists(bank_path):
        os.remove(bank_path)


def test_save_preset_bank_multiple_devices():
    """Test saving multiple device presets to same bank"""
    bank_name = "test_multiple_device_bank"

    from MCP_Server.server import save_preset_bank
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Save first device
    result_json1 = save_preset_bank(
        ctx, track_index=0, device_index=0, bank_name=bank_name
    )
    result1 = json.loads(result_json1)
    assert result1["success"] == True

    # Save second device to same bank
    result_json2 = save_preset_bank(
        ctx, track_index=1, device_index=0, bank_name=bank_name
    )
    result2 = json.loads(result_json2)
    assert result2["success"] == True

    # Verify bank file exists
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")
    assert os.path.exists(bank_path)

    # Verify bank contains both presets
    with open(bank_path) as f:
        bank = json.load(f)

    assert bank["version"] == "1.0"
    assert "created_at" in bank
    assert "presets" in bank
    assert len(bank["presets"]) == 2

    # Clean up
    if os.path.exists(bank_path):
        os.remove(bank_path)


def test_save_preset_bank_json_structure():
    """Test that preset bank JSON has correct structure"""
    bank_name = "test_structure_bank"

    from MCP_Server.server import save_preset_bank
    from mcp.server.fastmcp import Context

    ctx = Context()

    result_json = save_preset_bank(
        ctx, track_index=0, device_index=0, bank_name=bank_name
    )
    result = json.loads(result_json)
    assert result["success"] == True

    # Load and verify JSON structure
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    with open(bank_path) as f:
        bank = json.load(f)

    # Verify top-level fields
    assert "version" in bank
    assert "created_at" in bank
    assert "presets" in bank

    # Verify version and timestamp format
    assert bank["version"] == "1.0"
    datetime.fromisoformat(bank["created_at"].replace("Z", "+00:00"))

    # Verify preset structure
    assert len(bank["presets"]) == 1
    preset = bank["presets"][0]

    assert "device_class" in preset
    assert "device_name" in preset
    assert "track_index" in preset
    assert "device_index" in preset
    assert "preset_name" in preset
    assert "parameters" in preset

    # Clean up
    if os.path.exists(bank_path):
        os.remove(bank_path)


# ============================================================================
# LOAD PRESET BANK TESTS
# ============================================================================


def test_load_preset_bank_single_preset():
    """Test loading a single preset from bank"""
    bank_name = "test_load_single_bank"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    # Create test bank
    test_bank = {
        "version": "1.0",
        "created_at": "2026-02-09T12:00:00Z",
        "presets": [
            {
                "device_class": "Operator",
                "device_name": "Bass Lead",
                "track_index": 0,
                "device_index": 0,
                "preset_name": "Deep Sub Bass",
                "parameters": [
                    {"index": 0, "name": "Volume", "value": 0.75, "normalized": 0.75},
                ],
            }
        ],
    }

    os.makedirs(preset_bank_dir, exist_ok=True)
    with open(bank_path, "w") as f:
        json.dump(test_bank, f)

    try:
        from MCP_Server.server import load_preset_bank
        from mcp.server.fastmcp import Context

        ctx = Context()

        # This will fail because load_preset_bank doesn't exist yet
        result_json = load_preset_bank(
            ctx, bank_name=bank_name, track_index=0, device_index=0
        )
        result = json.loads(result_json)

        # Verify success
        assert result["success"] == True
        assert "loaded_presets_count" in result
        assert result["loaded_presets_count"] >= 0
    finally:
        # Clean up
        if os.path.exists(bank_path):
            os.remove(bank_path)


def test_load_preset_bank_entire_bank():
    """Test loading entire bank (all presets)"""
    bank_name = "test_load_full_bank"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    # Create test bank with multiple presets
    test_bank = {
        "version": "1.0",
        "created_at": "2026-02-09T12:00:00Z",
        "presets": [
            {
                "device_class": "Operator",
                "device_name": "Bass Lead",
                "track_index": 0,
                "device_index": 0,
                "preset_name": "Deep Sub Bass",
                "parameters": [],
            },
            {
                "device_class": "Wavetable",
                "device_name": "Pad Synth",
                "track_index": 2,
                "device_index": 0,
                "preset_name": "Atmospheric Pad",
                "parameters": [],
            },
        ],
    }

    os.makedirs(preset_bank_dir, exist_ok=True)
    with open(bank_path, "w") as f:
        json.dump(test_bank, f)

    try:
        from MCP_Server.server import load_preset_bank
        from mcp.server.fastmcp import Context

        ctx = Context()

        # Load entire bank (no specific track/device)
        result_json = load_preset_bank(ctx, bank_name=bank_name)
        result = json.loads(result_json)

        # Verify success
        assert result["success"] == True
        assert "loaded_presets_count" in result
        assert result["loaded_presets_count"] >= 0
        assert "errors" in result
    finally:
        # Clean up
        if os.path.exists(bank_path):
            os.remove(bank_path)


def test_load_preset_bank_missing_device_fallback():
    """Test loading preset when device is missing - should use parameters fallback"""
    bank_name = "test_fallback_bank"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    # Create test bank with parameters only (no preset_name)
    test_bank = {
        "version": "1.0",
        "created_at": "2026-02-09T12:00:00Z",
        "presets": [
            {
                "device_class": "Operator",
                "device_name": "Custom Bass",
                "track_index": 0,
                "device_index": 0,
                "preset_name": None,
                "parameters": [
                    {"index": 0, "name": "Volume", "value": 0.8, "normalized": 0.8},
                    {"index": 1, "name": "Pitch", "value": 0.5, "normalized": 0.5},
                ],
            }
        ],
    }

    os.makedirs(preset_bank_dir, exist_ok=True)
    with open(bank_path, "w") as f:
        json.dump(test_bank, f)

    try:
        from MCP_Server.server import load_preset_bank
        from mcp.server.fastmcp import Context

        ctx = Context()

        result_json = load_preset_bank(
            ctx, bank_name=bank_name, track_index=0, device_index=0
        )
        result = json.loads(result_json)

        # Should succeed with parameter fallback
        assert result["success"] == True
    finally:
        # Clean up
        if os.path.exists(bank_path):
            os.remove(bank_path)


def test_load_preset_bank_nonexistent():
    """Test handling of non-existent preset bank file"""
    bank_name = "nonexistent_bank"

    from MCP_Server.server import load_preset_bank
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Should not crash, should return success=False with error message
    result_json = load_preset_bank(ctx, bank_name=bank_name)
    result = json.loads(result_json)

    assert result["success"] == False
    assert "error" in result


def test_load_preset_bank_invalid_json():
    """Test handling of invalid JSON in preset bank"""
    bank_name = "invalid_json_bank"
    preset_bank_dir = os.path.expanduser("~/.ableton_mcp/preset_banks/")
    bank_path = os.path.join(preset_bank_dir, f"{bank_name}.json")

    # Create invalid JSON file
    os.makedirs(preset_bank_dir, exist_ok=True)
    with open(bank_path, "w") as f:
        f.write("{ invalid json }")

    try:
        from MCP_Server.server import load_preset_bank
        from mcp.server.fastmcp import Context

        ctx = Context()

        result_json = load_preset_bank(ctx, bank_name=bank_name)
        result = json.loads(result_json)

        assert result["success"] == False
        assert "error" in result
    finally:
        # Clean up
        if os.path.exists(bank_path):
            os.remove(bank_path)
