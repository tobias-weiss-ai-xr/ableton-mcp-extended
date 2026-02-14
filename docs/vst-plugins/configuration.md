# VST Audio Analysis - Configuration Reference

## Overview

This document provides comprehensive reference for all configuration options in the VST Audio Analysis system. It covers:

- YAML configuration file structure
- Plugin section options
- Rule definition syntax
- Action type reference
- Performance tuning parameters

---

## Configuration File Structure

### Top-Level Sections

```yaml
plugin:
  # Plugin metadata (section 1)
  name: "Plugin Name"
  track: 0
  device: 0

rules:
  # Rule definitions (section 2)
  - name: "rule_name"
    priority: 10
    condition:
      parameter: "Parameter Name"
      operator: ">"
      value: 0.5
    action:
      type: "set_volume"
      volume: 0.8
```

### Section 1: Plugin Metadata

Defines which VST plugin to analyze and how to access it.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | No | `""` | Plugin name (for logging purposes) |
| `track` | `integer` | Yes | - | Track index containing plugin (0-based) |
| `device` | `integer` | Yes | - | Device index on track (0-based) |

**Example**:
```yaml
plugin:
  name: "Youlean Loudness Meter"
  track: 0
  device: 0
```

### Section 2: Rules

List of rules defining when and how to react to audio analysis.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | Yes | - | Unique rule identifier |
| `priority` | `integer` | No | `10` | Priority (lower = higher priority, evaluated first) |
| `condition` | `object` | Yes | - | Condition to evaluate |
| `action` | `object` | Yes | - | Action to execute when condition is true |
| `cooldown` | `integer` | No | `0` | Minimum milliseconds between same rule triggers |

**Example**:
```yaml
rules:
  - name: "high_loudness_warning"
    priority: 20
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -14.0
    action:
      type: "log"
      message: "WARNING: High loudness"
    cooldown: 200
```

---

## Condition Syntax

### Condition Structure

```yaml
condition:
  parameter: "Parameter Name"
  operator: ">"
  value: 0.5

  # For complex conditions:
  and:
    - condition: ...
  or:
    - condition: ...
  not:
    - condition: ...
```

### Condition Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parameter` | `string` | Yes | Name of parameter to evaluate |
| `operator` | `string` | Yes | Comparison or logical operator |
| `value` | `number/string` | Yes | Threshold or reference value |
| `conditions` | `list` | No | Sub-conditions for logical operators |
| `param1`, `param2` | `string` | No | Parameter references for comparison |

### Supported Operators

#### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `>` | Greater than | `value: 0.5` - triggers when `parameter > 0.5` |
| `<` | Less than | `value: 0.3` - triggers when `parameter < 0.3` |
| `>=` | Greater than or equal | `value: 0.5` - triggers when `parameter >= 0.5` |
| `<=` | Less than or equal | `value: 0.5` - triggers when `parameter <= 0.5` |
| `==` | Equal to | `value: 0.5` - triggers when `parameter == 0.5` |
| `!=` | Not equal to | `value: 0.5` - triggers when `parameter != 0.5` |

**Example**:
```yaml
condition:
  parameter: "LUFS Integrated"
  operator: ">"
  value: -14.0
```

#### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `and` | All sub-conditions must be true | Evaluates to true only if all conditions are true |
| `or` | Any sub-condition must be true | Evaluates to true if any condition is true |
| `not` | Negate sub-condition | Evaluates to true if condition is false |

**AND Example**:
```yaml
condition:
  and:
    - condition:
        parameter: "LUFS Integrated"
        operator: ">"
        value: -14.0
    - condition:
        parameter: "Peak Level"
        operator: "<"
        value: -0.5
  # True when: LUFS > -14 AND Peak < -0.5 dB
```

**OR Example**:
```yaml
condition:
  or:
    - condition:
        parameter: "LUFS Integrated"
        operator: ">"
        value: -14.0
    - condition:
        parameter: "LUFS Integrated"
        operator: "<"
        value: -16.0
  # True when: LUFS > -14 OR LUFS < -16
```

**NOT Example**:
```yaml
condition:
  not:
    - condition:
        parameter: "Spectral Centroid"
        operator: "<"
        value: 2000.0
  # True when: Spectral Centroid >= 2000
```

### Parameter References

Compare values between parameters instead of using fixed thresholds.

**Syntax**:
- `param1`: First parameter name
- `param2`: Second parameter name

**Example**:
```yaml
condition:
  parameter: "LUFS Integrated"
  operator: ">"
  param1: "Threshold"

rules:
  - name: "set_threshold_high"
    condition:
      parameter: "Threshold"
      operator: ">"
      value: -14.0
    action:
      type: "set_device_parameter"
      parameter: "Threshold"
      value: -14.0

  - name: "loud_above_threshold"
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      param1: "Threshold"
    action:
      type: "log"
      message: "Loudness above threshold: {LUFS Integrated}"
```

---

