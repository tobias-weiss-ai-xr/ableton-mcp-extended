"""
Examples demonstrating benchmark usage for the audio analysis system.

Author: Audio Analysis System
Date: 2025-02-10
"""

import time
import gc
from typing import List, Dict

from .benchmarks import BenchmarkSuite, DataCollector, CPUMonitor, LatencyTimer
from .benchmark_report import generate_report


# ============================================================================
# Example 1: Simple Data Collection
# ============================================================================


def example_1_simple_data_collection():
    """
    Demonstrates basic DataCollector usage for collecting performance samples.
    """
    print("=" * 80)
    print("EXAMPLE 1: Simple Data Collection")
    print("=" * 80)
    print()

    collector = DataCollector()

    # Collect some sample values
    print("Collecting 100 samples...")
    for i in range(100):
        value = 0.5 + 0.1 * (i % 10 - 5)  # Simulated parameter value
        collector.add_sample(value)

    print(f"Collected {collector.size()} samples")
    print(f"First 5: {collector.get_all_values()[:5]}")
    print(f"Last 5:  {collector.get_all_values()[-5:]}")
    print()

    # Statistics
    values = collector.get_all_values()
    print(f"Min:  {min(values):.4f}")
    print(f"Max:  {max(values):.4f}")
    print(f"Mean: {sum(values) / len(values):.4f}")
    print()


# ============================================================================
# Example 2: CPU Monitoring
# ============================================================================


def example_2_cpu_monitoring():
    """
    Demonstrates CPU usage monitoring during operation.
    """
    print("=" * 80)
    print("EXAMPLE 2: CPU Monitoring")
    print("=" * 80)
    print()

    monitor = CPUMonitor(interval=0.1)

    print("Starting CPU monitor for 2 seconds...")
    with monitor.monitor_context():
        # Simulate work
        for i in range(10):
            # Do some work
            x = sum(range(10000))
            time.sleep(0.2)

    print("CPU monitoring complete.")

    cpu_values = monitor.get_cpu_values()
    if cpu_values:
        print(f"Collected {len(cpu_values)} CPU samples")
        print(f"Min:  {min(cpu_values):.2f}%")
        print(f"Max:  {max(cpu_values):.2f}%")
        print(f"Mean: {sum(cpu_values) / len(cpu_values):.2f}%")
    else:
        print("No CPU samples collected (psutil may not be available)")
    print()


# ============================================================================
# Example 3: Latency Timing
# ============================================================================


def example_3_latency_timing():
    """
    Demonstrates precise latency measurement for control operations.
    """
    print("=" * 80)
    print("EXAMPLE 3: Latency Timing")
    print("=" * 80)
    print()

    latencies = []

    for i in range(100):
        timer = LatencyTimer()
        timer.start()

        # Simulate polling
        timer.mark_stage("poll")
        time.sleep(0.001)

        # Simulate evaluation
        timer.mark_stage("evaluate")
        time.sleep(0.0005)

        # Simulate action
        timer.mark_stage("act")
        time.sleep(0.001)

        timer.stop()

        latencies.append(timer.elapsed())

    avg_latency = sum(latencies) / len(latencies)
    print(f"Measured 100 iterations")
    print(f"Min latency:  {min(latencies) * 1000:.3f} ms")
    print(f"Max latency:  {max(latencies) * 1000:.3f} ms")
    print(f"Mean latency: {avg_latency * 1000:.3f} ms")
    print()


# ============================================================================
# Example 4: Custom Benchmark Function
# ============================================================================


def example_4_custom_benchmark():
    """
    Demonstrates running a custom benchmark function.
    """
    print("=" * 80)
    print("EXAMPLE 4: Custom Benchmark")
    print("=" * 80)
    print()

    suite = BenchmarkSuite()

    def mock_operation():
        """Simulate an operation to benchmark."""
        time.sleep(0.001)
        return time.perf_counter()

    result = suite.run_benchmark(
        name="Mock Operation Time", func=mock_operation, target_samples=100
    )

    print(f"Benchmark: {result.name}")
    print(f"Samples:   {result.samples}")
    print(f"Duration:  {result.duration_seconds:.3f}s")
    print(f"Min:       {result.min_value:.6f}s")
    print(f"Mean:      {result.mean_value:.6f}s")
    print(f"Median:    {result.median_value:.6f}s")
    print(f"P95:       {result.p95:.6f}s")
    print(f"P99:       {result.p99:.6f}s")
    print()


