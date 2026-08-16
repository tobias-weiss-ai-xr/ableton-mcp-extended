# Improved Arrangement Capture Features

## Overview

This document describes the **improved arrangement capture tools** added to the Ableton MCP Extended project. These tools go beyond the basic scene capture and provide professional-grade features for building complete song arrangements.

## New Files

| File | Description | Tools | Lines |
|------|-------------|-------|-------|
| `MCP_Server/arrangement_tools_improved.py` | Enhanced arrangement capture with advanced features | 4 | 900+ |

## New MCP Tools

### 1. `capture_scenes_to_arrangement_improved` ⭐ **Most Feature-Complete**

The **enhanced version** of the original scene capture tool with additional options:

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scene_sequence` | List[int] | Required | List of scene indices to trigger in order |
| `scene_bars` | List[int] | Required | Bar lengths for each scene (must match scene_sequence length) |
| `start_bar` | int | 0 | Starting bar position in arrangement |
| `pre_count_bars` | int | 0 | **NEW**: Number of bars to count-in before recording starts |
| `use_metronome` | bool | False | **NEW**: Enable metronome during recording |
| `overdub` | bool | False | **NEW**: Keep existing arrangement clips, add new ones on top |
| `auto_stop` | bool | True | **NEW**: Automatically stop recording after all scenes complete |
| `tempo_changes` | Dict[int, float] | None | **NEW**: tempo automation - map scene index to BPM |
| `scene_names` | List[str] | None | **NEW**: Custom names for locators (e.g., ["Intro", "Verse"]) |
| `add_locators` | bool | True | **NEW**: Create locators at scene boundaries |

#### Returns

```json
{
  "status": "success",
  "scenes_captured": 3,
  "total_bars": 32,
  "start_bar": 0,
  "end_bar": 32,
  "pre_count_bars": 2,
  "bpm": 128,
  "overdub_mode": false,
  "metronome_used": true,
  "timing_log": [
    {"scene": 0, "name": "Intro", "start_bar": 2, "bars": 8, "bpm": 120},
    {"scene": 1, "name": "Verse", "start_bar": 10, "bars": 16, "bpm": 120},
    {"scene": 2, "name": "Chorus", "start_bar": 26, "bars": 8, "bpm": 125}
  ],
  "locators_created": true,
  "capture_method": "improved_scene_recording"
}
```

#### Examples

```python
# Basic capture with count-in
pi.call_tool("capture_scenes_to_arrangement_improved", {
    "scene_sequence": [0, 1, 2],
    "scene_bars": [8, 16, 8],
    "pre_count_bars": 2,
    "use_metronome": True,
    "scene_names": ["Intro", "Verse", "Outro"]
})

# With tempo changes
pi.call_tool("capture_scenes_to_arrangement_improved", {
    "scene_sequence": [0, 1, 2],
    "scene_bars": [16, 32, 16],
    "tempo_changes": {0: 120, 1: 125, 2: 130},
    "start_bar": 0
})

