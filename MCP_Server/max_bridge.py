"""
Max Bridge — OSC-based communication between ableton-mcp-extended and Max for Live.

Provides:
    - MaxBridgeClient: optional python-osc based OSC sender with graceful fallback
    - register_max_bridge_tools(): registers MCP tools for the bridge
    - test_max_bridge(): health-check tool that pings the bridge's OSC endpoint

Dependencies:
    - python-osc (optional): `pip install python-osc`
      Without it, all sends are no-ops with a logged warning.

Architecture:
    See docs/max-bridge-architecture.md for full design.
"""

from __future__ import annotations

import logging
import os
import socket
from typing import Any

logger = logging.getLogger("AbletonMCPServer")

# ---------------------------------------------------------------------------
# Optional python-osc import
# ---------------------------------------------------------------------------

_HAS_OSC: bool
try:
    from pythonosc.udp_client import SimpleUDPClient  # type: ignore[import-untyped]

    _HAS_OSC = True
except ImportError:
    SimpleUDPClient = None  # type: ignore[assignment]
    _HAS_OSC = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_OSC_PORT = 9000
"""Default UDP port for the Max bridge OSC sender."""

DEFAULT_OSC_HOST = "127.0.0.1"
"""Default host – localhost only for security."""

DEFAULT_PING_TIMEOUT = 2.0
"""Seconds to wait for a ping response before declaring the bridge unreachable."""

# OSC address allowlist — addresses not in this set are silently rejected
# before any network activity.
ALLOWED_OSC_ADDRESSES: frozenset[str] = frozenset({
    "/max/ping",
    "/max/device/load",
    "/max/device/info",
    "/max/device/message",
    "/max/device/parameter",
    "/max/open",
    "/max/presentation",
    "/max/bang",
})
"""Allowlist of OSC addresses that the bridge is permitted to send."""


# ---------------------------------------------------------------------------
# MaxBridgeClient
# ---------------------------------------------------------------------------


