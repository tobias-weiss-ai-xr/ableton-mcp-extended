"""
Benchmark suite runner for automated performance testing.

This module provides a command-line interface for running comprehensive
benchmark suites and generating reports.

Author: Audio Analysis System
Date: 2025-02-10
"""

import argparse
import sys
from typing import Optional

from .benchmarks import BenchmarkSuite
from .benchmark_report import generate_report


def create_mock_poller(target_rate_hz: int):
    """Create a mock poller for testing."""

    class MockPoller:
        def __init__(self):
            self.called_count = 0

        def poll_parameters(self):
            self.called_count += 1

        def get_status(self):
            return {
                "target_rate_hz": target_rate_hz,
                "actual_rate_hz": 0.0,
                "uptime_seconds": 0.0,
                "total_snapshots": self.called_count,
            }

    return MockPoller()


def create_mock_rule_engine():
    """Create a mock rule engine for testing."""

    class MockRuleEngine:
        def __init__(self):
            self.evaluation_count = 0

        def evaluate_all_rules(self, params):
            self.evaluation_count += 1
            # Simulate some rule evaluation
            # Occasionally trigger rules
            triggers = []
            if self.evaluation_count % 10 == 0:
                triggers.append(
                    {
                        "rule_id": "mock_rule_1",
                        "condition": "param > 0.5",
                        "actions": ["action_1"],
                    }
                )
            return triggers

    return MockRuleEngine()


def create_mock_controller(poll_rate_hz: int = 10):
    """Create a mock controller for testing."""

    class MockController:
        def __init__(self, poll_rate_hz: int):
            self.poll_rate_hz = poll_rate_hz
            self._running = False

        def start(self):
            self._running = True

        def stop(self):
            self._running = False

        def is_running(self):
            return self._running

        def _poll_one_cycle(self):
            time.sleep(0.001)

        def _evaluate_rules(self):
            time.sleep(0.0005)

        def _execute_actions(self):
            time.sleep(0.001)

    return MockController(poll_rate_hz)


def run_polling_benchmarks(suite: BenchmarkSuite, duration: float = 5.0):
    """Run polling-related benchmarks."""
    import time

    print(f"Running polling benchmarks ({duration}s each)...")
    print()

    # Test different polling rates
    poll_rates = [10, 20, 30, 50]

    for rate in poll_rates:
        mock_poller = create_mock_poller(rate)
        result = suite.polling_rate_benchmark(
            poller=mock_poller,
            target_rate_hz=rate,
            duration_seconds=duration,
            param_indices=[0, 1, 2],
        )
        suite.add_result(result)
        print(
            f"  - Polling rate {rate}Hz: {result.samples / result.duration_seconds:.1f}Hz actual"
        )

    print()


def run_rule_evaluation_benchmarks(suite: BenchmarkSuite, iterations: int = 100):
    """Run rule evaluation benchmarks."""
    print(f"Running rule evaluation benchmarks ({iterations} iterations)...")
    print()

    mock_engine = create_mock_rule_engine()
    result = suite.rule_evaluation_benchmark(
        rule_engine=mock_engine, poll_iterations=iterations
    )
    suite.add_result(result)
    print(
        f"  - Rule evaluation: {result.mean_value * 1000:.3f}ms mean, {result.p99 * 1000:.3f}ms P99"
    )

    print()


def run_latency_benchmarks(suite: BenchmarkSuite, iterations: int = 100):
    """Run end-to-end latency benchmarks."""
    import time

    print(f"Running latency benchmarks ({iterations} iterations)...")
    print()

    mock_controller = create_mock_controller(poll_rate_hz=20)

    result = suite.end_to_end_latency_benchmark(
        controller=mock_controller, poll_iterations=iterations
    )
    suite.add_result(result)
    print(
        f"  - End-to-end latency: {result.mean_value * 1000:.3f}ms mean, {result.p99 * 1000:.3f}ms P99"
    )

    print()


def run_cpu_benchmarks(suite: BenchmarkSuite, duration: float = 5.0):
    """Run CPU usage benchmarks."""
    import time

    print(f"Running CPU benchmarks ({duration}s)...")
    print()

    mock_controller = create_mock_controller(poll_rate_hz=10)

    try:
        result = suite.cpu_usage_benchmark(
            controller=mock_controller, duration_seconds=duration
        )
        suite.add_result(result)
        if result.samples > 0:
            print(
                f"  - CPU usage: {result.mean_value:.2f}% mean, {result.max_value:.2f}% max"
            )
        else:
            print(f"  - CPU usage: N/A (psutil not available)")
    except Exception as e:
        print(f"  - CPU usage: Skipped ({e})")

    print()


