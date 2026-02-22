# Ableton DJ Performance Skill

## Purpose
Live parameter adjustments, gradual clip switching, and creating evolving musical performances in Ableton Live via MCP. Triggers include "live adjustments", "switch clips gradually", "DJ style", "fade between clips", "parameter sweeps", "live automation".

---

## Audio Effects Reference

### Delay Effects
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Simple Delay** | `SimpleDelay` | Basic echo, slapback | Delay Time L/R, Feedback, Dry/Wet |
| **Ping Pong Delay** | `PingPongDelay` | Stereo movement, dub echoes | Delay Time, Feedback, Dry/Wet, Ping Pong |
| **Filter Delay** | `FilterDelay` | Filtered echoes, dub techno | Delay Time, Filter Freq, Feedback |
| **Grain Delay** | `GrainDelay` | Granular textures, atmospheric | Grain Size, Pitch, Feedback, Dry/Wet |
| **Delay** | `Delay` (Audio Effect Rack) | Complex delay chains | Varies by preset |

### Reverb Effects
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Reverb** | `Reverb` | Classic algorithmic reverb | Decay Time, Pre Delay, Dry/Wet |
| **Hybrid Reverb** | `HybridReverb` | Modern, versatile reverb | Decay, Size, Pre Delay, Tone |
| **Convolution Reverb** | `ConvolutionReverb` | Realistic spaces | IR File, Decay, Pre Delay |
| **Ambience** | `Ambience` | Subtle room sound | Size, Decay, Tone |

### Distortion/Saturation
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Saturator** | `Saturator` | Warmth, harmonic content | Drive, Color, Dry/Wet |
| **Overdrive** | `Overdrive` | Gritty distortion | Drive, Tone, Dry/Wet |
| **Distortion** | `Distortion` | Heavy distortion | Drive, Tone |
| **Amp** | `Amp` | Guitar amp simulation | Amp Type, Drive, EQ |
| **Dynamic Tube** | `DynamicTube` | Tube warmth | Drive, Tone, Mix |

### Modulation Effects
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Chorus** | `Chorus` | Thickening, stereo width | Rate, Depth, Dry/Wet |
| **Flanger** | `Flanger` | Sweeping metallic sound | Rate, Depth, Feedback |
| **Phaser** | `Phaser` | Phase sweeping | Rate, Depth, Stages |
| **Phaser-Flanger** | `PhaserFlanger` | Combined modulation | Rate, Depth, Feedback |
| **Chorus-Ensemble** | `ChorusEnsemble` | Rich modulation | Rate, Depth, Voices |
| **Freq Shifter** | `FreqShifter` | Pitch shifting, detuning | Shift Amount, Fine |
| **Beat Repeat** | `BeatRepeat` | Glitchy repeats | Grid, Chance, Gate |

### Filter Effects
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Auto Filter** | `AutoFilter` | Rhythmic filtering, sweeps | Frequency, Resonance, LFO Rate |
| **EQ Eight** | `Eq8` | Precise EQ, filter sweeps | 8 bands, filter types |
| **EQ Three** | `EqThree` | Simple 3-band EQ | Low, Mid, High |
| **Corpus** | `Corpus` | Resonant filtering | Resonance, Decay, Tune |

### Dynamics
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Compressor** | `Compressor2` | Level control, punch | Threshold, Ratio, Attack, Release |
| **Glue Compressor** | `GlueCompressor` | Bus compression | Threshold, Ratio, Attack, Makeup |
| **Limiter** | `Limiter` | Prevent clipping | Ceiling, Release |
| **Gate** | `Gate` | Noise reduction | Threshold, Attack, Hold, Release |
| **Multiband Dynamics** | `MultibandDynamics` | Frequency-specific compression | Band thresholds, ratios |

