# Task 3 Testing Guide - VST Plugin Parameter Exposure

## Purpose

This guide walks you through manually testing which parameters are exposed by recommended VST plugins in Ableton Live.

**Estimated Time:** 30-60 minutes

---

## Prerequisites

1. Ableton Live 11+ installed and running
2. MCP Remote Script configured and connected
3. Python environment with ableton-mcp-extended installed

---

## Step 1: Install Recommended Plugins

From Task 1 research, the following plugins were identified:

### 1. MAnalyzer by MeldaProduction
- **Download:** https://www.meldaproduction.com/MAnalyzer
- **License:** Free
- **Purpose:** Multi-band spectrum analyzer with loudness meters

### 2. Voxengo SPAN
- **Download:** https://www.voxengo.com/product/span/
- **License:** Freeware
- **Purpose:** Spectrum analyzer with stereo field analysis

### 3. Youlean Loudness Meter 2
- **Download:** https://youlean.co/youlean-loudness-meter-2/
- **License:** Free
- **Purpose:** EBU R128 loudness metering (LUFS)

---

## Step 2: Create Test Session

### Using MCP Tools:

```python
import socket
import json

def send_command(command_type, params=None):
    """Send command to Ableton MCP server (TCP, port 9877)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 9877))

    command = {
        'type': command_type,
        'params': params or {}
    }

    sock.send(json.dumps(command).encode('utf-8'))
    response = sock.recv(8192).decode('utf-8')
    sock.close()

    return json.loads(response)

# Create audio track for testing
result = send_command('create_audio_track', {'index': -1})
print(f"Created audio track: {result}")
```

### Or manually in Ableton:
1. Create a new audio track
2. Add some audio (loop, sample, or microphone input)
3. Ensure audio is audible (playback test)

---

## Step 3: Load Plugin and Get Parameters

### Load Plugin using MCP:

```python
# Load MAnalyzer on track 0
result = send_command('load_instrument_or_effect', {
    'track_index': 0,
    'uri': 'plugins/MAnalyzer'  # Actual URI may vary
})

print(f"Loaded plugin: {result}")
```

### Load Plugin manually in Ableton:
1. Click on Device Browser
2. Navigate to Plugins → Audio Effects → Analysis
3. Drag MAnalyzer onto track 0

---

## Step 4: Discover Parameters

### Method A: Using MCP Tool (Recommended)

```python
# Get all parameters for device 0 on track 0
result = send_command('get_device_parameters', {
    'track_index': 0,
    'device_index': 0
})

if result.get('success'):
    parameters = result.get('parameters', [])
    print(f"\nTotal parameters found: {len(parameters)}\n")

    # Print parameter table
    print(f"{'Index':<8} {'Name':<40} {'Value':<10} {'Min':<10} {'Max':<10}")
    print("-" * 90)

    for param in parameters:
        index = param.get('index')
        name = param.get('name', 'Unknown')
        value = param.get('value', 0.0)
        min_val = param.get('min', 0.0)
        max_val = param.get('max', 1.0)

        print(f"{index:<8} {name:<40} {value:<10.4f} {min_val:<10.4f} {max_val:<10.4f}")
else:
    print(f"Error: {result.get('error')}")
```

### Method B: Using Ableton UI

1. Click on the plugin device to select it
2. Look at the **Configuration** button (top-left of device)
3. Click to open device parameters
4. Identify which parameters are exposed for automation

---

## Step 5: Test Parameter Responsiveness

### Real-time Monitoring Script

```python
import time
import socket
import json

def send_command(command_type, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 9877))
    command = {'type': command_type, 'params': params or {}}
    sock.send(json.dumps(command).encode('utf-8'))
    response = json.loads(sock.recv(8192).decode('utf-8'))
    sock.close()
    return response

# Test parameter indices (update based on Step 4 discovery)
TEST_PARAMS = [5, 6, 7, 8]  # Example indices - replace with actual discovered indices

print("Starting parameter monitoring (Ctrl+C to stop)...")
print(f"Monitoring parameters: {TEST_PARAMS}")
print("-" * 80)

try:
    while True:
        # Get all parameters
        result = send_command('get_device_parameters', {
            'track_index': 0,
            'device_index': 0
        })

        if result.get('success'):
            params = result.get('parameters', [])

            # Extract test parameters
            values = {}
            for param in params:
                if param.get('index') in TEST_PARAMS:
                    values[param['index']] = param.get('value', 0.0)

            # Print row
            row = []
            for idx in TEST_PARAMS:
                row.append(f"{values.get(idx, 0.0):.4f}")

            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] " + " | ".join(row))

        time.sleep(0.1)  # 10 Hz polling

except KeyboardInterrupt:
    print("\nMonitoring stopped.")
```

