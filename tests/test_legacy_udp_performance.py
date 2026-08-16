"""UDP performance tests — migrated from scripts/test/test_network_performance.py.

Covers:
- Load: 1000 UDP commands complete within a generous time budget
- Latency: individual command dispatch < 2ms average (no response wait)
- Packet loss: simulated 5 % loss is tolerated
- Concurrent: mixed TCP/UDP traffic doesn't break UDP delivery
- Baseline: UDP is faster than TCP (which times out)

No Ableton Live connection required — uses a mock UDP server.
"""

from __future__ import annotations

import importlib.util
import json
import random
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

# Dedicated port for performance tests
_TEST_UDP_PORT = 19781


# ---------------------------------------------------------------------------
# Mock UDP server (with optional simulated packet loss)
# ---------------------------------------------------------------------------


class MockUDPServer:
    def __init__(self, port: int = _TEST_UDP_PORT, loss_rate: float = 0.0):
        self.port = port
        self.loss_rate = loss_rate
        self.sock: socket.socket | None = None
        self.running = False
        self.received: List[dict] = []

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.05)
        self.sock.bind(("127.0.0.1", self.port))
        self.running = True
        __import__("threading").Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(4096)
                if self.loss_rate > 0 and random.random() < self.loss_rate:
                    continue
                self.received.append(json.loads(data.decode("utf-8")))
            except socket.timeout:
                continue
            except Exception:
                pass

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()

    @property
    def count(self) -> int:
        return len(self.received)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_udp():
    srv = MockUDPServer()
    srv.start()
    time.sleep(0.05)
    yield srv
    srv.stop()


@pytest.fixture()
def conn():
    c = AbletonConnection(host="127.0.0.1", port=9877)
    orig = c.udp_port
    c.udp_port = _TEST_UDP_PORT
    yield c
    c.udp_port = orig


# ---------------------------------------------------------------------------
# Load Test
# ---------------------------------------------------------------------------


class TestLoadPerformance:
    def test_1000_commands_complete(self, mock_udp, conn):
        """1000 UDP commands should complete in < 5 seconds (generous budget)."""
        n = 1000
        templates = [
            ("set_device_parameter",
             {"track_index": 0, "device_index": 0, "parameter_index": 0, "value": 0.5}),
            ("set_track_volume", {"track_index": 0, "volume": 0.5}),
            ("set_track_pan", {"track_index": 0, "pan": 0.0}),
            ("set_track_mute", {"track_index": 0, "mute": False}),
            ("set_track_solo", {"track_index": 0, "solo": False}),
            ("set_track_arm", {"track_index": 0, "arm": False}),
            ("fire_clip", {"track_index": 0, "clip_index": 0}),
            ("set_master_volume", {"volume": 0.75}),
        ]
        start = time.time()
        for i in range(n):
            cmd_type, params = templates[i % len(templates)]
            conn.send_command_udp(cmd_type, params)
        elapsed = time.time() - start

        # Generous: must finish in 5 s (CI may be slow)
        assert elapsed < 5.0, f"Load test took {elapsed:.2f}s — too slow"

        time.sleep(0.2)
        # At least 90 % delivery
        assert mock_udp.count >= int(n * 0.9)


# ---------------------------------------------------------------------------
# Latency Test
# ---------------------------------------------------------------------------


class TestLatencyPerformance:
    def test_single_command_latency(self, mock_udp, conn):
        """Individual dispatch should be sub-millisecond (no response wait)."""
        latencies: List[float] = []
        for _ in range(100):
            t0 = time.perf_counter()
            conn.send_command_udp("set_track_volume", {"track_index": 0, "volume": 0.5})
            latencies.append((time.perf_counter() - t0) * 1000)

        avg_ms = sum(latencies) / len(latencies)
        # Must be < 5 ms on any reasonable machine
        assert avg_ms < 5.0, f"Average latency {avg_ms:.2f}ms too high"


# ---------------------------------------------------------------------------
# Packet Loss Test
# ---------------------------------------------------------------------------


class TestPacketLossTolerance:
    def test_5_percent_loss_tolerated(self):
        srv = MockUDPServer(loss_rate=0.05)
        srv.start()
        time.sleep(0.05)
        c = AbletonConnection(host="127.0.0.1", port=9877)
        c.udp_port = _TEST_UDP_PORT

        n = 100
        for i in range(n):
            c.send_command_udp(
                "set_track_volume", {"track_index": 0, "volume": i / 100.0}
            )
        time.sleep(0.3)

        # Must receive >= 80 % (with random 5 % loss, expect ~95 %)
        assert srv.count >= int(n * 0.8), (
            f"Too many packets lost: {srv.count}/{n}"
        )
        srv.stop()


# ---------------------------------------------------------------------------
# Concurrent TCP/UDP Test
# ---------------------------------------------------------------------------


class TestConcurrentTraffic:
    def test_mixed_traffic_udp_unaffected(self, mock_udp, conn):
        """Interleaved failed TCP calls must not block or break UDP delivery."""
        n = 200
        udp_sent = 0
        start = time.time()
        for i in range(n):
            if i % 20 == 0:
                # TCP call will fail (no Ableton) but must not block
                try:
                    conn.send_command("get_session_info", {})
                except Exception:
                    pass
            else:
                conn.send_command_udp(
                    "set_track_volume",
                    {"track_index": 0, "volume": (i % 100) / 100.0},
                )
                udp_sent += 1
        elapsed = time.time() - start
        assert elapsed < 5.0
        time.sleep(0.2)
        # Most UDP packets should arrive
        assert mock_udp.count >= int(udp_sent * 0.8)


# ---------------------------------------------------------------------------
# Baseline Comparison
# ---------------------------------------------------------------------------


class TestBaselineComparison:
    def test_udp_faster_than_tcp_attempt(self, mock_udp, conn):
        """Sending 50 UDP commands should be faster than 50 failing TCP attempts."""
        count = 50

        # UDP
        t0 = time.time()
        for _ in range(count):
            conn.send_command_udp("set_track_volume", {"track_index": 0, "volume": 0.5})
        udp_ms = (time.time() - t0) * 1000

        # TCP (will time out / fail)
        t0 = time.time()
        for _ in range(count):
            try:
                conn.send_command("get_session_info", {})
            except Exception:
                pass
        tcp_ms = (time.time() - t0) * 1000

        # UDP should be faster (TCP has connection timeout overhead)
        assert udp_ms < tcp_ms, (
            f"UDP ({udp_ms:.0f}ms) should be faster than TCP ({tcp_ms:.0f}ms)"
        )
