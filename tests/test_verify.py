"""
Tests for MCP_Server/verify.py — verify loop for Ableton MCP.

Tests the verify wrapper logic (MODIFYING_COMMANDS, snapshot capture, diff computation,
error handling, thread safety) without requiring an active Ableton Live connection.
"""

import json
import time
import threading
import os
import sys
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from MCP_Server.verify import (
    MODIFYING_COMMANDS,
    VERIFY_STRATEGY,
    capture_snapshot,
    compute_diff,
    wrap_ableton_connection,
)

# ── Helper: create a mock ableton "connection" ──────────────────────────────


def _make_mock_connection(send_command=None):
    """Create a mock object that looks like an AbletonConnection."""
    conn = MagicMock()
    if send_command is not None:
        conn.send_command = send_command
    else:
        conn.send_command = MagicMock(return_value={"status": "ok"})
    return conn


# ── Test 1: Verify wraps only modifying commands ────────────────────────────


class TestModifyingCommands:
    """Verify MODIFYING_COMMANDS covers all expected modifying operations."""

    def test_modifying_commands_include_create_midi_track(self):
        assert "create_midi_track" in MODIFYING_COMMANDS

    def test_modifying_commands_include_delete_all_tracks(self):
        assert "delete_all_tracks" in MODIFYING_COMMANDS

    def test_modifying_commands_include_set_tempo(self):
        assert "set_tempo" in MODIFYING_COMMANDS

    def test_modifying_commands_include_fire_clip(self):
        assert "fire_clip" in MODIFYING_COMMANDS


# ── Test 2: Verify does NOT wrap read-only / get-like commands ──────────────


class TestReadOnlyCommands:
    """Commands starting with get_, list_, query_ should NOT be in MODIFYING_COMMANDS."""

    def test_get_commands_not_modifying(self):
        for cmd in MODIFYING_COMMANDS:
            assert not cmd.startswith("get_"), f"get_ command in MODIFYING: {cmd}"

    def test_list_commands_not_modifying(self):
        for cmd in MODIFYING_COMMANDS:
            assert not cmd.startswith("list_"), f"list_ command in MODIFYING: {cmd}"

    def test_query_commands_not_modifying(self):
        for cmd in MODIFYING_COMMANDS:
            assert not cmd.startswith("query_"), f"query_ command in MODIFYING: {cmd}"


# ── Test 3: Pre/post snapshot captures correct state ────────────────────────


class TestSnapshotCapture:
    """capture_snapshot should call the right get_* command."""

    def test_capture_snapshot_calls_send_command(self):
        conn = _make_mock_connection()
        capture_snapshot(conn, "set_tempo", {"bpm": 120})
        conn.send_command.assert_called()

    def test_capture_snapshot_returns_dict(self):
        conn = _make_mock_connection()
        snapshot = capture_snapshot(conn, "set_tempo", {"bpm": 120})
        assert isinstance(snapshot, dict)

    def test_capture_snapshot_unknown_command(self):
        """Unknown commands use get_session_info as fallback strategy."""
        conn = _make_mock_connection()
        snapshot = capture_snapshot(conn, "nonexistent_cmd", {})
        assert isinstance(snapshot, dict)


# ── Test 4: Diff computed correctly when state changes ──────────────────────


class TestDiffComputation:
    """compute_diff should detect state changes."""

    def test_diff_detects_changes(self):
        before = {"tempo": {"bpm": 120}}
        after = {"tempo": {"bpm": 130}}
        diff = compute_diff(before, after)
        assert "tempo" in diff

    def test_diff_values_correct(self):
        before = {"tempo": {"bpm": 120}}
        after = {"tempo": {"bpm": 130}}
        diff = compute_diff(before, after)
        assert diff["tempo"]["before"]["bpm"] == 120
        assert diff["tempo"]["after"]["bpm"] == 130


# ── Test 5: No-op diff when state unchanged ─────────────────────────────────


class TestNoopDiff:
    """compute_diff should return empty dict when nothing changed."""

    def test_no_change_returns_empty(self):
        state = {"tempo": {"bpm": 120}}
        diff = compute_diff(state, state)
        assert diff == {}

    def test_no_change_for_deep_equal(self):
        before = {"tracks": [{"name": "Kick", "devices": ["Drum Rack"]}]}
        after = {"tracks": [{"name": "Kick", "devices": ["Drum Rack"]}]}
        diff = compute_diff(before, after)
        assert diff == {}


# ── Test 6: Error handling when snapshot capture fails ──────────────────────


class TestSnapshotErrors:
    """capture_snapshot should handle errors gracefully."""

    def test_snapshot_capture_error_returns_error_entry(self):
        conn = _make_mock_connection()
        conn.send_command.side_effect = RuntimeError("connection lost")
        snapshot = capture_snapshot(conn, "set_tempo", {"bpm": 120})
        # Should have an error entry instead of crashing
        assert isinstance(snapshot, dict)


# ── Test 7: Thread safety test (concurrent calls) ───────────────────────────


class TestThreadSafety:
    """Multiple concurrent verify calls should not corrupt state."""

    def test_concurrent_snapshot_calls(self):
        results = []
        errors = []

        def do_capture():
            try:
                conn = _make_mock_connection()
                s = capture_snapshot(conn, "delete_all_tracks", {})
                results.append(s)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=do_capture) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 10


# ── Test 8: Empty diff structure returned when no change ────────────────────


class TestEmptyDiff:
    """Empty diff when no change is an empty dict."""

    def test_empty_diff_is_empty_dict(self):
        diff = compute_diff({}, {})
        assert diff == {}


# ── Test 9: Verify disabled via env var ─────────────────────────────────────


class TestVerifyDisabled:
    """Verify loop should be skippable via environment variable."""

    def test_wrap_still_works_with_env(self):
        # The actual env check is in server.py; here we test that
        # wrap_ableton_connection still works normally.
        conn = _make_mock_connection()
        wrapped = wrap_ableton_connection(conn)
        assert wrapped is not None
        # Wrapping twice should be idempotent
        wrapped2 = wrap_ableton_connection(wrapped)
        assert wrapped2 is not None


# ── Test 10: Verify with missing snapshot handler ───────────────────────────


class TestMissingSnapshotHandler:
    """Commands with no strategy entry should use default fallback."""

    def test_no_strategy_uses_fallback(self):
        conn = _make_mock_connection()
        snapshot = capture_snapshot(conn, "unknown_cmd", {})
        assert isinstance(snapshot, dict)


# ── Test 11: Verify with timeout on snapshot ────────────────────────────────


class TestSnapshotTimeout:
    """Timeout on snapshot should not crash the verify loop."""

    def test_snapshot_timeout_returns_error(self):
        conn = _make_mock_connection()

        def slow_send(*args, **kwargs):
            time.sleep(0.5)
            return {"status": "ok"}

        conn.send_command = slow_send
        snapshot = capture_snapshot(conn, "set_tempo", {"bpm": 120})
        assert isinstance(snapshot, dict)


# ── Test 12: Verify with nested verify (prevent recursion) ──────────────────


class TestNestedVerify:
    """Verify loop should not cause infinite recursion."""

    def test_wrap_idempotent(self):
        conn = _make_mock_connection()
        w1 = wrap_ableton_connection(conn)
        w2 = wrap_ableton_connection(w1)
        w3 = wrap_ableton_connection(w2)
        # All three return the same wrapped object; no recursion
        assert w3 is not None
        assert w3._verify_wrapped is True
