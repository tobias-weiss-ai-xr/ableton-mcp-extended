# VST Audio Analysis - Rule Configuration Guide

## Table of Contents

1. [Rule Basics](#rule-basics)
2. [Condition Reference](#condition-reference)
3. [Action Reference](#action-reference)
4. [Rule Examples](#rule-examples)
5. [Advanced Patterns](#advanced-patterns)
6. [Best Practices](#best-practices)
7. [Troubleshooting Rules](#troubleshooting-rules)

---

## Rule Basics

### Rule Structure

A rule consists of:
1. **Name** - Unique identifier
2. **Condition** - When to trigger
3. **Actions** - What to do when triggered

```yaml
rules:
  - name: "my_rule"
    condition:
      metric: "metric_name"
      operator: ">"
      threshold: 0.5
    actions:
      - type: "log"
        message: "Rule triggered!"
```

### Rule Execution Flow

```
1. Poller collects metric values
   ↓
2. Control Loop passes values to Rule Engine
   ↓
3. Rule Engine evaluates each rule's condition
   ↓
4. If condition is True, execute all actions
   ↓
5. Action handler processes each action
```

### Loading Rules

**From YAML file:**
```python
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

engine = RuleEngine.from_file("my_rules.yaml")
```

**Programmatically:**
```python
from ableton_mcp_extended.audio_analysis.rules import Rule, Condition, Action

condition = Condition(metric="loudness", operator=">", threshold=0.8)
action = Action(type="log", message="High loudness!")
rule = Rule(name="high_loudness", condition=condition, actions=[action])

engine = RuleEngine([rule])
```

---

## Condition Reference

### Condition Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `metric` | `string` | Yes | Name of metric to evaluate |
| `operator` | `string` | Yes | Comparison operator |
| `threshold` | `float` | Yes | Value to compare against |

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `>` | Greater than | `threshold: 0.8` - triggers when `value > 0.8` |
| `<` | Less than | `threshold: 0.2` - triggers when `value < 0.2` |
| `>=` | Greater than or equal | `threshold: 0.5` - triggers when `value >= 0.5` |
| `<=` | Less than or equal | `threshold: 0.5` - triggers when `value <= 0.5` |
| `==` | Equal to | `threshold: 0.7` - triggers when `value == 0.7` |
| `!=` | Not equal to | `threshold: 0.7` - triggers when `value != 0.7` |

### Common Threshold Patterns

**Loudness (LUFS to 0-1 scale):**
```yaml
condition:
  metric: "loudness"
  operator: ">"
  threshold: 0.8  # 80% = high loudness warning
```

**Spectral Centroid (brightness):**
```yaml
condition:
  metric: "spectral_centroid"
  operator: "<"
  threshold: 0.3  # Low brightness = darker sound
```

**Peak Level:**
```yaml
condition:
  metric: "peak"
  operator: ">"
  threshold: 0.95  # Near clipping
```

---

## Action Reference

### Action Types

#### Log Action

Write a message to console/log file.

**Attributes:**
- `type`: `"log"` (required)
- `message`: Message string (required)
- Message supports Python format strings with metric values

**Example:**
```yaml
actions:
  - type: "log"
    message: "Loudness: {loudness:.2f} | Spectral: {spectral_centroid:.2f}"
```

**Output:**
```
[RULE] Loudness: 0.85 | Spectral: 0.62
```

---

#### Trigger Device Action

Set a parameter on an Ableton device.

**Attributes:**
- `type`: `"trigger_device"` (required)
- `track_index`: Track index (0-based) (required)
- `device_index`: Device index on track (0-based) (required)
- `parameter_index`: Parameter index (0-based) (required)
- `value`: Normalized value 0.0-1.0 (required)

**Example:**
```yaml
actions:
  - type: "trigger_device"
    track_index: 0
    device_index: 1
    parameter_index: 0
    value: 0.7
```

**Usage in Action Handler:**
```python
def action_handler(action):
    if action["type"] == "trigger_device":
        ableton_mcp_extended.set_device_parameter(
            track_index=action["track_index"],
            device_index=action["device_index"],
            parameter_index=action["parameter_index"],
            value=action["value"]
        )
```

---

#### Custom Action Types

You can extend with custom action types in your action handler:

```yaml
actions:
  - type: "send_osc_message"
    address: "/trigger"
    arguments: [1, 0.5]
```

```python
def action_handler(action):
    if action["type"] == "send_osc_message":
        send_osc(action["address"], action["arguments"])
```

---

## Rule Examples

### Example 1: Simple Loudness Warning

```yaml
rules:
  - name: "high_loudness_warning"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "⚠️  WARNING: High loudness detected: {loudness:.2f}"
```

**Triggers when:** Loudness exceeds 0.8

---

### Example 2: Low Energy Detection

```yaml
rules:
  - name: "low_energy_detected"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.2
    actions:
      - type: "log"
        message: "Silence detected at {timestamp}"
```

**Triggers when:** Loudness drops below 0.2 (silence)

---

### Example 3: Brightness Analysis

```yaml
rules:
  - name: "bright_sound_detected"
    condition:
      metric: "spectral_centroid"
      operator: ">"
      threshold: 0.7
    actions:
      - type: "log"
        message: "Bright sound: spectral_centroid = {spectral_centroid:.2f}"

  - name: "dark_sound_detected"
    condition:
      metric: "spectral_centroid"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "log"
        message: "Dark sound: spectral_centroid = {spectral_centroid:.2f}"
```

**Triggers when:**
- First rule: Sound is bright (high spectral centroid)
- Second rule: Sound is dark (low spectral centroid)

---

### Example 4: Automatic Gain Control

```yaml
rules:
  - name: "reduce_gain_high_loudness"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.85
    actions:
      - type: "log"
        message: "Reducing gain to prevent clipping: {loudness:.2f}"
      - type: "trigger_device"
        track_index: 0
        device_index: 1  # Compressor device
        parameter_index: 0  # Threshold
        value: 0.3

  - name: "reset_gain_normal"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.6
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.5
```

**Triggers when:**
- First rule: Loudness too high → reduce gain
- Second rule: Loudness back to normal → reset gain

---

### Example 5: Peak Protection

```yaml
rules:
  - name: "peak_protection"
    condition:
      metric: "peak"
      operator: ">"
      threshold: 0.98
    actions:
      - type: "log"
        message: "🚨 PEAK WARNING: {peak:.4f} - Immediate action required!"
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.1  # Emergency gain reduction
```

**Triggers when:** Signal approaches digital clipping

---

### Example 6: Dynamic Range Analysis

```yaml
rules:
  - name: "compress_signal"
    condition:
      metric: "dynamic_range"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "log"
        message: "High compression detected: DR = {dynamic_range:.2f}"

  - name: "good_dynamic_range"
    condition:
      metric: "dynamic_range"
      operator: ">"
      threshold: 0.6
    actions:
      - type: "log"
        message: "Good dynamic range: DR = {dynamic_range:.2f}"
```

**Triggers when:**
- First rule: Signal is over-compressed (DR < 0.3)
- Second rule: Signal has good dynamic range (DR > 0.6)

---

### Example 7: Multi-Metric Validation

```yaml
rules:
  - name: "balanced_audio_check"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.6
    actions:
      - type: "log"
        message: "Loudness OK, checking spectral balance..."

  - name: "spectral_imbalance_warning"
    condition:
      metric: "spectral_centroid"
      operator: "<"
      threshold: 0.4
    actions:
      - type: "log"
        message: "⚠️  Spectral imbalance: too much low-frequency content"
```

**Triggers when:** Loudness is OK, but spectrum is unbalanced

---

### Example 8: Absolute vs Relative Thresholds

```yaml
rules:
  - name: "absolute_threshold"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "Above absolute threshold: 0.8"

  - name: "relative_threshold"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.5  # Adjust based on average level
    actions:
      - type: "log"
        message: "Above relative threshold: 0.5 (songs's average)"
```

---

### Example 9: Temporary State Detection

```yaml
rules:
  - name: "transient_spike"
    condition:
      metric: "peak"
      operator: ">"
      threshold: 0.9
    actions:
      - type: "log"
        message: "Transient spike detected: {peak:.4f}"
```

**Triggers when:** Sudden transient spikes occur

---

### Example 10: Complete Production Rule Set

```yaml
rules:
  # Loudness Management
  - name: "loudness_compliant"
    condition:
      metric: "loudness"
      operator: ">="
      threshold: 0.6
    actions:
      - type: "log"
        message: "✓ Loudness compliant: {loudness:.2f}"

  - name: "loudness_too_low"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.4
    actions:
      - type: "log"
        message: "⚠️  Loudness too low: {loudness:.2f}"

  # Peak Protection
  - name: "peak_warning"
    condition:
      metric: "peak"
      operator: ">"
      threshold: 0.95
    actions:
      - type: "log"
        message: "🚨 Peak warning: {peak:.4f}"

  # Spectral Balance
  - name: "balanced_spectrum"
    condition:
      metric: "spectral_centroid"
      operator: ">="
      threshold: 0.4
    actions:
      - type: "log"
        message: "✓ Balanced spectrum: {spectral_centroid:.2f}"

  - name: "dark_sound"
    condition:
      metric: "spectral_centroid"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "log"
        message: "⚠️  Dark sound: {spectral_centroid:.2f}"

  - name: "bright_sound"
    condition:
      metric: "spectral_centroid"
      operator: ">"
      threshold: 0.7
    actions:
      - type: "log"
        message: "⚠️  Bright sound: {spectral_centroid:.2f}"

  # Dynamic Range
  - name: "good_dynamic_range"
    condition:
      metric: "dynamic_range"
      operator: ">"
      threshold: 0.5
    actions:
      - type: "log"
        message: "✓ Good dynamic range: {dynamic_range:.2f}"

  - name: "compressed_signal"
    condition:
      metric: "dynamic_range"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "log"
        message: "⚠️  Over-compressed: {dynamic_range:.2f}"
```

---

## Advanced Patterns

### Pattern 1: Hysteresis

Prevent rapid on/off toggling with thresholds:

```yaml
rules:
  - name: "enable_compression_high"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.85  # Upper threshold
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 2  # Makeup gain
        value: 0.7

  - name: "disable_compression_low"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.65  # Lower threshold (hysteresis)
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 2
        value: 0.5
```

**Hysteresis gap:** 0.85 ↔ 0.65 (prevents rapid toggling at 0.75)

---

### Pattern 2: Time-Based Deactivation

Use external state to implement time delays:

```yaml
rules:
  - name: "initial_silence_check"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.1
    actions:
      - type: "log"
        message: "Silence detected"
      - type: "trigger_device"
        track_index: 0
        device_index: 2
        parameter_index: 0  # Silence detection flag
        value: 1.0
```

**Note:** Implement time delays in action handler, not in rules.

---

### Pattern 3: Gradual Adjustment

Multiple rules for incremental changes:

```yaml
rules:
  - name: "increase_gain_level_1"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.6  # Slight increase

  - name: "increase_gain_level_2"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.2
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.7  # More increase

  - name: "increase_gain_level_3"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.1
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.8  # Maximum increase
```

---

### Pattern 4: Multi-Metric Conditions (Workaround)

Since conditions only support one metric, use multiple rules:

```yaml
rules:
  - name: "check_loudness_level"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.7
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 3
        parameter_index: 0
        value: 1.0  # Set flag: loudness OK

  - name: "check_spectrum_with_flag"
    condition:
      metric: "spectral_centroid"
      operator: "<"
      threshold: 0.4
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 4
        parameter_index: 0
        value: 1.0  # Set flag: spectral imbalanced

  # Read flags in action handler for combined logic
```

---

### Pattern 5: Priority-Based Actions

Order rules by priority (engine evaluates in order):

```yaml
rules:
  # Priority 1: Emergency peak protection
  - name: "emergency_peak_protection"
    condition:
      metric: "peak"
      operator: ">"
      threshold: 0.98
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.0

  # Priority 2: Loudness management
  - name: "loudness_compliance"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 1
        value: 0.5

  # Priority 3: Spectral balance
  - name: "spectral_enhancement"
    condition:
      metric: "spectral_centroid"
      operator: "<"
      threshold: 0.4
    actions:
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 2
        value: 0.6
```

---

## Best Practices

### 1. Use Descriptive Rule Names

✅ Good:
```yaml
- name: "high_loudness_warning_reduce_gain"
```

❌ Avoid:
```yaml
- name: "rule1"
- name: "temp_warning"
```

### 2. Include Context in Log Messages

✅ Good:
```yaml
message: "⚠️  High loudness on TRACK 0: {loudness:.2f} - Reducing gain"
```

❌ Avoid:
```yaml
message: "High loudness"
```

### 3. Test Thresholds with Real Data

Run CLI monitor first:

```python
# Observe actual metric ranges
monitor.start()
# ... observe values ...
```

Then set thresholds based on observed data.

### 4. Use Hysteresis for Stability

Prevent rapid toggling:

```yaml
# Upper threshold
- condition:
    metric: "loudness"
    operator: ">"
    threshold: 0.85

# Lower threshold (gap of 0.2)
- condition:
    metric: "loudness"
    operator: "<"
    threshold: 0.65
```

### 5. Limit Actions Per Rule

✅ Good:
```yaml
actions:
  - type: "log"
    message: "..."
  - type: "trigger_device"
    track_index: 0
    device_index: 1
    parameter_index: 0
    value: 0.5
```

❌ Avoid (too many actions):
```yaml
actions:
  - type: "log"
    message: "..."
  - type: "trigger_device"
    track_index: 0  # 10 device triggers | device_index: 1
    parameter_index: 0
    value: 0.5
  - type: "trigger_device"
    track_index: 0
    device_index: 1
    parameter_index: 1
    value: 0.6
  # ... (10 more actions)
```

### 6. Version Control Rule Files

```bash
git add rules.yaml
git commit -m "Add loudness management rules"
```

Track changes to thresholds and conditions.

### 7. Document Threshold Rationale

```yaml
rules:
  - name: "high_loudness_warning"
    # Document why this threshold was chosen
    # Based on measurements: average loudness = 0.55, target max = 0.8
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "High loudness: {loudness:.2f}"
```

### 8. Test Rules Independently

```python
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

engine = RuleEngine.from_file("rules.yaml")

# Test with sample values
test_values = {"loudness": 0.9, "spectral_centroid": 0.5}
actions = engine.evaluate(test_values)
print(f"Triggered {len(actions)} actions")
```

---

## Troubleshooting Rules

### Rule Not Triggering

**Symptom:** Expected condition met, but rule doesn't trigger

**Checklist:**
1. Verify metric name matches `AudioMetric.name`
2. Check operator spelling (`>`, `>=`, `<`, `<=`, `==`, `!=`)
3. Confirm threshold value is in correct range (0.0-1.0 for normalized)
4. Ensure rule is loaded: `engine.get_rule_names()`
5. Test with actual values: `engine.evaluate({"metric_name": 0.9})`

**Example Fix:**
```yaml
# Wrong
- condition:
    metric: "loudness "  # Trailing space!
    operator: ">"
    threshold: 0.8

# Fix
- condition:
    metric: "loudness"  # No space
    operator: ">"
    threshold: 0.8
```

---

### Rule Triggering Too Often

**Symptom:** Rule triggers continuously even when condition shouldn't be True

**Solutions:**
1. Add hysteresis (see Pattern 1)
2. Increase threshold gap
3. Add debounce in action handler

---

### Invalid YAML Syntax

**Symptom:** `yaml.YAMLError` when loading rules

**Common Errors:**
```yaml
# colons without space
condition: {metric:"loudness"}  # Wrong

# Missing quotation marks
message: High loudness: {loudness:.2f}  # Wrong

# Indentation errors
  - name: "rule"  # Wrong indentation
    condition:
```

**Fix:**
```yaml
# Correct
condition:
  metric: "loudness"

message: "High loudness: {loudness:.2f}"

- name: "rule"  # Correct indentation
  condition:
```

---

### Format String Not Working

**Symptom:** Message shows `{loudness}` instead of actual value

**Fix:**
```yaml
# Wrong
message: "Loudness: {loudness}"  # Wrong metric name?

# Wrong
message: "Loudness: {loudness:.2f"  # Missing closing brace

# Correct
message: "Loudness: {loudness:.2f}"  # Must match metric name exactly
```

---

### Action Handler Not Receiving Actions

**Symptom:** Rules trigger, but action handler never called

**Check:**
1. Verify action handler is passed to `ControlLoop.start()`
2. Check action handler signature
3. Use print/log to confirm receipt

```python
def action_handler(action):
    print(f"Received action: {action}")  # Debug logging
    # Process action...

loop.start(action_handler)
```

---

### Performance Issues

**Symptom:** Rules take too long to evaluate

**Solutions:**
1. Reduce number of rules
2. Simplify conditions (avoid multiple metrics)
3. Reduce polling rate
4. Run benchmarks: `python benchmark_runner.py --type rules`

---

## Complete Example: Production Setup

**File:** `production_rules.yaml`

```yaml
# VST Audio Analysis - Production Rules
# Purpose: Monitor mix compliance and prevent clipping

rules:
  # ─────────────────────────────────────────────────────
  # LOUDNESS MANAGEMENT (Target: 0.6-0.8)
  # ─────────────────────────────────────────────────────
  - name: "loudness_target_compliant"
    condition:
      metric: "loudness"
      operator: ">="
      threshold: 0.6
    actions:
      - type: "log"
        message: "✓ Loudness compliant: {loudness:.2f} LUFS (target: 0.6-0.8)"

  - name: "loudness_too_loud"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
    actions:
      - type: "log"
        message: "⚠️  Loudness too high: {loudness:.2f} - Reduce master gain"

  - name: "loudness_too_quiet"
    condition:
      metric: "loudness"
      operator: "<"
      threshold: 0.6
    actions:
      - type: "log"
        message: "⚠️  Loudness too low: {loudness:.2f} - Increase master gain"

  # ─────────────────────────────────────────────────────
  # PEAK PROTECTION (Max: 0.95)
  # ─────────────────────────────────────────────────────
  - name: "peak_warning"
    condition:
      metric: "peak"
      operator: ">"
      threshold: 0.95
    actions:
      - type: "log"
        message: "🚨 PEAK WARNING: {peak:.4f} - Immediate action!"

  - name: "peak_criticial"
    condition:
      metric: "peak"
      operator: ">"
      threshold: 0.98
    actions:
      - type: "log"
        message: "💀 CRITICAL PEAK: {peak:.4f} - EMERGENCY REDUCTION!"
      - type: "trigger_device"
        track_index: 0
        device_index: 1
        parameter_index: 0
        value: 0.0

  # ─────────────────────────────────────────────────────
  # SPECTRAL BALANCE (Target: 0.4-0.7)
  # ─────────────────────────────────────────────────────
  - name: "spectrum_balanced"
    condition:
      metric: "spectral_centroid"
      operator: ">="
      threshold: 0.4
    actions:
      - type: "log"
        message: "✓ Spectral balance OK: {spectral_centroid:.2f}"

  - name: "spectrum_too_dark"
    condition:
      metric: "spectral_centroid"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "log"
        message: "⚠️  Spectrum too dark: {spectral_centroid:.2f} - Add highs"

  - name: "spectrum_too_bright"
    condition:
      metric: "spectral_centroid"
      operator: ">"
      threshold: 0.7
    actions:
      - type: "log"
        message: "⚠️  Spectrum too bright: {spectral_centroid:.2f} - Add lows"

  # ─────────────────────────────────────────────────────
  # DYNAMIC RANGE (Target: >0.5)
  # ─────────────────────────────────────────────────────
  - name: "dynamic_range_good"
    condition:
      metric: "dynamic_range"
      operator: ">"
      threshold: 0.5
    actions:
      - type: "log"
        message: "✓ Good dynamic range: {dynamic_range:.2f}"

  - name: "dynamic_range_compressed"
    condition:
      metric: "dynamic_range"
      operator: "<"
      threshold: 0.3
    actions:
      - type: "log"
        message: "⚠️  Over-compressed: {dynamic_range:.2f} - Reduce compression"
```

**Usage:**
```python
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

engine = RuleEngine.from_file("production_rules.yaml")
print(f"Loaded {len(engine.get_rule_names())} rules")
```

---

## See Also

- [API Reference - RuleEngine](api_reference.md#module-rules)
- [User Guide - Configuration](user_guide.md#configuration)
- [CLI Monitor Guide](cli_monitor.md)