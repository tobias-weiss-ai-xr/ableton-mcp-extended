"""
Tests for MCP_Server/knowledge/__init__.py — device knowledge base.

Verifies device loading, parameter lookups, and error handling for both
native Ableton devices and (future) third-party plugins.
"""

import json
import os
import sys
import pytest

# Ensure MCP_Server is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "MCP_Server")))

from MCP_Server.knowledge import (
    get_device_knowledge,
    get_available_devices,
    _load_all_devices, # For direct testing of internal cache
)

# Reset cache before each test to ensure fresh load
@pytest.fixture(autouse=True)
def reset_knowledge_cache():
    _load_all_devices.cache_clear()


# ── Test 1: get_device_knowledge("Wavetable") returns correct parameter count ──

def test_get_wavetable_knowledge_parameter_count():
    wavetable = get_device_knowledge("Wavetable")
    assert isinstance(wavetable, dict)
    assert wavetable["name"] == "Wavetable"
    assert "parameters" in wavetable
    # Check for a reasonable number of parameters, e.g., > 10
    assert len(wavetable["parameters"]) > 10


# ── Test 2: get_device_knowledge("Wavetable", "Osc1 Level") returns specific param ──

def test_get_wavetable_osc1_level_parameter():
    param_info = get_device_knowledge("Wavetable", "Osc1 Level")
    assert isinstance(param_info, dict)
    assert param_info["device"] == "Wavetable"
    assert param_info["parameter"]["name"] == "Osc1 Level"
    assert "index" in param_info["parameter"]


# ── Test 3: get_device_knowledge("Nonexistent") returns not-found message ──

def test_get_nonexistent_device_knowledge():
    result = get_device_knowledge("Nonexistent")
    assert isinstance(result, dict)
    assert "error" in result
    assert "not found" in result["error"]


# ── Test 4: get_device_knowledge("Wavetable", "NonexistentParam") returns not-found ──

def test_get_wavetable_nonexistent_parameter():
    result = get_device_knowledge("Wavetable", "NonexistentParam")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Parameter 'NonexistentParam' not found" in result["error"]


# ── Test 5: All 36 devices load without error (iterate knowledge/__init__.py) ──

def test_all_devices_load_without_error():
    devices = _load_all_devices()
    assert len(devices) == 36  # Based on sprint spec: 14+4+6+3+9 = 36
    for device in devices:
        assert isinstance(device, dict)
        assert "name" in device
        assert "class_name" in device
        assert "parameters" in device


# ── Test 6: Total parameter count >= 245 ────────────────────────────────────

def test_total_parameter_count():
    devices = _load_all_devices()
    total_params = sum(len(d.get("parameters", [])) for d in devices)
    assert total_params >= 245


# ── Test 7: File count equals 5 JSON files ──────────────────────────────────

def test_json_file_count():
    devices_dir = os.path.join(os.path.dirname(__file__), "..", "MCP_Server", "knowledge", "devices")
    json_files = [f for f in os.listdir(devices_dir) if f.endswith(".json")]
    assert len(json_files) == 5


# ── Test 8: Query device by partial name match (case-insensitive) ───────────

def test_query_device_partial_name_match():
    # Example: Query "wavetable" should match "Wavetable"
    wavetable = get_device_knowledge("wavetable")
    assert isinstance(wavetable, dict)
    assert wavetable["name"] == "Wavetable"

    # Example: Query "eq eight" should match "EQ Eight"
    eq_eight = get_device_knowledge("eq eight")
    assert isinstance(eq_eight, dict)
    assert eq_eight["name"] == "EQ Eight"


# ── Test 9: All device schemas have required fields ─────────────────────────

def test_device_schemas_have_required_fields():
    devices = _load_all_devices()
    for device in devices:
        assert "name" in device
        assert "class_name" in device
        assert "parameters" in device
        # parameter indices are optional at top level but should be in parameter objects
        for param in device.get("parameters", []):
            assert "name" in param
            assert "index" in param
            assert "range" in param


# ── Test for get_available_devices ──────────────────────────────────────────

def test_get_available_devices():
    available_devices = get_available_devices()
    assert isinstance(available_devices, list)
    assert len(available_devices) == 36
    assert "Wavetable" in available_devices
    assert "EQ Eight" in available_devices
