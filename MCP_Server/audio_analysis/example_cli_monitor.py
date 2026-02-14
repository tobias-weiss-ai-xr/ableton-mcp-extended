"""
Example: CLI Monitor with Audio Analysis Controller

This example demonstrates how to use the AudioAnalysisMonitor
with the AudioAnalysisController to display real-time monitoring
of audio analysis parameters and rule execution.
"""

import sys
import os

# Add MCP_Server to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from MCP_Server.audio_analysis.cli_monitor import AudioAnalysisMonitor, MonitorConfig
from MCP_Server.audio_analysis.control_loop import AudioAnalysisController


class MockMCPClient:
    """Mock MCP client for testing without Ableton connection."""

    def call_tool(self, tool_name: str, params: dict) -> dict:
        """
        Mock MCP tool call.

        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool

        Returns:
            Mock response dict
        """
        print(f"[Mock] Calling {tool_name} with params: {params}")
        return {"success": True, "result": "mock_result"}


def example_1_basic_monitor():
    """
    Example 1: Basic monitor with mock values.

    This example creates a monitor with a mock controller
    and displays simulated parameter values.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Monitor with Mock Values")
    print("=" * 60)

    # Create mock controller
    mock_controller = create_mock_controller()

    # Create monitor with default config
    monitor = AudioAnalysisMonitor(mock_controller)

    # Start monitor
    print("\nStarting monitor for 5 seconds...")
    monitor.start()

    try:
        # Run for 5 seconds
        import time

        time.sleep(5)
    finally:
        monitor.stop()
        print("Monitor stopped.")


def example_2_custom_refresh_rate():
    """
    Example 2: Monitor with custom refresh rate.

    This example demonstrates setting a different refresh rate
    for the display (20 Hz for smoother updates).
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Monitor with 20 Hz Refresh Rate")
    print("=" * 60)

    # Create mock controller
    mock_controller = create_mock_controller()

    # Create monitor with custom config
    config = MonitorConfig(refresh_rate_hz=20, show_raw_values=True)
    monitor = AudioAnalysisMonitor(mock_controller, config=config)

    # Start monitor
    print("\nStarting monitor with 20 Hz refresh for 5 seconds...")
    monitor.start()

    try:
        import time

        time.sleep(5)
    finally:
        monitor.stop()
        print("Monitor stopped.")


def example_3_with_rules():
    """
    Example 3: Monitor with rule engine.

    This example loads a YAML rule file and displays
    rule execution statistics in the monitor.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Monitor with Rule Engine")
    print("=" * 60)

    from MCP_Server.audio_analysis.rules import Condition, Rule, RuleSet

    # Create mock controller
    mock_controller = create_mock_controller()

    # Create a sample rule
    rule = Rule(
        id="example_loudness_rule",
        name="Example Loudness Rule",
        conditions=[
            Condition(parameter_index=0, operator=Condition.Operator.GT, threshold=0.8)
        ],
        actions=[{"type": "set_parameter", "value": 0.5}],
        enabled=True,
        cooldown_seconds=1.0,
    )

    ruleset = RuleSet(id="example_ruleset", name="Example Rule Set", rules=[rule])

    # Add ruleset to controller
    mock_controller._rule_engine.load_ruleset(ruleset)

    # Create monitor
    monitor = AudioAnalysisMonitor(mock_controller)

    # Start monitor
    print("\nStarting monitor with rules for 5 seconds...")
    monitor.start()

    try:
        import time

        time.sleep(5)
    finally:
        monitor.stop()
        print("Monitor stopped.")


def example_4_interactive_mode():
    """
    Example 4: Interactive monitor with user commands.

    This example demonstrates an interactive mode where
    users can issue commands while monitoring.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Interactive Monitor Mode")
    print("=" * 60)
    print("Commands: [d] toggle debug, [q] quit")

    # Create mock controller
    mock_controller = create_mock_controller()

    # Create monitor
    monitor = AudioAnalysisMonitor(mock_controller)

    # Start monitor
    monitor.start()

    try:
        import time
        import select
        import sys

        print("Interactive mode started. Press 'd' to toggle debug, 'q' to quit...")

        # Interactive loop (non-blocking input check)
        start_time = time.time()
        while time.time() - start_time < 15:  # Run for 15 seconds max
            # Check for input (Unix-like systems only)
            # On Windows, use msvcrt module
            if sys.platform == "win32":
                import msvcrt

                if msvcrt.kbhit():
                    char = msvcrt.getch().decode("utf-8")
                    if char.lower() == "d":
                        monitor.toggle_debug()
                        print("Debug mode toggled")
                    elif char.lower() == "q":
                        break
            else:
                # Unix-like select for non-blocking input
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if char.lower() == "d":
                        monitor.toggle_debug()
                        print("Debug mode toggled")
                    elif char.lower() == "q":
                        break

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()
        print("Monitor stopped.")


