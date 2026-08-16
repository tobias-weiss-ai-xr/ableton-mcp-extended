# GOLDEN_RATIO_STUDIO - API REFERENCE

## **Module: generate_all_genres_refactored**

### **Classes**

#### **Genre (Enum)**
Music genres supported by the system.

```python
class Genre(Enum):
    DUB_REGGAE = "dub_reggae"
    DUB_TECHNO = "dub_techno"
    DEEP_HOUSE = "deep_house"
    TECH_HOUSE = "tech_house"
    HIP_HOP = "hip_hop"
    TRAP = "trap"
    DNB = "dnb"
    AMBIENT = "ambient"
```

---

#### **MIDINote (Dataclass)**
Type-safe MIDI note with validation.

```python
@dataclass
class MIDINote:
    time: float          # Note start position (beats)
    pitch: int          # MIDI pitch (0-127)
    velocity: int       # MIDI velocity (1-127)
    duration: float     # Note length (beats)
    
    def validate(self) -> bool:
        """Validate note is within MIDI ranges."""
        return (
            0 <= self.time and
            MIDIConstants.MIN_PITCH <= self.pitch <= MIDIConstants.MAX_PITCH and
            MIDIConstants.MIN_VELOCITY <= self.velocity <= MIDIConstants.MAX_VELOCITY and
            self.duration > 0
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for XML generation."""
        return {
            'time': self.time,
            'pitch': self.pitch,
            'velocity': self.velocity,
            'duration': self.duration
        }
```

**Usage:**
```python
from generate_all_genres_refactored import MIDINote

note = MIDINote(0.0, 36, 100, 0.5)
if note.validate():
    print("Note is valid")
    data = note.to_dict()
```

---

#### **PatternGenerator (Abstract Base Class)**
Base class for all pattern generators.

```python
class PatternGenerator(ABC):
    def __init__(self, genre: Genre):
        self.genre = genre
        self._random = random.Random()
    
    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducible generation."""
        self._random.seed(seed)
    
    @abstractmethod
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        """Generate MIDI notes for this pattern."""
        pass
```

**Usage:**
```python
from generate_all_genres_refactored import PatternGenerator, Genre, MIDINote

class MyPattern(PatternGenerator):
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        notes = []
        for bar in range(bar_count):
            notes.append(MIDINote(bar * 4, 36, 100, 0.3))
        return notes

pattern = MyPattern(Genre.DUB_REGGAE)
pattern.set_seed(42)
notes = pattern.generate(16)
```

---

#### **DrumPattern (Abstract Base Class)**
Specialized base class for drum patterns.

```python
class DrumPattern(PatternGenerator):
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        """Generate drum pattern across multiple bars."""
        notes = []
        for bar in range(bar_count):
            notes.extend(self.generate_bar(bar, **kwargs))
        return notes
    
    @abstractmethod
    def generate_bar(self, bar_number: int, **kwargs) -> List[MIDINote]:
        """Generate drum pattern for a single bar."""
        pass
```

**Usage:**
```python
class MyKickPattern(DrumPattern):
    def generate_bar(self, bar_number: int, **kwargs) -> List[MIDINote]:
        return [MIDINote(bar_number * 4, MIDIConstants.KICK, 115, 0.3)]
```

---

#### **BassPattern (Abstract Base Class)**  
Specialized base class for bass patterns.

```python
class BassPattern(PatternGenerator):
    def generate(self, bar_count: int, key: str = "C minor", **kwargs) -> List[MIDINote]:
        """Generate bass pattern across multiple bars."""
        notes = []
        for bar in range(bar_count):
            notes.extend(self.generate_bar(bar, key=key, **kwargs))
        return notes
    
    @abstractmethod
    def generate_bar(self, bar_number: int, key: str = "C minor", **kwargs) -> List[MIDINote]:
        """Generate bass pattern for a single bar."""
        pass
```

