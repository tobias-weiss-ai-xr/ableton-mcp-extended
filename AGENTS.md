# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-13 05:28:00
**Commit:** 30c5aa1
**Branch:** main

## OVERVIEW
Control Ableton Live via AI assistants using Model Context Protocol. Python-based MCP server with dual TCP/UDP architecture for real-time control and ElevenLabs voice integration.

## STRUCTURE
```
./
├── MCP_Server/              # Core MCP server (108 TCP + 9 UDP commands)
├── AbletonMCP_Remote_Script/ # Ableton Remote Script (socket server)
├── dub_techno_2h/           # 2-hour automation project
├── scripts/                  # Utilities and tests
├── tests/                     # Test suite
├── elevenlabs_mcp/            # Voice generation integration
└── max_devices/               # Max for Live audio export device
```

## WHERE TO LOOK
| Task                  | Location                         |
|-----------------------|----------------------------------|
| Protocol handlers      | MCP_Server/server.py              |
| Remote Script API    | AbletonMCP_Remote_Script/__init__.py |
| Automation scripts    | dub_techno_2h/                 |
| Test utilities       | scripts/ (test/, util/, analysis/) |
| Integration tests     | tests/integration/                  |
| Voice generation      | elevenlabs_mcp/                   |
| Audio export          | max_devices/                      |

## CONVENTIONS
- **Parameter normalization**: All device/track parameters use 0.0-1.0 normalized values
- **Dual-server architecture**: TCP (port 9877) for reliable operations, UDP (port 9878) for high-frequency parameter updates
- **NEVER-UDP protocol**: 30 critical operations (get_*, delete_*, quantize, mix, crop, undo/redo, recording) MUST use TCP only
- **Telegraphic documentation**: Sectioned by functional domain, minimal verbosity
- **pyproject.toml**: Modern Python packaging with setuptools build backend
- **Entry points**: MCP_Server/__init__.py (main), AbletonMCP_Remote_Script/__init__.py

## ANTI-PATTERNS (THIS PROJECT)
- NEVER attempt direct audio export (fundamentally impossible via Remote Script API)
- NEVER modify Ableton's Remote Script API
- NEVER use absolute parameter values (always normalize to 0.0-1.0)
- NEVER use UDP for Category D operations (30 critical commands: all get_*, delete_*, quantize, mix, crop, undo/redo, recording, heavy operations)
- NEVER modify LSP server configuration

## UNIQUE STYLES
- **Dual TCP/UDP architecture**: 108 TCP commands (request/response) vs 9 UDP commands (fire-and-forget for real-time control)
- **High-performance UDP**: Ultra-low latency (~0.2ms avg, 1.5ms P99), 1386+ Hz throughput for parameter sweeps
- **Manual audio export workflow**: Remote Script can't export audio → requires manual export in Ableton UI or Max for Live device
- **Project-specific UDP eligibility**: 9 commands pre-approved for UDP (set_device_parameter, set_track_*, set_clip_launch_mode, fire_clip, set_master_volume)
- **2-hour automation patterns**: dub_techno_2h uses timer-based scene progression, filter automation, section-based volume changes

## MUSIC THEORY & PERFORMANCE TOOLS (21 Commands)

### Constants
- **CAMELOT_WHEEL**: 24-key mapping for harmonic mixing (Camelot notation)
- **CHORD_INTERVALS**: 12 chord types (major, minor, dim, aug, maj7, min7, dom7, dim7, sus2, sus4, add9, power)
- **SCALE_INTERVALS**: 9 scale types (major, minor, dorian, phrygian, lydian, mixolydian, pentatonic_major, pentatonic_minor, blues)
- **DRUM_PATTERNS**: 6 genre patterns (one_drop, rockers, steppers, house_basic, techno_4x4, dub_techno)

