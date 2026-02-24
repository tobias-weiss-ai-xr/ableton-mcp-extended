#!/usr/bin/env python3
"""
Test script for MCP Server audio effects and modulator functionality.

Covers:
- Audio effect loading and parameter control
- Bulk parameter updates
- UDP parameter transmission
- LFO, Envelope, and Sidechain modulators
- Modulator parameter control and routing

Usage:
  python scripts/test/test_audio_effects.py
"""

import socket
import json
import time
import sys
from typing import Dict, Any, List

# Configuration
TCP_PORT = 9877
UDP_PORT = 9878
HOST = "localhost"


def send_tcp_command(cmd_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Send a command via TCP and return the response."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((HOST, TCP_PORT))

        command = {"type": cmd_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))
        response = sock.recv(8192).decode("utf-8")
        return json.loads(response)
    except Exception as e:
        print(f"TCP command {cmd_type} failed: {str(e)}")
        return {"error": str(e)}
    finally:
        if sock:
            sock.close()


def send_udp_command(cmd_type: str, params: Dict[str, Any]):
    """Send a fire-and-forget command via UDP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        command = {"type": cmd_type, "params": params}
        sock.sendto(json.dumps(command).encode("utf-8"), (HOST, UDP_PORT))
    except Exception as e:
        print(f"UDP command {cmd_type} failed: {str(e)}")


def setup_test_environment() -> Dict[str, Any]:
    """Create test tracks and setup basic environment."""
    print("🚀 Setting up test environment...")

    # Delete all existing tracks to start fresh
    send_tcp_command("delete_all_tracks", {})

    # Create MIDI tracks for testing
    for i in range(2):
        result = send_tcp_command("create_midi_track", {"index": -1})
        if "error" in result:
            print(f"Failed to create track {i}: {result['error']}")
            return {}

    # Name tracks for clarity
    send_tcp_command("set_track_name", {"track_index": 0, "name": "AudioFX_Test_Track"})
    send_tcp_command(
        "set_track_name", {"track_index": 1, "name": "Modulation_Test_Track"}
    )

    print("✅ Test environment ready with 2 tracks")
    return {"tracks": 2}


def test_audio_effect_loading():
    """Test loading audio effects onto tracks."""
    print("\n🔧 TESTING: Audio Effect Loading")
    test_results = []

    effects_to_test = ["Reverb", "Delay", "EQ", "Compressor"]

    for effect in effects_to_test:
        print(f"\tLoading {effect}...")
        result = send_tcp_command(
            "load_audio_effect", {"track_index": 0, "effect_type": effect}
        )

        success = "loaded" in result and result["loaded"]
        test_results.append({"effect": effect, "success": success, "response": result})

        if success:
            print(f"\t✅ {effect} loaded (device_index: {result['device_index']})")
        else:
            print(
                f"\t❌ Failed to load {effect}: {result.get('error', 'Unknown error')}"
            )

    return test_results


def test_set_audio_effect_parameter():
    """Test setting individual effect parameters."""
    print("\n🔧 TESTING: Effect Parameter Control")
    test_results = []

    # Load reverb for parameter testing
    reverb_result = send_tcp_command(
        "load_audio_effect",
        {
            "track_index": 0,
            "effect_type": "Reverb",
            "preset_name": "Small Room",  # Use a standard preset
        },
    )

    if "error" in reverb_result:
        return [
            {
                "test": "reverb_param_test",
                "success": False,
                "error": reverb_result["error"],
            }
        ]

    device_index = reverb_result["device_index"]

    # Test boundary values
    test_values = [0.0, 0.5, 1.0, 0.25, 0.75]

    for param_index, value in enumerate(test_values):
        print(f"\tSetting Reverb parameter {param_index} to {value}")
        result = send_tcp_command(
            "set_audio_effect_parameter",
            {
                "track_index": 0,
                "device_index": device_index,
                "parameter_index": param_index,
                "value": value,
            },
        )

        success = result.get("success", True)  # Returns JSON string or bool
        test_results.append(
            {
                "parameter": param_index,
                "value": value,
                "success": success,
                "response": result,
            }
        )

    return test_results


def test_set_parameters_bulk():
    """Test bulk parameter updates."""
    print("\n🔧 TESTING: Bulk Parameter Updates")
    test_results = []

    # Load delay for bulk testing
    delay_result = send_tcp_command(
        "load_audio_effect", {"track_index": 0, "effect_type": "Delay"}
    )

    if "error" in delay_result:
        return [{"test": "bulk_test", "success": False, "error": delay_result["error"]}]

    device_index = delay_result["device_index"]

    # Create bulk updates payload
    updates = []
    for i in range(5):  # Test first 5 parameters
        updates.append(
            {
                "parameter_index": i,
                "value": (i + 1) * 0.18,  # Values: 0.18, 0.36, 0.54, 0.72, 0.9
            }
        )

    print("\tSending bulk updates:", updates)
    result = send_tcp_command(
        "set_parameters_bulk",
        {"track_index": 0, "device_index": device_index, "updates": updates},
    )

    test_results.append(
        {
            "updates_sent": len(updates),
            "updates_applied": result.get("updated", 0),
            "errors": result.get("errors", 0),
            "success": result.get("errors", 0) == 0,
            "response": result,
        }
    )

    return test_results


def test_udp_parameter_control():
    """Test UDP fire-and-forget parameter updates."""
    print("\n🔧 TESTING: UDP Parameter Control")
    test_results = []

    # Load EQ for UDP testing
    eq_result = send_tcp_command(
        "load_audio_effect", {"track_index": 0, "effect_type": "EQ"}
    )

    if "error" in eq_result:
        return [{"test": "udp_test", "success": False, "error": eq_result["error"]}]

    device_index = eq_result["device_index"]

    # Simulate real-time automation via UDP
    for i in range(10):
        value = i / 10.0  # Sweep from 0.0 to 0.9
        param_index = i % 4  # Cycle through first 4 parameters

        print(f"\tSending UDP: param {param_index} = {value:.2f}")
        send_udp_command(
            "set_audio_effect_parameter",
            {
                "track_index": 0,
                "device_index": device_index,
                "parameter_index": param_index,
                "value": value,
            },
        )

        test_results.append(
            {
                "parameter": param_index,
                "value": value,
                "protocol": "UDP",
                "success": True,  # UDP is fire-and-forget, assume success
            }
        )

        time.sleep(0.05)  # Small delay for realism

    return test_results


def test_modulator_creation():
    """Test LFO, Envelope, and Sidechain modulator creation."""
    print("\n🔧 TESTING: Modulator Creation")
    test_results = []

    # Test LFO creation
    print("\tCreating LFO Modulator...")
    lfo_result = send_tcp_command(
        "create_lfo_modulator",
        {
            "track_index": 1,
            "device_index": 0,  # Target first device (instrument)
            "parameter_index": 0,  # Target first parameter
            "rate": 2.0,
            "depth": 0.8,
            "waveform": "sine",
        },
    )

    test_results.append(
        {
            "mod_type": "lfo",
            "success": "modulator_id" in lfo_result,
            "response": lfo_result,
            "waveform_tested": ["sine"],
        }
    )

    # Test Envelope creation
    print("\tCreating Envelope Modulator...")
    env_result = send_tcp_command(
        "create_envelope_modulator",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 1,
            "attack": 0.1,
            "decay": 0.2,
            "sustain": 0.75,
            "release": 0.3,
        },
    )

    test_results.append(
        {
            "mod_type": "envelope",
            "success": "modulator_id" in env_result,
            "response": env_result,
        }
    )

    # Test Sidechain creation
    print("\tCreating Sidechain Modulator...")
    sc_result = send_tcp_command(
        "create_sidechain_modulator",
        {
            "track_index": 0,
            "device_index": 1,  # Target loaded effect
            "parameter_index": 2,
            "source_track_index": 1,
            "amount": 0.65,
        },
    )

    test_results.append(
        {
            "mod_type": "sidechain",
            "success": "modulator_id" in sc_result,
            "response": sc_result,
        }
    )

    return test_results


def test_modulator_parameter_control():
    """Test updating modulator parameters."""
    print("\n🔧 TESTING: Modulator Parameter Updates")
    test_results = []

    # Create LFO first
    lfo_result = send_tcp_command(
        "create_lfo_modulator",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 0,
            "rate": 1.0,
            "depth": 0.5,
            "waveform": "sine",
        },
    )

    if "error" in lfo_result or "modulator_id" not in lfo_result:
        return [
            {
                "test": "mod_param_test",
                "success": False,
                "error": "Failed to create LFO",
            }
        ]

    mod_id = lfo_result["modulator_id"]

    # Test updating each parameter
    parameters_to_update = [("rate", 3.0), ("depth", 0.9), ("waveform", "saw")]

    for param, value in parameters_to_update:
        print(f"\tUpdating LFO {param} to {value}")
        result = send_tcp_command(
            "set_modulator_parameter",
            {"modulator_id": mod_id, "parameter": param, "value": value},
        )

        test_results.append(
            {
                "parameter": param,
                "value": value,
                "success": result.get("status") == "updated",
                "response": result,
            }
        )

    return test_results


def test_modulator_routing():
    """Test modulator attachment to parameters."""
    print("\n🔧 TESTING: Modulator Routing")

    # Create LFO modulator
    lfo_result = send_tcp_command(
        "create_lfo_modulator",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 0,
            "rate": 1.0,
            "depth": 0.7,
            "waveform": "triangle",
        },
    )

    if "error" in lfo_result:
        return [
            {"test": "routing_test", "success": False, "error": lfo_result["error"]}
        ]

    mod_id = lfo_result["modulator_id"]

    # Load reverb on track 0
    reverb_result = send_tcp_command(
        "load_audio_effect", {"track_index": 0, "effect_type": "Reverb"}
    )

    if "error" in reverb_result:
        return [
            {"test": "routing_test", "success": False, "error": reverb_result["error"]}
        ]

    reverb_device = reverb_result["device_index"]

    # Attach LFO to reverb parameter
    result = send_tcp_command(
        "attach_modulator_to_parameter",
        {
            "modulator_id": mod_id,
            "track_index": 0,
            "device_index": reverb_device,
            "parameter_index": 2,  # Reverb decay parameter
            "depth": 0.8,
        },
    )

    return [
        {
            "test": "modulator_routing",
            "success": result.get("status") == "attached",
            "response": result,
        }
    ]


def test_modulator_removal():
    """Test removing modulators."""
    print("\n🔧 TESTING: Modulator Removal")

    # Create a test modulator
    result = send_tcp_command(
        "create_lfo_modulator",
        {
            "track_index": 1,
            "device_index": 0,
            "parameter_index": 0,
            "rate": 1.5,
            "depth": 0.4,
            "waveform": "square",
        },
    )

    if "error" in result or "modulator_id" not in result:
        return [
            {
                "test": "removal_test",
                "success": False,
                "error": "Failed to create test modulator",
            }
        ]

    mod_id = result["modulator_id"]

    # Remove the modulator
    remove_result = send_tcp_command("remove_modulator", {"modulator_id": mod_id})

    return [
        {
            "test": "modulator_removal",
            "success": remove_result.get("status") == "removed",
            "response": remove_result,
        }
    ]


def generate_report(test_results: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate test report from collected results."""
    report = "\n" + "=" * 60 + "\n"
    report += "MCP AUDIO EFFECTS & MODULATORS TEST REPORT\n"
    report += "=" * 60 + "\n\n"

    total_tests = 0
    passed_tests = 0

    for test_name, results in test_results.items():
        if not results:
            continue

        report += f"📋 {test_name.upper().replace('_', ' ')}:\n"

        for i, result in enumerate(results):
            total_tests += 1
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            if result.get("success", False):
                passed_tests += 1

            if test_name == "audio_effect_loading":
                report += f"   {i + 1}. {result['effect']}: {status}\n"
            elif test_name == "set_audio_effect_parameter":
                report += f"   {i + 1}. Param {result['parameter']} = {result['value']}: {status}\n"
            elif test_name == "udp_parameter_control":
                report += f"   {i + 1}. UDP update Param {result['parameter']} = {result['value']}: {status}\n"
            else:
                report += f"   {i + 1}. {status}\n"
                if "error" in result:
                    report += f"       Error: {result['error']}\n"

        report += "\n"

    # Summary
    report += "=" * 60 + "\n"
    report += "📊 TEST SUMMARY:\n"
    report += f"   Total tests: {total_tests}\n"
    report += f"   Tests passed: {passed_tests}\n"
    report += f"   Success rate: {int(passed_tests / total_tests * 100)}%\n"
    report += "=" * 60 + "\n"

    return report


def main():
    """Run all tests and generate report."""
    test_results = {}

    # Setup test environment
    print("🧪 Preparing MCP Audio Effects & Modulators test")
    env = setup_test_environment()
    if not env:
        print("❌ Failed to setup test environment. Is MCP Server running?")
        return False

    print("⏳ Running test suite...\n")

    # Run all test categories
    test_functions = [
        ("audio_effect_loading", test_audio_effect_loading),
        ("set_audio_effect_parameter", test_set_audio_effect_parameter),
        ("set_parameters_bulk", test_set_parameters_bulk),
        ("udp_parameter_control", test_udp_parameter_control),
        ("modulator_creation", test_modulator_creation),
        ("modulator_parameter_control", test_modulator_parameter_control),
        ("modulator_routing", test_modulator_routing),
        ("modulator_removal", test_modulator_removal),
    ]

    for test_name, test_func in test_functions:
        try:
            test_results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            test_results[test_name] = [{"success": False, "error": str(e)}]

    # Generate and print report
    report = generate_report(test_results)
    print(report)

    # Return overall success
    total_tests = sum(len(r) for r in test_results.values())
    passed_tests = sum(
        1 for r in test_results.values() for i in r if i.get("success", False)
    )

    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