# ============================================================================
# Example 5: Polling Rate Benchmark (Mock)
# ============================================================================


def example_5_polling_rate_benchmark():
    """
    Demonstrates polling rate accuracy measurement.
    """
    print("=" * 80)
    print("EXAMPLE 5: Polling Rate Benchmark")
    print("=" * 80)
    print()

    suite = BenchmarkSuite()

    # Mock poller (just timing intervals)
    class MockPoller:
        def __init__(self):
            self.call_count = 0

        def poll_parameters(self):
            self.call_count += 1
            # Simulate very fast poll
            pass

    mock_poller = MockPoller()

    result = suite.polling_rate_benchmark(
        poller=mock_poller, target_rate_hz=20, duration_seconds=2.0
    )

    print(f"Benchmark: {result.name}")
    print(f"Target rate: 20 Hz")
    print(f"Actual rate: {result.samples / result.duration_seconds:.1f} Hz")
    print(f"Samples: {result.samples}")
    print(f"Mean interval: {result.mean_value * 1000:.2f} ms")
    print(f"Std dev:      {result.std_dev * 1000:.3f} ms")
    print(f"Min interval: {result.min_value * 1000:.2f} ms")
    print(f"Max interval: {result.max_value * 1000:.2f} ms")
    print(f"Jitter (std dev): {result.std_dev * 1000:.3f} ms")
    print(f"Jitter %:        {(result.std_dev / result.mean_value) * 100:.2f}%")
    print()


# ============================================================================
# Example 6: Rule Evaluation Benchmark (Mock)
# ============================================================================


def example_6_rule_evaluation_benchmark():
    """
    Demonstrates rule evaluation performance.
    """
    print("=" * 80)
    print("EXAMPLE 6: Rule Evaluation Benchmark")
    print("=" * 80)
    print()

    suite = BenchmarkSuite()

    # Mock rule engine
    class MockRuleEngine:
        def __init__(self):
            self.evaluation_count = 0

        def evaluate_all_rules(self, params: Dict):
            self.evaluation_count += 1
            # Simulate rule evaluation
            time.sleep(0.0001)
            return []

    mock_engine = MockRuleEngine()

    result = suite.rule_evaluation_benchmark(
        rule_engine=mock_engine, poll_iterations=100
    )

    print(f"Benchmark: {result.name}")
    print(f"Iterations: {result.samples}")
    print(
        f"Total time: {result.result.duration_seconds:.3f}s"
        if hasattr(result, "result")
        else "Total time: N/A"
    )
    print(f"Mean time:  {result.mean_value * 1000:.3f} ms")
    print(f"Median time: {result.median_value * 1000:.3f} ms")
    print(f"Max time:    {result.max_value * 1000:.3f} ms")
    print(f"P95 time:    {result.p95 * 1000:.3f} ms")
    print(f"P99 time:    {result.p99 * 1000:.3f} ms")

    # Calculate max throughput
    max_throughput = 1.0 / result.p99
    print(f"Max throughput (at P99): {max_throughput:.0f} evaluations/sec")
    print()


# ============================================================================
# Example 7: Complete Benchmark Suite
# ============================================================================


def example_7_complete_benchmark_suite():
    """
    Demonstrates running a complete benchmark suite.
    """
    print("=" * 80)
    print("EXAMPLE 7: Complete Benchmark Suite")
    print("=" * 80)
    print()

    suite = BenchmarkSuite()

    # Benchmark 1: Mock polling rate
    class MockPoller:
        def poll_parameters(self):
            pass

    result1 = suite.polling_rate_benchmark(
        poller=MockPoller(), target_rate_hz=10, duration_seconds=2.0
    )
    suite.add_result(result1)

    # Benchmark 2: Mock rule evaluation
    class MockRuleEngine:
        def evaluate_all_rules(self, params):
            time.sleep(0.0001)
            return []

    result2 = suite.rule_evaluation_benchmark(
        rule_engine=MockRuleEngine(), poll_iterations=100
    )
    suite.add_result(result2)

    # Benchmark 3: Custom operation
    def custom_op():
        x = sum(range(1000))
        return x

    result3 = suite.run_benchmark(
        name="Custom Operation", func=custom_op, target_samples=100
    )
    suite.add_result(result3)

    # Print summary
    suite.print_summary()

    # Generate simple report
    report = generate_report(
        suite=suite,
        duration_seconds=10.0,
        output_json=None,  # Don't save to file
        output_markdown=None,
        output_text=None,
    )

    print("\nReport Summary:")
    print(f"  Performance Grade: {report.performance_grade}")
    print(f"  Recommendations: {len(report.recommendations)}")

    for rec in report.recommendations:
        print(f"    - {rec}")

    print()


