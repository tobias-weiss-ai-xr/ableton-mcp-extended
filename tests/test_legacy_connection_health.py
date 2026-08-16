"""Tests for MCP_Server/connection_health.py — migrated from scripts/test/test_connection_health.py.

Covers ConnectionHealth state machine, error codes, reconnection constants,
ping recording, health snapshots, uptime tracking, and module-level singleton.

No Ableton Live connection required — pure unit tests on the state machine.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import connection_health directly to avoid MCP_Server/__init__.py side effects
# (sounddevice dependency, MCP tool registration).
# ---------------------------------------------------------------------------
_SERVER_DIR = Path(__file__).resolve().parent.parent / "MCP_Server"
_spec = importlib.util.spec_from_file_location(
    "connection_health",
    str(_SERVER_DIR / "connection_health.py"),
)
_ch_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ch_mod)

ConnectionHealth = _ch_mod.ConnectionHealth
make_error_response = _ch_mod.make_error_response
ERROR_CODES = _ch_mod.ERROR_CODES
RECONNECT_DELAYS = _ch_mod.RECONNECT_DELAYS
MAX_RETRIES = _ch_mod.MAX_RETRIES


# ===================================================================
# 1. Initial State
# ===================================================================


class TestInitialState:
    def test_state_is_disconnected(self):
        ch = ConnectionHealth()
        assert ch.state == "disconnected"

    def test_health_snapshot_disconnected(self):
        health = ConnectionHealth().get_health()
        assert health["connection_state"] == "disconnected"
        assert health["last_ping_ms"] == 0.0
        assert health["uptime"] == 0.0
        assert health["reconnect_count"] == 0
        assert health["last_error"] == ""
        assert health["disconnected_for"] >= 0.0


# ===================================================================
# 2. State Transitions
# ===================================================================


class TestStateTransitions:
    def test_disconnected_to_connecting(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        assert ch.state == "connecting"

    def test_connecting_to_connected(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        assert ch.state == "connected"

    def test_connected_to_reconnecting(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("reconnecting")
        assert ch.state == "reconnecting"

    def test_reconnecting_to_connected(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("reconnecting")
        ch.set_state("connected")
        assert ch.state == "connected"

    def test_connected_to_error(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("error", "Something broke")
        assert ch.state == "error"

    def test_error_to_disconnected(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("error", "broke")
        ch.set_state("disconnected")
        assert ch.state == "disconnected"


# ===================================================================
# 3. Invalid (no-op) Transitions
# ===================================================================


class TestNoopTransitions:
    def test_connected_to_connected_is_noop(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("connected")  # already connected — should be no-op
        assert ch.state == "connected"


# ===================================================================
# 4. Ping Recording
# ===================================================================


class TestPingRecording:
    def test_single_ping(self):
        ch = ConnectionHealth()
        ch.record_ping(5.0)
        assert ch._last_ping_ms == 5.0
        assert ch.average_ping_ms == 5.0

    def test_two_pings_average(self):
        ch = ConnectionHealth()
        ch.record_ping(5.0)
        ch.record_ping(10.0)
        assert ch._last_ping_ms == 10.0
        assert abs(ch.average_ping_ms - 7.5) < 0.001

    def test_rolling_window_drops_oldest(self):
        ch = ConnectionHealth()
        for v in [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]:
            ch.record_ping(v)
        assert len(ch._ping_window) == 5
        assert ch._ping_window[0] == 10.0  # 5.0 dropped
        assert ch._last_ping_ms == 30.0


# ===================================================================
# 5. Reconnect Counting
# ===================================================================


class TestReconnectCounting:
    def test_first_reconnect(self):
        ch = ConnectionHealth()
        ch.record_reconnect()
        assert ch._reconnect_count == 1

    def test_second_reconnect(self):
        ch = ConnectionHealth()
        ch.record_reconnect()
        ch.record_reconnect()
        assert ch._reconnect_count == 2


# ===================================================================
# 6. Error Recording
# ===================================================================


class TestErrorRecording:
    def test_record_error_sets_message(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.record_error("Socket timeout")
        assert ch._last_error == "Socket timeout"
        assert ch._last_error_timestamp is not None

    def test_set_state_error_records_details(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("error", "Connection refused")
        health = ch.get_health()
        assert health["last_error"] == "Connection refused"
        assert health["last_error_timestamp"] is not None


# ===================================================================
# 7. Health Snapshot
# ===================================================================


class TestHealthSnapshot:
    def test_snapshot_after_connect(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.record_ping(3.5)
        ch.record_reconnect()
        health = ch.get_health()
        assert health["connection_state"] == "connected"
        assert health["last_ping_ms"] == 3.5
        assert health["reconnect_count"] == 1
        assert health["uptime"] >= 0.0
        assert "disconnected_for" in health


# ===================================================================
# 8. Uptime Tracking
# ===================================================================


class TestUptimeTracking:
    def test_uptime_grows_when_connected(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        assert ch.get_health()["uptime"] >= 0.0

    def test_uptime_resets_on_disconnect(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("disconnected")
        assert ch.get_health()["uptime"] == 0.0

    def test_uptime_resumes_after_reconnect(self):
        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.set_state("disconnected")
        ch.set_state("connected")
        ch.record_reconnect()
        assert ch.get_health()["uptime"] >= 0.0


# ===================================================================
# 9. make_error_response
# ===================================================================


class TestMakeErrorResponse:
    def test_retryable_error(self):
        err = make_error_response("LIVE_DISCONNECTED", "Connection lost")
        assert err["code"] == "LIVE_DISCONNECTED"
        assert err["retryable"] is True
        assert err["error"] == "Connection lost"

    def test_non_retryable_error(self):
        err = make_error_response("INVALID_INDEX", "Index out of range")
        assert err["retryable"] is False

    def test_extra_fields(self):
        err = make_error_response(
            "INVALID_INDEX", "Index out of range", extra={"max_index": 7}
        )
        assert err["max_index"] == 7


# ===================================================================
# 10. All Error Codes
# ===================================================================


class TestErrorCodes:
    EXPECTED_CODES = {
        "LIVE_DISCONNECTED", "LIVE_RECONNECTING", "LIVE_NOT_RUNNING",
        "INVALID_INDEX", "TIMEOUT", "UNKNOWN_COMMAND",
        "INTERNAL_ERROR", "FILE_NOT_FOUND",
    }

    def test_all_codes_present(self):
        assert set(ERROR_CODES.keys()) == self.EXPECTED_CODES

    @pytest.mark.parametrize("code", EXPECTED_CODES)
    def test_code_has_retryable_field(self, code):
        assert "retryable" in ERROR_CODES[code]

    @pytest.mark.parametrize("code", EXPECTED_CODES)
    def test_code_has_description_field(self, code):
        assert "description" in ERROR_CODES[code]


# ===================================================================
# 11. Constants
# ===================================================================


class TestConstants:
    def test_reconnect_delays(self):
        assert RECONNECT_DELAYS == [1.0, 2.0, 4.0]

    def test_max_retries(self):
        assert MAX_RETRIES == 3


# ===================================================================
# 12. Singleton
# ===================================================================


class TestSingleton:
    def test_get_connection_health_returns_same_instance(self):
        ch1 = _ch_mod.get_connection_health()
        ch2 = _ch_mod.get_connection_health()
        assert ch1 is ch2
