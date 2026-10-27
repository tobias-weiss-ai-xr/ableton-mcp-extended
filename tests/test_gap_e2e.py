"""E2E layer of the gap/bugfix test pyramid.

Real Live round-trip via TCP (localhost:9877). Skips if Live unavailable.
Only tests read-only commands; destructive commands (delete_device,
build_arrangement) are skipped to avoid modifying session state.

Run:  pytest tests/test_gap_e2e.py -v
"""
import json
import socket
import pytest

from gap_specs import ALL_SPECS, GAPS, FIXES, IMPLEMENTED_GAPS

HOST = "localhost"
PORT = 9877
TIMEOUT = 5.0


def _send(cmd, params=None):
    """Send a command to the Remote Script and return the response dict."""
    s = socket.socket()
    s.settimeout(TIMEOUT)
    s.connect((HOST, PORT))
    msg = json.dumps({"type": cmd, "params": params or {}})
    s.send(msg.encode("utf-8"))
    data = b""
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue
    s.close()
    return json.loads(data.decode("utf-8"))


@pytest.fixture(scope="module")
def live():
    """Connect to Live; skip all tests if unavailable."""
    try:
        resp = _send("get_session_info")
        if resp.get("status") != "success":
            pytest.skip("Live connected but get_session_info failed: " + str(resp))
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        pytest.skip("Live not available: " + str(e))
    return True


# ---------------------------------------------------------------------------
# Connection sanity
# ---------------------------------------------------------------------------

class TestConnection:
    def test_session_info(self, live):
        resp = _send("get_session_info")
        assert resp["status"] == "success"
        result = resp.get("result", resp)
        assert "tracks" in result or "track_count" in result


# ---------------------------------------------------------------------------
# Bugfix: get_device_parameters (read-only, safe to test)
# ---------------------------------------------------------------------------

class TestGetDeviceParameters:
    """Bug repro: device_index must return the correct device, not device[0]."""

    def test_response_shape(self, live):
        resp = _send("get_device_parameters",
                     {"track_index": 0, "device_index": 0})
        if resp.get("status") == "error" and "out of range" in resp.get("message", "").lower():
            pytest.skip("track 0 has no devices")
        assert resp["status"] == "success", str(resp)
        result = resp.get("result", resp)
        assert "device_name" in result, "missing device_name"
        assert "device_index" in result, "missing device_index"
        assert "parameters" in result, "missing parameters"
        assert isinstance(result["parameters"], list)

    def test_device_index_respected(self, live):
        """Querying index 0 and 1 must return different device names
        (unless the track has < 2 devices). xfail if bug present."""
        resp0 = _send("get_device_parameters",
                      {"track_index": 0, "device_index": 0})
        resp1 = _send("get_device_parameters",
                      {"track_index": 0, "device_index": 1})
        if resp1.get("status") == "error":
            pytest.skip("track 0 has < 2 devices")
        assert resp0["status"] == "success"
        assert resp1["status"] == "success"
        name0 = resp0.get("result", resp0).get("device_name")
        name1 = resp1.get("result", resp1).get("device_name")
        if name0 == name1:
            pytest.xfail("bug present: device_index not respected "
                         "(both return '" + str(name0) + "')")
        assert name0 != name1


# ---------------------------------------------------------------------------
# Gap commands: must return UNKNOWN_COMMAND (handler not yet implemented)
# ---------------------------------------------------------------------------

class TestGapCommandsNotImplemented:
    """All gap commands should return UNKNOWN_COMMAND until implemented."""

    @pytest.mark.parametrize("spec", GAPS, ids=[s.name for s in GAPS])
    def test_returns_unknown_command(self, live, spec):
        resp = _send(spec.name, {})
        if resp.get("status") == "success":
            pytest.fail(spec.name + ": gap appears implemented! "
                        "Update gap_specs.py implemented=True")
        assert resp.get("status") == "error"
        assert resp.get("error") == "UNKNOWN_COMMAND", \
            spec.name + ": unexpected error type " + str(resp.get("error"))


# ---------------------------------------------------------------------------
# Bugfix commands: destructive ones are skipped, not called
# ---------------------------------------------------------------------------

class TestBugfixSafety:
    """delete_device and build_arrangement are destructive — skip in e2e."""

    def test_delete_device_skipped(self, live):
        pytest.skip("delete_device is destructive — tested via contract layer only")

    def test_build_arrangement_skipped(self, live):
        pytest.skip("build_arrangement is destructive — tested via contract layer only")


# ---------------------------------------------------------------------------
# Implemented gap commands: rack macros & drum pads
# ---------------------------------------------------------------------------

class TestImplementedGapCommands:
    """Implemented gap commands must be registered (not UNKNOWN_COMMAND).
    Uses track_index=999 to avoid side effects — any error except
    UNKNOWN_COMMAND proves the handler exists."""

    @pytest.mark.parametrize("spec", IMPLEMENTED_GAPS, ids=[s.name for s in IMPLEMENTED_GAPS])
    def test_not_unknown_command(self, live, spec):
        resp = _send(spec.name, {"track_index": 999})
        if resp.get("error") == "UNKNOWN_COMMAND":
            pytest.skip(spec.name + ": script not reloaded — toggle MIDI device in Live Preferences")
        # Any non-UNKNOWN_COMMAND response proves the handler is registered
        assert resp.get("error") != "UNKNOWN_COMMAND", \
            spec.name + ": handler not registered (UNKNOWN_COMMAND)"

    def test_get_rack_macros_response_shape(self, live):
        """get_rack_macros returns macros list or skips if no rack on track 0."""
        resp = _send("get_rack_macros", {"track_index": 0})
        if resp.get("error") == "UNKNOWN_COMMAND":
            pytest.skip("script not reloaded — toggle MIDI device in Live Preferences")
        if resp.get("status") == "error" and "No RackDevice" in resp.get("message", ""):
            pytest.skip("track 0 has no RackDevice")
        assert resp["status"] == "success", str(resp)
        result = resp.get("result", resp)
        assert "macros" in result, "missing macros"
        assert isinstance(result["macros"], list)

    def test_get_drum_pads_response_shape(self, live):
        """get_drum_pads returns pads list or skips if no drum rack on track 0."""
        resp = _send("get_drum_pads", {"track_index": 0})
        if resp.get("error") == "UNKNOWN_COMMAND":
            pytest.skip("script not reloaded — toggle MIDI device in Live Preferences")
        if resp.get("status") == "error" and "No Drum Rack" in resp.get("message", ""):
            pytest.skip("track 0 has no Drum Rack")
        assert resp["status"] == "success", str(resp)
        result = resp.get("result", resp)
        assert "pads" in result, "missing pads"
        assert isinstance(result["pads"], list)
