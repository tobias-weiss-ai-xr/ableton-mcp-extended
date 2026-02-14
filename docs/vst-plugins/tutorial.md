# VST Audio Analysis - 15-Minute Getting Started Tutorial

## Overview

This tutorial walks you through setting up and using the VST Audio Analysis system in 15 minutes. You'll learn to:

1. Install a VST plugin with audio analysis parameters
2. Create a rule configuration file
3. Run real-time audio analysis with automatic control
4. Monitor results with the CLI tool

**Time**: 15 minutes
**Prerequisites**:
- Ableton Live 11+ installed
- Python 3.8+ installed
- ableton-mcp-extended repository cloned

---

## Step 1: Install Audio Analysis Plugin (5 minutes)

If you already have a plugin installed, skip to Step 2.

### 1.1 Choose and Install Plugin

**Recommended Plugins**:
- **Youlean Loudness Meter 2** (Free) - LUFS analysis
- **Voxengo SPAN** (Freeware) - Spectral analysis
- **MAnalyzer** - Multi-metric analysis

### 1.2 Installation

Follow the [Installation Guide](installation_guide.md) for your OS and plugin.

**Quick Install (Youlean Loudness Meter 2):**
1. Download from: https://youlean.co/youlean-loudness-meter/
2. Run installer with admin privileges
3. Select VST3 format
4. Rescan plugins in Ableton (Options → Plug-Ins → Rescan)

### 1.3 Verify Installation

1. Open Ableton Live
2. Create new track (Cmd+T / Ctrl+T)
3. Open Browser (Shift+F5 / Cmd+F5)
4. Search for plugin name (e.g., "Youlean" or "Voxengo")
5. Drag plugin onto track

**Success**: Plugin loads and displays analysis meters.

---

## Step 2: Identify Plugin Parameters (2 minutes)

Find which parameters the plugin exposes for analysis.

### 2.1 List Device Parameters

In Python, query the plugin:

```python
import socket
import json

# Connect to Ableton MCP server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9877))

# Get device parameters
command = {
    'type': 'get_device_parameters',
    'params': {
        'track_index': 0,
        'device_index': 0
    }
}
sock.send(json.dumps(command).encode('utf-8'))
response = sock.recv(8192).decode('utf-8')
params = json.loads(response)

# Print all parameters
for i, param in enumerate(params):
    print(f"[{i}] {param['name']}: min={param['min_value']}, max={param['max_value']}")

sock.close()
```

### 2.2 Identify Analysis Parameters

Look for parameters related to:
- **LUFS/Loudness**: Usually named "LUFS Integrated", "Momentary LUFS", "Loudness"
- **Spectral Analysis**: "Spectral Centroid", "Spectral Spread", "Frequency Band"
- **Dynamics**: "Peak", "RMS", "Dynamic Range", "Crest Factor"

**Example Output**:
```
[0] Momentary LUFS: min=-60.0, max=0.0
[1] LUFS Integrated: min=-60.0, max=0.0
[2] True Peak: min=-60.0, max=6.0
```

**Note**: Parameter indices (0, 1, 2...) depend on plugin. Use the index shown in brackets.

---

## Step 3: Create Rule Configuration File (3 minutes)

Define when and how the system should react to audio analysis.

### 3.1 Create Config File

Create `my_analysis.yml`:

```yaml
plugin:
  name: "Youlean Loudness Meter"  # Plugin name (for logging)
  track: 0                                    # Track containing plugin
  device: 0                                    # Device index on track

rules:
  # Rule 1: Warning when loudness is too high
  - name: "loudness_warning"
    priority: 10                              # Lower = higher priority
    condition:
      parameter: "LUFS Integrated"           # Parameter name
      operator: ">"
      value: -14.0                           # LUFS threshold (EBU R128 standard)
    action:
      type: "log"                             # Action: log message
      message: "WARNING: Loudness exceeds -14 LUFS"
      cooldown: 200                            # Milliseconds between triggers

  # Rule 2: Reduce volume when loudness is very high
  - name: "reduce_volume_high"
    priority: 20
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -10.0
    action:
      type: "set_track_volume"
      target_track: 0                         # Track to control
      volume: 0.85                             # Normalized (0.0-1.0)
      cooldown: 200

  # Rule 3: Increase volume when quiet
  - name: "increase_volume_low"
    priority: 15
    condition:
      parameter: "LUFS Integrated"
      operator: "<"
      value: -16.0
    action:
      type: "set_track_volume"
      target_track: 0
      volume: 0.90
      cooldown: 300
```

### 3.2 Configuration Reference

