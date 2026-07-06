# Quick Start Guide - 2-Hour Dub Techno Mix

Autonomous dub techno session automation via Ableton MCP.

## Prerequisites

- **Ableton Live 11+** with Remote Script enabled
- **Ableton MCP Extended** (this repo) installed
- **MCP Server** running on TCP port 9877, UDP port 9878
- **Python 3.8+** with dependencies:
  ```bash
  pip install -e .
  ```

## 5-Minute Quick Start

### 1. Start MCP Server

```bash
cd MCP_Server
python server.py
```

Server should start on ports 9877 (TCP) and 9878 (UDP).

### 2. Run Session Setup

```bash
python session_setup.py
```

Creates:
- 5 tracks (Drums, Bass, Pad 1, Pad 2, FX)
- Instruments loaded on each track
- 32 clips (8 per track)
- Follow actions configured

### 3. Launch Main Automation

```bash
python scripts/dub_techno_2h_automation.py
```

Session will:
- Initialize session skeleton
- Configure 2-hour progression
- **Press Enter** to start 2-hour mix
- Run autonomous automation (filter sweeps, reverb washes, gate effects)
- Auto-save snapshots every ~8 minutes
- Handle errors gracefully

### 4. Monitor Session

Session outputs:
- Progress updates (current wave, block)
- Automation pattern notifications
- Error/recovery messages
- Auto-save confirmations

## Project Structure

```
ableton-mcp-extended/
├── MCP_Server/              # MCP server (ports 9877/9878)
├── session_setup.py         # Initial session setup
├── automation_patterns.py   # Automation pattern library
├── pattern_orchestration.py # Wave structure and scheduling
├── error_handling.py        # Error detection and recovery
├── session_auto-save.py     # Session auto-save and recovery
├── mcp_client.py            # MCP client (TCP/UDP)
├── clip_patterns.py         # Clip generation utilities
├── follow_actions.py        # Follow action configuration
├── parameter_sweeps.py      # Parameter sweep functions
├── audio_analysis.py        # Audio analysis wrapper
├── scripts/
│   ├── create_drum_clips.py
│   ├── create_bass_clips.py
│   ├── create_pad_clips.py
│   ├── create_percussion_clips.py
│   ├── create_dub_fx_clips.py
│   ├── setup_return_track.py
│   ├── configure_follow_actions.py
│   ├── get_device_param_indices.py
│   └── dub_techno_2h_automation.py  # Main automation script
└── tests/
    └── test_integration_test.py      # Integration test suite
```

## Session Waves

The 2-hour session is divided into 4 waves:

| Wave | Duration | Description |
|------|----------|-------------|
| **Intro** | 4 min | Sparse, atmospheric, fade in from silence |
| **Main** | 96 min | Driving dub techno core, breakdowns every 3rd block |
| **Climax** | 16 min | Maximum energy, massive filter sweeps, aggressive gating |
| **Outro** | 4 min | Fading, minimal, atmospheric |

## Automation Patterns

Available patterns in `automation_patterns.py`:

- `pattern_filter_drop()` - Classic dub techno filter sweeps
- `pattern_reverb_wash()` - Reverb wash for transitions
- `pattern_delay_syncopation()` - Rhythmic delay echo patterns
- `pattern_formant_sweep()` - Formant filter tape texture
- `pattern_synchronized_filter_sweep()` - Multi-track synchronized sweep
- `pattern_gate_effect()` - Rhythmic volume muting
- `pattern_sidechain_pumping()` - Audio-reactive sidechain

## Session Auto-Save

Auto-saves every 1000 beats (~8 minutes at 125 BPM).

Save files: `session_backups/dub_techno_session_*.json`

### Recover Session

```python
from session_auto_save import SessionRecovery
from mcp_client import MCPClientTCP

client = MCPClientTCP()
recovery = SessionRecovery("session_backups")

# List available saves
saves = recovery.list_available_saves()
print(saves)

# Recover latest save
state = recovery.get_latest_save()
recovery.recover_session_state(client, state['path'])
```

## Error Handling

Session includes robust error detection and recovery:

### Error Levels

- **LOW**: Minor automation glitch - retry or continue
- **MEDIUM**: Track/clip state compromised - reset track
- **HIGH**: Session state corrupted - reset scene
- **CRITICAL**: Complete session failure - abort

### Error Log

All errors logged to `session_errors.log` with timestamps.

## Customization

### Adjust Session Length

Edit `pattern_orchestration.py`:

```python
# Main wave duration
MAIN_DURATION_BEATS = 4800  # 96 minutes

# Or adjust individual wave structures
def _build_main_wave(self) -> WaveStructure:
    # Modify pattern blocks here
    ...
```

### Change Tempo

Edit `scripts/dub_techno_2h_automation.py`:

```python
class TwoHourDubTechnoSession:
    TEMPO = 125  # Change this
```

### Modify Automation Effects

Edit `automation_patterns.py`:

```python
# Adjust filter sweep intensity
def pattern_filter_drop(self, track_indices, intensity=0.7):
    start_filter = 0.3 if intensity > 0.5 else 0.4
    end_filter = 0.9
    ...
```

## Testing

Run integration test suite:

```bash
python tests/test_integration_test.py
```

Tests cover:
- MCP connection
- Session setup
- Wave structure
- Automation patterns
- Error handling
- Auto-save
- Performance metrics

## Troubleshooting

### MCP Server Not Starting

```bash
# Check if ports are in use
netstat -an | grep 9877
netstat -an | grep 9878

# Kill existing processes
kill -9 $(lsof -t -i:9877)
```

### Session Setup Fails

1. Verify Ableton is running with Remote Script enabled
2. Check MCP server is running
3. Review `session_errors.log` for details

### Automation Not Triggering

1. Verify clips exist in session
2. Check follow actions are configured
3. Manual trigger: `python -c "from mcp_client import *; fire_scene(0)"`

### Session Stalls

1. Check error log: `tail -f session_errors.log`
2. Verify auto-save files are being created
3. Check MCP server is still running

## Advanced Usage

### Standalone Pattern Execution

```python
from mcp_client import MCPClientTCP
from automation_patterns import AutomationSequencer

client = MCPClientTCP()
sequencer = AutomationSequencer(client)

# Run specific pattern
sequencer.pattern_filter_drop([0, 1], intensity=0.8)

# Run preset sequence
sequencer.sequence_climax_build(duration_beats=128)
```

### Custom Wave Structure

```python
from pattern_orchestration import WaveType, PatternBlock

wave_structure = WaveStructure(
    wave_type=WaveType.MAIN,
    duration_beats=1000,
    pattern_blocks=[
        PatternBlock(
            id="custom_block",
            duration_beats=500,
            scene_indices=[1, 2],
            automation_patterns=["pattern_filter_drop"],
            track_volumes={0: 0.7, 1: 0.7}
        )
    ]
)
```

## Support

For issues, check:
1. `session_errors.log` - Error details
2. MCP server logs - Connection problems
3. Integration test results - System health

## License

MIT License - See `LICENSE` file.