"""
Benchmark framework for audio analysis system.

This module provides performance measurement tools for:
- Polling rate accuracy and stability
- CPU usage over time
- End-to-end latency (poll → evaluate → act)
- Memory usage patterns

Author: Audio Analysis System
Date: 2025-02-10
"""

import time
import psutil
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from contextlib import contextmanager
from collections import defaultdict
import statistics

from .polling import AudioParameterPoller
from .rules import RuleEngine
from .control_loop import AudioAnalysisController


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    name: str
    duration_seconds: float
    samples: int

    # Statistics
    min_value: float
    max_value: float
    mean_value: float
    median_value: float
    std_dev: float

    # Percentiles
    p1: float  # 1st percentile
    p5: float  # 5th percentile
    p25: float  # 25th percentile
    p75: float  # 75th percentile
    p95: float  # 95th percentile
    p99: float  # 99th percentile

    # Additional metrics
    values: List[float] = field(default_factory=list, repr=False)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "duration_seconds": self.duration_seconds,
            "samples": self.samples,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "mean_value": self.mean_value,
            "median_value": self.median_value,
            "std_dev": self.std_dev,
            "p1": self.p1,
            "p5": self.p5,
            "p25": self.p25,
            "p75": self.p75,
            "p95": self.p95,
            "p99": self.p99,
            "metadata": self.metadata,
        }

    @classmethod
    def from_values(
        cls, name: str, values: List[float], **metadata
    ) -> "BenchmarkResult":
        """Create BenchmarkResult from raw values."""
        if not values:
            raise ValueError("No values provided")

        sorted_values = sorted(values)
        n = len(values)

        return cls(
            name=name,
            duration_seconds=metadata.get("duration_seconds", 0.0),
            samples=n,
            min_value=min(values),
            max_value=max(values),
            mean_value=statistics.mean(values),
            median_value=statistics.median(values),
            std_dev=statistics.stdev(values) if n > 1 else 0.0,
            p1=sorted_values[int(0.01 * n)] if n >= 100 else sorted_values[0],
            p5=sorted_values[int(0.05 * n)] if n >= 20 else sorted_values[0],
            p25=sorted_values[int(0.25 * n)],
            p75=sorted_values[int(0.75 * n)],
            p95=sorted_values[int(0.95 * n)] if n >= 20 else sorted_values[-1],
            p99=sorted_values[int(0.99 * n)] if n >= 100 else sorted_values[-1],
            values=values,
            metadata=metadata,
        )


class DataCollector:
    """Collects benchmark data over time."""

    def __init__(self, max_size: int = 100000):
        """
        Initialize data collector.

        Args:
            max_size: Maximum number of samples to retain
        """
        self.values: List[float] = []
        self.timestamps: List[float] = []
        self.max_size = max_size
        self.lock = threading.Lock()

    def add_sample(self, value: float, timestamp: float = None) -> None:
        """
        Add a sample to the collector.

        Args:
            value: Sample value
            timestamp: Sample timestamp (default: current time)
        """
        if timestamp is None:
            timestamp = time.time()

        with self.lock:
            self.values.append(value)
            self.timestamps.append(timestamp)

            # Trim if exceeds max size
            if len(self.values) > self.max_size:
                self.values = self.values[-self.max_size :]
                self.timestamps = self.timestamps[-self.max_size :]

    def get_all_values(self) -> List[float]:
        """Get all collected values (thread-safe)."""
        with self.lock:
            return self.values.copy()

    def get_all_timestamps(self) -> List[float]:
        """Get all timestamps (thread-safe)."""
        with self.lock:
            return self.timestamps.copy()

    def clear(self) -> None:
        """Clear all collected data."""
        with self.lock:
            self.values.clear()
            self.timestamps.clear()

    def size(self) -> int:
        """Get number of samples collected."""
        with self.lock:
            return len(self.values)


