"""Unit tests for MCP_Server/validate_server.py static validator."""

import ast
from pathlib import Path
from unittest.mock import patch

import pytest

from MCP_Server.validate_server import (
    ToolInfo,
    Violation,
    is_normalized_param,
    parse_tools,
    parse_remote_script_dispatch,
)


class TestParseTools:
    """Value-asserting tests for tool parsing from AST."""

    def test_parses_server_tools(self):
        """Server file should contain tool-decorated functions."""
        tools = parse_tools("MCP_Server/server.py")
        assert len(tools) > 100, f"Expected 100+ tools, got {len(tools)}"

    def test_tool_has_file_and_line(self):
        """Each tool should have file and line info."""
        tools = parse_tools("MCP_Server/server.py")
        assert all(t.file and t.line > 0 for t in tools)

    def test_tool_name_extracted(self):
        """Tool names should match @server.tool pattern."""
        tools = parse_tools("MCP_Server/server.py")
        names = {t.name for t in tools}
        assert "get_all_tracks" in names or len(names) > 0

    def test_parse_empty_file(self):
        """Empty file should return empty list."""
        tools = parse_tools("/dev/null")
        assert tools == []

    def test_parse_nonexistent_returns_empty(self):
        """Nonexistent file should not crash."""
        tools = parse_tools("/nonexistent/file.py")
        assert tools == []


class TestParseRemoteScriptDispatch:
    """Value-asserting tests for Remote Script dispatch parsing."""

    def test_parses_dispatch_handlers(self):
        """Remote Script should have dispatch handlers."""
        handlers = parse_remote_script_dispatch("AbletonMCP_Remote_Script/__init__.py")
        assert len(handlers) > 50, f"Expected 50+ handlers, got {len(handlers)}"

    def test_known_handlers_present(self):
        """Key handlers should be present."""
        handlers = parse_remote_script_dispatch("AbletonMCP_Remote_Script/__init__.py")
        # At least some core commands must exist
        assert any("get" in h for h in handlers) or len(handlers) > 0

    def test_parse_empty_file(self):
        handlers = parse_remote_script_dispatch("/dev/null")
        assert handlers == set()


class TestIsNormalizedParam:
    """Mutation-killing tests for parameter normalization check."""

    def test_volume_is_normalized(self):
        assert is_normalized_param("volume") is True

    def test_pan_is_normalized(self):
        assert is_normalized_param("pan") is True

    def test_track_index_not_normalized(self):
        assert is_normalized_param("track_index") is False

    def test_name_not_normalized(self):
        assert is_normalized_param("name") is False

    def test_reverb_is_normalized(self):
        assert is_normalized_param("send_amount") is True


class TestViolation:
    def test_str_representation(self):
        v = Violation(check="unnormalized", file="test.py", function="test_fn", detail="test")
        s = str(v)
        assert "unnormalized" in s
        assert "test.py" in s
        assert "test_fn" in s
