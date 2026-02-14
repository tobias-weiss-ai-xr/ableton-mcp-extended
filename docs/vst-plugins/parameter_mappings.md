# VST Audio Analysis Plugin Parameter Mappings

This document provides detailed parameter mappings for audio analysis VST plugins integrated with ableton-mcp-extended.

**Project**: VST Audio Analysis Implementation
**Last Updated**: 2026-02-10
**Status**: Template version (pending actual Ableton session testing validation)

---

## Purpose

This document serves as the definitive reference for:
- Mapping VST plugin parameter indices to audio analysis metrics
- Understanding value ranges and units for each parameter
- Interpretation guidelines for making control decisions
- Expected update rates and responsiveness

---

## Plugin 1: Youlean Loudness Meter 2 (Free Tier)

**Overview**: LUFS-based loudness metering with EBU R128 compliance
**Plugin Type**: Analysis / Metering
**License**: Free tier available (commercial license for full features)
**Website**: https://youlean.co/youlean-loudness-meter/
**Ableton Live Compatibility**: Verified for Live 11+

### Parameter Mappings

**Note**: These mappings are based on plugin documentation and expected behavior. Actual parameter indices and values must be validated via Ableton session testing (Task 3).

| Index | Parameter Name | Metric Type | Value Range | Units | Typical Range | Update Rate | Control Use |
|-------|----------------|-------------|-------------|-------|---------------|-------------|-------------|
| 0 | Momentary LUFS (LL-M) | Instantaneous loudness | -70.0 to +5.0 | LUFS | -30 to -4 | 10-20 Hz | Real-time level monitoring |
| 1 | Short-term LUFS (LL-S) | 3-second integrated loudness | -70.0 to +5.0 | LUFS | -25 to -10 | 3-5 Hz | Overall track loudness |
| 2 | Integrated LUFS (LL-I) | Full program loudness | -70.0 to +5.0 | LUFS | -16 to -8 | 0.1-0.5 Hz | Master output validation |
| 3 | RMS Level | Avg signal level | -60.0 to 0.0 | dBFS | -20 to -6 | 10-20 Hz | Dynamic range assessment |
| 4 | True Peak | Peak amplitude with intersample peaks | -6.0 to +6.0 | dBTP | -1.0 to -0.3 | 10-20 Hz | Clipping detection |
| 5 | Loudness Range (LRA) | Dynamic range measurement | 0.0 to 50.0 | LU | 5.0 to 20.0 | 0.5-1 Hz | Dynamics analysis |
| 6 | Crest Factor | Peak-to-average ratio | 0.0 to 30.0 | dB | 10.0 to 18.0 | 1-2 Hz | Transient assessment |

### Normalized Value Formulas

**Formula**: `normalized_value = (raw_value - min) / (max - min)`

Example for parameter 0 (Momentary LUFS):
- Min: -70.0 LUFS
- Max: +5.0 LUFS
- Range: 75.0

To convert normalized (0.0-1.0) back to LUFS:
```python
lufs_value = normalized_value * 75.0 - 70.0
```

### Control Decision Thresholds (Examples)

**Rule-based decision examples**:

```yaml
# Example: Compressor trigger based on loudness
rules:
  - metric: Momentary LUFS
    threshold: -12.0
    action: enable_compressor
    hysteresis: -14.0  # Disable when below -14

  - metric: True Peak
    threshold: -0.5
    action: enable_limiter
    severity: critical

  - metric: Loudness Range
    threshold: < 6.0
    action: warn_dynamic_range
    message: "Audio is overly compressed"
```

### Expected Behavior

- **Startup Time**: 2-3 seconds for analysis engine to initialize
- **Responsiveness**: Parameters update within 50-100ms of audio changes
- **Stability**: No significant drift or fluctuations during steady-state signals
- **Note**: Free tier may have parameter locking or limited refresh rates

---

## Plugin 2: Voxengo SPAN (Freeware)

**Overview**: Multi-channel spectral analyzer with FFT-based analysis
**Plugin Type**: Analysis / Spectrum
**License**: Freeware
**Website**: https://www.voxengo.com/product/span/
**Ableton Live Compatibility**: Verified for Live 11+

### ⚠️ Critical Status: Parameter Exposure Uncertain