def run_all_benchmarks(duration: float = 5.0, iterations: int = 100) -> BenchmarkSuite:
    """
    Run the complete benchmark suite.

    Args:
        duration: Duration for time-based benchmarks
        iterations: Iterations for count-based benchmarks

    Returns:
        BenchmarkSuite with all results
    """
    import time

    start_time = time.time()

    print("=" * 80)
    print("AUDIO ANALYSIS SYSTEM - BENCHMARK SUITE")
    print("=" * 80)
    print()

    suite = BenchmarkSuite()

    # Run all benchmark categories
    run_polling_benchmarks(suite, duration=duration)
    run_rule_evaluation_benchmarks(suite, iterations=iterations)
    run_latency_benchmarks(suite, iterations=iterations)
    run_cpu_benchmarks(suite, duration=duration)

    total_duration = time.time() - start_time

    # Print summary
    suite.print_summary()

    return suite, total_duration


def main():
    """Command-line interface for benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Run benchmarks for Audio Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run quick benchmarks (5s duration, 100 iterations)
  python benchmark_runner.py

  # Run extended benchmarks
  python benchmark_runner.py --duration 10 --iterations 500

  # Run specific benchmark type
  python benchmark_runner.py --type polling

  # Generate reports to files
  python benchmark_runner.py --output-dir benchmark_results

  # Run with custom parameters
  python benchmark_runner.py --duration 3 --iterations 250 --output-dir results
        """,
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Duration for time-based benchmarks (seconds). Default: 5.0",
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Iterations for count-based benchmarks. Default: 100",
    )

    parser.add_argument(
        "--type",
        type=str,
        choices=["all", "polling", "rules", "latency", "cpu"],
        default="all",
        help="Type of benchmark to run. Default: all",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save benchmark reports. Default: print to console only",
    )

    parser.add_argument(
        "--formats",
        type=str,
        nargs="+",
        choices=["text", "json", "markdown"],
        default=["text"],
        help="Report formats to generate. Default: text",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (only generate reports)",
    )

    args = parser.parse_args()

    # Create suite
    suite = BenchmarkSuite()

    import time

    start_time = time.time()

    if not args.quiet:
        print("=" * 80)
        print("AUDIO ANALYSIS SYSTEM - BENCHMARK SUITE")
        print("=" * 80)
        print(f"\nConfiguration:")
        print(f"  Duration:   {args.duration}s")
        print(f"  Iterations: {args.iterations}")
        print(f"  Type:       {args.type}")
        print(f"  Output dir: {args.output_dir or 'N/A'}")
        print(f"  Formats:    {', '.join(args.formats)}")
        print()

    # Run selected benchmarks
    try:
        if args.type in ["all", "polling"]:
            run_polling_benchmarks(suite, duration=args.duration)

        if args.type in ["all", "rules"]:
            run_rule_evaluation_benchmarks(suite, iterations=args.iterations)

        if args.type in ["all", "latency"]:
            run_latency_benchmarks(suite, iterations=args.iterations)

        if args.type in ["all", "cpu"]:
            run_cpu_benchmarks(suite, duration=args.duration)

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
        return 1

    total_duration = time.time() - start_time

    # Print summary
    if not args.quiet:
        suite.print_summary()

    # Generate reports
    if args.output_dir:
        import os
        from pathlib import Path

        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        base_filename = f"benchmark_report_{timestamp}"
        base_path = output_path / base_filename

        outputs = {}

        if "json" in args.formats:
            json_path = f"{base_path}.json"
            outputs["json"] = json_path

        if "markdown" in args.formats:
            md_path = f"{base_path}.md"
            outputs["markdown"] = md_path

        if "text" in args.formats:
            txt_path = f"{base_path}.txt"
            outputs["text"] = txt_path

        report = generate_report(
            suite=suite,
            duration_seconds=total_duration,
            output_json=outputs.get("json"),
            output_markdown=outputs.get("markdown"),
            output_text=outputs.get("text"),
        )

        if not args.quiet:
            print(f"\nReports generated:")
            for fmt, path in outputs.items():
                print(f"  {fmt:10s}: {path}")

            print(f"\nPerformance Grade: {report.performance_grade}")
            if report.recommendations:
                print("\nRecommendations:")
                for rec in report.recommendations:
                    print(f"  - {rec}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