## Action Syntax

### Action Structure

```yaml
action:
  type: "set_volume"
  target_track: 0
  volume: 0.8
```

### Action Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `string` | Yes | Action type (see Action Types below) |
| `message` | `string` | No (log) | Log message text |
| `target_track` | `integer` | No | Target track index (default: plugin track) |
| `target_device` | `integer` | No | Target device index (default: plugin device) |
| `parameter` | `string` | No (set_device_parameter) | Parameter name to set |
| `volume/value` | `number` | No | Value for volume or parameter actions |
| `cooldown` | `integer` | No | Override rule cooldown (action-specific) |

### Action Types

#### Log Action

Writes a message to console.

**Type**: `log`

**Fields**:
- `message` (required): Message text

**Example**:
```yaml
action:
  type: "log"
  message: "WARNING: Loudness exceeds threshold: {LUFS Integrated}"
```

#### Set Track Volume Action

Changes volume of a track.

**Type**: `set_track_volume`

**Fields**:
- `target_track` (optional): Track index (default: plugin track)
- `volume` (required): Normalized volume value (0.0 = silent, 1.0 = maximum)

**Example**:
```yaml
action:
  type: "set_track_volume"
  target_track: 0
  volume: 0.85
```

#### Set Device Parameter Action

Sets a specific parameter on a device.

**Type**: `set_device_parameter`

**Fields**:
- `target_device` (optional): Device index (default: plugin device)
- `parameter` (optional): Parameter name
- `value` (required): Parameter value (normalized or plugin-specific)

**Example**:
```yaml
action:
  type: "set_device_parameter"
  target_device: 1              # Filter device on synth track
  parameter: "Filter Frequency"
  value: 0.75                # Normalized value
```

#### Set Master Volume Action

Changes master output volume.

**Type**: `set_master_volume`

**Fields**:
- `volume` (required): Normalized volume value (0.0 = silent, 1.0 = maximum)

**Example**:
```yaml
action:
  type: "set_master_volume"
  volume: 0.75
```

---

## Rule Priority and Cooldown

### Priority

Rules are evaluated in priority order (lower number = higher priority). When multiple rules could trigger, only the highest priority rule executes.

**Priority Levels**:
- `1-9`: Emergency (e.g., peak protection)
- `10-19`: Critical (e.g., clipping prevention)
- `20-29`: Important (e.g., volume control)
- `30-49`: Normal (e.g., logging, monitoring)
- `50+`: Low (e.g., informational alerts)

**Example Priority Hierarchy**:
```yaml
rules:
  # Priority 5: Emergency peak protection
  - name: "emergency_peak_reduction"
    priority: 5
    condition:
      parameter: "Peak Level"
      operator: ">"
      value: -0.5
    action:
      type: "set_master_volume"
      volume: 0.0

  # Priority 20: Normal loudness control
  - name: "loudness_high"
    priority: 20
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -12.0
    action:
      type: "set_track_volume"
      volume: 0.85
```

### Cooldown

Prevents rapid rule re-triggering which can cause oscillation.

**Cooldown Behavior**:
- Rule-level cooldown applies to rule triggers
- After trigger, rule cannot fire again for `cooldown` milliseconds
- Prevents "flashing" behavior

**Example**:
```yaml
rules:
  - name: "reduce_volume"
    priority: 10
    cooldown: 500  # Wait 500ms between triggers
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -12.0
    action:
      type: "set_track_volume"
      volume: 0.80
```

**Action-Level Cooldown**:
Override rule cooldown for specific actions.

```yaml
action:
  type: "set_track_volume"
  volume: 0.80
  cooldown: 300  # This action waits 300ms before repeating
```

---

## CLI Configuration Options

### Polling Rate

Controls how frequently parameters are queried from the plugin.

**Default**: 20 Hz (50ms intervals)

**Recommended Rates**:
| Use Case | Rate | Interval | CPU Usage |
|-----------|------|----------|------------|
| Monitoring | 10 Hz | 100ms | 1-2% |
| Light Control | 15 Hz | 67ms | 1.8% |
| Normal Control | 20 Hz | 50ms | 2.4% |
| Aggressive Control | 30 Hz | 33ms | 3.6% |

**Setting Poll Rate**:
```bash
# Command-line option
python responsive_control.py --poll-rate 15

# In Python code
from scripts.analysis.polling import ThreadPoller
poller = ThreadPoller(metrics, target_rate_hz=15)
```

### Verbose Logging

Enable detailed logging for debugging.

**CLI Option**: `--verbose`

**Output Includes**:
- Connection status
- Polling timestamps
- Rule evaluation results
- Action execution details
- Error messages with stack traces

**Example**:
```bash
python responsive_control.py --config my_rules.yml --verbose
```

---

## Performance Tuning

### Optimize Polling Rate

Start conservative, increase if system allows.