**Risk Assessment**: HIGH RISK - SPAN is primarily a visualization tool. As of research phase, it is unclear whether analysis metrics are exposed as controllable VST parameters (indices 0+). This plugin may only expose GUI configuration parameters, not analysis data.

**Result from Task 3 Testing**: `[PENDING - Must validate in actual Ableton session]`

### Parameter Mappings (PENDING VALIDATION)

**If analysis metrics ARE exposed as parameters**:

| Index | Parameter Name | Metric Type | Value Range | Units | Typical Range | Update Rate | Control Use |
|-------|----------------|-------------|-------------|-------|---------------|-------------|-------------|
| 0 | Peak Level dB | Peak frequency level | -100 to 0 | dBFS | -60 to -3 | 10-20 Hz | Spectral peak monitoring |
| 1 | Average Level dB | Average spectrum level | -100 to 0 | dBFS | -40 to -10 | 5-10 Hz | Energy distribution |
| 2 | Spectral Centroid | Frequency "brightness" | 0 to 22050 | Hz | 1000 to 8000 | 10-20 Hz | Tone brightness control |
| 3 | Spectral Rolloff | Frequency below which 85% of energy exists | 0 to 22050 | Hz | 2000 to 15000 | 5-10 Hz | High-frequency content |
| 4 | Harmonic/Noise Ratio | Pitched vs unpitched content | 0.0 to 1.0 | ratio | 0.3 to 0.8 | 5-10 Hz | Tonal analysis |

**If analysis metrics ARE NOT exposed**:
- SPAN will not be usable for automated control purposes
- Must switch to alternative plugin or custom VST development plan

### Expected Behavior (If Parameters Exposed)

- **FFT Window Size**: Affects temporal resolution (shorter = faster updates, less frequency accuracy)
- **Update Rate**: Determined by FFT overlap and buffer size (typically 50-200ms)
- **Consideration**: Spectral parameters are less useful for basic loudness control than LUFS metrics

---

## Plugin 3: PSP Spector (Freeware)

**Overview**: 31-band spectrum analyzer with peak and RMS level meters
**Plugin Type**: Analysis / Spectrum
**License**: Freeware
**Website**: https://www.pspaudioware.com/products/psp-spector/
**Ableton Live Compatibility**: Verified for Live 11+

### Parameter Mappings (PENDING VALIDATION)

**Expected Structure**: 31 frequency bands × 2 metrics (Peak + RMS) = potentially 62+ parameters

#### Band-to-Frequency Mapping

| Band Index | Frequency Range | Center Frequency | Parameter Indices (Expected) |
|------------|-----------------|------------------|------------------------------|
| 0 | 25-31 Hz | 28 Hz | 0 (Peak), 1 (RMS) |
| 1 | 31-40 Hz | 35 Hz | 2, 3 |
| 2 | 40-50 Hz | 45 Hz | 4, 5 |
| 3 | 50-63 Hz | 56 Hz | 6, 7 |
| 4 | 63-80 Hz | 71 Hz | 8, 9 |
| 5 | 80-100 Hz | 89 Hz | 10, 11 |
| 6 | 100-125 Hz | 111 Hz | 12, 13 |
| 7 | 125-160 Hz | 141 Hz | 14, 15 |
| 8 | 160-200 Hz | 178 Hz | 16, 17 |
| 9 | 200-250 Hz | 222 Hz | 18, 19 |
| 10 | 250-315 Hz | 278 Hz | 20, 21 |
| 11 | 315-400 Hz | 353 Hz | 22, 23 |
| 12 | 400-500 Hz | 444 Hz | 24, 25 |
| 13 | 500-630 Hz | 558 Hz | 26, 27 |
| 14 | 630-800 Hz | 708 Hz | 28, 29 |
| 15 | 800-1000 Hz | 889 Hz | 30, 31 |
| 16 | 1.0-1.25 kHz | 1.11 kHz | 32, 33 |
| 17 | 1.25-1.6 kHz | 1.41 kHz | 34, 35 |
| 18 | 1.6-2.0 kHz | 1.78 kHz | 36, 37 |
| 19 | 2.0-2.5 kHz | 2.22 kHz | 38, 39 |
| 20 | 2.5-3.15 kHz | 2.78 kHz | 40, 41 |
| 21 | 3.15-4.0 kHz | 3.53 kHz | 42, 43 |
| 22 | 4.0-5.0 kHz | 4.44 kHz | 44, 45 |
| 23 | 5.0-6.3 kHz | 5.58 kHz | 46, 47 |
| 24 | 6.3-8.0 kHz | 7.08 kHz | 48, 49 |
| 25 | 8.0-10 kHz | 8.89 kHz | 50, 51 |
| 26 | 10-12.5 kHz | 11.1 kHz | 52, 53 |
| 27 | 12.5-16 kHz | 14.1 kHz | 54, 55 |
| 28 | 16-20 kHz | 17.8 kHz | 56, 57 |
| 29 | 20-25 kHz | 22.2 kHz | 58, 59 |
| 30 | 25-31.5 kHz | 27.8 kHz | 60, 61 |

