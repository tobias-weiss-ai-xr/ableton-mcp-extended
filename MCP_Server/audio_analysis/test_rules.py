"""
Unit tests for Rule-Based Decision System

Tests cover:
- Condition evaluation logic
- Rule satisfaction and cooldowns
- RuleSet management
- RuleEngine integration with pollers
- YAML configuration parsing
- Action execution
"""

import sys
from pathlib import Path

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import time
from unittest.mock import Mock, MagicMock
import tempfile
import yaml

from audio_analysis.rules import Operator, Condition, Rule, RuleSet, RuleEngine, Action
from audio_analysis.polling import ParameterSnapshot


class TestOperator:
    """Test Operator enum."""

    def test_operator_values(self):
        assert Operator.GT.value == ">"
        assert Operator.GTE.value == ">="
        assert Operator.LT.value == "<"
        assert Operator.LTE.value == "<="
        assert Operator.EQ.value == "=="
        assert Operator.NEQ.value == "!="
        assert Operator.IN.value == "in"
        assert Operator.NOT_IN.value == "not_in"


class TestCondition:
    """Test Condition evaluation logic."""

    def setup_method(self):
        self.snapshot_values = {0: 0.5, 1: 0.75, 2: 0.25}

    def test_condition_greater_than(self):
        cond = Condition(parameter_index=0, operator=Operator.GT, threshold=0.4)
        assert cond.evaluate(self.snapshot_values) is True  # 0.5 > 0.4

    def test_condition_greater_than_false(self):
        cond = Condition(parameter_index=0, operator=Operator.GT, threshold=0.6)
        assert cond.evaluate(self.snapshot_values) is False  # 0.5 not > 0.6

    def test_condition_greater_than_equal(self):
        cond = Condition(parameter_index=1, operator=Operator.GTE, threshold=0.75)
        assert cond.evaluate(self.snapshot_values) is True  # 0.75 >= 0.75

    def test_condition_less_than(self):
        cond = Condition(parameter_index=2, operator=Operator.LT, threshold=0.5)
        assert cond.evaluate(self.snapshot_values) is True  # 0.25 < 0.5

    def test_condition_less_than_equal(self):
        cond = Condition(parameter_index=0, operator=Operator.LTE, threshold=0.5)
        assert cond.evaluate(self.snapshot_values) is True  # 0.5 <= 0.5

    def test_condition_equal(self):
        cond = Condition(parameter_index=1, operator=Operator.EQ, threshold=0.75)
        assert cond.evaluate(self.snapshot_values) is True  # 0.75 == 0.75

    def test_condition_not_equal(self):
        cond = Condition(parameter_index=0, operator=Operator.NEQ, threshold=0.75)
        assert cond.evaluate(self.snapshot_values) is True  # 0.5 != 0.75

    def test_condition_missing_parameter(self):
        cond = Condition(parameter_index=99, operator=Operator.GT, threshold=0.1)
        assert cond.evaluate(self.snapshot_values) is False


class TestRule:
    """Test Rule evaluation logic including cooldowns."""

    def setup_method(self):
        snapshot = ParameterSnapshot(
            timestamp=time.time(),
            values={0: 0.8, 1: 0.3},
            raw_values={0: -10.0, 1: -20.0},
        )
        self.snapshot = snapshot

    def test_rule_all_conditions_met(self):
        cond1 = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        cond2 = Condition(parameter_index=1, operator=Operator.LTE, threshold=0.5)

        action = Action(type="set_parameter", track_index=1, target_value=0.5)

        rule = Rule(
            id="test_rule",
            name="Test Rule",
            conditions=[cond1, cond2],
            actions=[action],
            enabled=True,
        )

        assert rule.evaluate(self.snapshot) is True

    def test_rule_one_condition_fails(self):
        cond1 = Condition(
            parameter_index=0, operator=Operator.GTE, threshold=0.9
        )  # Fails: 0.8 < 0.9
        cond2 = Condition(
            parameter_index=1, operator=Operator.LTE, threshold=0.5
        )  # Passes

        action = Action(type="set_parameter", track_index=1, target_value=0.5)

        rule = Rule(
            id="test_rule",
            name="Test Rule",
            conditions=[cond1, cond2],
            actions=[action],
            enabled=True,
        )

        assert rule.evaluate(self.snapshot) is False

    def test_rule_disabled(self):
        cond = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        action = Action(type="set_parameter", track_index=1, target_value=0.5)

        rule = Rule(
            id="test_rule",
            name="Test Rule",
            conditions=[cond],
            actions=[action],
            enabled=False,  # Disabled
        )

        assert rule.evaluate(self.snapshot) is False

    def test_rule_cooldown_prevents_trigger(self):
        cond = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        action = Action(type="set_parameter", track_index=1, target_value=0.5)

        rule = Rule(
            id="test_rule",
            name="Test Rule",
            conditions=[cond],
            actions=[action],
            enabled=True,
            cooldown_seconds=5.0,
        )

        # First evaluation - should pass
        assert rule.evaluate(self.snapshot) is True
        rule.mark_triggered()

        # Immediate second evaluation - should fail due to cooldown
        assert rule.evaluate(self.snapshot) is False

    def test_rule_cooldown_expired(self):
        cond = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        action = Action(type="set_parameter", track_index=1, target_value=0.5)

        rule = Rule(
            id="test_rule",
            name="Test Rule",
            conditions=[cond],
            actions=[action],
            enabled=True,
            cooldown_seconds=1.0,  # Short cooldown for test
        )

        # First evaluation
        assert rule.evaluate(self.snapshot) is True
        rule.mark_triggered()

        # Wait for cooldown to expire
        time.sleep(1.1)

        # Second evaluation - should pass now
        assert rule.evaluate(self.snapshot) is True