### Testing Procedure:

1. Run the monitoring script
2. Play audio in Ableton (loop, track, or live input)
3. Vary the audio characteristics:
   - **Volume changes:** Play quiet vs loud audio
   - **Frequency sweeps:** Use synth oscillator sweep from low to high
   - **Stereo:** Move sound from left to right
   - **Dynamics:** Play percussive vs sustained sounds
4. Observe which parameters change
5. Correlate parameter changes with audio changes

---

## Step 6: Analyze Parameter Mappings

### For Each Plugin, Document:

| Parameter Index | Name | Min | Max | Audio Characteristic | Observed Behavior |
|-----------------|------|-----|-----|---------------------|-------------------|
| 5 | Loudness (LUFS) | -60 | 0 | Overall volume | Changes with fader |
| 6 | Spectral Centroid | 0 | 1 | Brightness | Increases with high frequencies |
| ... | ... | ... | ... | ... | ... |

### Key Analysis Insights:

1. **Which parameters actually update in response to audio?**
   - Make a list of "responsive parameters" that change during playback

2. **What does each parameter value represent?**
   - Normalized (0-1) vs specialized scale (e.g., LUFS, Hz)

3. **What is the update rate?**
   - Count parameter updates per second while playing audio
   - Measure time between consecutive value changes

4. **Are there any quirks or delays?**
   - Do parameters lag behind audio changes?
   - Are there any smoothing/averaging effects?

---

## Step 7: Capture Results

### Save Results to File

```python
import json

# Save discovered parameter mappings
plugin_results = {
    "plugin_name": "MAnalyzer",
    "plugin_version": "14.01",
    "test_date": "2026-02-10",
    "track_index": 0,
    "device_index": 0,
    "total_parameters": 23,
    "audio_responsive_parameters": [
        {
            "index": 5,
            "name": "Integrated Loudness",
            "range": {"min": -60.0, "max": 0.0},
            "typical_range": [-24.0, -12.0],
            "unit": "LUFS",
            "audio_characteristic": "Overall volume level",
            "update_rate_hz": 15,
            "notes": "Responds quickly to volume changes"
        },
        {
            "index": 7,
            "name": "Spectral Centroid",
            "range": {"min": 0.0, "max": 1.0},
            "typical_range": [0.3, 0.7],
            "unit": "Normalized (0-1)",
            "audio_characteristic": "Brightness / spectral center",
            "update_rate_hz": 18,
            "notes": "Increases with high-frequency content"
        }
        # ... add more parameters
    ],
    "non_responsive_parameters": [
        { "index": 0, "name": "Bypass", "reason": "Control parameter, not analysis" },
        # ... add more
    ]
}

# Save to file
with open('plugin_discovery_results.json', 'w') as f:
    json.dump(plugin_results, f, indent=2)

print("Results saved to plugin_discovery_results.json")
```

---

## Step 8: Repeat for All Plugins

Complete Steps 3-7 for each plugin:

- [ ] MAnalyzer
- [ ] Voxengo SPAN
- [ ] Youlean Loudness Meter 2

---

## Step 9: Report Findings

### Template for Reporting

