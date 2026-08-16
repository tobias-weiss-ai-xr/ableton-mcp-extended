# Arrangement View Integration & End-to-End Mix Production

This document describes the new **Arrangement View** capabilities added to Ableton MCP Extended, enabling complete end-to-end mix production workflows.

## Overview

The project now supports **complete arrangement view control**, allowing AI agents to:

1. ✅ **Create sessions** with tracks, instruments, clips, and scenes
2. ✅ **Record/Capture session into arrangement view** - non-real-time and real-time
3. ✅ **Edit arrangement clips** - create, move, copy, delete, crop, split, quantize
4. ✅ **Add arrangement automation** - volume, panning, device parameters across time
5. ✅ **Apply mix templates** - dub techno, house build, ambient swell, etc.
6. ✅ **Polish & finalize mixes** - master FX, optimization, level balancing
7. ✅ **Prepare for manual fine-tuning** - human takes over with a professional starting point

## New Files

### MCP Server Tools
- `MCP_Server/arrangement_tools.py` - 51KB, 20+ new arrangement tools
- `MCP_Server/optimization_tools.py` - 42KB, 15+ optimization tools

### Scripts
- `scripts/e2e_mix_producer.py` - Full end-to-end workflow (48KB)
- `scripts/quick_arrangement_demo.py` - Simplified demo (7KB)

### Remote Script Updates
- `AbletonMCP_Remote_Script/__init__.py` - Added 15+ arrangement view methods

## Quick Start

### 1. Run the Quick Demo

```bash
python scripts/quick_arrangement_demo.py
```

This will:
- Create 4 tracks (Drums, Bass, Chords, Lead)
- Add simple patterns to each
- Capture session to arrangement
- Add filter sweeps and volume automation
- Polish and prepare for manual editing

Time: ~2-3 minutes

### 2. Run the Full E2E Producer

```bash
python scripts/e2e_mix_producer.py
```

This runs the complete 7-step workflow:
1. Setup Session (tracks, instruments, returns)
2. Create Content (8 tracks, clips, scenes)
3. Session to Arrangement (capture session)
4. Arrange & Edit (structure, transitions)
5. Mix Automation (filter sweeps, volume curves)
6. Polish (master FX, compression, limiting)
7. Save & Ready (prep for manual fine-tuning)

Time: ~5-8 minutes

Run specific steps:
```bash
python scripts/e2e_mix_producer.py --start 4 --end 5  # Just arrange and automate
```

## New MCP Tools

### Arrangement Tools

#### Session to Arrangement
```python
# Non-real-time capture (instant)
capture_and_insert_arrangement(start_bar=0, length_bars=64, quantize=True)

# Real-time recording
record_session_to_arrangement(start_scene=0, end_scene=8, scene_duration_bars=16)

# Create arrangement from session with transitions
create_arrangement_from_session(scene_order=[0,1,2,3], scene_length_bars=16, 
                                 include_transitions=True, transition_bars=4)
```

#### Arrangement Clip Manipulation
```python
# Get all arrangement clips
get_arrangement_clips()
get_arrangement_clips(track_index=0)  # Filter by track

# Duplicate, move, delete
duplicate_arrangement_clip(track_index=0, clip_index=0, new_bar_position=16)
move_arrangement_clip(track_index=0, clip_index=0, new_bar_position=32)
delete_arrangement_clip(track_index=0, clip_index=0)

# Crop, split, quantize
crop_arrangement_clip(track_index=0, clip_index=0, start_bar=0, end_bar=16)
split_arrangement_clip(track_index=0, clip_index=0, split_bar=8)
quantize_arrangement_clip(track_index=0, clip_index=0, amount=1.0)

# Time range operations
duplicate_time_range(start_bar=0, end_bar=16, insert_position=16)
delete_time_range(start_bar=16, end_bar=24)
insert_silence(position_bar=0, length_bars=8)
consolidate_arrangement(start_bar=0, end_bar=64)
```

