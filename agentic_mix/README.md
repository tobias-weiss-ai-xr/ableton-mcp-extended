# LangGraph Agentic Mix Generator README

Ableton Live session generation and automated mixing using LangGraph agentic workflows.

## Features

- **Agentic Decision-Making**: AI decides arrangement structure and mixing techniques
- **Configurable Parameters**: Genre, tempo, duration, track count, energy curve
- **Non-Deterministic Output**: Creative variation each run
- **Genre Support**: dub_techno, house, techno, ambient
- **Mixing Techniques**: dub drops, bass-forward, crossfades, filter sweeps, etc.
- **Audio Feedback Loop**: Real-time audio capture between sections drives adaptive mixing decisions

## Installation

```bash
# Install dependencies
pip install langgraph langchain-openai

# The Ableton MCP server must be running on localhost:9877 (TCP)
```

## Quick Start

```bash
# Generate a 2-hour dub techno mix at 126 BPM
python -m agentic_mix.cli --genre dub_techno --tempo 126 --duration 120

# House 1h mix with high variation
python -m agentic_mix.cli --genre house --tempo 124 --duration 60 --variation 0.8

# Ambient 30m mix
python -m agentic_mix.cli --genre ambient --tempo 90 --duration 30 --energy gentle
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--genre` | dub_techno | Musical genre (dub_techno, house, techno, ambient) |
| `--tempo` | 126 | Tempo in BPM (60-180) |
| `--duration` | 120 | Mix duration in minutes (1-480) |
| `--tracks` | 8 | Number of tracks (2-16) |
| `--key` | Fm | Musical key (Fm, Cm, Am, etc.) |
| `--energy` | gradual | Energy curve (gradual, aggressive, gentle) |
| `--variation` | 0.5 | Variation level (0.0-1.0) |

## Architecture

### Pipeline Structure (with Audio Feedback Loop)

```
START → configure → setup_session → generate_clips → construct_arrangement
      → execute_section → analyze_section → [more sections? loop, or END]
```

### Nodes

1. **configure**: Parse and validate user parameters
2. **setup_session**: Create Ableton session with tracks
3. **generate_clips**: Generate MIDI clips for all tracks
4. **construct_arrangement**: Build section structure with AI decisions
5. **execute_section**: Execute ONE section (trigger scene + mixing technique)
6. **analyze_section**: Capture audio snapshot, validate, adapt next section

### Audio Feedback Loop

Sections are processed one at a time in a LangGraph loop:

1. **Execute**: Trigger the section's scene and apply its mixing technique
2. **Capture**: Record audio output via VB-Audio Cable (sounddevice)
3. **Analyze**: Validate snapshot (RMS, spectral, key confidence)
4. **Adapt**: Apply adaptation rules for the NEXT section:
   - **Energy**: RMS < 0.3 → boost energy; RMS > 0.9 → reduce energy
   - **Spectral**: centroid/rolloff ratio > 0.8 → cut highs; < 0.3 → open highs
   - **Technique**: RMS > 0.95 → switch to volume_automation technique
5. **Loop**: If more sections remain, continue; otherwise END

The `analyze_section` node returns a conditional edge: `analyze_section` →
`more_sections?` → `execute_section` (loop) or `END` (complete).

#### Adaptation Rules (`agentic_mix/adaptation_logic.py`)

| Condition | Action | Target |
|-----------|--------|--------|
| RMS < 0.3 | `energy_boost: +0.15` | Next section energy_level |
| RMS > 0.9 | `energy_reduct: -0.15` | Next section energy_level |
| Spectral ratio > 0.8 | `filter_adjust_down: -0.1` | Next section (high cut) |
| Spectral ratio < 0.3 | `filter_adjust_up: +0.1` | Next section (high boost) |
| RMS > 0.95 | Change technique to `volume_automation` | Next section mixing_technique |

#### Audio Capture (`agentic_mix/audio_capture.py`)

