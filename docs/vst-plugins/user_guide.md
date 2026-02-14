# VST Audio Analysis User Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Setup](#setup)
5. [Configuration](#configuration)
6. [Quick Start](#quick-start)
7. [Examples](#examples)
8. [Performance](#performance)
9. [Best Practices](#best-practices)

---

## Overview

The VST Audio Analysis system enables real-time audio analysis and automated control in Ableton Live using parameter polling from VST plugins. It provides:

- **Real-time Parameter Polling** - Read audio analysis metrics from VST plugins at configurable rates (10-30 Hz)
- **Rule-Based Control** - Define YAML-based rules to evaluate metrics and trigger actions
- **CLI Monitoring** - Real-time text-based display of analysis values and system state
- **Performance Benchmarking** - Measure and validate system performance (polling rate, CPU, latency)

### Key Capabilities

✅ **Plugin Independence** - Works with any VST/AU plugin that exposes analysis parameters
✅ **No Max for Live Required** - Pure Python implementation using Ableton's Remote Script API
✅ **Configurable Update Rate** - Adjustable polling frequency (default 20 Hz)
✅ **Robust Error Handling** - Gracefully handles plugin failures and parameter changes
✅ **Rule-Based Automation** - Custom YAML rules for real-time decision making
✅ **Cross-Platform** - Works on macOS, Windows, and Linux

---

## Architecture

### System Components

```
┌─────────────────┐
│  Ableton Live   │
│  (MCP Server)   │
└────────┬────────┘
         │ Ableton Remote Script API
┌────────▼────────┐
│  PollingSystem  │ ← Polls VST plugin parameters (10-30 Hz)
│  - AudioMetric  │
│  - ThreadPoller │
└────────┬────────┘
         │ Metric values
┌────────▼────────┐
│  ControlLoop    │ ← Orchestrates poll → evaluate → act cycle
│  - Poll →       │
│  - Evaluate →   │
│  - Act          │
└────────┬────────┘
         │ Metrics + evaluation results
┌────────▼────────┐
│  RuleEngine     │ ← Evaluates YAML rules against metrics
│  - RuleParser   │
│  - RuleEvaluator│
└────────┬────────┘
         │ Actions triggered
┌────────▲────────┐
│  CLI Monitor    │ ← Real-time text display
│  - Terminal UI  │
└─────────────────┘
```

### Data Flow

1. **Polling**: `AudioMetric` queries Ableton for device parameter values (e.g., track 1, device 0, parameter 5)
2. **Collection**: `ThreadPoller` collects metrics at `target_rate_hz` intervals
3. **Evaluation**: `ControlLoop` feeds metrics to `RuleEngine`
4. **Decision**: `RuleEngine` evaluates rules and returns triggered actions
5. **Action**: Actions executed (MCP tool calls, logging, etc.)
6. **Display**: `CLIMonitor` shows current values, triggered actions, system state

### Core Modules

| Module | File | Purpose |
|--------|------|---------|
| `AudioMetric` | `polling.py` | Parameter query definition (track, device, index, name) |
| `ThreadPoller` | `polling.py` | Background polling thread with configurable rate |
| `RuleEngine` | `rules.py` | YAML rule parsing and evaluation |
| `ControlLoop` | `control_loop.py` | Orchestrates poll → evaluate → act cycle |
| `CLIMonitor` | `cli_monitor.py` | Real-time terminal display |
| `BenchmarkSuite` | `benchmarks.py` | Performance measurement framework |

---

## Installation

### Prerequisites

- **Ableton Live 11+** with Remote Script API enabled
- **Python 3.8+** (3.10+ recommended)
- **VST/AU Plugin** that exposes audio analysis as parameters

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 4 GB | 8 GB+ |
| CPU | Dual-core | Quad-core |
| Ableton Live | 11 | 12 |

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ableton-mcp-extended.git
   cd ableton-mcp-extended
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

   Or manually:
   ```bash
   pip install PyYAML psutil
   ```

3. **Verify installation**:
   ```bash
   python -c "import ableton_mcp_extended.audio_analysis; print('✓ Installation successful')"
   ```

4. **Install a VST plugin** (see [Plugin Installation](docs/vst-plugins/installation_guide.md))

### Verification

Run the unit tests:
```bash
cd MCP_Server/audio_analysis
python -m pytest tests/ -v
```

Expected output: `76 passed` (all tests pass)

---

## Setup

### 1. Configure VST Plugin in Ableton

1. Open Ableton Live
2. Create a new session or load an existing session
3. Add a track with audio (or virtual instrument)
4. Insert your VST plugin (e.g., MAnalyzer)
5. **Verify parameter exposure**: In Max for Live or Remote Script, check that the plugin exposes analysis parameters

### 2. Identify Parameter Indices

Use the MCP server to list device parameters:
```python
from ableton_mcp_extended.audio_analysis.polling import AudioMetric

# Example: Query device info (you'll need the Python Remote Script running)
# See parameter_mappings.md for template
```

Document the parameter indices (see `docs/vst-plugins/parameter_mappings.md`):

```yaml
# Example parameter mapping
track_index: 0  # First track
device_index: 0  # First device on track
parameters:
  - index: 5
    name: "loudness"
    range: [0.0, 1.0]
    description: "Integrated loudness in LUFS"
    interpretation: "higher = louder"

  - index: 6
    name: "spectral_centroid"
    range: [0.0, 1.0]
    description: "Spectral centroid (brightness)"
    interpretation: "higher = brighter"
```

### 3. Configure Polling System

Create a `config.yaml` file:

```yaml
# Example polling configuration
polling:
  target_rate_hz: 20  # 20 Hz (50ms intervals)
  metrics:
    - track_index: 0
      device_index: 0
      parameter_index: 5
      name: "loudness"
      min_value: 0.0
      max_value: 1.0

control_loop:
  enabled: true
  poll_rate_hz: 20
```

---

## Configuration

### Polling Configuration

`polling.py` - `AudioMetric` definition:

```python
from ableton_mcp_extended.audio_analysis.polling import AudioMetric

metric = AudioMetric(
    track_index=0,      # Track number (0-based)
    device_index=0,     # Device index on track (0-based)
    parameter_index=5,  # Parameter index (from plugin docs)
    name="loudness",    # Friendly name for display
    min_value=0.0,      # Expected minimum (for scaling/displays)
    max_value=1.0       # Expected maximum
)
```

### Rule Configuration

`rules.yaml` - Rule definition:

```yaml
# Example rules
rules:
  - name: "high_loudness_warning"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "Loudness exceeded threshold: {loudness:.2f}"
      - type: "trigger_device"
        parameter_index: 0
        value: 0.5

  - name: "low_energy"
    condition:
      metric: "spectral_centroid"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "log"
        message: "Low spectral activity detected"
```

### Control Loop Configuration

```python
from ableton_mcp_extended.audio_analysis.control_loop import ControlLoop
from ableton_mcp_extended.audio_analysis.polling import AudioMetric, ThreadPoller

# Create metric
metric = AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")

# Create poller
poller = ThreadPoller([metric], target_rate_hz=20)

# Create rule engine
from ableton_mcp_extended.audio_analysis.rules import RuleEngine
rule_engine = RuleEngine.from_file("rules.yaml")

# Create control loop
loop = ControlLoop(poller, rule_engine)

# Start
loop.start()

# ... do work ...

# Stop
loop.stop()
```

### CLI Monitor Configuration

```python
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

# Create poller
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index=0, device_index=0, parameter_index=6, name="spectral_centroid")
]
poller = ThreadPoller(metrics, target_rate_hz=20)

# Create monitor
monitor = CLIMonitor(poller, update_interval_sec=0.2)

# Start monitoring
monitor.start()

# ... (monitor runs in background) ...

# Stop monitoring
monitor.stop()
```

---

## Quick Start

### Step 1: Monitor Parameters

```python
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

# Define metrics
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index=0, device_index=0, parameter_index=6, name="spectral_centroid")
]

# Create poller (20 Hz = 50ms intervals)
poller = ThreadPoller(metrics, target_rate_hz=20)

# Start CLI monitor
monitor = CLIMonitor(poller, update_interval_sec=0.2)
monitor.start()

# Press Ctrl+C to stop
monitor.wait_for_interrupt()
monitor.stop()
```

### Step 2: Add Rules

Create `my_rules.yaml`:
```yaml
rules:
  - name: "loud_loudness"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "WARNING: High loudness: {loudness:.2f}"
```

### Step 3: Run Control Loop

```python
from ableton_mcp_extended.audio_analysis.control_loop import ControlLoop
from ableton_mcp_extended.audio_analysis.rules import RuleEngine
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

# Setup
metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=20)
rule_engine = RuleEngine.from_file("my_rules.yaml")

# Create control loop
loop = ControlLoop(poller, rule_engine)

# Define action handler
def action_handler(action):
    if action["type"] == "log":
        print(action["message"])

# Start loop
loop.start(action_handler)

# Run for 10 seconds
import time
time.sleep(10)

# Stop
loop.stop()
```

---

## Examples

### Example 1: Simple Loudness Monitoring

```python
from ableton_mcp_extended.audio_analysis.polling import AudioMetric, ThreadPoller
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor

# Define single metric
loudness_metric = AudioMetric(
    track_index=0,
    device_index=0,
    parameter_index=5,
    name="loudness",
    min_value=0.0,
    max_value=1.0
)

# Create poller
poller = ThreadPoller([loudness_metric], target_rate_hz=20)

# Monitor
monitor = CLIMonitor(poller, update_interval_sec=0.2)
monitor.start()

# ... (monitor displays real-time values) ...

monitor.stop()
```

### Example 2: Multi-Metric Analysis

```python
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index Ableton=0, device_index=0, parameter_index=6, name="spectral_centroid"),
    AudioMetric(track_index=0, device_index=0, parameter_index=7, name="peak")
]

poller = ThreadPoller(metrics, target_rate_hz=30)
monitor = CLIMonitor(poller, update_interval_sec=0.1)
monitor.start()

monitor.stop()
```

### Example 3: Complex Rules

```python
from ableton_mcp_extended.audio_analysis.rules import Rule, Condition, Action

# Create rule programmatically
condition = Condition(metric="loudness", operator=">", threshold=0.8)
action = Action(type="log", message="ALERT: Loudness high!")
rule = Rule(name="high_loudness", condition=condition, actions=[action])

# Add to engine
engine = RuleEngine([rule])
```

### Example 4: Custom Action Handler

```python
import ableton_mcp_extended  # Assuming MCP server integration

def custom_action_handler(action):
    if action["type"] == "trigger_device":
        # Call MCP tool to set device parameter
        ableton_mcp_extended.set_device_parameter(
            track_index=0,
            device_index=1,
            parameter_index=action["parameter_index"],
            value=action["value"]
        )
    elif action["type"] == "log":
        print(f"[RULE] {action['message']}")

loop.start(custom_action_handler)
```

---

## Performance

### Polling Rate

The system can sustain polling rates of 10-30 Hz depending on:

- **Number of metrics** (each additional metric adds overhead)
- **Complexity of rules** (more rules = slower evaluation)
- **System CPU** (more cores = better parallelization)

### Benchmarks

Run the benchmark suite to measure your system's performance:

```bash
cd MCP_Server/audio_analysis
python benchmark_runner.py --duration 10 --output-dir results
```

This generates:
- `benchmark_report.json` - Full results
- `benchmark_report.md` - Human-readable report
- `benchmark_report.txt` - Console-friendly summary

See `docs/vst-plugins/benchmark_interpretation.md` for interpreting results.

### Performance Targets

| Metric | Target (20 Hz) | Target (30 Hz) |
|--------|---------------|---------------|
| Polling Rate | ≥ 19.0 Hz | ≥ 28.5 Hz |
| Polling Jitter | < 5% of interval | < 5% of interval |
| CPU Usage (Mean) | < 50% | < 50% |
| E2E Latency (P99) | < 100ms | < 67ms |
| Rule Evaluation (Mean) | < 5ms | < 3.3ms |

---

## Best Practices

### 1. Start with Conservative Polling Rate

Begin with 10 Hz (100ms intervals), increase to 20 Hz if needed:

```python
# Start conservative
poller = ThreadPoller(metrics, target_rate_hz=10)

# After testing, increase if performance allows
poller = ThreadPoller(metrics, target_rate_hz=20)
```

### 2. Limit Number of Rules

Each rule adds evaluation overhead. Keep rules simple:

✅ Good:
```yaml
- name: "high_loudness"
  condition: {metric: "loudness", operator: ">", threshold: 0.8}
  actions: [{type: "log", message: "High громкость"}]
```

❌ Avoid complex nested conditions if possible.

### 3. Use Metric Names for Readability

Friends names help debugging and rule authoring:

```python
# ✓ Good
metric = AudioMetric(..., name="loudness")

# ✗ Avoid
metric = AudioMetric(..., name="metric1")
```

### 4. Test Rules Individually

Test rule logic before running in production:

```python
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

engine = RuleEngine.from_file("rules.yaml")

# Test with sample metrics
metrics = {"loudness": 0.9}
actions = engine.evaluate(metrics)
print(actions)  # Should return triggered actions
```

### 5. Monitor CPU Usage

If CPU exceeds 80%, reduce polling rate or simplify rules:

```python
# Use benchmarks to identify bottlenecks
python -m audio_analysis.benchmark_runner --type cpu --duration 5
```

### 6. Graceful Shutdown

Always stop pollers and loops before exiting:

```python
try:
    monitor.start()
    # ... do work ...

except KeyboardInterrupt:
    monitor.stop()  # Clean shutdown
```

---

## Next Steps

- [API Reference](api_reference.md) - Detailed API documentation
- [Rule Configuration Guide](rule_configuration.md) - Advanced rule examples
- [CLI Monitor Guide](cli_monitor.md) - Monitoring features and options
- [Benchmark Guide](benchmark_guide.md) - Running and interpreting benchmarks
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

## Support

For issues or questions:
1. Check [Troubleshooting](troubleshooting.md)
2. Review unit tests for usage examples: `MCP_Server/audio_analysis/tests/`
3. Examine example files: `example_*.py` and `example_*.yaml`

---

## License

See repository LICENSE file.