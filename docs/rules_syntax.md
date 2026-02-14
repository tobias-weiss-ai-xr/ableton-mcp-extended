# Rules Syntax Documentation

This document describes the YAML-based rule syntax for the VST Audio Analysis rule-based decision system.

---

## Overview

The rule system enables automated control decisions based on real-time audio analysis parameters. Rules are defined in YAML files and evaluated by the rules engine.

**Key Components:**
- **Rules**: Individual decision rules with priority, conditions, and actions
- **Conditions**: Comparison or logical expressions using parameter values
- **Actions**: MCP commands to execute when conditions are met
- **Priority**: Lower number = higher priority (rules fire in priority order)

---

## Rule File Structure

```yaml
rules:
  - name: "Rule name"
    priority: 1
    condition:
      # Condition definition
    action:
      # Action definition

  - name: "Another rule"
    priority: 2
    condition:
      # Condition definition
    action:
      # Action definition
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable rule name |
| `priority` | integer | Priority (lower number = higher priority, must be >= 0) |
| `condition` | object | Condition to evaluate (see Condition Syntax) |
| `action` | object | Action to execute when condition is met (see Action Syntax) |

---

## Condition Syntax

### Comparison Operators

Compare a parameter value to a threshold or another parameter.

```yaml
condition:
  operator: ">"
  param1: "0:0"      # Parameter reference (track:device:param)
  param2: "-14.0"     # Literal value or parameter reference
```

**Supported Operators:**
- `>`: Greater than
- `<`: Less than
- `==`: Equal to
- `!=`: Not equal to
- `>=`: Greater than or equal to
- `<=`: Less than or equal to

**Parameter Reference Format:** `"track_index:device_index:parameter_index"`

**Examples:**
```yaml
# LUFS exceeds -14
condition:
  operator: ">"
  param1: "0:0"
  param2: "-14.0"

# LUFS is less than or equal to -20
condition:
  operator: "<="
  param1: "0:0"
  param2: "-20.0"

# True peak exceeds -0.5 dB
condition:
  operator: ">"
  param1: "0:4"
  param2: "-0.5"

# Compare two parameters (e.g., momentary vs short-term LUFS)
condition:
  operator: ">"
  param1: "0:0"
  param2: "0:1"
```

### Logical Operators

Combine multiple conditions with AND, OR, or NOT operators.

#### AND Operator

All sub-conditions must be true.

```yaml
condition:
  operator: "AND"
  conditions:
    - operator: ">"
      param1: "0:0"
      param2: "-14.0"
    - operator: ">"
      param1: "0:5"
      param2: "15.0"
```

**Example:** Compress if LUFS is high AND loudness range is narrow.

#### OR Operator

At least one sub-condition must be true.

```yaml
condition:
  operator: "OR"
  conditions:
    - operator: ">"
      param1: "0:0"
      param2: "-10.0"
    - operator: "<"
      param1: "0:2"
      param2: "-25.0"
```

**Example:** Reduce volume if too loud OR too quiet.

#### NOT Operator

Negates a single condition.

```yaml
condition:
  operator: "NOT"
  condition:
    operator: ">"
    param1: "0:0"
    param2: "-14.0"
```

**Example:** Enable effect if LUFS is NOT above -14.

#### Nested Logical Operators

Logical operators can be nested for complex conditions.

```yaml
condition:
  operator: "AND"
  conditions:
    - operator: ">"
      param1: "0:0"
      param2: "-12.0"
    - operator: "OR"
      conditions:
        - operator: ">"
          param1: "0:4"
          param2: "-0.5"
        - operator: ">"
          param1: "0:6"
          param2: "20.0"
```

**Example:** Trigger if LUFS is high AND (peak is high OR crest factor is high).

---

## Action Syntax

Actions define what happens when a rule's condition is met. Actions map to MCP tool commands.

### Action Types

| Action Type | Description | Required Parameters |
|-------------|-------------|---------------------|
| `set_parameter` | Set device parameter | `parameter_index`, `value` |
| `set_volume` | Set track volume | `volume` (normalized 0.0-1.0 or dB) |
| `set_pan` | Set track panning | `pan` (-1.0 to 1.0) |
| `set_tempo` | Set session tempo | `tempo` (BPM) |
| `fire_clip` | Trigger clip playback | `clip_index` |
| `start_playback` | Start playback | None |
| `stop_playback` | Stop playback | None |
| `start_recording` | Start recording | None |
| `stop_recording` | Stop recording | None |

### Action Structure

```yaml
action:
  type: "action_type"
  params:
    param_name: value
    # ... additional params
```

### Default Parameter Resolution

If `track_index` or `device_index` are not specified in params, they use the engine's defaults:
- `track_index`: Engine's default (from `RulesEngine.__init__`)
- `device_index`: Engine's default (from `RulesEngine.__init__`)

### Action Examples

#### Set Device Parameter

```yaml
action:
  type: "set_parameter"
  params:
    track_index: 1
    device_index: 0
    parameter_index: 2
    value: 0.5
