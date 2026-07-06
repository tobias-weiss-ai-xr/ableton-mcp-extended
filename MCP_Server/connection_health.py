"""
Connection Health — state machine + health tracking for Ableton MCP.

Tracks connection state transitions (disconnected → connecting → reconnecting
→ connected → error), ping latency, uptime, reconnection count, and last error
details. Used by server.py and server_watchdog.py via a module-level singleton.

Thread-safe via threading.Lock.
"""

import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

# ── Types ────────────────────────────────────────────────────────────────────

ConnectionState = Literal["connected", "disconnected", "reconnecting", "error"]

# ── Constants ────────────────────────────────────────────────────────────────

RECONNECT_DELAYS: list[float] = [1.0, 2.0, 4.0]
"""Exponential backoff delays (seconds) between reconnection attempts."""

MAX_RETRIES: int = 3
"""Maximum number of reconnection attempts before marking DISCONNECTED."""

WATCHDOG_DISCONNECT_TIMEOUT: float = 30.0
"""Seconds in DISCONNECTED state before the watchdog triggers a server restart."""

PING_WINDOW_SIZE: int = 5
"""Number of recent ping samples retained in rolling window."""

ERROR_CODES: dict[str, dict[str, Any]] = {
    "LIVE_DISCONNECTED": {
        "retryable": True,
        "description": "No connection to Ableton Live",
    },
    "LIVE_RECONNECTING": {
        "retryable": True,
        "description": "Reconnecting to Ableton Live, try again shortly",
    },
    "LIVE_NOT_RUNNING": {
        "retryable": True,
        "description": "Ableton Live process is not detected",
    },
    "INVALID_INDEX": {
        "retryable": False,
        "description": "Track, clip, or device index out of range",
    },
    "TIMEOUT": {
        "retryable": True,
        "description": "Command timed out waiting for Ableton response",
    },
    "UNKNOWN_COMMAND": {
        "retryable": False,
        "description": "Command not recognized by the Remote Script",
    },
    "INTERNAL_ERROR": {
        "retryable": False,
        "description": "Unexpected internal server error",
    },
    "FILE_NOT_FOUND": {
        "retryable": False,
        "description": "Referenced file path does not exist",
    },
}
"""Central registry of all structured error codes with retryability and description."""


# ── Helpers ──────────────────────────────────────────────────────────────────