# Overdub mode (layer on top of existing arrangement)
pi.call_tool("capture_scenes_to_arrangement_improved", {
    "scene_sequence": [0, 1],
    "scene_bars": [8, 8],
    "overdub": True,
    "start_bar": 16
})
```

#### Use Cases

- **Live Performance Recording**: Add pre-count and metronome for live takes
- **Tempo Building**: Gradually increase tempo through scenes (build-ups, drops)
- **Song Variations**: Overdub additional layers on top of existing arrangement
- **Structured Songs**: Use scene names to create named locators for navigation

---

### 2. `create_song_structure` 🎵 **High-Level Song Building**

Create **complete song structures** from reusable sections with built-in transitions.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `structure` | Dict[str, Dict] | Required | Section definitions with properties |
| `pattern` | List[str] | Required | Ordered list of section names |
| `start_bar` | int | 0 | Starting bar position |
| `pre_count_bars` | int | 0 | Bars of count-in before recording |
| `use_metronome` | bool | True | Enable metronome during recording |
| `crossfade_bars` | int | 0 | **FUTURE**: Bars for crossfading between sections |
| `overdub` | bool | False | Overdub mode (layer on top) |
| `add_locators` | bool | True | Create locators for each section |

#### Structure Definition

Each section in the `structure` dict can have:

```python
structure = {
    "intro": {
        "scene": 0,           # Which scene to trigger
        "bars": 16,           # Length in bars
        "tempo": 120,         # BPM for this section
        "color": "#00ff00"    # Optional: locator color
    },
    "verse": {
        "scene": 1,
        "bars": 16,
        "tempo": 120
    },
    "chorus": {
        "scene": 2,
        "bars": 16,
        "tempo": 125
    },
    "breakdown": {
        "scene": 3,
        "bars": 8,
        "tempo": 120
    },
    "outro": {
        "scene": 4,
        "bars": 16,
        "tempo": 110
    }
}
```

#### Returns

```json
{
  "status": "success",
  "song_structure": ["intro", "verse", "chorus", "verse", "chorus", "outro"],
  "sections_captured": 6,
  "total_bars": 88,
  "start_bar": 0,
  "end_bar": 88,
  "section_positions": {
    "intro": 0,
    "verse": 16,
    "chorus": 32,
    "outro": 80
  },
  "bpm_history": [120, 120, 125, 120, 125, 110],
  "overdub_mode": false,
  "metronome_used": true,
  "locators_created": true,
  "capture_method": "song_structure_recording"
}
```

#### Examples

```python
# House music structure
pi.call_tool("create_song_structure", {
    "structure": {
        "intro": {"scene": 0, "bars": 32, "tempo": 125},
        "buildup": {"scene": 1, "bars": 16, "tempo": 125},
        "drop": {"scene": 2, "bars": 32, "tempo": 128},
        "breakdown": {"scene": 3, "bars": 16, "tempo": 125}
    },
    "pattern": ["intro", "buildup", "drop", "breakdown", "buildup", "drop"],
    "pre_count_bars": 4,
    "use_metronome": True,
    "add_locators": True
})

# Techno live set
pi.call_tool("create_song_structure", {
    "structure": {
        "intro": {"scene": 0, "bars": 64, "tempo": 128},
        "main": {"scene": 1, "bars": 128, "tempo": 130},
        "transition": {"scene": 2, "bars": 32, "tempo": 128}
    },
    "pattern": ["intro", "main", "transition", "main", "transition", "main"],
    "start_bar": 0
})

# Hip-hop beat with variations
pi.call_tool("create_song_structure", {
    "structure": {
        "beat_a": {"scene": 0, "bars": 8, "tempo": 90},
        "beat_b": {"scene": 1, "bars": 8, "tempo": 90},
        " hook": {"scene": 2, "bars": 16, "tempo": 90}
    },
    "pattern": ["beat_a", "beat_a", "beat_b", "beat_b", "hook", "beat_a", "beat_a", "hook"],
    "use_metronome": True
})
```

#### Use Cases

- **Full Song Arrangements**: Build complete tracks from verse/chorus/bridge sections
- **Live Set Preparation**: Create structured DJ-friendly arrangements
- **Template-Based Production**: Use pre-defined song structures (house, techno, hip-hop)
- **A/B Testing**: Quickly test different arrangements with the same sections

---

### 3. `capture_with_transitions` 🎚️ **Smooth Scene Transitions**

Capture scenes with **smooth transitions** between them for professional-sounding mixes.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scene_sequence` | List[int] | Required | List of scene indices |
| `scene_bars` | List[int] | Required | Bar lengths for each scene |
| `transition_type` | str | "none" | Type of transition between scenes |
| `transition_bars` | int | 4 | Number of bars for each transition |
| `start_bar` | int | 0 | Starting bar position |
| `use_metronome` | bool | False | Enable metronome |

