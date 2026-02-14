#!/usr/bin/env python3
"""
Unit tests for VST rules parser.

Tests RulesParser class functionality including:
- YAML rule parsing
- Condition parsing (comparison and logical operators)
- Action parsing
- Rule validation
- Error handling for malformed files
"""

import unittest
import tempfile
import os
import yaml
from unittest.mock import mock_open

from test_analysis import BaseTestCase
from rules_parser import RulesParser, RulesParseError, Condition, Action, Rule


class TestRulesParser(BaseTestCase):
    """Test cases for RulesParser class."""

    def test_initialization(self):
        """Test RulesParser initialization."""
        parser = RulesParser()
        self.assertEqual(parser.rules, [])

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = RulesParser()

        with self.assertRaises(FileNotFoundError) as cm:
            parser.parse("non_existent.yml")

        self.assertIn("Rule file not found: non_existent.yml", str(cm.exception))

    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML syntax."""
        parser = RulesParser()

        invalid_yaml = "name: value\n  invalid: [unclosed"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(invalid_yaml)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        self.assertIn("YAML syntax error", str(cm.exception))

    def test_parse_missing_rules_section(self):
        """Test parsing YAML without rules section."""
        parser = RulesParser()

        yaml_data = {"not_rules": [{"name": "test"}]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        self.assertIn("Missing 'rules' section", str(cm.exception))

    def test_parse_empty_rules(self):
        """Test parsing empty rules section."""
        parser = RulesParser()

        yaml_data = {"rules": []}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        self.assertIn("Empty rule file", str(cm.exception))

    def test_parse_missing_required_fields(self):
        """Test parsing rule with missing required fields."""
        parser = RulesParser()

        # Test missing name
        yaml_data = {
            "rules": [
                {
                    "priority": 1,
                    "condition": {"operator": ">", "param1": "test", "param2": "5"},
                    "action": {"type": "set_volume", "params": {"track": 0}},
                    # Missing name field
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        self.assertIn("Missing required field: 'name'", str(cm.exception))

    def test_parse_invalid_priority(self):
        """Test parsing rule with invalid priority."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "test_rule",
                    "priority": -1,  # Invalid negative priority
                    "condition": {"operator": ">", "param1": "test", "param2": "5"},
                    "action": {"type": "set_volume", "params": {"track": 0}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        self.assertIn("priority' must be a non-negative integer", str(cm.exception))

    def test_parse_invalid_name_type(self):
        """Test parsing rule with invalid name type."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": 123,  # Invalid - not a string
                    "priority": 1,
                    "condition": {"operator": ">", "param1": "test", "param2": "5"},
                    "action": {"type": "set_volume", "params": {"track": 0}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        self.assertIn("'name' must be a string", str(cm.exception))

    def test_parse_unknown_operator(self):
        """Test parsing rule with unknown operator."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "test_rule",
                    "priority": 1,
                    "condition": {
                        "operator": "UNKNOWN",
                        "param1": "test",
                        "param2": "5",
                    },
                    "action": {"type": "set_volume", "params": {"track": 0}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        result = str(cm.exception)
        self.assertIn("Unknown operator 'UNKNOWN'", result)
        self.assertIn("Comparison operators", result)
        self.assertIn("Logical operators", result)

    def test_parse_unknown_action(self):
        """Test parsing rule with unknown action type."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "test_rule",
                    "priority": 1,
                    "condition": {"operator": ">", "param1": "test", "param2": "5"},
                    "action": {"type": "UNKNOWN_ACTION", "params": {"track": 0}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            with self.assertRaises(RulesParseError) as cm:
                parser.parse(f.name)

        result = str(cm.exception)
        self.assertIn("Unknown action type 'UNKNOWN_ACTION'", result)
        self.assertIn("set_parameter", result)

    def test_parse_logical_and_operator(self):
        """Test parsing AND logical operator."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "test_and",
                    "priority": 1,
                    "condition": {
                        "operator": "AND",
                        "conditions": [
                            {
                                "operator": ">",
                                "param1": "track:0:device:1:param",
                                "param2": "0.5",
                            },
                            {
                                "operator": "<",
                                "param1": "track:0:volume",
                                "param2": "0.8",
                            },
                        ],
                    },
                    "action": {
                        "type": "set_volume",
                        "params": {"track": 0, "value": 0.7},
                    },
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            rules = parser.parse(f.name)

        self.assertEqual(len(rules), 1)
        rule = rules[0]
        self.assertEqual(rule.name, "test_and")
        self.assertEqual(rule.priority, 1)
        self.assertEqual(rule.condition.operator, "AND")
        self.assertEqual(len(rule.condition.conditions), 2)

        # Check first condition
        cond1 = rule.condition.conditions[0]
        self.assertEqual(cond1.operator, ">")
        self.assertEqual(cond1.param1, "track:0:device:1:param")
        self.assertEqual(cond1.param2, "0.5")

        # Check second condition
        cond2 = rule.condition.conditions[1]
        self.assertEqual(cond2.operator, "<")
        self.assertEqual(cond2.param1, "track:0:volume")
        self.assertEqual(cond2.param2, "0.8")

        # Check action
        self.assertEqual(rule.action.type, "set_volume")
        self.assertEqual(rule.action.params["track"], 0)
        self.assertEqual(rule.action.params["value"], 0.7)

    def test_parse_logical_or_operator(self):
        """Test parsing OR logical operator."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "test_or",
                    "priority": 2,
                    "condition": {
                        "operator": "OR",
                        "conditions": [
                            {
                                "operator": "==",
                                "param1": "track:0:name",
                                "param2": "Kick",
                            },
                            {
                                "operator": "==",
                                "param1": "track:0:name",
                                "param2": "Snare",
                            },
                        ],
                    },
                    "action": {"type": "fire_clip", "params": {"track": 0, "clip": 1}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            rules = parser.parse(f.name)

        self.assertEqual(len(rules), 1)
        rule = rules[0]
        self.assertEqual(rule.condition.operator, "OR")
        self.assertEqual(len(rule.condition.conditions), 2)

    def test_parse_logical_not_operator(self):
        """Test parsing NOT logical operator."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "test_not",
                    "priority": 3,
                    "condition": {
                        "operator": "NOT",
                        "condition": {
                            "operator": ">",
                            "param1": "track:0:volume",
                            "param2": "0.9",
                        },
                    },
                    "action": {"type": "stop_playback", "params": {}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            rules = parser.parse(f.name)

        self.assertEqual(len(rules), 1)
        rule = rules[0]
        self.assertEqual(rule.condition.operator, "NOT")
        self.assertEqual(len(rule.condition.conditions), 1)

        # Check nested condition
        nested_cond = rule.condition.conditions[0]
        self.assertEqual(nested_cond.operator, ">")
        self.assertEqual(nested_cond.param1, "track:0:volume")
        self.assertEqual(nested_cond.param2, "0.9")

    def test_parse_comparison_operators(self):
        """Test parsing all comparison operators."""
        parser = RulesParser()

        for operator in RulesParser.COMPARISON_OPERATORS:
            yaml_data = {
                "rules": [
                    {
                        "name": f"test_{operator}",
                        "priority": 1,
                        "condition": {
                            "operator": operator,
                            "param1": "test_param",
                            "param2": "test_value",
                        },
                        "action": {"type": "set_parameter", "params": {}},
                    }
                ]
            }

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yml", delete=False
            ) as f:
                yaml.dump(yaml_data, f)
                f.flush()

                rules = parser.parse(f.name)

                self.assertEqual(len(rules), 1)
                rule = rules[0]
                self.assertEqual(rule.condition.operator, operator)
                self.assertEqual(rule.condition.param1, "test_param")
                self.assertEqual(rule.condition.param2, "test_value")

    def test_parse_action_types(self):
        """Test parsing all supported action types."""
        parser = RulesParser()

        for action_type in RulesParser.SUPPORTED_ACTIONS:
            yaml_data = {
                "rules": [
                    {
                        "name": f"test_{action_type}",
                        "priority": 1,
                        "condition": {"operator": ">", "param1": "test", "param2": "0"},
                        "action": {
                            "type": action_type,
                            "params": {"track": 0, "device": 1, "param": 2},
                        },
                    }
                ]
            }

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yml", delete=False
            ) as f:
                yaml.dump(yaml_data, f)
                f.flush()

                rules = parser.parse(f.name)

                self.assertEqual(len(rules), 1)
                rule = rules[0]
                self.assertEqual(rule.action.type, action_type)
                self.assertEqual(rule.action.params["track"], 0)
                self.assertEqual(rule.action.params["device"], 1)
                self.assertEqual(rule.action.params["param"], 2)

    def test_parse_rules_priority_sorting(self):
        """Test that rules are sorted by priority."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "high_priority",
                    "priority": 1,
                    "condition": {"operator": ">", "param1": "test", "param2": "0"},
                    "action": {"type": "set_volume", "params": {}},
                },
                {
                    "name": "medium_priority",
                    "priority": 5,
                    "condition": {"operator": ">", "param1": "test", "param2": "0"},
                    "action": {"type": "set_volume", "params": {}},
                },
                {
                    "name": "low_priority",
                    "priority": 10,
                    "condition": {"operator": ">", "param1": "test", "param2": "0"},
                    "action": {"type": "set_volume", "params": {}},
                },
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            rules = parser.parse(f.name)

        self.assertEqual(len(rules), 3)
        # Rules should be sorted by priority (lower number = higher priority)
        self.assertEqual(rules[0].name, "high_priority")  # priority 1
        self.assertEqual(rules[1].name, "medium_priority")  # priority 5
        self.assertEqual(rules[2].name, "low_priority")  # priority 10

    def test_validate_rules_success(self):
        """Test successful rule validation."""
        parser = RulesParser()

        # Create valid rule
        yaml_data = {
            "rules": [
                {
                    "name": "valid_rule",
                    "priority": 1,
                    "condition": {
                        "operator": ">",
                        "param1": "track:0:volume",
                        "param2": "0.8",
                    },
                    "action": {
                        "type": "set_volume",
                        "params": {"track": 0, "value": 0.9},
                    },
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            parser.parse(f.name)

            # Mock parameter mappings that include the referenced parameter
            parameter_mappings = {
                "track:0:volume": {"name": "Volume", "min": 0.0, "max": 1.0}
            }

            warnings = parser.validate_rules(parameter_mappings)
            self.assertEqual(warnings, [])

    def test_validate_rules_missing_parameter(self):
        """Test rule validation with missing parameter reference."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "invalid_rule",
                    "priority": 1,
                    "condition": {
                        "operator": ">",
                        "param1": "track:0:missing_param",  # Not in mappings
                        "param2": "0.8",
                    },
                    "action": {"type": "set_volume", "params": {}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            parser.parse(f.name)

            # Mock empty parameter mappings
            parameter_mappings = {}

            warnings = parser.validate_rules(parameter_mappings)
            self.assertEqual(len(warnings), 1)
            self.assertIn(
                "Parameter reference 'track:0:missing_param' not found", warnings[0]
            )

    def test_validate_rules_nested_conditions(self):
        """Test rule validation with nested logical conditions."""
        parser = RulesParser()

        yaml_data = {
            "rules": [
                {
                    "name": "nested_rule",
                    "priority": 1,
                    "condition": {
                        "operator": "AND",
                        "conditions": [
                            {
                                "operator": ">",
                                "param1": "track:0:volume",
                                "param2": "0.5",
                            },
                            {
                                "operator": "OR",
                                "conditions": [
                                    {
                                        "operator": "==",
                                        "param1": "track:0:name",
                                        "param2": "Kick",
                                    },
                                    {
                                        "operator": "==",
                                        "param1": "missing_param",
                                        "param2": "Snare",
                                    },
                                ],
                            },
                        ],
                    },
                    "action": {"type": "set_volume", "params": {}},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(yaml_data, f)
            f.flush()

            parser.parse(f.name)

            # Mock parameter mappings (missing one parameter)
            parameter_mappings = {
                "track:0:volume": {"name": "Volume"},
                "track:0:name": {"name": "Kick"},
                # missing: track:0:missing_param
            }

            warnings = parser.validate_rules(parameter_mappings)
            self.assertEqual(len(warnings), 1)
            self.assertIn(
                "Parameter reference 'track:0:missing_param' not found", warnings[0]
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
