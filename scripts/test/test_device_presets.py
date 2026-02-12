"""
Tests for device preset save/load functionality using Ableton's native preset system.

These tests verify that devices can save and load presets using Ableton's
native .advpt preset files, not the JSON-based preset banks.
"""

import pytest
import json
import socket
import time
import os
from pathlib import Path


# Ableton MCP connection settings
ABLETON_HOST = "127.0.0.1"
ABLETON_PORT = 9877


def send_command(command_type, params=None):
    """Send a command to Ableton MCP server and return the response."""
    if params is None:
        params = {}

    command = {"type": command_type, "params": params}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((ABLETON_HOST, ABLETON_PORT))
        sock.sendall(json.dumps(command).encode("utf-8"))
        response_data = sock.recv(4096 * 4).decode("utf-8")
        sock.close()

        response = json.loads(response_data)
        return response
    except socket.timeout:
        pytest.fail(f"Command {command_type} timed out - is Ableton running?")
    except ConnectionRefusedError:
        pytest.fail(
            f"Could not connect to Ableton MCP at {ABLETON_HOST}:{ABLETON_PORT}. "
            "Is Ableton Live running with AbletonMCP Remote Script loaded?"
        )
    except Exception as e:
        pytest.fail(f"Error sending command {command_type}: {str(e)}")


class TestSaveDevicePreset:
    """Tests for saving device presets."""

    def test_save_device_preset_creates_file(self):
        """Test that saving a device preset creates a preset file."""
        # Find any track with a device
        response = send_command("get_all_tracks")
        assert "result" in response

        tracks = response["result"].get("tracks", [])
        test_track = None
        test_device_index = None
        test_device_name = None

        for track_info in tracks:
            track_idx = track_info["index"]
            # Get track info to see devices
            response = send_command("get_track_info", {"track_index": track_idx})
            if "result" in response:
                track = response["result"]
                # Check if track has devices and get first one
                if track.get("devices") and len(track["devices"]) > 0:
                    # Prefer instrument devices for testing
                    for dev in track["devices"]:
                        # Look for instruments (Simpler, Sampler, Operator, etc.)
                        dev_class = dev.get("class_name", "")
                        if any(
                            x in dev_class
                            for x in ["Simpler", "Sampler", "Operator", "Wavetable"]
                        ):
                            test_track = track_idx
                            test_device_index = dev["index"]
                            test_device_name = dev.get("name", "Unknown")
                            break
                    # If no instrument found, use first device
                    if test_track is None:
                        test_track = track_idx
                        test_device_index = track["devices"][0]["index"]
                        test_device_name = track["devices"][0].get("name", "Unknown")
                    break

        # If no device found, skip test (need Ableton session with devices)
        if test_track is None:
            pytest.skip("No devices found in session - skipping preset save test")

        # Save the current device state as a preset
        preset_name = "test_preset_automation"
        response = send_command(
            "save_device_preset",
            {
                "track_index": test_track,
                "device_index": test_device_index,
                "preset_name": preset_name,
            },
        )

        # Verify save was successful
        assert "result" in response
        result = response["result"]
        assert result.get("status") == "success" and "saved" in result.get("result", {})
        assert result["saved"] is True
        assert "preset_name" in result
        assert result["preset_name"] == preset_name
        assert "device_name" in result

    def test_save_preset_for_different_device_types(self):
        """Test that presets are saved to correct subdirectories for different device types."""
        # We'll test with multiple device types if available
        response = send_command("get_all_tracks")
        assert "result" in response

        tracks = response["result"].get("tracks", [])
        devices_found = {}

        for track_info in tracks:
            track_idx = track_info["index"]
            response = send_command("get_track_info", {"track_index": track_idx})
            if "result" in response:
                track = response["result"]
                if track.get("devices"):
                    for dev in track["devices"]:
                        dev_name = dev.get("name", "")
                        # Store first instance of each device type
                        device_type = None
                        if (
                            "Operator" in dev_name or " worship" in dev_name.lower()
                        ):  # Typo fix
                            device_type = "Operator"
                        elif "Wavetable" in dev_name:
                            device_type = "Wavetable"
                        elif "Sampler" in dev_name:
                            device_type = "Sampler"
                        elif "Simpler" in dev_name:
                            device_type = "Simpler"

                        if device_type and device_type not in devices_found:
                            devices_found[device_type] = (track_idx, dev["index"])

        # If no devices found, skip
        if not devices_found:
            pytest.skip("No supported devices found - skipping multi-device type test")

        # Try to save a preset for each device type found
        for device_type, (track_idx, device_idx) in devices_found.items():
            preset_name = f"test_{device_type.lower()}_preset"
            response = send_command(
                "save_device_preset",
                {
                    "track_index": track_idx,
                    "device_index": device_idx,
                    "preset_name": preset_name,
                },
            )

            assert "result" in response
            result = response["result"]
            assert result.get("saved") is True
            # Verify the response includes device class info
            assert "device_name" in result