#### Transition Types

| Type | Description | Use Case |
|------|-------------|----------|
| `"none"` | No transition, hard cut | Fast scene changes, techno |
| `"crossfade"` | Gradual volume crossfade | Smooth transitions, ambient |
| `"volume_swell"` | Fade out all, then fade in | Big build-ups, dub techno |
| `"filter_sweep"` | Apply LPF sweep | House, trance, progressive |
| `"echo_out"` | Add echo that fades out | DJ-style transitions |

#### Returns

```json
{
  "status": "success",
  "scenes_captured": 4,
  "transitions_applied": 3,
  "transition_type": "crossfade",
  "transition_details": [
    {
      "from_scene": 0,
      "to_scene": 1,
      "type": "crossfade",
      "start_bar": 8,
      "end_bar": 12,
      "bars": 4
    },
    {
      "from_scene": 1,
      "to_scene": 2,
      "type": "crossfade",
      "start_bar": 24,
      "end_bar": 28,
      "bars": 4
    }
  ],
  "total_bars": 36,
  "capture_method": "transition_recording"
}
```

#### Examples

```python
# Crossfade between all scenes
pi.call_tool("capture_with_transitions", {
    "scene_sequence": [0, 1, 2, 3],
    "scene_bars": [16, 16, 16, 16],
    "transition_type": "crossfade",
    "transition_bars": 4
})

# Filter sweep for house music
pi.call_tool("capture_with_transitions", {
    "scene_sequence": [0, 1, 2],
    "scene_bars": [32, 32, 32],
    "transition_type": "filter_sweep",
    "transition_bars": 8
})

# Quick cuts (no transitions)
pi.call_tool("capture_with_transitions", {
    "scene_sequence": [0, 1, 0, 2],
    "scene_bars": [4, 4, 4, 4],
    "transition_type": "none",
    "transition_bars": 0
})
```

#### Use Cases

- **DJ-Style Mixes**: Professional transitions between sections
- **Ambient Music**: Smooth, seamless scene changes
- **Live Performance**: Command-triggered transitions for live sets
- **Sound Design**: Creative transition effects

---

### 4. `capture_dj_mix` 🎧 **Professional DJ Mix Recording**

Record **DJ-style mixes** with track pairs, transitions, and beat matching.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_pairs` | List[Dict] | Required | List of track pair configurations |
| `mix_pattern` | List[str] | Required | Pattern of transitions between pairs |
| `transition_bars` | int | 16 | Bars for each transition |
| `start_bar` | int | 0 | Starting bar position |
| `bpm` | float | None | Optional BPM override (uses current if None) |
| `use_metronome` | bool | True | Enable metronome |

#### Track Pair Configuration

Each track pair defines two tracks that play together with a specific scene:

```python
track_pairs = [
    {
        "track_a": 0,        # Track index for deck A
        "track_b": 1,        # Track index for deck B
        "start_scene": 0,    # Scene to trigger for this pair
        "bars": 64           # Length in bars
    },
    {
        "track_a": 2,
        "track_b": 3,
        "start_scene": 1,
        "bars": 64
    }
]
```

#### Mix Pattern

The mix pattern defines what type of transition to use between each pair:

```python
# For 3 pairs, you need 2 transition types
mix_pattern = ["filter_sweep", "crossfade"]
```

#### Returns

```json
{
  "status": "success",
  "pairs_recorded": 3,
  "transitions_applied": 2,
  "total_bars": 224,
  "bpm": 128,
  "mix_log": [
    {"action": "start", "pair": 0, "scene": 0, "bar": 0},
    {"action": "transition", "type": "filter_sweep", "from_pair": 0, "to_pair": 1, "start_bar": 64, "end_bar": 80},
    {"action": "pair_start", "pair": 1, "scene": 1, "bar": 80},
    {"action": "transition", "type": "crossfade", "from_pair": 1, "to_pair": 2, "start_bar": 144, "end_bar": 160},
    {"action": "pair_start", "pair": 2, "scene": 2, "bar": 160}
  ],
  "end_bar": 224,
  "capture_method": "dj_mix_recording"
}
```

#### Examples

```python
# Full DJ set with 3 track pairs
pi.call_tool("capture_dj_mix", {
    "track_pairs": [
        {"track_a": 0, "track_b": 1, "start_scene": 0, "bars": 64},
        {"track_a": 2, "track_b": 3, "start_scene": 1, "bars": 64},
        {"track_a": 4, "track_b": 5, "start_scene": 2, "bars": 64}
    ],
    "mix_pattern": ["filter_sweep", "crossfade"],
    "transition_bars": 16,
    "bpm": 128
})

