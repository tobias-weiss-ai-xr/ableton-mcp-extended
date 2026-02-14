"""
Tests for Audio Analysis Control Loop

Tests for the AudioAnalysisController integration layer between polling and rule engine.
"""

import sys
from pathlib import Path

# Add parent directory to path for tests
test_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(test_dir))

import time
import pytest
from unittest.mock import Mock, MagicMock, patch

from MCP_Server.audio_analysis.polling import ParameterConfig, ParameterSnapshot
from MCP_Server.audio_analysis.rules import RuleEngine
from MCP_Server.audio_analysis.control_loop import AudioAnalysisController


class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self):
        self.calls = []
        self.mock_params = [
            {"value": -14.0, "name": "LUFS", "min": -70, "max": 5},
            {"value": -10.0, "name": "RMS", "min": -60, "max": 0},
        ]

    def call_tool(self, server_name: str, method_name: str, params: dict):
        """Mock tool call."""
        self.calls.append(
            {"server": server_name, "method": method_name, "params": params}
        )
        if method_name == "get_device_parameters":
            return self.mock_params
        return {"success": True}


@pytest.fixture
def mcp_client():
    """Create mock MCP client."""
    return MockMCPClient()


@pytest.fixture
def params_to_poll():
    """Create sample parameter configurations."""
    return [
        ParameterConfig(
            index=0, name="LUFS", min_value=-70.0, max_value=5.0, unit="LUFS"
        ),
        ParameterConfig(index=1, name="RMS", min_value=-60.0, max_value=0.0, unit="dB"),
    ]


@pytest.fixture
def controller(mcp_client, params_to_poll):
    """Create AudioAnalysisController fixture."""
    return AudioAnalysisController(
        track_index=0,
        device_index=0,
        params_to_poll=params_to_poll,
        mcp_client=mcp_client,
        update_rate_hz=10.0,
        buffer_size=100,
    )


