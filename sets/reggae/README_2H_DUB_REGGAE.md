# 2-Hour Reggae Dub Automation

**Fully automated 2-hour reggae dub track in Ableton Live via MCP control.**

## Quick Start (3 Steps)

```bash
# 1. Create tracks and clips
python sets/reggae/create_2h_dub_reggae.py

# 2. Load instruments and effects
python sets/reggae/load_instruments_2h.py

# 3. Run full 2-hour automation
python sets/reggae/automate_2h_dub_reggae.py
```

## What You Get

- **8 tracks** (6 MIDI + 2 audio send)
- **48 MIDI clips** (8 per MIDI track)
- **30 sections** (4 minutes each = 2 hours)
- **Progressive drum patterns**: One Drop → Rockers → Steppers
- **Full timer-based automation** (hands-free playback)

## Track Structure

| Track | Type | Instrument | Purpose |
|-------|------|------------|---------|
| 0 | MIDI | Drum Rack | Drums (One Drop, Rockers, Steppers) |
| 1 | MIDI | Operator | Dub Bass (main focus) |
| 2 | MIDI | Electric | Guitar Chop (skank) |
| 3 | MIDI | Organ | Organ Bubble |
| 4 | MIDI | Wavetable | Synth Pad (atmosphere) |
| 5 | MIDI | Simpler | FX (sub hits, crashes) |
| 6 | Audio | Hybrid Reverb | Reverb Send |
| 7 | Audio | Simple Delay | Delay Send |

## Section Structure (30 Sections)

### Phase 1: One Drop (Sections 0-9)
- Minimal, spacious drums
- Establish groove
- Deep roots feel

### Phase 2: Rockers (Sections 10-19)
- Building energy
- Consistent driving pulse
- Walking bass lines

### Phase 3: Steppers (Sections 20-29)
- Peak energy
- Four-on-floor feel
- Maximum dance energy

## Scripts

### 1. `create_2h_dub_reggae.py`
Creates 8 tracks and 48 MIDI clips with drum patterns, bass lines, guitar chops, and organ parts.

```bash
python sets/reggae/create_2h_dub_reggae.py
python sets/reggae/create_2h_dub_reggae.py --dry-run  # Preview only
```

### 2. `load_instruments_2h.py`
Loads instruments and effects onto tracks, sets base volumes.

```bash
python sets/reggae/load_instruments_2h.py
python sets/reggae/load_instruments_2h.py --dry-run  # Preview only
```

### 3. `automate_2h_dub_reggae.py`
Runs the full 2-hour automation with section progression.

```bash
python sets/reggae/automate_2h_dub_reggae.py              # Full 2-hour run
python sets/reggae/automate_2h_dub_reggae.py --test-mode  # 30-second test
python sets/reggae/automate_2h_dub_reggae.py --dry-run    # Print only
```

## Manual Setup Required

After running scripts, you must configure in Ableton:

1. **Drum Kit**: Load samples into Drum Rack (track 0)
2. **Send Routing**: Configure sends A (Reverb) and B (Delay)
3. **Effect Settings**: 
   - Hybrid Reverb: Room ~40%, Decay ~50%
   - Simple Delay: Time 1/4, Feedback 40%
4. **Instrument Presets**: Choose sounds for Operator, Electric, Organ, Wavetable

## Timing

- **Tempo**: 72 BPM
- **Key**: C Minor
- **Section Duration**: 4 minutes (240 seconds)
- **Total Duration**: 120 minutes (2 hours)

## Volume Targets by Energy

| Energy | Drums | Bass | Guitar | Organ | Pad | FX |
|--------|-------|------|--------|-------|-----|-----|
| Minimal | 0.60 | 0.70 | 0.50 | 0.45 | 0.40 | 0.35 |
| Building | 0.70 | 0.78 | 0.60 | 0.55 | 0.50 | 0.45 |
| Peak | 0.80 | 0.88 | 0.70 | 0.65 | 0.60 | 0.55 |
| Breakdown | 0.50 | 0.60 | 0.40 | 0.35 | 0.45 | 0.30 |
| Fading | 0.55 | 0.65 | 0.45 | 0.40 | 0.35 | 0.30 |

## DJ Rules Applied

1. **ONE CLIP CHANGE AT A TIME** - Never overwhelm the listener
2. **Let the groove breathe** - Space between changes
3. **Bass is the foundation** - Always prominent in the mix
4. **Gradual evolution** - Slow builds and drops

## Troubleshooting

**Clips don't fire**: Verify clips were created with `create_2h_dub_reggae.py`

**No sound**: Check instruments are loaded with `load_instruments_2h.py`

**Wrong tempo**: Run `create_2h_dub_reggae.py` to set tempo to 72 BPM

**Automation stops**: Check MCP server connection (localhost:9877)

## Requirements

- Ableton Live 11+
- MCP Server running (port 9877)
- Python 3.10+
- All instruments from Ableton Core Library
