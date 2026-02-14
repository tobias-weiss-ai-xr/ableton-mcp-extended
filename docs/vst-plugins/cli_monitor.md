# VST Audio Analysis - CLI Monitor Guide

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Display Layout](#display-layout)
4. [Configuration Options](#configuration-options)
5. [Monitoring Scenarios](#monitoring-scenarios)
6. [Event System](#event-system)
7. [Integration Examples](#integration-examples)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The CLI Monitor (`CLIMonitor`) provides real-time terminal-based visualization of audio metrics and system state. It runs in a background thread and updates the display at configurable intervals.

**Key Features:**
- ✅ Real-time metric values (up to 30 Hz refresh)
- ✅ Historical statistics (min, max, average)
- ✅ System status (polling rate, threads)
- ✅ Event log with timestamps
- ✅ Thread-safe background execution
- ✅ Graceful shutdown

---

## Getting Started

### Basic Usage

```python
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

# Define metrics
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index=0, device_index=0, parameter_index=6, name="spectral_centroid")
]

# Create poller
poller = ThreadPoller(metrics, target_rate_hz=20)

# Create monitor
monitor = CLIMonitor(poller, update_interval_sec=0.2)

# Start monitoring
monitor.start()

# Monitor runs in background...
# Continue with other work

# Stop when done
monitor.stop()
```

### Running with Interrupt Handling

```python
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=20)
monitor = CLIMonitor(poller, update_interval_sec=0.2)

# Add startup event
monitor.add_event("Monitoring started")

# Start
monitor.start()

# Wait for Ctrl+C
monitor.wait_for_interrupt()

# Stop
monitor.stop()
print("Monitoring stopped")
```

---

## Display Layout

### Full Display Structure

```
╔══════════════════════════════════════════════════════╗
║  VST Audio Analysis Monitor                          ║
╠══════════════════════════════════════════════════════╣
║  Metrics:                                            ║
║  • loudness        0.85  [0.00 - 1.00]  T: 14:23:45 ║
║  • spectral_cntrd  0.62  [0.00 - 1.00]  T: 14:23:45 ║
╠══════════════════════════════════════════════════════╣
║  Statistics:                                         ║
║  • loudness        min:0.42  max:0.89  avg:0.68     ║
║  • spectral_cntrd  min:0.31  max:0.75  avg:0.54     ║
╠══════════════════════════════════════════════════════╣
║  System:                                             ║
║  • Polling Rate   20.0 Hz                           ║
║  • Threads        3 active                          ║
║  • Uptime         00:00:15                          ║
╠══════════════════════════════════════════════════════╣
║  Events:                                             ║
║  [14:23:30] Monitoring started                      ║
║  [14:23:35] High loudness detected (>0.8)           ║
║  [14:23:40] Peak warning: 0.96                      ║
╠══════════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                               ║
╚══════════════════════════════════════════════════════╝
```

### Section Breakdown

#### 1. Header
- Shows application name
- Fixed at top of display

#### 2. Metrics Section
- Lists all metrics being polled
- Shows: `name  current_value  [min_value - max_value]  timestamp`
- Updates real-time

#### 3. Statistics Section
- Calculated from collected samples
- Shows: min, max, average
- Optional (can be disabled)

#### 4. System Section
- Polling rate
- Active thread count
- Uptime (running time)
- Updates periodically

#### 5. Events Section
- Timestamped event messages
- Most recent at top
- Auto-scrolls to newest

#### 6. Footer
- Instruction to stop (Ctrl+C)
- Fixed at bottom

---

## Configuration Options

### Constructor Parameters

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
| `poller` | `ThreadPoller` | - | Poller to monitor (required) |
| `update_interval_sec` | `float` | `0.2` | Display refresh interval in seconds |
| `show_timestamps` | `bool` | `True` | Show last update timestamps |
| `show_statistics` | `bool` | `True` | Show min/max/avg statistics |

### Update Interval

**Update interval** controls how often the display refreshes:

| Setting | Refresh Rate | Use Case |
|---------|--------------|----------|
| `0.1` (100ms) | 10 Hz | High-frequency monitoring |
| `0.2` (200ms) | 5 Hz | Standard use (default) |
| `0.5` (500ms) | 2 Hz | Resource-constrained |
| `1.0` (1000ms) | 1 Hz | Minimal updates |

**Note:** Display refresh is independent of polling rate. You can poll at 20 Hz but refresh at 5 Hz.

### Show Timestamps

When `True` (default):
```
• loudness  0.85  [0.00 - 1.00]  T: 14:23:45
```

When `False`:
```
• loudness  0.85  [0.00 - 1.00]
```

### Show Statistics

When `True` (default):
```
Statistics:
  • loudness        min:0.42  max:0.89  avg:0.68
  • spectral_cntrd  min:0.31  max:0.75  avg:0.54
```

When `False`:
```
Statistics: (disabled)
```

---

## Monitoring Scenarios

### Scenario 1: Single Metric - Loudness

```python
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

# Single metric
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")
]

poller = ThreadPoller(metrics, target_rate_hz=10)
monitor = CLIMonitor(poller, update_interval_sec=0.2)

monitor.add_event("Loudness monitoring started")
monitor.start()

monitor.wait_for_interrupt()
monitor.stop()
```

**Display:**
```
╔══════════════════════════════════════════════════════╗
║  VST Audio Analysis Monitor                          ║
╠══════════════════════════════════════════════════════╣
║  Metrics:                                            ║
║  • loudness        0.85  [0.00 - 1.00]  T: 14:23:45 ║
╠══════════════════════════════════════════════════════╣
║  Statistics:                                         ║
║  • loudness        min:0.42  max:0.89  avg:0.68     ║
╠══════════════════════════════════════════════════════╣
║  System:                                             ║
║  • Polling Rate   10.0 Hz                           ║
║  • Threads        2 active                          ║
╠══════════════════════════════════════════════════════╣
║  Events:                                             ║
║  [14:23:30] Loudness monitoring started              ║
╚══════════════════════════════════════════════════════╝
```

---

### Scenario 2: Multi-Metric - Full Analysis

```python
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index=0, device_index=0, parameter_index=6, name="spectral_centroid"),
    AudioMetric(track_index=0, device_index=0, parameter_index=7, name="peak"),
    AudioMetric(track_index=0, device_index=0, parameter_index=8, name="dynamic_range")
]

poller = ThreadPoller(metrics, target_rate_hz=20)
monitor = CLIMonitor(poller, update_interval_sec=0.1)  # Faster refresh

# Add events
monitor.add_event("Full mix analysis started")
monitor.add_event("Monitoring 4 metrics at 20 Hz")

monitor.start()
monitor.wait_for_interrupt()
monitor.stop()
```

---

### Scenario 3: Minimal Display

```python
# Disable timestamps and statistics
monitor = CLIMonitor(
    poller=poller,
    update_interval_sec=0.5,  # Slower refresh
    show_timestamps=False,
    show_statistics=False
)

monitor.add_event("Minimal monitoring mode")
monitor.start()
```

**Display:**
```
╔══════════════════════════════════════════════════════╗
║  VST Audio Analysis Monitor                          ║
╠══════════════════════════════════════════════════════╣
║  Metrics:                                            ║
║  • loudness        0.85  [0.00 - 1.00]               ║
║  • spectral_cntrd  0.62  [0.00 - 1.00]               ║
╠══════════════════════════════════════════════════════╣
║  Statistics: (disabled)                              ║
╠══════════════════════════════════════════════════════╣
║  System:                                             ║
║  • Polling Rate   20.0 Hz                           ║
║  • Threads        3 active                          ║
╠══════════════════════════════════════════════════════╣
║  Events:                                             ║
║  [14:23:30] Minimal monitoring mode                  ║
╠══════════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                               ║
╚══════════════════════════════════════════════════════╝
```

---

### Scenario 4: Background Monitoring with Control Loop

```python
from ableton_mcp_extended.audio_analysis.control_loop import ControlLoop
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

# Setup
metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=20)
rule_engine = RuleEngine.from_file("rules.yaml")

# Create monitor (runs in background)
monitor = CLIMonitor(poller, update_interval_sec=0.2)
monitor.add_event("Control loop + monitor started")

# Create control loop
loop = ControlLoop(poller, rule_engine, poll_rate_hz=20)

# Start both
monitor.start()
loop.start(lambda action: print(f"Action: {action}"))

# Run for 60 seconds
import time
time.sleep(60)

# Stop both
loop.stop()
monitor.stop()
```

---

### Scenario 5: High-Frequency Updates (Performance Test)

```python
# Fast polling + fast display
metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=30)
monitor = CLIMonitor(poller, update_interval_sec=0.1)

monitor.add_event("High-frequency monitoring (30 Hz)")
monitor.start()

# Monitor CPU usage in another terminal
# Monitor runs for 10 seconds
time.sleep(10)

monitor.stop()
monitor.add_event("Test complete")
```

---

## Event System

### Adding Events

Events are timestamped messages displayed in the Events section.

```python
monitor.add_event("Monitoring started")
```

**Output:**
```
Events:
  [14:23:30] Monitoring started
```

**Rich Event Messages:**
```python
import datetime

monitor.add_event(f"Session started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
monitor.add_event("Loaded 3 metrics")
monitor.add_event("Polling at 20 Hz")
monitor.add_event("Threshold: loudness > 0.8")
monitor.add_event(f"Loudness range: 0.0 - 1.0")
```

**Condition-Based Events:**
```python
# Manual condition checking
while monitor.is_running():
    values = poller.get_values()
    if values["loudness"] > 0.8:
        monitor.add_event(f"High loudness: {values['loudness']:.2f}")
    time.sleep(0.5)
```

### Clearing Events

```python
# Clear all events
monitor.clear_events()

# Add new event
monitor.add_event("Events cleared, new session starting")
```

### Event Management

**Best Practices:**
1. Add descriptive events:
   ```python
   monitor.add_event("Configuration loaded: rules.yaml")
   monitor.add_event("Peak protection enabled")
   ```

2. Document state changes:
   ```python
   monitor.add_event("Gain reduction active")
   monitor.add_event("Gain normalized")
   ```

3. Limit event count (auto-scrolls to newest):
   ```python
   # Events automatically scroll, keep most recent ~10
   ```

---

## Integration Examples

### Example 1: Monitor + Control Loop

```python
from ableton_mcp_extended.audio_analysis.control_loop import ControlLoop
from ableton_mcp_extended.audio_analysis.rules import RuleEngine
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

# Setup
metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=20)
rule_engine = RuleEngine.from_file("rules.yaml")

# Create monitor
monitor = CLIMonitor(poller, update_interval_sec=0.2)
monitor.add_event("Control loop + monitor integration")
monitor.add_event(f"Loaded {len(rule_engine.get_rule_names())} rules")

# Create loop
loop = ControlLoop(poller, rule_engine, poll_rate_hz=20)

# Action handler that also monitors events
def action_handler(action):
    if action["type"] == "log":
        monitor.add_event(f"Rule triggered: {action['message']}")

# Start both
monitor.start()
loop.start(action_handler)

# Run
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
    loop.stop()
    monitor.stop()
```

---

### Example 2: Monitor + Alert Notification

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(message):
    # Email configuration
    sender = "alert@studio.com"
    receiver = "producer@studio.com"

    msg = MIMEText(message)
    msg["Subject"] = "VST Audio Alert"
    msg["From"] = sender
    msg["To"] = receiver

    # Send email (pseudo-code)
    # with smtplib.SMTP("smtp.server.com") as server:
    #     server.send_message(msg)

# Monitor
metrics = [AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness")]
poller = ThreadPoller(metrics, target_rate_hz=10)
monitor = CLIMonitor(poller, update_interval_sec=0.5)

# Background thread for threshold detection
def alert_thread():
    last_alert_time = 0
    while monitor.is_running():
        values = poller.get_values()
        current_time = time.time()

        if values["loudness"] > 0.9 and (current_time - last_alert_time > 60):
            alert_msg = f"High loudness alert: {values['loudness']:.2f}"
            monitor.add_event(f"📧 Email sent: {alert_msg}")
            # send_email_alert(alert_msg)  # Uncomment to enable
            last_alert_time = current_time

        time.sleep(1)

import threading
alert_thread_obj = threading.Thread(target=alert_thread, daemon=True)

monitor.add_event("Alert system active")
monitor.start()
alert_thread_obj.start()

monitor.wait_for_interrupt()
monitor.stop()
```

---

### Example 3: Monitor + Data Logging

```python
import csv
from datetime import datetime

# Setup logging
log_file = open("audio_analysis_log.csv", "w", newline="")
csv_writer = csv.writer(log_file)
csv_writer.writerow(["timestamp", "loudness", "spectral_centroid", "peak"])

# Metrics
metrics = [
    AudioMetric(track_index=0, device_index=0, parameter_index=5, name="loudness"),
    AudioMetric(track_index=0, device_index=0, parameter_index=6, name="spectral_centroid"),
    AudioMetric(track_index=0, device_index=0, parameter_index=7, name="peak")
]
poller = ThreadPoller(metrics, target_rate_hz=20)
monitor = CLIMonitor(poller, update_interval_sec=0.5)

# Background thread for logging
def logging_thread():
    while monitor.is_running():
        values = poller.get_values()
        timestamp = datetime.now().isoformat()
        csv_writer.writerow([
            timestamp,
            values["loudness"],
            values["spectral_centroid"],
            values["peak"]
        ])
        csv_writer.flush()
        time.sleep(0.1)  # Log at 10 Hz

import threading

monitor.add_event("Data logging started")
monitor.add_event(f"Log file: audio_analysis_log.csv")
monitor.start()

logging_thread_obj = threading.Thread(target=logging_thread, daemon=True)
logging_thread_obj.start()

monitor.wait_for_interrupt()
monitor.stop()
log_file.close()
monitor.add_event("Log file closed")
```

---

### Example 4: Custom Display Layout

```python
from ableton_mcp_extended.audio_analysis.cli_monitor import CLIMonitor

# Create custom monitor by subclassing
class CustomCLIMonitor(CLIMonitor):
    def _render_display(self) -> str:
        """Override to customize display layout."""
        values = self.poller.get_values()

        # Custom header
        lines = [
            "=" * 60,
            "🎵 AUDIO ANALYSIS 🎵",
            "=" * 60,
        ]

        # Custom metrics section
        lines.append("\nMetrics:")
        for name, value in values.items():
            bar = "█" * int(value * 20)  # 20-character bar
            lines.append(f"  {name:15} {value:05.2f} {bar}")

        # Custom footer
        lines.append("\n" + "=" * 60)
        lines.append(f"Updating every {self.update_interval_sec}s")
        lines.append("Press Ctrl+C to stop")
        lines.append("=" * 60)

        return "\n".join(lines)

# Use custom monitor
monitor = CustomCLIMonitor(poller, update_interval_sec=0.2)
monitor.start()
```

---

## Keyboard Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+C` | Stop | Gracefully stop monitor and poller |

**Note:** Monitor automatically catches `KeyboardInterrupt` and shuts down cleanly.

---

## Troubleshooting

### Issue: Display Not Updating

**Symptom:** Metrics section shows stale values

**Causes:**
1. Poller not started
2. Update interval too long
3. Thread blocked

**Solutions:**
```python
# 1. Verify poller is running
poller.start()
print(f"Poller running: {poller.is_running()}")

# 2. Reduce update interval
monitor = CLIMonitor(poller, update_interval_sec=0.1)

# 3. Check for blocking operations
# Avoid sleep() or I/O in monitor thread
```

---

### Issue: Display Garbled

**Symptom:** Display shows overlapping text or artifacts

**Cause:** Terminal width too narrow

**Solution:** Use wider terminal (minimum 80 characters)

---

### Issue: Statistics Not Updating

**Symptom:** Min/max/avg values don't change

**Cause:** `show_statistics=False` or samples not collected

**Solution:**
```python
# Enable statistics
monitor = CLIMonitor(poller, show_statistics=True)

# Verify poller has samples
for metric_name in poller.get_all_metrics():
    count = poller.get_sample_count(metric_name)
    print(f"{metric_name}: {count} samples")
```

---

### Issue: Events Not Showing

**Symptom:** Events section remains empty

**Cause:** Not calling `add_event()`

**Solution:**
```python
# Always add initial event
monitor.add_event("Monitor started")

# Add events from action handler
def action_handler(action):
    monitor.add_event(f"Action: {action}")
```

---

### Issue: CPU Usage High

**Symptom:** Monitor consumes too much CPU

**Causes:**
- Polling rate too high
- Update interval too short
- Too many metrics

**Solutions:**
```python
# Reduce polling rate
poller = ThreadPoller(metrics, target_rate_hz=10)  # Was 20

# Increase update interval
monitor = CLIMonitor(poller, update_interval_sec=0.5)  # Was 0.1

# Reduce metrics
metrics = metrics[:2]  # Monitor fewer metrics
```

---

### Issue: Ctrl+C Doesn't Stop

**Symptom:** Pressing Ctrl+C doesn't exit

**Cause:** Blocking operation in main thread

**Solution:**
```python
# Correct: Use wait_for_interrupt()
monitor.start()
monitor.wait_for_interrupt()  # Blocks until Ctrl+C
monitor.stop()

# Wrong: Manual KeyboardInterrupt handling (try/except already handles it)
```

---

### Issue: Error During Start

**Symptom:** Exception when calling `monitor.start()`

**Common Errors:**
```python
# Error: poller not initialized
monitor = CLIMonitor(None)  # Wrong!
monitor.start()  # TypeError

# Fix: Provide valid poller
monitor = CLIMonitor(poller)
monitor.start()
```

---

### Issue: Values Always 0.0

**Symptom:** All metrics show 0.0

**Cause:** Wrong parameter indices or plugin not exposing parameters

**Solutions:**
```python
# 1. Verify parameter indices
# Check parameter_mappings.md

# 2. Verify plugin exposes parameters
# Use Ableton's Device parameter browser

# 3. Test with mock values
print(f"Poller values: {poller.get_values()}")
```

---

## Performance Tips

### 1. Optimize Update Interval

Match update interval to your polling rate:

```python
# Polling at 20 Hz? Update at 5 Hz
poller = ThreadPoller(metrics, target_rate_hz=20)
monitor = CLIMonitor(poller, update_interval_sec=0.2)  # 5 Hz
```

### 2. Limit Display Width

Metrics with long names make display wide:

```python
# Good: Short names
metrics = [
    AudioMetric(..., name="loudness"),
    AudioMetric(..., name="spectral")
]

# Avoid: Long names
metrics = [
    AudioMetric(..., name="integrated_loudness_in_lufs"),  # Too long!
    AudioMetric(..., name="spectral_centroid_value")
]
```

### 3. Disable Unused Features

```python
# Minimal mode if slow system
monitor = CLIMonitor(
    poller,
    update_interval_sec=1.0,
    show_timestamps=False,
    show_statistics=False
)
```

---

## See Also

- [API Reference - CLIMonitor](api_reference.md#module-cli_monitor)
- [User Guide - Quick Start](user_guide.md#quick-start)
- [Control Loop Guide](control_loop.md)