### Scales
#### Scale Intervals and Character
| Scale            | Intervals (Semitones) | Character/Usage                          | MCP Command Example |
|------------------|-----------------------|-------------------------------------------|------------------------|
| Major            | 0, 2, 4, 5, 7, 9, 11   | Bright, happy, uplifting                | `create_scale_reference_clip` |
| Minor (Natural)  | 0, 2, 3, 5, 7, 8, 10   | Dark, melancholic, introspective        | `snap_notes_to_scale` |
| Dorian           | 0, 2, 3, 5, 7, 9, 10   | Jazz, funk, soulful                     | `fire_scene_with_transpose` |
| Phrygian         | 0, 1, 3, 5, 7, 8, 10   | Exotic, Spanish, metal                  | `batch_transpose_clips` |
| Lydian           | 0, 2, 4, 6, 7, 9, 11   | Dreamy, floating, film scores           | `apply_filter_buildup` |
| Mixolydian       | 0, 2, 4, 5, 7, 9, 10   | Blues, rock, jam bands                  | `transpose_all_playing_clips` |
| Pentatonic Major | 0, 2, 4, 7, 9          | Universal, pop, folk                    | `create_chord_progression` |
| Pentatonic Minor | 0, 3, 5, 7, 10         | Blues, rock, soloing                    | `apply_energy_curve` |
| Blues            | 0, 3, 5, 6, 7, 10      | Blues, jazz, soul                       | `set_global_quantization` |

#### Grid Patterns for Controller Layouts
```
[ Launchpad / Push Layout Example ]
+-----------------+   +-----------------+
| C Major         |   | A Minor         |
| 1 3 5 6 8 10 12 |   | 1 3 4 6 8 9  11 |
|                 |   |                 |
| Chord: C-E-G    |   | Chord: A-C-E    |
+-----------------+   +-----------------+

[ APC Mini Layout Example ]
+-----------------+-----------------+
| Scale Notes     | Chord Triads    |
|                 |                 |
| C D E F G A B   | I  III  V       |
|                 |                 |
+-----------------+-----------------+
```

### Chord Progressions (Organized by Genre)
#### Common Chord Progressions
| Genre          | Progression (Roman Numerals) | Key Example | MCP Command Example |
|---------------|-----------------------------|-------------|------------------------|
| Pop           | I-V-vi-IV                    | C Major     | `create_chord_progression` |
| Rock          | I-IV-V                      | G Major     | `fire_scene_with_transpose` |
| Jazz          | ii-V-I                      | F Major     | `batch_transpose_clips` |
| Blues         | I-I-I-I IV-IV-I-I V-IV-I-I  | A Minor     | `apply_filter_buildup` |
| EDM           | i-V-vi-IV (Minor)           | A Minor     | `transpose_all_playing_clips` |
| Hip-Hop       | i-bVI-bIII-bVII             | C Minor     | `apply_energy_curve` |

