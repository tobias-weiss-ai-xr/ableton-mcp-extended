"""
Rules Parser Module for VST Audio Analysis

Parses YAML-based rule configuration files for audio analysis to control decisions.

Usage:
    from scripts.analysis.rules_parser import RulesParser

    parser = RulesParser()
    rules = parser.parse('configs/analysis/lufs_compressor.yml')
"""

import yaml
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
@dataclass
class Condition:
    """Represents a condition in a rule."""

    operator: str  # >, <, ==, !=, >=, <=, AND, OR, NOT
    param1: Optional[str] = None  # Can be "track:device:param" or a value
    param2: Optional[str] = None  # Only for comparison operators
    conditions: Optional[List["Condition"]] = None  # Only for logical operators


@dataclass
class Action:
    """Represents an action to execute when a rule fires."""

    type: str  # set_parameter, set_volume, set_pan, set_tempo, fire_clip, etc.
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    """Represents a complete rule with name, priority, condition, and action."""

    name: str
    priority: int  # Lower number = higher priority
    condition: Condition
    action: Action


class RulesParseError(Exception):
    """Raised when a rule file cannot be parsed."""

    pass


class RulesParser:
    """Parses YAML rule configuration files."""

    # Supported operators
    COMPARISON_OPERATORS = {">", "<", "==", "!=", ">=", "<="}
    LOGICAL_OPERATORS = {"AND", "OR", "NOT"}

    # Supported action types
    SUPPORTED_ACTIONS = {
        "set_parameter",
        "set_volume",
        "set_pan",
        "set_tempo",
        "fire_clip",
        "start_playback",
        "stop_playback",
        "start_recording",
        "stop_recording",
    }

    def __init__(self):
        """Initialize the rules parser."""
        self.rules: List[Rule] = []

    def parse(self, filepath: str) -> List[Rule]:
        """
        Parse a YAML rule configuration file.

        Args:
            filepath: Path to the YAML rule file

        Returns:
            List of Rule objects sorted by priority (highest first)

        Raises:
            RulesParseError: If the file cannot be parsed
            FileNotFoundError: If the file does not exist
            yaml.YAMLError: If YAML syntax is invalid
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Rule file not found: {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise RulesParseError(f"YAML syntax error in {filepath}: {e}")
        except Exception as e:
            raise RulesParseError(f"Error reading {filepath}: {e}")

        if not data:
            raise RulesParseError(f"Empty rule file: {filepath}")

        if "rules" not in data:
            raise RulesParseError(f"Missing 'rules' section in {filepath}")

        self.rules = []
        for i, rule_data in enumerate(data["rules"]):
            try:
                rule = self._parse_rule(rule_data, filepath, i)
                self.rules.append(rule)
            except RulesParseError as e:
                raise RulesParseError(f"Error in rule {i + 1}: {e}")

        # Sort rules by priority (lower number = higher priority)
        self.rules.sort(key=lambda r: r.priority)

        return self.rules

    def _parse_rule(self, rule_data: Dict[str, Any], filepath: str, index: int) -> Rule:
        """Parse a single rule from the YAML data."""
        # Validate required fields
        required_fields = ["name", "priority", "condition", "action"]
        for field in required_fields:
            if field not in rule_data:
                raise RulesParseError(f"Missing required field: '{field}'")

        name = rule_data["name"]
        priority = rule_data["priority"]

        if not isinstance(name, str):
            raise RulesParseError(f"'name' must be a string, got {type(name).__name__}")

        if not isinstance(priority, int) or priority < 0:
            raise RulesParseError(
                f"'priority' must be a non-negative integer, got {priority}"
            )

        # Parse condition
        condition = self._parse_condition(
            rule_data["condition"], f"{filepath}:rule {index + 1}"
        )

        # Parse action
        action = self._parse_action(rule_data["action"], f"{filepath}:rule {index + 1}")

        return Rule(name=name, priority=priority, condition=condition, action=action)

    def _parse_condition(
        self, condition_data: Dict[str, Any], context: str
    ) -> Condition:
        """Parse a condition from the YAML data."""
        if "operator" not in condition_data:
            raise RulesParseError(f"Missing 'operator' in condition")

        operator = condition_data["operator"]

        # Logical operators
        if operator in self.LOGICAL_OPERATORS:
            if operator == "NOT":
                # NOT has a single condition
                if "condition" not in condition_data:
                    raise RulesParseError(f"NOT operator requires 'condition' field")
                sub_condition = self._parse_condition(
                    condition_data["condition"], context
                )
                return Condition(operator=operator, conditions=[sub_condition])
            else:
                # AND/OR have multiple conditions
                if "conditions" not in condition_data:
                    raise RulesParseError(
                        f"{operator} operator requires 'conditions' list"
                    )
                if not isinstance(condition_data["conditions"], list):
                    raise RulesParseError(f"{operator} 'conditions' must be a list")
                if len(condition_data["conditions"]) < 2:
                    raise RulesParseError(f"{operator} requires at least 2 conditions")

                sub_conditions = []
                for i, sub_cond in enumerate(condition_data["conditions"]):
                    sub_condition = self._parse_condition(
                        sub_cond, f"{context}:condition {i + 1}"
                    )
                    sub_conditions.append(sub_condition)

                return Condition(operator=operator, conditions=sub_conditions)

        # Comparison operators
        elif operator in self.COMPARISON_OPERATORS:
            if "param1" not in condition_data:
                raise RulesParseError(
                    f"Missing 'param1' for comparison operator '{operator}'"
                )
            if "param2" not in condition_data:
                raise RulesParseError(
                    f"Missing 'param2' for comparison operator '{operator}'"
                )

            param1 = condition_data["param1"]
            param2 = condition_data["param2"]

            if not isinstance(param1, str):
                raise RulesParseError(
                    f"'param1' must be a string, got {type(param1).__name__}"
                )
            if not isinstance(param2, str):
                raise RulesParseError(
                    f"'param2' must be a string, got {type(param2).__name__}"
                )

            return Condition(operator=operator, param1=param1, param2=param2)

        else:
            raise RulesParseError(
                f"Unknown operator '{operator}'. "
                f"Comparison operators: {', '.join(self.COMPARISON_OPERATORS)}. "
                f"Logical operators: {', '.join(self.LOGICAL_OPERATORS)}."
            )

    def _parse_action(self, action_data: Dict[str, Any], context: str) -> Action:
        """Parse an action from the YAML data."""
        if "type" not in action_data:
            raise RulesParseError(f"Missing 'type' in action")

        action_type = action_data["type"]

        if action_type not in self.SUPPORTED_ACTIONS:
            raise RulesParseError(
                f"Unknown action type '{action_type}'. "
                f"Supported actions: {', '.join(sorted(self.SUPPORTED_ACTIONS))}."
            )

        params = {}
        if "params" in action_data:
            if not isinstance(action_data["params"], dict):
                raise RulesParseError(f"'params' must be a dictionary")
            params = action_data["params"]

        return Action(type=action_type, params=params)

    def validate_rules(
        self, parameter_mappings: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Validate rules against parameter mappings.

        Args:
            parameter_mappings: Dictionary mapping "track:device:param" to parameter info

        Returns:
            List of warning messages (empty if no warnings)
        """
        warnings = []

        for rule in self.rules:
            # Check parameter references in conditions
            self._validate_condition(
                rule.condition, parameter_mappings, rule.name, warnings
            )

        return warnings

    def _validate_condition(
        self,
        condition: Condition,
        parameter_mappings: Dict[str, Dict[str, Any]],
        rule_name: str,
        warnings: List[str],
    ):
        """Recursively validate a condition against parameter mappings."""
        if condition.operator in self.LOGICAL_OPERATORS and condition.conditions:
            # Validate sub-conditions
            for sub_cond in condition.conditions:
                self._validate_condition(
                    sub_cond, parameter_mappings, rule_name, warnings
                )
        elif condition.operator in self.COMPARISON_OPERATORS:
            # Check if param1 is a parameter reference (format: "track:device:param")
            if ":" in condition.param1:
                param_key = condition.param1
                if param_key not in parameter_mappings:
                    warnings.append(
                        f"Rule '{rule_name}': Parameter reference '{param_key}' "
                        f"not found in parameter mappings"
                    )