**Usage:**
```python
class MyBassPattern(BassPattern):
    def generate_bar(self, bar_number: int, key: str = "C minor", **kwargs) -> List[MIDINote]:
        return [MIDINote(bar_number * 4, 36, 110, 2.0)]
```

---

### **Concrete Pattern Classes**

#### **DubReggaeKickPattern**
Authentic one-drop dub reggae kick pattern.

```python
class DubReggaeKickPattern(DrumPattern):
    def generate_bar(self, bar_number: int, **kwargs) -> List[MIDINote]:
        # One drop: kick on beat 1 only
        # Ghost kick (bar 2, beat 3.8) every 4 bars
```

#### **DubReggaeBassPattern**
Dub reggae bassline with sub-bass layer.

```python
class DubReggaeBassPattern(BassPattern):
    def generate_bar(self, bar_number: int, key: str = "C minor", **kwargs) -> List[MIDINote]:
        # Main bass + sub-bass (octave down)
```

#### **DubReggaeSkankPattern**
Authentic reggae guitar skank pattern.

```python
class DubReggaeSkankPattern(PatternGenerator):
    def generate(self, bar_count: int, key: str = "C minor", **kwargs) -> List[MIDINote]:
        # Skank on offbeats (2 and 4)
        # Muted then open pattern
```

#### **DubTechnoKickPattern**
Four-on-the-floor techno kick with variation.

```python
class DubTechnoKickPattern(DrumPattern):
    def generate_bar(self, bar_number: int, **kwargs) -> List[MIDINote]:
        # Four-on-floor with velocity variation
        # Occasional offbeat kick (bar 8)
```

#### **HouseKickPattern**
House kick with swing pocket.

```python
class HouseKickPattern(DrumPattern):
    def generate_bar(self, bar_number: int, **kwargs) -> List[MIDINote]:
        # Four-on-floor with 20ms swing on offbeats
```

#### **HouseHiHatPattern**
8th-note hi-hat pattern.

```python
class HouseHiHatPattern(PatternGenerator):
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        # 8th-note hi-hats with offbeat emphasis
```

#### **AmbientPattern**
Ethereal ambient pads with chord clusters.

```python
class AmbientPattern(PatternGenerator):
    def generate(self, bar_count: int, key: str = "C minor", **kwargs) -> List[MIDINote]:
        # Dense chord clusters (7 notes)
        # Half-bar evolution for ambient feel
```

---

### **Configuration Classes**

#### **GenreTrackConfig**
Configuration for a single track in a genre project.

```python
@dataclass
class GenreTrackConfig:
    name: str                              # Track name
    track_type: TrackType                   # Track type enum
    pattern_generator: Optional[PatternGenerator]  # Pattern generator
    midi_channel: int = 0                 # MIDI channel
    volume: float = 0.75                  # Track volume
    pan: float = 0.0                      # Track pan
```

**Usage:**
```python
from generate_all_genres_refactored import (
    GenreTrackConfig, TrackType, Genre, DubReggaeKickPattern
)

kick_config = GenreTrackConfig(
    name="Kick Drum",
    track_type=TrackType.KICK,
    pattern_generator=DubReggaeKickPattern(Genre.DUB_REGGAE),
    volume=0.8,
    pan=0.0
)
```

---

#### **GenreProjectConfig**
Complete configuration for a genre project.

```python
@dataclass
class GenreProjectConfig:
    genre: Genre                           # Genre enum
    bpm: int                               # Tempo
    key: str                               # Musical key
    sections: List[str]                    # Arrangement sections
    tracks: List[GenreTrackConfig]         # Track configurations
```

**Usage:**
```python
from generate_all_genres_refactored import (
    GenreProjectConfig, Genre
)

config = GenreProjectConfig(
    genre=Genre.DUB_REGGAE,
    bpm=78,
    key="C Minor",
    sections=['INTRO', 'DROP', 'OUTRO'],
    tracks=[kick_config, bass_config, skank_config]
)
```

---

### **Main Generator Class**

#### **GenreProjectGenerator**
Main class for generating complete genre projects.

