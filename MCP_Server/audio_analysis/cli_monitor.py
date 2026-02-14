"""
CLI Monitor for Audio Analysis System

Provides a terminal-based real-time monitoring interface for the
audio analysis polling and rule engine system.

Features:
- Real-time parameter value display (normalized + raw)
- Polling rate indicator (actual vs target Hz)
- Rule engine statistics
- Rule activation status with timestamps
- Visual indicators (ANSI colors, progress bars)
- Keyboard shortcuts (pause, quit, toggle debug)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import time
import threading


class MonitorColors:
    """ANSI color codes for terminal rendering."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"


@dataclass
class MonitorConfig:
    """Configuration for monitoring display."""

    refresh_rate_hz: int = 10  # Default 10 Hz refresh (match polling rate)
    show_raw_values: bool = True
    show_history: bool = True
    show_debug: bool = False
    terminal_width: int = 80
    progress_bar_width: int = 20


class MonitorDisplay:
    """
    Terminal-based real-time monitoring display for audio analysis system.

    Renders parameter values, polling status, rule statistics, and trigger events
    in a clean, color-coded terminal interface.
    """

    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()
        self._last_reresh_time: float = 0.0

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        print("\033[2J\033[H", end="")

    def move_cursor(self, row: int, col: int) -> None:
        """Move cursor to specific row and column."""
        print(f"\033[{row};{col}H", end="")

    def render_header(self, title: str) -> str:
        """Render section header."""
        line = MonitorColors.BOLD + MonitorColors.CYAN
        line += f"=== {title} ==="
        line += MonitorColors.RESET
        return line

    def render_parameter_row(
        self,
        param_index: int,
        param_name: str,
        normalized_value: float,
        raw_value: Optional[float] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        unit: Optional[str] = None,
    ) -> str:
        """
        Render a single parameter row with value and optional progress bar.

        Args:
            param_index: Parameter index
            param_name: Human-readable parameter name
            normalized_value: Normalized value (0.0-1.0)
            raw_value: Raw value (if available)
            min_value: Minimum raw value (for progress bar)
            max_value: Maximum raw value (for progress bar)
            unit: Unit label (e.g., "dB", "LUFS")

        Returns:
            Formatted parameter row string
        """
        # Color based on value level
        if normalized_value >= 0.8:
            value_color = MonitorColors.RED
        elif normalized_value >= 0.6:
            value_color = MonitorColors.YELLOW
        elif normalized_value >= 0.4:
            value_color = MonitorColors.GREEN
        else:
            value_color = MonitorColors.DIM

        # Progress bar
        bar_filled = int(normalized_value * self.config.progress_bar_width)
        bar_empty = self.config.progress_bar_width - bar_filled
        progress_bar = (
            MonitorColors.BG_GREEN
            + " " * bar_filled
            + MonitorColors.RESET
            + " " * bar_empty
        )

        # Build row
        row = f"  [{param_index:2d}] {param_name:20s}: "
        row += value_color + f"{normalized_value:6.3f}" + MonitorColors.RESET

        if self.config.show_raw_values and raw_value is not None:
            raw_str = f"{raw_value:8.2f}"
            if unit:
                raw_str += f" {unit}"
            row += f" (raw: {raw_str})"

        row += f" [{progress_bar}]"

        return row

    def render_polling_status(
        self,
        actual_rate_hz: float,
        target_rate_hz: float,
        uptime_seconds: float,
        total_snapshots: int,
    ) -> str:
        """
        Render polling system status section.

        Args:
            actual_rate_hz: Actual polling rate in Hz
            target_rate_hz: Target polling rate in Hz
            uptime_seconds: Controller uptime in seconds
            total_snapshots: Total number of snapshots collected

        Returns:
            Formatted status section string
        """
        # Color based on performance
        rate_ratio = actual_rate_hz / target_rate_hz if target_rate_hz > 0 else 0.0
        if rate_ratio >= 0.95:
            status_color = MonitorColors.GREEN
            status = "OK"
        elif rate_ratio >= 0.80:
            status_color = MonitorColors.YELLOW
            status = "SLOW"
        else:
            status_color = MonitorColors.RED
            status = "UNSTABLE"

        lines = [
            self.render_header("POLLING STATUS"),
            f"  Rate:         {status_color}{actual_rate_hz:6.2f} Hz{MonitorColors.RESET} "
            f"(target: {target_rate_hz:.2f} Hz) [{status}]",
            f"  Uptime:       {uptime_seconds:8.1f}s ({uptime_seconds / 60:.1f}m)",
            f"  Snapshots:    {total_snapshots:8d}",
        ]

        return "\n".join(lines)

    def render_rule_stats(
        self,
        evaluations: int,
        triggers: int,
        actions: int,
        errors: int,
        enabled_rules: int,
        total_rules: int,
    ) -> str:
        """
        Render rule engine statistics.

        Args:
            evaluations: Total rule evaluations
            triggers: Total rule triggers
            actions: Total actions executed
            errors: Total errors encountered
            enabled_rules: Number of enabled rules
            total_rules: Total number of loaded rules

        Returns:
            Formatted statistics section string
        """
        # Colors
        eval_color = MonitorColors.GREEN if errors == 0 else MonitorColors.YELLOW
        error_color = MonitorColors.RED if errors > 0 else MonitorColors.GREEN

        lines = [
            self.render_header("RULE ENGINE"),
            f"  Evaluations:  {eval_color}{evaluations:10d}{MonitorColors.RESET}",
            f"  Triggers:     {eval_color}{triggers:10d}{MonitorColors.RESET}",
            f"  Actions:      {eval_color}{actions:10d}{MonitorColors.RESET}",
            f"  Errors:       {error_color}{errors:10d}{MonitorColors.RESET}",
            f"  Rules:        {enabled_rules:2d}/{total_rules:2d} enabled",
        ]

        return "\n".join(lines)

    def render_active_rules(self, active_rules: List[Dict]) -> str:
        """
        Render list of recently triggered rules.

        Args:
            active_rules: List of rule trigger info dicts with:
                - rule_id: Rule identifier
                - rule_name: Human-readable name
                - triggered_at: Timestamp of trigger
                - actions: List of actions taken

        Returns:
            Formatted active rules section string
        """
        if not active_rules:
            return self.render_header("ACTIVE RULES") + "\n  No recent triggers"

        lines = [self.render_header("RECENT TRIGGERS")]

        for i, rule in enumerate(active_rules[:5]):  # Show last 5
            trigger_time = datetime.fromtimestamp(rule["triggered_at"])
            time_str = trigger_time.strftime("%H:%M:%S.%f")[:-3]  # 毫秒

            lines.append(
                f"  [{i + 1}] {MonitorColors.CYAN}{rule['rule_name']}{MonitorColors.RESET}"
            )
            lines.append(
                f"      {MonitorColors.DIM}ID: {rule['rule_id']} @ {time_str}{MonitorColors.RESET}"
            )

            if rule.get("actions"):
                lines.append(f"      Actions: {', '.join(rule['actions'])}")

        return "\n".join(lines)

    def render_monitor_display(
        self,
        poller_status: Dict,
        parameter_configs: List[Dict],
        current_values: Dict[int, float],
        rule_stats: Dict,
        active_rules: List[Dict],
        debug_info: Optional[Dict] = None,
    ) -> str:
        """
        Render complete monitoring display.

        Args:
            poller_status: Poller status dict from AudioAnalysisController
            parameter_configs: List of parameter configuration dicts
            current_values: Dict of parameter_index -> normalized_value
            rule_stats: Rule engine statistics dict
            active_rules: List of recent rule triggers
            debug_info: Optional debug information dict

        Returns:
            Complete formatted display string
        """
        sections = []

        # Timestamp
        sections.append(
            MonitorColors.BOLD
            + MonitorColors.BLUE
            + f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
            + MonitorColors.RESET
        )

        # Polling status
        sections.append(
            self.render_polling_status(
                actual_rate_hz=poller_status.get("actual_rate_hz", 0.0),
                target_rate_hz=poller_status.get("target_rate_hz", 0.0),
                uptime_seconds=poller_status.get("uptime_seconds", 0.0),
                total_snapshots=poller_status.get("total_snapshots", 0),
            )
        )

        # Parameter values
        sections.append(self.render_header("PARAMETER VALUES"))
        for config in parameter_configs:
            param_idx = config["index"]
            if param_idx in current_values:
                sections.append(
                    self.render_parameter_row(
                        param_index=param_idx,
                        param_name=config["name"],
                        normalized_value=current_values[param_idx],
                        raw_value=current_values.get(f"raw_{param_idx}"),
                        min_value=config.get("min_value"),
                        max_value=config.get("max_value"),
                        unit=config.get("unit"),
                    )
                )

        # Rule statistics
        sections.append(
            self.render_rule_stats(
                evaluations=rule_stats.get("evaluations", 0),
                triggers=rule_stats.get("triggers", 0),
                actions=rule_stats.get("actions", 0),
                errors=rule_stats.get("errors", 0),
                enabled_rules=rule_stats.get("enabled_rules", 0),
                total_rules=rule_stats.get("total_rules", 0),
            )
        )

        # Active rules
        sections.append(self.render_active_rules(active_rules))

        # Debug info (optional)
        if debug_info and self.config.show_debug:
            sections.append(self.render_header("DEBUG"))
            for key, value in debug_info.items():
                sections.append(f"  {key}: {value}")

        # Join sections with empty lines
        return "\n\n".join(sections)

    def update_display(self, display_text: str) -> None:
        """
        Update terminal display with new content.

        Args:
            display_text: Complete formatted display string
        """
        # Clear screen and render
        self.clear_screen()
        print(display_text, flush=True)

        # Update refresh time
        self._last_reresh_time = time.time()


