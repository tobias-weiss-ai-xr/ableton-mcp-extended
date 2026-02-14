# Responsive Control Loop

Continuous parameter polling and rule evaluation for VST audio analysis.

## Overview

The `responsive_control.py` script provides a responsive control loop that:
1. Continuously polls VST plugin parameters from Ableton Live
2. Evaluates rules against current parameter values
3. Executes actions when rule conditions are met
4. Measures latency from parameter read to action completion
5. Provides statistics (rules fired per second, latency metrics)
6. Supports dry-run mode for testing without executing actions

## Features

- **Continuous Control Loop**: Polls parameters at configurable rate (5-30 Hz)
- **Latency Measurement**: Tracks end-to-end latency (parameter read → action complete)
- **Statistics Tracking**: Monitors rules fired, actions executed, latency metrics
- **Dry-Run Mode**: Test rule logic without executing actions
- **Graceful Shutdown**: Ctrl+C handling with summary statistics
- **Cooldown Support**: Prevents rule oscillation with configurable cooldown
- **Rule Prioritization**: Processes rules by priority (lower number = higher priority)

## Usage

### Basic Usage

```bash
python scripts/analysis/responsive_control.py --rules=configs/analysis/lufs_compressor.yml --track=0 --device=0 --rate=15 --duration=60
```

### Dry-Run Mode (Testing)

Test rules without executing actions:

```bash
python scripts/analysis/responsive_control.py --rules=configs/analysis/lufs_compressor.yml --dry-run --duration=10
```

### Verbose Output

See detailed information about rule evaluation:

```bash
python scripts/analysis/responsive_control.py --rules=configs/analysis/lufs_compressor.yml --verbose --duration=30
```

### Infinite Polling

Run continuously until Ctrl+C:

```bash
python scripts/analysis/responsive_control.py --rules=configs/analysis/lufs_compressor.yml --track=0 --device=0 --rate=15 --duration=0
```

## Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|----------|-------------|
| `--rules` | str | (required) | Path to YAML rule configuration file |
| `--track` | int | 0 | Track index for parameter polling |
| `--device` | int | 0 | Device index for parameter polling |
| `--rate` | float | 15.0 | Polling rate in Hz (5-30) |
| `--duration` | int | 0 | Duration in seconds (0 = infinite) |
| `--dry-run` | flag | False | Dry-run mode - show actions without executing |
| `--verbose` | flag | False | Enable verbose output |
| `-h, --help` | - | - | Show help message |

## Output

### Real-Time Statistics

Every 50 poll cycles, the script displays:

```
[STATS] Polls: 50 | Rate: 12.5 Hz | Rules fired: 3 | Rules/sec: 0.25
[STATS] Latency: avg=45.23ms, max=78.45ms (last 50)
[STATS] Elapsed: 4.0s
```

### Final Summary

On exit (Ctrl+C or duration complete), displays:

```
======================================================================
RESPONSIVE CONTROL SUMMARY
======================================================================
Total poll cycles: 150
Total duration: 60.5 seconds
Actual polling rate: 2.48 Hz
Target polling rate: 15.00 Hz

Rule Statistics:
  Total rules fired: 15
  Rules per second: 0.25
  Total actions executed: 15

Latency Statistics:
  Average latency: 45.23 ms
  Min latency: 12.34 ms
  Max latency: 78.45 ms
  <100ms target: PASS (45.23ms)

Mode:
  Dry-run: False
======================================================================
```

## Latency Measurement

The script measures end-to-end latency:

1. **Parameter Poll Start**: Timestamp when parameter polling begins
2. **Action Complete**: Timestamp when action execution completes

**Latency = Action Complete Time - Parameter Poll Start Time**

**Target**: Average latency < 100ms

## Dry-Run Mode

Dry-run mode (`--dry-run`) allows you to:
- Test rule logic without executing actions
- Verify rule syntax and evaluation
- Understand which actions would be triggered
- Test with sample data without affecting Ableton session

**Note**: Dry-run mode still requires Ableton to be running (for parameter polling), but does not modify parameters.

## Rule Configuration

See example rule files in `configs/analysis/`:

