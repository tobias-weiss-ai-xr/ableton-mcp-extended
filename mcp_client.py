"""
MCP Client wrappers for Ableton Live MCP API.

Classes:
    MCPClientTCP: TCP client for request/response commands (port 9877)
    MCPClientUDP: UDP client for fire-and-forget commands (port 9878)

Usage:
    from mcp_client import MCPClientTCP, MCPClientUDP

    tcp_client = MCPClientTCP()
    response = tcp_client.send_command_tcp("get_session_info", {})

    udp_client = MCPClientUDP()
    udp_client.send_command_udp("set_master_volume", {"volume": 0.8})  # No return
"""

import socket
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MCPClientTCP:
    """
    TCP client for Ableton MCP API (port 9877).

    Used for request/response commands where a response is required.
    Commands like get_*, create_*, delete_*, quantize_* run over TCP.
    """

    def __init__(self, host: str = "localhost", port: int = 9877, max_retries: int = 3):
        """
        Initialize TCP client.

        Args:
            host: MCP server host (default: localhost)
            port: MCP server TCP port (default: 9877)
            max_retries: Number of retry attempts on connection failure (default: 3)

        Note:
            Default ports from AGENTS.md: TCP 9877, UDP 9878
        """
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.timeout = 2  # Connection timeout in seconds

    def send_command(self, command_type: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a TCP command and receive response.

        Wrapper around send_command_tcp for compatibility.

        Args:
            command_type: MCP command type (e.g., "get_session_info")
            params: Command parameters dictionary

        Returns:
            Parsed JSON response or None on failure

        Raises:
            socket.error: After all retry attempts exhausted
            json.JSONDecodeError: If response is not valid JSON
        """
        return self.send_command_tcp(command_type, params)

    def send_command_tcp(self, command_type: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a TCP command and receive response.

        Implements connection recovery with exponential backoff.

        Args:
            command_type: MCP command type (e.g., "get_session_info")
            params: Command parameters dictionary

        Returns:
            Parsed JSON response or None on failure

        Raises:
            socket.error: After all retry attempts exhausted
            json.JSONDecodeError: If response is not valid JSON

        Note:
            Pattern from scripts/live_dj_performance.py:16-30:
            - socket.create_connection with timeout
            - send json.dumps() + newline
            - recv() with large buffer (65536)
            - json.loads() for response
        """
        retry_count = 0
        last_error = None

        while retry_count < self.max_retries:
            try:
                # Create connection with timeout
                sock = socket.create_connection((self.host, self.port), timeout=self.timeout)

                # Prepare message
                message = json.dumps({"type": command_type, "params": params}) + "\n"
                logger.debug(f"TCP send: {command_type}")

                # Send message
                sock.sendall(message.encode())

                # Receive response (large buffer for big responses)
                response_data = sock.recv(65536).decode()
                sock.close()

                # Parse response
                result = json.loads(response_data)
                logger.debug(f"TCP recv: {result}")
                return result

            except socket.timeout as e:
                retry_count += 1
                last_error = e
                logger.warning(f"TCP timeout on attempt {retry_count}/{self.max_retries}: {e}")
                # Exponential backoff: 0.1s, 0.4s, 1.6s
                import time
                time.sleep(0.1 * (4 ** (retry_count - 1)))

            except socket.error as e:
                retry_count += 1
                last_error = e
                logger.warning(f"TCP error on attempt {retry_count}/{self.max_retries}: {e}")
                # Exponential backoff
                import time
                time.sleep(0.1 * (4 ** (retry_count - 1)))

            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode TCP response: {e}")
                logger.error(f"Response data: {response_data[:200]}")
                raise  # Don't retry JSON decode errors

        # All retries exhausted
        error_msg = f"TCP connection failed after {self.max_retries} retries. Last error: {last_error}"
        logger.error(error_msg)
        raise socket.error(error_msg)


class MCPClientUDP:
    """
    UDP client for Ableton MCP API (port 9878).

    Used for fire-and-forget commands where no response is expected.
    Low-latency parameter updates: set_device_parameter, set_track_volume, etc.
    """

    def __init__(self, host: str = "localhost", port: int = 9878):
        """
        Initialize UDP client.

        Args:
            host: MCP server host (default: localhost)
            port: MCP server UDP port (default: 9878)

        Note:
            Default ports from AGENTS.md: TCP 9877, UDP 9878
        """
        self.host = host
        self.port = port

    def send_command(self, command_type: str, params: Dict[str, Any]) -> None:
        """
        Send a UDP command (fire-and-forget).

        Wrapper around send_command_udp for compatibility.

        Args:
            command_type: MCP command type (e.g., "set_master_volume")
            params: Command parameters dictionary

        Returns:
            None (fire-and-forget, no response)

        Note:
            UDP commands from AGENTS.md:28-29 (only 10 allowed):
            - set_device_parameter
            - set_track_volume
            - set_track_pan
            - set_track_mute
            - set_track_solo
            - set_track_arm
            - set_master_volume
            - set_send_amount
            - fire_clip
            - set_clip_launch_mode
        """
        self.send_command_udp(command_type, params)

    def send_command_udp(self, command_type: str, params: Dict[str, Any]) -> None:
        """
        Send a UDP command (fire-and-forget).

        Args:
            command_type: MCP command type (e.g., "set_master_volume")
            params: Command parameters dictionary

        Returns:
            None (fire-and-forget, no response)

        Note:
            Pattern from scripts/live_dj_performance.py:26-30:
            - socket.socket(AF_INET, SOCK_DGRAM)
            - sendto() with json.dumps() + newline
            - No recv() (immediate return)
            - close() immediately
        """
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Prepare message
            message = json.dumps({"type": command_type, "params": params}) + "\n"
            logger.debug(f"UDP send: {command_type}")

            # Send message (no response expected)
            sock.sendto(message.encode(), (self.host, self.port))
            sock.close()

            logger.debug(f"UDP sent {command_type} (fire-and-forget)")

        except socket.error as e:
            logger.warning(f"UDP send failed (fire-and-forget, continuing): {e}")

        except Exception as e:
            logger.error(f"Unexpected UDP error: {e}")
            # Continue even on error - UDP is best-effort


# Backward compatibility aliases
ClientTCP = MCPClientTCP
ClientUDP = MCPClientUDP