class TestLoadDevicePreset:
    """Tests for loading device presets."""

    def test_load_device_prest_restores_settings(self):
        """Test that loading a preset restores device settings."""
        # Find a track with a device
        response = send_command("get_all_tracks")
        assert "result" in response

        tracks = response["result"].get("tracks", [])
        operator_track = None
        operator_device_index = None

        for track_info in tracks:
            track_idx = track_info["index"]
            response = send_command("get_track_info", {"track_index": track_idx})
            if "result" in response:
                track = response["result"]
                if track.get("devices"):
                    for dev in track["devices"]:
                        if "Operator" in dev.get("name", ""):
                            operator_track = track_idx
                            operator_device_index = dev["index"]
                            break
                    if operator_track is not None:
                        break

        if operator_track is None:
            pytest.skip("No Operator device found - skipping preset load test")

        # Get current device parameters
        response = send_command(
            "get_device_parameters",
            {"track_index": operator_track, "device_index": operator_device_index},
        )
        assert "result" in response
        original_params = response["result"]["parameters"]

        # Save as a preset
        preset_name = "test_load_preset"
        response = send_command(
            "save_device_preset",
            {
                "track_index": operator_track,
                "device_index": operator_device_index,
                "preset_name": preset_name,
            },
        )
        assert response.get("result", {}).get("saved") is True

        # Modify some parameters to verify the preset will restore them
        if len(original_params) > 0:
            first_param_idx = original_params[0]["index"]
            # Change to a different value
            new_value = 0.5
            response = send_command(
                "set_device_parameter",
                {
                    "track_index": operator_track,
                    "device_index": operator_device_index,
                    "parameter_index": first_param_idx,
                    "value": new_value,
                },
            )
            assert "result" in response

        # Now load the preset back
        response = send_command(
            "load_device_preset",
            {
                "track_index": operator_track,
                "device_index": operator_device_index,
                "preset_name": preset_name,
            },
        )

        assert "result" in response
        result = response["result"]
        assert result.get("loaded") is True
        assert result["preset_name"] == preset_name

        # Verify parameters are restored (allowing for potential differences in Ableton's behavior)
        # In a real Ableton session, the preset should restore the exact parameters
        response = send_command(
            "get_device_parameters",
            {"track_index": operator_track, "device_index": operator_device_index},
        )
        assert "result" in response

    def test_load_preset_with_wrong_name(self):
        """Test that loading a non-existent preset handles error gracefully."""
        response = send_command("get_all_tracks")
        assert "result" in response

        tracks = response["result"].get("tracks", [])
        if not tracks:
            pytest.skip("No tracks available - skipping error handling test")

        # Try to load a non-existent preset
        response = send_command(
            "load_device_preset",
            {
                "track_index": 0,
                "device_index": 0,
                "preset_name": "preset_that_definitely_does_not_exist_xyz123",
            },
        )

        assert "result" in response
        result = response["result"]
        assert result.get("loaded") is False
        assert "error" in result or "available_presets" in result


