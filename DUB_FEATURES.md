# Dub-Centric Features for Ableton MCP Extended

> **BASS AND EFFECTS ARE KEY TO DUB** - added as high-priority features

This document describes the dub-specific capabilities integrated into the arrangement capture tools.

## Overview

Following the project's consolidation of arrangement tools and the addition of performance optimizations, we recognized a critical need: **dub music is fundamentally defined by its basslines and effects processing**. This led to the development of dedicated dub-centric features that go beyond generic arrangement capture.

## What Was Added

### 1. Enhanced Device Discovery (Specific for Dub Production)

Located in `MCP_Server/arrangement_tools.py`:

- **`_find_delay_device(ableton, track_index)`**: Finds delay/echo devices (Simple Delay, Echo, Grain Delay)
- **`_find_reverb_device(ableton, track_index)`**: Finds reverb devices
- **`_find_eq_device(ableton, track_index)`**: Finds EQ devices (EQ Eight, EQ Three, Auto Filter)
- **`_find_filter_device(ableton, track_index)`**: Finds filter devices (already existed, enhanced)

### 2. Dub-Specific Parameter Setting Helpers

Precise control over dub-critical parameters:

- **`_set_filter_freq(ableton, track_index, device_index, norm_value)`**: Controls filter cutoff frequency
- **`_set_filter_reso(ableton, track_index, device_index, norm_value)`**: Controls filter resonance (for self-oscillation)
- **`_set_delay_feedback(ableton, track_index, device_index, norm_value)`**: Controls delay feedback amount
- **`_set_delay_time(ableton, track_index, device_index, norm_value)`**: Controls delay time
- **`_set_reverb_decay(ableton, track_index, device_index, norm_value)`**: Controls reverb decay time
- **`_set_reverb_dry_wet(ableton, track_index, device_index, norm_value)`**: Controls reverb dry/wet mix
- **`_set_eq_band_gain(ableton, track_index, device_index, band_index, norm_value)`**: Controls EQ band gain (for sub-bass)
- **`_normalize_freq(hz)` / `_denormalize_freq(norm)`**: Frequency normalization utilities

### 3. Enhanced `ultimate_arrangement_capture` Tool

Added new dub-specific parameters to the existing `ultimate_arrangement_capture` function:

```python
# Dub filter sweep
enable_dub_filter_sweep: bool = False
dub_filter_range: Optional[Tuple[float, float]] = None  # Frequency range in Hz, e.g., (50, 5000)
dub_filter_resonance: float = 0.7  # Resonance amount (0.0-1.0)

# Dub echo automation
enable_dub_echo: bool = True
dub_echo_feedback_range: Optional[Tuple[float, float]] = None  # Feedback amount range
dub_echo_time_range: Optional[Tuple[float, float]] = None  # Delay time range in ms

# Dub reverb automation
enable_dub_reverb: bool = False
dub_reverb_decay_range: Optional[Tuple[float, float]] = None  # Decay time range in seconds
dub_reverb_dry_wet_range: Optional[Tuple[float, float]] = None  # Dry/wet mix range

# Sub-bass EQ automation
enable_sub_bass_automation: bool = False
sub_bass_track_index: Optional[int] = None  # Track to apply sub-bass EQ to
sub_bass_eq_band: int = 0  # EQ band index (0-7 for EQ Eight)
sub_bass_gain_range: Optional[Tuple[float, float]] = None  # Gain range in dB
```

### 4. New `create_dub_arrangement` High-Level Tool

A dedicated tool for creating dub arrangements with pre-configured dub effects:

```python
@mcp.tool()
def create_dub_arrangement(
    ctx: Context,
    sections: List[Dict[str, Any]],  # Section definitions with dub-specific flags
    bpm: float = 90.0,
    bass_track_index: int = 0,
    sub_bass_band: int = 0,
    sub_bass_boost_db: float = 6.0,
    sub_bass_cut_db: float = -6.0,
    filter_transition_frequency_range: Tuple[float, float] = (50, 5000),
    filter_resonance: float = 0.75,
    echo_feedback_min: float = 0.3,
    echo_feedback_max: float = 0.85,
    echo_time_ms: float = 500,
    reverb_decay_min: float = 1.0,
    reverb_decay_max: float = 4.0,
    reverb_dry_wet_min: float = 0.0,
    reverb_dry_wet_max: float = 0.6,
    pre_count_bars: int = 4,
    use_metronome: bool = True,
    add_locators: bool = True,
    arm_strategy: str = "union",
) -> str:
```