#### Jazz Progressions
- **ii-V-I**: The most common jazz progression (e.g., Dm7 → G7 → Cmaj7 in C Major).
- **Coltrane Changes**: i-bIII-bVI-bII-V-I (e.g., Im7 → #Idim7 → iim7 → V7 → I).
- **Rhythm Changes**: I-vi-ii-V (e.g., C → Am → Dm → G in C Major).

### Harmonic Mixing / Camelot Wheel Reference
#### Camelot Wheel Cheat Sheet
```
        8B (Gb) -------- 9B (Db)
      /                 \
    7B (B)             10B (Ab)
   /                   \
12B (F)               11B (Eb)
   \                   /
    1B (A) ---------- 2B (E)
     \               /
      12A (C#m) --- 1A (F#m)
       \           /
        11A (G#m) / 2A (C#m)
         \     /
          10A (Dm)

One-Hour Transition Path (Minimal Energy Change):
8B → 9B → 10B → 11B → 12B → 1B → 2B → 3B → 5A → 8A → 8B
```

### Rhythm Patterns in Grid Notation
#### House Basic (4/4)
```
Kick:  |X---|----|X---|----|
Clap: |----|X---|----|X---|
HiHat: |X-X-|X-X-|X-X-|X-X-|
```

#### Techno 4x4 (Driving)
```
Kick:  |X---|----|X---|----|X---|----|X---|----|
HiHat: |--X-|--X-|--X-|--X-|--X-|--X-|--X-|--X-|
```

#### Dub Techno (Syncopated)
```
Kick:  |X---|----|--X-|----|X---|----|--X-|----|
Snare: |----|X---|----|X---|----|X---|----|----|
HiHat: |X-X-|X---|X-X-|X---|X-X-|X---|X-X-|X---|
```

### Tempo Ranges by Genre
| Genre          | Tempo (BPM) | MCP Command Example |
|---------------|--------------|------------------------|
| Deep House    | 115-125      | `set_tempo` |
| Techno        | 125-140      | `set_tempo` |
| Dub Techno    | 110-120      | `set_tempo` |
| Drum & Bass   | 160-180      | `set_tempo` |
| Hip-Hop       | 85-95        | `set_tempo` |
| Trance        | 130-150      | `set_tempo` |
| Downtempo     | 70-90        | `set_tempo` |

### Transposition Guide with MCP Commands
- **Transpose a single clip**: `transpose_clip(track_index, clip_index, semitones)`
- **Transpose all playing clips**: `transpose_all_playing_clips(semitones)`
- **Batch transpose clips**: `batch_transpose_clips(clips=[{"track": 0, "clip": 0}], semitones=2)`
- **Fire scene with transposition**: `fire_scene_with_transpose(scene_index=0, semitones=2)`

### Live Performance Tips Using Theory
#### Clip Launch Timing
- Use `set_global_quantization("1 Bar")` to sync clip launches to the grid.
- Example: `fire_clip(track_index=0, clip_index=0)` will launch at the next bar.

#### Crossfading Between Tracks
- Use `apply_energy_curve` to automate volume and filter changes:
  ```json
  {
    "parameter_changes": [
      {"track_index": 0, "device_index": 0, "parameter_index": 0, "start_value": 0.8, "end_value": 0.2},
      {"track_index": 1, "device_index": 0, "parameter_index": 0, "start_value": 0.2, "end_value": 0.8}
    ],
    "duration_beats": 16,
    "steps": 16
  }
  ```

#### Dummy Clips for Control
- Create empty clips with names like "FILTER_UP_8B" to trigger automation:
  ```
  apply_filter_buildup(track_index=0, device_index=0, start_value=0.2, end_value=0.9, duration_beats=16)
  ```

#### Energy Management
- Use `apply_drop` to reset energy before a build:
  ```
  apply_drop(tracks_to_drop=[0, 1, 2], filter_param_index=0, drop_filter_value=0.2, return_delay_beats=8)
  ```

#### Harmonic Mixing
- Transition to harmonically compatible keys using the Camelot Wheel:
  ```
  get_compatible_keys("8A") → {"one_up": ["9A"]}
  transpose_all_playing_clips(semitones=2)  // e.g., A Minor → C Minor (8A → 9A)
  ```

### Sources
- **Camelot Wheel**: Mixed In Key (https://mixedinkey.com/)
- **Scale Intervals**: Music Theory for Dummies
- **Chord Progressions**: Hooktheory (https://www.hooktheory.com/)
- **Drum Patterns**: Attack Magazine (https://www.attackmagazine.com/)

## NOTES
- **Max for Live device**: Required for audio export, but must be manually triggered (bang inlet) - no Remote Script control
- **Ableton Remote Script limitations**: Cannot export/save audio files, cannot trigger export dialog
- **Dual-server performance**: UDP is 100-250x faster than TCP for parameter updates, but TCP is required for 30 critical operations
- **Cache directories**: .pytest_cache, .ruff_cache, __pycache__, .sisyphus - can be safely excluded from analysis
- **Large files**: MCP_Server/server.py (4,234 lines), AbletonMCP_Remote_Script/__init__.py (3,622 lines)