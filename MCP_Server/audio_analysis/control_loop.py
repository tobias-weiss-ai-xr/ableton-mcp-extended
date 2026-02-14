"""
Responsive Control Loop for VST Audio Analysis

This module provides the integration layer between the polling system and rule engine,
creating a complete feedback loop: poll → evaluate → act → poll.

Architecture:
- AudioAnalysisController manages lifecycle (initialization, start, stop)
- Poller continuously reads VST parameters at configured rate
- Rule Engine evaluates rules against each snapshot
- Actions are executed via MCP client when rules trigger
- Statistics and monitoring available in real-time
"""

import time
import signal
import logging
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

from .polling import AudioAnalysisPoller, ParameterConfig, ParameterSnapshot
from .rules import RuleEngine, RuleSet

logger = logging.getLogger(__name__)


class AudioAnalysisController:
    """
    Main controller for audio analysis-based feedback control.

    Integrates polling and rule evaluation into a cohesive system:
    1. Configures poller with VST parameters to monitor
    2. Loads rule sets from YAML files
    3. Registers engine as poller callback
    4. Manages start/stop lifecycle
    5. Provides monitoring and statistics

    Example:
        controller = AudioAnalysisController(
            track_index=0,
            device_index=0,
            params_to_poll=[
                ParameterConfig(index=0, name="LUFS", min_value=-70, max_value=5, unit="LUFS"),
            ],
            mcp_client=mcp_client,
        )
        controller.load_ruleset("MCP_Server/audio_analysis/example_rules.yaml")
        controller.start()
        # ... poll loop runs automatically
        controller.stop()
    """

    def __init__(
        self,
        track_index: int,
        device_index: int,
        params_to_poll: List[ParameterConfig],
        mcp_client: Optional[Any] = None,
        update_rate_hz: float = 10.0,
        buffer_size: int = 1000,
    ):
        """
        Initialize audio analysis controller.

        Args:
            track_index: Ableton track index containing VST device
            device_index: VST device index on track
            params_to_poll: List of parameter configurations to monitor
            mcp_client: MCP client instance for Ableton communication
            update_rate_hz: Polling frequency in Hz (default: 10 Hz)
            buffer_size: Max snapshots to store in circular buffer
        """
        self.track_index = track_index
        self.device_index = device_index
        self.params_to_poll = params_to_poll
        self.mcp_client = mcp_client

        # Initialize components
        self.poller = AudioAnalysisPoller(
            track_index=track_index,
            device_index=device_index,
            params_to_poll=params_to_poll,
            update_rate_hz=update_rate_hz,
            buffer_size=buffer_size,
            mcp_client=mcp_client,
        )

        self.engine = RuleEngine(mcp_client=mcp_client)

        # State
        self.running = False
        self.setup_time: Optional[float] = None
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None

        # Graceful shutdown flags
        self._shutdown_requested = False
        self._interrupted = False

        logger.info(
            f"AudioAnalysisController created for Track {track_index}, "
            f"Device {device_index}, {len(params_to_poll)} parameters"
        )

    def load_ruleset(self, yaml_path: str) -> RuleSet:
        """
        Load a rule set from YAML file and register with engine.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            Loaded RuleSet object
        """
        ruleset = self.engine.load_ruleset_from_yaml(yaml_path)
        self.engine.add_ruleset(ruleset)
        return ruleset

    def load_rulesets(self, yaml_paths: List[str]) -> List[RuleSet]:
        """
        Load multiple rule sets from YAML files.

        Args:
            yaml_paths: List of paths to YAML configuration files

        Returns:
            List of loaded RuleSet objects
        """
        rulesets = []
        for path in yaml_paths:
            ruleset = self.load_ruleset(path)
            rulesets.append(ruleset)
        return rulesets

    def register_engine(self):
        """Register rule engine as callback on poller (integration point)."""
        self.engine.apply_to_poller(self.poller)
        logger.info("Rule engine registered with poller")

    def start(self, register_engine: bool = True):
        """
        Start the control loop.

        Args:
            register_engine: If True, auto-register engine as poller callback
        """
        if self.running:
            logger.warning("Controller already running")
            return

        if register_engine:
            self.register_engine()

        self.setup_time = time.time()
        self.running = True
        self._shutdown_requested = False
        self._interrupted = False

        logger.info("Starting audio analysis control loop...")
        self.poller.start()
        self.start_time = time.time()

        logger.info(
            f"Control loop running at {self.poller.update_rate_hz} Hz, "
            f"{len(self.engine.rule_sets)} rule sets loaded"
        )

    def stop(self):
        """Stop the control loop gracefully."""
        if not self.running:
            return

        logger.info("Stopping audio analysis control loop...")
        self.running = False
        self._shutdown_requested = True

        # Stop poller (waits for thread to finish)
        self.poller.stop()

        self.stop_time = time.time()
        duration = self.stop_time - self.start_time if self.start_time else 0

        logger.info(
            f"Control loop stopped. Duration: {duration:.2f}s, "
            f"Interrupted: {self._interrupted}"
        )

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of controller and components.

        Returns:
            Dictionary with poller status, engine stats, and controller state
        """
        poller_status = self.poller.get_status()
        engine_stats = self.engine.get_stats()

        status = {
            "controller": {
                "running": self.running,
                "track_index": self.track_index,
                "device_index": self.device_index,
                "parameters_polling": len(self.params_to_poll),
                "setup_time": self.setup_time,
                "start_time": self.start_time,
                "stop_time": self.stop_time,
                "interrupted": self._interrupted,
                "runtime_seconds": (
                    (time.time() - self.start_time)
                    if self.running and self.start_time
                    else (self.stop_time - self.start_time)
                    if self.stop_time and self.start_time
                    else 0
                ),
            },
            "poller": poller_status,
            "engine": engine_stats,
        }

        # Add latest snapshot values
        latest_snapshot = self.poller.get_latest_snapshot()
        if latest_snapshot:
            status["latest_values"] = {
                "timestamp": latest_snapshot.timestamp,
                "normalized": latest_snapshot.values,
                "raw": latest_snapshot.raw_values,
            }

        return status

    def get_current_parameter_values(self) -> Optional[Dict[int, float]]:
        """
        Get current normalized parameter values.

        Returns:
            Dict mapping parameter_index -> normalized_value (0.0-1.0), or None
        """
        snapshot = self.poller.get_latest_snapshot()
        return snapshot.values if snapshot else None

    def get_raw_parameter_values(self) -> Optional[Dict[int, float]]:
        """
        Get current raw parameter values.

        Returns:
            Dict mapping parameter_index -> raw_value, or None
        """
        snapshot = self.poller.get_latest_snapshot()
        return snapshot.raw_values if snapshot else None

    def get_parameter_value(self, parameter_index: int) -> Optional[float]:
        """
        Get current normalized value for specific parameter.

        Args:
            parameter_index: Index of parameter to query

        Returns:
            Normalized value (0.0-1.0), or None if not available
        """
        values = self.get_current_parameter_values()
        return values.get(parameter_index) if values else None

    def get_raw_parameter_value(self, parameter_index: int) -> Optional[float]:
        """
        Get current raw value for specific parameter.

        Args:
            parameter_index: Index of parameter to query

        Returns:
            Raw value, or None if not available
        """
        values = self.get_raw_parameter_values()
        return values.get(parameter_index) if values else None

    def get_parameter_config(self, parameter_index: int) -> Optional[ParameterConfig]:
        """
        Get configuration for specific parameter.

        Args:
            parameter_index: Index of parameter to query

        Returns:
            ParameterConfig object, or None if index not found
        """
        return self.poller.params_to_poll.get(parameter_index)

    def print_status(self):
        """Print human-readable status to console."""
        status = self.get_status()

        print("\n" + "=" * 70)
        print("AUDIO ANALYSIS CONTROLLER STATUS")
        print("=" * 70)

        # Controller status
        ctrl = status["controller"]
        print(f"State: {'RUNNING' if ctrl['running'] else 'STOPPED'}")
        print(f"Track: {ctrl['track_index']}, Device: {ctrl['device_index']}")
        print(f"Parameters monitored: {ctrl['parameters_polling']}")
        print(f"Runtime: {ctrl['runtime_seconds']:.1f}s")
        print(f"Interrupted: {ctrl['interrupted']}")

        # Poller status
        poller = status["poller"]
        print(f"\nPOLLER:")
        print(f"  Target rate: {poller['update_rate_hz']:.1f} Hz")
        print(f"  Actual rate: {poller['actual_rate_hz']:.1f} Hz")
        print(f"  Total polls: {poller['total_polls']}")
        print(f"  Buffer size: {poller['buffer_size']}")
        print(f"  Running: {poller['running']}")

        # Engine status
        engine = status["engine"]
        print(f"\nENGINE:")
        print(f"  Rule sets loaded: {engine['loaded_rulesets']}")
        print(f"  Total rules: {engine['total_rules']}")
        print(f"  Total evaluations: {engine['total_evaluations']}")
        print(f"  Total triggers: {engine['total_triggers']}")
        print(f"  Actions executed: {engine['total_action_executions']}")
        print(f"  Errors: {engine['errors']}")

        # Latest values
        if "latest_values" in status:
            latest = status["latest_values"]
            print(f"\nLATEST VALUES ({time.ctime(latest['timestamp'])}):")
            print("  Normalized:")
            for idx, val in latest["normalized"].items():
                config = self.get_parameter_config(idx)
                param_name = config.name if config else f"Param {idx}"
                print(f"    {param_name} (idx {idx}): {val:.4f}")

            print("  Raw:")
            for idx, val in latest["raw"].items():
                config = self.get_parameter_config(idx)
                param_name = config.name if config else f"Param {idx}"
                unit = config.unit if config else ""
                print(f"    {param_name} (idx {idx}): {val:.2f} {unit}")

        print("=" * 70 + "\n")

    def enable_rule(self, rule_id: str):
        """Enable a specific rule by ID."""
        # Search all rule sets
        for ruleset in self.engine.rule_sets:
            if ruleset.get_rule(rule_id):
                ruleset.enable_rule(rule_id)
                return
        logger.warning(f"Rule '{rule_id}' not found in any rule set")

    def disable_rule(self, rule_id: str):
        """Disable a specific rule by ID."""
        # Search all rule sets
        for ruleset in self.engine.rule_sets:
            if ruleset.get_rule(rule_id):
                ruleset.disable_rule(rule_id)
                return
        logger.warning(f"Rule '{rule_id}' not found in any rule set")

    def reset_statistics(self):
        """Reset all controller and engine statistics."""
        self.engine.reset_stats()
        logger.info("Controller statistics reset")


def run_with_graceful_shutdown(controller: AudioAnalysisController):
    """
    Run controller with graceful shutdown handling (Ctrl+C).

    Args:
        controller: AudioAnalysisController instance
    """

    def signal_handler(sig, frame):
        """Handle interrupt signal."""
        logger.info("\nInterrupt received, shutting down gracefully...")
        controller._interrupted = True
        controller.stop()

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start controller
    controller.start()

    print("Controller running. Press Ctrl+C to stop.")
    print("Type 'status' to see current status, 'help' for commands")

    try:
        # Simple command loop
        while controller.running:
            cmd = input("> ").strip().lower() if not controller._interrupted else ""

            if cmd == "status":
                controller.print_status()
            elif cmd == "help":
                print("Available commands:")
                print("  status  - Print current status")
                print("  stop    - Stop controller")
                print("  help    - Show this help")
            elif cmd == "stop":
                controller.stop()
            elif cmd == "":
                pass  # Empty input, continue
            else:
                print(f"Unknown command: {cmd}")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, shutting down...")
        controller._interrupted = True
        controller.stop()
    finally:
        # Print final status
        print()
        controller.print_status()
