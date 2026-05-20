# Effect Management System Documentation

The `MCP_Server/effect_management.py` module provides improved effect loading capabilities with preset-based loading, genre-specific chains, and common signal flow configurations.

## Core Components

### 1. DeviceConfig
Configuration dataclass for a single device:
```python
@dataclass
class DeviceConfig:
    name: str                      # Display name
    device_type: str               # "audio_effect" or "midi_effect"
    uri: str                       # Ableton plugin URI
    preset_name: Optional[str]     # Optional preset name
    position: int = -1             # Device chain position (-1 = end)
    parameters: Optional[Dict[str, float]]  # Normalized parameters (0.0-1.0)
```

### 2. EffectPresets
Named effect presets for common effects:
- **REVERB**: Standard reverb
- **DELAY**: Simple delay
- **LIMITER**: Master limiter with gain/ceiling/release parameters
- **COMPRESSOR**: Compressor with ratio/threshold/release
- **EQ_THREE**: Three-band EQ
- **FILTER_FREQ**: Auto filter with frequency/resonance
- **SATURATOR**: Saturator with drive/color
- **CHORUS**: Chorus with mix/rate/depth

### 3. GenreEffectChains
Preconfigured effect chains for specific genres:

**Dub Techno**
- `DUB_TECHNO_BASS`: Compressor → Saturator → Filter → Limiter
- `DUB_TECHNO_CHORDS`: Saturator → Reverb → Delay

**House**
- `HOUSE_BASS`: EQ → Compressor → Saturator

**Techno**
- `TECHNO_LEAD`: Filter → Saturator → Delay → Reverb

**Ambient**
- `AMBIENT_PAD`: Saturator → EQ → Reverb → Chorus

**Electronic (General)**
- `CLASSIC_DRUMS`: EQ → Compressor → Limiter

### 4. EffectLoader
Helper class for loading effects with common names:

```python
# Get effect config by common name
config = EffectLoader.get_effect_config("reverb")
config = EffectLoader.get_effect_config("compressor")
config = EffectLoader.get_effect_config("filter")

# Get genre-specific chain
chain = EffectLoader.get_genre_chain("dub_techno", "bass")

# Create complete mix
mix = EffectLoader.create_mix("dub_techno", {
    "bass": "Bass Track",
    "chords": "Chord Track",
    "melody": "Melody Track"
})

# Parameter conversion
normalized = EffectLoader.normalize_parameter(72, 0, 127)  # Range to 0.0-1.0
actual = EffectLoader.denormalize_parameter(0.566, 0, 127)  # 0.0-1.0 to range
```

### 5. EffectChainBuilder
Templates for common effect configurations:

```python
# Dub techno return tracks (reverb and delay)
reverb_chain, delay_chain = EffectChainBuilder.build_dub_techno_return_setup()

# Dub techno mastering chain
master_chain = EffectChainBuilder.build_dub_techno_master_chain()

# Parallel processing chain
parallel_chain = EffectChainBuilder.build_parallel_processing_chain()
```

### 6. EffectLibrary
Searchable database of available Ableton effects:

```python
# Search by name
results = EffectLibrary.search("reverb")  # List matching effects

# Get all categories
categories = EffectLibrary.get_all_categories()

# Get effects by category
compressors = EffectLibrary.get_effects_by_category("dynamics")
```

## Usage Examples

### Example 1: Load Single Effect Preset
```python
from MCP_Server.effect_management import EffectLoader

# Get compressor preset
config = EffectLoader.get_effect_config("compressor")

# Load via Ableton MCP (conceptual)
ableton.send_command("load_instrument_or_effect", {
    "track_index": 4,
    "uri": config.uri
})
```

### Example 2: Load Genre-Specific Chain
```python
from MCP_Server.effect_management import GenreEffectChains

# Get dub techno bass chain
chain = GenreEffectChains.DUB_TECHNO_BASS

# Load each device
for device_config in chain.devices:
    ableton.send_command("load_instrument_or_effect", {
        "track_index": track_index,
        "uri": device_config.uri
    })
    # Set parameters if defined
    if device_config.parameters:
        # Apply normalized parameters (0.0-1.0)
        pass
```