```python
class GenreProjectGenerator:
    _GENRE_CONFIGS: Dict[Genre, GenreProjectConfig] = {}
    
    @classmethod
    def register_genre_config(cls, genre: Genre, config: GenreProjectConfig):
        """Register a genre configuration."""
    
    @classmethod
    def get_genre_config(cls, genre: Genre) -> Optional[GenreProjectConfig]:
        """Get genre configuration."""
    
    @classmethod
    def generate_project(cls, genre: Genre, bar_count: int = 128,
                        seed: Optional[int] = None) -> Optional[Dict]:
        """Generate complete project for specified genre.
        
        Args:
            genre: Genre to generate
            bar_count: Number of bars (1-1000 required)
            seed: Random seed for reproducibility
        
        Returns:
            Project data dict or None if invalid parameters
        
        Raises:
            ValueError: If bar_count < 0 or > 1000
        """
```

**Usage:**
```python
from generate_all_genres_refactored import GenreProjectGenerator, Genre

# Generate project
project = GenreProjectGenerator.generate_project(
    genre=Genre.DUB_REGGAE,
    bar_count=128,
    seed=42
)

# Access project data
print(project['genre'])      # - Genre name
print(project['bpm'])        # - Tempo
print(project['key'])        # - Musical key
print(project['patterns'])   # - Track-to-notes mapping
```

---

### **Constants Classes**

#### **MIDIConstants**
MIDI hardware limits and standard values.

```python
class MIDIConstants:
    MIN_PITCH = 0
    MAX_PITCH = 127
    MIN_VELOCITY = 1
    MAX_VELOCITY = 127
    
    # Standard drum pitches
    KICK = 36
    SNARE = 40
    HI_HAT_CLOSED = 42
    HI_HAT_OPEN = 46
    CLAP = 39
    CRASH = 49
    RIDE = 51
    LOW_TOM = 45
    MID_TOM = 48
    HIGH_TOM = 50
    
    # Standard instrument ranges
    GUITAR_MUTE = 48
    GUITAR_OPEN = 52
    
    # Bass octave ranges  
    SUB_BASS_MIN = 12
    SUB_BASS_MAX = 36
    BASS_MIN = 24
    BASS_MAX = 48
```

**Usage:**
```python
from generate_all_genres_refactored import MIDIConstants

note = MIDINote(0.0, MIDIConstants.KICK, 100, 0.5)
```

---

#### **HumanizationConstants**
Humanization parameters for different genres.

```python
class HumanizationConstants:
    # Velocity variation (%)
    VELOCITY_TIGHT = 0.06
    VELOCITY_NORMAL = 0.12
    VELOCITY_LOOSE = 0.18
    
    # Timing variation (beats)
    TIMING_TIGHT = 0.06
    TIMING_NORMAL = 0.12
    TIMING_LOOSE = 0.15
    
    # Duration variation (%)
    DURATION_TIGHT = 0.10
    DURATION_NORMAL = 0.20
    DURATION_LOOSE = 0.25
```

**Usage:**
```python
from generate_all_genres_refactored import HumanizationConstants

# Choose appropriate level based on genre
humanization = HumanizationConstants.VELOCITY_LOOSE  # For dub reggae
```

---

#### **GenreConstants**
Genre-specific BPM and key recommendations.

```python
class GenreConstants:
    DUB_REGGAE = {'bpm': 78, 'key': 'C Minor', 'humanization': 'LOOSE'}
    DUB_TECHNO = {'bpm': 135, 'key': 'E Minor', 'humanization': 'TIGHT'}
    DEEP_HOUSE = {'bpm': 124, 'key': 'G# Minor', 'humanization': 'NORMAL'}
    # ... other genres
```

---

## **Module: als_generator_fixed**

### **Classes**

#### **AbletonTrack**
Ableton track configuration.