**Guidelines**:
1. Begin with 10 Hz (100ms intervals)
2. Monitor CPU usage during operation
3. Increase to 15-20 Hz if CPU < 50%
4. Reduce if CPU > 80%
5. Use benchmarks to measure actual achieved rate

### Optimize Rule Evaluation

Fewer/simpler rules = faster evaluation.

**Guidelines**:
1. Limit total rules to < 20 for optimal performance
2. Avoid deep nested AND/OR conditions
3. Use parameter references instead of complex logic
4. Group related rules by priority

**Example Optimization**:
```yaml
# Before: Multiple separate rules
rules:
  - name: "check_loudness_high"
    priority: 10
    condition: {parameter: "LUFS Integrated", operator: ">", value: -14.0}
    action: {type: "set_track_volume", volume: 0.85}
  - name: "check_loudness_medium"
    priority: 9
    condition: {parameter: "LUFS Integrated", operator: ">", value: -12.0}
    action: {type: "set_track_volume", volume: 0.88}
  - name: "check_loudness_low"
    priority: 8
    condition: {parameter: "LUFS Integrated", operator: "<", value: -16.0}
    action: {type: "set_track_volume", volume: 0.90}

# After: Single rule with hysteresis
rules:
  - name: "volume_control"
    priority: 10
    cooldown: 200
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -14.0
    action: {type: "set_track_volume", volume: 0.85}
  - name: "volume_recovery"
    priority: 9
    cooldown: 200
    condition:
      parameter: "LUFS Integrated"
      operator: "<"
      value: -16.0
    action: {type: "set_track_volume", volume: 0.90}
```

### Memory Management

The system samples parameter values for statistics.

**Per-Metric Sample Limit**: 100,000 samples by default
**Memory Per Sample**: ~24 bytes (float value + timestamp)
**Estimated Memory**: 100,000 samples × 24 bytes ≈ 2.4 MB per metric

**Memory Usage Guidelines**:
- 10 metrics × 2.4 MB ≈ 24 MB total
- Adjust sampling window if memory constrained
- See `poll_plugin_params.py` for sampling control

---

## Environment Variables

### MCP Server Host

Ableton MCP server hostname (default: localhost).

**Environment Variable**: `ABLETON_MCP_HOST`

**Usage**:
```bash
# Set custom host
export ABLETON_MCP_HOST=192.168.1.100

# Connects to custom host
python responsive_control.py --config my_rules.yml
```

### MCP Server Port

Ableton MCP server port (default: 9877).

**Environment Variable**: `ABLETON_MCP_PORT`

**Usage**:
```bash
# Set custom port
export ABLETON_MCP_PORT=9999

# Connects to custom port
python responsive_control.py --config my_rules.yml
```

---

## Complete Configuration Example

**File**: `production_lufs_control.yml`

```yaml
# VST Audio Analysis - Production LUFS Control
# Plugin: Youlean Loudness Meter 2
# Purpose: Automatic volume management based on EBU R128 standard

plugin:
  name: "Youlean Loudness Meter 2"
  track: 0
  device: 0

rules:
  # === EMERGENCY PROTECTION ===
  - name: "emergency_peak_protection"
    priority: 5
    cooldown: 100
    condition:
      parameter: "True Peak"
      operator: ">"
      value: -0.5
    action:
      type: "set_master_volume"
      volume: 0.0

  # === LOUDNESS MANAGEMENT ===
  - name: "loudness_high"
    priority: 15
    cooldown: 300
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -12.0
    action:
      type: "set_track_volume"
      volume: 0.80

  - name: "loudness_target"
    priority: 14
    cooldown: 500
    condition:
      and:
        - condition:
            parameter: "LUFS Integrated"
            operator: "<="
            value: -15.5
        - condition:
            parameter: "LUFS Integrated"
            operator: ">="
            value: -12.5
    action:
      type: "set_track_volume"
      volume: 0.88

  - name: "loudness_low"
    priority: 13
    cooldown: 300
    condition:
      parameter: "LUFS Integrated"
      operator: "<"
      value: -16.0
    action:
      type: "set_track_volume"
      volume: 0.92

  # === MONITORING ===
  - name: "loudness_status_log"
    priority: 8
    cooldown: 1000
    condition:
      parameter: "LUFS Integrated"
      operator: ">="
      value: -30.0
    action:
      type: "log"
      message: "LUFS: {LUFS Integrated} | Target: -14.0"
```

**Usage**:
```bash
python scripts/analysis/responsive_control.py \
  --config configs/analysis/production_lufs_control.yml \
  --poll-rate 20
```

---

## See Also

- [Getting Started Tutorial](tutorial.md) - 15-minute quick start guide
- [Rules API Reference](rules_api.md) - Complete rule syntax documentation
- [User Guide](user_guide.md) - Comprehensive usage guide
- [API Reference](api_reference.md) - Python API documentation
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

*Last Updated: 2026-02-10*
*Part of VST Audio Analysis Integration*
*Compatible with Ableton Live 11+*
