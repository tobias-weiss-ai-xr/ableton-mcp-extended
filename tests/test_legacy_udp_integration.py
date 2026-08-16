"""Mock-based UDP integration tests — migrated from scripts/test/test_udp_integration.py.

Covers:
- Mock UDP server receives dispatched commands
- Multiple rapid UDP commands arrive in order
- UDP and TCP coexist (different ports)

No Ableton Live connection required — uses a mock UDP server.
"""

from __future__ import annotations

import importlib.util
import json
import socket
import time
from pathlib import Path
from typing import List

import pytest

# ---------------------------------------------------------------------------
# Import server module via importlib
# ---------------------------------------------------------------------------
_SERVER_DIR = Path(__file__).resolve().parent.parent / "MCP_Server"
_spec = importlib.util.spec_from_file_location("server", str(_SERVER_DIR / "server.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AbletonConnection = _mod.AbletonConnection

# Dedicated test port
_TEST_UDP_PORT = 19780


# ---------------------------------------------------------------------------
# Mock UDP server
# ---------------------------------------------------------------------------


class MockRemoteScriptUDPServer:
    """Minimal mock that captures received UDP commands."""

    def __init__(self, host: str = "127.0.0.1", port: int = _TEST_UDP_PORT):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.running = False
        self.received_commands: List[dict] = []

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        self.sock.bind((self.host, self.port))
        self.running = True
        thread = __import__("threading").Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(4096)
                cmd = json.loads(data.decode("utf-8"))
                self.received_commands.append(cmd)
            except socket.timeout:
                continue
            except Exception:
                if self.running:
                    pass

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()

    @property
    def command_count(self) -> int:
        return len(self.received_commands)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_server():
    srv = MockRemoteScriptUDPServer()
    srv.start()
    time.sleep(0.1)  # let the listener thread start
    yield srv
    srv.stop()


@pytest.fixture()
def connection():
    conn = AbletonConnection(host="127.0.0.1", port=9877)
    original_port = conn.udp_port
    conn.udp_port = _TEST_UDP_PORT
    yield conn
    conn.udp_port = original_port


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestUdpDispatch:
    def test_single_command_received(self, mock_server, connection):
        connection.send_command_udp(
            "set_track_volume", {"track_index": 0, "volume": 0.75}
        )
        time.sleep(0.2)
        assert mock_server.command_count >= 1
        cmd = mock_server.received_commands[0]
        assert cmd["type"] == "set_track_volume"
        assert cmd["params"]["volume"] == 0.75

    def test_multiple_commands_in_order(self, mock_server, connection):
        n = 10
        for i in range(n):
            volume = 0.5 + i * 0.05
            connection.send_command_udp(
                "set_track_volume", {"track_index": 0, "volume": volume}
            )
        time.sleep(0.3)
        assert mock_server.command_count == n
        for i, cmd in enumerate(mock_server.received_commands):
            expected = 0.5 + i * 0.05
            assert cmd["params"]["volume"] == expected


class TestTcpUdpCoexistence:
    def test_udp_port_differs_from_tcp_port(self):
        """Protocol separation is verified by design: UDP 9878 vs TCP 9877."""
        assert AbletonConnection.udp_port != 9877