#### Arrangement Automation
```python
# Single automation point
add_arrangement_automation_point(track_index=0, device_index=0, 
                                  parameter_index=0, bar_position=16, value=0.8)

# Track-level automation (volume, pan, sends)
add_arrangement_track_automation(track_index=0, automation_type="volume",
                                  bar_position=0, value=0.8)
add_arrangement_track_automation(track_index=0, automation_type="pan",
                                  bar_position=16, value=-0.3)
add_arrangement_track_automation(track_index=0, automation_type="send_0",
                                  bar_position=32, value=0.5)

# Automation curves
create_automation_curve(track_index=0, device_index=0, parameter_index=0,
                        points=[{"bar": 0, "value": 0}, {"bar": 16, "value": 1}],
                        curve_type="s_curve")

# Convenience tools
create_volume_automation_ramp(track_index=0, start_bar=0, end_bar=16,
                               start_volume=0.0, end_volume=0.8, curve="s_curve")

create_filter_sweep(track_index=0, start_bar=16, end_bar=24,
                    start_freq=100.0, end_freq=5000.0, curve="exponential")

# Mix templates
apply_mix_automation_template(template_name="dub_techno", intensity=0.8)
# Available: dub_techno, house_build, ambient_swell, minimal_pulse, drum_and_bass

# Polish
polish_arrangement_mix(master_volume=0.85, apply_limiter=True, apply_compression=True)
```

#### Arrangement Navigation
```python
# Scroll and zoom
set_arrangement_view_position(bar=32, beat=0)
set_arrangement_zoom(zoom_level=0.5)  # 0.1-2.0
```

#### DJ Mix Tools
```python
# Automated DJ-style mix arrangement
arrange_dj_mix(track_plans=[{"track": 0, "clips": [0,1,2,3]}], 
               mix_length_bars=256, transition_bars=32)
```

### Optimization Tools

#### Level Balancing
```python
# Auto-balance all track levels
auto_balance_levels(target_headroom_db=-6.0, reference_track=None, max_boost_db=6.0)

# Normalize individual clip gain
normalize_clip_gain(track_index=0, clip_index=0, target_peak_db=-6.0)
```

#### Frequency Analysis
```python
# Find frequency collisions
analyze_frequency_collisions(track_indices=[0,1,2,3])

# Get EQ suggestions
suggest_eq_settings(track_index=0, instrument_type="kick")  # Auto-detects from track name
```

#### Dynamics
```python
# Compression suggestions
suggest_compression_settings(track_index=1, instrument_type="bass")

# Sidechain setup guidance
setup_sidechain_compression(source_track=0, target_track=1)  # Kick -> Bass
```

#### Mix Bus
```python
# Setup complete mix bus processing
setup_mix_bus_processing(glue_compression=True, saturation=True, eq=True, limiter=True)

# Individual components
setup_mix_bus_processing(glue_compression=True, limiter=True)  # Minimal
```

#### Performance
```python
# Optimize CPU usage
optimize_cpu_usage(freeze_tracks=[2,3,4], disable_unused_devices=True)

# Get performance metrics
get_performance_metrics()
```

## Workflow Patterns

### Pattern 1: Quick Session to Arrangement
```python
# Create a session
delete_all_tracks()
for i in range(4):
    create_midi_track(i)
    load_instrument(i, INSTRUMENTS[i])

# Create some clips and scenes
# ... (add your content)

# Capture to arrangement (instant, non-real-time)
capture_and_insert_arrangement(start_bar=0, length_bars=32, quantize=True)

# Add some automation
create_filter_sweep(0, 8, 16)  # Filter sweep on track 0, bars 8-16
create_volume_automation_ramp(-1, 28, 32, 0.8, 0.0)  # Master fade out

# Polish
polish_arrangement_mix(master_volume=0.85, apply_limiter=True)
```

### Pattern 2: Real-Time Session Recording
```python
# Set up scene triggering
for scene_idx in range(8):
    trigger_scene(scene_idx)  # Or use scene follow actions

# Start recording
start_recording()
start_playback()

# Let it play through
# ... wait for scenes to trigger

# Stop and you have arrangement clips
stop_recording()
stop_playback()

# The session clips are now captured as arrangement clips
```