```markdown
## Task 3 Findings

### Plugin 1: MAnalyzer
- Plugin installed successfully: [Yes/No]
- Parameters exposed: [Count]
- Audio-responsive parameters: [Count]
- Parameter mappings:
  | Index | Name | Range | Unit | Audio Characteristic |
  |-------|------|-------|------|---------------------|
  | 5 | Integrated Loudness | -60 to 0 LUFS | LUFS | Overall volume |
  | 7 | Spectral Centroid | 0-1 | Normalized | Brightness |
- Measured update rate: [X] Hz
- Verified with real audio: [Yes/No]
- Notes: [Any observations, quirks, limitations]

### Plugin 2: Voxengo SPAN
...

### Plugin 3: Youlean Loudness Meter 2
...

### Conclusion
- [x] Free plugins DO expose analysis parameters - proceed with Task 10
- [ ] Free plugins DO NOT expose analysis parameters - pursue backup plan
- Recommended plugin for Task 10: [Plugin name]
- Top parameters to use: [List of indices and names]
```

---

## Troubleshooting

### "get_device_parameters returns empty list"
- **Cause:** Device index may be incorrect
- **Fix:** Try device_index = 0, 1, 2, etc. until you find the correct device

### "Parameters don't change during playback"
- **Cause:** Plugin may be in analysis mode but not configured
- **Fix:** Check plugin UI - ensure it's active and analyzing audio

### "Plugin not found in Ableton"
- **Cause:** Plugin installed in wrong location
- **Fix:** Reinstall plugin to correct VST folder:
  - Windows: `C:\Program Files\Common Files\VST3\`
  - Mac: `/Library/Audio/Plug-Ins/VST3/`

### "Connection refused to MCP server"
- **Cause:** Ableton Remote Script not running
- **Fix:**
  1. Check Ableton is open
  2. Verify Control Surface is set to "AbletonMCP" in Preferences
  3. Restart Ableton

---

## Next Steps After Testing

Once Task 3 is complete and you have the parameter mappings:

1. **Share results** with the AI assistant
2. **Update** `docs/vst-plugins/parameter_mappings.md` with actual indices
3. **Proceed** with Task 10 (Integration Tests)
4. **Update** example rules with real parameter indices

---

## Appendix: Full Test Script

```python
#!/usr/bin/env python3
"""
VST Plugin Parameter Discovery Script
Tests plugin parameter exposure and responsiveness in Ableton Live
"""

import json
import socket
import time
from datetime import datetime

