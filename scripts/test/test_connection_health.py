"""
Test connection_health.py state machine, error codes, and reconnection constants.

Standalone script (no Ableton Live required) — tests the state machine logic
in isolation. Run with: python scripts/test/test_connection_health.py
"""

import sys
import os

# Ensure MCP_Server is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import directly to avoid __init__.py side effects (sounddevice dependency)
import importlib.util

spec = importlib.util.spec_from_file_location(
    "connection_health",
    os.path.join(os.path.dirname(__file__), "..", "..", "MCP_Server", "connection_health.py"),
)
ch_mod = importlib.util.module_from_spec(spec)
sys.modules["connection_health"] = ch_mod
spec.loader.exec_module(ch_mod)

ConnectionHealth = ch_mod.ConnectionHealth
make_error_response = ch_mod.make_error_response
ERROR_CODES = ch_mod.ERROR_CODES
RECONNECT_DELAYS = ch_mod.RECONNECT_DELAYS
MAX_RETRIES = ch_mod.MAX_RETRIES

passed = 0
failed = 0


def check(condition: bool, name: str):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed += 1
        print(f"  ✗ {name}")


# ── Test 1: Initial State ────────────────────────────────────────────────
print("\n=== 1. Initial State ===")
ch = ConnectionHealth()
check(ch.state == "disconnected", "Initial state is disconnected")

health = ch.get_health()
check(health["connection_state"] == "disconnected", "Health snapshot shows disconnected")
check(health["last_ping_ms"] == 0.0, "last_ping_ms starts at 0.0")
check(health["uptime"] == 0.0, "uptime starts at 0.0 when disconnected")
check(health["reconnect_count"] == 0, "reconnect_count starts at 0")
check(health["last_error"] == "", "last_error starts empty")
check(health["disconnected_for"] >= 0.0, "disconnected_for is non-negative")

# ── Test 2: State Transitions ────────────────────────────────────────────
print("\n=== 2. State Transitions ===")

ch = ConnectionHealth()
ch.set_state("connecting")
check(ch.state == "connecting", "disconnected → connecting")

ch.set_state("connected")
check(ch.state == "connected", "connecting → connected")

ch.set_state("reconnecting")
check(ch.state == "reconnecting", "connected → reconnecting")

ch.set_state("connected")
check(ch.state == "connected", "reconnecting → connected")

ch.set_state("error", "Something broke")
check(ch.state == "error", "connected → error")

ch.set_state("disconnected")
check(ch.state == "disconnected", "error → disconnected")

# ── Test 3: Invalid transitions are no-ops ────────────────────────────────
print("\n=== 3. Invalid (no-op) Transitions ===")

ch = ConnectionHealth()
ch.set_state("connecting")
ch.set_state("connected")
ch.set_state("connected")  # Already connected — should be no-op
check(ch.state == "connected", "connected → connected is no-op")

# ── Test 4: Ping Recording ───────────────────────────────────────────────
print("\n=== 4. Ping Recording ===")

ch = ConnectionHealth()
ch.record_ping(5.0)
check(ch._last_ping_ms == 5.0, "Single ping recorded")
check(ch.average_ping_ms == 5.0, "Average matches single ping")

ch.record_ping(10.0)
check(ch._last_ping_ms == 10.0, "Second ping updates last_ping_ms")
check(abs(ch.average_ping_ms - 7.5) < 0.001, "Average of 2 pings is 7.5")

ch.record_ping(15.0)
ch.record_ping(20.0)
ch.record_ping(25.0)
ch.record_ping(30.0)  # 6th ping — rolling window should drop the first (5.0)
check(len(ch._ping_window) == 5, "Rolling window capped at 5 entries")
check(ch._ping_window[0] == 10.0, "Oldest ping (5.0) dropped from window")
check(ch._last_ping_ms == 30.0, "Most recent ping retained")

# ── Test 5: Reconnect Counting ────────────────────────────────────────────
print("\n=== 5. Reconnect Counting ===")