## Section Configuration for `create_dub_arrangement`

The `sections` parameter accepts a list of dictionaries, each defining a section of your dub arrangement with these keys:

- `name`: Section name (e.g., "Intro", "Drop", "Breakdown")
- `scene_index`: Ableton scene index to capture
- `bars`: Duration in bars
- `is_dub_drop`: Boolean - triggers extra effects (filter sweeps, echo build-ups) at this section
- `is_breakdown`: Boolean - focuses on bass, enables reverb automation
- `unique_bassline`: Boolean - applies special sub-bass EQ processing

### Example Usage

```python
create_dub_arrangement(
    sections=[
        {"name": "Intro", "scene_index": 0, "bars": 16, 
         "is_dub_drop": False, "is_breakdown": False, "unique_bassline": False},
        {"name": "Verse1", "scene_index": 1, "bars": 16, 
         "is_dub_drop": False, "is_breakdown": False, "unique_bassline": True},
        {"name": "Drop1", "scene_index": 2, "bars": 32, 
         "is_dub_drop": True, "is_breakdown": False, "unique_bassline": True},
        {"name": "Breakdown", "scene_index": 3, "bars": 16, 
         "is_dub_drop": False, "is_breakdown": True, "unique_bassline": False},
        {"name": "Drop2", "scene_index": 2, "bars": 24, 
         "is_dub_drop": True, "is_breakdown": False, "unique_bassline": False},
        {"name": "Outro", "scene_index": 4, "bars": 16, 
         "is_dub_drop": False, "is_breakdown": True, "unique_bassline": False},
    ],
    bpm=85.0,
    bass_track_index=0,
    sub_bass_band=0,
    sub_bass_boost_db=8.0,
    filter_resonance=0.8,
    echo_feedback_min=0.4,
    echo_feedback_max=0.9,
    echo_time_ms=600,
    reverb_decay_min=1.5,
    reverb_decay_max=5.0
)
```

## Dub Automation Behaviors

### Filter Sweeps
- **Trigger**: On transitions between scenes where `enable_dub_filter_sweep=True`
- **Action**: Smooth sweep from low to high frequencies with adjustable resonance
- **Range**: Configurable from 50Hz to 5000Hz+ with 0.7-0.8 resonance for classic dub sound
- **Effect**: Creates dramatic tension and release, perfect for drops

### Echo/Feedback Automation
- **Trigger**: On dub drop sections and transitions
- **Action**: Feedback parameter animates from minimum to maximum and back
- **Range**: Configurable (typically 30-85% feedback for dub effects)
- **Effect**: Builds up endless repeats, then pulls back for clarity

### Delay Time Automation
- **Trigger**: When `dub_echo_time_range` is specified
- **Action**: Smooth changes in delay time
- **Range**: Configurable in milliseconds
- **Effect**: Creates rhythmic variations in echo patterns

### Reverb Automation
- **Trigger**: On breakdown sections
- **Action**: 
  - Decay: Smooth increase from minimum to maximum
  - Dry/Wet: Patterns like 0%-50%-0% for swells
- **Effect**: Creates spacious, atmospheric breaks

### Sub-Bass EQ Automation
- **Trigger**: On sections with `unique_bassline=True`
- **Action**: Boosts sub frequencies on beats, cuts between beats
- **Range**: Configurable boost (e.g., +6dB) and cut (e.g., -6dB)
- **Effect**: Pulsing bass that drives the rhythm

## Technical Integration

### Architecture
- All dub features are integrated into the consolidated `MCP_Server/arrangement_tools.py`
- The `create_dub_arrangement` tool calls `ultimate_arrangement_capture` with pre-configured dub parameters
- Device discovery and parameter setting are handled by helper functions