class TestRuleSet:
    """Test RuleSet management and evaluation."""

    def setup_method(self):
        snapshot = ParameterSnapshot(
            timestamp=time.time(),
            values={0: 0.8, 1: 0.3},
            raw_values={0: -10.0, 1: -20.0},
        )
        self.snapshot = snapshot

    def test_ruleset_evaluate_returns_triggered_rules(self):
        # Note: param 1 (0.3) IS <= 0.4, so rule2 also triggers
        cond1 = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        cond2 = Condition(parameter_index=1, operator=Operator.LTE, threshold=0.4)

        rule1 = Rule(
            id="rule1",
            name="Rule 1",
            conditions=[cond1],
            actions=[Action(type="set_parameter", track_index=1, target_value=0.5)],
        )

        rule2 = Rule(
            id="rule2",
            name="Rule 2",
            conditions=[cond2],
            actions=[Action(type="set_parameter", track_index=1, target_value=0.5)],
        )

        ruleset = RuleSet(id="test_ruleset", name="Test RuleSet", rules=[rule1, rule2])

        triggered = ruleset.evaluate_all(self.snapshot)

        # Both rules trigger: 0.8 >= 0.7 AND 0.3 <= 0.4
        assert len(triggered) == 2
        assert triggered[0].id == "rule1"
        assert triggered[1].id == "rule2"

    def test_ruleset_disabled(self):
        cond = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        rule = Rule(
            id="test_rule",
            name="Test Rule",
            conditions=[cond],
            actions=[Action(type="set_parameter", track_index=1, target_value=0.5)],
        )

        ruleset = RuleSet(
            id="test_ruleset",
            name="Test RuleSet",
            rules=[rule],
            enabled=False,  # Disabled
        )

        triggered = ruleset.evaluate_all(self.snapshot)

        assert len(triggered) == 0

    def test_ruleset_get_rule(self):
        rule = Rule(id="target_rule", name="Target Rule", conditions=[], actions=[])

        ruleset = RuleSet(id="test_ruleset", name="Test RuleSet", rules=[rule])

        retrieved = ruleset.get_rule("target_rule")
        assert retrieved is not None
        assert retrieved.id == "target_rule"

        not_found = ruleset.get_rule("nonexistent")
        assert not_found is None

    def test_ruleset_enable_disable_rule(self):
        rule = Rule(
            id="togglable_rule",
            name="Togglable Rule",
            conditions=[],
            actions=[],
            enabled=True,
        )

        ruleset = RuleSet(id="test_ruleset", name="Test RuleSet", rules=[rule])

        assert rule.enabled is True

        ruleset.disable_rule("togglable_rule")
        assert rule.enabled is False

        ruleset.enable_rule("togglable_rule")
        assert rule.enabled is True