### Time/Pitch
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Looper** | `Looper` | Live looping | Record, Overdub, Playback Speed |
| **Velocity** | `Velocity` (MIDI) | MIDI velocity control | Velocity curve, range |
| **Arpeggiator** | `Arpeggiator` (MIDI) | Rhythmic patterns | Style, Rate, Gate |

### Utility
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Utility** | `Utility` | Gain, phase, width | Gain, Width, Phase L/R |
| **Spectrum** | `Spectrum` | Visual analysis | N/A (display only) |
| **Correlation Meter** | `CorrelationMeter` | Phase correlation | N/A (display only) |

### Creative/Spectral Effects
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Echo** | `Echo` | Modern delay with filtering | Feedback (16), Dry/Wet (52), HP/LP Filter (29,31) |
| **Beat Repeat** | `BeatRepeat` | Glitchy stutter effects | Chance (1), Grid (4), Gate (8), Decay (9) |
| **Erosion** | `Erosion` | Lo-fi digital degradation | Mode, Freq, Amount |
| **Resonators** | `Resonator` | Metallic, tonal resonances | Decay (5), Color (7), Dry/Wet (9) |
| **Spectral Time** | `SpectralTime` | Spectral freezing, smearing | Freeze, Blur, Size |
| **Spectral Blur** | `SpectralBlur` | Spectral smearing | Blur Amount, Size |
| **Spectral Resonator** | `SpectralResonator` | Spectral filtering | Freq, Resonance |
| **Shifter** | `Shifter` | Pitch shifting | Semitones, Formants |
| **Vocoder** | `Vocoder` | Robot voice, synthesis | Bands, Formant Shift |
| **Drum Buss** | `DrumBuss` | Drum processing | Drive, Transient, Damping |
| **Roar** | `Roar` | Multi-mode distortion | Mode, Tone, Amount |
| **Pedal** | `Pedal` | Guitar pedal simulation | Pedal Type, Tone |
| **Redux** | `Redux` | Bitcrusher, decimation | Downsample, Bit Depth |
| **Vinyl Distortion** | `VinylDistortion` | Vinyl character | Drive, Crackle, Rumble |

### New Effects (Live 12+)
| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Auto Shift** | `AutoShift` | Automatic pitch correction | Scale, Speed, Mix |
| **Roar** | `Roar` | Multi-band distortion | Mode, Tone, Mix |
| **Vector Delay** | `VectorDelay` | Multi-tap spatial delay | X/Y Position, Feedback |
| **Performer** | `Performer` | Macro control | Shape, Rate |

---

## MIDI Effects Reference

| Effect | Class Name | Best For | Key Parameters |
|--------|-----------|----------|----------------|
| **Arpeggiator** | `Arpeggiator` | Rhythmic note patterns | Style, Rate, Gate, Swing |
| **Chord** | `Chord` | Create chords from single notes | Intervals 1-6 |
| **Note Length** | `NoteLength` | Modify note durations | Length, Mode |
| **Pitch** | `Pitch` | Transpose MIDI | Transpose, Range |
| **Random** | `Random` | Randomize notes | Chance, Choices |
| **Scale** | `Scale` | Constrain to scale | Root, Scale Type |
| **Velocity** | `Velocity` | Modify velocities | Out High/Low, Drive |
| **Note Echo** | `NoteEcho` | MIDI delay | Delay Time, Feedback, Pitch |

---

## DJ Performance Techniques

### 1. Filter Sweeps (Most Common)
```
# Low-pass filter sweep for builds
apply_filter_buildup(
    track_indices=[0, 1, 2],
    device_index=4,  # EQ Eight
    parameter_index=6,  # Frequency
    start_value=0.1,  # Low (muffled)
    end_value=0.9,    # High (open)
    duration_beats=32,
    steps=32
)
```

### 2. Drop Effect (Instant Energy Change)
```
# Instant filter close for drops
apply_drop(
    track_indices=[0, 2, 4],
    device_index=4,
    parameter_index=6,
    drop_value=0.1,  # Closed filter
    return_value=0.8,  # Open after drop
    drop_instant=True
)
```

