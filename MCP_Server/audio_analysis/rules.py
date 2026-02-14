"""
Rule-Based Decision System for VST Audio Analysis

This module provides a YAML-configurable rule engine for making control decisions
based on real-time audio analysis parameters from VST plugins.

Architecture:
- Rules are defined in YAML files
- Each rule has conditions, actions, and optional cooldowns
- Rule Engine evaluates rules against ParameterSnapshot data
- Actions are executed via MCP client interface
- Supports cooldowns to prevent oscillation
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Callable, Optional, List, Dict, Any, Union
import logging
import yaml
from pathlib import Path

from .polling import ParameterSnapshot, ParameterConfig

logger = logging.getLogger(__name__)


class Operator(Enum):
    """Comparison operators for rule conditions."""

    GT = ">"  # Greater than
    GTE = ">="  # Greater than or equal
    LT = "<"  # Less than
    LTE = "<="  # Less than or equal
    EQ = "=="  # Equal
    NEQ = "!="  # Not equal
    IN = "in"  # In list
    NOT_IN = "not_in"  # Not in list


class TimeUnit(Enum):
    """Time units for cooldowns and thresholds."""

    SECONDS = "seconds"
    SAMPLES = "samples"


@dataclass
class Condition:
    """A single condition that can be evaluated against a ParameterSnapshot."""

    parameter_index: int  # Index of parameter to check
    operator: Operator  # Comparison operator
    threshold: float  # Threshold value (in normalized 0.0-1.0 range)
    parameter_name: str = ""  # Optional parameter name for readability

    def evaluate(self, values: Dict[int, float]) -> bool:
        """Evaluate this condition against parameter values.

        Args:
            values: Dict mapping parameter_index -> normalized_value (0.0-1.0)

        Returns:
            True if condition is satisfied, False otherwise
        """
        value = values.get(self.parameter_index)
        if value is None:
            logger.warning(
                f"Parameter index {self.parameter_index} not found in snapshot. Condition fails."
            )
            return False

        try:
            if self.operator == Operator.GT:
                return value > self.threshold
            elif self.operator == Operator.GTE:
                return value >= self.threshold
            elif self.operator == Operator.LT:
                return value < self.threshold
            elif self.operator == Operator.LTE:
                return value <= self.threshold
            elif self.operator == Operator.EQ:
                return abs(value - self.threshold) < 1e-6
            elif self.operator == Operator.NEQ:
                return abs(value - self.threshold) >= 1e-6
            elif self.operator == Operator.IN:
                return value in self.threshold  # threshold is a list
            elif self.operator == Operator.NOT_IN:
                return value not in self.threshold
            else:
                logger.error(f"Unknown operator: {self.operator}")
                return False
        except (TypeError, AttributeError) as e:
            logger.error(f"Error evaluating condition: {e}")
            return False


@dataclass
class SetParameterAction:
    """Action to set a device parameter to a specific value."""

    track_index: int
    device_index: int
    parameter_index: int
    target_value: float  # Normalized value (0.0-1.0)
    action_type: str = "set_parameter"  # For YAML serialization


@dataclass
class TriggerClipAction:
    """Action to trigger a clip slot."""

    track_index: int
    clip_index: int
    action_type: str = "trigger_clip"


@dataclass
class StopClipAction:
    """Action to stop a clip slot."""

    track_index: int
    clip_index: int
    action_type: str = "stop_clip"


@dataclass
class SetTrackVolumeAction:
    """Action to set track volume."""

    track_index: int
    volume: float  # Normalized value (0.0-1.0)
    action_type: str = "set_volume"


ActionType = Union[
    SetParameterAction, TriggerClipAction, StopClipAction, SetTrackVolumeAction
]


@dataclass
class Action:
    """An action to execute when rule conditions are met."""

    type: str  # "set_parameter", "trigger_clip", "stop_clip", "set_volume"
    track_index: int
    device_index: int = 0  # For device-related actions
    parameter_index: int = 0  # For parameter actions
    clip_index: int = 0  # For clip actions
    target_value: float = 0.0  # For parameter/volume actions (normalized 0.0-1.0)
    data: Optional[Dict[str, Any]] = None  # Additional action-specific data

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary for execution."""
        return {
            "type": self.type,
            "track_index": self.track_index,
            "device_index": self.device_index,
            "parameter_index": self.parameter_index,
            "clip_index": self.clip_index,
            "target_value": self.target_value,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        """Create Action from dictionary (YAML parsing)."""
        return cls(
            type=data["type"],
            track_index=data["track_index"],
            device_index=data.get("device_index", 0),
            parameter_index=data.get("parameter_index", 0),
            clip_index=data.get("clip_index", 0),
            target_value=data.get("target_value", 0.0),
            data=data.get("data"),
        )


@dataclass
class Rule:
    """A rule that triggers actions when conditions are met."""

    id: str  # Unique rule identifier
    name: str  # Human-readable name
    conditions: List[Condition]  # All conditions must be met (AND logic)
    actions: List[Action]  # Actions to execute when satisfied
    enabled: bool = True  # Can be disabled without removing
    cooldown_seconds: float = (
        0.0  # Minimum time between triggers (prevents oscillation)
    )
    description: str = ""  # Optional description
    last_triggered: float = 0.0  # Timestamp of last trigger (internal state)
    trigger_count: int = 0  # Number of times triggered (internal state)

    def can_trigger(self) -> bool:
        """Check if cooldown period has elapsed since last trigger."""
        if self.cooldown_seconds <= 0:
            return True
        if self.last_triggered == 0.0:
            return True
        elapsed = time.time() - self.last_triggered
        return elapsed >= self.cooldown_seconds

    def evaluate(self, snapshot: ParameterSnapshot) -> bool:
        """Evaluate all conditions against a parameter snapshot.

        Args:
            snapshot: ParameterSnapshot containing current parameter values

        Returns:
            True if all conditions are satisfied and cooldown is met, False otherwise
        """
        if not self.enabled:
            return False

        if not self.can_trigger():
            logger.debug(f"Rule '{self.id}' on cooldown. Skipping.")
            return False

        # Evaluate all conditions (AND logic)
        for condition in self.conditions:
            if not condition.evaluate(snapshot.values):
                logger.debug(
                    f"Rule '{self.id}' condition failed: "
                    f"parameter {condition.parameter_index} "
                    f"{condition.operator.value} {condition.threshold}"
                )
                return False

        logger.info(f"Rule '{self.id}' conditions satisfied.")
        return True

    def mark_triggered(self):
        """Record that this rule was triggered."""
        self.last_triggered = time.time()
        self.trigger_count += 1
        logger.info(f"Rule '{self.id}' triggered (count: {self.trigger_count})")


@dataclass
class RuleSet:
    """A collection of rules loaded from a YAML configuration file."""

    id: str  # Unique rule set identifier
    name: str  # Human-readable name
    rules: List[Rule] = field(default_factory=list)
    description: str = ""
    enabled: bool = True  # Can disable entire rule set

    def evaluate_all(self, snapshot: ParameterSnapshot) -> List[Rule]:
        """Evaluate all rules in this rule set.

        Args:
            snapshot: ParameterSnapshot to evaluate against

        Returns:
            List of rules that should trigger (conditions + cooldown satisfied)
        """
        if not self.enabled:
            return []

        triggered_rules = []
        for rule in self.rules:
            if rule.evaluate(snapshot):
                triggered_rules.append(rule)

        return triggered_rules

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def enable_rule(self, rule_id: str):
        """Enable a specific rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
            logger.info(f"Rule '{rule_id}' enabled.")
        else:
            logger.warning(f"Rule '{rule_id}' not found.")

    def disable_rule(self, rule_id: str):
        """Disable a specific rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
            logger.info(f"Rule '{rule_id}' disabled.")
        else:
            logger.warning(f"Rule '{rule_id}' not found.")


class RuleEngine:
    """Main rule engine that evaluates rules and executes actions.

    The engine integrates with the AudioAnalysisPoller via callbacks:
    1. AudioAnalysisPoller triggers callback on each new snapshot
    2. RuleEngine.evaluate() checks all loaded rule sets
    3. For triggered rules, execute actions via MCP client
    4. Track rule statistics and handle errors gracefully
    """

    def __init__(self, mcp_client=None):
        """Initialize rule engine.

        Args:
            mcp_client: MCP client instance for executing actions
        """
        self.mcp_client = mcp_client
        self.rule_sets: List[RuleSet] = []
        self.executed_actions: List[Dict[str, Any]] = []  # Audit log
        self.stats = {
            "total_evaluations": 0,
            "total_triggers": 0,
            "total_action_executions": 0,
            "errors": 0,
        }

    def load_ruleset_from_yaml(self, yaml_path: Union[str, Path]) -> RuleSet:
        """Load a rule set from a YAML configuration file.

        Args:
            yaml_path: Path to YAML file

        Returns:
            Loaded RuleSet object

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is malformed
            ValueError: If rule configuration is invalid
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Rule file not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return self._parse_ruleset(data, yaml_path.stem)

    def _parse_ruleset(self, data: Dict[str, Any], source: str) -> RuleSet:
        """Parse rule set data from dictionary.

        Args:
            data: Dictionary from YAML parsing
            source: Source identifier (e.g., filename)

        Returns:
            Parsed RuleSet object
        """
        ruleset_id = data.get("id", source)
        name = data.get("name", ruleset_id)
        description = data.get("description", "")
        enabled = data.get("enabled", True)

        rules = []
        for rule_data in data.get("rules", []):
            rule = self._parse_rule(rule_data)
            rules.append(rule)

        ruleset = RuleSet(
            id=ruleset_id,
            name=name,
            rules=rules,
            description=description,
            enabled=enabled,
        )

        logger.info(f"Loaded rule set '{ruleset_id}' with {len(rules)} rules.")
        return ruleset

    def _parse_rule(self, data: Dict[str, Any]) -> Rule:
        """Parse a single rule from dictionary.

        Args:
            data: Dictionary from YAML parsing

        Returns:
            Parsed Rule object

        Raises:
            ValueError: If required fields are missing
        """
        rule_id = data.get("id")
        if not rule_id:
            raise ValueError("Rule must have 'id' field")

        name = data.get("name", rule_id)
        description = data.get("description", "")
        enabled = data.get("enabled", True)
        cooldown = data.get("cooldown_seconds", 0.0)

        # Parse conditions
        conditions = []
        for cond_data in data.get("conditions", []):
            param_idx = cond_data.get("parameter_index")
            op_str = cond_data.get("operator", ">=")
            threshold = cond_data.get("threshold")
            param_name = cond_data.get("parameter_name", "")

            try:
                operator = Operator(op_str)
            except ValueError:
                raise ValueError(
                    f"Invalid operator '{op_str}' in rule '{rule_id}'. "
                    f"Valid: {[op.value for op in Operator]}"
                )

            condition = Condition(
                parameter_index=param_idx,
                operator=operator,
                threshold=threshold,
                parameter_name=param_name,
            )
            conditions.append(condition)

        # Parse actions
        actions = []
        for act_data in data.get("actions", []):
            action = Action.from_dict(act_data)
            actions.append(action)

        return Rule(
            id=rule_id,
            name=name,
            conditions=conditions,
            actions=actions,
            enabled=enabled,
            cooldown_seconds=cooldown,
            description=description,
        )

    def add_ruleset(self, ruleset: RuleSet):
        """Add a rule set to the engine.

        Args:
            ruleset: RuleSet to add
        """
        self.rule_sets.append(ruleset)
        logger.info(f"Added rule set '{ruleset.id}' to engine.")

    def remove_ruleset(self, ruleset_id: str):
        """Remove a rule set from the engine.

        Args:
            ruleset_id: ID of rule set to remove
        """
        self.rule_sets = [rs for rs in self.rule_sets if rs.id != ruleset_id]
        logger.info(f"Removed rule set '{ruleset_id}' from engine.")

    def evaluate(self, snapshot: ParameterSnapshot) -> List[Dict[str, Any]]:
        """Evaluate all loaded rule sets against a parameter snapshot.

        This method is typically called by AudioAnalysisPoller via callback.

        Args:
            snapshot: Current parameter values

        Returns:
            List of action dictionaries that were executed
        """
        self.stats["total_evaluations"] += 1

        all_triggered_rules = []

        # Check all rule sets
        for ruleset in self.rule_sets:
            triggered = ruleset.evaluate_all(snapshot)
            all_triggered_rules.extend(triggered)

        if not all_triggered_rules:
            # logger.debug("No rules triggered.")
            return []

        # Execute actions for triggered rules
        executed = self._execute_triggered_rules(all_triggered_rules)

        # Update statistics
        self.stats["total_triggers"] += len(all_triggered_rules)
        self.stats["total_action_executions"] += len(executed)

        return executed

    def _execute_triggered_rules(
        self, triggered_rules: List[Rule]
    ) -> List[Dict[str, Any]]:
        """Execute actions for all triggered rules.

        Args:
            triggered_rules: List of rules that should trigger

        Returns:
            List of executed action descriptions
        """
        executed = []
        current_time = time.time()

        for rule in triggered_rules:
            # Mark rule as triggered (records timestamp)
            rule.mark_triggered()

            # Execute all actions
            for action in rule.actions:
                try:
                    result = self._execute_action(action, rule, current_time)
                    executed.append(result)
                except Exception as e:
                    logger.error(
                        f"Error executing action in rule '{rule.id}': {e}",
                        exc_info=True,
                    )
                    self.stats["errors"] += 1

        return executed

    def _execute_action(
        self, action: Action, rule: Rule, timestamp: float
    ) -> Dict[str, Any]:
        """Execute a single action via MCP client.

        Args:
            action: Action to execute
            rule: Rule that triggered the action
            timestamp: Current timestamp

        Returns:
            Dictionary describing the execution

        Raises:
            RuntimeError: If MCP client is not configured
            Exception: If action execution fails
        """
        if not self.mcp_client:
            raise RuntimeError("MCP client not configured. Cannot execute actions.")

        action_dict = action.to_dict()
        action_type = action.type

        # Route to appropriate MCP tool
        if action_type == "set_parameter":
            result = self.mcp_client.call_tool(
                "ableton-mcp-server",
                "set_device_parameter",
                {
                    "track_index": action.track_index,
                    "device_index": action.device_index,
                    "parameter_index": action.parameter_index,
                    "value": action.target_value,
                },
            )

        elif action_type == "trigger_clip":
            result = self.mcp_client.call_tool(
                "ableton-mcp-server",
                "fire_clip",
                {"track_index": action.track_index, "clip_index": action.clip_index},
            )

        elif action_type == "stop_clip":
            result = self.mcp_client.call_tool(
                "ableton-mcp-server",
                "stop_clip",
                {"track_index": action.track_index, "clip_index": action.clip_index},
            )

        elif action_type == "set_volume":
            result = self.mcp_client.call_tool(
                "ableton-mcp-server",
                "set_track_volume",
                {"track_index": action.track_index, "volume": action.target_value},
            )

        else:
            raise ValueError(f"Unknown action type: {action_type}")

        execution_record = {
            "timestamp": timestamp,
            "rule_id": rule.id,
            "action_type": action_type,
            "success": True,
            "result": result,
        }

        self.executed_actions.append(execution_record)
        logger.info(f"Executed action '{action_type}' from rule '{rule.id}'")

        return execution_record

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            **self.stats,
            "loaded_rulesets": len(self.rule_sets),
            "total_rules": sum(len(rs.rules) for rs in self.rule_sets),
            "total_actions": len(self.executed_actions),
        }

    def reset_stats(self):
        """Reset engine statistics."""
        self.stats = {
            "total_evaluations": 0,
            "total_triggers": 0,
            "total_action_executions": 0,
            "errors": 0,
        }
        self.executed_actions.clear()
        logger.info("Rule engine statistics reset.")

    def apply_to_poller(self, poller: "AudioAnalysisPoller") -> None:
        """Register this engine as a callback on a poller.

        This creates the integration: polling -> rule evaluation -> action execution.

        Args:
            poller: AudioAnalysisPoller instance to attach to
        """
        poller.add_callback(self.evaluate)
        logger.info("Rule engine registered as callback on poller.")
