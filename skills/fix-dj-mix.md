# Fix DJ Mix - Lessons Learned

## Date: 2026-02-22

## Issues Fixed

### 1. FX Track (Dub FX) - Empty Clips

**Problem:** 
- Simpler loaded but clips were empty (no notes)
- Drum Rack was also on track instead of proper instrument
- Clips designed for Simpler but Drum Rack loaded doesn't respond to those MIDI notes

**Solution:**
- Updated all FX clips (1-7) with drum notes (pitch 36-60 range)
- Drum notes trigger the loaded Drum Rack on Track 5
- Notes added: side stick, snare, hi-hat, clap, crash, ride

**Code Pattern:**
```python
# Use drum note ranges for Drum Rack (36-60)
fx_drum_patterns = {
    1: [{'pitch': 37, 'start': 0.5, 'dur': 0.25, 'vel': 100}],   # Side stick
    2: [{'pitch': 38, 'start': 0.0, 'dur': 1.0, 'vel': 110}],  # Snare 1
    3: [{'pitch': 40, 'start': 0.0, 'dur': 1.5, 'vel': 115}],  # Hi-hat
    4: [{'pitch': 42, 'start': 0.5, 'dur': 3.0, 'vel': 90}],   # Closed HH
    5: [{'pitch': 46, 'start': 0.0, 'dur': 0.5, 'vel': 100}],  # Open HH
    6: [{'pitch': 39, 'start': 0.0, 'dur': 3.5, 'vel': 110}],  # Clap
    7: [{'pitch': 49, 'start': 0.25, 'dur': 0.25, 'vel': 100},   # Crash
          {'pitch': 51, 'start': 0.75, 'dur': 0.25, 'vel': 100}],  # Ride
}
```

### 2. Hats_Wash Clip - Empty

**Problem:**
- Clip 6 (Hats_Wash) on Track 2 had 0 notes
- Resulted in silence when fired

**Solution:**
- Added minimal, subtle hat notes (pitch 42, velocity 40)
- Sparse pattern: notes at 0.5 and 2.5 beats

**Code Pattern:**
```python
# Add notes to empty clip
notes = [
    {'pitch': 42, 'start_time': 0.5, 'duration': 0.125, 'velocity': 40, 'mute': False},
    {'pitch': 42, 'start_time': 2.5, 'duration': 0.125, 'velocity': 40, 'mute': False},
]
cmd = {'type': 'add_notes_to_clip', 'params': {'track_index': 2, 'clip_index': 6, 'notes': notes}}
```

### 3. Lead Pad Track Creation

**Problem:**
- Needed additional track for lead melodic elements
- Initial Wavetable load failed

**Solution:**
- Used correct MCP command: `load_browser_item` (not `load_instrument_or_effect`)
- Created Track 6 "Lead Pad" with Wavetable
- Created 8 melodic clips with arpeggios and ostinato patterns

**Important: MCP Command Name**
```python
# WRONG - This doesn't exist:
cmd = {'type': 'load_instrument_or_effect', ...}

# CORRECT - This works:
cmd = {'type': 'load_browser_item', 'params': {'track_index': track_idx, 'item_uri': uri}}
```

## Anti-Patterns to Avoid

### 1. Creating Empty Clips
❌ **Don't** create clips with 0 notes unless intentional (e.g., FX_None)
✅ **Do** add minimal notes even for "wash" or "subtle" clips

### 2. Wrong MIDI Note Ranges
❌ **Don't** use arbitrary MIDI notes (pitch 60-90) for Drum Rack
✅ **Do** use drum note ranges (pitch 36-60) for Drum Rack instruments

### 3. Wrong MCP Command Names
❌ **Don't** assume command names like `load_instrument_or_effect` or `load_preset`
✅ **Do** use verified commands: `load_browser_item`, `create_clip`, `add_notes_to_clip`, etc.

### 4. Deleting Devices
❌ **Don't** try to delete devices - `delete_device` is broken in Remote Script
✅ **Do** recreate tracks or work with existing devices

## Reference: Working Code Patterns

### Create Track with Instrument
```python
# Create MIDI track
s.send(json.dumps({'type': 'create_midi_track', 'params': {'index': -1}}).encode())

# Name track
s.send(json.dumps({'type': 'set_track_name', 
                  'params': {'track_index': i, 'name': 'Track Name'}}).encode())

# Load instrument
s.send(json.dumps({'type': 'load_browser_item',
                  'params': {'track_index': i, 'item_uri': 'query:Category#Device'}}).encode())
```

### Add Notes to Existing Clip
```python
# Get clip info first (optional)
result = s.recv(4096)

# Add notes (will append to existing)
notes = [
    {'pitch': 60, 'start_time': 0.0, 'duration': 0.5, 'velocity': 100, 'mute': False},
    # ... more notes
]
s.send(json.dumps({'type': 'add_notes_to_clip',
                  'params': {'track_index': track_idx, 'clip_index': clip_idx, 'notes': notes}}).encode())
```

### Verify Clips Created
```python
# Get all clips in track
s.send(json.dumps({'type': 'get_all_clips_in_track', 
                  'params': {'track_index': track_idx}}).encode())
result = json.loads(s.recv(8192).decode())

clips = result.get('result', {}).get('clips', [])
for clip in clips:
    print(f'Clip {clip["index"]}: {clip["name"]} - {clip["length"]} bars')
```

## File Locations

- **Live DJ Mix Script:** `.sisyphus/evidence/live_dub_mix.py`
- **48 Clip Creation Script:** `create_2h_clips.py`
- **Session Setup:** `recreate_arrangement.py`
- **MCP Server:** `MCP_Server/server.py`

## Commands Used

| Command | Purpose | Example |
|---------|---------|---------|
| `create_midi_track` | Create MIDI track | `{'type': 'create_midi_track', 'params': {'index': -1}}` |
| `set_track_name` | Name a track | `{'type': 'set_track_name', 'params': {'track_index': 0, 'name': 'Kick'}}` |
| `load_browser_item` | Load instrument/effect from browser | `{'type': 'load_browser_item', 'params': {'track_index': 0, 'item_uri': 'query:Synths#Wavetable'}}` |
| `create_clip` | Create empty MIDI clip | `{'type': 'create_clip', 'params': {'track_index': 0, 'clip_index': 0, 'length': 4.0}}` |
| `add_notes_to_clip` | Add notes to clip | `{'type': 'add_notes_to_clip', 'params': {'track_index': 0, 'clip_index': 0, 'notes': [...]}}` |
| `set_clip_name` | Name a clip | `{'type': 'set_clip_name', 'params': {'track_index': 0, 'clip_index': 0, 'name': 'Clip Name'}}` |
| `fire_clip` | Trigger clip playback | `{'type': 'fire_clip', 'params': {'track_index': 0, 'clip_index': 0}}` |
| `set_track_volume` | Set track volume (0.0-1.0) | `{'type': 'set_track_volume', 'params': {'track_index': 0, 'volume': 0.8}}` |
| `get_all_clips_in_track` | List all clips in track | `{'type': 'get_all_clips_in_track', 'params': {'track_index': 0}}` |
| `get_notes_in_clip` | Get notes from a clip | `{'type': 'get_notes_in_clip', 'params': {'track_index': 0, 'clip_index': 0}}` |

## Next Steps

1. ✅ Fixed FX clips with drum notes
2. ✅ Fixed Hats_Wash with subtle notes
3. ✅ Created Track 6 "Lead Pad" with 8 melodic clips
4. ⏳ Update live mix script to include Track 6
5. ⏳ Commit all changes
