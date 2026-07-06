# Sprint 08: MCP Resources V2 + Knowledge Base V2

**Theme:** More session state exposed as URI-addressable resources. More device knowledge.
**Est. days:** 5 | **New resources:** 3-4 | **Knowledge:** +20 devices | **Risk:** Low
**Dependencies:** None

## Goal
Double down on our strongest differentiator: deep, queryable session state. Add resource subscriptions (Live-updating resources), expand the device knowledge base from 36 to 55+ devices, and add production recipes.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/server.py` | Modify | Add new resource URIs + subscription support |
| `MCP_Server/resources.py` | Create | Extract resource definitions for modularity |
| `MCP_Server/resources_sub.py` | Create | Subscription handler (polling-based) |
| `MCP_Server/knowledge/__init__.py` | Modify | Add recipe loading, caching improvements |
| `MCP_Server/knowledge/devices/third_party.json` | Create | 20 third-party device schemas |
| `MCP_Server/knowledge/recipes/` | Create | Production recipe directory |
| `MCP_Server/knowledge/recipes/minimal_techno.json` | Create | Recipe: minimal techno setup |
| `MCP_Server/knowledge/recipes/ambient_pad.json` | Create | Recipe: ambient pad sound |
| `MCP_Server/knowledge/recipes/drum_mix.json` | Create | Recipe: drum mixing chain |
| `tests/test_resources_v2.py` | Create | Resource subscription + URI unit tests |

## Deliverables

### 8.1 New Resource URIs

| URI | Wraps | Returns |
|-----|-------|---------|
| `live://track/{ti}/clip/{ci}/notes` | Existing `add_notes_to_clip` read alternative | MIDI note data (pitch, time, duration, velocity) |
| `live://track/{ti}/device/{di}/parameters` | `get_device_parameters(ti, di)` | Full parameter details with current values |
| `live://scene/{si}/clip/{ci}` | `get_all_clips_in_track` per scene | Clip data filtered to scene |
| `live://session/projects` | File scan of Live Projects folder | Recent project list |

Each registered with `@mcp.resource()` decorator:
```python
@mcp.resource("live://track/{track_index}/device/{device_index}/parameters")
def get_device_parameters_resource(track_index: int, device_index: int) -> str:
    """Get all parameters with current values for a device."""
    ...
```

