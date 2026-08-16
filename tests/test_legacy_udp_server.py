"""Tests for UDP socket creation and messaging — migrated from scripts/test/test_udp_server.py.

Covers:
- UDP socket creation on port 9878
- UDP message sending

No Ableton Live connection required.
"""

from __future__ import annotations

import json
import socket

import pytest

# Use a non-conflicting port so tests run in parallel with other UDP tests.
# The original script used 9878 but that conflicts with mock servers in other
# migrated tests.  9879 is safe (not used by Ableton MCP).
_TEST_PORT = 9879


class TestUDPSocketCreation:
    """Test that a UDP socket can be created and bound."""

    def test_socket_creation(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(("127.0.0.1", _TEST_PORT))
        try:
            pass  # if we got here, binding succeeded
        finally:
            udp_socket.close()

    def test_socket_creation_tolerates_address_in_use(self):
        """Port already in use should not be a hard failure."""
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock1.bind(("127.0.0.1", _TEST_PORT))
        try:
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # On some OSes, binding a second UDP socket to the same port
            # raises Address already in use — that's acceptable.
            try:
                sock2.bind(("127.0.0.1", _TEST_PORT))
            except OSError as exc:
                assert "already in use" in str(exc).lower() or "address" in str(exc).lower()
            finally:
                sock2.close()
        finally:
            sock1.close()


class TestUDPMessageSend:
    """Test that UDP messages can be constructed and sent."""

    def test_send_udp_message(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind(("127.0.0.1", _TEST_PORT))
        server_sock.settimeout(0.5)

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_command = {
            "type": "set_device_parameter",
            "params": {
                "track_index": 0,
                "device_index": 0,
                "parameter_index": 0,
                "value": 0.5,
            },
        }
        message = json.dumps(test_command).encode("utf-8")
        client_sock.sendto(message, ("127.0.0.1", _TEST_PORT))

        try:
            data, _ = server_sock.recvfrom(1024)
            received = json.loads(data.decode("utf-8"))
            assert received["type"] == "set_device_parameter"
            assert received["params"]["value"] == 0.5
        finally:
            client_sock.close()
            server_sock.close()