```

#### Set Track Volume

```yaml
# Using normalized value (0.0-1.0)
action:
  type: "set_volume"
  params:
    track_index: 1
    volume: 0.75

# Using dB value (automatic conversion)
action:
  type: "set_volume"
  params:
    track_index: 1
    volume: -3.0  # -60 dB to 0 dB maps to 0.0-1.0
```

#### Set Track Panning

```yaml
action:
  type: "set_pan"
  params:
    track_index: 2
    pan: -0.5  # Left (-1.0 = full left, 1.0 = full right)
```

#### Set Tempo

```yaml
action:
  type: "set_tempo"
  params:
    tempo: 128
```

#### Fire Clip

```yaml
action:
  type: "fire_clip"
  params:
    track_index: 3
    clip_index: 0
```

#### Transport Control

```yaml
# Start playback
action:
  type: "start_playback"
  params: {}

# Stop playback
action:
  type: "stop_playback"
  params: {}

# Start recording
action:
  type: "start_recording"
  params: {}

# Stop recording
action:
  type: "stop_recording"
  params: {}
```

---

## Complete Rule Examples

### Example 1: Loudness-Based Volume Control

```yaml
rules:
  - name: "Reduce volume when LUFS exceeds -14"
    priority: 1
    condition:
      operator: ">"
      param1: "0:0"  # Track 0, Device 0, Parameter 0 (Momentary LUFS)
      param2: "-14.0"
    action:
      type: "set_volume"
      params:
        track_index: 1
        volume: "-3.0"  # Reduce by 3 dB

  - name: "Restore volume when quiet"
    priority: 2
    condition:
      operator: "<"
      param1: "0:0"
      param2: "-20.0"
    action:
      type: "set_volume"
      params:
        track_index: 1
        volume: 0.0  # Full volume
```

### Example 2: Peak Protection

```yaml
rules:
  - name: "Limit peak above -0.5 dB"
    priority: 1
    condition:
      operator: ">"
      param1: "0:4"  # True Peak parameter
      param2: "-0.5"
    action:
      type: "set_volume"
      params:
        track_index: 0
        volume: "-6.0"  # Significantly reduce volume
```

### Example 3: Multi-Condition Rule

```yaml
rules:
  - name: "Compress if loud and dynamic"
    priority: 1
    condition:
      operator: "AND"
      conditions:
        - operator: ">"
          param1: "0:0"  # Momentary LUFS
          param2: "-12.0"
        - operator: ">"
          param1: "0:5"  # Loudness Range
          param2: "10.0"
    action:
      type: "set_parameter"
      params:
        track_index: 0
        device_index: 2
        parameter_index: 0
        value: 0.7
```

### Example 4: Clip Triggering

```yaml
rules:
  - name: "Trigger break clip on quiet"
    priority: 3
    condition:
      operator: "<"
      param1: "0:0"
      param2: "-25.0"
    action:
      type: "fire_clip"
      params:
        track_index: 2
        clip_index: 0
```

### Example 5: Tempo Increase

```yaml
rules:
  - name: "Increase tempo on high energy"
    priority: 5
    condition:
      operator: "AND"
      conditions:
        - operator: ">"
          param1: "0:0"
          param2: "-10.0"
        - operator: ">"
          param1: "0:5"
          param2: "15.0"
    action:
      type: "set_tempo"
      params:
        tempo: 128
```

---

## Rule Priority System

### Priority Rules

- **Lower number = higher priority**
- Rules are evaluated in priority order (1, then 2, then 3, etc.)
- Same priority rules execute in declaration order
- Multiple rules can fire in a single evaluation

### When to Use Different Priorities

| Priority | Use Case |
|----------|-----------|
| 1-5 | Critical safety rules (peak protection, clipping prevention) |
| 6-10 | Important processing rules (compression, limiting) |
| 11-20 | Normal processing rules (volume adjustments) |
| 21-50 | Creative rules (clip triggering, tempo changes) |

### Example: Priority-Based Rule Chain

```yaml
rules:
  # Priority 1: Critical safety
  - name: "Emergency peak limit"
    priority: 1
    condition:
      operator: ">"
      param1: "0:4"
      param2: "-0.3"
    action:
      type: "set_volume"
      params:
        track_index: 0
        volume: "-10.0"

  # Priority 2: Normal processing
  - name: "Apply compression"
    priority: 10
    condition:
      operator: ">"
      param1: "0:0"
      param2: "-14.0"
    action:
      type: "set_parameter"
      params:
        parameter_index: 1
        value: 0.6

  # Priority 3: Creative effect
  - name: "Trigger breakbeat"
    priority: 25
    condition:
      operator: "<"
      param1: "0:0"
      param2: "-25.0"
    action:
      type: "fire_clip"
      params:
        clip_index: 0
```

---

## Parameter Reference Format

### Format

```
"track_index:device_index:parameter_index"
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| `track_index` | Track index in Ableton (0 = first track) | `0`, `1`, `2` |
| `device_index` | Device index on the track (0 = first device) | `0`, `1`, `2` |
| `parameter_index` | Parameter index on the device | `0`, `1`, `2` |