### 3. Energy Curve (Gradual Volume Changes)
```
# Gradual volume/parameter curves
apply_energy_curve(
    parameter_changes=[
        {"track_index": 0, "device_index": 4, "parameter_index": 6, "start_value": 0.3, "end_value": 0.8},
        {"track_index": 1, "device_index": 4, "parameter_index": 6, "start_value": 0.2, "end_value": 0.9}
    ],
    duration_beats=64,
    steps=64
)
```

### 4. Send Automation (Reverb/Delay Swells)
```
# Increase reverb for breakdown
set_send_amount(track_index=0, send_index=0, amount=0.8)  # Reverb
set_send_amount(track_index=1, send_index=1, amount=0.6)  # Delay

# Reduce sends for dry sections
set_send_amount(track_index=0, send_index=0, amount=0.3)
```

### 5. Track Volume Fades
```
# Fade out track
set_track_volume(track_index=0, volume=0.8)
# ... wait ...
set_track_volume(track_index=0, volume=0.4)
```

---

## Device Parameter Indices (Common)

### EQ Eight (Most Useful for DJ)
| Index | Parameter | Range | DJ Use |
|-------|-----------|-------|--------|
| 0 | Device On | 0-1 | Enable/disable |
| 1 | Output Gain | -12 to +12 | Volume boost/cut |
| 6 | Filter 1 Frequency | 0-1 | Filter sweeps |
| 7 | Filter 1 Gain | -15 to +15 | EQ boost/cut |
| 8 | Filter 1 Resonance | 0-1 | Resonance |
| 16 | Filter 2 Frequency | 0-1 | Second filter |
| 36 | Filter 4 Frequency (High) | 0-1 | High filter sweeps |

### Saturator
| Index | Parameter | Range | DJ Use |
|-------|-----------|-------|--------|
| 0 | Device On | 0-1 | Enable/disable |
| 1 | Drive | 0-1 | Saturation amount |
| 2 | Color | 0-1 | Tone character |
| 3 | Dry/Wet | 0-1 | Mix level |

### Compressor
| Index | Parameter | Range | DJ Use |
|-------|-----------|-------|--------|
| 0 | Device On | 0-1 | Enable/disable |
| 1 | Threshold | 0-1 | Compression trigger |
| 2 | Ratio | 0-1 | Compression amount |
| 3 | Attack | 0-1 | Response time |
| 4 | Release | 0-1 | Recovery time |
| 5 | Makeup | 0-1 | Output gain |

### Grain Delay
| Index | Parameter | Range | DJ Use |
|-------|-----------|-------|--------|
| 0 | Device On | 0-1 | Enable/disable |
| 1 | Grain Size | 0-1 | Texture |
| 2 | Pitch | 0-1 | Pitch shift |
| 3 | Feedback | 0-1 | Echo repeats |
| 4 | Dry/Wet | 0-1 | Mix level |

---

## Loading Effects

### Method 1: By URI (Recommended)
```
load_instrument_or_effect(
    track_index=0,
    uri="query:Audio%20Effects#Delay:Simple%20Delay"
)
```

### Method 2: Browser Path
```
get_browser_items_at_path("Audio Effects/Delay")
load_instrument_or_effect(track_index, uri_from_browser)
```

### Common URIs
- Delay: `query:Audio%20Effects#Delay:Simple%20Delay`
- Reverb: `query:Audio%20Effects#Reverb:Reverb`
- Saturator: `query:Audio%20Effects#Distortion:Saturator`
- Compressor: `query:Audio%20Effects#Dynamics:Compressor`
- EQ Eight: `query:Audio%20Effects#Filter/EQ:EQ%20Eight`
- Chorus: `query:Audio%20Effects#Modulation/Chorus:Chorus`

---

## Complete Effects URIs Reference

