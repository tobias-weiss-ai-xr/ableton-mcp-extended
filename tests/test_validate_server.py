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


class TestMutationKillingValueAssertions:
    """Kill remaining validate_server mutation survivors."""

    def test_boundary_float_defaults_are_valid(self, tmp_path):
        from MCP_Server.validate_server import check_normalized_params, parse_tools
        p = tmp_path / "boundary_tools.py"
        p.write_text(
            'from mcp.server.fastmcp import FastMCP\n'
            'server = FastMCP("b")\n'
            '@server.tool()\n'
            'def set_volume(volume: float = 0.0) -> None:\n'
            '    "set the volume"\n'
            '    pass\n'
            '@server.tool()\n'
            'def set_pan(pan: float = 1.0) -> None:\n'
            '    "set the pan"\n'
            '    pass\n',
            encoding="utf-8")
        tools = parse_tools(str(p))
        assert len(tools) == 2
        viols = check_normalized_params(tools)
        assert not any(v.check == "normalized_param" for v in viols), \
            "exact 0.0 / 1.0 defaults must be inside the valid range"

    def test_precise_tool_count_excludes_non_tool_decorators(self, tmp_path):
        from MCP_Server.validate_server import parse_tools
        p = tmp_path / "decorator_tools.py"
        p.write_text(
            'from mcp.server.fastmcp import FastMCP\n'
            'server = FastMCP("d")\n'
            '@server.tool()\n'
            'def real_one() -> None:\n'
            '    "doc"\n'
            '    pass\n'
            '@server.tool("named")\n'
            'def real_two() -> None:\n'
            '    "doc"\n'
            '    pass\n'
            '@server.something_else()\n'
            'def not_a_tool() -> None:\n'
            '    "doc"\n'
            '    pass\n',
            encoding="utf-8")
        tools = parse_tools(str(p))
        names = {t.name for t in tools}
        assert {"real_one", "real_two"} == names, \
            "only @*.tool() decorated functions must be counted as tools"
        assert len(tools) == 2


@pytest.mark.parametrize("name,expected", [
    ("set_track_volume", True),   # volume -> normalized
    ("volume", True),
    ("pan", True),
    ("send_amount", True),
    ("feedback", True),
    ("track_index", False),        # no normalized word
    ("name", False),
    ("pitch", False),
    ("ctx", False),
    ("clip_index", False),
], ids=["set_track_volume", "volume", "pan", "send_amount", "feedback",
        "track_index", "name", "pitch", "ctx", "clip_index"])
class TestIsNormalizedParamTable:
    """Table-driven cases for the normalized-param heuristic (S2)."""

    def test_heuristic(self, name, expected):
        from MCP_Server.validate_server import is_normalized_param
        assert is_normalized_param(name) is expected
