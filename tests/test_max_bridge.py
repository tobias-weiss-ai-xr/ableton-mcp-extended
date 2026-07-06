"""
Tests for MCP_Server/max_bridge.py — OSC-based communication with Max for Live.

Verifies MaxBridgeClient functionality, graceful degradation without python-osc,
address allowlisting, port validation, and tool registration.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure MCP_Server is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "MCP_Server")))

from MCP_Server.max_bridge import (
    MaxBridgeClient,
    ALLOWED_OSC_ADDRESSES,
    DEFAULT_OSC_PORT,
    register_max_bridge_tools,
)


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_simple_udp_client():
    """Mocks the pythonosc.udp_client.SimpleUDPClient class."""
    with patch(
        "MCP_Server.max_bridge.SimpleUDPClient", autospec=True
    ) as mock_client:
        yield mock_client


@pytest.fixture
def mock_no_osc():
    """Simulates python-osc not being installed."""
    with patch.dict(sys.modules, {"pythonosc.udp_client": None}):
        # Force a reload of the module to pick up the change
        import importlib
        import MCP_Server.max_bridge

        importlib.reload(MCP_Server.max_bridge)
        yield
        # Clean up: reload original module
        importlib.reload(MCP_Server.max_bridge)


# ── Test 1: MaxBridgeClient created without python-osc (graceful fallback) ──


def test_client_without_python_osc_is_unavailable(mock_no_osc):
    client = MaxBridgeClient()
    assert not client.available
    # Sending should be a no-op
    assert not client.send_osc("/max/ping")


# ── Test 2: MaxBridgeClient with mocked python-osc sends correct OSC message ──


def test_client_sends_correct_osc_message(mock_simple_udp_client):
    client = MaxBridgeClient()
    assert client.available
    mock_send_message = mock_simple_udp_client.return_value.send_message

    client.send_osc("/max/ping", 1, "test")
    mock_send_message.assert_called_once_with("/max/ping", [1, "test"])


# ── Test 3: Address allowlist rejects unauthorized addresses ────────────────


def test_send_osc_rejects_unauthorized_address(mock_simple_udp_client):
    client = MaxBridgeClient()
    assert client.available
    mock_send_message = mock_simple_udp_client.return_value.send_message

    # Test an address not in ALLOWED_OSC_ADDRESSES
    assert not client.send_osc("/max/unauthorized")
    mock_send_message.assert_not_called()

    # Test an allowed address
    assert client.send_osc("/max/ping")
    mock_send_message.assert_called_once()


# ── Test 4: Port validation rejects privileged ports (<1024) ───────────────


def test_port_validation_rejects_privileged_ports():
    with pytest.raises(ValueError, match="port must be in range 1024-65535"):
        MaxBridgeClient(port=80)
    with pytest.raises(ValueError, match="port must be in range 1024-65535"):
        MaxBridgeClient(port=1000)


def test_port_validation_accepts_valid_ports():
    client = MaxBridgeClient(port=9001)  # No error should be raised
    assert client.port == 9001


# ── Test 5: `test_max_bridge` tool registered (check module-level function exists) ──


def test_test_max_bridge_tool_exists():
    # This test verifies that the `test_max_bridge` function is present
    # within the module, as it would be registered by `register_max_bridge_tools`.
    from MCP_Server.max_bridge import test_max_bridge
    assert callable(test_max_bridge)


# ── Test 6: Register function signature matches expected pattern ────────────


def test_register_max_bridge_tools_signature():
    import inspect

    assert inspect.isfunction(register_max_bridge_tools)
    sig = inspect.signature(register_max_bridge_tools)
    assert "mcp" in sig.parameters
    assert "get_ableton_connection" in sig.parameters


# ── Test 7: OSC address construction works with various args ────────────────


def test_send_osc_with_various_args(mock_simple_udp_client):
    client = MaxBridgeClient()
    mock_send_message = mock_simple_udp_client.return_value.send_message

    # Test sending bang
    client.send_bang(0, 1)
    mock_send_message.assert_called_with("/max/bang", [0, 1])
    mock_send_message.reset_mock()

    # Test sending message
    client.send_message(2, 3, "some_message")
    mock_send_message.assert_called_with("/max/device/message", [2, 3, "some_message"])