### Pattern 3: Arrangement Editing
```python
# Get current arrangement
clips = get_arrangement_clips()

# Duplicate the first section
for clip in clips["arrangement_clips"][:10]:
    duplicate_arrangement_clip(clip["track_index"], clip["clip_index"], 
                                new_bar_position=clip["position"]/4.0 + 32)

# Insert silence between sections
insert_silence(32, 4)

# Add time-stretched transition
duplicate_time_range(0, 4, 32)
```

### Pattern 4: Professional Mix Automation
```python
# Fade in
create_volume_automation_ramp(-1, 0, 8, 0.0, 0.8, curve="s_curve")

# Build up to drop (filter sweep + volume)
create_filter_sweep(0, 24, 32, start_freq=100, end_freq=5000)
create_filter_sweep(1, 24, 32, start_freq=80, end_freq=1000)

for track in [0, 1, 5]:  # Drums and percussion
    create_volume_automation_ramp(track, 28, 32, 0.8, 1.0, curve="s_curve")

# Breakdown - drop volume
for track in [2, 3, 4, 6, 7]:  # Melodic elements
    create_volume_automation_ramp(track, 64, 72, 0.8, 0.3, curve="linear")

# Outro fade
create_volume_automation_ramp(-1, total_bars - 8, total_bars, 0.8, 0.0, curve="s_curve")

# Apply mix template
apply_mix_automation_template("dub_techno", intensity=0.7)
```

### Pattern 5: Total Optimization
```python
# Auto-balance levels
auto_balance_levels(target_headroom_db=-6.0)

# Optimize frequency spectrum
result = analyze_frequency_collisions()
for suggestion in result["suggestions"]:
    print(suggestion["recommendation"])

# Get EQ settings for each track
for track_idx in range(8):
    eq_settings = suggest_eq_settings(track_idx)
    print(f"Track {track_idx}: {eq_settings['recommended_settings']}")

# Setup mix bus
setup_mix_bus_processing()

# Final polish
polish_arrangement_mix()
```

## Architecture

### Dual-Track Approach

The system maintains **two parallel command paths**:

1. **TCP (Port 9877)** - Reliable, request/response
   - Session view operations
   - Arrangement inspection
   - Complex operations
   - All `get_*` commands

2. **UDP (Port 9878)** - Fire-and-forget, low latency
   - Parameter automation updates
   - Track volume/pan/mute changes
   - Device parameter changes
   - Clip triggering

### Remote Script API Limitations

Ableton Live's Remote Script API has some limitations:

- ★ **Can do**: Session to Arrangement capture (non-real-time)
- ★ **Can do**: Real-time recording with transport
- ★ **Can do**: Arrangement clip manipulation
- ★ **Can do**: Automation envelope editing
- ✅ **Can do**: Time range operations (copy, delete, insert)
- ❌ **Cannot do**: Direct arrangement view scrolling (workaround via app.view)
- ❌ **Cannot do**: Direct audio export (must use Manual Export or Max4Live)

### Workarounds Implemented

1. **Arrangement View Navigation**: Uses `app.view.scroll_to()` via `_song.app.view`
2. **Session to Arrangement**: Uses `capture_and_insert_midi()` or real-time recording
3. **Clip Quantization in Arrangement**: Quantizes notes within arrangement clips
4. **Time Range Operations**: Uses Live's `_song.duplicate_time_range()`, `_song.delete_time_range()`

## Mix Finalization Checklist

Before exporting your mix:

### 1. Technical Quality
- [ ] Check for clipping (master output meter)
- [ ] Ensure consistent headroom (-6dB to -3dB)
- [ ] Verify all automation curves are smooth
- [ ] Check all clips are properly trimmed and aligned

### 2. Musical Balance
- [ ] Kick and bass are balanced
- [ ] Vocals/leads cut through the mix
- [ ] Panning creates good stereo image
- [ ] Frequency spectrum is balanced (no mud, no harshness)

### 3. Dynamics
- [ ] Appropriate dynamic range
- [ ] Punch and impact where needed
- [ ] Smooth transitions between sections
- [ ] Consistent levels across the arrangement

### 4. Effects
- [ ] Reverb and delay tails don'tMask important elements
- [ ] Effects are consistent across scenes
- [ ] Automation on effects creates movement
- [ ] Master effects provide cohesion