class TestAction:
    """Test Action serialization and deserialization."""

    def test_action_to_dict(self):
        action = Action(
            type="set_parameter",
            track_index=1,
            device_index=0,
            parameter_index=5,
            target_value=0.75,
        )

        result = action.to_dict()

        assert result["type"] == "set_parameter"
        assert result["track_index"] == 1
        assert result["device_index"] == 0
        assert result["parameter_index"] == 5
        assert result["target_value"] == 0.75

    def test_action_from_dict(self):
        data = {
            "type": "trigger_clip",
            "track_index": 2,
            "clip_index": 3,
            "data": {"extra": "info"},
        }

        action = Action.from_dict(data)

        assert action.type == "trigger_clip"
        assert action.track_index == 2
        assert action.clip_index == 3
        assert action.data == {"extra": "info"}


class TestRuleEngine:
    """Test RuleEngine integration and YAML loading."""

    def setup_method(self):
        self.mcp_client = Mock()
        self.mcp_client.call_tool = MagicMock(return_value={"status": "success"})
        self.engine = RuleEngine(mcp_client=self.mcp_client)

        self.snapshot = ParameterSnapshot(
            timestamp=time.time(),
            values={0: 0.8, 1: 0.3},
            raw_values={0: -10.0, 1: -20.0},
        )

    def test_engine_load_ruleset_from_yaml(self):
        # Create temporary YAML file
        yaml_content = {
            "id": "test_ruleset",
            "name": "Test RuleSet",
            "description": "Test description",
            "enabled": True,
            "rules": [
                {
                    "id": "rule1",
                    "name": "Rule 1",
                    "conditions": [
                        {"parameter_index": 0, "operator": ">=", "threshold": 0.7}
                    ],
                    "actions": [
                        {
                            "type": "set_parameter",
                            "track_index": 1,
                            "device_index": 0,
                            "parameter_index": 0,
                            "target_value": 0.5,
                        }
                    ],
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(yaml_content, f)
            yaml_path = f.name

        try:
            ruleset = self.engine.load_ruleset_from_yaml(yaml_path)

            assert ruleset.id == "test_ruleset"
            assert ruleset.name == "Test RuleSet"
            assert len(ruleset.rules) == 1
            assert ruleset.rules[0].id == "rule1"
        finally:
            Path(yaml_path).unlink()

    def test_engine_evaluate(self):
        # Add a rule set with a triggering rule
        cond = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        action = Action(
            type="set_parameter",
            track_index=1,
            device_index=0,
            parameter_index=0,
            target_value=0.5,
        )
        rule = Rule(
            id="test_rule", name="Test Rule", conditions=[cond], actions=[action]
        )
        ruleset = RuleSet(id="test_ruleset", name="Test RuleSet", rules=[rule])

        self.engine.add_ruleset(ruleset)

        # Evaluate (should trigger rule and execute action)
        executed = self.engine.evaluate(self.snapshot)

        assert len(executed) == 1
        assert executed[0]["rule_id"] == "test_rule"
        assert executed[0]["action_type"] == "set_parameter"
        assert executed[0]["success"] is True

        # Verify MCP client was called
        self.mcp_client.call_tool.assert_called_once()

    def test_engine_statistics(self):
        cond = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        action = Action(type="set_parameter", track_index=1, target_value=0.5)
        rule = Rule(
            id="test_rule", name="Test Rule", conditions=[cond], actions=[action]
        )
        ruleset = RuleSet(id="test_ruleset", name="Test RuleSet", rules=[rule])

        self.engine.add_ruleset(ruleset)

        # Evaluate multiple times
        self.engine.evaluate(self.snapshot)  # First evaluation

        stats = self.engine.get_stats()

        assert stats["total_evaluations"] == 1
        assert stats["total_triggers"] == 1
        assert stats["total_action_executions"] == 1
        assert stats["loaded_rulesets"] == 1
        assert stats["total_rules"] == 1

    def test_engine_reset_statistics(self):
        cond = Condition(parameter_index=0, operator=Operator.GTE, threshold=0.7)
        action = Action(type="set_parameter", track_index=1, target_value=0.5)
        rule = Rule(
            id="test_rule", name="Test Rule", conditions=[cond], actions=[action]
        )
        ruleset = RuleSet(id="test_ruleset", name="Test RuleSet", rules=[rule])

        self.engine.add_ruleset(ruleset)
        self.engine.evaluate(self.snapshot)

        # Reset
        self.engine.reset_stats()

        stats = self.engine.get_stats()

        assert stats["total_evaluations"] == 0
        assert stats["total_triggers"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
