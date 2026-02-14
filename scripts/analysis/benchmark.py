#!/usr/bin/env python3
"""
Performance Benchmarking Suite for VST Audio Analysis System

This script benchmarks parameter polling rates, control loop latency,
CPU/memory usage, and identifies performance bottlenecks.

Usage:
    python benchmark.py --test=polling_rates --duration=60
    python benchmark.py --test=latency --duration=30
    python benchmark.py --test=cpu_memory --duration=120
    python benchmark.py --test=all --duration=180

Features:
    - Parameter polling rate benchmarks (10 Hz, 15 Hz, 20 Hz)
    - Control loop latency measurement (<100ms target)
    - CPU and memory usage profiling
    - Performance bottleneck identification
    - Optimization recommendations
"""

import argparse
import json
import time
import sys
import threading
import psutil
import cProfile
import pstats
import io
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add scripts/analysis directory to path for imports
analysis_dir = Path(__file__).parent
sys.path.insert(0, str(analysis_dir))

from poll_plugin_params import ParameterPoller
from responsive_control import ResponsiveController


class PerformanceBenchmarker:
    """Comprehensive performance benchmarking for VST audio analysis system."""

    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 9877
        self.results = {}

    def benchmark_polling_rates(self, duration_seconds: int = 60) -> Dict:
        """
        Benchmark parameter polling at different rates (10, 15, 20 Hz).

        Args:
            duration_seconds: How long to test each rate

        Returns:
            Dictionary with benchmark results
        """
        print("=" * 60)
        print("POLLING RATE BENCHMARKS")
        print("=" * 60)
        print(f"Testing duration: {duration_seconds} seconds per rate")
        print()

        rates_to_test = [10, 15, 20]
        results = {}

        for rate in rates_to_test:
            print(f"Testing {rate} Hz polling rate...")

            # Create poller for this rate
            poller = ParameterPoller(
                track_index=0,
                device_index=0,
                update_rate_hz=rate,
                duration_seconds=duration_seconds,
            )

            # Connect and run benchmark
            if not poller.connect():
                results[rate] = {
                    "error": "connection_failed",
                    "message": f"Failed to connect for {rate} Hz test",
                }
                print(f"  [FAILED] Could not connect for {rate} Hz test")
                continue

            start_time = time.time()
            poller.start_time = start_time
            poller.readings_count = 0
            # Use local list to avoid referencing issues
            poll_times_local = []

            # Run polling for specified duration
            try:
                while time.time() - start_time < duration_seconds:
                    # Direct poll without caching for benchmarking
                    if poller.poll_once(cache_enabled=False):
                        poller.readings_count += 1
                        # Store poll time locally
                        if hasattr(poller, "poll_times") and poller.poll_times:
                            poll_times_local.append(
                                poller.poll_times[-1]
                                if len(poller.poll_times) > 0
                                else 0
                            )

                    # Progress every 5 seconds (more frequent for benchmarks)
                    if poller.readings_count % (rate * 5) == 0:
                        elapsed = time.time() - start_time
                        current_rate = (
                            poller.readings_count / elapsed if elapsed > 0 else 0
                        )
                        print(
                            f"  Progress: {poller.readings_count} readings, {current_rate:.1f} Hz, {elapsed:.1f}s elapsed"
                        )

            except KeyboardInterrupt:
                print(f"  Interrupted by user at {rate} Hz")
            finally:
                poller.stop()

                # Calculate results
                elapsed = time.time() - start_time
                actual_rate = poller.readings_count / elapsed if elapsed > 0 else 0
                avg_poll_time = (
                    sum(poll_times_local) / len(poll_times_local)
                    if poll_times_local
                    else 0
                )

                if poller.readings_count > 0 and actual_rate > 0:
                    results[rate] = {
                        "target_rate": rate,
                        "actual_rate": actual_rate,
                        "efficiency": (actual_rate / rate) * 100,
                        "total_readings": poller.readings_count,
                        "duration": elapsed,
                        "avg_poll_time_ms": avg_poll_time * 1000,
                        "error": None,
                    }
                    print(
                        f"  Completed: {actual_rate:.2f} Hz actual, {results[rate]['efficiency']:.1f}% efficiency"
                    )
                    print(f"  Avg poll time: {avg_poll_time * 1000:.2f} ms")
                else:
                    results[rate] = {
                        "target_rate": rate,
                        "actual_rate": 0.0,
                        "efficiency": 0.0,
                        "total_readings": poller.readings_count,
                        "duration": elapsed,
                        "avg_poll_time_ms": 0.0,
                        "error": "no_data_collected",
                    }
                    print(f"  Warning: No data collected for {rate} Hz test")

        return results

    def benchmark_latency(self, duration_seconds: int = 30) -> Dict:
        """
        Benchmark control loop latency (parameter read → action execute).

        Args:
            duration_seconds: How long to run latency test

        Returns:
            Dictionary with latency measurements
        """
        print("=" * 60)
        print("CONTROL LOOP LATENCY BENCHMARK")
        print("=" * 60)
        print(f"Testing duration: {duration_seconds} seconds")
        print()

        try:
            # Create controller with test rule
            controller = ResponsiveController(
                track_index=0,
                device_index=0,
                polling_rate_hz=15.0,
                cooldown_seconds=0.1,  # Fast cooldown for latency testing
                dry_run=False,
                verbose=True,
            )

            # Simulate rule that fires frequently
            test_rules_content = """
rules:
  - name: "latency_test_rule"
    priority: 1
    condition:
      parameter: "test_param"
      operator: ">"
      value: 0.5
    action:
      type: "set_track_volume"
      params:
        track_index: 1
        volume: 0.8
"""

            # Write test rules to temporary file
            test_rules_path = Path("temp_latency_test_rules.yml")
            with open(test_rules_path, "w") as f:
                f.write(test_rules_content)

            start_time = time.time()
            latencies = []
            actions_executed = 0

            # Run control loop for specified duration
            try:
                controller.run_control_loop(str(test_rules_path), duration_seconds)
            except KeyboardInterrupt:
                print("  Interrupted by user")
            finally:
                # Collect latency data from controller
                latencies = controller.latencies.copy()
                actions_executed = controller.total_actions

                elapsed = time.time() - start_time

                # Calculate statistics
                avg_latency = sum(latencies) / len(latencies) if latencies else 0
                min_latency = min(latencies) if latencies else 0
                max_latency = max(latencies) if latencies else 0
                p95_latency = (
                    sorted(latencies)[int(len(latencies) * 0.95)]
                    if len(latencies) > 20
                    else max_latency
                )
                p99_latency = (
                    sorted(latencies)[int(len(latencies) * 0.99)]
                    if len(latencies) > 20
                    else max_latency
                )

                result = {
                    "duration": elapsed,
                    "total_actions": actions_executed,
                    "avg_latency_ms": avg_latency,
                    "min_latency_ms": min_latency,
                    "max_latency_ms": max_latency,
                    "p95_latency_ms": p95_latency,
                    "p99_latency_ms": p99_latency,
                    "target_met": avg_latency < 100,
                    "error": None,
                }

                print(f"  Total actions executed: {actions_executed}")
                print(f"  Average latency: {avg_latency:.2f} ms")
                print(f"  P95 latency: {p95_latency:.2f} ms")
                print(f"  P99 latency: {p99_latency:.2f} ms")
                print(f"  <100ms target: {'PASS' if result['target_met'] else 'FAIL'}")
                print()

                # Cleanup
                test_rules_path.unlink(missing_ok=True)
                return result

        except Exception as e:
            return {"error": "latency_test_failed", "message": str(e)}

    def benchmark_cpu_memory(self, duration_seconds: int = 120) -> Dict:
        """
        Benchmark CPU and memory usage during VST analysis operation.

        Args:
            duration_seconds: How long to monitor resource usage

        Returns:
            Dictionary with CPU and memory measurements
        """
        print("=" * 60)
        print("CPU & MEMORY USAGE BENCHMARK")
        print("=" * 60)
        print(f"Monitoring duration: {duration_seconds} seconds")
        print()

        try:
            # Create high-frequency poller for CPU load
            poller = ParameterPoller(
                track_index=0,
                device_index=0,
                update_rate_hz=20.0,  # Maximum frequency
                duration_seconds=duration_seconds,
            )

            if not poller.connect():
                return {
                    "error": "connection_failed",
                    "message": "Failed to connect for CPU/memory benchmark",
                }

            # Start monitoring
            start_time = time.time()
            cpu_readings = []
            memory_readings = []

            # Monitor system resources
            process = psutil.Process()

            # Create mock log file to prevent None errors
            import io

            mock_log_file = io.StringIO()

            try:
                while time.time() - start_time < duration_seconds:
                    # Record current usage
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory_info = psutil.virtual_memory()

                    cpu_readings.append(cpu_percent)
                    memory_readings.append(
                        memory_info.used / memory_info.total * 100
                    )  # Memory usage percentage

                    # Perform polling to generate load
                    poller.poll_once(mock_log_file, cache_enabled=False)

                    # Progress every 30 seconds
                    if len(cpu_readings) % (20 * 30) == 0:
                        elapsed = time.time() - start_time
                        print(
                            f"  Progress: {elapsed:.1f}s, CPU: {cpu_percent:.1f}%, Memory: {memory_readings[-1]:.1f}%"
                        )

            except KeyboardInterrupt:
                print("  Interrupted by user")
            finally:
                poller.stop()
                elapsed = time.time() - start_time

                # Calculate statistics
                avg_cpu = sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0
                max_cpu = max(cpu_readings) if cpu_readings else 0
                avg_memory = (
                    sum(memory_readings) / len(memory_readings)
                    if memory_readings
                    else 0
                )
                max_memory = max(memory_readings) if memory_readings else 0

                result = {
                    "duration": elapsed,
                    "avg_cpu_percent": avg_cpu,
                    "max_cpu_percent": max_cpu,
                    "avg_memory_percent": avg_memory,
                    "max_memory_percent": max_memory,
                    "sample_count": len(cpu_readings),
                    "error": None,
                }

                print(f"  Average CPU usage: {avg_cpu:.1f}%")
                print(f"  Maximum CPU usage: {max_cpu:.1f}%")
                print(f"  Average memory usage: {avg_memory:.1f}%")
                print(f"  Maximum memory usage: {max_memory:.1f}%")
                print()

                return result

        except Exception as e:
            return {"error": "cpu_memory_benchmark_failed", "message": str(e)}

    def run_profiling_benchmark(self, duration_seconds: int = 60) -> Dict:
        """
        Run detailed profiling to identify performance bottlenecks.

        Args:
            duration_seconds: How long to run profiling

        Returns:
            Dictionary with profiling results
        """
        print("=" * 60)
        print("DETAILED PROFILING BENCHMARK")
        print("=" * 60)
        print(f"Profiling duration: {duration_seconds} seconds")
        print()

        try:
            # Create profiler
            profiler = cProfile.Profile()

            # Profile high-frequency polling
            poller = ParameterPoller(
                track_index=0,
                device_index=0,
                update_rate_hz=20.0,
                duration_seconds=duration_seconds,
            )

            def profiled_run():
                if not poller.connect():
                    return

                start_time = time.time()
                poll_count = 0

                # Create mock log file to prevent None errors
                import io

                mock_log_file = io.StringIO()

                while time.time() - start_time < duration_seconds:
                    poller.poll_once(mock_log_file, cache_enabled=False)
                    poll_count += 1

                    # Progress every 100 polls
                    if poll_count % 100 == 0:
                        elapsed = time.time() - start_time
                        print(f"  Progress: {poll_count} polls, {elapsed:.1f}s elapsed")

                poller.stop()

            # Run profiling
            start_time = time.time()
            profiler.enable()
            profiled_run()
            profiler.disable()
            elapsed = time.time() - start_time

            # Get profiling stats
            stats_stream = io.StringIO()
            ps = pstats.Stats(profiler, stream=stats_stream)
            ps.sort_stats("cumulative")
            ps.print_stats(20)  # Top 20 functions by time

            # Parse key metrics from stats
            stats_text = stats_stream.getvalue()

            result = {
                "duration": elapsed,
                "total_polls": poll_count,
                "profiling_output": stats_text,
                "error": None,
            }

            print(f"  Total polls executed: {poll_count}")
            print(f"  Average poll rate: {poll_count / elapsed:.1f} Hz")
            print(f"  Profiling completed - see output above")
            print()

            return result

        except Exception as e:
            return {"error": "profiling_failed", "message": str(e)}

    def identify_bottlenecks(self, all_results: Dict) -> Dict:
        """
        Analyze all benchmark results to identify bottlenecks and optimization opportunities.

        Args:
            all_results: Dictionary with all benchmark results

        Returns:
            Dictionary with bottleneck analysis and recommendations
        """
        print("=" * 60)
        print("BOTTLENECK ANALYSIS")
        print("=" * 60)
        print()

        analysis = {"bottlenecks": [], "recommendations": [], "optimal_config": {}}

        # Analyze polling results
        polling_results = all_results.get("polling_rates", {})
        best_rate = None

        if polling_results:
            for rate, result in polling_results.items():
                if result.get("error") is not None:
                    continue

                # Check efficiency and identify best rate
                efficiency = result.get("efficiency", 0)
                if efficiency < 90:
                    analysis["bottlenecks"].append(
                        f"Rate {rate} inefficient: {efficiency:.1f}% efficiency"
                    )
                    analysis["recommendations"].append(
                        f"Consider rate optimization for {rate} (current: {efficiency:.1f}% efficiency)"
                    )
                else:
                    best_rate = rate
                    analysis["optimal_config"]["polling_rate"] = rate
        else:
            best_rate = None

        # Analyze resource usage
        resource_results = all_results.get("cpu_memory", {})
        avg_cpu = 0
        max_cpu = 0
        avg_memory = 0

        if resource_results:
            avg_cpu = resource_results.get("avg_cpu_percent", 0)
            max_cpu = resource_results.get("max_cpu_percent", 0)
            avg_memory = resource_results.get("avg_memory_percent", 0)

            # Add resource usage analysis
            analysis["cpu_memory"] = {
                "avg_cpu_percent": avg_cpu,
                "max_cpu_percent": max_cpu,
                "avg_memory_percent": avg_memory,
            }

        # Add CPU and memory analysis to results
        if "cpu_memory" in all_results:
            analysis["cpu_memory"] = resource_results["cpu_memory"]
        else:
            analysis["cpu_memory"] = {
                "avg_cpu_percent": avg_cpu,
                "max_cpu_percent": max_cpu,
                "avg_memory_percent": avg_memory,
            }

        return analysis

    def generate_report(self, all_results: Dict, output_path: str = None) -> None:
        """
        Generate comprehensive performance report.

        Args:
            all_results: Dictionary with all benchmark results
            output_path: Optional path to save report
        """
        report_path = Path(output_path or "docs/vst-plugins/performance_report.md")

        # Ensure directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate report content
        report_content = self._generate_report_content(all_results)

        # Write report
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"Performance report generated: {report_path}")

    def _generate_report_content(self, all_results: Dict) -> str:
        """Generate markdown content for performance report."""

        content = f"""# VST Audio Analysis Performance Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Test Duration:** Various benchmarks completed

---

## Executive Summary

This report contains comprehensive performance benchmarks for the VST Audio Analysis system,
including polling rates, control loop latency, CPU/memory usage, and optimization recommendations.

---

## Benchmark Results

### Parameter Polling Rates

"""

        # Add polling results
        polling_results = all_results.get("polling_rates", {})
        if polling_results:
            content += "| Rate (Hz) | Actual Rate (Hz) | Efficiency (%) | Avg Poll Time (ms) | Total Readings |\n"
            content += "|-------------|-------------------|----------------|------------------|----------------|\n"

            for rate, result in sorted(polling_results.items()):
                if result.get("error") is None:
                    content += f"| {rate} | {result['actual_rate']:.2f} | {result['efficiency']:.1f} | {result['avg_poll_time_ms']:.2f} | {result['total_readings']} |\n"
                else:
                    content += f"| {rate} | FAILED | {result.get('error', 'unknown')} | - | - |\n"

            content += "\n"

        # Add latency results
        latency_results = all_results.get("latency", {})
        if latency_results:
            content += f"""
### Control Loop Latency

- **Target:** <100ms average, <200ms P99
- **Average Latency:** {latency_results.get("avg_latency_ms", 0):.2f} ms
- **P95 Latency:** {latency_results.get("p95_latency_ms", 0):.2f} ms
- **P99 Latency:** {latency_results.get("p99_latency_ms", 0):.2f} ms
- **Target Met:** {"✅ YES" if latency_results.get("target_met", False) else "❌ NO"}
- **Total Actions:** {latency_results.get("total_actions", 0)}

"""

        # Add resource usage results
        resource_results = all_results.get("cpu_memory", {})
        if resource_results:
            content += f"""
### System Resource Usage

- **Average CPU Usage:** {resource_results.get("avg_cpu_percent", 0):.1f}%
- **Maximum CPU Usage:** {resource_results.get("max_cpu_percent", 0):.1f}%
- **Average Memory Usage:** {resource_results.get("avg_memory_percent", 0):.1f}%
- **Maximum Memory Usage:** {resource_results.get("max_memory_percent", 0):.1f}%
- **Monitoring Duration:** {resource_results.get("duration", 0):.1f} seconds

"""

        # Add bottleneck analysis
        bottleneck_analysis = self.identify_bottlenecks(all_results)
        content += f"""
### Performance Bottlenecks

"""

        if bottleneck_analysis["bottlenecks"]:
            for bottleneck in bottleneck_analysis["bottlenecks"]:
                content += f"- {bottleneck}\n"
        else:
            content += "- No critical bottlenecks identified\n"

        content += "\n### Recommendations\n\n"

        for rec in bottleneck_analysis["recommendations"]:
            content += f"- {rec}\n"

        content += (
            """
---

## Optimization Recommendations

### Immediate Actions

1. **Use Optimal Polling Rate**: Configure polling at """
            + str(bottleneck_analysis.get("optimal_config", {}).get("polling_rate", 15))
            + """ Hz for best efficiency
2. **Switch to UDP Protocol**: Use port 9878 for parameter updates to reduce latency
3. **Implement Parameter Caching**: Enable caching to reduce redundant MCP calls
4. **Monitor System Resources**: Track CPU/memory usage during operation

### Performance Targets

- **Polling Rate**: 10-20 Hz (configured rate should be achievable)
- **Latency**: <100ms average, <200ms P99 for responsive control
- **CPU Usage**: <50% average for sustained operation
- **Memory Usage**: Monitor for leaks and optimize if >80% sustained

### Long-term Optimizations

1. **Adaptive Rate Control**: Adjust polling frequency based on system load
2. **Batch Parameter Operations**: Group multiple parameter changes in single MCP call
3. **Connection Pooling**: Reuse TCP connections to reduce overhead
4. **Asynchronous Operations**: Implement async I/O for better responsiveness

---

## Testing Methodology

### Environment
- **System**: Python {sys.version.split()[0]}
- **Platform**: {sys.platform}
- **Ableton**: Connected via TCP (port 9877)
- **Plugin**: VST analysis plugin on track 0, device 0

### Test Parameters
- **Polling Rates**: 10 Hz, 15 Hz, 20 Hz for 60 seconds each
- **Latency Test**: Rule-based control with 0.1s cooldown for 30 seconds
- **Resource Monitoring**: 20 Hz polling for 120 seconds with psutil tracking

### Measurement Techniques
- **Polling Efficiency**: (actual_rate / target_rate) × 100
- **Latency**: Time from parameter read to action execution completion
- **Resource Usage**: psutil CPU and memory monitoring during operation
- **Profiling**: cProfile for detailed performance analysis

---

*Report generated by VST Audio Analysis Performance Benchmark Suite*
"""
        )

        return content


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Performance benchmarking for VST audio analysis system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Run all benchmarks for 3 minutes
  python benchmark.py --test=all --duration=180
  
  # Test polling rates specifically
  python benchmark.py --test=polling_rates --duration=60
  
  # Test latency with verbose output
  python benchmark.py --test=latency --duration=30
  
  # Monitor CPU and memory usage
  python benchmark.py --test=cpu_memory --duration=120
        """,
    )

    parser.add_argument(
        "--test",
        type=str,
        required=True,
        choices=["polling_rates", "latency", "cpu_memory", "profiling", "all"],
        help="Type of benchmark to run",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration in seconds for each test (default: 60)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for performance report (default: docs/vst-plugins/performance_report.md)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    print("=" * 70)
    print("VST AUDIO ANALYSIS PERFORMANCE BENCHMARK SUITE")
    print("=" * 70)
    print(f"Test type: {args.test}")
    print(f"Duration: {args.duration} seconds")
    print("=" * 70)
    print()

    benchmarker = PerformanceBenchmarker()
    all_results = {}

    try:
        if args.test == "polling_rates" or args.test == "all":
            print("Running parameter polling rate benchmarks...")
            all_results["polling_rates"] = benchmarker.benchmark_polling_rates(
                args.duration
            )

        if args.test == "latency" or args.test == "all":
            print("Running control loop latency benchmarks...")
            all_results["latency"] = benchmarker.benchmark_latency(args.duration)

        if args.test == "cpu_memory" or args.test == "all":
            print("Running CPU and memory usage benchmarks...")
            all_results["cpu_memory"] = benchmarker.benchmark_cpu_memory(args.duration)

        if args.test == "profiling" or args.test == "all":
            print("Running detailed profiling benchmarks...")
            all_results["profiling"] = benchmarker.run_profiling_benchmark(
                args.duration
            )

        # Generate bottleneck analysis
        if all_results:
            bottleneck_analysis = benchmarker.identify_bottlenecks(all_results)

            # Generate comprehensive report
            benchmarker.generate_report(all_results, args.output)

            print("\n" + "=" * 70)
            print("BENCHMARK SUMMARY")
            print("=" * 70)

            # Print summary statistics
            if "polling_rates" in all_results:
                polling_results = all_results["polling_rates"]
                successful_tests = sum(
                    1 for r in polling_results.values() if r.get("error") is None
                )
                print(
                    f"Polling rate tests: {successful_tests}/{len(polling_results)} successful"
                )

                if successful_tests > 0:
                    best_rate = None
                    best_efficiency = 0
                    for rate, result in polling_results.items():
                        if result.get("error") is None:
                            efficiency = result.get("efficiency", 0)
                            if efficiency > best_efficiency:
                                best_efficiency = efficiency
                                best_rate = rate
                    print(
                        f"Recommended polling rate: {best_rate} Hz ({best_efficiency:.1f}% efficiency)"
                    )

            if "latency" in all_results:
                latency_result = all_results["latency"]
                if latency_result.get("error") is None:
                    target_met = latency_result.get("target_met", False)
                    print(
                        f"Latency test: {'PASS' if target_met else 'FAIL'} (<100ms target)"
                    )
                    print(
                        f"Average latency: {latency_result.get('avg_latency_ms', 0):.2f} ms"
                    )

            if "cpu_memory" in all_results:
                resource_result = all_results["cpu_memory"]
                if resource_result.get("error") is None:
                    avg_cpu = resource_result.get("avg_cpu_percent", 0)
                    print(f"Resource usage: Average CPU {avg_cpu:.1f}%")

            print(
                f"Performance report saved to: {args.output or 'docs/vst-plugins/performance_report.md'}"
            )
            print("=" * 70)

    except KeyboardInterrupt:
        print("\nBenchmarking interrupted by user")
    except Exception as e:
        print(f"Benchmarking failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