def create_mock_controller():
    """
    Create a mock AudioAnalysisController for testing.

    Returns:
        Mock controller with realistic behavior
    """
    import time
    from unittest.mock import Mock, MagicMock

    controller = Mock(spec=AudioAnalysisController)

    # Create mock poller
    mock_poller = Mock()
    mock_poller._params_to_poll = []
    mock_poller.get_status.return_value = {
        "actual_rate_hz": 10.0,
        "target_rate_hz": 10.0,
        "uptime_seconds": 0.0,
        "total_snapshots": 0,
    }

    # Mock snapshot with changing values
    class MockSnapshot:
        def __init__(self):
            self.timestamp = time.time()
            self.values = {0: 0.5, 1: 0.3, 2: 0.7}
            self.raw_values = {"raw_0": -10.0, "raw_1": -20.0, "raw_2": -5.0}

    # Return new snapshot with slight variations
    var_counter = [0]

    def get_latest_snapshot():
        var_counter[0] += 1
        snapshot = MockSnapshot()
        # Vary values slightly
        snapshot.values[0] = 0.5 + 0.1 * (var_counter[0] % 10) / 10.0
        snapshot.values[1] = 0.3 + 0.1 * ((var_counter[0] // 10) % 10) / 10.0
        snapshot.values[2] = 0.7 + 0.1 * ((var_counter[0] // 100) % 10) / 10.0
        return snapshot

    mock_poller.get_latest_snapshot = get_latest_snapshot

    # Create rule engine mock
    from MCP_Server.audio_analysis.rules import RuleEngine

    mock_rule_engine = RuleEngine(MockMCPClient())
    mock_rule_engine.add_callback = Mock()

    # Set up parameter configs
    from MCP_Server.audio_analysis.polling import ParameterConfig

    mock_poller._params_to_poll = [
        ParameterConfig(
            index=0, name="Loudness (LUFS)", min_value=-70.0, max_value=-5.0, unit="dB"
        ),
        ParameterConfig(
            index=1, name="Peak Level", min_value=-60.0, max_value=0.0, unit="dBFS"
        ),
        ParameterConfig(
            index=2, name="Crest Factor", min_value=1.0, max_value=20.0, unit="dB"
        ),
    ]

    # Assign mocks to controller
    controller._poller = mock_poller
    controller._rule_engine = mock_rule_engine

    # Mock get_status
    def get_status():
        mock_poller.get_status.return_value = {
            "actual_rate_hz": 10.0,
            "target_rate_hz": 10.0,
            "uptime_seconds": time.time(),
            "total_snapshots": var_counter[0],
        }
        return mock_poller.get_status()

    controller.get_status = get_status

    return controller


def main():
    """Run all examples."""
    examples = [
        example_1_basic_monitor,
        example_2_custom_refresh_rate,
        example_3_with_rules,
        example_4_interactive_mode,
    ]

    print("\n" + "=" * 60)
    print("CLI MONITOR EXAMPLES")
    print("=" * 60)
    print("\nAvailable examples:")
    for i, example in enumerate(examples, 1):
        print(
            f"  {i}. {example.__name__.replace('example_', '').replace('_', ' ').title()}"
        )
    print("  all. Run all examples")

    choice = input("\nSelect example (1-4, all): ").strip().lower()

    if choice == "all":
        for example in examples:
            try:
                example()
            except KeyboardInterrupt:
                print("\nExample interrupted.")
    elif choice in ("1", "2", "3", "4"):
        examples[int(choice) - 1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
