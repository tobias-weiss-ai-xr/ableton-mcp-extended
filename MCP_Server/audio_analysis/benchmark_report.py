"""
Benchmark report generator for audio analysis system.

This module provides tools for generating detailed benchmark reports
in multiple formats (text, JSON, Markdown).

Author: Audio Analysis System
Date: 2025-02-10
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .benchmarks import BenchmarkResult, BenchmarkSuite


@dataclass
class BenchmarkReport:
    """Complete benchmark report."""

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    system_info: Dict[str, str] = field(default_factory=dict)
    test_duration_seconds: float = 0.0

    # Results
    results: List[BenchmarkResult] = field(default_factory=list)

    # Summary statistics
    total_benchmarks: int = 0
    passed_benchmarks: int = 0
    performance_grade: str = "N/A"

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    def add_result(self, result: BenchmarkResult) -> None:
        """Add a benchmark result."""
        self.results.append(result)
        self.total_benchmarks += 1

    def get_result_by_name(self, name: str) -> Optional[BenchmarkResult]:
        """Get a benchmark result by name."""
        for result in self.results:
            if result.name == name:
                return result
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": {
                "timestamp": self.timestamp,
                "system_info": self.system_info,
                "test_duration_seconds": self.test_duration_seconds,
                "total_benchmarks": self.total_benchmarks,
                "passed_benchmarks": self.passed_benchmarks,
                "performance_grade": self.performance_grade,
            },
            "results": [r.to_dict() for r in self.results],
            "recommendations": self.recommendations,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save_json(self, path: str) -> None:
        """Save report to JSON file."""
        Path(path).write_text(self.to_json(indent=2))

    def to_markdown(self) -> str:
        """Generate Markdown report."""
        lines = []

        # Title
        lines.append("# Audio Analysis System - Benchmark Report")
        lines.append("")

        # Metadata
        lines.append("## Metadata")
        lines.append("")
        lines.append(f"- **Timestamp**: {self.timestamp}")
        lines.append(f"- **Total Benchmarks**: {self.total_benchmarks}")
        lines.append(f"- **Passed**: {self.passed_benchmarks}")
        lines.append(f"- **Duration**: {self.test_duration_seconds:.2f}s")
        lines.append(f"- **Performance Grade**: {self.performance_grade}")
        lines.append("")

        # System Info
        if self.system_info:
            lines.append("### System Information")
            lines.append("")
            for key, value in self.system_info.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        # Results
        lines.append("## Benchmark Results")
        lines.append("")

        for result in self.results:
            lines.append(f"### {result.name}")
            lines.append("")

            # Create table
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Duration | {result.duration_seconds:.3f}s |")
            lines.append(f"| Samples | {result.samples} |")
            lines.append(f"| Min | {result.min_value:.6f} |")
            lines.append(f"| Max | {result.max_value:.6f} |")
            lines.append(f"| Mean | {result.mean_value:.6f} |")
            lines.append(f"| Median | {result.median_value:.6f} |")
            lines.append(f"| Std Dev | {result.std_dev:.6f} |")
            lines.append(f"| P25 | {result.p25:.6f} |")
            lines.append(f"| P75 | {result.p75:.6f} |")
            lines.append(f"| P95 | {result.p95:.6f} |")
            lines.append(f"| P99 | {result.p99:.6f} |")
            lines.append("")

            # Add metadata if present
            if result.metadata:
                lines.append("**Additional Metadata:**")
                lines.append("")
                for key, value in result.metadata.items():
                    lines.append(f"- `{key}`: {value}")
                lines.append("")

        # Recommendations
        if self.recommendations:
            lines.append("## Recommendations")
            lines.append("")

            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")

            lines.append("")

        return "\n".join(lines)

    def save_markdown(self, path: str) -> None:
        """Save report to Markdown file."""
        Path(path).write_text(self.to_markdown())

    def to_text(self) -> str:
        """Generate plain text report."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("AUDIO ANALYSIS SYSTEM - BENCHMARK REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Timestamp: {self.timestamp}")
        lines.append(f"Total Benchmarks: {self.total_benchmarks}")
        lines.append(f"Passed: {self.passed_benchmarks}")
        lines.append(f"Duration: {self.test_duration_seconds:.2f}s")
        lines.append(f"Performance Grade: {self.performance_grade}")
        lines.append("")

        # System Info
        if self.system_info:
            lines.append("-" * 80)
            lines.append("SYSTEM INFORMATION")
            lines.append("-" * 80)
            lines.append("")
            for key, value in self.system_info.items():
                lines.append(f"{key}: {value}")
            lines.append("")

        # Results
        lines.append("-" * 80)
        lines.append("BENCHMARK RESULTS")
        lines.append("-" * 80)
        lines.append("")

        for result in self.results:
            lines.append(f"\n{result.name}")
            lines.append(f"  Duration:  {result.duration_seconds:.3f}s")
            lines.append(f"  Samples:   {result.samples}")
            lines.append(f"  Min:       {result.min_value:.6f}")
            lines.append(f"  Mean:      {result.mean_value:.6f}")
            lines.append(f"  Median:    {result.median_value:.6f}")
            lines.append(f"  Max:       {result.max_value:.6f}")
            lines.append(f"  Std Dev:   {result.std_dev:.6f}")
            lines.append(f"  P95:       {result.p95:.6f}")
            lines.append(f"  P99:       {result.p99:.6f}")

            if result.metadata:
                lines.append("  Metadata:")
                for key, value in result.metadata.items():
                    lines.append(f"    {key}: {value}")

            lines.append("")

        # Recommendations
        if self.recommendations:
            lines.append("-" * 80)
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 80)
            lines.append("")

            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")

            lines.append("")

        lines.append("=" * 80)
        lines.append("")

        return "\n".join(lines)

    def save_text(self, path: str) -> None:
        """Save report to text file."""
        Path(path).write_text(self.to_text())


