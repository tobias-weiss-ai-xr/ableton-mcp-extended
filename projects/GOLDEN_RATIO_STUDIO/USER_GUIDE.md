# GOLDEN_RATIO_STUDIO - USER GUIDE

## **Getting Started Quickly**

### Installation

```bash
# Clone or navigate to the project
cd C:/Users/Tobias/git/ableton-mcp-extended/GOLDEN_RATIO_STUDIO

# Verify Python is available (requires Python 3.8+)
python --version

# Validate the system
python validation_tests.py
```

### Your First Generated Track

```bash
# Generate a 64-bar dub reggae track (about 2 minutes at 78 BPM)
python generate_complete.py 64 42 dub_reggae

# Output: dub_reggae_enhanced.als
```

This creates a ready-to-use Ableton Live project with:
- ✅ 3 instrument tracks (Kick Drum, Bass, Guitar Skank)
- ✅ 3 return tracks (Dub Echo, Spring Reverb, Dub Filter)
- ✅ Complete arrangement (INTRO → ONE_DROP → DUB_SECTION_1 ... OUTRO)
- ✅ Validated MIDI notes (1,184 total)
- ✅ Compressed file size (~6.8 KB)

---

## **Command Reference**

### Basic Usage

```bash
python generate_complete.py [bars] [seed] [genre]
```

### Parameters

| Parameter | Required | Description | Valid Values | Default |
|-----------|----------|-------------|--------------|---------|
| **bars** | No | Number of bars to generate | 1-1000 | 128 |
| **seed** | No | Random seed for reproducibility | Any integer | None (random) |
| **genre** | No | Specific genre to generate | See genres below | All genres |

### Examples

```bash
# Generate all genres with default 128 bars
python generate_complete.py

# Generate just dub reggae (64 bars, seed 42)
python generate_complete.py 64 42 dub_reggae

# Generate deep house with 512 bars (long track)
python generate_complete.py 512 123 deep_house

# Generate single bar for testing
python generate_complete.py 1 99 dub_techno
```

### Available Genres

| Command | Genre | BPM | Key |
|---------|-------|-----|-----|
| `dub_reggae` | Dub Reggae | 78 | C Minor |
| `dub_techno` | Dub Techno | 135 | E Minor |
| `deep_house` | Deep House | 124 | G# Minor |
| `tech_house` | Tech House | 128 | A Minor |
| `hip_hop` | Hip-Hop | 92 | C Minor |
| `trap` | Trap | 140 | C Minor |
| `dnb` | Drum & Bass | 174 | G Minor |
| `ambient` | Ambient | 70 | C Minor |

---

## **Generated File Structure**

When you open a generated `.als` file in Ableton Live, you'll see:

### Instrument Tracks (varies by genre)

**Dub Reggae Example:**
```
├─ Kick Drum        - One-drop kick pattern with ghost notes
├─ Bass             - Dub bass with sub-bass layer
└─ Guitar Skank     - Reggae guitar skank (upstrokes)
```

**Deep House Example:**
```
├─ Kick             - Four-on-floor with swing
├─ Bass             - Groovy melodic bassline
└─ Hi-Hats          - 8th-note hi-hat pattern
```

### Return Tracks (varies by genre)

**Dub Reggae Example:**
```
├─ Dub Echo         - Tape delay (1/4 @ 75% feedback)
├─ Spring Reverb    - Spring reverb (3.2s decay)
└─ Dub Filter       - Auto filter + utility
```

### Arrangement

Projects include complete song structures:

```
[INTRO] → [ONE_DROP] → [DUB_SECTION_1] → [ROCKERS] → [DUB_DROP] →
[BUILD_UP] → [BASS_INVERSION] → [FINAL_DUB] → [RE_ENTRY] → [OUTRO]
```

Each section is marked with a scene in Ableton Live.

---

## **Python API**

### Basic API Usage

```python
from generate_complete import generate_complete_project
from generate_all_genres_refactored import Genre

# Generate programmatically
project = generate_complete_project(
    genre=Genre.DUB_REGGAE,
    bar_count=128,
    seed=42,
    output_file="my_dub_track.als"
)

# Access project data
print(f"Genre: {project['genre']}")
print(f"BPM: {project['bpm']}")
print(f"Key: {project['key']}")
print(f"Tracks: {len(project['patterns'])}")
print(f"File: {project['filename']} ({project['file_size']} bytes)")
```

### Pattern Generation Directly

```python
from generate_all_genres_refactored import Genre, GenreProjectGenerator

# Generate patterns without saving to file
project = GenreProjectGenerator.generate_project(
    genre=Genre.DEEP_HOUSE,
    bar_count=64,
    seed=123
)

# Output pattern data
for track_name, notes in project['patterns'].items():
    print(f"{track_name}: {len(notes)} notes")
    for note in notes[:5]:  # Show first 5 notes
        print(f"  - Time: {note.time:.2f}, Pitch: {note.pitch}, "
              f"Velocity: {note.velocity}, Duration: {note.duration:.2f}")
```

### Direct XML Generation

```python
from als_generator_fixed import (
    AlexLiveXMLGenerator,
    AbletonProjectSaver,
    AbletonTrack
)
from generate_all_genres_refactored import MIDINote

# Create custom track
custom_track = AbletonTrack(
    id=0,
    name="Custom Track",
    notes=[
        MIDINote(0.0, 36, 100, 0.5),
        MIDINote(1.0, 38, 95, 0.4),
    ],
    instrument_path="Instruments/Piano/Piano Melt"
)

# Generate XML
xml = AlexLiveXMLGenerator.create_ableton_xml(
    midi_tracks=[custom_track],
    return_tracks=[],
    bpm=120,
    sections=['INTRO', 'DROP'],
    bar_count=32
)

# Save to file
AbletonProjectSaver.save_ableton_file(xml, "custom_project.als")
```