### Example 3: Complete Genre Setup
```python
from MCP_Server.effect_management import EffectLoader

# Create dub techno setup across multiple tracks
genre = "dub_techno"
tracks = {"bass": 4, "chords": 5, "melody": 6}

mix = EffectLoader.create_mix(genre, tracks)
for track_name, track_index in tracks.items():
    chain = EffectLoader.get_genre_chain(genre, track_name)
    if chain:
        print(f"Loading {chain.name} on track {track_index}")
        # Load devices...
```

### Example 4: Search and Explore Effects
```python
from MCP_Server.effect_management import EffectLibrary

# Find all reverb types
reverbs = EffectLibrary.search("reverb")
print(f"Reverbs: {reverbs}")

#Browse all categories
for category in EffectLibrary.get_all_categories():
    effects = EffectLibrary.get_effects_by_category(category)
    print(f"{category.upper()}: {', '.join(effects)}")
```

## Genre Chain Details

### DUB_TECHNO_BASS (4 devices)
1. **Compressor**: Controls dynamics, punchy low end
   - ratio: 0.4, threshold: 0.3, release: 0.5
2. **Saturator**: Adds harmonic richness/drive
   - drive: 0.3, color: 0.0
3. **Auto Filter**: Frequency cutoff modulation
   - frequency: 0.7, resonance: 0.3
4. **Limiter**: Prevents clipping
   - gain: 0.0, ceiling: 0.98, release: 0.3

### DUB_TECHNO_CHORDS (3 devices)
1. **Saturator**: Adds harmonic depth/warmth
2. **Reverb**: Creates space/atmosphere
3. **Delay**: Echoes for dub techno feel

### HOUSE_BASS (3 devices)
1. **EQ Three**: Shape bass freq response
2. **Compressor**: Consistent punchy level
3. **Saturator**: Add warmth/grit

### TECHNO_LEAD (4 devices)
1. **Auto Filter**: Sweep/filter modulation
2. **Saturator**: Aggressive harmonic distortion
3. **Delay**: Stereo feedback echoes
4. **Reverb**: Space for lead

### AMBIENT_PAD (4 devices)
1. **Saturator**: Subtle harmonic richness
2. **EQ Three**: Shimmer frequencies
3. **Reverb**: Large, lush reverb
4. **Chorus**: Slow modulation for movement

### CLASSIC_DRUMS (3 devices)
1. **EQ Three**: Drum tonal shaping
2. **Compressor**: Transient control
3. **Limiter**: Peak limiting

## Parameter Normalization

All parameters use normalized values (0.0-1.0) for consistency with Ableton MCP API:
- MIDI velocity 0-127 → normalized 0.0-1.0
- Frequency 20Hz-20kHz → normalized 0.0-1.0
- Time values → normalized 0.0-1.0

Use `EffectLoader.normalize_parameter()` and `EffectLoader.denormalize_parameter()` for conversions.

## Advantages Over Manual Effect Loading

1. **Named presets**: "reverb", "delay" instead of URIs
2. **Genre-specific chains**: Pre-configured proven processing
3. **Parameter included**: Correct settings applied
4. **Discoverable**: Searchable library of all effects
5. **Extensible**: Easy to add new presets/chains
6. **Studio-tested**: Configurations based on genre best practices

## Future Enhancements

- [ ] Integrate with MCP tools for direct Ableton control
- [ ] Add more genre chains (breakbeat, glitch, cinematic)
- [ ] MIDI effect presets support
- - [ ] Preset loading from Ableton presets
- [ ] Device preset library expansion
- [ ] Signal flow routing templates
- [ ] Parallel/split chains
- [ ] Sidechain compression setups

## Testing

Run tests to verify functionality:
```bash
python -c "
from MCP_Server.effect_management import EffectLoader, GenreEffectChains, EffectLibrary

# Test preset lookup
compressor = EffectLoader.get_effect_config('compressor')
print(f'Compressor: {compressor.name} - {compressor.uri}')

# Test genre chain
bass_chain = GenreEffectChains.DUB_TECHNO_BASS
print(f'Bass chain: {bass_chain.name}')
print(f'Devices: {[d.name for d in bass_chain.devices]}')

# Test search
results = EffectLibrary.search('reverb')
print(f'Search results: {results}')
"
```

## Notes

- All URIs use Ableton's query format
- Parameters are always normalized (0.0-1.0)
- Position -1 means "append to end of device chain"
- Genre chains are ordered sequentially for proper signal flow
- Library can be extended by adding to `EffectLibrary._library`