class ReportGenerator:
    """Generator for comprehensive benchmark reports."""

    def __init__(self):
        """Initialize report generator."""
        self.report = BenchmarkReport()

    def collect_system_info(self) -> None:
        """Collect system information for the report."""
        try:
            import platform
            import psutil

            info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": str(psutil.cpu_count()),
                "memory_total_gb": f"{psutil.virtual_memory().total / (1024**3):.2f}",
                "hostname": platform.node(),
            }

            self.report.system_info = info

        except ImportError:
            # psutil not available
            import platform

            self.report.system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": "unknown",
                "memory_total_gb": "unknown",
                "hostname": platform.node(),
            }

    def generate_from_suite(
        self, suite: BenchmarkSuite, duration_seconds: float
    ) -> BenchmarkReport:
        """
        Generate report from benchmark suite.

        Args:
            suite: BenchmarkSuite with results
            duration_seconds: Total test duration

        Returns:
            BenchmarkReport
        """
        self.collect_system_info()
        self.report.results = suite.get_results()
        self.report.total_benchmarks = len(suite.results)
        self.report.test_duration_seconds = duration_seconds

        # Analyze performance and assign grade
        self._analyze_performance()

        return self.report

    def _analyze_performance(self) -> None:
        """Analyze performance and generate recommendations."""
        recommendations = []

        # Check each benchmark
        for result in self.report.results:
            name = result.name.lower()

            # Polling rate analysis
            if "polling rate" in name:
                target_hz = result.metadata.get("target_hz", 10)
                actual_hz = result.samples / result.duration_seconds
                jitter = result.std_dev

                if actual_hz < target_hz * 0.95:
                    recommendations.append(
                        f"Polling rate ({name}) is below target "
                        f"({actual_hz:.1f}Hz vs {target_hz}Hz target)"
                    )

                if jitter > 0.01:  # 10ms jitter
                    recommendations.append(
                        f"High jitter detected in {name} "
                        f"(std dev: {jitter * 1000:.1f}ms)"
                    )

            # CPU usage analysis
            elif "cpu usage" in name:
                if result.mean_value > 50.0:
                    recommendations.append(
                        f"High CPU usage detected ({result.mean_value:.1f}%)"
                    )

            # Latency analysis
            elif "latency" in name:
                target_latency = 1.0 / 20.0  # Target: 50Hz = 20ms
                if result.p95 > target_latency:
                    recommendations.append(
                        f"P95 latency exceeds target "
                        f"({result.p95 * 1000:.1f}ms vs {target_latency * 1000:.1f}ms)"
                    )

        # General recommendations
        if recommendations:
            self.report.recommendations = recommendations
            self.report.performance_grade = "B" if len(recommendations) < 3 else "C"
        else:
            self.report.recommendations = [
                "All benchmarks performing within acceptable limits."
            ]
            self.report.performance_grade = "A"

        self.report.passed_benchmarks = self.report.total_benchmarks


def generate_report(
    suite: BenchmarkSuite,
    duration_seconds: float,
    output_json: Optional[str] = None,
    output_markdown: Optional[str] = None,
    output_text: Optional[str] = None,
) -> BenchmarkReport:
    """
    Generate benchmark reports in multiple formats.

    Args:
        suite: BenchmarkSuite with results
        duration_seconds: Total test duration
        output_json: Path to save JSON report
        output_markdown: Path to save Markdown report
        output_text: Path to save text report

    Returns:
        BenchmarkReport object
    """
    generator = ReportGenerator()
    report = generator.generate_from_suite(suite, duration_seconds)

    if output_json:
        report.save_json(output_json)

    if output_markdown:
        report.save_markdown(output_markdown)

    if output_text:
        report.save_text(output_text)

    return report