class AudioAnalysisMonitor:
    """
    Integration layer between AudioAnalysisController and CLI display.

    Runs a continuous monitoring loop that polls the controller state
    and updates the terminal display at the configured refresh rate.
    """

    def __init__(
        self,
        controller,
        display: Optional[MonitorDisplay] = None,
        config: Optional[MonitorConfig] = None,
    ):
        """
        Initialize the monitor.

        Args:
            controller: AudioAnalysisController instance to monitor
            display: MonitorDisplay instance (created if None)
            config: MonitorConfig instance (created if None)
        """
        self.controller = controller
        self.display = display or MonitorDisplay(config or MonitorConfig())
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Track recent rule triggers for display
        self._recent_triggers: List[Dict] = []
        self._max_triggers = 10

        # Store parameter configs for display
        self._parameter_configs: List[Dict] = []

    def _update_trigger_list(self, actions_result: List[Dict]) -> None:
        """
        Update recent trigger list with new actions.

        Args:
            actions_result: List of action result dicts from rule evaluation
        """
        with self._lock:
            for action_result in actions_result:
                # Extract rule info from action result
                rule_info = {
                    "rule_id": action_result.get("rule_id", "unknown"),
                    "rule_name": action_result.get("rule_name", "Unknown Rule"),
                    "triggered_at": time.time(),
                    "actions": action_result.get("actions", []),
                }

                # Add to front of list and keep max size
                self._recent_triggers.insert(0, rule_info)
                if len(self._recent_triggers) > self._max_triggers:
                    self._recent_triggers.pop()

    def _get_display_data(self) -> Dict:
        """
        Collect current display data from controller.

        Returns:
            Dict with all display sections ready for rendering
        """
        # Get controller status
        poller_status = self.controller.get_status()

        # Get current parameter values
        current_values = {}
        raw_values = {}
        if hasattr(self.controller, "_poller"):
            snapshot = self.controller._poller.get_latest_snapshot()
            if snapshot:
                for param_idx, norm_val in snapshot.values.items():
                    current_values[param_idx] = norm_val
                for param_idx, raw_val in snapshot.raw_values.items():
                    raw_values[f"raw_{param_idx}"] = raw_val

                # Combine
                current_values.update(raw_values)

        # Get rule engine statistics
        rule_stats = {}
        if hasattr(self.controller, "_rule_engine"):
            stats = self.controller._rule_engine.get_stats()
            rule_stats = {
                "evaluations": stats.get("evaluations", 0),
                "triggers": stats.get("triggers", 0),
                "actions": stats.get("actions", 0),
                "errors": stats.get("errors", 0),
                "enabled_rules": len(
                    [r for r in self.controller._rule_engine._rules if r.enabled]
                )
                if hasattr(self.controller._rule_engine, "_rules")
                else 0,
                "total_rules": len(self.controller._rule_engine._rules)
                if hasattr(self.controller._rule_engine, "_rules")
                else 0,
            }

        # Get recent triggers with lock
        with self._lock:
            recent_triggers = self._recent_triggers.copy()

        return {
            "poller_status": poller_status,
            "parameter_configs": self._parameter_configs,
            "current_values": current_values,
            "rule_stats": rule_stats,
            "active_rules": recent_triggers,
        }

    def _render_loop(self) -> None:
        """
        Main rendering loop running in separate thread.
        """
        interval = 1.0 / self.display.config.refresh_rate_hz

        while self._running:
            start_time = time.time()

            try:
                # Collect display data
                display_data = self._get_display_data()

                # Render display
                display_text = self.display.render_monitor_display(**display_data)

                # Update terminal
                self.display.update_display(display_text)

            except Exception as e:
                print(f"Monitor error: {e}", flush=True)

            # Sleep until next update
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def on_rule_actions(self, actions_result: List[Dict]) -> None:
        """
        Callback for rule engine to report triggered actions.

        Args:
            actions_result: List of action result dicts
        """
        self._update_trigger_list(actions_result)

    def start(self) -> None:
        """
        Start the monitoring loop.

        Registers callback with controller and starts rendering thread.
        """
        if self._running:
            return

        # Register callback for rule actions
        if hasattr(self.controller, "_rule_engine"):
            self.controller._rule_engine.add_callback(self.on_rule_actions)

        # Store parameter configs
        if hasattr(self.controller, "_poller"):
            self._parameter_configs = [
                {
                    "index": cfg.index,
                    "name": cfg.name,
                    "min_value": cfg.min_value,
                    "max_value": cfg.max_value,
                    "unit": cfg.unit,
                }
                for cfg in self.controller._poller._params_to_poll
            ]

        # Start rendering thread
        self._running = True
        self._thread = threading.Thread(target=self._render_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """
        Stop the monitoring loop.

        Clears screen and terminates rendering thread.
        """
        if not self._running:
            return

        self._running = False

        # Wait for thread to finish
        if self._thread:
            self._thread.join(timeout=1.0)

        # Clear screen on exit
        print("\033[2J\033[H", end="", flush=True)

    def toggle_debug(self) -> None:
        """Toggle debug display mode."""
        self.display.config.show_debug = not self.display.config.show_debug

    def set_refresh_rate(self, rate_hz: int) -> None:
        """
        Set display refresh rate.

        Args:
            rate_hz: Refresh rate in Hz (1-30 recommended)
        """
        if 1 <= rate_hz <= 60:
            self.display.config.refresh_rate_hz = rate_hz