def make_error_response(
    code: str,
    message: str,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build a structured error response dict.

    >>> make_error_response("LIVE_DISCONNECTED", "Connection lost")
    {"error": "Connection lost", "code": "LIVE_DISCONNECTED", "retryable": True}
    """
    info = ERROR_CODES.get(code, {"retryable": False})
    resp: dict[str, Any] = {
        "error": message,
        "code": code,
        "retryable": info["retryable"],
    }
    if extra:
        resp.update(extra)
    return resp


# ── State Machine ────────────────────────────────────────────────────────────

# Valid state transitions
_VALID_TRANSITIONS: dict[ConnectionState, set[ConnectionState]] = {
    "disconnected": {"connecting", "reconnecting", "error"},
    "connecting": {"connected", "disconnected", "error"},
    "connected": {"disconnected", "reconnecting", "error"},
    "reconnecting": {"connected", "disconnected", "error"},
    "error": {"disconnected", "connecting", "reconnecting"},
}


class ConnectionHealth:
    """Thread-safe connection health state machine.

    Typical lifecycle::

        ch = ConnectionHealth()
        ch.set_state("connecting")
        ch.set_state("connected")
        ch.record_ping(5.0)                  # 5 ms round-trip
        ch.record_error("Socket timeout")
        ch.set_state("reconnecting")
        ch.record_reconnect()                 # after successful reconnect
        ch.get_health()                       # full snapshot
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: ConnectionState = "disconnected"
        self._last_ping_ms: float = 0.0
        self._ping_window: list[float] = []
        self._reconnect_count: int = 0
        self._connect_start_time: Optional[float] = None
        self._last_error: str = ""
        self._last_error_timestamp: Optional[str] = None
        self._disconnected_since: Optional[float] = None  # timestamp when entered disconnected

    # ── State ────────────────────────────────────────────────────────────

    @property
    def state(self) -> ConnectionState:
        with self._lock:
            return self._state

    def set_state(self, new_state: ConnectionState, error_msg: str = "") -> None:
        """Transition to *new_state*.

        If the transition is invalid (e.g. connected → connected) it is logged
        as a warning but not raised — the caller should never crash from a
        redundant transition.
        """
        with self._lock:
            allowed = _VALID_TRANSITIONS.get(self._state, set())
            if new_state == self._state:
                # No-op: already there
                return
            if new_state not in allowed:
                import logging

                logging.getLogger("AbletonMCPServer").warning(
                    "Invalid state transition: %s → %s (error=%r)",
                    self._state,
                    new_state,
                    error_msg,
                )
                return

            self._state = new_state

            if error_msg:
                self._last_error = error_msg
                self._last_error_timestamp = _now_iso()

            if new_state == "disconnected":
                self._disconnected_since = time.time()
                self._connect_start_time = None
            elif new_state == "connected":
                self._disconnected_since = None
                if self._connect_start_time is None:
                    self._connect_start_time = time.time()

    # ── Ping ─────────────────────────────────────────────────────────────

    def record_ping(self, latency_ms: float) -> None:
        """Record a ping latency sample.

        Maintains a rolling window of the last *PING_WINDOW_SIZE* samples.
        ``last_ping_ms`` reflects the most recent sample.
        """
        with self._lock:
            self._last_ping_ms = latency_ms
            self._ping_window.append(latency_ms)
            if len(self._ping_window) > PING_WINDOW_SIZE:
                self._ping_window.pop(0)

    @property
    def average_ping_ms(self) -> float:
        """Rolling average ping latency, or 0.0 if no samples."""
        with self._lock:
            if not self._ping_window:
                return 0.0
            return sum(self._ping_window) / len(self._ping_window)

    # ── Reconnects ───────────────────────────────────────────────────────

    def record_reconnect(self) -> None:
        """Increment reconnect counter and reset connect-start time."""
        with self._lock:
            self._reconnect_count += 1
            self._connect_start_time = time.time()
            self._last_error = ""
            self._last_error_timestamp = None

    # ── Errors ───────────────────────────────────────────────────────────

    def record_error(self, message: str) -> None:
        """Record an error message and ISO-8601 timestamp."""
        with self._lock:
            self._last_error = message
            self._last_error_timestamp = _now_iso()

    # ── Health snapshot ──────────────────────────────────────────────────

    def get_health(self) -> dict[str, Any]:
        """Return a full health snapshot dict.

        Keys: connection_state, last_ping_ms, uptime, reconnect_count,
        last_error, last_error_timestamp.
        """
        with self._lock:
            uptime = 0.0
            if self._state == "connected" and self._connect_start_time is not None:
                uptime = time.time() - self._connect_start_time

            disconnected_for = 0.0
            if self._state == "disconnected" and self._disconnected_since is not None:
                disconnected_for = time.time() - self._disconnected_since

            return {
                "connection_state": self._state,
                "last_ping_ms": self._last_ping_ms,
                "uptime": round(uptime, 2),
                "reconnect_count": self._reconnect_count,
                "last_error": self._last_error,
                "last_error_timestamp": self._last_error_timestamp,
                "disconnected_for": round(disconnected_for, 2),
            }

    # ── Helpers ──────────────────────────────────────────────────────────

    @property
    def disconnected_since(self) -> Optional[float]:
        with self._lock:
            return self._disconnected_since


# ── Module-level Singleton ───────────────────────────────────────────────────

_health: Optional[ConnectionHealth] = None
_health_lock = threading.Lock()


def get_connection_health() -> ConnectionHealth:
    """Return the module-level ConnectionHealth singleton."""
    global _health
    if _health is None:
        with _health_lock:
            if _health is None:
                _health = ConnectionHealth()
    return _health


# Convenience reference — importers can use ``connection_health`` directly.
connection_health = get_connection_health()


# ── Internal helpers ─────────────────────────────────────────────────────────


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