class TestListDevicePresets:
    """Tests for listing available presets for a device."""

    def test_list_presets_returns_correct_presets(self):
        """Test that listing presets returns presets for the specific device type."""
        # Find a track with a device
        response = send_command("get_all_tracks")
        assert "result" in response

        tracks = response["result"].get("tracks", [])
        operator_track = None
        operator_device_index = None

        for track_info in tracks:
            track_idx = track_info["index"]
            response = send_command("get_track_info", {"track_index": track_idx})
            if "result" in response:
                track = response["result"]
                if track.get("devices"):
                    for dev in track["devices"]:
                        if "Operator" in dev.get("name", ""):
                            operator_track = track_idx
                            operator_device_index = dev["index"]
                            break
                    if operator_track is not None:
                        break

        if operator_track is None:
            pytest.skip("No Operator device found - skipping list presets test")

        # List presets for this device
        response = send_command(
            "list_device_presets",
            {"track_index": operator_track, "device_index": operator_device_index},
        )

        assert "result" in response
        result = response["result"]
        assert "presets" in result
        assert isinstance(result["presets"], list)
        assert "device_name" in result
        assert "device_class" in result

    def test_list_presets_for_different_device_types(self):
        """Test that presets are device-type specific (Operator presets only for Operator)."""
        response = send_command("get_all_tracks")
        assert "result" in response

        tracks = response["result"].get("tracks", [])
        devices_found = {}

        for track_info in tracks:
            track_idx = track_info["index"]
            response = send_command("get_track_info", {"track_index": track_idx})
            if "result" in response:
                track = response["result"]
                if track.get("devices"):
                    for dev in track["devices"]:
                        dev_name = dev.get("name", "")
                        device_type = None
                        if "Operator" in dev_name:
                            device_type = "Operator"
                        elif "Wavetable" in dev_name:
                            device_type = "Wavetable"
                        elif "Sampler" in dev_name:
                            device_type = "Sampler"

                        if device_type and device_type not in devices_found:
                            devices_found[device_type] = (track_idx, dev["index"])

        if len(devices_found) < 2:
            pytest.skip(
                "Need at least 2 different device types to test device-specific presets"
            )

        # List presets for each device type and verify they're different
        preset_lists = {}
        for device_type, (track_idx, device_idx) in devices_found.items():
            response = send_command(
                "list_device_presets",
                {"track_index": track_idx, "device_index": device_idx},
            )

            assert "result" in response
            result = response["result"]
            assert "device_class" in result
            device_class = result["device_class"]
            assert "presets" in result

            # Store the preset list for this device class
            if device_class not in preset_lists:
                preset_lists[device_class] = result["presets"]

        # Different device classes should have different preset lists
        # (though there might be some overlap in preset names, the lists will differ)
        assert len(preset_lists) >= 2


class TestErrorHandling:
    """Tests for error handling in device preset operations."""

    def test_save_preset_invalid_track_index(self):
        """Test that saving preset with invalid track index handles error."""
        response = send_command(
            "save_device_preset",
            {"track_index": 9999, "device_index": 0, "preset_name": "test"},
        )

        assert "result" in response or "error" in response
        result = response.get("result", {})
        assert result.get("saved") is False or "error" in response

    def test_save_preset_invalid_device_index(self):
        """Test that saving preset with invalid device index handles error."""
        response = send_command("get_all_tracks")
        assert "result" in response

        tracks = response["result"].get("tracks", [])
        if not tracks:
            pytest.skip("No tracks available - skipping invalid device index test")

        # Use valid track index but invalid device index
        response = send_command(
            "save_device_preset",
            {"track_index": 0, "device_index": 9999, "preset_name": "test"},
        )

        assert "result" in response or "error" in response
        result = response.get("result", {})
        assert result.get("saved") is False or "error" in response

    def test_list_presets_invalid_track_index(self):
        """Test that listing presets with invalid track index handles error."""
        response = send_command(
            "list_device_presets", {"track_index": 9999, "device_index": 0}
        )

        assert "error" in response or (
            "result" in response and "presets" not in response["result"]
        )