| Section | Required | Description |
|---------|----------|-------------|
| `plugin` | Yes | Plugin metadata |
| `rules` | Yes | List of rules to evaluate |

| Plugin Field | Required | Description |
|-------------|----------|-------------|
| `name` | No | Plugin name (for logging) |
| `track` | Yes | Track index (0-based) |
| `device` | Yes | Device index (0-based) |

| Rule Field | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique rule name |
| `priority` | No | Priority (higher = evaluated first) |
| `condition` | Yes | Condition to evaluate |
| `action` | Yes | Action to execute |
| `cooldown` | No | Minimum milliseconds between triggers |

| Condition Field | Required | Description |
|----------------|----------|-------------|
| `parameter` | Yes | Parameter name to evaluate |
| `operator` | Yes | Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=`, `AND`, `OR` |
| `value` | Yes | Threshold value (plugin-specific units) |

| Action Field | Required | Description |
|--------------|----------|-------------|
| `type` | Yes | Action type: `log`, `set_track_volume`, `set_device_parameter` |
| `message` | No (log) | Log message text |
| `target_track` | No (set_track_volume) | Track index (default: plugin track) |
| `target_device` | No (set_device_parameter) | Target device (default: plugin device) |
| `parameter` | No (set_device_parameter) | Parameter name |
| `volume/value` | No | Normalized value (0.0-1.0) or plugin-specific value |

---

## Step 4: Test Your Configuration (2 minutes)

Verify the configuration parses correctly.

### 4.1 Parse Configuration

```python
from scripts.analysis.rules_parser import RulesParser

parser = RulesParser()
rules = parser.parse('my_analysis.yml')

print(f"Loaded {len(rules)} rules:")
for rule in rules:
    print(f"  - {rule.name} (priority {rule.priority})")
```

**Expected Output**:
```
Loaded 3 rules:
 - loudness_warning (priority 10)
 - reduce_volume_high (priority 20)
 - increase_volume_low (priority 15)
```

### 4.2 Troubleshooting

**Error: "File not found"**
- Check file path is correct
- Ensure working directory is repository root

**Error: "YAML syntax error"**
- Verify YAML indentation (2 spaces, no tabs)
- Check colons have space after them
- Use YAML validator

**Error: "No rules loaded"**
- Ensure `rules:` section exists
- Check rule indentation under `rules:`

---

## Step 5: Run Real-Time Analysis (3 minutes)

Execute the responsive control system.

### 5.1 Run with Python Script

Using the built-in control script:

```bash
cd scripts/analysis
python responsive_control.py \
  --config ../../configs/analysis/my_analysis.yml \
  --poll-rate 20 \
  --verbose
```

**CLI Options**:
- `--config`: Path to YAML config file (required)
- `--poll-rate`: Polling rate in Hz (default: 20)
- `--verbose`: Enable detailed logging (optional)

### 5.2 What to Expect

**Console Output**:
```
[INFO] Loading configuration from my_analysis.yml
[INFO] Loaded 3 rules
[INFO] Starting parameter polling at 20 Hz
[INFO] Connected to Ableton at localhost:9877
[INFO] Polling LUFS Integrated: -13.2 LUFS
[INFO] Evaluating rules...
[INFO] [RULE] Loudness within range
[INFO] Polling LUFS Integrated: -13.5 LUFS
[INFO] Evaluating rules...
[INFO] [RULE] Loudness within range
```

**System Behavior**:
- Polls plugin parameters at configured rate
- Evaluates all rules in priority order
- Executes actions when conditions are met
- Respects cooldown periods to prevent oscillation
- Handles errors gracefully (continues polling)

---

## Step 6: Monitor Results (Optional)

Use the CLI monitor tool for real-time visualization.

### 6.1 Start CLI Monitor

```bash
cd scripts/analysis
python monitor_analysis.py \
  --plugin-name "Youlean Loudness Meter" \
  --track 0 \
  --device 0 \
  --parameters "LUFS Integrated:5,True Peak:6" \
  --rate 20
```

**CLI Monitor Features**:
- Real-time metric display
- Min/max/average statistics
- Timestamp tracking
- Visual event log
- Ctrl+C to exit

**Expected Display**:
```
╔══════════════════════════════════════╗
║  VST Audio Analysis Monitor                         ║
╠════════════════════════════════════════╣
║  Metrics:                                   ║
║  • LUFS Integrated    -13.2 LUFS    [-14.0 to -12.5]  ║
║  • True Peak         -1.2 dB      [-6.0 to -0.8]     ║
╠════════════════════════════════════════╣
║  Statistics:                                ║
║  • LUFS Integrated    min:-14.2 max:-12.0 avg:-13.4 ║
╠════════════════════════════════════════╣
║  Press Ctrl+C to stop                    ║
╚══════════════════════════════════════════╝
```

---

## Common Configurations

### Example 1: LUFS Monitoring Only

Monitor loudness without automatic control:

```yaml
plugin:
  name: "Youlean Loudness Meter"
  track: 0
  device: 0

