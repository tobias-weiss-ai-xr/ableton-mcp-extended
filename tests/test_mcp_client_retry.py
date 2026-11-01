"""A command that reached Live must never be sent twice.

The client used to retry any timeout, including one that happened *after* the
command had been sent. An `undo` that timed out was therefore applied up to
three times, rolling the session back further than asked.
"""

import socket

import pytest

from mcp_client import MCPClientTCP


def test_sent_command_is_not_retried_on_timeout(monkeypatch):
    monkeypatch.setenv("ABLETON_LIVE_TESTS", "1")  # no sockets below, nothing goes live
    sends = []

    class SilentSocket:
        def sendall(self, data):
            sends.append(data)

        def recv(self, _size):
            raise socket.timeout("timed out")

        def close(self):
            pass

    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: SilentSocket())

    with pytest.raises(socket.timeout, match="may already have been applied"):
        MCPClientTCP(max_retries=3).send_command_tcp("undo", {})

    assert len(sends) == 1, "a sent command was retried"


def test_connect_failure_is_still_retried(monkeypatch):
    monkeypatch.setenv("ABLETON_LIVE_TESTS", "1")  # no sockets below, nothing goes live
    attempts = []

    def refuse(*_a, **_k):
        attempts.append(1)
        raise socket.error("connection refused")

    monkeypatch.setattr(socket, "create_connection", refuse)

    with pytest.raises(socket.error):
        MCPClientTCP(max_retries=2).send_command_tcp("get_session_info", {})

    assert len(attempts) == 2