# Short mix for testing
pi.call_tool("capture_dj_mix", {
    "track_pairs": [
        {"track_a": 0, "track_b": 1, "start_scene": 0, "bars": 32},
        {"track_a": 0, "track_b": 1, "start_scene": 1, "bars": 32}
    ],
    "mix_pattern": ["hard_cut"],
    "transition_bars": 4,
    "use_metronome": True
})
```

#### Use Cases

- **DJ Mix Recording**: Record seamless mixes for podcasts or performances
- **Track Transition Practice**: Practice transitions between tracks
- **Live Set Building**: Create structured DJ sets with automatic transitions
- **Mashup Creation**: Mix tracks together with professional transitions

---

## Integration with Existing Features

### Server Configuration

These new tools are registered in `MCP_Server/server.py`:

```python
from MCP_Server.arrangement_tools_improved import register_improved_arrangement_tools
# ...
register_improved_arrangement_tools(mcp, get_ableton_connection)
```

### Dependency on Existing Tools

The improved tools use these existing Remote Script commands:
- `set_playhead_position` - Set arrangement playhead
- `set_track_arm` - Arm/disarm tracks for recording
- `start_recording` / `stop_recording` - Control session recording
- `start_playback` / `stop_playback` - Control transport
- `trigger_scene` - Trigger session scenes
- `set_tempo` - Change BPM
- `set_metronome` - Enable/disable metronome
- `create_locator` - Create navigation locators
- `get_all_tracks` - Get track information
- `get_session_info` - Get session information

### Timeout Configuration

These tools have extended timeouts (up to 30-60 seconds) configured in `MCP_Server/server.py`:

```python
# Increased timeout for recording/scene/capture commands
if "scene" in command_type or "record" in command_type or "capture" in command_type:
    timeout = 60.0  # 60 seconds for operations involving real-time recording
