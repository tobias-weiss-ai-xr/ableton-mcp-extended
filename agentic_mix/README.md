# LangGraph Agentic Mix Generator README

Ableton Live session generation and automated mixing using LangGraph agentic workflows.

## Features

- **Agentic Decision-Making**: AI decides arrangement structure and mixing techniques
- **Configurable Parameters**: Genre, tempo, duration, track count, energy curve
- **Non-Deterministic Output**: Creative variation each run
- **Genre Support**: dub_techno, house, techno, ambient
- **Mixing Techniques**: dub drops, bass-forward, crossfades, filter sweeps, etc.

## Installation

```bash
# Install dependencies
pip install langgraph langchain-openai

# The Ableton MCP server must be running on localhost:9877 (TCP)
```

## Quick Start

```bash
# Generate a 2-hour dub techno mix at 126 BPM
python -m langgraph.cli --genre dub_techno --tempo 126 --duration 120

# House 1h mix with high variation
python -m langgraph.cli --genre house --tempo 124 --duration 60 --variation 0.8

# Ambient 30m mix
python -m langgraph.cli --genre ambient --tempo 90 --duration 30 --energy gentle
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

### Pipeline Structure

```
START → configure → setup_session → generate_clips → construct_arrangement
      → execute_mix_loop → analyze_adapt → END
```

### Nodes

1. **configure**: Parse and validate user parameters
2. **setup_session**: Create Ableton session with tracks
3. **generate_clips**: Generate MIDI clips for all tracks
4. **construct_arrangement**: Build section structure with AI decisions
5. **execute_mix_loop**: Run live mix with mixing techniques
6. **analyze_adapt**: Evaluate and adapt (feedback loop)

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
    config: Config                  # User parameters
    session_info: SessionInfo       # Ableton session state
    arrangement: List[Section]      # Section definitions
    current_section: int
    track_states: List[TrackState]  # Current track levels
    playback_metrics: PlaybackMetrics
    feedback: List[str]
    complete: bool
    error: Optional[str]
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
python -m langgraph.cli --genre dub_techno --duration 5

# Test individual components
python -c "from langgraph.nodes.configure import configure_node; ..."
```

## Notes

- The system connects to Ableton via MCP API (TCP:9877, UDP:9788)
- Clip generation uses rhythmic patterns and generative algorithms
- Arrangement length adapts to duration parameter
- Section energy levels follow configurable energy curve
- Mixing techniques vary per section with AI selection