class AbletonMCPClient:
    """Simple TCP client for Ableton MCP server"""

    def __init__(self, host='localhost', port=9877):
        self.host = host
        self.port = port

    def send_command(self, command_type, params=None):
        """Send command and get response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
            command = {'type': command_type, 'params': params or {}}
            sock.send(json.dumps(command).encode('utf-8'))
            response = json.loads(sock.recv(8192).decode('utf-8'))
            return response
        finally:
            sock.close()

def discover_parameters(client, track_index, device_index):
    """Get all parameters from a device"""
    print(f"\n📡 Discovering parameters for Track {track_index}, Device {device_index}...")

    result = client.send_command('get_device_parameters', {
        'track_index': track_index,
        'device_index': device_index
    })

    if result.get('success'):
        params = result.get('parameters', [])
        print(f"✅ Found {len(params)} parameters\n")

        print(f"{'Index':<8} {'Name':<40} {'Value':<10} {'Min':<10} {'Max':<10}")
        print("-" * 90)

        for param in params:
            index = param.get('index')
            name = param.get('name', 'Unknown')[:40]  # Truncate long names
            value = param.get('value', 0.0)
            min_val = param.get('min', 0.0)
            max_val = param.get('max', 1.0)

            print(f"{index:<8} {name:<40} {value:<10.4f} {min_val:<10.4f} {max_val:<10.4f}")

        return params

    else:
        error = result.get('error', 'Unknown error')
        print(f"❌ Failed to get parameters: {error}")
        return []

def monitor_parameters(client, track_index, device_index, param_indices, duration_seconds=30):
    """Monitor specific parameters over time"""
    print(f"\n🎛️ Monitoring parameters {param_indices} for {duration_seconds}s...")
    print("(Start varying audio in Ableton now!)")
    print("-" * 80)

    values_history = {idx: [] for idx in param_indices}
    start_time = time.time()
    sample_count = 0

    try:
        while time.time() - start_time < duration_seconds:
            result = client.send_command('get_device_parameters', {
                'track_index': track_index,
                'device_index': device_index
            })

            if result.get('success'):
                params = result.get('parameters', [])

                for param in params:
                    idx = param.get('index')
                    if idx in param_indices:
                        value = param.get('value', 0.0)
                        values_history[idx].append(value)

                # Extract current values
                current_values = []
                for idx in param_indices:
                    current_values.append(values_history[idx][-1] if values_history[idx] else 0.0)

                # Print row
                row = [f"{v:.4f}" for v in current_values]
                elapsed = time.time() - start_time
                timestamp = f"{elapsed:6.1f}s"
                print(f"[{timestamp}] " + " | ".join(row))

                sample_count += 1

            time.sleep(0.1)  # 10 Hz polling

    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped early")

    print(f"\n📊 Collected {sample_count} samples")

    # Calculate statistics
    print("\nParameter Statistics:")
    print(f"{'Index':<8} {'Min':<12} {'Max':<12} {'Avg':<12} {'Range':<12}")
    print("-" * 60)

    for idx in param_indices:
        values = values_history[idx]
        if values:
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            range_val = max_val - min_val

            print(f"{idx:<8} {min_val:<12.4f} {max_val:<12.4f} {avg_val:<12.4f} {range_val:<12.4f}")
        else:
            print(f"{idx:<8} {'No data':<48}")

    return values_history

def main():
    """Main test workflow"""
    print("=" * 80)
    print("VST PLUGIN PARAMETER DISCOVERY TEST")
    print("=" * 80)

    client = AbletonMCPClient()

    # Configuration
    track_index = 0      # Modify based on your setup
    device_index = 0     # Modify based on your setup

    # Step 1: Discover all parameters
    all_params = discover_parameters(client, track_index, device_index)

    if not all_params:
        print("\n❌ No parameters found. Check track/device indices.")
        return

    # Step 2: Select parameters to monitor
    param_indices = [p['index'] for p in all_params[:5]]  # Monitor first 5 parameters
    print(f"\n📋 Monitoring parameters: {param_indices}")

    # Step 3: Monitor parameters
    values_history = monitor_parameters(
        client,
        track_index,
        device_index,
        param_indices,
        duration_seconds=30
    )

    # Step 4: Identify responsive parameters
    print("\n🔍 Analyzing responsiveness...")

    responsive_params = []
    for idx in param_indices:
        values = values_history[idx]
        if values:
            range_val = max(values) - min(values)
            if range_val > 0.001:  # More than 0.1% range
                responsive_params.append({
                    'index': idx,
                    'name': next((p['name'] for p in all_params if p['index'] == idx), 'Unknown'),
                    'range': range_val,
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                })

    print(f"\n✅ Found {len(responsive_params)} responsive parameters:")
    for p in responsive_params:
        print(f"  Index {p['index']}: {p['name']}")
        print(f"    Range: {p['min']:.4f} - {p['max']:.4f} ({p['range']:.4f})")
        print(f"    Average: {p['avg']:.4f}")

    # Step 5: Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"parameter_discovery_{timestamp}.json"

    results = {
        'test_date': datetime.now().isoformat(),
        'track_index': track_index,
        'device_index': device_index,
        'total_parameters': len(all_params),
        'monitored_parameters': param_indices,
        'sample_count': sum(len(v) for v in values_history.values()) // len(param_indices),
        'responsive_parameters': responsive_params,
        'all_parameters': [
            {
                'index': p['index'],
                'name': p['name'],
                'min': p['min'],
                'max': p['max'],
                'current_value': p['value']
            }
            for p in all_params
        ]
    }

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {filename}")
    print("\n✅ Test complete!")

if __name__ == '__main__':
    main()
```

---

## Summary

This guide provides a complete testing workflow for Task 3:

1. ✅ Install recommended plugins
2. ✅ Load plugins in Ableton
3. ✅ Discover all exposed parameters
4. ✅ Test parameter responsiveness with real audio
5. ✅ Analyze parameter mappings
6. ✅ Capture and save results
7. ✅ Report findings for continuation

**Time Investment:** 30-60 minutes
**Difficulty:** Easy-Medium
**Deliverable:** `plugin_discovery_results.json` with parameter mappings

---

Once you complete Task 3, share the results and we can proceed with Task 10 (Integration Tests).