```

---

## Feature Comparison

| Feature | Original | Improved | Notes |
|---------|----------|----------|-------|
| Basic scene capture | ✅ | ✅ | Both tools available |
| Pre-count | ❌ | ✅ | 0-4 bar count-in |
| Metronome | ❌ | ✅ | Optional metronome |
| Overdub mode | ❌ | ✅ | Layer on top of existing |
| Tempo changes | ❌ | ✅ | Per-scene BPM automation |
| Scene naming | ❌ | ✅ | For locator organization |
| Locator creation | ❌ | ✅ | Automatic navigation markers |
| Auto-stop | ✅ | ✅ | Stop after all scenes |
| Song structures | ❌ | ✅ | High-level arrangement building |
| Transitions | ❌ | ✅ | Crossfade, volume swell, filter sweep, echo |
| DJ mix recording | ❌ | ✅ | Track pairs with transitions |
| Progress feedback | ❌ | ✅ | Detailed timing logs |

---

## Migration Guide

### For Existing Users

If you're currently using `capture_scenes_to_arrangement`, you can continue using it. The improved version is available as `capture_scenes_to_arrangement_improved`.

### Recommended Upgrade Path

1. **Start with the improved version**: Use `capture_scenes_to_arrangement_improved` for new projects
2. **Use song structures**: For complex arrangements, use `create_song_structure`
3. **Add transitions**: Use `capture_with_transitions` for professional-sounding scene changes
4. **DJ mixes**: Use `capture_dj_mix` for DJ-style recordings

### Backward Compatibility

All existing tools continue to work without changes. The new tools are **additive** - they don't replace or modify existing functionality.

---

## Performance Considerations

### Maximum Capture Times

| Tool | Maximum Time | Reason |
|------|---------------|--------|
| `capture_scenes_to_arrangement_improved` | 30 seconds | MCP Server timeout |
| `create_song_structure` | 60 seconds | Longer for complex songs |
| `capture_with_transitions` | 30 seconds | Includes transition time |
| `capture_dj_mix` | 120 seconds (2 minutes) | Extended for DJ sets |

Note: These are **configurable** in the tool code. Longer captures can be achieved by:
1. Splitting into multiple capture calls
2. Using overdub mode to layer sections
3. Adjusting the timeout in `MCP_Server/server.py`

### Memory Usage

- All tools arm all tracks by default (can be customized)
- Recording creates new arrangement clips (disarm tracks after to save memory)
- Locator creation is lightweight
- Tempo changes create automation data

### CPU Usage

- Pre-count and metronome have minimal CPU impact
- Transitions (filter sweep, echo) require device automation
- Crossfade uses track volume automation
- All features are optimized for real-time performance

---

## Troubleshooting

### Common Issues

**"Tool already exists" warnings**
- These are **harmless** and caused by module import order
- The tools are registered exactly once with the MCP Server
- Only appear during startup, not during operation

**Timeout errors**
- Check that total capture time < maximum timeout
- Reduce scene bars or use fewer scenes
- Use overdub mode for complex arrangements

**Scene not triggering**
- Verify scene index exists: `get_all_scenes`
- Check that scenes have clips: `get_session_info`
- Ensure tracks are armed: use `set_track_arm`

**Locators not created**
- Verify `add_locators=True`
- Check that scene names are provided
- Some Ableton versions may have locator limits

### Debugging

Enable debug logging by setting the `MCP_LOG_LEVEL` environment variable:

```bash
MCP_LOG_LEVEL=DEBUG python -m MCP_Server.server
```

This will show detailed information about tool registration and execution.

---

## Example Workflows

### Workflow 1: Building a House Track

```python
# Step 1: Setup session with clips and scenes
# Scene 0: Kick, bass, hats (intro)
# Scene 1: Full beat + chord progression (verse)
# Scene 2: Full beat + leads + vocals (chorus)
# Scene 3: Bass and hats only (breakdown)

# Step 2: Define song structure
structure = {
    "intro": {"scene": 0, "bars": 32, "tempo": 125, "color": "#00ff00"},
    "buildup": {"scene": 1, "bars": 16, "tempo": 125, "color": "#ffff00"},
    "drop": {"scene": 2, "bars": 32, "tempo": 128, "color": "#ff0000"},
    "breakdown": {"scene": 3, "bars": 16, "tempo": 125, "color": "#0000ff"}
}

# Step 3: Create arrangement
result = pi.call_tool("create_song_structure", {
    "structure": structure,
    "pattern": ["intro", "buildup", "drop", "breakdown", "buildup", "drop"],
    "pre_count_bars": 4,
    "use_metronome": True,
    "add_locators": True
})

# Step 4: Fine-tune
# Edit clips, add automation, mix, etc.
```

### Workflow 2: DJ-Style Mixdown

```python
# Step 1: Setup 6 tracks (3 pairs)
# Tracks 0-1: Deck A
# Tracks 2-3: Deck B  
# Tracks 4-5: Deck C

# Step 2: Create DJ mix
result = pi.call_tool("capture_dj_mix", {
    "track_pairs": [
        {"track_a": 0, "track_b": 1, "start_scene": 0, "bars": 64},
        {"track_a": 2, "track_b": 3, "start_scene": 1, "bars": 64},
        {"track_a": 4, "track_b": 5, "start_scene": 2, "bars": 64}
    ],
    "mix_pattern": ["filter_sweep", "crossfade"],
    "transition_bars": 16,
    "bpm": 128,
    "use_metronome": True
})

