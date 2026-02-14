# Integration Tests for VST Audio Analysis

This directory contains integration tests that verify the VST audio analysis system works correctly with actual Ableton Live sessions.

## Overview

Integration tests are critical for validating that the VST audio analysis system works in real-world scenarios with actual Ableton Live sessions. These tests complement unit tests by testing:

- **Real-world Ableton integration** with actual VST plugins
- **End-to-end workflows** from audio analysis to control decisions
- **Performance under load** with multiple simultaneous operations
- **Error handling** in production scenarios

## Test Structure

```
tests/integration/
├── __init__.py                    # Module initialization
├── test_plugin_analysis.py         # Main integration test suite
└── README.md                      # This file
```

## Requirements

### Prerequisites

1. **Ableton Live 11+** must be running
2. **AbletonMCP Remote Script** loaded in Ableton Preferences
3. **MCP Server** running (`python MCP_Server/server.py`)
4. **Analysis plugins** installed and loaded on tracks:
   - Sound Analyser (free spectrum analyzer)
   - Blue Cat's FreqAnalyst (freeware frequency analyzer)
   - Youlean Loudness Meter 2 (freeware loudness meter)

5. **Test audio sources** prepared (varying frequencies, volumes, etc.)

### Plugin Installation

Install the selected analysis plugins in Ableton Live:

1. **Sound Analyser**: Download from [Sound Analyser GitHub](https://github.com/adamstark/Sound-Analyser)
2. **Blue Cat's FreqAnalyst**: Download from [Blue Cat Audio](https://www.bluecataudio.com/Products/Product_FreqAnalyst/)
3. **Youlean Loudness Meter 2**: Download from [Youlean Audio](https://docs.youlean.co/youlean-loudness-meter/)

## Running Tests

### Basic Usage

```bash
# Test specific plugin
python -m tests.integration.test_plugin_analysis --plugin=SoundAnalyser

# Test responsive control loop
python -m tests.integration.test_plugin_analysis --test=responsive_control

# Test multiple scenarios
python -m tests.integration.test_plugin_analysis --test=multiple_scenarios

# Test all plugins and scenarios
python -m tests.integration.test_plugin_analysis --plugin=SoundAnalyser --test=responsive_control --test=multiple_scenarios
```

### Test Categories

#### 1. Plugin Parameter Tests
- **Parameter Exposure**: Verify all expected parameters are available
- **Parameter Responsiveness**: Test that parameters update in response to audio
- **Parameter Accuracy**: Verify parameter values match expected ranges

#### 2. Real-Time Polling Tests
- **Update Rate**: Test polling at target rates (10-20 Hz)
- **Performance**: Measure actual polling rate and latency
- **Stability**: Test extended polling duration (60+ seconds)

#### 3. Responsive Control Tests
- **Rule Evaluation**: Test rule-based decisions work correctly
- **Control Actions**: Verify Ableton commands are executed properly
- **Latency**: Measure response time from parameter change to action

#### 4. Scenario Tests
- **Quiet Audio**: Test with low-level audio (noise floor detection)
- **Loud Audio**: Test with high-level audio (peak detection, compression)
- **Frequency Sweeps**: Test with frequency sweeps (spectral tracking)
- **Tempo Changes**: Test system stability during tempo modifications

## Test Results

Each test reports:
- **PASS**: Test completed successfully
- **FAIL**: Test failed with detailed error information
- **SKIP**: Test skipped (prerequisite not met)

## Interpreting Results

### Success Criteria
- All plugin parameter tests pass
- Real-time polling achieves target rates (10+ Hz)
- Responsive control loop executes actions within 100ms
- All scenario tests pass with expected behaviors
- No connection errors or timeouts

### Troubleshooting

#### Common Issues
1. **"Connection refused"**: Ableton Remote Script not running
   - Solution: Start MCP server and load Remote Script in Ableton
   
2. **"Plugin not found"**: Analysis plugin not loaded on track 0
   - Solution: Load plugin on track 0 before running tests
   
3. **"Parameters not updating"**: Plugin parameters not responsive to audio
   - Solution: Check plugin supports parameter automation in Ableton
   
4. **"Rules file not found"**: Control rules file missing
   - Solution: Test creates rules file automatically

## Test Data and Logs

Tests generate logs in `tests/integration/logs/`:
- Parameter reading logs with timestamps
- Performance metrics (polling rates, latencies)
- Error reports and stack traces
- Control action logs

## Development Notes

### Adding New Tests
1. Add test method to `AbletonIntegrationTester` class
2. Add expected parameters list for new plugins
3. Update `test_multiple_scenarios()` with new scenario
4. Update documentation

### Test Framework Patterns
- Use TCP socket communication (port 9877)
- Implement timeout and retry logic
- Mock Ableton state for testing without Live running
- Log all operations with timestamps and success/failure states