class TestAudioAnalysisController:
    """Test AudioAnalysisController functionality."""

    def test_controller_initialization(self, controller):
        """Test controller initializes correctly."""
        assert controller.track_index == 0
        assert controller.device_index == 0
        assert len(controller.params_to_poll) == 2
        assert controller.poller is not None
        assert controller.engine is not None
        assert controller.mcp_client is not None
        assert not controller.running

    def test_get_parameter_config(self, controller):
        """Test getting parameter configuration."""
        config = controller.get_parameter_config(0)
        assert config is not None
        assert config.name == "LUFS"
        assert config.min_value == -70.0
        assert config.max_value == 5.0

    def test_get_parameter_config_not_found(self, controller):
        """Test getting non-existent parameter configuration."""
        config = controller.get_parameter_config(99)
        assert config is None

    def test_load_ruleset_success(self, controller, tmp_path):
        """Test loading a valid rule set."""
        # Create sample YAML file
        yaml_content = """
id: test_ruleset
name: Test Rules
enabled: true
rules:
  - id: test_rule
    name: Test Rule
    enabled: true
    cooldown_seconds: 0
    conditions:
      - parameter_index: 0
        operator: ">="
        threshold: 0.5
    actions:
      - type: set_volume
        track_index: 0
        target_value: 0.5
"""
        yaml_file = tmp_path / "test_rules.yaml"
        yaml_file.write_text(yaml_content)

        # Load rule set
        ruleset = controller.load_ruleset(str(yaml_file))

        assert ruleset.id == "test_ruleset"
        assert len(ruleset.rules) == 1
        assert len(controller.engine.rule_sets) == 1

    def test_load_ruleset_file_not_found(self, controller):
        """Test loading non-existent rule set raises error."""
        with pytest.raises(FileNotFoundError):
            controller.load_ruleset("nonexistent.yaml")

    def test_load_multiple_rulesets(self, controller, tmp_path):
        """Test loading multiple rule sets."""
        # Create two rule files
        yaml_content = """
id: ruleset_{i}
name: Ruleset {i}
rules: []
"""
        for i in range(2):
            yaml_file = tmp_path / f"ruleset_{i}.yaml"
            yaml_file.write_text(yaml_content.format(i=i))

        # Load both
        rulesets = controller.load_rulesets(
            [str(tmp_path / "ruleset_0.yaml"), str(tmp_path / "ruleset_1.yaml")]
        )

        assert len(rulesets) == 2
        assert len(controller.engine.rule_sets) == 2

    def test_register_engine(self, controller):
        """Test registering rule engine as poller callback."""
        controller.register_engine()

        # Check that engine is in poller callbacks
        assert controller.engine.evaluate in controller.poller.callbacks

    def test_start_controller(self, controller):
        """Test starting controller."""
        controller.start(register_engine=True)

        assert controller.running
        assert controller.poller.running
        assert controller.start_time is not None
        assert not controller._shutdown_requested

    def test_start_already_running(self, controller):
        """Test starting already-running controller."""
        controller.start(register_engine=True)

        # Should not raise error, just warn
        controller.start()

        assert controller.running

    def test_stop_controller(self, controller):
        """Test stopping controller."""
        controller.start(register_engine=True)
        time.sleep(0.1)  # Let poll loop start

        controller.stop()

        assert not controller.running
        assert controller.stop_time is not None
        assert controller._shutdown_requested

    def test_stop_not_running(self, controller):
        """Test stopping non-running controller."""
        # Should not raise error
        controller.stop()
        assert not controller.running

    def test_get_status_while_stopped(self, controller):
        """Test getting status while controller is stopped."""
        status = controller.get_status()

        assert "controller" in status
        assert "poller" in status
        assert "engine" in status
        assert not status["controller"]["running"]
        assert status["controller"]["runtime_seconds"] == 0

    def test_get_status_while_running(self, controller):
        """Test getting status while controller is running."""
        controller.start(
            register_engine=False
        )  # Don't register engine (requires rules)
        time.sleep(0.2)

        status = controller.get_status()

        assert status["controller"]["running"]
        assert status["poller"]["running"]
        assert status["controller"]["runtime_seconds"] > 0

        controller.stop()

    def test_get_current_parameter_values(self, controller, mcp_client):
        """Test getting current normalized parameter values."""
        # Manually create a snapshot
        snapshot = ParameterSnapshot(
            timestamp=time.time(),
            values={0: 0.4, 1: 0.6},
            raw_values={0: -14.0, 1: -10.0},
        )
        controller.poller.buffer.push(snapshot)
        controller.poller.latest_snapshot = snapshot

        values = controller.get_current_parameter_values()

        assert values is not None
        assert values[0] == 0.4
        assert values[1] == 0.6

    def test_get_current_parameter_values_none(self, controller):
        """Test getting values when no snapshot exists."""
        values = controller.get_current_parameter_values()
        assert values is None

    def test_get_raw_parameter_values(self, controller, mcp_client):
        """Test getting current raw parameter values."""
        snapshot = ParameterSnapshot(
            timestamp=time.time(),
            values={0: 0.4, 1: 0.6},
            raw_values={0: -14.0, 1: -10.0},
        )
        controller.poller.buffer.push(snapshot)
        controller.poller.latest_snapshot = snapshot

        values = controller.get_raw_parameter_values()

        assert values is not None
        assert values[0] == -14.0
        assert values[1] == -10.0

    def test_get_parameter_value(self, controller):
        """Test getting specific parameter value."""
        snapshot = ParameterSnapshot(
            timestamp=time.time(),
            values={0: 0.4, 1: 0.6},
            raw_values={0: -14.0, 1: -10.0},
        )
        controller.poller.buffer.push(snapshot)
        controller.poller.latest_snapshot = snapshot

        value = controller.get_parameter_value(0)
        assert value == 0.4

        value = controller.get_parameter_value(1)
        assert value == 0.6

    def test_get_parameter_value_not_found(self, controller):
        """Test getting non-existent parameter value."""
        value = controller.get_parameter_value(99)
        assert value is None

    def test_get_raw_parameter_value(self, controller):
        """Test getting specific raw parameter value."""
        snapshot = ParameterSnapshot(
            timestamp=time.time(),
            values={0: 0.4, 1: 0.6},
            raw_values={0: -14.0, 1: -10.0},
        )
        controller.poller.buffer.push(snapshot)
        controller.poller.latest_snapshot = snapshot

        value = controller.get_raw_parameter_value(0)
        assert value == -14.0

    def test_enable_rule(self, controller, tmp_path):
        """Test enabling a specific rule."""
        # Create rule set with enabled=False
        yaml_content = """
id: test_ruleset
rules:
  - id: test_rule
    name: Test Rule
    enabled: false
    conditions:
      - parameter_index: 0
        operator: ">="
        threshold: 0.5
    actions:
      - type: set_volume
        track_index: 0
        target_value: 0.5
"""
        yaml_file = tmp_path / "test_rules.yaml"
        yaml_file.write_text(yaml_content)
        controller.load_ruleset(str(yaml_file))

        # Rule should be disabled initially
        rule = controller.engine.rule_sets[0].get_rule("test_rule")
        assert not rule.enabled

        # Enable rule
        controller.enable_rule("test_rule")

        # Rule should now be enabled
        assert rule.enabled

    def test_enable_rule_not_found(self, controller):
        """Test enabling non-existent rule."""
        # Should not raise error, just warn
        controller.enable_rule("nonexistent_rule")

    def test_disable_rule(self, controller, tmp_path):
        """Test disabling a specific rule."""
        yaml_content = """
id: test_ruleset
rules:
  - id: test_rule
    name: Test Rule
    enabled: true
    conditions:
      - parameter_index: 0
        operator: ">="
        threshold: 0.5
    actions:
      - type: set_volume
        track_index: 0
        target_value: 0.5
"""
        yaml_file = tmp_path / "test_rules.yaml"
        yaml_file.write_text(yaml_content)
        controller.load_ruleset(str(yaml_file))

        # Rule should be enabled initially
        rule = controller.engine.rule_sets[0].get_rule("test_rule")
        assert rule.enabled

        # Disable rule
        controller.disable_rule("test_rule")

        # Rule should now be disabled
        assert not rule.enabled

    def test_disable_rule_not_found(self, controller):
        """Test disabling non-existent rule."""
        # Should not raise error, just warn
        controller.disable_rule("nonexistent_rule")

    def test_reset_statistics(self, controller):
        """Test resetting controller statistics."""
        # Set some stats
        controller.start(register_engine=False)
        time.sleep(0.2)

        # Reset
        controller.reset_statistics()

        stats = controller.get_status()["engine"]
        assert stats["total_evaluations"] == 0
        assert stats["total_triggers"] == 0

        controller.stop()

    def test_print_status(self, controller, capsys):
        """Test printing status to console."""
        controller.print_status()

        captured = capsys.readouterr()
        assert "AUDIO ANALYSIS CONTROLLER STATUS" in captured.out
        assert "State:" in captured.out
        assert "POLLER:" in captured.out
        assert "ENGINE:" in captured.out

    def test_integration_lifecycle(self, controller, tmp_path):
        """Test full integration lifecycle: setup → start → poll → stop."""
        # 1. Setup: Load rule set
        yaml_content = """
id: test_ruleset
rules:
  - id: test_rule
    name: Test Rule
    enabled: true
    cooldown_seconds: 0
    conditions:
      - parameter_index: 0
        operator: ">="
        threshold: 0.5
    actions:
      - type: set_volume
        track_index: 0
        target_value: 0.5
"""
        yaml_file = tmp_path / "test_rules.yaml"
        yaml_file.write_text(yaml_content)
        controller.load_ruleset(str(yaml_file))

        # 2. Start controller
        controller.start(register_engine=True)
        poll_count_before = controller.poller.poll_count

        assert controller.running
        assert len(controller.engine.rule_sets) == 1

        # 3. Let it poll a few times
        time.sleep(0.3)

        # 4. Verify polling occurred
        poll_count_after = controller.poller.poll_count
        assert poll_count_after > poll_count_before

        # 5. Stop controller
        controller.stop()
        assert not controller.running
        assert controller.stop_time is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
