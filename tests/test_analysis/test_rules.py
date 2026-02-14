import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to sys.path to import analysis modules
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "analysis")
)

try:
    from rules_parser import parse_rules
    from rules_engine import RulesEngine
except ImportError as e:
    print(f"Error importing analysis modules: {e}")
    print("Make sure analysis scripts are properly implemented")
    sys.exit(1)


class TestRulesParser(unittest.TestCase):
    """Test rules parser functionality."""

    def test_parse_valid_yaml_rules(self):
        """Test parsing valid YAML rule configuration."""
        yaml_content = """
rules:
  - name: "Compress loud audio"
    condition:
      parameter: "lufs"
      operator: ">"
      value: -14.0
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: -0.1
  - name: "Reduce high frequency"
    condition:
      parameter: "spectral_centroid"
      operator: ">"
      value: 5000
    action:
      type: "set_parameter"
      target:
        track: 2
        parameter: "filter_cutoff"
        value: 0.8
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                yaml_content
            )
            mock_file.return_value.__exit__.return_value = None

            rules = parse_rules("test_rules.yml")

            self.assertEqual(len(rules), 2)
            self.assertEqual(rules[0]["name"], "Compress loud audio")
            self.assertEqual(rules[0]["condition"]["parameter"], "lufs")
            self.assertEqual(rules[0]["action"]["type"], "set_parameter")

    def test_parse_invalid_yaml_syntax(self):
        """Test parsing invalid YAML syntax."""
        invalid_yaml = """
rules:
  - name: "Invalid rule"
    condition:
      parameter: "lufs"
    # Missing operator - invalid syntax
    action:
      type: "set_parameter"
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                invalid_yaml
            )

            with self.assertRaises(Exception) as context:
                parse_rules("test_rules.yml")

    def test_parse_empty_rules_file(self):
        """Test parsing empty rules file."""
        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                "rules: []"
            )

            rules = parse_rules("test_rules.yml")
            self.assertEqual(len(rules), 0)

    def test_parse_malformed_yaml(self):
        """Test parsing malformed YAML with unclosed brackets."""
        malformed_yaml = """
rules:
  - name: "Malformed rule"
    condition:
      parameter: "lufs"
      operator: ">"
      value: -14.0
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: -0.1  # Missing closing bracket
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                malformed_yaml
            )

            with self.assertRaises(Exception):
                parse_rules("test_rules.yml")

    def test_parse_rules_with_logical_operators(self):
        """Test parsing rules with AND/OR operators."""
        yaml_with_and = """
rules:
  - name: "AND condition rule"
    condition:
      operator: "AND"
      conditions:
        - parameter: "lufs"
          operator: ">"
          value: -14.0
        - parameter: "spectral_centroid"
          operator: "<"
          value: 1000
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: -0.2
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                yaml_with_and
            )

            rules = parse_rules("test_rules.yml")

            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0]["condition"]["operator"], "AND")
            self.assertEqual(len(rules[0]["condition"]["conditions"]), 2)

    def test_parse_rules_with_or_operator(self):
        """Test parsing rules with OR operator."""
        yaml_with_or = """
rules:
  - name: "OR condition rule"
    condition:
      operator: "OR"
      conditions:
        - parameter: "lufs"
          operator: ">"
          value: -12.0
        - parameter: "peak_level"
          operator: ">"
          value: 0.9
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: 0.8
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                yaml_with_or
            )

            rules = parse_rules("test_rules.yml")

            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0]["condition"]["operator"], "OR")
            self.assertEqual(len(rules[0]["condition"]["conditions"]), 2)

    def test_parse_rules_with_not_operator(self):
        """Test parsing rules with NOT operator."""
        yaml_with_not = """
