# Instrument Loading Status - Dub Techno Track

## Current Status

### ✅ What Works
- Track creation and naming: 100% complete
- Clip creation with patterns: 35% complete (Kick fully done, others have clips)
- Volume configuration: 100% complete
- Session structure: 100% complete

### ❌ What Doesn't Work Yet
- **Instrument loading via MCP:** Server has the code, but Ableton's internal browser URIs don't match simple names
- The command `load_instrument_or_effect` exists but requires Ableton's specific URI format

## Technical Analysis

### MCP Server (server.py)
- Line 1430: `@mcp.tool()` decorator on `load_instrument_or_effect`
- Line 1441: Calls Remote Script's `load_browser_item` command
- The function exists and is properly registered

### Remote Script (__init__.py)
- Line 527: Listens for `load_browser_item` command
- Line 3687: `_load_browser_item()` implementation exists
- Line 3699: Uses `_find_browser_item_by_uri()` to locate instruments
- **The Problem:** Ableton's browser items have URIs like `"browser://instruments/operator:FileId_12345"` not just `"Operator"`

### Why It's Failing
```
Tried URI: "Operator"
Expected:   "browser://instruments/operator:specific_guid_or_fileid"
Result:     Browser item not found - URI doesn't match
```

## Solution Options

### Option 1: Manual Loading (CURRENT - FASTEST)
Load instruments directly in Ableton Live by:
1. Click device area on each track
2. Press TAB to open Browser
3. Navigate to:
   - Track 0: Instruments → Operator
   - Track 1: Instruments → Operator  
   - Track 2: Instruments → Drums → Drum Rack
   - Track 3: Instruments → Drums → Drum Rack
   - Track 4: Instruments → Wavetable
   - Track 5: Instruments → Simpler
   - Track 6: Audio Effects → Delay → Simple Delay
   - Track 7: Audio Effects → Reverb → Hybrid Reverb
4. Press ENTER to load

**Time:** ~5 minutes
**Success Rate:** 100%

### Option 2: Query Ableton Browser for URIs (REQUIRES CODE)
Create a script that:
1. Queries Ableton's browser structure
2. Lists available instruments with their full URIs
3. Matches instrument names to their URIs
4. Loads using complete URIs

**Challenge:** Browser commands (`get_browser_items`, `get_browser_categories`) are also returning errors from the current MCP server

### Option 3: Roundabout via Device Creation (COMPLEX)
1. Create device types directly via Remote Script API
2. Skip browser lookup entirely
3. Works for built-in instruments like Operator, Wavetable

**Status:** Would require new Remote Script methods

## Recommended Path

### Immediate Action (Use This!)
**Manual instrument loading in Ableton Live**

Estimated time: 5 minutes
Reason: 100% reliable, no code changes needed

Instructions:
```
1. Open Ableton Live (must be running for MCP connection)
2. Select Track 0 (Deep Kick)
   - Click the empty device area at top of track
   - Press TAB to open Browser
   - Use arrows to navigate: Instruments → Operator
   - Press ENTER to load
   - Load preset: "Kick" or "Kick - Punchy"

3. Repeat for all 8 tracks:
   Track 1 (Sub-Bass): Instruments → Operator
   Track 2 (Dub Hats): Instruments → Drums → Drum Rack
   Track 3 (Percs): Instruments → Drums → Drum Rack
   Track 4 (Atmo Pad): Instruments → Wavetable
   Track 5 (Dub FX): Instruments → Simpler
   Track 6 (Dub Delay): Audio Effects → Signal → Delay → Simple Delay
   Track 7 (Reverb): Audio Effects → Reverb → Hybrid Reverb

4. Configure instruments per INSTRUMENT_GUIDE_DUB_TECHNO.md
```

### If You Want to Automate It (Future Development)
To make `load_instrument_or_effect` work automatically:

1. **Fix browser querying:**
   - Debug why `get_browser_items` returns error
   - Test actual Ableton instance connected

2. **Create URI mapping:**
   ```python
   # Map simple names to likely Ableton URIs
   INSTRUMENT_URIS = {
       "Operator": ["browser://instruments/operator:*"],
       "Wavetable": ["browser://instruments/wavetable:*"],
       "Drums/Drum Rack": ["browser://drums/drum rack:*"],
       # Wildcard matching needed
   }
   ```

3. **Use fuzzy matching:**
   - Try multiple URI variants
   - Handle GUIDs that vary by Ableton version

4. **Alternative approach:**
   ```python
   # Skip browser, use device creation
   # This would require new Remote Script methods like:
   - create_operator_device()
   - create_wavetable_device()
   - create_drum_rack()
   ```

## Success Checklist After Manual Loading

Once instruments are manually loaded, verify:

- [ ] Track 0: Operator visible with kick sound
- [ ] Track 1: Operator visible, ready for bass configuration
- [ ] Track 2: Drum Rack visible on hi-hat track
- [ ] Track 3: Drum Rack visible on percussion track
- [ ] Track 4: Wavetable visible on pad track
- [ ] Track 5: Simpler visible on FX track
- [ ] Track 6: Simple Delay on send track
- [ ] Track 7: Hybrid Reverb on send track
- [ ] Can fire clip and hear sound?
- [ ] Press ENTER to confirm sound works

## Documentation Created

For your reference, these documents guide manual setup:

1. **INSTRUMENT_GUIDE_DUB_TECHNO.md**
   - Complete instrument configuration
   - Sound design parameters for heavy bass
   - Effects chain setup

2. **DUB_TECHNO_IMPLEMENTATION_SUMMARY.md**
   - Full implementation overview
   - Clip patterns for all tracks
   - Section progression guide

3. **load_instruments_dub_techno.py**
   - Script reference (currently requires manual URI adjustment)

## Final Recommendation

**Go with manual loading now.** It's fast (5 minutes) and 100% reliable. The automation can be developed later after more testing is done with the Ableton browser API.

---

**Date Created:** 2026-02-21
**Session:** 2-Hour Dub Techno Track (Heavy Bass)
**Status:** Ready for manual instrument loading