### 8.2 Resource Subscriptions (`resources_sub.py`)
Implement MCP `subscribe`/`unsubscribe` protocol:
- `subscribe_resource(ctx, uri: str, interval_ms: int = 1000)` — polls the resource at interval, sends `resources/updated` notifications on state change
- `unsubscribe_resource(ctx, uri: str)` — stops polling
- Polling-based (Live doesn't push state changes)
- Tracks last seen hash per URI; only notifies on change
- Automatic unsubscribe on server stop or resource error

```python
_subscription_registry: dict[str, dict] = {}
# { uri: {"interval": int, "last_hash": str, "timer": TimerThread} }
```

### 8.3 Third-Party Device Knowledge (+20 devices)
Add `third_party.json` with schemas for popular third-party plugins:

| Category | Devices |
|----------|---------|
| **Synths** | Serum (Xfer), Massive (NI), Sylenth1 (Lennar), Spire (Reveal Sound), Diva (u-he), Hive (u-he), Pigments (Arturia), Vital (Matt Tytel) |
| **Samplers** | Kontakt (NI), Battery (NI) |
| **Effects** | Valhalla Room/Room, Shimmer (Valhalla), FabFilter Pro-Q 3, Pro-C 2, Pro-L 2, Soundtoys EchoBoy, Decapitator, Little AlterBoy, iZotope Ozone 11, Ozone Neutron 5 |

Each with realistic parameter schemas (essential params, not all 500+):
```json
{
  "name": "Serum",
  "class_name": "SynthPluginDevice",
  "company": "Xfer Records",
  "parameter_count": 250,
  "documented_params": [
    {"name": "Osc A Pitch", "index": 0, "range": [-24, 24], "default": 0, "unit": "semitones", "page": "Osc A"},
    {"name": "Osc A Coarse", "index": 1, "range": [-48, 48], "default": 0, "unit": "semitones"},
    {"name": "Osc A Fine", "index": 2, "range": [-100, 100], "default": 0, "unit": "cents"},
    {"name": "Osc A Level", "index": 3, "range": [0.0, 1.0], "default": 0.8, "unit": "normalized"},
    {"name": "Osc A Blend", "index": 4, "range": [0.0, 1.0], "default": 0.5},
    {"name": "Filter Type", "index": 5, "range": [0, 5], "default": 0},
    {"name": "Filter Cutoff", "index": 6, "range": [0.0, 1.0], "default": 1.0},
    ...
  ]
}
```

### 8.4 Production Recipes (`knowledge/recipes/`)
JSON files with prescriptive production guides:

**`minimal_techno.json`:**
```json
{
  "name": "Minimal Techno Setup",
  "genre": "techno",
  "description": "Build a minimal techno session from scratch",
  "tracks": [
    {"name": "Kick", "instrument": "Drum Rack", "pattern": "techno_4x4", "effects": ["EQ Eight", "Compressor"]},
    {"name": "Hihat", "instrument": "Drum Rack", "pattern": "one_drop"},
    {"name": "Clap", "instrument": "Drum Rack", "pattern": "house_basic"},
    {"name": "Bass", "instrument": "Operator", "preset": "Deep Mono"},
    {"name": "Pad", "instrument": "Wavetable", "preset": "Warm Pad"}
  ],
  "mix": {"kick_level": -6, "bass_level": -8, "pad_level": -12},
  "effects_sends": {"reverb": 0.3, "delay": 0.15}
}
```

**`drum_mix.json`:**
```json
{
  "name": "Drum Bus Mix Chain",
  "description": "Standard drum processing chain on a return/group track",
  "chain": [
    {"device": "Drum Buss", "params": {"mode": 0, "drive": 0.15, "boom": 0.2}},
    {"device": "Glue Compressor", "params": {"threshold": -12, "ratio": 4, "attack": 0.1, "release": 100}},
    {"device": "EQ Eight", "params": {"band": {"freq": 40, "gain": 2, "type": "low_shelf"}}}
  ]
}
```

### 8.5 Resource Module Extraction
Refactor resource registrations from `server.py` into `MCP_Server/resources.py`:
- All `@mcp.resource()` decorators move to resource module
- `MCP_Server/resources.py` exports `register_resources(mcp)` function
- Called in server.py at startup alongside other registrations
- Makes server.py slightly smaller (currently 6600+ lines)

### 8.6 Resource Tool
**Tool: `get_resource_preview`**
```
(ctx, uri_pattern: str) -> str
```
- Shows sample output for a resource URI (without connecting to Live)
- Useful for discovering what resources are available and their format

**Tool: `subscribe_resource`**
```
(ctx, uri: str, interval_ms: int = 1000) -> str
```
- Subscribe to a resource for live updates

**Tool: `unsubscribe_resource`**
```
(ctx, uri: str) -> str
```
- Cancel a subscription

## API Surface

### New Resources
| URI | Description |
|-----|-------------|
| `live://track/{ti}/clip/{ci}/notes` | MIDI notes in clip |
| `live://track/{ti}/device/{di}/parameters` | Device params with values |
| `live://scene/{si}/clip/{ci}` | Clip in specific scene |
| `live://session/projects` | Recent project list |

### New Tools
| Tool | Signature | Returns |
|------|-----------|---------|
| `get_resource_preview` | (uri_pattern) | Example output JSON |
| `subscribe_resource` | (uri, interval_ms) | Subscription confirmation |
| `unsubscribe_resource` | (uri) | Unsubscribe confirmation |

## Acceptance Criteria
```bash
# 4 new resource URIs registered
grep -c "@mcp.resource" MCP_Server/resources.py  # >= 4

# 20+ third-party devices
python -c "
import json
with open('MCP_Server/knowledge/devices/third_party.json') as f:
    devices = json.load(f)
assert len(devices) >= 20
total_params = sum(len(d['parameters']) for d in devices)
assert total_params >= 100
print(f'{len(devices)} devices, {total_params} params')
"

# 5+ production recipes
ls MCP_Server/knowledge/recipes/*.json  # >= 5 files

# Subscription tool exists
grep -c "def subscribe_resource\|def unsubscribe_resource" MCP_Server/server.py  # >= 2
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Subscriptions hammer Live with polling | Medium | Min interval 500ms; max 5 concurrent subscriptions |
| Third-party param indices inaccurate | High | Mark as "approximate"; add disclaimer in tool output |
| server.py becomes even larger | Medium | Extract resources to separate module (server.py is too big at 6600 lines) |

## Must NOT Do
- Do NOT poll more than 5 subscriptions simultaneously (rate limit)
- Do NOT add external plugin detection (third-party schemas are manual best-effort)
- Do NOT modify or delete existing resource URIs
- Do NOT attempt real-time audio resource streaming (Live API doesn't support it)
