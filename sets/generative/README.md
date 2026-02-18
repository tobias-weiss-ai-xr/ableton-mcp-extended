# Generative Dub Techno System

A self-evolving dub techno system with infinite variation through follow actions, probabilistic note generation, and real-time UDP parameter control.

## Quick Start

```bash
# Set up the session (requires Ableton running with MCP Remote Script)
python -m dub_techno_2h.generative.setup_generative_session

# Run the evolution engine
python -m dub_techno_2h.generative.evolution_engine --duration 30 --verbose

# Simulate without Ableton
python -m dub_techno_2h.generative.evolution_engine --duration 10 --simulate

# Verify variation entropy
python -m dub_techno_2h.generative.verify_variation --duration 30 --simulate
```

## Architecture

```
generative/
├── config.py              # Central configuration
├── mcp_client.py          # TCP/UDP communication
├── pattern_generator.py   # Algorithmic MIDI generation
├── follow_action_setup.py # Clip chain configuration
├── udp_controller.py      # Real-time parameter sweeps
├── evolution_engine.py    # Main orchestrator
├── verify_follow_actions.py
├── verify_variation.py
├── reset_session.py
└── setup_generative_session.py
```

## Features

### Pattern Generation
- **Markov chains** for bass and pad melodies
- **Probabilistic ghost notes** (20% chance on offbeats)
- **Micro-timing variation** (±0.02 beats Gaussian)
- **Velocity humanization** (±10 uniform)
- **Prime-length patterns** (3, 5, 7 bars) for phase relationships

### Follow Actions
- **60% stay / 40% transition** probability
- **Self-evolving clips** that never repeat the same way twice
- **No dead ends** - all clips reachable from any starting point

### Real-Time Control
- **UDP parameter sweeps** at 8000+ Hz
- **Filter sweeps** (sine, triangle, ramp, random walk)
- **Volume automation**
- **Rate limiting** to prevent audio glitches

## Performance

| Metric | Value |
|--------|-------|
| UDP throughput | 8200+ Hz |
| UDP latency | 0.12ms average |
| Pattern entropy | 2.81 bits |
| Max consecutive repeats | 1 |

## Configuration

Edit `config.py` to customize:
- `TEMPO` - Default 126 BPM
- `GHOST_NOTE_PROBABILITY` - Default 0.2 (20%)
- `FOLLOW_ACTION_STAY_PROB` - Default 0.6 (60%)
- `MARKOV_MATRICES` - Bass and pad transition probabilities
- `UDP_RATE_LIMITS` - Max Hz for different parameter types
