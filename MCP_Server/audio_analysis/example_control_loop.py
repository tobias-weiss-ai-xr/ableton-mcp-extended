"""
Example Usage of Audio Analysis Controller

This script demonstrates how to set up and use the AudioAnalysisController
for real-time audio analysis and responsive control in Ableton Live.

Setup:
1. Install Ableton Remote Script (see README.md)
2. Open Ableton Live and load a VST analysis plugin (e.g., Youlean Loudness Meter 2)
3. Update track_index and device_index below to match your session
4. Run: python MCP_Server/audio_analysis/example_control_loop.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "MCP_Server"))

from MCP_Server.audio_analysis.polling import ParameterConfig
from MCP_Server.audio_analysis.rules import ParameterSnapshot
from MCP_Server.audio_analysis.control_loop import (
    AudioAnalysisController,
    run_with_graceful_shutdown,
)


# Mock MCP client for testing without actual Ableton connection
class MockMCPClient:
    """Mock MCP client for testing purposes."""

    def __init__(self):
        self.call_count = 0
        self.last_action = None
        self.mock_parameter_value = -14.0  # Starting LUFS value

    def call_tool(self, server_name: str, method_name: str, params: dict):
        """Mock tool call that simulates Ableton MCP tools."""
        self.call_count += 1
        self.last_action = (method_name, params)

        # Simulate get_device_parameters
        if method_name == "get_device_parameters":
            # Return mock parameters (assuming 3 parameters)
            return [
                {
                    "value": self.mock_parameter_value,
                    "name": "LUFS",
                    "min": -70,
                    "max": 5,
                },
                {
                    "value": -5.0,
                    "name": "RMS",
                    "min": -60,
                    "max": 0,
                },
                {
                    "value": -1.5,
                    "name": "TruePeak",
                    "min": -6,
                    "max": 6,
                },
            ]

        # Simulate action methods
        print(f"[MOCK] Executing {method_name}: {params}")

        # Simulate dynamic parameter values for realism
        if "clip_index" in params:
            # Simulate changing LUFS based on clip trigger
            self.mock_parameter_value = -18.0 if params["clip_index"] == 1 else -14.0

        return {"success": True}


def example_basic_setup():
    """
    Basic example: Monitor LUFS and control track volume.

    This example:
    1. Monitors LUFS parameter from VST plugin
    2. Loads loudness-based rules from YAML
    3. Automatically reduces track volume when LUFS too high
    4. Restores volume when safe level reached
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Loudness-Based Track Control")
    print("=" * 70)

    # Create mock MCP client (replace with actual client in production)
    mcp_client = MockMCPClient()

    # Configure parameters to poll
    # Note: These indices MUST match your actual VST plugin's parameter indices
    params_to_poll = [
        ParameterConfig(
            index=0,  # Momentary LUFS (verify with get_device_parameters)
            name="Momentary LUFS",
            min_value=-70.0,  # Minimum LUFS value
            max_value=5.0,  # Maximum LUFS value
            unit="LUFS",
        ),
    ]

    # Create controller
    controller = AudioAnalysisController(
        track_index=0,  # Update to your track index
        device_index=0,  # Update to your VST device index
        params_to_poll=params_to_poll,
        mcp_client=mcp_client,
        update_rate_hz=10.0,  # 10 Hz = 10 updates per second
        buffer_size=1000,
    )

    # Load rule set from YAML
    rule_file = Path(__file__).parent / "example_rules.yaml"
    if rule_file.exists():
        controller.load_ruleset(str(rule_file))
        print(f"Loaded rules from: {rule_file}")
    else:
        print(f"Warning: Rule file not found: {rule_file}")
        print("Create example_rules.yaml based on the template in docs/")

    # Print status before starting
    print("\nBefore starting:")
    controller.print_status()

    # Run with graceful shutdown (Ctrl+C to stop)
    run_with_graceful_shutdown(controller)