---

## **Common Workflows**

### Workflow 1: Generate & Test

```bash
# Generate a quick test version
python generate_complete.py 16 88 dub_reggae

# Open in Ableton Live
# Press SPACE to play
# Test different tempos, instruments, effects
```

### Workflow 2: Generate & Modify

```bash
# Generate full project
python generate_complete.py 256 42 deep_house

# Open in Ableton Live
# Add your own instruments
# Modify MIDI notes
# Create variations
```

### Workflow 3: Batch Generation

```bash
# Generate all genres for review
python generate_complete.py 64 0

# Review each .als file
# Select best one for development
```

---

## **Tips & Tricks**

### Tempo Selection

- **Dub Reggae (78 BPM)**: Slow, relaxed dub feel
- **Deep House (124 BPM)**: Grosy house tempo
- **Tech House (128 BPM)**: Driving, energetic
- **Drum & Bass (174 BPM)**: Fast, aggressive

### Key Selection

- **Minor keys**: Darker, emotional (most electronic genres)
- **Major keys**: Bright, uplifting (some subgenres)

### Humanization Levels

- **TIGHT (6%)**: Precise, electronic (techno, electro)
- **NORMAL (12%)**: Natural, organic (house, dub)
- **LOOSE (18%)**: Relaxed, human (hip-hop, reggae)

### Reproducibility

Always use a seed when you want consistent results:

```bash
# Same seed = same output
python generate_complete.py 64 42 dub_reggae
python generate_complete.py 64 42 dub_reggae
# Both files are identical
```

---

## **Troubleshooting**

### Issue: "Invalid bar_count"
**Error:** `Invalid bar_count: 0. Must be > 0`

**Solution:** Use positive value:
```bash
# WRONG
python generate_complete.py 0 42 dub_reggae

# RIGHT
python generate_complete.py 64 42 dub_reggae
```

### Issue: "No configuration found for genre"
**Error:** `No configuration found for genre: DubReggae`

**Solution:** Use exact genre names (underscores, no spaces):
```bash
# WRONG
python generate_complete.py 64 42 DubReggae

# RIGHT
python generate_complete.py 64 42 dub_reggae
```

### Issue: Generated file won't open
**Possible cause:** Using older Ableton Live version

**Solution:** Update to Ableton Live 12.4.3 or later

### Issue: Too many generated notes
**Symptom:** Files getting too large

**Solution:** Reduce bar count:
```bash
# Too large
python generate_complete.py 1000 42 dnb

# Better
python generate_complete.py 256 42 dnb
```

---

## **Advanced Usage**

### Custom Pattern Creation

```python
from generate_all_genres_refactored import (
    PatternGenerator, MIDINote, MIDIConstants
)

class MyCustomPattern(PatternGenerator):
    def generate(self, bar_count, **kwargs):
        notes = []
        for bar in range(bar_count):
            # Add kick every beat
            for beat in range(4):
                time = bar * 4 + beat
                notes.append(MIDINote(time, MIDIConstants.KICK, 120, 0.3))
        return notes
```

### Adding New Genres

```python
from generate_all_genres_refactored import (
    Genre, GenreProjectConfig, GenreTrackConfig,
    GenreProjectGenerator, TrackType
)

# Define enum
class Genre(Enum):
    MY_GENRE = "my_genre"

# Create pattern
class MyGenreKick(DrumPattern):
    def generate_bar(self, bar_number, **kwargs):
        return [MIDINote(bar_number * 4, MIDIConstants.KICK, 115, 0.3)]

# Configure
config = GenreProjectConfig(
    Genre.MY_GENRE,
    120,
    "D Minor",
    ['INTRO', 'DROP', 'OUTRO'],
    [GenreTrackConfig("Kick", TrackType.KICK, MyGenreKick(Genre.MY_GENRE))]
)

# Register
GenreProjectGenerator.register_genre_config(Genre.MY_GENRE, config)
```

---

## **Performance Guidelines**

### Maximum Recommended Values

- **Bar count**: 1000 (generates ~1-5 minutes of music)
- **Notes per track**: 500 (file size consideration)
- **Tracks per project**: 10 (Ableton Live practical limit)

### File Sizes

- **16 bars**: ~1-2 KB
- **64 bars**: ~5-10 KB
- **256 bars**: ~15-30 KB
- **1000 bars**: ~50-100 KB

### Generation Time

- **16 bars**: <0.001s
- **128 bars**: ~0.002s
- **1000 bars**: ~0.015s

---

## **Next Steps**

1. **Start with defaults** - Generate a few tracks to understand the system
2. **Customize parameters** - Try different bar counts, seeds, genres
3. **Modify in Ableton** - Open files and make your own changes
4. **Create variations** - Use the same seed with different parameters
5. **Build your own** - Add custom patterns and genres

---

## **Additional Resources**

- `README.md` - Project overview and quick reference
- `API.md` - Complete API documentation
- `GOLDEN_RATIO_STUDIO_COMPLETE.md` - Genre-specific details
- `validation_tests.py` - System validation

## **Support**

For issues or questions:
1. Check this guide
2. Review API documentation
3. Run `validation_tests.py`
4. Consult project documentation

**BLESS UP - Start creating electronic music with multi-genre power! 🎛️🎵**
