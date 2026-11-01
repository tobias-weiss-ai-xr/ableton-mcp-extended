"""Tests must never drive the operator's Ableton set.

These modules used to connect to the live session (port 9877/9878) and fire
scenes or create/delete tracks, which once deleted every track in the set the
user had open. mcp_client now refuses to send anything from a pytest run unless
ABLETON_LIVE_TESTS=1.
"""

import pytest

from mcp_client import MCPClientTCP, MCPClientUDP


def test_tcp_command_is_blocked_under_pytest():
    with pytest.raises(RuntimeError, match="ABLETON_LIVE_TESTS"):
        MCPClientTCP().send_command("get_session_info", {})


def test_udp_command_is_blocked_under_pytest():
    with pytest.raises(RuntimeError, match="ABLETON_LIVE_TESTS"):
        MCPClientUDP().send_command_udp("set_master_volume", {"volume": 0.5})
