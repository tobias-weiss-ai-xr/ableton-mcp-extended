# VST Audio Analysis API Reference

## Table of Contents

1. [Module: `polling`](#module-polling)
2. [Module: `rules`](#module-rules)
3. [Module: `control_loop`](#module-control_loop)
4. [Module: `cli_monitor`](#module-cli_monitor)
5. [Module: `benchmarks`](#module-benchmarks)
6. [Module: `benchmark_report`](#module-benchmark_report)

---

## Module: `polling`

**File**: `MCP_Server/audio_analysis/polling.py`

### Classes

#### `AudioMetric`

Dataclass defining a single audio metric to poll.

**Attributes:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `track_index` | `int` | Yes | Track index (0-based) in Ableton session |
| `device_index` | `int` | Yes | Device index (0-based) on the track |
| `parameter_index` | `int` | Yes | Parameter index (0-based) on the device |
| `name` | `str` | Yes | Human-readable name for display |
| `min_value` | `float` | No | Expected minimum value (default: 0.0) |
| `max_value` | `float` | No | Expected maximum value (default: 1.0) |

**Methods:**

```python
@dataclass
class AudioMetric:
    """Represents a single audio metric to poll from a VST plugin."""

    track_index: int
    device_index: int
    parameter_index: int
    name: str
    min_value: float = 0.0
    max_value: float = 1.0
```

**Example:**

```python
from ableton_mcp_extended.audio_analysis.polling import AudioMetric

metric = AudioMetric(
    track_index=0,
    device_index=0,
    parameter_index=5,
    name="loudness",
    min_value=0.0,
    max_value=1.0
)
```

---

#### `ThreadPoller`

Background thread that polls multiple `AudioMetric` objects at a target rate.

**Constructor:**

```python
ThreadPoller(metrics: List[AudioMetric], target_rate_hz: float = 20.0)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metrics` | `List[AudioMetric]` | - | List of metrics to poll |
| `target_rate_hz` | `float` | `20.0` | Target polling rate in Hz |

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `start()` | `None` | Start the polling thread |
| `stop()` | `None` | Stop the polling thread (graceful shutdown) |
| `get_values()` | `Dict[str, float]` | Get current values for all metrics |
| `get_value(metric_name: str)` | `Optional[float]` | Get value for specific metric |
| `get_timestamps()` | `Dict[str, float]` | Get last update timestamps |
| `get_timestamp(metric_name: str)` | `Optional[float]` | Get timestamp for specific metric |
| `get_all_metrics()` | `List[AudioMetric]` | Get list of all metrics being polled |
| `get_sample_count(metric_name: str)` | `int` | Get number of samples collected for metric |
| `get_average_value(metric_name: str)` | `Optional[float]` | Get average value for metric |
| `clear_samples(metric_name: str)` | `None` | Clear collected samples for metric |
| `is_running()` | `bool` | Check if poller is currently running |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `target_rate_hz` | `float` | Target polling rate (read-only after construction) |
| `interval_seconds` | `float` | Target interval in seconds (1 / target_rate_hz) |

**Example:**

```python
from ableton_mcp_extended.audio_analysis.polling import AudioMetric, ThreadPoller

metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index=0, device_index=0, parameter_index=6, name="spectral_centroid")
]

poller = ThreadPoller(metrics, target_rate_hz=20.0)
poller.start()

# Get current values
values = poller.get_values()
print(f"Loudness: {values['loudness']}")

# Get specific metric value
loudness = poller.get_value("loudness")

# Stop poller
poller.stop()
```

---

## Module: `rules`

**File**: `MCP_Server/audio_analysis/rules.py`

### Classes

#### `Condition`

Represents a rule condition to evaluate.

**Attributes:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `metric` | `str` | Yes | Name of metric to evaluate |
| `operator` | `str` | Yes | Comparison operator: `>`, `<`, `>=`, `<=`, `==`, `!=` |
| `threshold` | `float` | Yes | Threshold value for comparison |

**Methods:**

```python
@dataclass
class Condition:
    metric: str
    operator: str
    threshold: float

    def evaluate(self, values: Dict[str, float]) -> bool:
        """Evaluate condition against metric values."""
```

**Example:**

```python
condition = Condition(
    metric="loudness",
    operator=">",
    threshold=0.8
)

result = condition.evaluate({"loudness": 0.9})  # Returns True
```

---

#### `Action`

Represents an action to execute when a rule triggers.

**Attributes:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `type` | `str` | Yes | Action type: `"log"`, `"trigger_device"`, etc. |
| `message` | `str` | No | Message for log actions |
| `parameter_index` | `int` | No | Parameter index for device actions |
| `value` | `float` | No | Value for device actions |

**Methods:**

```python
@dataclass
class Action:
    type: str
    message: Optional[str] = None
    parameter_index: Optional[int] = None
    value: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
```

**Example:**

```python
action = Action(
    type="log",
    message="High loudness detected!"
)

action_dict = action.to_dict()
# {"type": "log", "message": "High loudness detected!"}
```

---

#### `Rule`

Represents a complete rule with condition and actions.

**Attributes:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | `str` | Yes | Unique name for the rule |
| `condition` | `Condition` | Yes | Condition to evaluate |
| `actions` | `List[Action]` | Yes | Actions to execute when condition is True |

**Methods:**

```python
@dataclass
class Rule:
    name: str
    condition: Condition
    actions: List[Action]

    def evaluate(self, values: Dict[str, float]) -> List[Dict[str, Any]]:
        """Evaluate rule and return triggered actions."""
```

**Example:**

```python
from ableton_mcp_extended.audio_analysis.rules import Rule, Condition, Action

condition = Condition(metric="loudness", operator=">", threshold=0.8)
actions = [
    Action(type="log", message="High loudness: {loudness:.2f}"),
    Action(type="trigger_device", parameter_index=0, value=0.5)
]

rule = Rule(name="high_loudness", condition=condition, actions=actions)

# Evaluate
triggered = rule.evaluate({"loudness": 0.9})
```

---

#### `RuleEngine`

Engine that parses and evaluates rules.

**Constructor:**

```python
RuleEngine(rules: Optional[List[Rule]] = None)
```

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `add_rule(rule: Rule)` | `None` | Add a rule to the engine |
| `evaluate(values: Dict[str, float])` | `List[Dict[str, Any]]` | Evaluate all rules and return triggered actions |
| `get_rule_names()` | `List[str]` | Get names of all rules in engine |
| `get_rule(name: str)` | `Optional[Rule]` | Get rule by name |
| `clear_rules()` | `None` | Remove all rules |
| `to_dict()` | `Dict[str, Any]` | Export engine configuration to dictionary |
| `save_yaml(path: str)` | `None` | Save engine configuration to YAML file |

**Class Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `from_dict(data: Dict[str, Any])` | `RuleEngine` | Create engine from dictionary |
| `from_file(path: str)` | `RuleEngine` | Load engine from YAML file |

**Example:**

```python
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

# Load from YAML file
engine = RuleEngine.from_file("rules.yaml")

# Evaluate with metric values
values = {"loudness": 0.9, "spectral_centroid": 0.5}
actions = engine.evaluate(values)

for action in actions:
    print(action)

# Save to file
engine.save_yaml("rules_backup.yaml")
```

---

## Module: `control_loop`

**File**: `MCP_Server/audio_analysis/control_loop.py`

### Classes

#### `ControlLoop`

Orchestrates the poll → evaluate → act cycle.

**Constructor:**

```python
ControlLoop(
    poller: ThreadPoller,
    rule_engine: RuleEngine,
    poll_rate_hz: float = 20.0
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `poller` | `ThreadPoller` | - | Poller to get metric values |
| `rule_engine` | `RuleEngine` | - | Rule engine for evaluation |
| `poll_rate_hz` | `float` | `20.0` | Control loop polling rate |

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `start(action_handler: Callable[[Dict[str, Any]], None])` | `None` | Start control loop with action handler |
| `stop()` | `None` | Stop control loop (graceful shutdown) |
| `is_running()` | `bool` | Check if loop is running |
| `get_stats()` | `Dict[str, Any]` | Get loop statistics (iterations, errors, latency) |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `poll_rate_hz` | `float` | Current polling rate |
| `iteration_count` | `int` | Total iterations executed |
| `error_count` | `int` | Total errors encountered |

**Action Handler Signature:**

```python
def action_handler(action: Dict[str, Any]) -> None:
    """
    Called when a rule triggers.

    Args:
        action: Action dictionary with 'type', 'message', etc.
    """
    pass
```

**Example:**

```python
from ableton_mcp_extended.audio_analysis.control_loop import ControlLoop
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

# Setup
metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=20)
rule_engine = RuleEngine.from_file("rules.yaml")

# Create loop
loop = ControlLoop(poller, rule_engine, poll_rate_hz=20)

# Define action handler
def handle_action(action):
    if action["type"] == "log":
        print(action["message"])
    elif action["type"] == "trigger_device":
        # Call MCP tool
        ableton_mcp_extended.set_device_parameter(
            track_index=0,
            device_index=1,
            parameter_index=action["parameter_index"],
            value=action["value"]
        )

# Start
loop.start(handle_action)

# Run
import time
time.sleep(10)

# Stop
loop.stop()

# Get stats
stats = loop.get_stats()
print(f"Iterations: {stats['iteration_count']}")
print(f"Errors: {stats['error_count']}")
```

---

## Module: `cli_monitor`

**File**: `MCP_Server/audio_analysis/cli_monitor.py`

### Classes

#### `CLIMonitor`

Real-time terminal UI for monitoring audio metrics and system state.

**Constructor:**

```python
CLIMonitor(
    poller: ThreadPoller,
    update_interval_sec: float = 0.2,
    show_timestamps: bool = True,
    show_statistics: bool = True
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `poller` | `ThreadPoller` | - | Poller to monitor |
| `update_interval_sec` | `float` | `0.2` | Display update interval (seconds) |
| `show_timestamps` | `bool` | `True` | Show last update timestamps |
| `show_statistics` | `bool` | `True` | Show statistics (min, max, avg) |

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `start()` | `None` | Start monitoring in background thread |
| `stop()` | `None` | Stop monitoring |
| `wait_for_interrupt()` | `None` | Block until Ctrl+C is pressed |
| `is_running()` | `bool` | Check if monitor is running |
| `add_event(message: str)` | `None` | Add an event message to display |
| `clear_events()` | `None` | Clear all event messages |

**Example:**

```python
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

# Setup
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index=0, device_index=0, parameter_index=6, name="spectral_centroid")
]
poller = ThreadPoller(metrics, target_rate_hz=20)

# Create monitor
monitor = CLIMonitor(poller, update_interval_sec=0.2)

# Start
monitor.start()

# Add events
monitor.add_event("Monitoring started")

# Wait for interrupt
monitor.wait_for_interrupt()  # Blocks until Ctrl+C

# Stop
monitor.stop()
```

**Display Format:**

```
╔────────────────────────────────────────────────────╗
║  VST Audio Analysis Monitor                        ║
╠────────────────────────────────────────────────────╣
║  Metrics:                                          ║
║  • loudness        0.85  [0.00 - 1.00]            ║
║  • spectral_cntrd  0.62  [0.00 - 1.00]            ║
╠────────────────────────────────────────────────────╣
║  Statistics:                                       ║
║  • loudness        min:0.42  max:0.89  avg:0.68   ║
║  • spectral_cntrd  min:0.31  max:0.75  avg:0.54   ║
╠────────────────────────────────────────────────────╣
║  System:                                           ║
║  • Polling Rate   20.0 Hz                         ║
║  • Threads        3 active                        ║
╠────────────────────────────────────────────────────╣
║  Events:                                           ║
║  [14:23:45] Monitoring started                    ║
║  [14:23:50] High loudness detected                ║
╠────────────────────────────────────────────────────╣
║  Press Ctrl+C to stop                              ║
╚────────────────────────────────────────────────────╘
```

---

## Module: `benchmarks`

**File**: `MCP_Server/audio_analysis/benchmarks.py`

### Classes

#### `BenchmarkResult`

Represents results from a single benchmark run.

**Attributes:**

| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | Benchmark name |
| `duration_seconds` | `float` | Duration in seconds |
| `samples` | `int` | Number of samples collected |
| `min_value` | `float` | Minimum value |
| `max_value` | `float` | Maximum value |
| `mean_value` | `float` | Mean (average) value |
| `median_value` | `float` | Median value |
| `std_dev` | `float` | Standard deviation |
| `p1, p5, p25, p75, p95, p99` | `float` | Percentiles |
| `values` | `List[float]` | Raw sample values |
| `metadata` | `Dict[str, Any]` | Additional metadata |

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `to_dict()` | `Dict[str, Any]` | Convert to dictionary |
| `from_values(name, values, **metadata)` | `BenchmarkResult` | Create result from values |

---

#### `BenchmarkSuite`

Framework for running multiple benchmarks.

**Constructor:**

```python
BenchmarkSuite()
```

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `run_benchmark(name, func, duration_seconds, target_samples)` | `BenchmarkResult` | Run generic benchmark |
| `polling_rate_benchmark(poller, target_rate_hz, duration_seconds)` | `BenchmarkResult` | Measure polling accuracy |
| `cpu_usage_benchmark(controller, duration_seconds)` | `BenchmarkResult` | Measure CPU consumption |
| `end_to_end_latency_benchmark(controller, poll_iterations)` | `BenchmarkResult` | Measure poll→evaluate→act latency |
| `rule_evaluation_benchmark(rule_engine, poll_iterations)` | `BenchmarkResult` | Measure rule engine performance |
| `add_result(result)` | `None` | Add a benchmark result |
| `get_results()` | `List[BenchmarkResult]` | Get all results |
| `clear_results()` | `None` | Clear all results |
| `print_summary()` | `None` | Print summary to console |

**Example:**

```python
from ableton_mcp_extended.audio_analysis.benchmarks import BenchmarkSuite

suite = BenchmarkSuite()

# Run polling benchmark
polling_result = suite.polling_rate_benchmark(
    poller=my_poller,
    target_rate_hz=20,
    duration_seconds=5.0
)
suite.add_result(polling_result)

# Run rule evaluation benchmark
rule_result = suite.rule_evaluation_benchmark(
    rule_engine=my_rule_engine,
    poll_iterations=100
)
suite.add_result(rule_result)

# Print summary
suite.print_summary()
```

---

## Module: `benchmark_report`

**File**: `MCP_Server/audio_analysis/benchmark_report.py`

### Classes

#### `BenchmarkReport`

Complete report with system info and results.

**Attributes:**

| Name | Type | Description |
|------|------|-------------|
| `timestamp` | `str` | ISO format timestamp |
| `system_info` | `Dict[str, str]` | System information |
| `test_duration_seconds` | `float` | Total test duration |
| `results` | `List[BenchmarkResult]` | Benchmark results |
| `total_benchmarks` | `int` | Total benchmarks run |
| `passed_benchmarks` | `int` | Benchmarks passing targets |
| `performance_grade` | `str` | Grade: A/B/C |
| `recommendations` | `List[str]` | Performance recommendations |

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `to_dict()` | `Dict[str, Any]` | Convert to dictionary |
| `to_json(indent=2)` | `str` | Convert to JSON string |
| `save_json(path)` | `None` | Save to JSON file |
| `to_markdown()` | `str` | Convert to Markdown |
| `save_markdown(path)` | `None` | Save Markdown to file |
| `to_text()` | `str` | Convert to plain text |

---

#### `ReportGenerator`

Generator for creating benchmark reports.

**Constructor:**

```python
ReportGenerator()
```

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `collect_system_info()` | `None` | Gather system information |
| `generate_from_suite(suite, duration_seconds)` | `BenchmarkReport` | Generate report from suite |

**Functions:**

| Function | Return Type | Description |
|----------|-------------|-------------|
| `generate_report(suite, duration_seconds, output_json, output_markdown, output_text)` | `BenchmarkReport` | Convenience function |

**Example:**

```python
from ableton_mcp_extended.audio_analysis.benchmark_report import generate_report

# Generate report
report = generate_report(
    suite=my_suite,
    duration_seconds=10.0,
    output_json="results/report.json",
    output_markdown="results/report.md",
    output_text="results/report.txt"
)

# Print grade
print(f"Performance Grade: {report.performance_grade}")

# Print recommendations
for rec in report.recommendations:
    print(f"  - {rec}")
```

---

## CLI Tool: `benchmark_runner`

**File**: `MCP_Server/audio_analysis/benchmark_runner.py`

### Usage

```bash
python benchmark_runner.py [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--duration SECONDS` | `5.0` | Benchmark duration |
| `--iterations N` | `100` | Number of iterations |
| `--type TYPE` | `all` | Benchmark type: `all`, `polling`, `rules`, `latency`, `cpu` |
| `--output-dir DIR` | `results` | Output directory |
| `--formats FORMAT` | `json,markdown,text` | Output formats (comma-separated) |
| `--quiet` | `False` | Suppress console output |

**Examples:**

```bash
# Run all benchmarks
python benchmark_runner.py --duration 10

# Run only polling benchmarks
python benchmark_runner.py --type polling --duration 5

# Run with custom output
python benchmark_runner.py --output-dir my_results --formats json,markdown

# Quiet mode (no console output)
python benchmark_runner.py --quiet --duration 10 --iterations 500
```

---

## Type Signatures

### Common Types

```python
from typing import Dict, List, Optional, Callable, Any

MetricValues = Dict[str, float]
ActionDict = Dict[str, Any]
ActionHandler = Callable[[ActionDict], None]
```

---

## Error Handling

All modules use Python's standard exception handling. Common exceptions:

| Exception | Raised When |
|-----------|--------------|
| `ValueError` | Invalid parameter (e.g., negative rate, unknown operator) |
| `KeyError` | Metric name not found |
| `RuntimeError` | Poller/loop already running or not running |
| `FileNotFoundError` | YAML file not found |
| `yaml.YAMLError` | Invalid YAML syntax |

---

## Thread Safety

- `ThreadPoller`: Thread-safe (uses threading.Lock internally)
- `RuleEngine`: Thread-safe (read-only after construction)
- `ControlLoop`: Not thread-safe (single-threaded execution)
- `CLIMonitor`: Thread-safe (uses threading.Lock internally)

---

## Performance Notes

### Polling Rate Limits

| Rate | Minimum CPU | Recommended RAM |
|------|-------------|-----------------|
| 10 Hz | 1-2% | 100 MB |
| 20 Hz | 2-4% | 150 MB |
| 30 Hz | 3-6% | 200 MB |

### Memory Usage

- Each metric stores max `100,000` samples by default
- Average memory per sample: ~24 bytes (float + timestamp)
- 100,000 samples ≈ 2.4 MB per metric

---

## See Also

- [User Guide](user_guide.md)
- [Rule Configuration Guide](rule_configuration.md)
- [Benchmark Interpretation Guide](benchmark_interpretation.md)