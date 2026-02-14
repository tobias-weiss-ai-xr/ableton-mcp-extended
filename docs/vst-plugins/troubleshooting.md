# VST Audio Analysis - Troubleshooting Guide

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues By Category](#common-issues-by-category)
3. [Installation Issues](#installation-issues)
4. [Configuration Issues](#configuration-issues)
5. [Runtime Issues](#runtime-issues)
6. [Performance Issues](#performance-issues)
7. [Plugin Issues](#plugin-issues)
8. [Ableton Integration Issues](#ableton-integration-issues)
9. [Debugging Checklist](#debugging-checklist)
10. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Run Diagnostic Checks

```bash
cd MCP_Server/audio_analysis

# 1. Test Python installation
python --version
# Should show Python 3.8+

# 2. Test module imports
python -c "import ableton_mcp_extended.audio_analysis; print('✓ OK')"

# 3. Run unit tests
python -m pytest tests/ -v
# Should show 76 passed

# 4. Run benchmarks
python benchmark_runner.py --duration 5
# Should complete without errors
```

### System Environment Check

```python
import sys
import platform
import psutil

print(f"Python: {sys.version}")
print(f"Platform: {platform.system()}")
print(f"CPU Count: {psutil.cpu_count()}")
print(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
print(f"Available: {psutil.virtual_memory().available / (1024**3):.1f} GB")
```

---

## Common Issues By Category

### Category 1: Import/Module Errors

**Symptom:**
```python
ModuleNotFoundError: No module named 'ableton_mcp_extended'
```

**Solutions:**

1. **Install in development mode:**
```bash
pip install -e .
```

2. **Check Python path:**
```bash
python -c "import sys; print(sys.path)"
# Should include repository root
```

3. **Verify installation:**
```bash
pip list | grep ableton-mcp
```

---

### Category 2: Dependency Errors

**Symptom:**
```python
ModuleNotFoundError: No module named 'yaml'
ImportError: cannot import name 'psutil'
```

**Solutions:**

1. **Install dependencies:**
```bash
pip install PyYAML psutil
```

2. **Check installed packages:**
```bash
pip list | grep -E "PyYAML|psutil"
```

3. **Upgrade if outdated:**
```bash
pip install --upgrade PyYAML psutil
```

---

### Category 3: Polling Errors

**Symptom:**
```python
RuntimeError: Poller already running
RuntimeError: Poller not running
```

**Solutions:**

1. **Check poller state:**
```python
from ableton_mcp_extended.audio_analysis.polling import ThreadPoller, AudioMetric

poller = ThreadPoller([AudioMetric(...)])
print(f"Running: {poller.is_running()}")

if not poller.is_running():
    poller.start()
```

2. **Stop before restarting:**
```python
if poller.is_running():
    poller.stop()
    # Give it time to stop
    import time
    time.sleep(0.1)

poller.start()
```

---

### Category 4: Value Errors

**Symptom:**
```python
ValueError: Invalid operator 'GREATERTHAN'
ValueError: target_rate_hz must be positive
```

**Solutions:**

1. **Check operator syntax:**
```yaml
# Wrong
operator: "GREATERTHAN"

# Correct
operator: ">"
```

2. **Check数值范围:**
```python
# Wrong
poller = ThreadPoller(metrics, target_rate_hz=-10)

# Correct
poller = ThreadPoller(metrics, target_rate_hz=20)  # Must be positive
```

---

## Installation Issues

### Issue 1: pip install fails

**Symptom:**
```bash
ERROR: Could not find a version that satisfies the requirement ableton-mcp-extended
```

**Solution:** Install from local repository:
```bash
cd /path/to/ableton-mcp-extended
pip install -e .
```

---

### Issue 2: Permission denied

**Symptom:**
```bash
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use user install:**
```bash
pip install --user -e .
```

2. **Use virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

---

### Issue 3: Python version mismatch

**Symptom:**
```bash
ERROR: Python 3.7 is not supported
```

**Solution:** Upgrade to Python 3.8+
```bash
# Install Python 3.10 from python.org
# Or use pyenv (Linux/macOS)
pyenv install 3.10.0
pyenv global 3.10.0
```

---

## Configuration Issues

### Issue 1: Metric name mismatch

**Symptom:**
```python
KeyError: 'loudness '
```
**Cause:** Extra space in metric name

**Solution:**
```python
from ableton_mcp_extended.audio_analysis.polling import AudioMetric

# Wrong
metric = AudioMetric(..., name="loudness ")

# Correct
metric = AudioMetric(..., name="loudness")
```

---

### Issue 2: Wrong parameter index

**Symptom:**
```python
Values always return 0.0 or None
```

**Solutions:**

1. **Verify parameter index:**
   - Open Ableton Live
   - Double-click device to see parameter list
   - Count parameters from 0 (leftmost = 0)

2. **Test with known working parameter:**
```python
# Try parameter 0 (usually first parameter)
metric = AudioMetric(track_index=0, device_index=0, parameter_index=0, name="test")
```

3. **Consult plugin documentation:**
   - Check `docs/vst-plugins/parameter_mappings.md`
   - Plugin manual may list parameter indices

---

### Issue 3: YAML parse error

**Symptom:**
```python
yaml.YAMLError: while parsing a flow sequence
```

**Solution:**
Check YAML syntax:
```yaml
# Wrong
rules: [ {name: "rule1", condition: {metric: "loudness", operator: ">", threshold: 0.8} } ]

# Correct
rules:
  - name: "rule1"
    condition:
      metric: "loudness"
      operator: ">"
      threshold: 0.8
```

Use online YAML validator: https://www.yamllint.com/

---

## Runtime Issues

### Issue 1: Poller returns no values

**Symptom:**
```python
poller.get_values() == {}
```

**Root Causes:**
1. Ableton not running
2. Wrong session loaded
3. Plugin not inserted
4. Parameter index incorrect

**Debug Steps:**

1. **Check Ableton connection:**
```python
# Assuming MCP server is running
# Try to query session
try:
    session_info = get_session_info()
    print(f"Ableton connected: {len(session_info['tracks'])} tracks")
except:
    print("Unable to connect to Ableton")
```

2. **Verify session:**
```python
session_info = get_session_info()
if len(session_info['tracks']) == 0:
    print("No tracks in session")
```

3. **Verify device:**
```python
track_info = get_track_info(track_index=0)
if len(track_info['devices']) == 0:
    print("No devices on track 0")
```

---

### Issue 2: Rules not triggering

**Symptom:** Conditions met, but no actions execute

**Debug Steps:**

1. **Verify rule loaded:**
```python
from ableton_mcp_extended.audio_analysis.rules import RuleEngine

engine = RuleEngine.from_file("rules.yaml")
print(f"Rules loaded: {engine.get_rule_names()}")
```

2. **Test condition directly:**
```python
values = {"loudness": 0.9}
actions = engine.evaluate(values)
print(f"Triggered actions: {actions}")
```

3. **Check threshold values:**
```yaml
# Verify threshold is in correct range (0.0-1.0 for normalized)
condition:
  metric: "loudness"
  operator: ">"
  threshold: 0.8  # Should be 0.0-1.0
```

---

### Issue 3: Control loop stops unexpectedly

**Symptom:** Loop runs for a few seconds, then stops

**Root Causes:**
1. Unhandled exception
2. Poller stopped
3. System resource exhaustion

**Debug Steps:**

1. **Check for exceptions:**
```python
def action_handler(action):
    try:
        # Process action
        print(action)
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

loop.start(action_handler)
```

2. **Monitor poller:**
```python
import time
while loop.is_running():
    print(f"Poller running: {poller.is_running()}")
    print(f"Values: {poller.get_values()}")
    time.sleep(1)
```

3. **Check system resources:**
```bash
# Monitor memory
watch -n 1 'free -m'  # Linux
# or
python -c "import psutil; print(psutil.virtual_memory())"
```

---

## Performance Issues

### Issue 1: Polling rate too low

**Symptom:** Actual rate <90% of target

**Benchmark Test:**
```bash
python benchmark_runner.py --type polling --duration 10
```

**Solutions:**

1. **Reduce target rate:**
```python
# Before: 30 Hz
poller = ThreadPoller(metrics, target_rate_hz=30)

# After: 20 Hz
poller = ThreadPoller(metrics, target_rate_hz=20)
```

2. **Reduce number of metrics:**
```python
# Before: 10 metrics
metrics = [metric1, metric2, ..., metric10]

# After: 3 metrics
metrics = [metric1, metric2, metric3]
```

3. **Check system load:**
```bash
top  # Linux/macOS
Task Manager  # Windows
```

---

### Issue 2: High CPU usage

**Symptom:** CPU usage >70%

**Benchmark Test:**
```bash
python benchmark_runner.py --type cpu --duration 10
```

**Solutions:**

1. **Reduce polling rate** (most effective)
2. **Simplify rules**
3. **Close other applications**
4. **Use faster hardware**

---

### Issue 3: High latency

**Symptom:** E2E latency >2× polling interval

**Benchmark Test:**
```bash
python benchmark_runner.py --type latency --iterations 100
```

**Solutions:**

1. **Profile rule evaluation:**
```bash
python benchmark_runner.py --type rules --iterations 1000
```

2. **Optimize action handler:**
```python
# Avoid blocking operations
def action_handler(action):
    # Fast: Queue for background processing
    action_queue.put(action)

    # Slow: File I/O, network calls, etc.
    # with open("log.txt", "a") as f:
    #     f.write(str(action))
```

---

## Plugin Issues

### Issue 1: Plugin parameter not accessible

**Symptom:** Querying parameter always returns None or 0.0

**Root Causes:**
1. Plugin doesn't expose parameter to host
2. Plugin parameters are automation-inaccessible
3. Wrong parameter index

**Debug Steps:**

1. **Test in Ableton UI:**
   - Open device panel
   - Verify parameter is visible
   - Try to automate parameter manually

2. **Check plugin documentation:**
   - Read plugin manual
   - Confirm parameters are automatable

3. **Try different parameter:**
```python
# Test parameter 0 (usually volume or main control)
metric = AudioMetric(track_index=0, device_index=0, parameter_index=0, name="test")
```

---

### Issue 2: Plugin crashes when queried

**Symptom:** Ableton crashes or becomes unresponsive

**Root Causes:**
1. Plugin bug
2. Incompatible plugin version
3. System incompatibility

**Solutions:**

1. **Test plugin standalone:**
   - Use plugin in DAW without this system
   - Verify plugin is stable

2. **Update plugin:**
   - Check for updates from developer
   - Install latest version

3. **Try alternative plugin:**
   - Use recommended plugins from Task 1
   - See `docs/vst-plugins/installation_guide.md`

---

### Issue 3: Values out of expected range

**Symptom:** Values return outside 0.0-1.0 (for normalized)

**Root Cause:** Plugin uses unnormalized values

**Solution:**

1. **Adjust metric range:**
```python
# If plugin returns LUFS (-60 to 0)
metric = AudioMetric(
    ...,
    name="loudness",
    min_value=-60.0,  # Adjusted
    max_value=0.0    # Adjusted
)
```

2. **Normalize in code:**
```python
def normalize_lufs(lufs_value):
    """Convert LUFS to 0-1 scale."""
    return (lufs_value + 60) / 60
```

---

## Ableton Integration Issues

### Issue 1: Cannot connect to Ableton

**Symptom:** `Timeout waiting for Ableton connection`

**Debug Steps:**

1. **Verify Ableton is running:**
   - Check Ableton Live is open
   - Verify session is loaded

2. **Check Remote Script API:**
   - Preferences → MIDI → Remote Scripts
   - Verify script is installed

3. **Test connection manually:**
```python
# Assuming MCP server is configured
try:
    session = get_session_info()
    print("Connected")
except:
    print("Not connected")
```

---

### Issue 2: Wrong track/device index

**Symptom:** Getting values from wrong track or device

**Debug Steps:**

1. **List all tracks:**
```python
session = get_session_info()
for i, track in enumerate(session['tracks']):
    print(f"Track {i}: {track['name']}")
```

2. **List all devices on track:**
```python
track_info = get_track_info(track_index=0)
for i, device in enumerate(track_info['devices']):
    print(f"Device {i}: {device['name']}")
```

3. **Correct indices:**
```python
# Based on output above
track_index = 0     # Update with correct track
device_index = 1    # Update with correct device
```

---

### Issue 3: Session changes break system

**Symptom:** Works initially, stops after changing session

**Root Cause:** Track/device indices changed

**Solution:**

1. **Stop poller before session change:**
```python
poller.stop()

# Change session...

# Restart with new indices
poller.start()
```

2. **Use track/device names instead of indices** (advanced):
```python
# Find track by name
session = get_session_info()
track_index = next((i for i, t in enumerate(session['tracks']) if t['name'] == "Bass"), None)
```

---

## Debugging Checklist

### Before Reporting Issue

- [ ] Python version ≥ 3.8
- [ ] Dependencies installed: `pip install PyYAML psutil`
- [ ] Repository cloned and installed: `pip install -e .`
- [ ] Ableton Live running with session loaded
- [ ] VST plugin inserted on track
- [ ] Unit tests pass: `pytest tests/`
- [ ] Benchmarks run without errors
- [ ] Checked error messages in console
- [ ] Tried basic example from documentation
- [ ] Reviewed relevant documentation sections

### Diagnostic Information Collection

```python
import sys
import platform
import ableton_mcp_extended.audio_analysis as aa

print("=" * 60)
print("VST Audio Analysis - Diagnostic Information")
print("=" * 60)
print()

print("System:")
print(f"  Python: {sys.version}")
print(f"  Platform: {platform.system()} {platform.release()}")
print(f"  Architecture: {platform.machine()}")
print()

print("Module:")
print(f"  Version: {aa.__version__ if hasattr(aa, '__version__') else 'Unknown'}")
print(f"  Path: {aa.__file__}")
print()

print("Dependencies:")
try:
    import yaml
    print(f"  PyYAML: {yaml.__version__}")
except ImportError:
    print("  PyYAML: NOT INSTALLED")

try:
    import psutil
    print(f"  psutil: {psutil.__version__}")
except ImportError:
    print("  psutil: NOT INSTALLED")
print()

print("=" * 60)
```

---

## Getting Help

### Documentation Resources

1. **User Guide** - `docs/vst-plugins/user_guide.md`
2. **API Reference** - `docs/vst-plugins/api_reference.md`
3. **Rule Configuration** - `docs/vst-plugins/rule_configuration.md`
4. **CLI Monitor** - `docs/vst-plugins/cli_monitor.md`
5. **Benchmark Guide** - `docs/vst-plugins/benchmark_execution.md`
6. **Plugin Installation** - `docs/vst-plugins/installation_guide.md`

### Code Examples

- `MCP_Server/audio_analysis/example_control_loop.py`
- `MCP_Server/audio_analysis/example_cli_monitor.py`
- `MCP_Server/audio_analysis/example_benchmarks.py`
- `MCP_Server/audio_analysis/example_rules.yaml`

### Unit Tests

Run tests for usage examples:
```bash
cd MCP_Server/audio_analysis
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_polling.py -v

# Specific test
python -m pytest tests/test_rules.py::test_rule_evaluation -v
```

### Issue Reporting Format

When reporting issues, include:

```
**Issue Summary:**
[One-sentence description]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Messages:**
[Paste error messages or stack traces]

**Environment:**
- OS: [Windows/macOS/Linux]
- Python: [3.x.x]
- Ableton Live: [11.x / 12.x]
- VST Plugin: [Name and version]

**Diagnostic Output:**
[Output from diagnostic script above]

**Additional Context:**
[Any additional information]
```

---

## Contact & Support

### Self-Service

1. Search existing documentation
2. Review unit tests for examples
3. Run benchmarks to identify issues
4. Check troubleshooting checklist

### Community

- GitHub Issues: [repository URL]/issues
- Discussions: [repository URL]/discussions

### Professional Support

If you require professional support:
- Contact repository maintainers
- Provide full diagnostic information
- Include reproduction steps

---

**Last Updated:** 2025-01-20
**Document Version:** 1.0