#### Parameter Specifications

| Parameter Type | Index Pattern | Value Range | Units | Typical Range | Update Rate |
|----------------|---------------|-------------|-------|---------------|-------------|
| Level Band Peak | 0, 2, 4, ..., 60 | -60.0 to 0.0 | dBFS | -40 to -6 | 10-20 Hz |
| Level Band RMS | 1, 3, 5, ..., 61 | -60.0 to 0.0 | dBFS | -40 to -10 | 5-10 Hz |

### Control Decision Examples

```yaml
# Example: Detect bass content
rules:
  - metric: RMS Band 5-6 (80-125 Hz)
    threshold: -20  # dBFS
    action: enable_bass_boost
    duration: 2.0  # Continue for 2 seconds

  - Example: Detect harsh high frequencies
  - metric: Peak Band 24-26 (6.3-12.5 kHz)
    threshold: -12
    action: enable_high_shelf_cut
    message: "High-frequency harshness detected"
```

### Challenges

- **Parameter Count**: 62+ parameters makes polling overhead significant
- **Granularity**: Fine-grained frequency data may be overkill for basic control decisions
- **Update Synchronization**: Different bands may update at different rates, making aggregated measurements complex

---

## Validation Plan (Task 3)

### Step-by-Step Testing Procedure

**Goal**: For each plugin, verify:
1. Parameters are exposed via `get_device_parameters` tool
2. Parameter indices match expected mappings above
3. Values update in real-time during audio playback
4. Update rate meets 10-20 Hz requirement
5. Value ranges match documented ranges

### Testing Script (Conceptual)

```python
# This script would be run in an actual Ableton session
from ableton_mcp_extended import get_device_parameters

# For each plugin track_index and device_index:
def test_plugin(track_index, device_index):
    print(f"Testing plugin on track {track_index}, device {device_index}")

    # Get all parameters
    params = get_device_parameters(track_index, device_index)

    # Parameter count
    print(f"Parameter count: {len(params)}")

    # Poll parameters during audio playback
    import time
    updates = []
    start_time = time.time()

    while len(updates) < 100:  # Collect 100 samples
        current_values = [p['value'] for p in params]
        updates.append({
            'time': time.time() - start_time,
            'values': current_values
        })
        time.sleep(0.05)  # 20 Hz polling

    # Analyze update rate
    intervals = [updates[i+1]['time'] - updates[i]['time'] for i in range(len(updates)-1)]
    avg_update_interval = sum(intervals) / len(intervals)
    print(f"Average update interval: {avg_update_interval*1000:.1f} ms ({1/avg_update_interval:.1f} Hz)")

    # Check parameter responsiveness
    for i, param in enumerate(params):
        values = [u['values'][i] for u in updates]
        min_val, max_val = min(values), max(values)
        if max_val - min_val > 0.01:  # Parameter changed
            print(f"Parameter {i} ({param.get('name', 'Unknown')}): Range [{min_val:.3f}, {max_val:.3f}]")
```

### Expected Outcomes

| Plugin | Expected Parameter Count | Critical Parameter Indices | Expected Update Rate |
|--------|-------------------------|----------------------------|----------------------|
| Youlean Loudness Meter 2 | 6-8 | 0-5 (LUFS, RMS, Peak) | 10-20 Hz |
| Voxengo SPAN | 0-10 OR 0 (no parameters) | 0-3 (if exposed) | 5-20 Hz OR N/A |
| PSP Spector | 60-70 | 30-61 (mid-bands) | 5-15 Hz |

### Decision Tree Based on Results