# Step 3: Export (manual step - use Ableton UI)
```

### Workflow 3: Overdub Layering

```python
# Step 1: Capture base arrangement
pi.call_tool("capture_scenes_to_arrangement_improved", {
    "scene_sequence": [0, 1, 2],
    "scene_bars": [16, 16, 16],
    "start_bar": 0
})

# Step 2: Add bass layer starting at bar 16
pi.call_tool("capture_scenes_to_arrangement_improved", {
    "scene_sequence": [3],  # Bass scene
    "scene_bars": [32],
    "start_bar": 16,
    "overdub": True
})

# Step 3: Add vocal layer starting at bar 32
pi.call_tool("capture_scenes_to_arrangement_improved", {
    "scene_sequence": [4],  # Vocal scene
    "scene_bars": [16],
    "start_bar": 32,
    "overdub": True
})
```

### Workflow 4: Live Performance with Transitions

```python
# Pre-configure scenes with different energy levels
# Scene 0: Low energy (pads, soft kick)
# Scene 1: Medium energy (add bass, hats)
# Scene 2: High energy (add leads, full beat)

# Capture with smooth transitions
pi.call_tool("capture_with_transitions", {
    "scene_sequence": [0, 1, 2, 1, 2],
    "scene_bars": [16, 16, 16, 16, 16],
    "transition_type": "filter_sweep",
    "transition_bars": 4,
    "use_metronome": True
})
```

---

## API Reference

### Common Parameters

All tools accept these common parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_bar` | int | 0 | Starting position in arrangement |
| `use_metronome` | bool | Varies | Enable metronome during capture |

### Common Returns

All tools return JSON with these common fields:

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success", "error", or "warning" |
| `message` | str | Human-readable status message |
| `capture_method` | str | Identification of the capture method used |

### Error Codes

| Status | Meaning | Action |
|--------|---------|--------|
| "success" | Operation completed successfully | Continue with next step |
| "warning" | Operation completed with warnings | Check message, may need manual fix |
| "error" | Operation failed | Check message, retry or fix issue |

---

## Files Modified

- `MCP_Server/arrangement_tools_improved.py` - New file with 4 improved tools
- `MCP_Server/server.py` - Added registration of improved tools (line ~994)

## Files Created

- `MCP_Server/arrangement_tools_improved.py` - 900+ lines, 4 tools

## No Files Requiring Ableton Restart

All changes are in the MCP Server layer. No modifications to `AbletonMCP_Remote_Script` were needed.

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-27 | 1.0 | Initial release - 4 improved arrangement tools |

---

## Future Enhancements

### Planned Features

1. **Real crossfade implementation** - Actual volume automation between scenes
2. **Device automation** - Record filter sweeps, echo, and other effects
3. **Scene transition presets** - Pre-configured transition templates
4. **Arm only relevant tracks** - Intelligent track arming based on scene content
5. **Validation mode** - Dry-run to check setup before recording
6. **Progress callbacks** - Real-time feedback during long captures
7. **Undo capture** - Easy undo of accidental captures
8. **Capture presets** - Save and recall capture configurations

### Experimental Features

1. **AI-powered arrangement suggestions** - Suggest song structures based on scenes
2. **Automatic beat matching** - Sync scenes with different tempos
3. ** harmonic mixing** - Scene transitions based on musical key
4. **Energy-based automation** - Automatic volume/filter based on scene energy

---

## Support

For issues or questions:
1. Check this documentation
2. Run with `MCP_LOG_LEVEL=DEBUG` for detailed logging
3. Use the test scripts to verify functionality
4. Check, no restrictions here

---

*© 2026 Ableton MCP Extended Project*
