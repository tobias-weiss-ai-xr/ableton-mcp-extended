"""Tests for UDP command dispatching in MCP server — migrated from scripts/test/test_udp_dispatch.py.

Covers:
- send_command_udp() method exists on AbletonConnection
- Correct UDP port and protocol
- Fire-and-forget behaviour (returns immediately)

No Ableton Live connection required — uses a test UDP listener.
"""

from __future__ import annotations

import importlib.util
import json
import socket
import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import server module via importlib to match original script's pattern
# and avoid MCP_Server/__init__.py side effects.
# ---------------------------------------------------------------------------
_SERVER_DIR = Path(__file__).resolve().parent.parent / "MCP_Server"
_spec = importlib.util.spec_from_file_location("server", str(_SERVER_DIR / "server.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AbletonConnection = _mod.AbletonConnection

# Use a dedicated test port to avoid conflicts with other parallel tests
_TEST_UDP_PORT = 19779


@pytest.fixture()
def test_udp_listener():
    """Create a short-lived UDP listener on the test port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    sock.bind(("127.0.0.1", _TEST_UDP_PORT))
    yield sock
    sock.close()


class TestSendCommandUdpExists:
    def test_method_exists(self):
        assert hasattr(AbletonConnection, "send_command_udp")


class TestUdpPortAndProtocol:
    def test_uses_udp_port_9878(self):
        """Class-level udp_port constant should be 9878."""
        assert AbletonConnection.udp_port == 9878

    def test_sends_to_udp_port(self, test_udp_listener):
        """Verify send_command_udp() sends a UDP packet."""
        conn = AbletonConnection(host="127.0.0.1", port=9877)
        # Monkey-patch the UDP port so the test listener catches it
        original_port = conn.udp_port
        conn.udp_port = _TEST_UDP_PORT
        try:
            result = conn.send_command_udp(
                "set_track_volume", {"track_index": 0, "volume": 0.75}
            )
            # fire-and-forget returns None
            assert result is None

            data, addr = test_udp_listener.recvfrom(1024)
            received = json.loads(data.decode("utf-8"))
            assert received["type"] == "set_track_volume"
            assert received["params"]["volume"] == 0.75
        finally:
            conn.udp_port = original_port


class TestFireAndForget:
    def test_returns_immediately(self):
        conn = AbletonConnection(host="127.0.0.1", port=9877)
        start = time.time()
        conn.send_command_udp("set_track_volume", {"track_index": 0, "volume": 0.5})
        elapsed = time.time() - start
        # Must complete in < 100 ms (no network I/O waiting for response)
        assert elapsed < 0.1