```
Task 3 Testing Complete?
├─ YES
│  ├─ ALL plugins expose parameters? → PROCEED to Task 4
│  ├─ SOME plugins expose parameters? → SELECT best plugin, PROCEED with subset
│  └─ NO plugins expose parameters? → TRIGGER backup plan (custom VST development)
└─ NO / INCOMPLETE → CONTINUE testing or manual verification
```

---

## Backup Plan: Custom VST Development

**Scenario**: If NO free/freeware plugins expose audio analysis as programmable parameters:

**Objective**: Develop minimal VST plugin using JUCE framework that exposes a small set of critical analysis metrics as VST parameters.

**Metrics to Expose**:
1. Momentary LUFS (or approximate RMS-based loudness)
2. True Peak level
3. Dynamic range (LRA approximation)

**Development Effort**: 2-3 weeks for:
- JUCE project setup
- Analysis algorithms (EBU R128 LUFS implementation)
- VST parameter exposure
- Testing and validation

**Alternative**: Explore paid/commercial analysis plugins that specifically parameterize their metrics (e.g., MeterPlugs Loudness Meter, Nugen Audio VisLM).

---

## Getting This Document

**Status**: Template version created based on research assumptions and plugin documentation.

**Next Actions**:
1. Execute Task 3 testing in actual Ableton session
2. Populate actual parameter mappings based on test results
3. Update this document with validated indices, ranges, and update rates
4. Replace "PENDING VALIDATION" labels with confirmed data

---

## Appendix A: Parameter Polling Implementation Guide

**Related Task**: Task 5 - Implement parameter polling system

### Polling Loop Architecture

```python
# Poller worker structure (high-level design)
import time
from threading import Thread

class AudioAnalysisPoller:
    def __init__(self, track_index, device_index, params_to_poll, update_rate_hz):
        self.track_index = track_index
        self.device_index = device_index
        self.params_to_poll = params_to_poll  # List of parameter indices to monitor
        self.update_interval = 1.0 / update_rate_hz
        self.running = False
        self.thread = None
        self.latest_values = {}
        self.callbacks = []

    def start(self):
        self.running = True
        self.thread = Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def _poll_loop(self):
        while self.running:
            # Poll parameters via MCP tool
            params = get_device_parameters(self.track_index, self.device_index)

            # Extract monitored parameters
            for idx in self.params_to_poll:
                if idx < len(params):
                    self.latest_values[idx] = params[idx]['value']

            # Notify rule engine via callbacks
            for callback in self.callbacks:
                callback(self.latest_values)

            time.sleep(self.update_interval)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
```

### Performance Considerations

- **Polling Rate**: 10-20 Hz (50-100ms intervals)
- **Parallel Polling**: Can poll multiple plugins simultaneously via threads
- **Batching**: Consider using `get_device_parameters` once per plugin, not per parameter
- **Buffering**: Implement circular buffer for time-series analysis if needed

---

## Appendix B: Rule-Based Decision System Guide

**Related Task**: Task 6 - Create rule-based decision system

### YAML Configuration Example

```yaml
# analysis_rules.yaml
rulesets:
  - name: loudness_control
    enabled: true
    rules:
      - condition:
          metric: momentary_lufs
          operator: ">="
          value: -10.0
        actions:
          - type: set_device
            target: "Compressor"
            parameter: threshold
            value: -10.0
        cooldown: 1.0  # seconds

  - name: peak_protection
    enabled: true
    rules:
      - condition:
          metric: true_peak
          operator: ">="
          value: -0.5
        actions:
          - type: set_device
            target: "Limiter"
            parameter: ceiling
            value: -0.5
          - type: log_message
            message: "Peak limiting activated"
```

### Decision Engine Flow

1. **Poll**: Audio analysis parameters update at configured rate
2. **Evaluate**: Rule engine checks all enabled rules against current values
3. **Execute**: Matching rules trigger actions (device parameter changes, alerts)
4. **Cooldown**: Rule cooldown timers prevent oscillation (e.g., rapid enable/disable cycle)

---

## Document Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-02-10 | 0.1 (Template) | Initial template created based on research | Atlas (Sisyphus) |
| [PENDING] | 1.0 | populate with actual Ableton session test results | TBD |

---

## Contact / Issues

- **Project**: ableton-mcp-extended
- **Plan**: VST Audio Analysis Implementation
- **Task Reference**: vst-audio-analysis.md (Task 4)

Open issues, clarifications, or corrections should be reported in the project repository or relevant planning documentation.