### Using MCP Tools for Quality Checks:

```python
# Check levels
auto_balance_levels(-6.0, max_boost_db=0.0)  # dry run only

# Check frequency collisions
analyze_frequency_collisions()

# Get performance metrics (CPU usage, etc.)
get_performance_metrics()

# Get current arrangement
clips = get_arrangement_clips()
print(f"Total arrangement clips: {len(clips['arrangement_clips'])}")
```

## Audio Export Workflow

Since Remote Script cannot directly export audio, here are the options:

### Option 1: Manual Export (Recommended)
1. Open Ableton Live
2. Switch to Arrangement View (Tab)
3. Set loop region to cover the entire arrangement
4. Go to File > Export Audio/Video
5. Choose export settings:
   - Format: WAV or AIFF
   - Sample Rate: 44.1kHz or 48kHz
   - Bit Depth: 24-bit
   - Normalize: Off
   - Convert to Mono: Off
6. Click Export

### Option 2: Max for Live Device (Automation)
The project includes a Max for Live device that can trigger exports:

1. Load `max_devices/audio_export_device.maxpat` on a MIDI track
2. Use MCP to trigger the export:
```python
# Trigger Max for Live export
# Note: This requires manual bang trigger in current implementation
fire_clip(track_index_with_max, clip_index)
```

### Option 3: Command Line (Advanced)
Use Ableton's command line interface (CLI) or AppleScript on macOS to automate export.

## Example: Complete Dub Techno Mix

```python
# Step 1: Setup
from agentic_mix.tools import _client

tcp = lambda cmd, p=None: _client.tcp_command(cmd, p or {})

tcp("delete_all_tracks")

# Create 5 tracks
for i in range(5):
    tcp("create_midi_track", {"index": i})

# Load instruments
instruments = [
    "query:Drums#FileId_58622",
    "query:Sounds#Bass:FileId_49654",
    "query:Sounds#Pad:FileId_45564",
    "query:Sounds#Synth%20Lead:FileId_50175",
    "query:AudioFx#Hybrid%20Reverb",
]
for i, uri in enumerate(instruments):
    tcp("load_browser_item", {"track_index": i, "item_uri": uri})

# Configure
for i, name in enumerate(["Drums", "Bass", "Chords", "Lead", "Reverb"]):
    tcp("set_track_name", {"track_index": i, "name": name})

tcp("set_tempo", {"tempo": 126})
tcp("set_master_volume", {"volume": 0.85})

# Step 2: Create Content
from MCP_Server.server import create_drum_pattern, create_chord_notes

# Drums
create_drum_pattern(None, 0, 0, "one_drop", 16)

# Bass
notes = []
for b in range(0, 64, 4):
    notes.append({"pitch": 36, "start_time": b, "duration": 2.0, "velocity": 90})
tcp("create_clip", {"track_index": 1, "clip_index": 0, "length": 16})
tcp("add_notes_to_clip", {"track_index": 1, "clip_index": 0, "notes": notes})

# Chords
create_chord_notes(None, 2, 0, 48, "min7", 0, 8.0, 70)
tcp("create_clip", {"track_index": 2, "clip_index": 0, "length": 16})

# Lead (simple)
lead_notes = []
for b in range(0, 64, 2):
    lead_notes.append({"pitch": 60 + (b % 8), "start_time": b, "duration": 1.0, "velocity": 75})
tcp("create_clip", {"track_index": 3, "clip_index": 0, "length": 16})
tcp("add_notes_to_clip", {"track_index": 3, "clip_index": 0, "notes": lead_notes})

# Create 4 scenes
tcp("create_scene", {"index": 0})
tcp("set_scene_name", {"scene_index": 0, "name": "Intro"})
tcp("create_scene", {"index": 1})
tcp("set_scene_name", {"scene_index": 1, "name": "Main"})

# Step 3: Capture to Arrangement
tcp("capture_and_insert_arrangement", {"start_bar": 0, "length_bars": 64, "quantize": True})

# Step 4: Add Automation
# Filter sweep on bass
tcp("create_filter_sweep", {
    "track_index": 1,
    "start_bar": 16,
    "end_bar": 24,
    "start_freq": 50,
    "end_freq": 5000,
})

# Volume automation
tcp("create_volume_automation_ramp", {
    "track_index": -1,
    "start_bar": 0,
    "end_bar": 8,
    "start_volume": 0.0,
    "end_volume": 0.8,
})

# Reverb send on chords
tcp("set_send_amount", {"track_index": 2, "send_index": 4, "amount": 0.4})

# Step 5: Polish
tcp("polish_arrangement_mix", {
    "master_volume": 0.85,
    "apply_limiter": True,
    "apply_compression": True,
})

# Step 6: Apply Dub Techno Template
tcp("apply_mix_automation_template", {
    "template_name": "dub_techno",
    "intensity": 0.8,
})

print("Dub Techno mix ready for manual fine-tuning!")
```

