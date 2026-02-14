#!/usr/bin/env python3
"""
Responsive Control Loop for VST Audio Analysis

This script integrates polling, rule evaluation, and action execution
with latency measurement and dry-run mode support.

Usage:
    python responsive_control.py --rules=configs/analysis/lufs_compressor.yml --track=0 --device=0 --rate=15 --duration=60

Features:
    - Continuous parameter polling and rule evaluation
    - Latency measurement (<100ms target)
    - Dry-run mode for testing
    - Statistics tracking (rules fired/second, latency metrics)
    - Graceful shutdown with summary
"""

import argparse
import signal
import sys
import time
from typing import List, Optional, Dict
from pathlib import Path

# Add scripts/analysis directory to path for imports
analysis_dir = Path(__file__).parent
sys.path.insert(0, str(analysis_dir))

# Import from sibling modules
from rules_engine import (
    PollingRulesEngine,
    RuleEvaluationResult,
    RulesEngineError,
)
from rules_parser import RulesParser, RulesParseError


class ResponsiveController(PollingRulesEngine):
    """
    Responsive control loop with latency tracking and dry-run mode.

    Extends PollingRulesEngine to add:
    - Latency measurement (parameter read → action complete)
    - Dry-run mode (shows actions without executing)
    - Statistics tracking
    """

    def __init__(
        self,
        track_index: int = 0,
        device_index: int = 0,
        polling_rate_hz: float = 15.0,
        cooldown_seconds: float = 0.5,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        """
        Initialize responsive controller.

        Args:
            track_index: Track index for parameter polling
            device_index: Device index for parameter polling
            polling_rate_hz: How often to poll parameters (Hz)
            cooldown_seconds: Minimum time between firing same rule
            dry_run: If True, shows actions without executing
            verbose: Enable verbose logging
        """
        super().__init__(
            track_index=track_index,
            device_index=device_index,
            polling_rate_hz=polling_rate_hz,
            cooldown_seconds=cooldown_seconds,
            verbose=verbose,
        )
        self.dry_run = dry_run

        # Latency tracking
        self.latencies: List[float] = []

        # Statistics
        self.total_actions = 0
        self.rules_fired_count = 0
        self.start_time: Optional[float] = None

    def evaluate_and_execute(
        self,
        rules: List,
        parameter_values: Dict[str, float],
        cooldown_seconds: float = 0.0,
    ) -> List[RuleEvaluationResult]:
        """
        Evaluate all rules and execute actions for matching conditions.

        Extends parent method to add latency tracking and dry-run mode.

        Args:
            rules: List of Rule objects (sorted by priority)
            parameter_values: Dictionary of parameter values
            cooldown_seconds: Minimum time between firing same rule

        Returns:
            List of RuleEvaluationResult objects
        """
        results = []
        loop_start_time = time.time()

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
                    # Record latency before executing action
                    poll_start = loop_start_time
                    action_start = time.time()

                    if self.verbose:
                        print(f"[RULE] '{rule.name}' fired - priority {rule.priority}")

                    # Execute action (or dry-run)
                    if not self.dry_run:
                        self._execute_action(rule.action)
                    else:
                        # Dry-run mode: show action without executing
                        print(f"[DRY-RUN] Would execute: {rule.action.type}")
                        if self.verbose and rule.action.params:
                            print(f"[DRY-RUN]   Params: {rule.action.params}")

                    # Calculate latency
                    action_complete = time.time()
                    latency = (action_complete - poll_start) * 1000  # Convert to ms
                    self.latencies.append(latency)

                    if self.verbose:
                        print(f"[LATENCY] {latency:.2f}ms (poll→action)")

                    # Update cooldown
                    if cooldown_seconds > 0:
                        self.cooldowns[rule.name] = time.time()

                    # Update statistics
                    self.total_actions += 1
                    self.rules_fired_count += 1
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

    def run_control_loop(self, rules_file: str, duration_seconds: float = 0.0) -> None:
        """
        Run the control loop with statistics tracking.

        Args:
            rules_file: Path to YAML rule configuration file
            duration_seconds: How long to run (0 = infinite)

        Raises:
            RulesParseError: If rules file cannot be parsed
            RulesEngineError: If unable to connect to MCP server
        """
        # Parse rules
        parser = RulesParser()
        rules = parser.parse(rules_file)

        print(f"[ENGINE] Loaded {len(rules)} rules from {rules_file}")
        print(f"[ENGINE] Polling rate: {self.polling_rate_hz} Hz")
        print(f"[ENGINE] Cooldown: {self.cooldown_seconds} seconds")
        print(f"[ENGINE] Dry-run mode: {self.dry_run}")

        if duration_seconds > 0:
            print(f"[ENGINE] Duration: {duration_seconds} seconds")
        else:
            print(f"[ENGINE] Duration: infinite (Ctrl+C to stop)")

        print()

        # Start loop
        self.running = True
        self.start_time = time.time()
        poll_count = 0

        try:
            poll_interval = 1.0 / self.polling_rate_hz

            while self.running:
                # Poll parameters
                parameter_values = self._poll_parameters()

                # Evaluate and execute rules
                if self.rules and parameter_values:
                    results = self.evaluate_and_execute(
                        rules, parameter_values, self.cooldown_seconds
                    )

                    # Track firing stats
                    fired_count = sum(1 for r in results if r.fired)
                    if fired_count > 0:
                        if self.verbose:
                            print(f"[ENGINE] {fired_count} rule(s) fired this cycle")
                else:
                    # Store rules for evaluation
                    self.rules = rules

                poll_count += 1

                # Display statistics every 50 iterations
                if poll_count % 50 == 0:
                    self._display_statistics(poll_count)

                # Check duration limit
                if duration_seconds > 0:
                    if time.time() - self.start_time >= duration_seconds:
                        print(f"[ENGINE] Duration limit reached ({duration_seconds}s)")
                        break

                # Wait for next poll
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n[ENGINE] Interrupted by user (Ctrl+C)")

        finally:
            self.running = False
            self._print_summary(poll_count)

    def _display_statistics(self, poll_count: int) -> None:
        """Display current statistics."""
        elapsed = time.time() - self.start_time
        actual_hz = poll_count / elapsed

        # Calculate latency statistics
        avg_latency = (
            sum(self.latencies[-50:]) / min(len(self.latencies), 50)
            if self.latencies
            else 0
        )
        max_latency = max(self.latencies[-50:]) if self.latencies else 0

        # Calculate rules fired per second
        rules_per_sec = self.rules_fired_count / elapsed if elapsed > 0 else 0

        print(
            f"[STATS] Polls: {poll_count} | "
            f"Rate: {actual_hz:.1f} Hz | "
            f"Rules fired: {self.rules_fired_count} | "
            f"Rules/sec: {rules_per_sec:.2f}"
        )
        print(
            f"[STATS] Latency: avg={avg_latency:.2f}ms, "
            f"max={max_latency:.2f}ms (last 50)"
        )
        print(f"[STATS] Elapsed: {elapsed:.1f}s")
        print()

    def _print_summary(self, poll_count: int) -> None:
        """Print final summary statistics."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        print("\n" + "=" * 70)
        print("RESPONSIVE CONTROL SUMMARY")
        print("=" * 70)

        # General stats
        print(f"Total poll cycles: {poll_count}")
        print(f"Total duration: {elapsed:.2f} seconds")
        print(f"Actual polling rate: {poll_count / elapsed:.2f} Hz")
        print(f"Target polling rate: {self.polling_rate_hz:.2f} Hz")

        # Rules stats
        print(f"\nRule Statistics:")
        print(f"  Total rules fired: {self.rules_fired_count}")
        print(
            f"  Rules per second: {self.rules_fired_count / elapsed if elapsed > 0 else 0:.2f}"
        )
        print(f"  Total actions executed: {self.total_actions}")

        # Latency stats
        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            min_latency = min(self.latencies)
            max_latency = max(self.latencies)
            print(f"\nLatency Statistics:")
            print(f"  Average latency: {avg_latency:.2f} ms")
            print(f"  Min latency: {min_latency:.2f} ms")
            print(f"  Max latency: {max_latency:.2f} ms")

            # Check if <100ms target met
            target_met = avg_latency < 100
            status = "PASS" if target_met else "FAIL"
            print(f"  <100ms target: {status} ({avg_latency:.2f}ms)")
        else:
            print(f"\nLatency Statistics:")
            print(f"  No latency data collected")

        # Dry-run indicator
        print(f"\nMode:")
        print(f"  Dry-run: {self.dry_run}")

        print("=" * 70)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Responsive control loop for VST audio analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Basic usage - run for 60 seconds at 15 Hz
  python responsive_control.py --rules=configs/analysis/lufs_compressor.yml --track=0 --device=0 --rate=15 --duration=60

  # Dry-run mode - test without executing actions
  python responsive_control.py --rules=configs/analysis/lufs_compressor.yml --dry-run --duration=10

  # Verbose output - see detailed information
  python responsive_control.py --rules=configs/analysis/lufs_compressor.yml --verbose --duration=30

  # Infinite polling (Ctrl+C to stop)
  python responsive_control.py --rules=configs/analysis/lufs_compressor.yml --track=0 --device=0 --rate=15 --duration=0
        """,
    )

    parser.add_argument(
        "--rules",
        type=str,
        required=True,
        help="Path to YAML rule configuration file",
    )

    parser.add_argument(
        "--track",
        type=int,
        default=0,
        help="Track index for parameter polling (default: 0)",
    )

    parser.add_argument(
        "--device",
        type=int,
        default=0,
        help="Device index for parameter polling (default: 0)",
    )

    parser.add_argument(
        "--rate",
        type=float,
        default=15.0,
        choices=[float(x) for x in range(5, 31)],  # 5-30 Hz
        metavar="HZ",
        help="Polling rate in Hz (5-30, default: 15)",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Duration in seconds (0 = infinite, default: 0)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode - show planned actions without executing",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()

    print("=" * 70)
    print("RESPONSIVE CONTROL LOOP")
    print("=" * 70)
    print(f"Rules file: {args.rules}")
    print(f"Track index: {args.track}")
    print(f"Device index: {args.device}")
    print(f"Polling rate: {args.rate} Hz")
    print(
        f"Duration: {'Infinite' if args.duration == 0 else f'{args.duration} seconds'}"
    )
    print(f"Dry-run: {args.dry_run}")
    print(f"Verbose: {args.verbose}")
    print("=" * 70)
    print()

    # Validate rules file exists
    rules_path = Path(args.rules)
    if not rules_path.exists():
        print(f"[ERROR] Rules file not found: {args.rules}")
        sys.exit(1)

    # Validate polling rate
    if args.rate < 5 or args.rate > 30:
        print("[ERROR] Invalid rate: Must be between 5-30 Hz")
        sys.exit(2)

    # Create controller
    try:
        controller = ResponsiveController(
            track_index=args.track,
            device_index=args.device,
            polling_rate_hz=args.rate,
            cooldown_seconds=0.5,  # Default cooldown
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
    except Exception as e:
        print(f"[ERROR] Failed to initialize controller: {str(e)}")
        sys.exit(3)

    # Setup signal handler for graceful exit
    def signal_handler(signum, frame):
        print("\n\n[INFO] Signal received, stopping gracefully...")
        controller.running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start control loop
    print("[OK] Starting responsive control loop...")
    print("[OK] Press Ctrl+C to stop gracefully")
    print("-" * 70)
    print()

    try:
        controller.run_control_loop(
            rules_file=args.rules,
            duration_seconds=args.duration if args.duration > 0 else 0.0,
        )
    except RulesParseError as e:
        print(f"[ERROR] Failed to parse rules: {str(e)}")
        sys.exit(4)
    except RulesEngineError as e:
        print(f"[ERROR] Rules engine error: {str(e)}")
        sys.exit(5)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(6)


if __name__ == "__main__":
    main()
