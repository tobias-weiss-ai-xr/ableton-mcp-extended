#!/usr/bin/env python3
"""
Test suite for VST audio analysis system.

This package contains unit tests for:
- Parameter polling system
- VST rules parser and engine
- Control loop logic
- Error handling scenarios
- Integration testing with mock MCP server
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
import socket
import threading
import time

# Add the scripts/analysis directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))

from poll_plugin_params import ParameterPoller
from rules_parser import RulesParser
from rules_engine import RulesEngine
from responsive_control import ResponsiveController


class MockMCPServer:
    """Mock MCP server for testing without Ableton connection."""

    def __init__(self, host="127.0.0.1", tcp_port=9877, udp_port=9878):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_socket = None
        self.udp_socket = None
        self.running = False
        self.responses = {}
        self.log = []

    def start(self):
        """Start mock server on both TCP and UDP ports."""
        self.running = True

        # Start TCP server for reliable operations
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.tcp_socket.bind((self.host, self.tcp_port))
            self.tcp_socket.listen(5)
            threading.Thread(target=self._tcp_handler, daemon=True).start()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Mock server: TCP port {self.tcp_port} already in use")
            else:
                raise

        # Start UDP server for parameter updates
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.udp_socket.bind((self.host, self.udp_port))
            threading.Thread(target=self._udp_handler, daemon=True).start()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Mock server: UDP port {self.udp_port} already in use")
            else:
                raise

    def stop(self):
        """Stop mock server."""
        self.running = False
        if self.tcp_socket:
            self.tcp_socket.close()
        if self.udp_socket:
            self.udp_socket.close()

    def _tcp_handler(self):
        """Handle TCP connections."""
        while self.running:
            try:
                client_socket, addr = self.tcp_socket.accept()
                threading.Thread(
                    target=self._tcp_client_handler,
                    args=(client_socket, addr),
                    daemon=True,
                ).start()
            except:
                break

    def _tcp_client_handler(self, client_socket, addr):
        """Handle individual TCP client."""
        try:
            data = client_socket.recv(8192).decode("utf-8")
            command = json.loads(data)

            # Log the command
            self.log.append(
                {
                    "type": "command",
                    "protocol": "tcp",
                    "data": command,
                    "timestamp": time.time(),
                }
            )

            # Get predefined response or create default
            response = self.responses.get(
                command["type"], self._default_response(command)
            )
            client_socket.send(json.dumps(response).encode("utf-8"))

        except Exception as e:
            print(f"Mock TCP handler error: {e}")
        finally:
            client_socket.close()

    def _udp_handler(self):
        """Handle UDP messages."""
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(4096)
                command = json.loads(data.decode("utf-8"))

                # Log the command
                self.log.append(
                    {
                        "type": "command",
                        "protocol": "udp",
                        "data": command,
                        "timestamp": time.time(),
                    }
                )

            except Exception as e:
                print(f"Mock UDP handler error: {e}")

    def _default_response(self, command):
        """Generate default response for unknown commands."""
        return {
            "status": "success",
            "type": command.get("type", "unknown"),
            "result": None,
        }

    def set_response(self, command_type, response):
        """Set custom response for a command type."""
        self.responses[command_type] = response

    def get_log(self):
        """Get logged commands."""
        return self.log

    def clear_log(self):
        """Clear command log."""
        self.log = []


class BaseTestCase(unittest.TestCase):
    """Base test case with mock server setup."""

    def setUp(self):
        """Set up test environment with mock server."""
        self.mock_server = MockMCPServer()
        self.mock_server.start()
        time.sleep(0.1)  # Give server time to start

    def tearDown(self):
        """Clean up test environment."""
        self.mock_server.stop()

    def send_tcp_command(self, command):
        """Send command via TCP and return response."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", self.mock_server.tcp_port))
            sock.send(json.dumps(command).encode("utf-8"))
            response = sock.recv(8192).decode("utf-8")
            sock.close()
            return json.loads(response)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def send_udp_command(self, command):
        """Send command via UDP (fire and forget)."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(
                json.dumps(command).encode("utf-8"),
                ("127.0.0.1", self.mock_server.udp_port),
            )
            sock.close()
            return True
        except Exception as e:
            print(f"UDP send error: {e}")
            return False


if __name__ == "__main__":
    # Run tests when script is executed directly
    unittest.main(verbosity=2)