# ============================================================================
# Example 8: End-to-End Timing with Context Manager
# ============================================================================


def example_8_latency_context_manager():
    """
    Demonstrates using LatencyTimer with context manager (if implemented).
    """
    print("=" * 80)
    print("EXAMPLE 8: Latency Context Manager")
    print("=" * 80)
    print()

    timings = []

    for i in range(10):
        timer = LatencyTimer()

        # Use context manager pattern (if available)
        # For now, use start/stop
        timer.start()

        # Simulate operation
        time.sleep(0.001)

        timer.stop()

        timings.append(timer.elapsed())

    print(f"Measured 10 operations")
    print(f"Average latency: {sum(timings) / len(timings) * 1000:.3f} ms")
    print()


# ============================================================================
# Example 9: Benchmark with Memory Cleanup
# ============================================================================


def example_9_benchmark_with_gc():
    """
    Demonstrates benchmarking with controlled garbage collection.
    """
    print("=" * 80)
    print("EXAMPLE 9: Benchmark with GC Control")
    print("=" * 80)
    print()

    suite = BenchmarkSuite()

    def memory_intensive_operation():
        """Operation that creates temporary objects."""
        result = []
        for i in range(100):
            result.append([j for j in range(10)])
        return len(result)

    # Force GC before benchmark
    gc.collect()

    result = suite.run_benchmark(
        name="GC-Controlled Operation",
        func=memory_intensive_operation,
        target_samples=50,
    )

    print(f"Benchmark: {result.name}")
    print(f"Mean time: {result.mean_value * 1000:.3f} ms")
    print()

    # Force GC after benchmark
    gc.collect()
    print("Garbage collection performed.")
    print()


# ============================================================================
# Example 10: Multi-Stage Timing Breakdown
# ============================================================================


def example_10_stage_timing():
    """
    Demonstrates measuring individual stages of a process.
    """
    print("=" * 80)
    print("EXAMPLE 10: Multi-Stage Timing Breakdown")
    print("=" * 80)
    print()

    measurements = {"poll": [], "evaluate": [], "act": [], "total": []}

    for i in range(20):
        timer = LatencyTimer()
        timer.start()

        # Poll stage
        poll_start = time.perf_counter()
        time.sleep(0.001)
        poll_end = time.perf_counter()
        measurements["poll"].append(poll_end - poll_start)
        timer.mark_stage("poll")

        # Evaluate stage
        eval_start = time.perf_counter()
        time.sleep(0.0005)
        eval_end = time.perf_counter()
        measurements["evaluate"].append(eval_end - eval_start)
        timer.mark_stage("evaluate")

        # Act stage
        act_start = time.perf_counter()
        time.sleep(0.001)
        act_end = time.perf_counter()
        measurements["act"].append(act_end - act_start)
        timer.mark_stage("act")

        timer.stop()
        measurements["total"].append(timer.elapsed())

    print("Stage Breakdown (averages over 20 iterations):")
    for stage, values in measurements.items():
        avg = sum(values) / len(values)
        pct = (
            avg
            / sum(measurements["total"])
            / measure_stage_avg(sum(measurements["total"]))
        ) * 100
        print(f"  {stage:8s}: {avg * 1000:6.3f} ms ({pct:5.1f}%)")
    print()


def measure_stage_avg(total_sum):
    """Helper to calculate percentage."""
    return lambda x: (x / total_sum) * 100


# ============================================================================
# Main
# ============================================================================


def main():
    """Run all examples."""
    examples = [
        example_1_simple_data_collection,
        example_2_cpu_monitoring,
        example_3_latency_timing,
        example_4_custom_benchmark,
        example_5_polling_rate_benchmark,
        example_6_rule_evaluation_benchmark,
        example_7_complete_benchmark_suite,
        example_8_latency_context_manager,
        example_9_benchmark_with_gc,
        example_10_stage_timing,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
            print()
        except Exception as e:
            print(f"Error running example {i}: {e}")
            import traceback

            traceback.print_exc()
            print()

    print("All examples completed.")


if __name__ == "__main__":
    main()