def example_advanced_setup():
    """
    Advanced example: Multi-parameter spectral analysis.

    This example:
    1. Monitors multiple spectral bands
    2. Loads spectral-based rules from YAML
    3. Triggers different clips based on frequency content
    4. Demonstrates rule enable/disable
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Advanced Spectral Analysis Control")
    print("=" * 70)

    # Create mock MCP client
    mcp_client = MockMCPClient()

    # Configure multiple spectral parameters
    params_to_poll = [
        ParameterConfig(
            index=0, name="Low Frequencies", min_value=-60.0, max_value=0.0, unit="dB"
        ),
        ParameterConfig(
            index=1, name="Mid Frequencies", min_value=-60.0, max_value=0.0, unit="dB"
        ),
        ParameterConfig(
            index=2, name="High Frequencies", min_value=-60.0, max_value=0.0, unit="dB"
        ),
    ]

    # Create controller
    controller = AudioAnalysisController(
        track_index=1,  # Different track
        device_index=0,
        params_to_poll=params_to_poll,
        mcp_client=mcp_client,
        update_rate_hz=15.0,  # Higher rate for spectral monitoring
        buffer_size=500,
    )

    # Load spectral rule set
    spectral_rule_file = Path(__file__).parent / "example_rules_spectral.yaml"
    if spectral_rule_file.exists():
        controller.load_ruleset(str(spectral_rule_file))
        print(f"Loaded spectral rules from: {spectral_rule_file}")
    else:
        print(f"Warning: Spectral rule file not found: {spectral_rule_file}")

    # Print status
    print("\nController configuration:")
    controller.print_status()

    # Note: In production, you would call run_with_graceful_shutdown(controller)
    print("\nIn production, call run_with_graceful_shutdown(controller) to start")


def example_custom_callback():
    """
    Example: Using custom callbacks for monitoring.

    Demonstrates adding custom monitoring callbacks alongside rule engine.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Custom Monitoring Callbacks")
    print("=" * 70)

    mcp_client = MockMCPClient()

    params_to_poll = [
        ParameterConfig(
            index=0, name="LUFS", min_value=-70.0, max_value=5.0, unit="LUFS"
        ),
    ]

    controller = AudioAnalysisController(
        track_index=0,
        device_index=0,
        params_to_poll=params_to_poll,
        mcp_client=mcp_client,
        update_rate_hz=10.0,
    )

    # Add custom callback to monitor parameter values
    def monitor_callback(snapshot: ParameterSnapshot):
        """Custom callback to log parameter values."""
        for idx, val in snapshot.values.items():
            config = controller.get_parameter_config(idx)
            if config:
                raw_val = snapshot.raw_values[idx]
                print(
                    f"[MONITOR] {config.name}: {val:.4f} normalized ({raw_val:.2f} {config.unit})"
                )

    # Register custom callback (runs alongside rule engine)
    controller.poller.add_callback(monitor_callback)

    print("Custom monitoring callback registered")
    print("\nIn production:")
    print("  1. Load rule sets: controller.load_ruleset(...)")
    print("  2. Start: controller.start()")
    print("  3. Monitor callback receives each snapshot")


def manual_control_example():
    """
    Example: Manual controller usage with explicit start/stop.

    For when you need programmatic control beyond run_with_graceful_shutdown.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Manual Controller Lifecycle")
    print("=" * 70)

    mcp_client = MockMCPClient()

    params_to_poll = [
        ParameterConfig(
            index=0, name="LUFS", min_value=-70.0, max_value=5.0, unit="LUFS"
        ),
    ]

    controller = AudioAnalysisController(
        track_index=0,
        device_index=0,
        params_to_poll=params_to_poll,
        mcp_client=mcp_client,
        update_rate_hz=10.0,
    )

    print("Manual control steps:")
    print()
    print("1. Load rule sets:")
    print("   controller.load_ruleset('path/to/rules.yaml')")
    print()
    print("2. Get current values:")
    print("   values = controller.get_current_parameter_values()")
    print("   raw = controller.get_raw_parameter_values()")
    print("   lufs = controller.get_parameter_value(0)")
    print()
    print("3. Start polling:")
    print("   controller.start()")
    print()
    print("4. Check status while running:")
    print("   status = controller.get_status()")
    print("   controller.print_status()")
    print()
    print("5. Enable/disable rules:")
    print("   controller.enable_rule('reduce_loudness')")
    print("   controller.disable_rule('restore_volume')")
    print()
    print("6. Stop controller:")
    print("   controller.stop()")
    print()
    print("7. Reset statistics:")
    print("   controller.reset_statistics()")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audio Analysis Controller Examples")
    parser.add_argument(
        "example",
        choices=["basic", "advanced", "callback", "manual"],
        help="Which example to run",
    )
    args = parser.parse_args()

    try:
        if args.example == "basic":
            example_basic_setup()
        elif args.example == "advanced":
            example_advanced_setup()
        elif args.example == "callback":
            example_custom_callback()
        elif args.example == "manual":
            manual_control_example()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