```python
@dataclass
class AbletonTrack:
    id: int                              # Track ID number
    name: str                            # Track name
    notes: List[Dict]                    # MIDI notes (dict format)
    midi_channel: int = 0                # MIDI channel
    volume: float = 0.75                 # Track volume
    pan: float = 0.0                     # Track pan
    instrument_path: str = "Drums/Acoustic/Memphis Studio Kit"
```

---

#### **AbletonReturnTrack**
Ableton return track with effects.

```python
@dataclass
class AbletonReturnTrack:
    id: int                              # Track ID number
    name: str                            # Track name
    effects: List[str]                   # Effect device names
    volume: float = 0.8                  # Track volume
    pan: float = 0.0                     # Track pan
```

**Usage:**
```python
from als_generator_fixed import AbletonReturnTrack

echo_track = AbletonReturnTrack(
    id=0,
    name="Dub Echo",
    effects=["Tape Delay", "Ping Pong Delay"],
    volume=0.85
)
```

---

#### **AlexLiveXMLGenerator**
Generate Ableton Live XML structure.

```python
class AlexLiveXMLGenerator:
    MAJOR_VERSION = 5
    MINOR_VERSION = "12.0_12402"
    CREATOR = "Ableton Live 12.4.3"
    SCHEMA_CHANGE_COUNT = 5
    
    @staticmethod
    def escape_xml(text: str) -> str:
        """Escape special XML characters."""
    
    @staticmethod
    def create_midi_track_xml(track: AbletonTrack) -> str:
        """Create XML for a MIDI track."""
    
    @staticmethod
    def create_return_track_xml(track: AbletonReturnTrack) -> str:
        """Create XML for a return track."""
    
    @staticmethod
    def create_ableton_xml(midi_tracks: List[AbletonTrack],
                          return_tracks: List[AbletonReturnTrack],
                          bpm: int,
                          sections: List[str],
                          bar_count: int) -> str:
        """Create complete Ableton Live XML structure."""
```

**Usage:**
```python
from als_generator_fixed import AlexLiveXMLGenerator

xml = AlexLiveXMLGenerator.create_ableton_xml(
    midi_tracks=[kick_track, bass_track],
    return_tracks=[echo_track],
    bpm=78,
    sections=['INTRO', 'DROP', 'OUTRO'],
    bar_count=64
)
```

---

#### **AbletonProjectSaver**
Save Ableton projects with correct compression.

```python
class AbletonProjectSaver:
    FILE_HEADER = b' Golden Ratio Studio '
    
    @staticmethod
    def save_ableton_file(xml_content: str, filename: str) -> int:
        """Save Ableton project with proper compression.
        
        Args:
            xml_content: XML content to save
            filename: Output filename (.als)
        
        Returns:
            Compressed file size in bytes
        
        Raises:
            ValueError: If XML is too short or empty
            IOError: If file cannot be written
        """
    
    @staticmethod
    def load_ableton_file(filename: str) -> Optional[str]:
        """Load and decompress Ableton project file.
        
        Args:
            filename: Input filename (.als)
        
        Returns:
            XML content as string, or None if loading fails
        """
```

**Usage:**
```python
from als_generator_fixed import AbletonProjectSaver

# Save
xml = "<?xml version=\"1.0\"?>..."
size = AbletonProjectSaver.save_ableton_file(xml, "project.als")

# Load
content = AbletonProjectSaver.load_ableton_file("project.als")
```

---

## **Module: generate_complete**

### **Functions**

#### **generate_complete_project**
Generate and save complete Ableton project.

```python
def generate_complete_project(genre: Genre,
                             bar_count: int = 128,
                             seed: int = None,
                             output_file: str = None) -> dict:
    """Generate complete project with patterns and save to ALS file.
    
    Args:
        genre: Genre to generate
        bar_count: Number of bars (1-1000)
        seed: Random seed for reproducibility
        output_file: Output filename (optional, auto-generated if None)
    
    Returns:
        Project data dict with keys:
        - genre: Genre name
        - bpm: Tempo
        - key: Musical key
        - config: GenreProjectConfig object
        - patterns: Track-to-notes mapping
        - bar_count: Number of bars
        - filename: Output filename
        - file_size: File size in bytes
        - return_tracks: Number of return tracks
    
    Raises:
        ValueError: If generation fails
    
    Example:
        >>> project = generate_complete_project(
        ...     Genre.DUB_REGGAE,
        ...     bar_count=64,
        ...     seed=42
        ... )
        >>> print(project['filename'])
        'dub_reggae_enhanced.als'
    """
```