class MaxBridgeClient:
    """OSC client for sending messages to the Max bridge patcher.

    This client sends OSC messages via UDP to ``mcp_bridge.maxpat`` running
    inside Ableton Live.  If python-osc is not installed every method degrades
    gracefully: sends become no-ops and :meth:`ping` returns ``False``.

    Parameters
    ----------
    host:
        OSC target host (default 127.0.0.1).
    port:
        OSC target port (default 9000, overridable via ``MAX_BRIDGE_PORT``
        environment variable).
    """

    def __init__(self, host: str = DEFAULT_OSC_HOST, port: int | None = None) -> None:
        self.host = host

        # Resolve port: explicit arg > env var > default
        if port is not None:
            self.port = port
        else:
            env_port = os.environ.get("MAX_BRIDGE_PORT")
            self.port = int(env_port) if env_port is not None else DEFAULT_OSC_PORT

        self._validate_port(self.port)

        self._client: SimpleUDPClient | None = None  # type: ignore[type-arg]
        if _HAS_OSC and SimpleUDPClient is not None:
            try:
                self._client = SimpleUDPClient(self.host, self.port)
            except Exception as exc:
                logger.warning("Failed to create OSC client: %s", exc)
        else:
            logger.info(
                "python-osc not available. Max Bridge OSC sends will be no-ops. "
                "Install: pip install python-osc"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def available(self) -> bool:
        """``True`` if python-osc is installed and the UDP client is ready."""
        return self._client is not None

    def send_osc(self, address: str, *args: Any) -> bool:
        """Send an OSC message to the Max bridge patcher.

        Parameters
        ----------
        address:
            OSC address pattern (e.g. ``/max/ping``).
        *args:
            OSC arguments (typed per OSC spec).

        Returns
        -------
        ``True`` if the message was sent, ``False`` otherwise.
        """
        if not self.available:
            logger.debug(
                "OSC send skipped (python-osc not available): %s %s", address, args
            )
            return False

        if address not in ALLOWED_OSC_ADDRESSES:
            logger.debug("OSC address not in allowlist, dropping: %s", address)
            return False

        try:
            self._client.send_message(address, list(args))
            logger.debug("OSC sent: %s %s", address, args)
            return True
        except Exception as exc:
            logger.warning("OSC send failed for %s: %s", address, exc)
            return False

    def ping(self, timeout: float = DEFAULT_PING_TIMEOUT) -> bool:
        """Check if the Max bridge OSC endpoint is reachable.

        Sends a ``/max/ping`` message.  Because python-osc is a pure UDP
        sender (fire-and-forget) the **real** reachability test requires
        reading a /pong response back on a listener socket.

        For the prototype we use a socket-level probe: try to open a UDP
        socket to the target to verify the endpoint exists.

        Parameters
        ----------
        timeout:
            Socket timeout in seconds.

        Returns
        -------
        ``True`` if the port appears reachable, ``False`` otherwise.
        """
        if not self.available:
            return False

        # Quick socket-level check
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(timeout)
                sock.connect((self.host, self.port))
                # Send a zero-length datagram as a probe; connect() won't
                # fail on UDP but it ensures the address is valid.
                sock.sendall(b"")
                return True
        except (OSError, socket.gaierror) as exc:
            logger.debug("Max bridge ping failed: %s", exc)
            return False

    def send_bang(self, track_index: int, device_index: int) -> bool:
        """Send a bang to a Max device's inlet 0.

        Convenience wrapper around ``/max/bang``.
        """
        return self.send_osc("/max/bang", track_index, device_index)

    def send_message(
        self, track_index: int, device_index: int, message: str
    ) -> bool:
        """Send an arbitrary message string to a Max device inlet.

        Convenience wrapper around ``/max/device/message``.
        """
        return self.send_osc("/max/device/message", track_index, device_index, message)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_port(port: int) -> None:
        if not (1024 <= port <= 65535):
            raise ValueError(
                f"Max bridge port must be in range 1024-65535, got {port}"
            )


# ---------------------------------------------------------------------------
# MCP Tool Registration
# ---------------------------------------------------------------------------


def register_max_bridge_tools(mcp: Any, get_ableton_connection: Any) -> None:
    """Register Max Bridge MCP tools.

    This function follows the same registration pattern as
    ``register_mixer_tools``, ``register_advanced_tools``, etc.

    Parameters
    ----------
    mcp:
        The ``FastMCP`` server instance.
    get_ableton_connection:
        Callable that returns the current ``AbletonConnection``.
    """
    from mcp.server.fastmcp import Context

    # ---------- test_max_bridge -------------------------------------------------

    @mcp.tool()
    def test_max_bridge(ctx: Context, port: int | None = None) -> str:
        """
        Test connectivity to the Max for Live bridge OSC endpoint.

        Sends a ping to the Max bridge patcher (``mcp_bridge.maxpat``) via
        OSC on the configured port (default 9000).  Returns a human-readable
        reachability report.

        Parameters
        ----------
        port:
            Optional OSC port override.  If not provided, uses the default
            port (9000) or the value of the ``MAX_BRIDGE_PORT`` environment
            variable.

        Returns
        -------
        A human-readable string describing the bridge status.
        """
        client = MaxBridgeClient(port=port or DEFAULT_OSC_PORT)

        if not _HAS_OSC:
            return (
                "Max Bridge is not reachable: python-osc is not installed.\n"
                "Install it with: pip install python-osc\n\n"
                "The Max Bridge provides OSC-based communication between\n"
                "ableton-mcp-extended and Max for Live devices. Without\n"
                "python-osc, all Max Bridge features are unavailable."
            )

        bridge_ok = client.ping()

        lines: list[str] = [
            "=== Max Bridge Connectivity Report ===",
            f"OSC endpoint: {client.host}:{client.port}",
            f"python-osc installed: {'✓' if _HAS_OSC else '✗'}",
            f"Client ready: {'✓' if client.available else '✗'}",
            "",
        ]

        if bridge_ok:
            lines.append("Bridge is REACHABLE ✓")
            lines.append("")
            lines.append("Next steps:")
            lines.append("  1. Load mcp_bridge.maxpat on a track in Ableton Live")
            lines.append("  2. Use send_max_message etc. to control Max devices")
        else:
            lines.append("Bridge is NOT REACHABLE ✗")
            lines.append("")
            lines.append("Troubleshooting:")
            lines.append(
                "  • Is Ableton Live running with mcp_bridge.maxpat loaded?"
            )
            lines.append(f"  • Is port {client.port} free and bound to 127.0.0.1?")
            lines.append("  • Check for firewall rules blocking UDP")
            lines.append("  • Set a different port: export MAX_BRIDGE_PORT=<port>")

        return "\n".join(lines)