- `lufs_compressor.yml` - LUFS-based volume control
- `peak_protection.yml` - Peak limiting protection
- `spectral_control.yml` - Spectral content analysis
- `multi_param_control.yml` - Multiple parameter evaluation

### Rule Format

```yaml
rules:
  - name: "Reduce volume when LUFS exceeds -14"
    priority: 2
    condition:
      operator: ">"
      param1: "0:0"  # Track:Device:Param
      param2: "-14.0"
    action:
      type: "set_volume"
      params:
        track_index: 0
        volume: "-3.0"
```

### Parameter References

Use format `track:device:param` to reference parameters:
- `0:0` - Track 0, Device 0, Parameter 0
- `1:2` - Track 1, Device 2, Parameter 2

### Supported Operators

**Comparison**: `>`, `<`, `==`, `!=`, `>=`, `<=`

**Logical**:
- `AND` - All conditions must be true
- `OR` - At least one condition must be true
- `NOT` - Condition must be false

### Supported Actions

- `set_parameter` - Set device parameter
- `set_volume` - Set track volume
- `set_pan` - Set track panning
- `set_tempo` - Set global tempo
- `fire_clip` - Trigger clip playback
- `start_playback` - Start playback
- `stop_playback` - Stop playback
- `start_recording` - Start recording
- `stop_recording` - Stop recording

## Exit Codes

| Code | Description |
|-------|-------------|
| 0 | Success (normal exit or Ctrl+C) |
| 1 | Rules file not found |
| 2 | Invalid polling rate (not 5-30 Hz) |
| 3 | Controller initialization failed |
| 4 | Rules file parsing failed |
| 5 | Rules engine error (connection to Ableton failed) |
| 6 | Unexpected error |

## Requirements

- Python 3.10+
- Ableton Live with Remote Script loaded on port 9877
- Rule configuration file (YAML format)

## Performance

**Target**: <100ms average latency (parameter read → action complete)

With proper network and Ableton configuration:
- Average latency: 20-50ms
- P99 latency: 50-100ms
- Polling rate: 10-15 Hz achievable

## Error Handling

The script handles:
- **Connection errors**: Reports connection failure, retries up to 3 times
- **Timeout errors**: Reports timeout, continues polling
- **Invalid rules**: Reports parsing errors with line numbers
- **Action execution failures**: Logs error, continues evaluating other rules
- **Keyboard interrupt**: Graceful shutdown with summary statistics

## Troubleshooting

**"Cannot connect to Ableton"**
- Verify Ableton Live is running
- Check Remote Script is loaded (Preferences → Link, Tempo & MIDI → Control Surface: AbletonMCP)
- Verify TCP port 9877 is not blocked by firewall

**"Latency too high (>100ms)"**
- Reduce polling rate (try 10 Hz instead of 15 Hz)
- Check network latency to Ableton (localhost should be <1ms)
- Verify Ableton session is not overloaded

**"No rules firing"**
- Check rule conditions match expected parameter values
- Enable verbose mode (`--verbose`) to see evaluation results
- Verify parameter reference format (`track:device:param`)

**"Rules oscillating (firing repeatedly)"**
- Increase cooldown (`--cooldown` not directly exposed, defaults to 0.5s)
- Modify rules to have wider trigger ranges
- Add hysteresis to conditions

## Examples

See `configs/analysis/` for complete examples:

1. **LUFS Compressor**: Automatically adjust volume based on loudness
2. **Peak Protection**: Emergency limit on excessive peaks
3. **Spectral Control**: Adjust processing based on spectral content
4. **Multi-Param Control**: Complex conditions with multiple parameters

## Integration with MCP

The script uses the PollingRulesEngine from `rules_engine.py`, which:
- Connects to Ableton Remote Script via TCP (port 9877)
- Polls parameters using `get_device_parameters` command
- Executes actions using MCP commands (set_volume, set_parameter, etc.)
- Manages rule cooldowns to prevent oscillation

## See Also

- `scripts/analysis/poll_plugin_params.py` - Parameter polling and logging
- `scripts/analysis/rules_engine.py` - Rule evaluation and action execution
- `scripts/analysis/rules_parser.py` - YAML rule configuration parsing
- `configs/analysis/` - Example rule configurations