### Audio Effects URIs (Use with load_instrument_or_effect)
All URIs use format: `query:AudioFx#EffectName` (spaces encoded as %20)

#### Delay/Echo
| Effect | URI |
|--------|-----|
| Echo | `query:AudioFx#Echo` |
| Delay | `query:AudioFx#Delay` |
| Filter Delay | `query:AudioFx#Filter%20Delay` |
| Grain Delay | `query:AudioFx#Grain%20Delay` |
| Gated Delay | `query:AudioFx#Gated%20Delay` |
| Align Delay | `query:AudioFx#Align%20Delay` |
| Vector Delay | `query:AudioFx#Vector%20Delay` |

#### Reverb
| Effect | URI |
|--------|-----|
| Reverb | `query:AudioFx#Reverb` |
| Hybrid Reverb | `query:AudioFx#Hybrid%20Reverb` |
| Convolution Reverb | `query:AudioFx#Convolution%20Reverb` |
| Convolution Reverb Pro | `query:AudioFx#Convolution%20Reverb%20Pro` |

#### Distortion/Saturation
| Effect | URI |
|--------|-----|
| Saturator | `query:AudioFx#Saturator` |
| Overdrive | `query:AudioFx#Overdrive` |
| Dynamic Tube | `query:AudioFx#Dynamic%20Tube` |
| Amp | `query:AudioFx#Amp` |
| Cabinet | `query:AudioFx#Cabinet` |
| Pedal | `query:AudioFx#Pedal` |
| Roar | `query:AudioFx#Roar` |
| Shaper | `query:AudioFx#Shaper` |
| Vinyl Distortion | `query:AudioFx#Vinyl%20Distortion` |
| Drum Buss | `query:AudioFx#Drum%20Buss` |

#### Modulation
| Effect | URI |
|--------|-----|
| Chorus-Ensemble | `query:AudioFx#Chorus-Ensemble` |
| Phaser-Flanger | `query:AudioFx#Phaser-Flanger` |
| Auto Pan-Tremolo | `query:AudioFx#Auto%20Pan-Tremolo` |
| LFO | `query:AudioFx#LFO` |

#### Filter/EQ
| Effect | URI |
|--------|-----|
| EQ Eight | `query:AudioFx#EQ%20Eight` |
| EQ Three | `query:AudioFx#EQ%20Three` |
| Channel EQ | `query:AudioFx#Channel%20EQ` |
| Auto Filter | `query:AudioFx#Auto%20Filter` |
| Corpus | `query:AudioFx#Corpus` |

#### Dynamics
| Effect | URI |
|--------|-----|
| Compressor | `query:AudioFx#Compressor` |
| Glue Compressor | `query:AudioFx#Glue%20compressor` |
| Limiter | `query:AudioFx#Limiter` |
| Color Limiter | `query:AudioFx#Color%20Limiter` |
| Gate | `query:AudioFx#Gate` |
| Multiband Dynamics | `query:AudioFx#Multiband%20Dynamics` |

#### Creative/Spectral
| Effect | URI |
|--------|-----|
| Beat Repeat | `query:AudioFx#Beat%20Repeat` |
| Erosion | `query:AudioFx#Erosion` |
| Resonators | `query:AudioFx#Resonators` |
| Spectral Time | `query:AudioFx#Spectral%20Time` |
| Spectral Blur | `query:AudioFx#Spectral%20Blur` |
| Spectral Resonator | `query:AudioFx#Spectral%20Resonator` |
| Shifter | `query:AudioFx#Shifter` |
| Vocoder | `query:AudioFx#Vocoder` |
| Looper | `query:AudioFx#Looper` |
| Redux | `query:AudioFx#Redux` |

#### Utility/Other
| Effect | URI |
|--------|-----|
| Utility | `query:AudioFx#Utility` |
| Spectrum | `query:AudioFx#Spectrum` |
| Tuner | `query:AudioFx#Tuner` |
| Envelope Follower | `query:AudioFx#Envelope%20Follower` |
| Audio Effect Rack | `query:AudioFx#Audio%20Effect%20Rack` |

