"""
Rules Engine Module for VST Audio Analysis

Evaluates rules and executes MCP actions based on audio analysis parameters.

Usage:
    from scripts.analysis.rules_engine import RulesEngine
    from scripts.analysis.rules_parser import RulesParser

    parser = RulesParser()
    rules = parser.parse('configs/analysis/lufs_compressor.yml')

    engine = RulesEngine(
        host='localhost',
        port=9877,
        track_index=0,
        device_index=0
    )
    engine.evaluate_and_execute(rules, parameter_values)
"""

import socket
import json
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from rules_parser import Rule, Condition, Action, RulesParseError


@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation."""

    rule_name: str
    fired: bool
    timestamp: float = 0.0
    error: Optional[str] = None


class RulesEngineError(Exception):
    """Raised when a rule evaluation or action execution fails."""

    pass


class RulesEngine:
    """Evaluates rules and executes MCP actions."""

    # Timeout for MCP command responses (seconds)
    MCP_TIMEOUT = 5.0
    # Buffer size for receiving responses
    BUFFER_SIZE = 8192

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9877,
        track_index: int = 0,
        device_index: int = 0,
        verbose: bool = False,
    ):
        """
        Initialize the rules engine.

        Args:
            host: Ableton MCP server host
            port: Ableton MCP server port (TCP)
            track_index: Default track index for actions
            device_index: Default device index for actions
            verbose: Enable verbose logging
        """
        self.host = host
        self.port = port
        self.track_index = track_index
        self.device_index = device_index
        self.verbose = verbose

        # Rule cooldown tracking to prevent oscillation
        # Maps rule name to last execution timestamp
        self.cooldowns: Dict[str, float] = {}

    def evaluate_and_execute(
        self,
        rules: List[Rule],
        parameter_values: Dict[str, float],
        cooldown_seconds: float = 0.0,
    ) -> List[RuleEvaluationResult]:
        """
        Evaluate all rules and execute actions for matching conditions.

        Args:
            rules: List of Rule objects (sorted by priority)
            parameter_values: Dictionary of parameter values (e.g., {"0:0": -14.5})
            cooldown_seconds: Minimum time between firing same rule (prevents oscillation)

        Returns:
            List of RuleEvaluationResult objects
        """
        results = []

        for rule in rules:
            result = RuleEvaluationResult(
                rule_name=rule.name, fired=False, timestamp=time.time()
            )

            try:
                # Check cooldown
                if cooldown_seconds > 0:
                    last_fired = self.cooldowns.get(rule.name, 0.0)
                    time_since_last_fired = time.time() - last_fired
                    if time_since_last_fired < cooldown_seconds:
                        if self.verbose:
                            print(
                                f"[RULE] '{rule.name}' on cooldown "
                                f"({time_since_last_fired:.2f}s < {cooldown_seconds}s)"
                            )
                        result.fired = False
                        results.append(result)
                        continue

                # Evaluate condition
                condition_met = self._evaluate_condition(
                    rule.condition, parameter_values
                )

                if condition_met:
                    if self.verbose:
                        print(f"[RULE] '{rule.name}' fired - priority {rule.priority}")

                    # Execute action
                    self._execute_action(rule.action)

                    # Update cooldown
                    if cooldown_seconds > 0:
                        self.cooldowns[rule.name] = time.time()

                    result.fired = True
                else:
                    if self.verbose:
                        print(f"[RULE] '{rule.name}' not met")

            except Exception as e:
                error_msg = str(e)
                result.error = error_msg
                print(f"[ERROR] Rule '{rule.name}': {error_msg}")

            results.append(result)

        return results

    def _evaluate_condition(
        self, condition: Condition, parameter_values: Dict[str, float]
    ) -> bool:
        """
        Evaluate a single condition.

        Args:
            condition: Condition object to evaluate
            parameter_values: Dictionary of current parameter values

        Returns:
            True if condition is met, False otherwise
        """
        operator = condition.operator

        # Logical operators
        if operator == "AND":
            if not condition.conditions:
                raise RulesEngineError("AND operator requires conditions")
            # All sub-conditions must be true
            return all(
                self._evaluate_condition(cond, parameter_values)
                for cond in condition.conditions
            )

        elif operator == "OR":
            if not condition.conditions:
                raise RulesEngineError("OR operator requires conditions")
            # At least one sub-condition must be true
            return any(
                self._evaluate_condition(cond, parameter_values)
                for cond in condition.conditions
            )

        elif operator == "NOT":
            if not condition.conditions:
                raise RulesEngineError("NOT operator requires conditions")
            # Sub-condition must be false
            return not self._evaluate_condition(
                condition.conditions[0], parameter_values
            )

        # Comparison operators
        elif operator in {">", "<", "==", "!=", ">=", "<="}:
            # Resolve param1 (could be parameter reference or literal value)
            val1 = self._resolve_value(condition.param1, parameter_values)
            val2 = self._resolve_value(condition.param2, parameter_values)

            # Perform comparison
            if operator == ">":
                return val1 > val2
            elif operator == "<":
                return val1 < val2
            elif operator == "==":
                return val1 == val2
            elif operator == "!=":
                return val1 != val2
            elif operator == ">=":
                return val1 >= val2
            elif operator == "<=":
                return val1 <= val2
            else:
                raise RulesEngineError(f"Unknown comparison operator: {operator}")

        else:
            raise RulesEngineError(f"Unknown operator: {operator}")

    def _resolve_value(self, value: str, parameter_values: Dict[str, float]) -> float:
        """
        Resolve a value to a float.

        If the value is a parameter reference (format: "track:device:param"),
        look up the current value from parameter_values.
        Otherwise, parse it as a float literal.

        Args:
            value: Value to resolve
            parameter_values: Dictionary of current parameter values

        Returns:
            Float value
        """
        # Check if it's a parameter reference (contains ":")
        if ":" in value:
            if value not in parameter_values:
                raise RulesEngineError(
                    f"Parameter reference '{value}' not found in current values"
                )
            return float(parameter_values[value])
        else:
            # Parse as float literal
            try:
                return float(value)
            except ValueError:
                raise RulesEngineError(
                    f"Cannot parse '{value}' as float or parameter reference"
                )

    def _execute_action(self, action: Action) -> None:
        """
        Execute an action via MCP server.

        Args:
            action: Action object to execute

        Raises:
            RulesEngineError: If action execution fails
        """
        command = self._build_command(action)

        try:
            # Create TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.MCP_TIMEOUT)
            sock.connect((self.host, self.port))

            # Send command
            command_json = json.dumps(command)
            sock.sendall(command_json.encode("utf-8"))

            # Receive response
            response_data = sock.recv(self.BUFFER_SIZE).decode("utf-8")

            # Parse response
            try:
                response = json.loads(response_data)
            except json.JSONDecodeError as e:
                raise RulesEngineError(f"Invalid JSON response: {e}")

            # Check for errors in response
            if isinstance(response, dict) and "error" in response:
                raise RulesEngineError(f"MCP error: {response['error']}")

            if self.verbose:
                print(f"[ACTION] {action.type} executed: {command['params']}")

            sock.close()

        except socket.timeout:
            raise RulesEngineError(f"MCP server timeout after {self.MCP_TIMEOUT}s")
        except socket.error as e:
            raise RulesEngineError(f"Socket error: {e}")
        finally:
            sock.close()

    def _build_command(self, action: Action) -> Dict[str, Any]:
        """
        Build an MCP command from an action.

        Args:
            action: Action object

        Returns:
            MCP command dictionary
        """
        params = action.params.copy()

        # Apply default track/device index if not specified
        if "track_index" not in params:
            params["track_index"] = self.track_index
        if "device_index" not in params:
            params["device_index"] = self.device_index

        # Build command based on action type
        if action.type == "set_parameter":
            # Validate required params
            if "parameter_index" not in params:
                raise RulesEngineError("set_parameter action requires parameter_index")
            if "value" not in params:
                raise RulesEngineError("set_parameter action requires value")

            return {"type": "set_device_parameter", "params": params}

        elif action.type == "set_volume":
            # Normalize volume if given as dB
            if "volume" in params:
                vol = params["volume"]
                # If it's a negative dB value, convert to normalized (0.0-1.0)
                if isinstance(vol, (int, float)) and vol < 0:
                    # Assume dB scale: -60 dB = 0.0, 0 dB = 1.0
                    params["volume"] = max(0.0, min(1.0, (vol + 60.0) / 60.0))

            return {"type": "set_track_volume", "params": params}

        elif action.type == "set_pan":
            if "pan" not in params:
                raise RulesEngineError("set_pan action requires pan parameter")
            return {"type": "set_track_pan", "params": params}

        elif action.type == "set_tempo":
            if "tempo" not in params:
                raise RulesEngineError("set_tempo action requires tempo parameter")
            return {"type": "set_tempo", "params": params}

        elif action.type == "fire_clip":
            if "clip_index" not in params:
                raise RulesEngineError("fire_clip action requires clip_index")
            return {"type": "fire_clip", "params": params}

        elif action.type == "start_playback":
            return {"type": "start_playback", "params": params}

        elif action.type == "stop_playback":
            return {"type": "stop_playback", "params": params}

        elif action.type == "start_recording":
            return {"type": "start_recording", "params": params}

        elif action.type == "stop_recording":
            return {"type": "stop_recording", "params": params}

        else:
            raise RulesEngineError(f"Unknown action type: {action.type}")

    def clear_cooldowns(self) -> None:
        """Clear all rule cooldowns."""
        self.cooldowns.clear()
        if self.verbose:
            print("[RULE] All cooldowns cleared")


class PollingRulesEngine(RulesEngine):
    """
    Rules engine that continuously polls parameters and evaluates rules.

    Usage:
        engine = PollingRulesEngine(
            track_index=0,
            device_index=0,
            polling_rate_hz=10
        )
        engine.start(rules_file='configs/analysis/lufs_compressor.yml')
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9877,
        track_index: int = 0,
        device_index: int = 0,
        polling_rate_hz: float = 10.0,
        cooldown_seconds: float = 0.5,
        verbose: bool = False,
    ):
        """
        Initialize the polling rules engine.

        Args:
            host: Ableton MCP server host
            port: Ableton MCP server port (TCP)
            track_index: Track index for parameter polling
            device_index: Device index for parameter polling
            polling_rate_hz: How often to poll parameters (Hz)
            cooldown_seconds: Minimum time between firing same rule
            verbose: Enable verbose logging
        """
        super().__init__(host, port, track_index, device_index, verbose)
        self.polling_rate_hz = polling_rate_hz
        self.cooldown_seconds = cooldown_seconds
        self.running = False
        self.rules: Optional[List[Rule]] = None

    def start(self, rules_file: str, duration_seconds: float = 0.0) -> None:
        """
        Start polling parameters and evaluating rules.

        Args:
            rules_file: Path to YAML rule configuration file
            duration_seconds: How long to run (0 = infinite)

        Raises:
            RulesParseError: If rules file cannot be parsed
        """
        from scripts.analysis.rules_parser import RulesParser

        # Parse rules
        parser = RulesParser()
        self.rules = parser.parse(rules_file)

        print(f"[ENGINE] Loaded {len(self.rules)} rules from {rules_file}")
        print(f"[ENGINE] Polling rate: {self.polling_rate_hz} Hz")
        print(f"[ENGINE] Cooldown: {self.cooldown_seconds} seconds")

        if duration_seconds > 0:
            print(f"[ENGINE] Duration: {duration_seconds} seconds")
        else:
            print(f"[ENGINE] Duration: infinite (Ctrl+C to stop)")

        self.running = True
        start_time = time.time()

        try:
            poll_interval = 1.0 / self.polling_rate_hz
            poll_count = 0

            while self.running:
                # Poll parameters
                parameter_values = self._poll_parameters()

                # Evaluate and execute rules
                if self.rules and parameter_values:
                    results = self.evaluate_and_execute(
                        self.rules, parameter_values, self.cooldown_seconds
                    )

                    # Track firing stats
                    fired_count = sum(1 for r in results if r.fired)
                    if fired_count > 0 and self.verbose:
                        print(f"[ENGINE] {fired_count} rule(s) fired")

                poll_count += 1

                # Progress display every 50 polls
                if poll_count % 50 == 0:
                    elapsed = time.time() - start_time
                    actual_hz = poll_count / elapsed
                    print(
                        f"[ENGINE] Polls: {poll_count} | "
                        f"Rate: {actual_hz:.1f} Hz | "
                        f"Elapsed: {elapsed:.1f}s"
                    )

                # Check duration limit
                if duration_seconds > 0:
                    if time.time() - start_time >= duration_seconds:
                        print(f"[ENGINE] Duration limit reached ({duration_seconds}s)")
                        break

                # Wait for next poll
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n[ENGINE] Interrupted by user")

        finally:
            self.running = False
            total_time = time.time() - start_time
            print(f"[ENGINE] Stopped after {total_time:.1f}s ({poll_count} polls)")

    def _poll_parameters(self) -> Dict[str, float]:
        """
        Poll current parameter values from MCP server.

        Returns:
            Dictionary mapping "track:device:param" to values
        """
        try:
            # Create TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.MCP_TIMEOUT)
            sock.connect((self.host, self.port))

            # Send get_device_parameters command
            command = {
                "type": "get_device_parameters",
                "params": {
                    "track_index": self.track_index,
                    "device_index": self.device_index,
                },
            }
            command_json = json.dumps(command)
            sock.sendall(command_json.encode("utf-8"))

            # Receive response
            response_data = sock.recv(self.BUFFER_SIZE).decode("utf-8")
            sock.close()

            # Parse response
            try:
                response = json.loads(response_data)
            except json.JSONDecodeError:
                return {}

            if not isinstance(response, dict):
                return {}

            # Extract parameter values
            parameter_values = {}
            if "params" in response and isinstance(response["params"], list):
                for param in response["params"]:
                    if isinstance(param, dict) and "value" in param:
                        # Parameter index
                        param_idx = param.get("index", -1)
                        key = f"{self.track_index}:{self.device_index}:{param_idx}"
                        parameter_values[key] = param["value"]

            return parameter_values

        except (socket.timeout, socket.error, json.JSONDecodeError) as e:
            if self.verbose:
                print(f"[WARN] Failed to poll parameters: {e}")
            return {}

    def stop(self) -> None:
        """Stop the polling rules engine."""
        self.running = False