### How It Works
1. **Device Discovery**: Before automation, the system finds appropriate devices on tracks
2. **Parameter Identification**: Uses standard parameter indices (e.g., parameter 0 = Frequency for Auto Filter)
3. **Normalization**: Converts dub-specific values (Hz, dB, ms) to 0-1 range for Ableton
4. **Animation**: Applies values over multiple steps with small delays for smooth automation
5. **Context-Aware**: Automation is applied based on section type (drop, breakdown, etc.)

## Dub-Specific Return Data

Both `ultimate_arrangement_capture` (with dub parameters) and `create_dub_arrangement` return dub-specific analytics:

```json
{
    "status": "success",
    "scenes_captured": 5,
    ...
    "dub_metadata": {
        "dub_analysis": {
            "total_sections": 5,
            "dub_drop_count": 2,
            "breakdown_count": 2,
            "unique_bassline_count": 3,
            "dub_drop_indices": [2, 4],
            "breakdown_indices": [3, 5]
        },
        "dub_effects": {
            "filter_sweep_frequency_range_hz": [50, 5000],
            "filter_resonance": 0.75,
            "echo_feedback_range": [0.3, 0.85],
            "echo_time_ms": 500,
            "reverb_decay_range_s": [1.0, 4.0],
            "reverb_dry_wet_range": [0.0, 0.6],
            "sub_bass_band": 0,
            "sub_bass_range_db": [-6, 6]
        },
        "section_structure": [
            {
                "name": "Intro",
                "scene": 0,
                "bars": 16,
                "is_dub_drop": false,
                "is_breakdown": false,
                "unique_bassline": false
            },
            ...
        ]
    }
}
```

## Performance Considerations

- Device discovery uses caching (via `_ableton_cache`) to minimize redundant API calls
- Automation values are batched and sent with appropriate delays (50-200ms between steps)
- All dub automation happens within the main capture loop, adding minimal overhead
- Dub effects are applied selectively based on parameters (disabled by default)

## Future Enhancements

Potential additions for future versions:

1. **Dub Siren Sample Triggering**: Integration with specific samples or synth patches
2. **Spring Reverb Emulation**: Specialized reverb settings for vintage dub sound
3. **Tape Saturation**: Integration with saturation effects for warmth
4. **Sidechain Compression**: Duck effects when bass plays
5. **Dub Style Templates**: Pre-configured settings for different dub subgenres (roots, steppers, digital)
6. **Real-time Parameter Recording**: Capture actual parameter movements from hardware controllers

## Usage Recommendations

### For Classic Dub Sound:
- **Bass Track**: Use track 0 for bass, ensure it has an EQ Eight
- **Filter**: Auto Filter on drum bus and individual tracks
- **Delay**: Simple Delay or Echo on returns
- **Reverb**: Reverb on a return track
- **Sub-Bass Band**: Band 0 (lowest) on EQ Eight
- **Filter Range**: 50-5000Hz with 0.7-0.8 resonance
- **Echo Feedback**: 40-85% range
- **Reverb Decay**: 1-5 seconds

### Performance Tips:
- Start with `create_dub_arrangement` for a complete dub workflow
- Use `ultimate_arrangement_capture` directly for fine-tuned control
- Enable only 1-2 dub effects initially, then add more
- Test with shorter sections (4-8 bars) before full arrangements
- Monitor CPU usage - echo/reverb can be CPU-intensive

## Testing

The dub features can be tested with:

```bash
# Make sure Ableton is running with the Remote Script
# Then in Python:
from MCP_Server.arrangement_tools import create_dub_arrangement

# Or call via MCP Server tools
```

---

**Created**: July 2026  
**Status**: Implemented and integrated  
**Key Files**:
- `MCP_Server/arrangement_tools.py` - All dub features
- `MCP_Server/server.py` - Tool registration

**Maintainer Notes**:
- This implements the "bass and effects are key to dub" requirement
- All features are backward compatible
- No Ableton restarts required for testing
- Uses existing Remote Script infrastructure