class CPUMonitor:
    """Monitors CPU usage over time."""

    def __init__(self, interval: float = 0.1):
        """
        Initialize CPU monitor.

        Args:
            interval: Sampling interval in seconds
        """
        self.interval = interval
        self.process = psutil.Process()
        self.collector = DataCollector()
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        process = psutil.Process()
        collector = self.collector

        while self.running:
            try:
                # Get CPU percentage since last call
                cpu_percent = process.cpu_percent(interval=None)

                # Get memory usage
                mem_info = process.memory_info()
                mem_mb = mem_info.rss / (1024 * 1024)

                # Store both metrics (store combined metric: cpu + 100 * mem_mb_factor)
                # This keeps them in same collector for simplicity
                # For now, just track CPU
                collector.add_sample(cpu_percent, time.time())

                time.sleep(self.interval)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process may have been terminated
                break

    def start(self) -> None:
        """Start CPU monitoring in background thread."""
        with self.lock:
            if self.running:
                return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop CPU monitoring."""
        with self.lock:
            if not self.running:
                return

        self.running = False

        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None

    def get_cpu_values(self) -> List[float]:
        """Get all CPU usage samples."""
        return self.collector.get_all_values()

    def get_timestamps(self) -> List[float]:
        """Get all sample timestamps."""
        return self.collector.get_all_timestamps()

    def clear(self) -> None:
        """Clear collected data."""
        self.collector.clear()

    @contextmanager
    def monitor_context(self):
        """Context manager for automatic CPU monitoring."""
        self.start()
        try:
            yield self
        finally:
            self.stop()


class LatencyTimer:
    """Measures end-to-end latency for operations."""

    def __init__(self):
        """Initialize latency timer."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.stages: Dict[str, float] = {}

    def start(self) -> None:
        """Start timing."""
        self.start_time = time.perf_counter()
        self.end_time = None
        self.stages.clear()

    def mark_stage(self, stage_name: str) -> None:
        """
        Mark a timing checkpoint.

        Args:
            stage_name: Name of the checkpoint
        """
        if self.start_time is None:
            raise RuntimeError("Timer not started. Call start() first.")

        stage_time = time.perf_counter() - self.start_time
        self.stages[stage_name] = stage_time

    def stop(self) -> float:
        """
        Stop timing and return elapsed time.

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            raise RuntimeError("Timer not started. Call start() first.")

        self.end_time = time.perf_counter()
        return self.end_time - self.start_time

    def elapsed(self) -> Optional[float]:
        """
        Get elapsed time (if stopped).

        Returns:
            Elapsed time in seconds, or None if not stopped
        """
        if self.start_time is None or self.end_time is None:
            return None
        return self.end_time - self.start_time

    def get_stage_duration(self, stage_name: str) -> Optional[float]:
        """
        Get duration from start to a specific stage.

        Args:
            stage_name: Name of the stage

        Returns:
            Duration in seconds, or None if stage not marked
        """
        return self.stages.get(stage_name)

    def get_stage_durations(self) -> Dict[str, float]:
        """Get all stage durations."""
        return self.stages.copy()

    @contextmanager
    def measure(self):
        """Context manager for automatic timing."""
        self.start()
        try:
            yield self
        finally:
            self.stop()


class BenchmarkSuite:
    """Suite of benchmarks for audio analysis system."""

    def __init__(self):
        """Initialize benchmark suite."""
        self.results: List[BenchmarkResult] = []

    def run_benchmark(
        self,
        name: str,
        func: Callable[[], float],
        duration_seconds: float = 10.0,
        target_samples: Optional[int] = None,
    ) -> BenchmarkResult:
        """
        Run a single benchmark function repeatedly.

        Args:
            name: Benchmark name
            func: Function to benchmark (returns a measured value)
            duration_seconds: Duration to run benchmark
            target_samples: Target number of samples (alternative to duration)

        Returns:
            BenchmarkResult with statistics
        """
        values = []
        target_time = time.perf_counter()

        # Determine stopping condition
        if target_samples is not None:
            while len(values) < target_samples:
                value = func()
                values.append(value)
        else:
            end_time = time.time() + duration_seconds
            while time.time() < end_time:
                value = func()
                values.append(value)

        actual_duration = time.time() - target_time

        return BenchmarkResult.from_values(
            name=name, values=values, duration=actual_duration
        )

    def polling_rate_benchmark(
        self,
        poller: AudioParameterPoller,
        target_rate_hz: int,
        duration_seconds: float = 10.0,
        param_indices: Optional[List[int]] = None,
    ) -> BenchmarkResult:
        """
        Benchmark the polling rate accuracy and stability.

        Args:
            poller: AudioParameterPoller instance (or mock)
            target_rate_hz: Target polling rate in Hz
            duration_seconds: Benchmark duration
            param_indices: Parameter indices to poll

        Returns:
            BenchmarkResult with interval statistics
        """
        param_indices = param_indices or [0]

        intervals = []
        start_time = time.perf_counter()
        last_poll_time = None

        poll_count = 0

        while (time.perf_counter() - start_time) < duration_seconds:
            if last_poll_time is None:
                last_poll_time = time.perf_counter()

            # Simulate or perform poll
            try:
                if hasattr(poller, "poll_parameters"):
                    poller.poll_parameters()
                else:
                    # Mock poll - just sleep
                    pass
            except Exception:
                pass

            current_time = time.perf_counter()
            intervals.append(current_time - last_poll_time)
            last_poll_time = current_time
            poll_count += 1

            # Sleep to maintain target rate
            sleep_time = max(
                0, (1.0 / target_rate_hz) - (current_time - last_poll_time)
            )
            if sleep_time > 0:
                time.sleep(sleep_time)

        actual_duration = time.perf_counter() - start_time
        actual_rate = poll_count / actual_duration

        return BenchmarkResult.from_values(
            name=f"Polling Rate (target={target_rate_hz}Hz)",
            values=intervals,
            duration_seconds=actual_duration,
        )

    def cpu_usage_benchmark(
        self, controller, duration_seconds: float = 10.0
    ) -> BenchmarkResult:
        """
        Benchmark CPU usage during audio analysis control loop.

        Args:
            controller: AudioAnalysisController instance
            duration_seconds: Benchmark duration

        Returns:
            BenchmarkResult with CPU usage statistics
        """
        monitor = CPUMonitor(interval=0.1)

        # Start monitoring
        monitor.start()

        # Run controller
        try:
            if hasattr(controller, "start"):
                controller.start()

            end_time = time.time() + duration_seconds
            while time.time() < end_time:
                time.sleep(0.1)

        finally:
            if hasattr(controller, "stop"):
                controller.stop()

            monitor.stop()

        cpu_values = monitor.get_cpu_values()

        return BenchmarkResult.from_values(
            name=f"CPU Usage ({duration_seconds}s)",
            values=cpu_values,
            duration_seconds=duration_seconds,
        )

    def end_to_end_latency_benchmark(
        self, controller, poll_iterations: int = 1000
    ) -> BenchmarkResult:
        """
        Benchmark end-to-end latency (poll → evaluate → act).

        Args:
            controller: AudioAnalysisController instance
            poll_iterations: Number of iterations to measure

        Returns:
            BenchmarkResult with latency statistics
        """
        latencies = []

        for _ in range(poll_iterations):
            timer = LatencyTimer()
            timer.start()

            # Simulate control loop steps
            # Poll
            if hasattr(controller, "_poll_one_cycle"):
                controller._poll_one_cycle()
                timer.mark_stage("poll")

            # Evaluate
            if hasattr(controller, "_evaluate_rules"):
                controller._evaluate_rules()
                timer.mark_stage("evaluate")

            # Act
            if hasattr(controller, "_execute_actions"):
                controller._execute_actions()
                timer.mark_stage("act")

            elapsed = timer.stop()
            latencies.append(elapsed)

            # Natural delay
            time.sleep(0.001)

        return BenchmarkResult.from_values(
            name="End-to-End Latency (poll → evaluate → act)", values=latencies
        )

    def rule_evaluation_benchmark(
        self, rule_engine: RuleEngine, poll_iterations: int = 1000
    ) -> BenchmarkResult:
        """
        Benchmark rule evaluation performance.

        Args:
            rule_engine: RuleEngine instance
            poll_iterations: Number of evaluations

        Returns:
            BenchmarkResult with evaluation time statistics
        """
        evaluation_times = []

        # Create sample parameters
        sample_params = {
            "total_loudness": 0.5,
            "spectral_centroid": 0.7,
            "peak_level": 0.3,
            "rms_level": 0.4,
        }

        for _ in range(poll_iterations):
            start_time = time.perf_counter()

            # Evaluate rules
            if hasattr(rule_engine, "evaluate_all_rules"):
                rule_engine.evaluate_all_rules(sample_params)
            else:
                # Mock evaluation
                time.sleep(0.0001)

            elapsed = time.perf_counter() - start_time
            evaluation_times.append(elapsed)

        return BenchmarkResult.from_values(
            name="Rule Evaluation Time", values=evaluation_times
        )

    def add_result(self, result: BenchmarkResult) -> None:
        """Add a benchmark result to the suite."""
        self.results.append(result)

    def get_results(self) -> List[BenchmarkResult]:
        """Get all benchmark results."""
        return self.results.copy()

    def clear_results(self) -> None:
        """Clear all benchmark results."""
        self.results.clear()

    def print_summary(self) -> None:
        """Print summary of all benchmark results."""
        if not self.results:
            print("No benchmark results available.")
            return

        print("\n" + "=" * 80)
        print("BENCHMARK RESULTS SUMMARY")
        print("=" * 80)

        for result in self.results:
            print(f"\n{result.name}")
            print(f"  Duration: {result.duration_seconds:.3f}s")
            print(f"  Samples:  {result.samples}")
            print(f"  Min:      {result.min_value:.6f}")
            print(f"  Mean:     {result.mean_value:.6f}")
            print(f"  Median:   {result.median_value:.6f}")
            print(f"  Max:      {result.max_value:.6f}")
            print(f"  Std Dev:  {result.std_dev:.6f}")
            print(f"  P95:      {result.p95:.6f}")
            print(f"  P99:      {result.p99:.6f}")

        print("\n" + "=" * 80 + "\n")