rules:
  - name: "loudness_log"
    priority: 10
    condition:
      parameter: "LUFS Integrated"
      operator: ">="
      value: -14.0
    action:
      type: "log"
      message: "Loudness: {LUFS Integrated} LUFS"
      cooldown: 500  # Log every 500ms
```

### Example 2: Simple Volume Control

Automatic volume adjustments based on LUFS:

```yaml
plugin:
  name: "Youlean Loudness Meter"
  track: 0
  device: 0

rules:
  - name: "loud_too_high"
    condition:
      parameter: "LUFS Integrated"
      operator: ">"
      value: -12.0
    action:
      type: "set_track_volume"
      volume: 0.85

  - name: "quiet_too_low"
    condition:
      parameter: "LUFS Integrated"
      operator: "<"
      value: -16.0
    action:
      type: "set_track_volume"
      volume: 0.90
```

### Example 3: Spectral Filter Control

Control filter based on spectral content:

```yaml
plugin:
  name: "Voxengo SPAN"
  track: 0
  device: 0

rules:
  - name: "bright_sound_open_filter"
    condition:
      parameter: "Spectral Centroid"
      operator: ">"
      value: 4000.0
    action:
      type: "set_device_parameter"
      target_device: 1           # Filter device on synth track
      parameter: "Filter Frequency"
      value: 0.90

  - name: "dark_sound_close_filter"
    condition:
      parameter: "Spectral Centroid"
      operator: "<"
      value: 2000.0
    action:
      type: "set_device_parameter"
      target_device: 1
      parameter: "Filter Frequency"
      value: 0.40
```

---

## Next Steps

### 1. Explore Advanced Features

- **Multi-Scenario Rules**: Combine conditions with AND/OR
- **Complex Actions**: Execute multiple actions per rule
- **Custom Action Types**: Extend with custom action handlers

See [Configuration Reference](configuration.md) for all options.

### 2. Learn Rule Syntax

Master the full rule language for complex scenarios.

See [Rules API Reference](rules_api.md) for complete syntax.

### 3. Performance Optimization

Adjust polling rates and rule complexity for your system.

See [User Guide](user_guide.md) for performance best practices.

### 4. Run Benchmarks

Measure system performance and optimize configurations.

See [Performance Report](performance_report.md) for benchmark interpretation.

---

## Troubleshooting

### Issue 1: Rules Not Triggering

**Symptom**: Expected condition met, but rule doesn't fire.

**Solutions**:
1. Verify parameter name matches exactly (case-sensitive)
2. Check operator value is correct (`>`, `<`, `>=`, `<=`, `==`, `!=`)
3. Confirm threshold value matches plugin output range
4. Check priority order (higher priority evaluated first)
5. Verify cooldown period has elapsed

### Issue 2: Connection Errors

**Symptom**: "Connection refused" or timeout errors.

**Solutions**:
1. Confirm Ableton Live is open
2. Verify Remote Script is loaded (Preferences → Link, Tempo & MIDI → Control Surface: AbletonMCP)
3. Check MCP server is running (port 9877)
4. Ensure Ableton session is not frozen

### Issue 3: Parameter Values Not Updating

**Symptom**: Parameters show same values despite audio playing.

**Solutions**:
1. Verify plugin is receiving audio signal (track routing)
2. Check track volume is not muted
3. Confirm plugin parameters are exposed (see Step 2)
4. Try playing test audio to verify plugin responds

### Issue 4: High CPU Usage

**Symptom**: System uses >80% CPU during polling.

**Solutions**:
1. Reduce polling rate (e.g., 10 Hz instead of 20 Hz)
2. Reduce number of rules
3. Simplify rule conditions
4. Run benchmarks to identify bottlenecks

---

## See Also

- [Installation Guide](installation_guide.md) - Plugin installation
- [Configuration Reference](configuration.md) - All configuration options
- [Rules API Reference](rules_api.md) - Complete rule syntax
- [User Guide](user_guide.md) - Comprehensive user guide
- [API Reference](api_reference.md) - Python API documentation
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

*Last Updated: 2026-02-10*
*Part of VST Audio Analysis Integration*
*Compatible with Ableton Live 11+*