The `capture_audio_snapshot()` function wraps the MCP server's audio analysis
tools:
1. Send `audio_analysis_start` to begin capture on VB-Audio Cable input
2. Wait 1 second for the capture to settle
3. Retrieve analysis data via `get_analysis`
4. Stop analysis via `audio_analysis_stop`
5. Return structured `AudioAnalysisData`

If the Ableton MCP server is not running (e.g., during testing), the capture
falls back gracefully with an `ImportError` / `ConnectionRefusedError`.

### Mixing Techniques

- `scene_transition`: Reverb/delay wash between sections
- `bass_forward`: Boost bass, cut other melodic tracks
- `dub_drop`: Filter slam + volume cut on drums
- `crossfade`: Volume crossfade between tracks
- `send_sweep`: Automated send amount changes
- `strip_and_build`: Strip mix then rebuild layers
- `filter_sweep`: Filter parameter automation
- `volume_automation`: Volume curve automation

### State Management

```python
class GraphState(TypedDict):
    config: Config                       # User parameters
    session_info: SessionInfo            # Ableton session state
    arrangement: List[Section]           # Section definitions
    track_states: List[TrackState]       # Current track levels
    playback_metrics: PlaybackMetrics    # Timing and transition data
    feedback: FeedbackState              # Audio analysis + adaptation history
    errors: List[str]                    # Non-fatal errors during execution
    complete: bool                       # Pipeline finished
    current_section_index: int           # Current section (0-based)
    audio_snapshot: Optional[AudioAnalysisData]  # Latest audio analysis
```

#### Feedback Types

```python
class AudioAnalysisData(TypedDict):
    """Single snapshot from AudioAnalyzer"""
    timestamp: float
    bpm: Optional[float]
    beat: Optional[float]
    rms: float                       # Energy level (0.0-1.0)
    loudness_lufs: float            # Integrated loudness
    key: Optional[str]
    key_confidence: Optional[float]
    spectral_centroid_hz: float
    spectral_rolloff_hz: float

class Adaptation(TypedDict):
    """Action applied to a future section"""
    type: str                        # "energy_boost", "energy_reduct", etc.
    target_section: int              # Section index to modify
    value: float                     # Magnitude of adjustment
    tracks: Optional[List[int]]      # Track-specific adjustments
    from_technique: Optional[str]    # Original technique
    to_technique: Optional[str]     # New technique

class FeedbackState(TypedDict):
    """Accumulated feedback across sections"""
    history: List[Tuple[int, AudioAnalysisData]]  # Section snapshots
    adaptations: List[Adaptation]                  # Applied adaptations
    energy_trend: List[float]                      # RMS per section
```

## Programmatic Usage

```python
from agentic_mix.state import Config
from agentic_mix.graph import run_pipeline

# Create configuration
config = Config(
    tempo=126,
    duration_minutes=120,
    genre="dub_techno",
    track_count=8,
    key="Fm",
    energy_curve="gradual",
    variation_level=0.5
)

# Run pipeline
result = run_pipeline(config)

# Check results
if result["complete"]:
    print("Mix complete!")
    print(result["feedback"])
    print(result["metrics"])
```

## Requirements

- Python 3.10+
- Ableton Live 11+ with Remote Script installed
- Ableton MCP server running on localhost:9877/9788
- LangGraph and LangChain dependencies

## Development

```bash
# Run pipeline with debug output
python -m agentic_mix.cli --genre dub_techno --duration 5

# Test individual components
python -c "from agentic_mix.nodes.configure import configure_node; ..."
```

## Notes

- The system connects to Ableton via MCP API (TCP:9877, UDP:9788)
- Clip generation uses rhythmic patterns and generative algorithms
- Arrangement length adapts to duration parameter
- Section energy levels follow configurable energy curve
- Mixing techniques vary per section with AI selection
- Audio feedback loop adapts each section based on the previous section's output
- Capture requires VB-Audio Cable (or similar loopback) for audio analysis
- Feedback adapts energy, spectral balance, and technique selection in real-time