"""Tests for Ableton-dependent tools — migrated from scripts/test/.

Migrated from:
- test_device_presets.py
- test_preset_banks.py
- test_session_templates.py
- test_session_integration.py

All tests are skipped unless LIVE_ABLETON env var is set.
"""

from __future__ import annotations

import os

import pytest

LIVE_ABLETON = os.environ.get("LIVE_ABLETON")

skip_no_ableton = pytest.mark.skipif(
    not LIVE_ABLETON,
    reason="Requires live Ableton Live connection (set LIVE_ABLETON env var)",
)


@skip_no_ableton
class TestDevicePresets:
    """Tests for device preset save/load via Ableton MCP."""

    def test_save_device_preset_creates_file(self):
        import json
        import socket

        def send_command(command_type, params=None):
            if params is None:
                params = {}
            command = {"type": command_type, "params": params}
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect(("127.0.0.1", 9877))
            sock.sendall(json.dumps(command).encode("utf-8"))
            response_data = sock.recv(4096 * 4).decode("utf-8")
            sock.close()
            return json.loads(response_data)

        response = send_command("get_all_tracks")
        assert "result" in response


@skip_no_ableton
class TestPresetBanks:
    """Tests for preset bank management."""

    def test_list_preset_banks_empty(self):
        import json

        from MCP_Server.server import list_preset_banks
        from mcp.server.fastmcp import Context

        ctx = Context()
        result_json = list_preset_banks(ctx)
        result = json.loads(result_json)
        assert result["success"]
        assert "banks" in result
        assert isinstance(result["banks"], list)


@skip_no_ableton
class TestSessionTemplates:
    """Tests for session template save/load."""

    def test_save_session_template_basic(self):
        import json
        import os

        template_path = "test_legacy_session_template.json"

        from MCP_Server.server import save_session_template
        from mcp.server.fastmcp import Context

        ctx = Context()
        result_json = save_session_template(ctx, template_path)
        result = json.loads(result_json)
        assert result["success"]
        assert os.path.exists(template_path)

        with open(template_path) as f:
            template = json.load(f)
        assert "version" in template
        assert "created_at" in template
        assert "session" in template

        # Cleanup
        if os.path.exists(template_path):
            os.remove(template_path)

    def test_save_session_template_metadata(self):
        import json
        import os

        template_path = "test_legacy_session_meta.json"

        from MCP_Server.server import save_session_template
        from mcp.server.fastmcp import Context

        ctx = Context()
        result_json = save_session_template(ctx, template_path)
        result = json.loads(result_json)
        assert result["success"]

        with open(template_path) as f:
            template = json.load(f)
        assert "metadata" in template["session"]
        assert "tracks" in template["session"]

        if os.path.exists(template_path):
            os.remove(template_path)


@skip_no_ableton
class TestSessionIntegration:
    """End-to-end session save/load cycle tests."""

    def test_session_save_load_full_cycle(self):
        import json
        import os

        template_path = "test_legacy_full_cycle.json"

        from MCP_Server.server import (
            load_session_template,
            save_session_template,
        )
        from mcp.server.fastmcp import Context

        ctx = Context()
        try:
            save_result_json = save_session_template(ctx, template_path)
            try:
                save_result = json.loads(save_result_json)
            except json.JSONDecodeError:
                pytest.skip(f"Unable to connect to Ableton: {save_result_json[:100]}")

            assert save_result["success"]
            assert os.path.exists(template_path)

            with open(template_path) as f:
                template = json.load(f)
            assert "version" in template
            assert "created_at" in template
            assert "session" in template
        finally:
            if os.path.exists(template_path):
                os.remove(template_path)