rules:
  - name: "NOT condition rule"
    condition:
      operator: "NOT"
      condition:
        parameter: "error_flag"
        operator: "=="
        value: 0
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: 1.0
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                yaml_with_not
            )

            rules = parse_rules("test_rules.yml")

            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0]["condition"]["operator"], "NOT")
            self.assertIsNotNone(rules[0]["condition"]["condition"])

    def test_parse_rule_with_priority(self):
        """Test parsing rules with priority field."""
        yaml_with_priority = """
rules:
  - name: "High priority rule"
    priority: 100
    condition:
      parameter: "lufs"
      operator: ">"
      value: -14.0
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: -0.3
  - name: "Low priority rule"
    priority: 10
    condition:
      parameter: "spectral_centroid"
      operator: ">"
      value: 5000
    action:
      type: "set_parameter"
      target:
        track: 2
        parameter: "filter_cutoff"
        value: 0.7
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                yaml_with_priority
            )

            rules = parse_rules("test_rules.yml")

            self.assertEqual(len(rules), 2)
            self.assertEqual(rules[0]["priority"], 100)
            self.assertEqual(rules[1]["priority"], 10)

    def test_parse_nested_conditions(self):
        """Test parsing deeply nested conditions."""
        yaml_nested = """
rules:
  - name: "Complex nested rule"
    condition:
      operator: "AND"
      conditions:
        - parameter: "lufs"
          operator: ">"
          value: -14.0
        - operator: "OR"
          conditions:
            - parameter: "spectral_centroid"
              operator: "<"
              value: 1000
            - parameter: "peak_level"
              operator: ">"
              value: 0.8
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: -0.2
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                yaml_nested
            )

            rules = parse_rules("test_rules.yml")

            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0]["condition"]["operator"], "AND")
            # Check nested structure
            nested_or = rules[0]["condition"]["conditions"][1]
            self.assertEqual(nested_or["operator"], "OR")