## Troubleshooting

### Common Issues

**"Unknown command: capture_and_insert_arrangement"**
- Make sure you've updated the Remote Script (`AbletonMCP_Remote_Script/__init__.py`)
- Restart Ableton Live to reload the Remote Script

**Commands timing out**
- Some operations take time. Increase timeout in `AbletonTCPClient`
- Check Ableton's CPU usage - freeze tracks if needed

**Automation not appearing**
- Make sure the track has a device at the specified index
- Check that the parameter index is correct for that device
- Try using `get_device_parameters` to verify parameter indices

**Arrangement clips not appearing**
- Try both `capture_and_insert_arrangement` and real-time recording
- Check that clips exist in session view first
- Ensure the session clips are playing when you trigger recording

### Debugging Tips

1. **Check connection**:
```python
tcp("get_session_info")
```

2. **Check tracks**:
```python
tcp("get_all_tracks")
```

3. **Check arrangement clips**:
```python
tcp("get_arrangement_clips")
```

4. **Check logs**:
```bash
# Remote Script logs are in Ableton's Console (Ctrl+Alt+Shift+C on Windows)
# MCP server logs are in your terminal
```

## Performance Tips

1. **Processing Order**: Run generation first, then automation, then export
2. **Batch Operations**: Use `batch_set_device_parameters` for multiple changes
3. **Freeze Tracks**: Use `optimize_cpu_usage(freeze_tracks=[...])` for heavy sessions
4. **Disable Unused Devices**: Bypass devices on muted tracks
5. **Small Buffer for Editing**: Use larger buffer (512-1024) for editing, smaller (128-256) for recording

## API Reference

For complete API documentation, see:
- `MCP_Server/arrangement_tools.py` - All arrangement tools
- `MCP_Server/optimization_tools.py` - All optimization tools
- `scripts/e2e_mix_producer.py` - Complete workflow example
- `scripts/quick_arrangement_demo.py` - Simple demo example

## Contributing

To add new arrangement features:

1. **Add to Remote Script**: Add the `_method_name()` method in `AbletonMCP_Remote_Script/__init__.py`
2. **Add command routing**: Add the command type in `_process_command()` and `_execute_udp_command()`
3. **Add to MCP Server**: Create or update a tool in `MCP_Server/arrangement_tools.py`
4. **Register the tool**: Import and register in `MCP_Server/server.py`
5. **Test**: Run `scripts/quick_arrangement_demo.py` or `scripts/e2e_mix_producer.py`

## Future Enhancements

Possible future additions:
- [ ] Direct audio export support (requires Max4Live or external tool)
- [ ] Arrangement marker/locator manipulation
- [ ] Warp marker editing in arrangement view
- [ ] Clip envelope viewing/editing in arrangement view
- [ ] MIDI CC automation in arrangement view
- [ ] More mix templates (EDM, hip-hop, orchestral, etc.)
- [ ] AI-powered automatic mixing suggestions
- [ ] Batch processing of multiple arrangements
- [ ] Session template loading/saving
- [ ] Collaboration features (_shared arrangements)

## Support

For issues or questions:
1. Check this documentation
2. Run the demo scripts to verify your setup
3. Check Ableton's console for Remote Script errors
4. Check MCP server logs for connection issues
5. Open an issue on the GitHub repository

## License

This extension is licensed under the same terms as the main project. See `LICENSE` for details.

---

**Happy producing!** 🎛️🎧