**Usage:**
```python
from generate_complete import generate_complete_project
from generate_all_genres_refactored import Genre

project = generate_complete_project(
    genre=Genre.DUB_REGGAE,
    bar_count=128,
    seed=42
)
```

---

## **Module: validation_tests**

### **Functions**

#### **test_syntax**
Test Python syntax compile.

```python
def test_syntax() -> bool:
    """Test that all modules compile without syntax errors."""
```

---

#### **test_imports**
Test imports and basic functionality.

```python
def test_imports() -> bool:
    """Test that all required modules import successfully."""
```

---

#### **run_all_tests**
Run all validation tests.

```python
def run_all_tests() -> bool:
    """Run all validation tests.
    
    Returns:
        True if all tests pass, False otherwise
    """
```

**Usage:**
```bash
python validation_tests.py
```

---

## **Enums**

### **TrackType**
MIDI track types used in genres.

```python
class TrackType(Enum):
    KICK = "kick"
    SNARE = "snare"
    HI_HAT = "hi_hat"
    BASS = "bass"
    SUB_BASS = "sub_bass"
    SYNTH = "synth"
    PAD = "pad"
    GUITAR = "guitar"
    ORGAN = "organ"
    PERCUSSION = "percussion"
```

---

## **Error Handling**

### **Standard Exceptions**

The following exceptions may be raised:

- **ValueError**: Invalid parameters (bar_count <= 0 or > 1000)
- **IOError**: File read/write errors
- **RuntimeError**: Pattern generation failures
- **KeyError**: Missing genre configuration

### **Logging**

The system uses Python's logging module:

```python
import logging
logger = logging.getLogger("GoldenRatioStudio")

# Standard log levels
logger.debug("Detailed internal info")
logger.info("Informational message")
logger.warning("Non-critical issue")
logger.error("Critical failure")
```

---

## **Best Practices**

### 1. Always Validate Notes

```python
note = MIDINote(0.0, 36, 100, 0.5)
if note.validate():
    # Use note
```

### 2. Use Seeds for Reproducibility

```python
project = GenreProjectGenerator.generate_project(
    Genre.DUB_REGGAE,
    bar_count=128,
    seed=42  # Same seed = same output
)
```

### 3. Check for Errors

```python
project = GenreProjectGenerator.generate_project(Genre.DUB_REGGAE, 128)
if project is None:
    print("Generation failed")
    return
```

### 4. Use Type Hints

```python
def my_pattern_generator(bar_count: int, 
                        key: str = "C minor") -> List[MIDINote]:
    """
    Generate custom pattern.
    
    Args:
        bar_count: Number of bars
        key: Musical key
    
    Returns:
        List of MIDI notes
    """
    pass
```

---

## **Quick Reference**

### Generate a Complete Project

```python
from generate_complete import generate_complete_project
project = generate_complete_project(Genre.DUB_REGGAE, 128, 42)
```

### Generate Pattern Only

```python
from generate_all_genres_refactored import GenreProjectGenerator, Genre
project = GenreProjectGenerator.generate_project(Genre.DUB_REGGAE, 128)
notes = project['patterns']['Kick Drum']
```

### Save Custom XML

```python
from als_generator_fixed import AlexLiveXMLGenerator, AbletonProjectSaver
xml = AlexLiveXMLGenerator.create_ableton_xml(...)
AbletonProjectSaver.save_ableton_file(xml, "custom.als")
```

### Validate System

```bash
python validation_tests.py
```

**BLESS UP - Complete API reference for Golden Ratio Studio! 🎛️📚**