ch.record_reconnect()
check(ch._reconnect_count == 1, "reconnect_count incremented to 1")

ch.record_reconnect()
check(ch._reconnect_count == 2, "reconnect_count incremented to 2")

# ── Test 6: Error Recording ──────────────────────────────────────────────
print("\n=== 6. Error Recording ===")

ch = ConnectionHealth()
ch.set_state("connected")
ch.record_error("Socket timeout")
check(ch._last_error == "Socket timeout", "Error message recorded")
check(ch._last_error_timestamp is not None, "Error timestamp set")

# Record error via set_state
ch.set_state("error", "Connection refused")
health = ch.get_health()
check(health["last_error"] == "Connection refused", "set_state records error")
check(health["last_error_timestamp"] is not None, "set_state records timestamp")

# ── Test 7: Health Snapshot ──────────────────────────────────────────────
print("\n=== 7. Health Snapshot ===")

ch = ConnectionHealth()
ch.set_state("connecting")
ch.set_state("connected")
ch.record_ping(3.5)
ch.record_reconnect()
health = ch.get_health()
check(health["connection_state"] == "connected", "Snapshot shows connected")
check(health["last_ping_ms"] == 3.5, "Snapshot shows last_ping_ms")
check(health["reconnect_count"] == 1, "Snapshot shows reconnect_count")
check(health["uptime"] >= 0.0, "Snapshot uptime is non-negative")
check("disconnected_for" in health, "Snapshot includes disconnected_for")

# ── Test 8: Uptime Tracking ──────────────────────────────────────────────
print("\n=== 8. Uptime Tracking ===")

ch = ConnectionHealth()
ch.set_state("connected")
check(ch.get_health()["uptime"] >= 0.0, "Uptime grows when connected")
ch.set_state("disconnected")
check(ch.get_health()["uptime"] == 0.0, "Uptime resets on disconnect")
ch.set_state("connected")
ch.record_reconnect()  # record_reconnect resets connect_start_time
check(ch.get_health()["uptime"] >= 0.0, "Uptime resumes after reconnect")

# ── Test 9: make_error_response ──────────────────────────────────────────
print("\n=== 9. make_error_response ===")

err = make_error_response("LIVE_DISCONNECTED", "Connection lost")
check(err["code"] == "LIVE_DISCONNECTED", "Error code set")
check(err["retryable"] is True, "LIVE_DISCONNECTED is retryable")
check(err["error"] == "Connection lost", "Error message set")

err2 = make_error_response("INVALID_INDEX", "Index out of range", extra={"max_index": 7})
check(err2["max_index"] == 7, "Extra fields included in error response")
check(err2["retryable"] is False, "INVALID_INDEX is not retryable")

# ── Test 10: All Error Codes ─────────────────────────────────────────────
print("\n=== 10. All Error Codes ===")

expected_codes = {
    "LIVE_DISCONNECTED", "LIVE_RECONNECTING", "LIVE_NOT_RUNNING",
    "INVALID_INDEX", "TIMEOUT", "UNKNOWN_COMMAND",
    "INTERNAL_ERROR", "FILE_NOT_FOUND",
}
actual_codes = set(ERROR_CODES.keys())
check(actual_codes == expected_codes, f"All {len(expected_codes)} error codes present")
for code in expected_codes:
    info = ERROR_CODES[code]
    check("retryable" in info, f"{code} has retryable field")
    check("description" in info, f"{code} has description field")

# ── Test 11: Constants ───────────────────────────────────────────────────
print("\n=== 11. Constants ===")

check(RECONNECT_DELAYS == [1.0, 2.0, 4.0], "RECONNECT_DELAYS = [1, 2, 4]")
check(MAX_RETRIES == 3, "MAX_RETRIES = 3")

# ── Test 12: Singleton ───────────────────────────────────────────────────
print("\n=== 12. Module-level Singleton ===")

ch1 = ch_mod.get_connection_health()
ch2 = ch_mod.get_connection_health()
check(ch1 is ch2, "get_connection_health() returns the same instance")

# ── Summary ──────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
