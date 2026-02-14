# VST Audio Analysis - Benchmark Execution and Interpretation Guide

## Table of Contents

1. [Overview](#overview)
2. [Why Benchmark?](#why-benchmark)
3. [Benchmark Types](#benchmark-types)
4. [Running Benchmarks](#running-benchmarks)
5. [Interpreting Results](#interpreting-results)
6. [Performance Targets](#performance-targets)
7. [Optimization Guide](#optimization-guide)
8. [Common Issues](#common-issues)

---

## Overview

The benchmark framework measures system performance for the VST Audio Analysis system. It evaluates polling accuracy, CPU consumption, latency, and rule evaluation speed.

**Key Metrics Measured:**
- **Polling Rate** - Accuracy of parameter polling
- **CPU Usage** - System resource consumption
- **End-to-End Latency** - Time from poll → evaluate → act
- **Rule Evaluation** - Speed of rule engine processing

---

## Why Benchmark?

Benchmarking helps you:

1. **Validate System Performance**
   - Confirm system meets real-time requirements
   - Identify bottlenecks before production use

2. **Capacity Planning**
   - Determine maximum polling rate
   - Estimate resource requirements

3. **Compare Configurations**
   - Test different polling rates (10 Hz vs 20 Hz vs 30 Hz)
   - Evaluate rule performance (simple vs complex rules)

4. **Troubleshoot Issues**
   - Identify why system is slow
   - Pinpoint problematic components

5. **Validate Changes**
   - Measure impact of code optimizations
   - Confirm performance after updates

---

## Benchmark Types

### 1. Polling Rate Benchmark

**Purpose:** Measures how accurately the polling system hits the target rate.

**Metrics:**
- **Actual Rate** - Measured polling frequency (Hz)
- **Accuracy** - Percentage of target rate achieved
- **Jitter** - Variation in polling intervals (milliseconds)
- **Interval Stats** - Min, max, mean, median of polling intervals

**What It Tests:**
- Thread timing precision
- Scheduler overhead
- System load impact

**Example Output:**
```
Polling Rate Benchmark (Target: 20 Hz)
  Actual Rate:      19.78 Hz (98.9% accuracy)
  Jitter:          2.1 ms (4.2% of mean interval)
  Interval:
    Min:  48.5 ms
    Max:  53.7 ms
    Mean: 50.5 ms
    Std:  1.2 ms
```

---

### 2. CPU Usage Benchmark

**Purpose:** Measures CPU consumption during control loop execution.

**Metrics:**
- **Mean CPU** - Average CPU percentage
- **Max CPU** - Peak CPU percentage
- **CPU Stability** - Variation in CPU usage

**What It Tests:**
- Polling overhead
- Rule evaluation cost
- Thread synchronization overhead

**Example Output:**
```
CPU Usage Benchmark (Duration: 10s)
  Mean CPU:    3.2%
  Max CPU:     5.8%
  Std Dev:     0.8%
  Stability:   Good (low variation)
```

---

### 3. End-to-End Latency Benchmark

**Purpose:** Measures total time from poll → evaluate → act.

**Metrics:**
- **Mean Latency** - Average round-trip time (ms)
- **P95 Latency** - 95th percentile (95% of cycles ≤ this)
- **P99 Latency** - 99th percentile (99% of cycles ≤ this)
- **Max Latency** - Worst-case latency

**What It Tests:**
- Polling system performance
- Rule engine speed
- Action handler efficiency

**Example Output:**
```
End-to-End Latency Benchmark (100 iterations)
  Mean:  4.2 ms
  P95:   7.8 ms
  P99:   12.3 ms
  Max:   18.5 ms
```

---

### 4. Rule Evaluation Benchmark

**Purpose:** Measures rule engine processing speed.

**Metrics:**
- **Mean Time** - Average evaluation time per rule set (ms)
- **P95/P99 Time** - Percentile evaluation times
- **Throughput** - Rules per second

**What It Tests:**
- Rule parsing overhead
- Condition evaluation cost
- Action preparation speed

**Example Output:**
```
Rule Evaluation Benchmark (100 iterations, 5 rules)
  Mean:  0.8 ms
  P95:   1.5 ms
  P99:   2.3 ms
  Max:   4.1 ms
  Throughput: 1250 rules/sec
```

---

## Running Benchmarks

### Quick Start

Run all benchmarks with default settings:

```bash
cd MCP_Server/audio_analysis
python benchmark_runner.py
```

**Output:**
```
Running benchmarks...
[====================] 100%

Benchmark Report
================
Total Duration: 10.2s
Performance Grade: A

Recommendations:
  - System is performing optimally

Results saved to:
  results/benchmark_report_20250120_142305.json
  results/benchmark_report_20250120_142305.md
  results/benchmark_report_20250120_142305.txt
```

---

### Custom Duration

```bash
# Run for 30 seconds
python benchmark_runner.py --duration 30
```

---

### Selective Benchmarking

```bash
# Only polling benchmarks
python benchmark_runner.py --type polling --duration 5

# Only rule evaluation
python benchmark_runner.py --type rules --iterations 500

# Only CPU usage
python benchmark_runner.py --type cpu --duration 10
```

---

### Custom Output

```bash
# Save to custom directory
python benchmark_runner.py --output-dir my_results

# Only JSON output
python benchmark_runner.py --formats json

# Only Markdown and Text
python benchmark_runner.py --formats markdown,text
```

---

### Quiet Mode

```bash
# Suppress console output (save only to files)
python benchmark_runner.py --quiet --duration 10
```

---

### Programmatic Usage

```python
from ableton_mcp_extended.audio_analysis.benchmarks import BenchmarkSuite
from ableton_mcp_extended.audio_analysis.benchmark_report import generate_report

# Create suite
suite = BenchmarkSuite()

# Run specific benchmarks
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=20)

# Polling benchmark
polling_result = suite.polling_rate_benchmark(poller, target_rate_hz=20, duration_seconds=5)
suite.add_result(polling_result)

# Generate report
report = generate_report(
    suite=suite,
    duration_seconds=5.0,
    output_json="custom_report.json",
    output_markdown="custom_report.md",
    output_text="custom_report.txt"
)

print(f"Performance Grade: {report.performance_grade}")
```

---

## Interpreting Results

### Performance Grades

The benchmark system assigns grades based on results:

| Grade | Criteria | Implication |
|-------|----------|-------------|
| **A** | All metrics within targets, 0-2 recommendations | Production-ready |
| **B** | Minor issues, 3-4 recommendations | Acceptable with monitoring |
| **C** | Multiple issues, ≥5 recommendations | Not production-ready |

---

### Reading the Report

#### JSON Report (Detailed)

```json
{
  "timestamp": "2025-01-20T14:23:05",
  "system_info": {
    "platform": "Windows",
    "python_version": "3.10.0",
    "cpu_count": 4
  },
  "test_duration_seconds": 10.0,
  "results": [
    {
      "name": "Polling Rate (20 Hz)",
      "duration_seconds": 5.0,
      "samples": 99,
      "mean_value": 19.78,
      "min_value": 19.5,
      "max_value": 20.1,
      "p95": 19.9,
      "p99": 20.0,
      "metadata": {
        "target_rate_hz": 20.0,
        "accuracy_percent": 98.9
      }
    }
  ],
  "performance_grade": "A",
  "recommendations": []
}
```

#### Markdown Report (Human-Readable)

```markdown
# Benchmark Report

**Generated**: 2025-01-20 14:23:05
**Duration**: 10.0 seconds
**Performance Grade**: A

## System Information

| Property | Value |
|----------|-------|
| Platform | Windows |
| Python | 3.10.0 |
| CPU Cores | 4 |

## Results

### Polling Rate (20 Hz)
- **Actual Rate**: 19.78 Hz (98.9% accuracy)
- **Mean Interval**: 50.5 ms
- **P95 Interval**: 51.2 ms
- **Jitter**: 2.1 ms (4.2% of mean)

### CPU Usage
- **Mean CPU**: 3.2%
- **Max CPU**: 5.8%

### End-to-End Latency
- **Mean**: 4.2 ms
- **P95**: 7.8 ms
- **P99**: 12.3 ms

### Rule Evaluation
- **Mean Time**: 0.8 ms
- **Throughput**: 1250 rules/sec

## Recommendations

System is performing optimally.
```

#### Text Report (Console-Friendly)

```
═══════════════════════════════════════════════════════════════
  BENCHMARK REPORT
═══════════════════════════════════════════════════════════════

Generated:    2025-01-20 14:23:05
Duration:     10.0 seconds
Grade:        A

──────────────────────────────────────────────────────────────────
  POLLING RATE (20 Hz)
──────────────────────────────────────────────────────────────────
  Actual Rate:    19.78 Hz (98.9%)
  Mean Interval:  50.5 ms
  Jitter:         2.1 ms

──────────────────────────────────────────────────────────────────
  CPU USAGE
──────────────────────────────────────────────────────────────────
  Mean CPU:       3.2%
  Max CPU:        5.8%

──────────────────────────────────────────────────────────────────
  END-TO-END LATENCY
──────────────────────────────────────────────────────────────────
  Mean:           4.2 ms
  P95:            7.8 ms
  P99:            12.3 ms

──────────────────────────────────────────────────────────────────
  RECOMMENDATIONS
──────────────────────────────────────────────────────────────────
  System is performing optimally.

═══════════════════════════════════════════════════════════════
```

---

## Performance Targets

### Targets by Polling Rate

#### 10 Hz (100ms intervals)

| Metric | Target | Acceptable |
|--------|--------|------------|
| Polling Rate | ≥ 9.5 Hz (≥95%) | ≥ 9.0 Hz |
| Polling Jitter | < 10% of interval | < 15% |
| CPU Usage (Mean) | < 30% | < 50% |
| CPU Usage (Max) | < 60% | < 80% |
| E2E Latency (P99) | < 200ms (2× interval) | < 300ms |
| Rule Evaluation (Mean) | < 10ms | < 20ms |
| Rule Evaluation (P99) | < 20ms | < 40ms |

---

#### 20 Hz (50ms intervals). Default

| Metric | Target | Acceptable |
|--------|--------|------------|
| Polling Rate | ≥ 19.0 Hz (≥95%) | ≥ 18.0 Hz |
| Polling Jitter | < 5% of interval | < 10% |
| CPU Usage (Mean) | < 50% | < 70% |
| CPU Usage (Max) | < 80% | < 90% |
| E2E Latency (P99) | < 100ms (2× interval) | < 150ms |
| Rule Evaluation (Mean) | < 5ms | < 10ms |
| Rule Evaluation (P99) | < 10ms | < 20ms |

---

#### 30 Hz (33ms intervals). High-Performance

| Metric | Target | Acceptable |
|--------|--------|------------|
| Polling Rate | ≥ 28.5 Hz (≥95%) | ≥ 27.0 Hz |
| Polling Jitter | < 3ms | < 5ms |
| CPU Usage (Mean) | < 60% | < 80% |
| CPU Usage (Max) | < 90% | < 95% |
| E2E Latency (P99) | < 67ms (2× interval) | < 100ms |
| Rule Evaluation (Mean) | < 3.3ms | < 6.7ms |
| Rule Evaluation (P99) | < 6.7ms | < 13.3ms |

---

### Interpreting Against Targets

**Example: Polling Rate Benchmark at 20 Hz**

```
Results:
  Actual Rate: 18.2 Hz (91% accuracy)
  Jitter: 6.0 ms (12% of interval)

Analysis:
  - Actual rate: FAIL (18.2 < 19.0 target)
  - Accuracy: FAIL (91% < 95% target)
  - Jitter: FAIL (12% > 5% target)

Recommendation:
  Reduce polling rate to 10 Hz or optimize system.
```

---

### What If I Don't Meet Targets?

**If polling rate is low (<90% accuracy):**
- Reduce target rate (e.g., 20 Hz → 10 Hz)
- Check CPU usage (if >80%, system overloaded)
- Reduce number of metrics
- Simplify rules

**If jitter is high (>10% of interval):**
- Check background processes (antivirus, backups)
- Reduce polling rate
- Use dedicated CPU (affinity)

**If CPU usage is high (>70% mean):**
- Reduce polling rate
- Reduce number of metrics
- Simplify rule conditions
- Use faster hardware

**If latency is high (>2× interval):**
- Check rule evaluation time
- Optimize action handler
- Use faster polling rate (split polling from evaluation)

---

## Optimization Guide

### 1. Reduce Polling Rate

**Before:**
```python
poller = ThreadPoller(metrics, target_rate_hz=30)  # 30 Hz
```

**After:**
```python
poller = ThreadPoller(metrics, target_rate_hz=20)  # 20 Hz
```

**Impact:**
- Lower CPU usage
- Higher accuracy (less scheduler pressure)
- Lower jitter

---

### 2. Reduce Number of Metrics

**Before:**
```python
metrics = [metric1, metric2, metric3, metric4, metric5, metric6]
```

**After:**
```python
metrics = [metric1, metric2, metric3]  # Only essential
```

---

### 3. Simplify Rules

**Before:**
```yaml
rules:
  - name: "complex_rule"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "Long message with lots of formatting: {loudness:.4f} | {spectral:.4f} | {peak:.4f}"
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.5
      # ... 10 more actions
```

**After:**
```yaml
rules:
  - name: "simple_rule"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "High loudness"
```

---

### 4. Optimize Action Handler

**Before (slow):**
```python
def action_handler(action):
    if action["type"] == "log":
        # Slow logging (file I/O)
        with open("log.txt", "a") as f:
            f.write(f"{action}\n")
    elif action["type"] == "trigger_device":
        # Slow device operation
        ableton_mcp_extended.set_device_parameter(...)  # Network call
```

**After (fast):**
```python
def action_handler(action):
    if action["type"] == "log":
        # Fast in-memory buffering
        action_buffer.append(action)
    elif action["type"] == "device_action":
        # Batch device updates
        device_updates.append(action)
```

---

### 5. Use Background Threads

Offload slow operations to background threads:

```python
import threading
from queue import Queue

# Queue for background logging
log_queue = Queue()

def log_writer_thread():
    while True:
        message = log_queue.get()
        with open("log.txt", "a") as f:
            f.write(f"{message}\n")

# Start background thread
threading.Thread(target=log_writer_thread, daemon=True).start()

# Fast action handler
def action_handler(action):
    if action["type"] == "log":
        log_queue.put(action["message"])  # Non-blocking
```

---

## Common Issues

### Issue: Polling Rate Never Meets Target

**Symptom:** Consistently 5-10% below target

**Root Causes:**
1. **System load** - Other processes consuming CPU
2. **Thread priority** - Low thread priority
3. **Hardware limitations** - Slow CPU

**Solutions:**
```bash
# Check system load
top  # Linux
Task Manager  # Windows

# Increase thread priority (requires elevated privileges)
# Not recommended due to system stability risks

# Reduce polling rate
poller = ThreadPoller(metrics, target_rate_hz=10)  # Reduce from 20 Hz
```

---

### Issue: High Jitter

**Symptom:** Jitter > 10% of interval

**Root Causes:**
1. **Background processes** - Antivirus, backups, indexing
2. **Power management** - CPU frequency scaling
3. **Scheduler preemption** - Other threads interrupting

**Solutions:**
```bash
# Disable unnecessary background services
# (depends on OS)

# Set power plan to "High Performance"
# (Windows: Control Panel → Power Options)

# Use CPU affinity (Linux)
taskset -c 0,1 python my_script.py  # Pin to CPUs 0,1
```

---

### Issue: CPU Usage Spikes

**Symptom:** CPU spikes to 90%+ intermittently

**Root Causes:**
1. **Garbage collection** - Python GC pauses
2. **Rule complexity** - Complex conditions or many actions
3. **Action handler** - Blocking operations

**Solutions:**
```python
# 1. Reduce GC frequency
import gc
gc.set_threshold(1000, 10, 10)  # Less frequent GC

# 2. Profile rule evaluation
# Use benchmark_runner.py --type rules

# 3. Move blocking operations to background
# (see "Optimize Action Handler" above)
```

---

### Issue: High Latency

**Symptom:** E2E latency > 2× polling interval

**Root Causes:**
1. **Slow rule evaluation** - Complex rules
2. **Blocking action handler** - I/O operations
3. **GIL contention** - Python Global Interpreter Lock

**Solutions:**
```python
# 1. Profile rule evaluation
suite.rule_evaluation_benchmark(rule_engine, poll_iterations=100)

# 2. Simplify action handler
def action_handler(action):
    # Minimal processing
    action_queue.put(action)  # Queue for background processing

# 3. Use multiprocessing (for CPU-bound rules)
# (advanced - check documentation)
```

---

### Issue: Inconsistent Results

**Symptom:** Benchmark results vary between runs

**Root Causes:**
1. **System load** - Variable background load
2. **Thermal throttling** - CPU reduces speed when hot
3. **OS scheduling** - Non-deterministic thread scheduling

**Solutions:**
```bash
# Run benchmarks multiple times
for i in {1..5}; do
  python benchmark_runner.py --quiet
done

# Use median results, not single run

# Stabilize system before benchmarking
# - Close other applications
# - Disable power saving
# - Ensure adequate cooling
```

---

### Issue: Grade C Despite Meeting Targets

**Symptom:** Performance grade is C, but all metrics look OK

**Root Cause:** Aggregated scoring includes hidden recommendations

**Solution:**
Check full report for recommendations:
```bash
python benchmark_runner.py --output-dir results

# View markdown report
cat results/benchmark_report_20250120_142305.md

# Look for "Recommendations" section
```

---

### Issue: Benchmark Fails to Start

**Symptom:** Exception when running benchmark

**Common Errors:**

```python
# Error: Missing dependencies
# ModuleNotFoundError: No module named 'psutil'

# Solution: Install dependencies
pip install psutil PyYAML
```

```python
# Error: Unable to create mock poller
# TypeError: 'NoneType' object is not callable

# Solution: Ensure benchmark_runner.py has mock implementations
# Check if mock_poller() function exists
```

---

## Benchmark Workflow

### Recommended Benchmark Cycle

1. **Initial Benchmark (Baseline)**
   ```bash
   python benchmark_runner.py --duration 30
   ```

2. **Analyze Results**
   ```bash
   cat results/benchmark_report_*.md
   ```

3. **Identify Issues**
   - Look for recommendations section
   - Compare to performance targets

4. **Optimize**
   - Apply optimizations from guide
   - Change configuration

5. **Re-Benchmark**
   ```bash
   python benchmark_runner.py --duration 30
   ```

6. **Compare**
   ```diff
   # Before
   Actual Rate: 18.2 Hz
   CPU Usage: 65%

   # After
   Actual Rate: 19.5 Hz
   CPU Usage: 45%
   ```

7. **Document**
   - Save benchmark reports
   - Note optimization steps
   - Track improvement over time

---

## Best Practices

### 1. Benchmark Reproducibly

```bash
# Same conditions every time
# - Close other applications
# - Use same power plan
# - Run at same duration
# - Use same configuration

python benchmark_runner.py --duration 30 --iterations 1000
```

### 2. Run Multiple Times

```bash
# Run 5 times, use median
for i in {1..5}; do
  python benchmark_runner.py --quiet \
    --output-dir results/run_$i \
    --duration 30
done
```

### 3. Compare Before/After

Always benchmark before making changes:

```bash
# Before optimization
python benchmark_runner.py --output-dir before

# Make changes...

# After optimization
python benchmark_runner.py --output-dir after
```

### 4. Document Findings

```bash
# Create benchmark log
echo "$(date): Benchmark started" >> benchmark_log.txt
python benchmark_runner.py --output-dir results_$(date +%Y%m%d_%H%M%S)
echo "$(date): Benchmark complete" >> benchmark_log.txt
```

### 5. Use Results for Capacity Planning

If benchmark shows CPU usage 30% at 20 Hz:

- 20 Hz: 30% CPU
- 40 Hz: ~60% CPU (linear scaling)
- 60 Hz: ~90% CPU (near limit)

Don't exceed 80% CPU in production.

---

## See Also

- [API Reference - BenchmarkSuite](api_reference.md#module-benchmarks)
- [User Guide - Performance](user_guide.md#performance)
- [Troubleshooting Guide](troubleshooting.md)