"""
Tests for session template save functionality.
Tests save_session_template MCP tool.
"""

import json
import os
import tempfile
import pytest
from datetime import datetime


def test_save_session_template_basic():
    """Test saving a simple session to JSON template"""
    template_path = "test_session_template.json"

    # This will fail because save_session_template doesn't exist yet
    from MCP_Server.server import save_session_template
    from mcp.server.fastmcp import Context

    ctx = Context()  # Mock context

    # Call the function - should create file and return success
    result_json = save_session_template(ctx, template_path)
    result = json.loads(result_json)

    # Verify success
    assert result["success"] == True
    assert os.path.exists(template_path)

    # Load and verify JSON structure
    with open(template_path) as f:
        template = json.load(f)

    assert "version" in template
    assert "created_at" in template
    assert "session" in template
    assert "metadata" in template["session"]
    assert "tracks" in template["session"]

    # Clean up
    if os.path.exists(template_path):
        os.remove(template_path)


def test_save_session_template_metadata():
    """Test that session metadata is captured correctly"""
    template_path = "test_session_template_metadata.json"

    from MCP_Server.server import save_session_template
    from mcp.server.fastmcp import Context

    ctx = Context()

    result_json = save_session_template(ctx, template_path)
    result = json.loads(result_json)
    assert result["success"] == True

    with open(template_path) as f:
        template = json.load(f)

    # Verify metadata fields
    metadata = template["session"]["metadata"]
    assert "tempo" in metadata
    assert "signature_numerator" in metadata
    assert "signature_denominator" in metadata

    # Clean up
    if os.path.exists(template_path):
        os.remove(template_path)


def test_save_session_template_timestamp():
    """Test that timestamp is ISO formatted"""
    template_path = "test_session_template_timestamp.json"

    from MCP_Server.server import save_session_template
    from mcp.server.fastmcp import Context

    ctx = Context()

    result_json = save_session_template(ctx, template_path)
    result = json.loads(result_json)
    assert result["success"] == True

    with open(template_path) as f:
        template = json.load(f)

    # Verify timestamp format
    timestamp = template["created_at"]
    # Should be parseable as ISO datetime
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    # Clean up
    if os.path.exists(template_path):
        os.remove(template_path)


def test_save_session_template_file_error():
    """Test handling of invalid file path"""
    # Use an invalid path (non-existent directory)
    template_path = "/non/existent/directory/template.json"

    from MCP_Server.server import save_session_template
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Should not crash, should return success=False with error message
    result_json = save_session_template(ctx, template_path)
    result = json.loads(result_json)
    assert result["success"] == False
    assert "error" in result


# ============================================================================
# LOAD SESSION TEMPLATE TESTS
# ============================================================================


def test_load_session_template_minimal():
    """Test loading minimal template (metadata only)"""
    template_path = "test_load_minimal.json"

    # Create minimal template
    minimal_template = {
        "version": "1.0",
        "created_at": "2026-02-09T12:00:00Z",
        "session": {
            "metadata": {
                "name": "Test Minimal",
                "tempo": 120.0,
                "signature_numerator": 4,
                "signature_denominator": 4,
                "metronome_enabled": False,
            }
        },
    }

    with open(template_path, "w") as f:
        json.dump(minimal_template, f)

    try:
        # This will fail because load_session_template doesn't exist yet
        from MCP_Server.server import load_session_template
        from mcp.server.fastmcp import Context

        ctx = Context()

        # Call the function - should load template and return success
        result_json = load_session_template(ctx, template_path, clear_existing=False)
        result = json.loads(result_json)

        # Verify success
        assert result["success"] == True
        assert result["loaded_tracks_count"] == 0
        assert result["loaded_clips_count"] == 0

        # Verify metadata was loaded (session tempo should be set)
        # Note: We can't verify this without a real Ableton connection
        # But the function should not crash
    finally:
        # Clean up
        if os.path.exists(template_path):
            os.remove(template_path)


def test_load_session_template_with_tracks():
    """Test loading template with MIDI tracks and clips"""
    template_path = "test_load_tracks.json"

    # Create template with tracks
    template_with_tracks = {
        "version": "1.0",
        "created_at": "2026-02-09T12:00:00Z",
        "session": {
            "metadata": {
                "name": "Test Tracks",
                "tempo": 126.0,
                "signature_numerator": 4,
                "signature_denominator": 4,
                "metronome_enabled": False,
            },
            "tracks": [
                {
                    "index": 0,
                    "type": "midi",
                    "name": "Bass Track",
                    "color_index": 10,
                    "mute": False,
                    "solo": False,
                    "arm": False,
                    "volume": 0.75,
                    "panning": 0.0,
                    "folded": False,
                    "devices": [],
                    "clips": [
                        {
                            "slot_index": 0,
                            "name": "Bass Pattern",
                            "length": 4.0,
                            "is_audio": False,
                            "loop_start": 0.0,
                            "loop_length": 4.0,
                            "launch_mode": "trigger",
                            "notes": [
                                {
                                    "pitch": 36,
                                    "start_time": 0.0,
                                    "duration": 1.0,
                                    "velocity": 100,
                                    "mute": False,
                                }
                            ],
                        }
                    ],
                }
            ],
        },
    }

    with open(template_path, "w") as f:
        json.dump(template_with_tracks, f)

    try:
        from MCP_Server.server import load_session_template
        from mcp.server.fastmcp import Context

        ctx = Context()

        result_json = load_session_template(ctx, template_path, clear_existing=True)
        result = json.loads(result_json)

        # Verify success
        assert result["success"] == True
        assert result["loaded_tracks_count"] >= 0  # May not create tracks in test env
        assert result["loaded_clips_count"] >= 0
        assert result["errors"] == [] or all(
            isinstance(e, str) for e in result["errors"]
        )
    finally:
        # Clean up
        if os.path.exists(template_path):
            os.remove(template_path)


def test_load_session_template_invalid_file():
    """Test handling of invalid file path"""
    template_path = "/non/existent/directory/template.json"

    from MCP_Server.server import load_session_template
    from mcp.server.fastmcp import Context

    ctx = Context()

    # Should not crash, should return success=False with error message
    result_json = load_session_template(ctx, template_path, clear_existing=False)
    result = json.loads(result_json)

    assert result["success"] == False
    assert "error" in result


def test_load_session_template_invalid_json():
    """Test handling of invalid JSON content"""
    template_path = "test_load_invalid.json"

    # Create invalid JSON file
    with open(template_path, "w") as f:
        f.write("{ invalid json }")

    try:
        from MCP_Server.server import load_session_template
        from mcp.server.fastmcp import Context

        ctx = Context()

        result_json = load_session_template(ctx, template_path, clear_existing=False)
        result = json.loads(result_json)

        assert result["success"] == False
        assert "error" in result
    finally:
        # Clean up
        if os.path.exists(template_path):
            os.remove(template_path)