### MIDI Effects URIs
All URIs use format: `query:MidiFx#EffectName`

| Effect | URI | Best For |
|--------|-----|----------|
| Arpeggiator | `query:MidiFx#Arpeggiator` | Rhythmic note patterns |
| Chord | `query:MidiFx#Chord` | Create chords from single notes |
| Note Length | `query:MidiFx#Note%20Length` | Modify note durations |
| Note Echo | `query:MidiFx#Note%20Echo` | MIDI delay/repeat |
| Pitch | `query:MidiFx#Pitch` | Transpose MIDI |
| Random | `query:MidiFx#Random` | Randomize notes |
| Scale | `query:MidiFx#Scale` | Constrain to scale |
| Velocity | `query:MidiFx#Velocity` | Modify velocities |
| Melodic Steps | `query:MidiFx#Melodic%20Steps` | Step sequencer |
| Rhythmic Steps | `query:MidiFx#Rhythmic%20Steps` | Rhythmic patterns |
| Step Arp | `query:MidiFx#Step%20Arp` | Step arpeggiator |
| SQ Sequencer | `query:MidiFx#SQ%20Sequencer` | Sequencer |
| Expressive Chords | `query:MidiFx#Expressive%20Chords` | Expressive chord playing |
| Bouncy Notes | `query:MidiFx#Bouncy%20Notes` | Physics-based notes |

## Performance Workflow

### Pre-Performance Setup
1. Load effects on each track (EQ, Compressor, Saturator)
2. Set up return tracks (Reverb, Delay)
3. Configure send routing
4. Test all clips fire correctly

### During Performance
1. Trigger scenes/clips for progression
2. Apply filter sweeps for builds
3. Use drops for breakdowns
4. Adjust sends for atmosphere
5. Monitor volume levels

### Common Automation Patterns

#### Build-Up (8 bars)
```
apply_filter_buildup([0,2,4], 4, 6, 0.2, 0.9, 32, 32)
# Increase sends gradually
set_send_amount(0, 0, 0.7)  # More reverb
```

#### Breakdown (8 bars)
```
apply_drop([0,2,4], 4, 6, 0.1, 0.7, True)
set_send_amount(0, 0, 0.9)  # Maximum reverb
set_track_volume(0, 0.4)    # Reduce drums
```

#### Drop/Release
```
set_send_amount(0, 0, 0.3)  # Less reverb
set_track_volume(0, 0.8)    # Full drums
set_device_parameter(0, 4, 6, 0.85)  # Open filter
```

---

## Safety Notes

1. **Never automate device_index=0, parameter_index=0** - This is "Device On" on the instrument!
2. **Always verify device indices** with `get_track_info` before automating
3. **Test effects with low volumes** before full automation
4. **Use undo** if something goes wrong: `undo()`

---

## Quick Reference Commands

```python
# Get track info with devices
get_track_info(track_index=0)

# Get device parameters
get_device_parameters(track_index=0, device_index=4)

# Set single parameter
set_device_parameter(track_index=0, device_index=4, parameter_index=6, value=0.8)

# Filter sweep
apply_filter_buildup(track_indices=[0,2,4], device_index=4, parameter_index=6, start_value=0.2, end_value=0.9, duration_beats=32, steps=32)

# Drop effect
apply_drop(track_indices=[0,2,4], device_index=4, parameter_index=6, drop_value=0.1, return_value=0.8, drop_instant=True)

# Send levels
set_send_amount(track_index=0, send_index=0, amount=0.7)

# Track volume
set_track_volume(track_index=0, volume=0.75)

# Fire clip
fire_clip(track_index=0, clip_index=0)

# Trigger scene
trigger_scene(scene_index=0)
```