class TestRulesEngine(unittest.TestCase):
    """Test rules engine evaluation."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = RulesEngine()

        # Test rule configuration
        self.test_rules = [
            {
                "name": "Test Rule 1",
                "priority": 50,
                "condition": {"parameter": "lufs", "operator": ">", "value": -14.0},
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 1, "parameter": "volume", "value": -0.1},
                },
            },
            {
                "name": "Test Rule 2",
                "priority": 100,  # Higher priority
                "condition": {
                    "parameter": "spectral_centroid",
                    "operator": "<",
                    "value": 1000,
                },
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 2, "parameter": "filter_cutoff", "value": 0.5},
                },
            },
        ]

        # Test parameters
        self.test_parameters = {
            "lufs": -15.0,  # Should trigger rule 1
            "spectral_centroid": 800,  # Should trigger rule 2
            "peak_level": 0.9,
        }

    def test_evaluate_rules_priority_ordering(self):
        """Test that higher priority rules are evaluated first."""
        self.engine.load_rules(self.test_rules)
        mock_params = {"lufs": -15.0, "spectral_centroid": 800, "peak_level": 0.9}

        actions = self.engine.evaluate_rules(mock_params)

        # Both rules should trigger, but higher priority rule (rule 2) should come first
        self.assertEqual(len(actions), 2)
        # Rule 2 has priority 100, should be first
        self.assertEqual(actions[0]["target"]["parameter"], "filter_cutoff")
        self.assertEqual(actions[0]["target"]["value"], 0.5)
        # Rule 1 has priority 50, should be second
        self.assertEqual(actions[1]["target"]["parameter"], "volume")
        self.assertEqual(actions[1]["target"]["value"], -0.1)

    def test_evaluate_rules_no_priority_default_ordering(self):
        """Test rule ordering when no priority specified."""
        rules_no_priority = [
            {
                "name": "First Rule",
                "condition": {"parameter": "lufs", "operator": ">", "value": -14.0},
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 1, "parameter": "volume", "value": -0.1},
                },
            },
            {
                "name": "Second Rule",
                "condition": {
                    "parameter": "spectral_centroid",
                    "operator": "<",
                    "value": 1000,
                },
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 2, "parameter": "filter_cutoff", "value": 0.5},
                },
            },
        ]

        self.engine.load_rules(rules_no_priority)
        mock_params = {"lufs": -15.0, "spectral_centroid": 800, "peak_level": 0.9}

        actions = self.engine.evaluate_rules(mock_params)

        # Should maintain original order when no priority
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["target"]["parameter"], "volume")  # First rule
        self.assertEqual(
            actions[1]["target"]["parameter"], "filter_cutoff"
        )  # Second rule

    def test_evaluate_rules_complex_logical_conditions(self):
        """Test evaluation of complex AND/OR/NOT conditions."""
        complex_rule = {
            "name": "Complex Rule",
            "priority": 50,
            "condition": {
                "operator": "AND",
                "conditions": [
                    {"parameter": "lufs", "operator": ">", "value": -14.0},
                    {
                        "operator": "OR",
                        "conditions": [
                            {
                                "parameter": "spectral_centroid",
                                "operator": "<",
                                "value": 1000,
                            },
                            {"parameter": "peak_level", "operator": ">", "value": 0.8},
                        ],
                    },
                ],
            },
            "action": {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": -0.2},
            },
        }

        self.engine.load_rules([complex_rule])

        # Test case 1: LUFS > -14 AND (spectral < 1000 OR peak > 0.8)
        mock_params_1 = {"lufs": -15.0, "spectral_centroid": 800, "peak_level": 0.9}
        actions_1 = self.engine.evaluate_rules(mock_params_1)
        self.assertEqual(len(actions_1), 1)  # Should trigger

        # Test case 2: LUFS > -14 AND (spectral >= 1000 OR peak <= 0.8)
        mock_params_2 = {"lufs": -15.0, "spectral_centroid": 1000, "peak_level": 0.7}
        actions_2 = self.engine.evaluate_rules(mock_params_2)
        self.assertEqual(len(actions_2), 0)  # Should NOT trigger

        # Test case 3: LUFS <= -14 (first condition false)
        mock_params_3 = {"lufs": -16.0, "spectral_centroid": 800, "peak_level": 0.9}
        actions_3 = self.engine.evaluate_rules(mock_params_3)
        self.assertEqual(len(actions_3), 0)  # Should NOT trigger

    def test_evaluate_rules_not_operator(self):
        """Test NOT operator evaluation."""
        not_rule = {
            "name": "NOT Rule",
            "condition": {
                "operator": "NOT",
                "condition": {"parameter": "error_flag", "operator": "==", "value": 0},
            },
            "action": {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": 1.0},
            },
        }

        self.engine.load_rules([not_rule])

        # Test case 1: error_flag = 0 (condition is false), so NOT makes it true
        mock_params_1 = {"error_flag": 0}
        actions_1 = self.engine.evaluate_rules(mock_params_1)
        self.assertEqual(len(actions_1), 1)

        # Test case 2: error_flag = 1 (condition is true), so NOT makes it false
        mock_params_2 = {"error_flag": 1}
        actions_2 = self.engine.evaluate_rules(mock_params_2)
        self.assertEqual(len(actions_2), 0)

    def test_rules_engine_error_handling(self):
        """Test rules engine handles invalid operators gracefully."""
        invalid_rule = {
            "name": "Invalid Rule",
            "condition": {"parameter": "lufs", "operator": "INVALID", "value": -14.0},
            "action": {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": -0.1},
            },
        }

        self.engine.load_rules([invalid_rule])

        with self.assertLogs(level="ERROR") as log:
            actions = self.engine.evaluate_rules({"lufs": -15.0})
            self.assertEqual(len(actions), 0)  # Should handle gracefully

    def test_rules_engine_performance(self):
        """Test rules engine performance with many rules."""
        # Create 1000 rules to test performance
        many_rules = [
            {
                "name": f"Rule {i}",
                "priority": i % 100,
                "condition": {"parameter": "param", "operator": ">", "value": i},
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 1, "parameter": "volume", "value": 0.5},
                },
            }
            for i in range(1000)
        ]

        self.engine.load_rules(many_rules)

        import time

        start_time = time.time()
        actions = self.engine.evaluate_rules({"param": 500})
        end_time = time.time()

        # Should complete quickly even with many rules
        self.assertLess(end_time - start_time, 0.1)  # Should be under 100ms
        self.assertEqual(len(actions), 1)  # Only rule 500 should trigger


if __name__ == "__main__":
    # Run tests with coverage reporting
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