### Finding Parameter Indices

Use `get_device_parameters` MCP tool to list available parameters:

```python
import socket
import json

sock = socket.socket()
sock.connect(('localhost', 9877))

command = {
    'type': 'get_device_parameters',
    'params': {
        'track_index': 0,
        'device_index': 0
    }
}
sock.send(json.dumps(command).encode('utf-8'))
response = json.loads(sock.recv(8192).decode('utf-8'))

# Print parameter indices and names
for param in response.get('params', []):
    print(f"Index {param['index']}: {param['name']}")
```

**Expected Output (Youlean Loudness Meter):**
```
Index 0: Momentary LUFS
Index 1: Short-term LUFS
Index 2: Integrated LUFS
Index 3: RMS Level
Index 4: True Peak
Index 5: Loudness Range
Index 6: Crest Factor
```

---

## Error Handling

### Parse Errors

The rules parser will raise clear error messages for:

- **Invalid YAML syntax**: "YAML syntax error in file.yml: line X"
- **Missing required fields**: "Missing required field: 'priority'"
- **Unknown operator**: "Unknown operator 'BETWEEN'. Supported: >, <, ==, !=, >=, <=, AND, OR, NOT"
- **Unknown action type**: "Unknown action type 'warp_time'. Supported: set_parameter, set_volume, ..."

### Validation Warnings

When validating rules against parameter mappings:

```python
from scripts.analysis.rules_parser import RulesParser

parser = RulesParser()
rules = parser.parse('rules.yml')

# Validate against known parameters
parameter_mappings = {
    "0:0": {"name": "Momentary LUFS", "range": [-70, 5]},
    "0:4": {"name": "True Peak", "range": [-6, 6]},
}
warnings = parser.validate_rules(parameter_mappings)

for warning in warnings:
    print(f"[WARN] {warning}")
```

---

## Best Practices

### 1. Use Cooldowns

Prevent rapid oscillation by using cooldown timers:

```python
engine = RulesEngine(cooldown_seconds=0.5)  # 500ms minimum between firings
```

### 2. Prioritize Safety Rules

Always give peak protection rules priority 1:

```yaml
rules:
  - name: "Peak protection (CRITICAL)"
    priority: 1
    # ...
```

### 3. Use Meaningful Rule Names

```yaml
# Good
name: "Reduce volume when LUFS exceeds -14 dB"

# Bad
name: "Rule 1"
```

### 4. Test Rules Incrementally

Start with simple rules, then add complexity:

1. Test single comparison
2. Test logical operators
3. Test priority ordering
4. Test action execution

### 5. Document Parameter Indices

Add comments to rule files:

```yaml
rules:
  # Youlean Loudness Meter 2 on Track 0, Device 0
  # Parameter 0: Momentary LUFS (-70 to +5 LUFS)
  - name: "Reduce when loud"
    priority: 1
    condition:
      operator: ">"
      param1: "0:0"
      param2: "-14.0"
```

---

## Complete Example Rule File

```yaml
# configs/analysis/lufs_compressor.yml
# Loudness-based control system for dub techno
# Assumes Youlean Loudness Meter 2 on Track 0, Device 0

rules:
  # Priority 1: Emergency peak protection
  - name: "Emergency peak limit"
    priority: 1
    condition:
      operator: ">"
      param1: "0:4"  # True Peak
      param2: "-0.3"
    action:
      type: "set_volume"
      params:
        track_index: 0
        volume: "-10.0"

  # Priority 2: Normal loudness compression
  - name: "Compress when LUFS exceeds -14"
    priority: 2
    condition:
      operator: ">"
      param1: "0:0"  # Momentary LUFS
      param2: "-14.0"
    action:
      type: "set_volume"
      params:
        track_index: 0
        volume: "-3.0"

  # Priority 3: Restore volume when quiet
  - name: "Restore volume when LUFS below -20"
    priority: 3
    condition:
      operator: "<"
      param1: "0:0"
      param2: "-20.0"
    action:
      type: "set_volume"
      params:
        track_index: 0
        volume: 0.0

  # Priority 10: Trigger break clip on quiet sections
  - name: "Trigger break on quiet"
    priority: 10
    condition:
      operator: "<"
      param1: "0:0"
      param2: "-25.0"
    action:
      type: "fire_clip"
      params:
        track_index: 2
        clip_index: 0

  # Priority 20: Increase tempo on high energy
  - name: "Increase tempo on high energy"
    priority: 20
    condition:
      operator: "AND"
      conditions:
        - operator: ">"
          param1: "0:0"
          param2: "-10.0"
        - operator: ">"
          param1: "0:5"  # Loudness Range
          param2: "15.0"
    action:
      type: "set_tempo"
      params:
        tempo: 128
```

---

## Related Documentation

- **Parameter Mappings**: `docs/vst-plugins/parameter_mappings.md`
- **Implementation Guide**: `scripts/analysis/README.md`
- **MCP Tool Reference**: Available via MCP server (`list-tools` command)
