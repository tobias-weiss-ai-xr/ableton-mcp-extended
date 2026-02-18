"""
MCP Client for Ableton Live communication.

Provides TCP/UDP socket communication wrapper with auto-routing for critical vs
high-frequency operations.

TCP (port 9877): Reliable request/response for critical operations
UDP (port 9878): Fire-and-forget for high-frequency parameter updates

Usage:
    with MCPClient() as client:
        result = client.send("get_session_info", {})
        client.send("set_track_volume", {"track_index": 0, "volume": 0.75})
"""

import socket
import json
import time
from typing import Any, Optional


# Operations that MUST use TCP (Category D - critical operations)
CRITICAL_OPS = frozenset(
    {
        "get_",  # All get_* operations need response
        "delete_",  # All delete_* operations need confirmation
        "quantize",  # Quantize needs confirmation
        "undo",  # Undo needs confirmation
        "redo",  # Redo needs confirmation
        "start_recording",  # Recording control needs confirmation
        "stop_recording",
        "crop",  # Crop needs confirmation
        "mix",  # Mix operations need confirmation
    }
)


class MCPConnectionError(Exception):
    """Raised when connection to Ableton MCP server fails."""

    pass


class MCPClient:
    """
    TCP/UDP client for Ableton Live MCP communication.

    Features:
    - Dual TCP/UDP socket connections
    - Auto-routing based on command type
    - Retry logic with exponential backoff
    - Context manager support

    Attributes:
        host: Server hostname (default: localhost)
        tcp_port: TCP server port (default: 9877)
        udp_port: UDP server port (default: 9878)
        timeout: Socket timeout in seconds (default: 5.0)
        buffer_size: Receive buffer size (default: 8192)
        max_retries: Maximum retry attempts (default: 3)
    """

    def __init__(
        self,
        host: str = "localhost",
        tcp_port: int = 9877,
        udp_port: int = 9878,
        timeout: float = 5.0,
        buffer_size: int = 8192,
        max_retries: int = 3,
    ):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.max_retries = max_retries

        self._tcp_socket: Optional[socket.socket] = None
        self._udp_socket: Optional[socket.socket] = None
        self._connected = False

    def __enter__(self) -> "MCPClient":
        """Context manager entry - connects sockets."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes sockets."""
        self.close()

    def connect(self) -> None:
        """Initialize TCP and UDP socket connections."""
        # Create UDP socket (connectionless, just create it)
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Create TCP socket
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.settimeout(self.timeout)

        self._connected = True

    def close(self) -> None:
        """Close all socket connections."""
        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except Exception:
                pass
            self._tcp_socket = None

        if self._udp_socket:
            try:
                self._udp_socket.close()
            except Exception:
                pass
            self._udp_socket = None

        self._connected = False

    def verify_connection(self) -> bool:
        """
        Test TCP connection to Ableton MCP server.

        Returns:
            True if connection is successful

        Raises:
            MCPConnectionError: If connection fails
        """
        if not self._tcp_socket:
            raise MCPConnectionError("TCP socket not initialized")

        try:
            # Create a new socket for testing
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(self.timeout)
            test_socket.connect((self.host, self.tcp_port))
            test_socket.close()
            return True
        except socket.error as e:
            raise MCPConnectionError(
                f"Cannot connect to Ableton MCP at {self.host}:{self.tcp_port} - {e}"
            )

    def _is_critical_op(self, cmd_type: str) -> bool:
        """Check if command type requires TCP (critical operation)."""
        for critical_prefix in CRITICAL_OPS:
            if cmd_type.startswith(critical_prefix):
                return True
            if cmd_type == critical_prefix:
                return True
        return False

    def send(self, cmd_type: str, params: Optional[dict] = None) -> Optional[dict]:
        """
        Send command with auto-routing.

        Automatically routes to TCP for critical operations (get_*, delete_*, etc.)
        or UDP for high-frequency parameter updates.

        Args:
            cmd_type: Command type (e.g., "get_session_info", "set_track_volume")
            params: Command parameters (default: empty dict)

        Returns:
            Response dict for TCP commands, None for UDP commands
        """
        if self._is_critical_op(cmd_type):
            return self.tcp_command(cmd_type, params)
        else:
            self.udp_command(cmd_type, params)
            return None

    def tcp_command(self, cmd_type: str, params: Optional[dict] = None) -> dict:
        """
        Send command via TCP with retry logic.

        Uses exponential backoff: 0.5s, 1s, 2s delays between retries.

        Args:
            cmd_type: Command type
            params: Command parameters (default: empty dict)

        Returns:
            Response dict from server

        Raises:
            MCPConnectionError: If all retries fail
        """
        if not self._tcp_socket:
            raise MCPConnectionError(
                "TCP socket not initialized. Call connect() first."
            )

        command = {"type": cmd_type, "params": params or {}}
        command_str = json.dumps(command).encode("utf-8")

        backoff_times = [0.5, 1.0, 2.0]
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                # Create new socket for each attempt (TCP is connection-oriented)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.tcp_port))

                try:
                    sock.sendall(command_str)
                    response_data = sock.recv(self.buffer_size)
                    response = json.loads(response_data.decode("utf-8"))
                    return response
                finally:
                    sock.close()

            except (socket.error, json.JSONDecodeError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(backoff_times[attempt])
                    continue

        raise MCPConnectionError(
            f"TCP command '{cmd_type}' failed after {self.max_retries} attempts: {last_error}"
        )

    def udp_command(self, cmd_type: str, params: Optional[dict] = None) -> None:
        """
        Send command via UDP (fire-and-forget).

        No acknowledgment or response expected. Suitable for high-frequency
        parameter updates where occasional packet loss is acceptable.

        Args:
            cmd_type: Command type
            params: Command parameters (default: empty dict)
        """
        if not self._udp_socket:
            raise MCPConnectionError(
                "UDP socket not initialized. Call connect() first."
            )

        command = {"type": cmd_type, "params": params or {}}
        command_str = json.dumps(command).encode("utf-8")

        self._udp_socket.sendto(command_str, (self.host, self.udp_port))


# Convenience function for quick one-off commands
def quick_send(
    cmd_type: str, params: Optional[dict] = None, use_tcp: bool = True
) -> Optional[dict]:
    """
    Send a single command without context manager.

    Args:
        cmd_type: Command type
        params: Command parameters
        use_tcp: If True, use TCP; otherwise use UDP

    Returns:
        Response for TCP commands, None for UDP
    """
    with MCPClient() as client:
        if use_tcp:
            return client.tcp_command(cmd_type, params)
        else:
            client.udp_command(cmd_type, params)
            return None


if __name__ == "__main__":
    # Quick test - verify import works
    print("MCPClient module loaded successfully")
    print(f"Critical operations: {CRITICAL_OPS}")

    # Test connection (requires Ableton Live running)
    try:
        with MCPClient() as client:
            client.verify_connection()
            print("Connection to Ableton MCP verified")
    except MCPConnectionError as e:
        print(f"Connection test skipped (Ableton not running): {e}")
