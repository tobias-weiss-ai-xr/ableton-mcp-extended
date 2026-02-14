# VST Audio Analysis - Rules API Reference

## Table of Contents

1. [Overview](#overview)
2. [Rule Structure](#rule-structure)
3. [Condition Reference](#condition-reference)
4. [Action Reference](#action-reference)
5. [Complete Rule Examples](#complete-rule-examples)
6. [Advanced Patterns](#advanced-patterns)
7. [Error Handling](#error-handling)

---

## Overview

This document provides comprehensive API reference for the VST Audio Analysis rule system. It describes all available condition operators, action types, and how to construct complex rule configurations.

### Key Concepts

- **Rules**: Define when to react and what to do
- **Conditions**: Logical tests on audio analysis metrics
- **Actions**: Commands executed when conditions are true
- **Priority**: Higher priority rules evaluated first
- **Cooldown**: Minimum time between rule triggers

---

## Rule Structure

### YAML Format

```yaml
plugin:
  name: "Plugin Name"
  track: 0
  device: 0

rules:
  - name: "rule_name"
    priority: 10
    cooldown: 200
    condition:
      # Condition definition
    action:
      # Action definition
```

### Rule Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | Yes | - | Unique rule identifier |
| `priority` | `integer` | No | `10` | Lower = higher priority (evaluated first) |
| `cooldown` | `integer` | No | `0` | Milliseconds between same rule triggers |
| `condition` | `object` | Yes | - | Condition to evaluate |
| `action` | `object` | Yes | - | Action(s) to execute when condition true |

### Plugin Section Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Plugin name (for logging) |
| `track` | `integer` | Yes | Track index containing plugin |
| `device` | `integer` | Yes | Device index on track |

---

## Condition Reference

### Condition Structure

```yaml
condition:
  parameter: "Parameter Name"
  operator: ">"
  value: 0.5

  # For complex conditions:
  and:
    - condition: ...
    - condition: ...
  or:
    - condition: ...
    - condition: ...
  not:
    - condition: ...
```

### Condition Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parameter` | `string` | Yes | Metric parameter name to evaluate |
| `operator` | `string` | Yes | Comparison or logical operator |
| `value` | `number/string` | Yes | Threshold or reference value |
| `conditions` | `array` | No | Sub-conditions (AND/OR/NOT) |
| `param1`, `param2` | `string` | No | Parameter references (for comparisons) |

---

## Condition Operators

### Comparison Operators

| Operator | Description | Example | Value Type |
|----------|-------------|---------|------------|
| `>` | Greater than | `value: 0.8` - triggers when `parameter > 0.8` | `number` |
| `<` | Less than | `value: 0.2` - triggers when `parameter < 0.2` | `number` |
| `>=` | Greater than or equal | `value: 0.5` - triggers when `parameter >= 0.5` | `number` |
| `<=` | Less than or equal | `value: 0.7` - triggers when `parameter <= 0.7` | `number` |
| `==` | Equal to | `value: 0.6` - triggers when `parameter == 0.6` | `number`/`string` |
| `!=` | Not equal to | `value: 0.4` - triggers when `parameter != 0.4` | `number`/`string` |

**Example: LUFS Threshold**

```yaml
condition:
  parameter: "LUFS Integrated"
  operator: ">"
  value: -14.0
```

### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `and` | All conditions must be true | Evaluates to true only when all sub-conditions are true |
| `or` | Any condition must be true | Evaluates to true when any sub-condition is true |
| `not` | Negate condition | Evaluates to true when sub-condition is false |

**AND Example: Multi-Parameter Check**

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
  # True when: LUFS > -14 AND Peak < -0.5
```

**OR Example: Range Check**

```yaml
condition:
  or:
    - condition:
        parameter: "LUFS Integrated"
        operator: ">"
        value: -16.0
    - condition:
        parameter: "LUFS Integrated"
        operator: "<"
        value: -13.0
  # True when: LUFS > -16 OR LUFS < -13
```

**NOT Example: Exclusion**

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

Compare values between two parameters instead of using fixed thresholds.

**Syntax**:
- `param1`: First parameter name
- `param2`: Second parameter name

**Example: Dynamic Range**

```yaml
condition:
  parameter: "Dynamic Range"
  operator: "<"
  param1: "LUFS Integrated"
  param2: "LUFS Integrated"
  # True when: DR < (LUFS Integrated × 0.5)
```

---

## Action Reference

### Action Structure

```yaml
action:
  type: "action_type"
  # Additional fields based on type
```

### Action Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `string` | Yes | Action type (see below) |
| `message` | `string` | No (log) | Log message text |
| `target_track` | `integer` | No | Track index (set_track_volume) |
| `target_device` | `integer` | No | Device index (set_device_parameter) |
| `parameter` | `string` | No (set_device_parameter) | Parameter name |
| `volume/value` | `number` | No | Normalized value (0.0-1.0) |
| `cooldown` | `integer` | No | Override rule cooldown (ms) |

---

## Action Types

### Log Action

Write a message to console/log file.

**Type**: `log`

**Fields**:
- `message` (required): Message text with optional formatting

**Example: Simple Message**

```yaml
action:
  type: "log"
  message: "Loudness exceeds threshold"
```

**Example: Formatted Message**

```yaml
action:
  type: "log"
  message: "Loudness: {LUFS Integrated:.2f} exceeds threshold: -14.0"
  # Substitutes {LUFS Integrated} with actual value
```

---

### Set Track Volume Action

Change volume of a track.

**Type**: `set_track_volume`

**Fields**:
- `target_track` (optional): Track index (default: plugin track)
- `volume` (required): Normalized value (0.0 = silent, 1.0 = maximum)

**Example: Reduce Volume**

```yaml
action:
  type: "set_track_volume"
  target_track: 0
  volume: 0.75
```

**Example: Increase Volume**

```yaml
action:
  type: "set_track_volume"
  target_track: 1
  volume: 0.90
```

---

### Set Master Volume Action

Change master output volume.

**Type**: `set_master_volume`

**Fields**:
- `volume` (required): Normalized value (0.0 = silent, 1.0 = maximum)

**Example: Emergency Volume Reduction**

```yaml
action:
  type: "set_master_volume"
  volume: 0.5
```

---

### Set Device Parameter Action

Set a specific parameter on a device.

**Type**: `set_device_parameter`

**Fields**:
- `target_device` (optional): Device index (default: plugin device)
- `parameter` (required): Parameter name
- `volume/value` (required): Parameter value (normalized or plugin-specific)

**Example: Filter Frequency**

```yaml
action:
  type: "set_device_parameter"
  target_device: 1  # Filter device on track 1
  parameter: "Filter Frequency"
  volume: 0.75  # 75% open
```

**Example: Compressor Threshold**

```yaml
action:
  type: "set_device_parameter"
  parameter: "Compressor Threshold"
  volume: 0.6  # Compressor threshold (plugin-specific scale)
```

**Example: Resonance**

```yaml
action:
  type: "set_device_parameter"
  parameter: "Resonance"
  volume: 0.8  # High resonance
```

---

## Complete Rule Examples

### Example 1: LUFS Monitoring

Monitor loudness levels with log actions only.

```yaml
plugin:
  name: "Youlean Loudness Meter"
  track: 0
  device: 0

rules:
  - name: "loudness_normal"
    priority: 10
    condition:
      parameter: "LUFS Integrated"
      operator: ">="
      value: -14.0
    action:
      type: "log"
      message: "✓ LUFS normal: {LUFS Integrated:.2f}"

  - name: "loudness_high"
    priority: 15
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -12.0
    action:
      type: "log"
      message: "⚠️  High LUFS: {LUFS Integrated:.2f}"

  - name: "loudness_low"
    priority: 12
    condition:
      parameter: "LUFS Integrated"
      operator: "<"
      value: -16.0
    action:
      type: "log"
      message: "⚠️  Low LUFS: {LUFS Integrated:.2f}"
```

---

### Example 2: Automatic Volume Control

Adjust track volume based on LUFS measurements.

```yaml
plugin:
  name: "Youlean Loudness Meter"
  track: 0
  device: 0

rules:
  - name: "reduce_volume_loud"
    priority: 20
    cooldown: 500
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -12.0
    action:
      type: "set_track_volume"
      volume: 0.80
      cooldown: 200  # Slower updates when reducing

  - name: "increase_volume_quiet"
    priority: 18
    cooldown: 500
    condition:
      parameter: "LUFS Integrated"
      operator: "<"
      value: -16.0
    action:
      type: "set_track_volume"
      volume: 0.88
      cooldown: 300
```

---

### Example 3: Spectral Filter Control

Control filter frequency based on spectral centroid (brightness).

```yaml
plugin:
  name: "Voxengo SPAN"
  track: 0
  device: 0

rules:
  - name: "bright_sound_open_filter"
    priority: 15
    cooldown: 400
    condition:
      parameter: "Spectral Centroid"
      operator: ">"
      value: 4000.0  # Hz
    action:
      type: "set_device_parameter"
      target_device: 1  # Synth pad track
      parameter: "Filter Frequency"
      volume: 0.90  # Open filter

  - name: "dark_sound_close_filter"
    priority: 15
    cooldown: 400
    condition:
      parameter: "Spectral Centroid"
      operator: "<"
      value: 2000.0  # Hz
    action:
      type: "set_device_parameter"
      target_device: 1
      parameter: "Filter Frequency"
      volume: 0.40  # Closed filter
```

---

### Example 4: Peak Protection

Emergency response to prevent clipping.

```yaml
plugin:
  name: "Sound Analyzer"
  track: 0
  device: 0

rules:
  - name: "emergency_peak_reduction"
    priority: 5
    cooldown: 100
    condition:
      parameter: "Peak Level"
      operator: ">"
      value: 0.98
    action:
      type: "set_master_volume"
      volume: 0.0  # Emergency volume cut

  - name: "peak_warning"
    priority: 10
    cooldown: 300
    condition:
      parameter: "Peak Level"
      operator: ">"
      value: 0.95
    action:
      type: "log"
      message: "🚨 PEAK WARNING: {Peak Level:.4f}"
```

---

### Example 5: Multi-Parameter Condition

Check multiple conditions before triggering.

```yaml
plugin:
  name: "Multi-Analyzer"
  track: 0
  device: 0

rules:
  - name: "loud_and_bright"
    priority: 18
    cooldown: 500
    condition:
      and:
        - condition:
            parameter: "LUFS Integrated"
            operator: ">"
            value: -14.0
        - condition:
            parameter: "Spectral Centroid"
            operator: ">"
            value: 3000.0
    action:
      type: "set_device_parameter"
      target_device: 2
      parameter: "Filter Frequency"
      volume: 0.85  # Aggressive filtering

  - name: "loud_or_bright"
    priority: 17
    cooldown: 500
    condition:
      or:
        - condition:
            parameter: "LUFS Integrated"
            operator: ">"
            value: -14.0
        - condition:
            parameter: "Spectral Centroid"
            operator: ">"
            value: 3000.0
    action:
      type: "set_device_parameter"
      target_device: 2
      parameter: "Filter Frequency"
      volume: 0.75
```

---

### Example 6: Hysteresis

Prevent rapid on/off toggling with threshold gap.

```yaml
plugin:
  name: "Youlean Loudness Meter"
  track: 0
  device: 0

rules:
  - name: "enable_compression_high"
    priority: 20
    cooldown: 500
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -13.0  # Upper threshold
    action:
      type: "set_device_parameter"
      parameter: "Compressor Threshold"
      volume: 0.7  # Enable compression

  - name: "disable_compression_low"
    priority: 15
    cooldown: 500
    condition:
      parameter: "LUFS Integrated"
      operator: "<"
      value: -11.0  # Lower threshold (hysteresis gap)
    action:
      type: "set_device_parameter"
      parameter: "Compressor Threshold"
      volume: 0.5  # Disable compression
```

**Hysteresis Gap**: 2.0 LUFS (upper 13.0 vs lower 11.0) prevents rapid toggling around 12.0.

---

### Example 7: Priority-Based Rules

Emergency rules override lower priority rules.

```yaml
plugin:
  name: "Production Analyzer"
  track: 0
  device: 0

rules:
  # Priority 5: Emergency (highest)
  - name: "emergency_peak_limiter"
    priority: 5
    cooldown: 100
    condition:
      parameter: "Peak Level"
      operator: ">"
      value: 0.5
    action:
      type: "set_master_volume"
      volume: 0.0  # Immediate cutoff

  # Priority 20: Normal operation
  - name: "loudness_monitoring"
    priority: 20
    cooldown: 1000
    condition:
      parameter: "LUFS Integrated"
      operator: ">="
      value: -14.0
    action:
      type: "log"
      message: "LUFS: {LUFS Integrated:.2f}"
```

**Behavior**: When Peak > 0.5, emergency rule fires and overrides all normal rules until peak drops.

---

### Example 8: Parameter Comparison

Dynamic threshold based on another parameter.

```yaml
plugin:
  name: "Dynamics Analyzer"
  track: 0
  device: 0

rules:
  - name: "compress_when_dynamic_low"
    priority: 12
    cooldown: 400
    condition:
      parameter: "Dynamic Range"
      operator: "<"
      param1: "LUFS Integrated"
      param2: "LUFS Integrated"
      value: 2.5  # DR < LUFS × 2.5
    action:
      type: "set_device_parameter"
      parameter: "Compressor Ratio"
      volume: 0.8  # More compression

  - name: "release_when_dynamic_high"
    priority: 11
    cooldown: 400
    condition:
      parameter: "Dynamic Range"
      operator: ">"
      param1: "LUFS Integrated"
      param2: "LUFS Integrated"
      value: 3.5  # DR > LUFS × 3.5
    action:
      type: "set_device_parameter"
      parameter: "Compressor Ratio"
      volume: 0.4  # Less compression
```

---

## Advanced Patterns

### Pattern 1: Multiple Actions Per Rule

Execute several actions when condition is true.

```yaml
rules:
  - name: "peak_protection_comprehensive"
    priority: 15
    condition:
      parameter: "Peak Level"
      operator: ">"
      value: 0.95
    action:
      # Action 1: Log warning
      type: "log"
      message: "⚠️  PEAK WARNING: {Peak Level:.4f}"

      # Action 2: Reduce volume
      type: "set_master_volume"
      volume: 0.75
```

### Pattern 2: Action-Level Cooldown

Override rule cooldown for specific actions.

```yaml
rules:
  - name: "fast_volume_adjustment"
    priority: 10
    cooldown: 2000  # 2 seconds between rule triggers
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -13.0
    action:
      type: "set_track_volume"
      volume: 0.85
      cooldown: 100  # But this action can repeat every 100ms
```

### Pattern 3: Parameter Format Strings

Use formatting in log messages.

```yaml
rules:
  - name: "detailed_status"
    condition:
      parameter: "LUFS Integrated"
      operator: ">="
      value: -14.0
    action:
      type: "log"
      message: "Status: LUFS={LUFS Integrated:.2f}, Peak={Peak Level:.2f}, DR={Dynamic Range:.2f}"
```

### Pattern 4: Time-Based Behavior

Use different cooldowns for different rule behaviors.

```yaml
rules:
  - name: "fast_alert"
    priority: 5
    cooldown: 50  # Fast response
    condition:
      parameter: "Peak Level"
      operator: ">"
      value: 0.98
    action:
      type: "log"
      message: "ALERT: Peak {Peak Level:.4f}"

  - name: "gradual_adjustment"
    priority: 15
    cooldown: 1000  # Slower response
    condition:
      parameter: "LUFS Integrated"
      operator: ">="
      value: -14.0
    action:
      type: "set_track_volume"
      volume: 0.88
```

---

## Error Handling

### Common Parsing Errors

**Error**: Parameter name not found in metrics

**Solution**: Verify parameter name matches exactly (case-sensitive).

```yaml
# Wrong
condition:
  parameter: "loudness"  # Typo

# Correct
condition:
  parameter: "LUFS Integrated"  # Actual parameter name
```

**Error**: Invalid operator

**Solution**: Use only supported operators: `>`, `<`, `>=`, `<=`, `==`, `!=`, `and`, `or`, `not`.

```yaml
# Wrong
condition:
  operator: "="  # Missing one character

# Correct
condition:
  operator: ">="  # Complete operator
```

**Error**: YAML syntax error

**Solution**: Verify indentation (2 spaces), colons with spaces, proper quoting.

```yaml
# Wrong
condition: {parameter: "LUFS", operator: ">", value: -14.0}

# Correct
condition:
  parameter: "LUFS Integrated"
  operator: ">"
  value: -14.0
```

### Common Logic Errors

**Error**: Condition never triggers

**Possible Causes**:
1. Threshold value too high/low
2. Operator direction wrong (`>` vs `<`)
3. Parameter values not updating

**Debugging Steps**:
1. Use CLI monitor to observe actual parameter values
2. Add log action to condition to verify evaluation
3. Check cooldown period preventing trigger
4. Verify priority order (higher evaluated first)

**Debug Rule**:
```yaml
rules:
  - name: "debug_loudness_check"
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -14.0
    action:
      type: "log"
      message: "DEBUG: LUFS={LUFS Integrated}, Condition: > -14.0"
```

### Common Action Errors

**Error**: Action executes but no effect

**Possible Causes**:
1. Wrong track/device index
2. Parameter name incorrect
3. Value out of range
4. MCP server not connected

**Verification Steps**:
1. Check Ableton Live is open
2. Verify Remote Script is loaded
3. Confirm MCP server is running (port 9877)
4. Use `get_device_parameters` to verify parameter exists
5. Check device index (first device on track = index 0)

---

## Best Practices

### 1. Use Descriptive Rule Names

✅ **Good**:
```yaml
- name: "emergency_peak_protection_when_loud"
  priority: 5
```

❌ **Avoid**:
```yaml
- name: "rule1"
- name: "loudness_warning"
```

### 2. Set Appropriate Priorities

- Emergency: 1-9
- Critical: 10-19
- Important: 20-39
- Normal: 40-49
- Low: 50+

### 3. Use Cooldowns Prevent Oscillation

- Start with cooldown of 200-500ms
- Adjust based on observed behavior
- Higher cooldown for aggressive actions

### 4. Test Rules Individually

1. Create test configuration with single rule
2. Run with verbose logging
3. Verify trigger points
4. Check action execution

### 5. Document Threshold Rationale

```yaml
rules:
  # Document why this threshold
  - name: "ebu_r128_loudness_limit"
    # Target: EBU R128 standard (-16 LUFS integrated for music)
    priority: 15
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -14.0  # Slightly below EBU R128
    action:
      type: "log"
      message: "Above EBU R128 target"
```

### 6. Monitor Performance

- Check CPU usage during operation
- Measure achieved polling rate
- Adjust if system overloaded
- Use benchmarks to optimize

---

## Performance Notes

### Condition Evaluation Cost

- **Simple comparison**: < 0.1ms
- **AND/OR with 2 conditions**: < 0.2ms
- **AND/OR with 4 conditions**: < 0.3ms
- **NOT operation**: < 0.1ms

### Action Execution Cost

- **Log action**: < 0.01ms
- **set_track_volume**: < 5ms (MCP TCP round-trip)
- **set_device_parameter**: < 10ms (MCP TCP round-trip)

### Optimization Guidelines

- Keep rules simple when high polling rate (20-30 Hz)
- Use priority for emergency rules
- Increase cooldowns for expensive actions
- Batch log messages when possible

---

## See Also

- [Configuration Reference](configuration.md) - All configuration options
- [Getting Started Tutorial](tutorial.md) - 15-minute quick start
- [Rule Configuration Guide](rule_configuration.md) - Advanced rule patterns
- [User Guide](user_guide.md) - Comprehensive usage guide
- [API Reference](api_reference.md) - Python API documentation
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

*Last Updated: 2026-02-10*
*Part of VST Audio Analysis Integration*
*Compatible with Ableton Live 11+*
