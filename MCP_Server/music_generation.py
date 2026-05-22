# Algorithmic Music Generation Pipeline
# Inspired by isobar (ideoforms/isobar) and subsequence (simonholliday/subsequence)
# Provides pattern-based composition instead of manual note arrays

import random
import math
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# SCALE SYSTEM
# ============================================================================

class ScaleType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    HARMONIC_MINOR = "harmonic_minor"
    MELODIC_MINOR = "melodic_minor"

# Intervals from root (semitones)
SCALE_INTERVALS = {
    ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
    ScaleType.MINOR: [0, 2, 3, 5, 7, 8, 10],
    ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
    ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
    ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
    ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
    ScaleType.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
    ScaleType.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],
}

@dataclass
class Scale:
    root: int  # MIDI root note (e.g., 60 = C4)
    scale_type: ScaleType
    
    @property
    def intervals(self) -> List[int]:
        return SCALE_INTERVALS[self.scale_type]
    
    def degree_to_midi(self, degree: int, octave_offset: int = 0) -> int:
        """Convert scale degree to MIDI note. Degree can be negative (below root)."""
        octave = degree // 7
        degree_in_octave = degree % 7
        if degree_in_octave < 0:
            degree_in_octave += 7
            octave -= 1
        interval = self.intervals[degree_in_octave]
        return self.root + interval + (octave + octave_offset) * 12
    
    def scale_notes_in_range(self, low: int, high: int) -> List[int]:
        """Return all scale notes within MIDI range [low, high]."""
        notes = []
        current = low
        while current <= high:
            for interval in self.intervals:
                note = current + interval
                if low <= note <= high:
                    notes.append(note)
                elif note > high:
                    break
            current += 12
        return sorted(set(notes))


# ============================================================================
# CHORD SYSTEM
# ============================================================================

@dataclass
class Chord:
    root: int  # MIDI root note
    quality: str  # "major", "minor", "min7", "maj7", "dom7", "dim", "aug", "sus2", "sus4"
    
    # Intervals from root for chord qualities
    CHORD_INTERVALS = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "major7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
        "dom7": [0, 4, 7, 10],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8],
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
        "power": [0, 7],  # Octave only
    }
    
    @property
    def intervals(self) -> List[int]:
        return self.CHORD_INTERVALS.get(self.quality, [0, 4, 7])
    
    @property
    def notes(self) -> List[int]:
        return [self.root + i for i in self.intervals]
    
    def __str__(self) -> str:
        return f"{self.root}({self.quality})"


class ChordProgression:
    """Build chord progressions from Roman numeral notation."""
    
    # Minor scale chord degrees (quality by position)
    MINOR_QUALITIES = ["min7", "dim7", "maj7", "min7", "min7", "maj7", "dom7"]
    MAJOR_QUALITIES = ["maj7", "min7", "min7", "maj7", "dom7", "min7", "min7b5"]
    
    # Common chord mappings for dub techno
    DUB_TECHNO_PROGRESSIONS = {
        "i-VII-VI-V": ["min7", "dom7", "min7", "dom7"],  # Fm7 - Eb7 - Dbm7 - Cm7
        "i-VII-III-VII": ["min7", "dom7", "min7", "dom7"],
        "i-VI-III-VII": ["min7", "min7", "min7", "dom7"],
        "i-iv-VII-iii": ["min7", "min7", "dom7", "min7"],
        "i-VII-iv-V": ["min7", "dom7", "min7", "dom7"],
    }
    
    def __init__(self, root: int, scale_type: ScaleType = ScaleType.MINOR):
        self.root = root
        self.scale_type = scale_type
        self.chords: List[Chord] = []
    
    @staticmethod
    def from_roman(root: int, numeral: str, scale_type: ScaleType = ScaleType.MINOR) -> Chord:
        """Create a chord from Roman numeral (e.g., 'i7', 'IVmaj7', 'Vdom7')."""
        scale = Scale(root, scale_type)
        
        # Parse numeral
        numeral = numeral.lower()
        
        # Extract degree number
        degree_map = {'i': 0, 'ii': 1, 'iii': 2, 'iv': 3, 'v': 4, 'vi': 5, 'vii': 6}
        degree = 0
        for char in numeral:
            if char in degree_map:
                degree = degree_map[char]
                break
        
        # Extract quality from suffix
        quality = "minor" if numeral[0].islower() else "major"
        if "maj7" in numeral or "M7" in numeral:
            quality = "min7" if numeral[0].islower() else "maj7"
        elif "dom7" in numeral or "7" in numeral:
            quality = "dom7"
        elif "dim" in numeral:
            quality = "dim"
        elif "aug" in numeral:
            quality = "aug"
        elif "sus4" in numeral:
            quality = "sus4"
        elif "sus2" in numeral:
            quality = "sus2"
        
        # Calculate chord root from scale degree
        chord_root = scale.degree_to_midi(degree, octave_offset=1)
        return Chord(chord_root, quality)
    
    @staticmethod
    def build_progression(
        root: int,
        numerals: List[str],
        scale_type: ScaleType = ScaleType.MINOR
    ) -> List[Chord]:
        """Build full chord progression from Roman numerals."""
        return [ChordProgression.from_roman(root, n, scale_type) for n in numerals]
    
    @staticmethod
    def from_preset(root: int, preset: str) -> List[Chord]:
        """Build progression from preset name (e.g., 'i-VII-VI-V')."""
        numerals = preset.split("-")
        return ChordProgression.build_progression(root, numerals)


# ============================================================================
# EUCLIDEAN RHYTHM GENERATOR
# ============================================================================

def euclidean_rhythm(steps: int, pulses: int, rotation: int = 0) -> List[int]:
    """
    Generate Euclidean rhythm using Bjorklund algorithm.
    
    Creates the most evenly distributed rhythm for given steps and pulses.
    Used for authentic groove patterns (e.g., Afrobeat, Balkan, techno).
    
    Args:
        steps: Total steps in pattern (e.g., 16 for 16th notes in a bar)
        pulses: Number of active pulses (e.g., 3 for tresillo)
        rotation: Rotate pattern by N positions
        
    Returns:
        List of beat positions (as fractions of step) that should play
        
    Examples:
        euclidean_rhythm(16, 3) → tresillo: [0, 0.5, 1] repeating
        euclidean_rhythm(16, 4) → classic four on floor
        euclidean_rhythm(16, 5) → interesting syncopation
    """
    if pulses == 0:
        return []
    if pulses == steps:
        return list(range(steps))
    
    # Bjorklund algorithm
    pattern = []
    bucket = [0] * steps
    
    for i in range(pulses):
        bucket[i] = 1
    
    for _ in range(steps - pulses):
        # Find first non-zero bucket
        for i in range(steps):
            if bucket[i] > 0:
                bucket[i] -= 1
                # Find next non-zero bucket
                for j in range(i + 1, steps):
                    if bucket[j] > 0:
                        bucket[j] -= 1
                        # Move '1' from i to j
                        pattern.append((i, j))
                        break
                break
    
    # Build final pattern
    result = [0] * steps
    for i in range(steps):
        count = sum(1 for p in pattern if p[0] == i)
        result[i] = count
    
    # Convert to positions
    positions = []
    pos = 0
    for i in range(steps):
        if result[i] > 0:
            positions.append(pos)
        pos += 1
    
    # Rotate
    positions = positions[rotation % len(positions):] + positions[:rotation % len(positions)]
    
    return positions


def generate_euclidean_pattern(
    steps: int,
    pulses: int,
    duration: float = 0.25,
    rotation: int = 0
) -> List[Tuple[float, float]]:
    """
    Generate Euclidean rhythm as (start_time, duration) tuples.
    
    Args:
        steps: Total subdivision (e.g., 16 for 16th note grid)
        pulses: Number of hits
        duration: Length of each hit (default 0.25 = 16th)
        rotation: Pattern rotation
        
    Returns:
        List of (start_time, duration) tuples
    """
    positions = euclidean_rhythm(steps, pulses, rotation)
    return [(pos * duration, duration * 0.9) for pos in positions]


# ============================================================================
# PATTERN CLASSES (Inspired by isobar)
# ============================================================================

class PNone:
    """Empty pattern - produces no events."""
    def generate(self, cycle: int = 0) -> List[Any]:
        return []


class PSequence:
    """Static sequence - cycles through fixed values."""
    
    def __init__(self, values: List[Any], repeats: int = 1):
        self.values = values
        self.repeats = repeats
    
    def generate(self, cycle: int = 0) -> List[Any]:
        return self.values * self.repeats
    
    def __len__(self) -> int:
        return len(self.values) * self.repeats


class PSeries:
    """Arithmetic series - generates values with fixed step."""
    
    def __init__(self, start: float, step: float, length: int):
        self.start = start
        self.step = step
        self.length = length
    
    def generate(self, cycle: int = 0) -> List[float]:
        return [self.start + i * self.step for i in range(self.length)]


class PArpeggiate:
    """Arpeggiate a chord pattern."""
    
    def __init__(self, chords: List[List[int]], direction: str = "up"):
        self.chords = chords
        self.direction = direction
    
    def generate(self, cycle: int = 0) -> List[int]:
        notes = []
        for chord in self.chords:
            if self.direction == "up":
                notes.extend(sorted(chord))
            elif self.direction == "down":
                notes.extend(sorted(chord, reverse=True))
            elif self.direction == "up_down":
                sorted_chord = sorted(chord)
                notes.extend(sorted_chord + list(reversed(sorted_chord[1:-1])))
            elif self.direction == "random":
                notes.extend(random.sample(chord, len(chord)))
        return notes


class PLoop:
    """Loop a pattern N times."""
    
    def __init__(self, pattern: List[Any], times: int = 2):
        self.pattern = pattern
        self.times = times
    
    def generate(self, cycle: int = 0) -> List[Any]:
        return self.pattern * self.times


class PPingPong:
    """Ping-pong pattern - forward then backward."""
    
    def __init__(self, pattern: List[Any]):
        self.pattern = pattern
    
    def generate(self, cycle: int = 0) -> List[Any]:
        if len(self.pattern) <= 1:
            return self.pattern
        return self.pattern + list(reversed(self.pattern[1:-1]))


class PBrown:
    """Brownian/random walk for velocity or parameter modulation."""
    
    def __init__(self, base: float, step: float, min_val: float, max_val: float):
        self.base = base
        self.step = step
        self.min_val = min_val
        self.max_val = max_val
        self.current = base
    
    def generate(self, cycle: int = 0) -> List[float]:
        values = []
        for _ in range(cycle if cycle > 0 else 1):
            self.current += random.uniform(-self.step, self.step)
            self.current = max(self.min_val, min(self.max_val, self.current))
            values.append(self.current)
        return values
    
    def next(self) -> float:
        return self.generate(1)[0]


class PRandom:
    """Random values within range."""
    
    def __init__(self, low: float, high: float, count: int = 1):
        self.low = low
        self.high = high
        self.count = count
    
    def generate(self, cycle: int = 0) -> List[float]:
        return [random.uniform(self.low, self.high) for _ in range(self.count)]


class PEuclidean:
    """Euclidean rhythm pattern."""
    
    def __init__(self, steps: int, pulses: int, duration: float = 0.25, rotation: int = 0):
        self.steps = steps
        self.pulses = pulses
        self.duration = duration
        self.rotation = rotation
    
    def generate(self, cycle: int = 0) -> List[Tuple[float, float]]:
        return generate_euclidean_pattern(self.steps, self.pulses, self.duration, self.rotation)


class PMarkov:
    """
    Markov chain-based melodic sequence generator.
    
    Generates melodies using a transition probability matrix. More musically
    coherent than pure random because it respects melodic motion patterns
    (step vs leap likelihoods).
    
    Usage:
        # Transition matrix: P(next_degree | current_degree)
        # Rows sum to 1.0
        transitions = {
            0: {0: 0.1, 1: 0.3, 2: 0.3, 3: 0.2, 4: 0.1},
            1: {0: 0.2, 1: 0.1, 2: 0.4, 3: 0.2, 4: 0.1},
            2: {0: 0.1, 1: 0.3, 2: 0.2, 3: 0.3, 4: 0.1},
            3: {0: 0.2, 1: 0.2, 2: 0.3, 3: 0.1, 4: 0.2},
            4: {0: 0.3, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.1},
        }
        markov = PMarkov(transitions, scale)
        melody = markov.generate(length=32)
    """
    
    def __init__(self, transitions: Dict[int, Dict[int, float]], scale: Optional[Scale] = None):
        """
        Initialize Markov melody generator.
        
        Args:
            transitions: Dict mapping degree -> {next_degree: probability}
            scale: Scale object for MIDI conversion (optional)
        """
        self.transitions = transitions
        self.scale = scale
        self._current_degree = 0
    
    def generate(self, length: int = 16, start_degree: int = 0) -> List[int]:
        """
        Generate melodic sequence.
        
        Args:
            length: Number of notes to generate
            start_degree: Starting scale degree
            
        Returns:
            List of MIDI note numbers (if scale provided) or scale degrees
        """
        self._current_degree = start_degree
        notes = []
        
        for _ in range(length):
            # Add current note
            if self.scale:
                midi_note = self.scale.degree_to_midi(self._current_degree, octave_offset=1)
                notes.append(midi_note)
            else:
                notes.append(self._current_degree)
            
            # Transition to next note
            self._current_degree = self._next_degree()
        
        return notes
    
    def _next_degree(self) -> int:
        """Get next degree based on transition probabilities."""
        if self._current_degree not in self.transitions:
            return self._current_degree
        
        probs = self.transitions[self._current_degree]
        degrees = list(probs.keys())
        weights = list(probs.values())
        
        return random.choices(degrees, weights=weights)[0]
    
    @staticmethod
    def create_diatonic_transitions(scale_type: ScaleType) -> Dict[int, Dict[int, float]]:
        """
        Create standard diatonic transition matrix for a scale type.
        
        Tends to prefer stepwise motion over leaps.
        """
        # Step probability distribution by distance
        step_probs = {
            0: 0.35,  # same note
            1: 0.25,  # step up/down
            2: 0.20,  # skip
            3: 0.10,  # leap
            4: 0.07,  # big leap
            5: 0.03,  # octave
        }
        
        transitions = {}
        for degree in range(7):
            transitions[degree] = {}
            for next_deg in range(7):
                distance = abs(degree - next_deg)
                distance = min(distance, 6)  # cap at octave
                transitions[degree][next_deg] = step_probs.get(distance, 0.01)
            
            # Normalize
            total = sum(transitions[degree].values())
            for k in transitions[degree]:
                transitions[degree][k] /= total
        
        return transitions


class PatternEvolution:
    """
    Pattern that evolves over time - morphs density and complexity.
    
    Instead of a static pattern, this generates patterns that change
    over the duration of a clip (e.g., building energy, fading out).
    
    Usage:
        gen = PatternEvolution(
            start_pulses=2,  # Sparse
            end_pulses=8,    # Dense
            duration_beats=64,
            curve="exponential"
        )
        # Get kick pattern that builds energy
        timing = gen.generate_timing(track="kick")
    """
    
    CURVES = ["linear", "exponential", "logarithmic", "sigmoid"]
    
    def __init__(
        self,
        start_value: float,
        end_value: float,
        duration_beats: float = 64.0,
        curve: str = "linear"
    ):
        """
        Initialize PatternEvolution.
        
        Args:
            start_value: Starting parameter value (e.g., pulse count)
            end_value: Ending parameter value
            duration_beats: Total clip length in beats
            curve: Interpolation curve - "linear", "exponential", "logarithmic", "sigmoid"
        """
        self.start_value = start_value
        self.end_value = end_value
        self.duration_beats = duration_beats
        self.curve = curve
    
    def get_value_at(self, beat: float) -> float:
        """
        Get interpolated parameter value at a specific beat.
        
        Args:
            beat: Beat position (0.0 to duration_beats)
            
        Returns:
            Interpolated parameter value
        """
        t = beat / max(1, self.duration_beats)
        t = max(0.0, min(1.0, t))
        
        if self.curve == "exponential":
            t = t * t
        elif self.curve == "logarithmic":
            t = math.sqrt(t) if t > 0 else 0
        elif self.curve == "sigmoid":
            # Sigmoid curve - slow start, fast middle, slow end
            t = 1 / (1 + math.exp(-10 * (t - 0.5)))
        
        return self.start_value + (self.end_value - self.start_value) * t
    
    def generate_euclidean_evolution(
        self,
        steps: int = 16,
        base_rotation: int = 0,
        rotation_range: int = 8,
        duration: float = 0.25
    ) -> List[Tuple[float, float, int]]:
        """
        Generate Euclidean rhythm that evolves in density.
        
        Args:
            steps: Steps per bar
            base_rotation: Starting rotation
            rotation_range: How much rotation changes over duration
            duration: Note duration
            
        Returns:
            List of (start_time, duration, pulses) tuples for each bar
        """
        bars = int(self.duration_beats / 4)
        result = []
        
        for bar in range(bars):
            beat = bar * 4
            # Get pulses at this point in the evolution
            pulses = max(1, int(self.get_value_at(beat)))
            # Rotation evolves too
            rotation = (base_rotation + int(rotation_range * bar / bars)) % steps
            
            timing = generate_euclidean_pattern(steps, pulses, duration, rotation)
            for pos, dur in timing:
                if beat + pos < self.duration_beats:
                    result.append((beat + pos, dur, pulses))
        
        return result


# ============================================================================
# GROOVE VELOCITY GENERATOR
# ============================================================================

class GrooveGenerator:
    """
    Generate musical velocity patterns with microtiming and groove.
    
    Unlike random velocities, GrooveGenerator produces patterns that:
    - Have musical emphasis on downbeats
    - Include swing/swagger
    - Build dynamic trajectories over time
    """
    
    @staticmethod
    def basic_pattern(base_velocity: int = 100, variation: int = 10) -> List[int]:
        """Basic 8th note groove with emphasis on downbeats."""
        # Downbeats (0, 2, 4, 6) louder, offbeats (1, 3, 5, 7) softer
        pattern = []
        for i in range(8):
            if i % 2 == 0:
                vel = base_velocity + random.randint(-variation, variation)
            else:
                vel = base_velocity - 15 + random.randint(-variation // 2, variation // 2)
            pattern.append(max(20, min(127, vel)))
        return pattern
    
    @staticmethod
    def house_pattern(base_velocity: int = 105) -> List[int]:
        """Four-on-the-floor house groove - emphatic kick, light hats."""
        return [
            base_velocity + 5,   # 1
            base_velocity - 25,  # &
            base_velocity - 15,  # 2
            base_velocity - 30,  # &
            base_velocity + 3,   # 3
            base_velocity - 25,  # &
            base_velocity - 15,  # 4
            base_velocity - 35,  # &
        ]
    
    @staticmethod
    def dub_techno_pattern(base_velocity: int = 95) -> List[int]:
        """Authentic dub techno groove - driving kick, shuffled hats."""
        return [
            base_velocity,       # kick on 1
            base_velocity - 30,  # hat offbeat
            base_velocity - 20,  # hat
            base_velocity - 35,  # hat offbeat
            base_velocity - 5,   # kick
            base_velocity - 30,  # hat
            base_velocity - 25,  # snare
            base_velocity - 40,  # ghost hat
        ]
    
    @staticmethod
    def trajectory(
        pattern: List[int],
        length: int,
        start_vel: int = 80,
        end_vel: int = 115,
        ramp: str = "linear"
    ) -> List[int]:
        """
        Apply dynamic trajectory over multiple bars.
        
        Args:
            pattern: Single-bar velocity pattern
            length: Number of bars
            start_vel: Starting velocity
            end_vel: Ending velocity
            ramp: "linear", "exponential", "logarithmic"
        """
        velocities = []
        for bar in range(length):
            t = bar / max(1, length - 1)
            if ramp == "linear":
                scale = t
            elif ramp == "exponential":
                scale = t * t
            elif ramp == "logarithmic":
                scale = math.sqrt(t) if t > 0 else 0
            else:
                scale = t
            
            bar_vel = int(start_vel + (end_vel - start_vel) * scale)
            for vel in pattern:
                velocities.append(vel + bar_vel - 100)  # Normalize to pattern
        
        return [max(20, min(127, v)) for v in velocities]


# ============================================================================
# MIDI CLIP GENERATOR
# ============================================================================

@dataclass
class MIDINote:
    """Single MIDI note event."""
    pitch: int
    start_time: float
    duration: float
    velocity: int
    mute: bool = False

class ClipGenerator:
    """
    Generate MIDI clips with musical intelligence.
    
    Usage:
        gen = ClipGenerator(tempo=126)
        gen.add_kick(euclidean_rhythm(16, 4))
        gen.add_hats(euclidean_rhythm(16, 8), velocity_groove=GROOVE_PATTERNS["dub_techno"])
        gen.add_bass("Fm", ["i", "VII", "VI", "V"])
        notes = gen.generate()
    """
    
    def __init__(self, tempo: float = 126.0, length_beats: float = 64.0):
        self.tempo = tempo
        self.length_beats = length_beats
        self.notes: List[MIDINote] = []
        self.scale = Scale(60, ScaleType.MINOR)  # Default C minor
        self.key = 60  # MIDI root
        
    def set_key(self, key: str):
        """Set key from string (e.g., 'Fm', 'Cm', 'Am')."""
        key_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        root_str = key[0].upper()
        self.key = 12 * 4 + key_map.get(root_str, 0)  # Octave 4
        if 'm' in key.lower() or key.islower():
            self.scale = Scale(self.key, ScaleType.MINOR)
        else:
            self.scale = Scale(self.key, ScaleType.MAJOR)
    
    def add_kick(
        self,
        timing: List[float],
        velocity: int = 120,
        velocity_pattern: Optional[List[int]] = None
    ) -> 'ClipGenerator':
        """Add kick drum hits. timing = beat positions (0.0, 4.0, etc.)."""
        for i, beat in enumerate(timing):
            vel = velocity
            if velocity_pattern and i < len(velocity_pattern):
                vel = velocity_pattern[i]
            if beat < self.length_beats:
                self.notes.append(MIDINote(36, beat, 0.25, vel))
        return self
    
    def add_snare(
        self,
        timing: List[float],
        velocity: int = 100,
        pitch: int = 40
    ) -> 'ClipGenerator':
        """Add snare hits."""
        for beat in timing:
            if beat < self.length_beats:
                self.notes.append(MIDINote(pitch, beat, 0.25, velocity))
        return self
    
    def add_hats(
        self,
        timing: List[float],
        velocity: int = 75,
        pitch: int = 42,
        open_hat: bool = False
    ) -> 'ClipGenerator':
        """Add hi-hat hits. Timing uses 0.25 for 16ths."""
        for i, pos in enumerate(timing):
            if pos >= self.length_beats:
                break
            vel = velocity
            if isinstance(velocity, list) and i < len(velocity):
                vel = velocity[i]
            note_pitch = pitch + 1 if (open_hat and i % 4 == 2) else pitch
            self.notes.append(MIDINote(note_pitch, pos, 0.125, vel))
        return self
    
    def add_clap(
        self,
        timing: List[float],
        velocity: int = 100,
        pitch: int = 39
    ) -> 'ClipGenerator':
        """Add clap/snare hits."""
        for beat in timing:
            if beat < self.length_beats:
                self.notes.append(MIDINote(pitch, beat, 0.2, velocity))
        return self
    
    def add_bass(
        self,
        root_note: int,
        chord_qualities: List[str],
        beats_per_chord: int = 16,
        velocity: int = 105
    ) -> 'ClipGenerator':
        """Add bass line following chord progression."""
        for i, quality in enumerate(chord_qualities):
            if i * beats_per_chord >= self.length_beats:
                break
            beat_pos = i * beats_per_chord
            # Root note of chord
            root = self.scale.degree_to_midi(["i", "ii", "iii", "iv", "v", "vi", "vii"].index(quality.lower().replace("7", "").replace("maj", "").replace("min", "").replace("dom", "").replace("dim", "").replace("aug", "")[0]))
            # Simplified: just use root
            root = self.key + [0, 2, 3, 5, 7, 8, 10][i % 7] if False else self.key
            self.notes.append(MIDINote(root, beat_pos, beats_per_chord * 0.9, velocity))
        return self
    
    def add_chord(
        self,
        chord: Chord,
        start_beat: float,
        duration: float,
        velocity: int = 90
    ) -> 'ClipGenerator':
        """Add a chord (from ChordProgression)."""
        for note in chord.notes:
            if start_beat < self.length_beats:
                self.notes.append(MIDINote(note, start_beat, duration, velocity))
        return self
    
    def add_chord_progression(
        self,
        chords: List[Chord],
        beats_per_chord: float = 16,
        velocity: int = 90,
        octave: int = 0
    ) -> 'ClipGenerator':
        """Add full chord progression."""
        for i, chord in enumerate(chords):
            start = i * beats_per_chord
            if start >= self.length_beats:
                break
            for note in chord.notes:
                midi_note = note + octave * 12
                if midi_note < 127:
                    self.notes.append(MIDINote(midi_note, start, beats_per_chord * 0.95, velocity))
        return self
    
    def add_melody(
        self,
        scale_degrees: List[int],
        durations: Optional[List[float]] = None,
        velocity: int = 85,
        octave: int = 1,
        groove: str = "chill"
    ) -> 'ClipGenerator':
        """Add melodic phrase from scale degrees."""
        if durations is None:
            durations = [2.0] * len(scale_degrees)
        
        pos = 0.0
        for i, degree in enumerate(scale_degrees):
            if pos >= self.length_beats:
                break
            dur = durations[i] if i < len(durations) else 2.0
            pitch = self.scale.degree_to_midi(degree, octave)
            if 0 <= pitch <= 127:
                vel = velocity
                if groove == "chill":
                    vel = velocity - 10 + (i % 3) * 5
                elif groove == "driving":
                    vel = velocity + (i % 4) * 3
                self.notes.append(MIDINote(pitch, pos, dur, vel))
                pos += dur
        return self
    
    def add_percussion(
        self,
        pitch: int,
        timing: List[float],
        velocity: int = 80
    ) -> 'ClipGenerator':
        """Add percussion hits."""
        for beat in timing:
            if beat < self.length_beats:
                self.notes.append(MIDINote(pitch, beat, 0.15, velocity))
        return self
    
    def add_markov_melody(
        self,
        length: int = 32,
        velocity: int = 85,
        octave: int = 1,
        start_degree: int = 0,
        scale_type: Optional[ScaleType] = None
    ) -> 'ClipGenerator':
        """
        Add melody generated using Markov chain for musically coherent motion.
        
        Args:
            length: Number of notes to generate
            velocity: Base velocity
            octave: Octave offset for MIDI notes
            start_degree: Starting scale degree
            scale_type: ScaleType to use for diatonic transitions (uses self.scale if None)
        """
        # Use provided scale or default to self.scale
        scale = self.scale
        if scale_type:
            scale = Scale(self.key, scale_type)
        
        # Get or create transition matrix
        if scale_type:
            transitions = PMarkov.create_diatonic_transitions(scale_type)
        else:
            # Create simple transitions based on current scale
            transitions = PMarkov.create_diatonic_transitions(self.scale.scale_type)
        
        markov = PMarkov(transitions, scale)
        melody = markov.generate(length, start_degree)
        
        # Convert to notes with rhythmic spacing
        pos = 0.0
        for i, midi_note in enumerate(melody):
            if pos >= self.length_beats:
                break
            # Alternate between half-beat and whole-beat durations for variety
            dur = 1.5 if i % 3 == 0 else 1.0
            vel = velocity + (i % 5) * 3 - 10
            self.notes.append(MIDINote(midi_note, pos, dur, max(30, min(127, vel))))
            pos += dur
        
        return self
    
    def add_evolving_pattern(
        self,
        pattern_type: str,
        start_value: float,
        end_value: float,
        pitch: int = 36,
        velocity: int = 100,
        curve: str = "exponential"
    ) -> 'ClipGenerator':
        """
        Add pattern that evolves in density/complexity over time.
        
        Args:
            pattern_type: "euclidean" or "pulse"
            start_value: Starting value (e.g., pulses for euclidean, notes per bar for pulse)
            end_value: Ending value
            pitch: MIDI note number
            velocity: Base velocity
            curve: "linear", "exponential", "logarithmic", "sigmoid"
        """
        evolution = PatternEvolution(start_value, end_value, self.length_beats, curve)
        bars = int(self.length_beats / 4)
        
        for bar in range(bars):
            beat = bar * 4
            pulses = max(1, int(evolution.get_value_at(beat)))
            
            if pattern_type == "euclidean":
                # Generate euclidean pattern for this bar
                timing = generate_euclidean_pattern(16, pulses, 0.25, bar % 16)
                for pos, dur in timing:
                    if beat + pos < self.length_beats:
                        self.notes.append(MIDINote(pitch, beat + pos, dur * 0.9, velocity))
            else:
                # Simple evenly-spaced pulses that increase in density
                interval = 4.0 / pulses
                for p in range(pulses):
                    pos = beat + p * interval
                    if pos < self.length_beats:
                        self.notes.append(MIDINote(pitch, pos, 0.2, velocity))
        
        return self
    
    def generate(self) -> List[Dict[str, Any]]:
        """Generate Ableton-compatible note list."""
        return [
            {
                "pitch": note.pitch,
                "start_time": note.start_time,
                "duration": note.duration,
                "velocity": note.velocity,
                "mute": note.mute
            }
            for note in sorted(self.notes, key=lambda n: (n.start_time, n.pitch))
        ]


# ============================================================================
# DUB TECHNO PRESETS
# ============================================================================

DUB_TECHNO_KICK_PATTERN = euclidean_rhythm(16, 4, rotation=0)  # Four on floor
DUB_TECHNO_HAT_PATTERN = euclidean_rhythm(16, 11, rotation=2)  # Shuffled 16ths
DUB_TECHNO_SNARE_PATTERN = [4.0, 12.0]  # Beats 3 and 11 (1-indexed)

GROOVE_PATTERNS = {
    "basic": GrooveGenerator.basic_pattern,
    "house": GrooveGenerator.house_pattern,
    "dub_techno": GrooveGenerator.dub_techno_pattern,
}


# ============================================================================
# PIPELINE ORCHESTRATOR
# ============================================================================

class GenerationPipeline:
    """
    High-level pipeline for generating complete track patterns.
    
    Orchestrates multiple ClipGenerators with consistent timing and groove.
    
    Usage:
        pipeline = GenerationPipeline(tempo=126, key="Fm")
        pipeline.add_track("kick", euclidean_pattern(16, 4))
        pipeline.add_track("bass", chord_progression)
        pipeline.add_track("melody", scale_degrees=[0, 2, 4, 5])
        tracks = pipeline.generate()
        # tracks = {"kick": [...], "bass": [...], ...}
    """
    
    def __init__(self, tempo: float = 126.0, length_beats: float = 64.0, key: str = "Cm"):
        self.tempo = tempo
        self.length_beats = length_beats
        self.key = key
        self.tracks: Dict[str, ClipGenerator] = {}
        self.defaults: Dict[str, Any] = {
            "kick": {"pitch": 36, "velocity": 120},
            "snare": {"pitch": 40, "velocity": 100},
            "hat": {"pitch": 42, "velocity": 75},
            "clap": {"pitch": 39, "velocity": 100},
            "perc": {"pitch": 37, "velocity": 80},
        }
    
    def add_track(self, name: str, generator: ClipGenerator) -> None:
        """Add a track generator."""
        self.tracks[name] = generator
    
    def generate_track(self, name: str, **kwargs) -> ClipGenerator:
        """Generate a new track with specified parameters."""
        gen = ClipGenerator(self.tempo, self.length_beats)
        gen.set_key(self.key)
        self.tracks[name] = gen
        return gen
    
    def generate(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all tracks and return as dict of Ableton notes."""
        return {name: gen.generate() for name, gen in self.tracks.items()}
    
    @staticmethod
    def dub_techno_session(
        tempo: float = 126.0,
        key: str = "Fm",
        length_bars: int = 16,
        scene: str = "drop"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate complete dub techno session data.
        
        Args:
            tempo: BPM
            key: Key signature (e.g., "Fm")
            length_bars: Number of bars (16 bars = 64 beats)
            scene: Scene type ("intro", "drop", "break", "build", "atmosphere", "outro")
            
        Returns:
            Dict with tracks: kick, snare, hat, clap, bass, chords, melody, perc
        """
        length_beats = length_bars * 4.0
        pipeline = GenerationPipeline(tempo, length_beats, key)
        
        # Key components - key is set via constructor, no set_key needed
        scale = Scale(60 if key == "Cm" else 53, ScaleType.MINOR)  # Default to Cm or Fm
        
        # Different scenes have different intensity
        if scene == "intro":
            kick_vel, hat_vel, bass_vel = 85, 50, 70
            kick_pulses, hat_pulses = 2, 4
            use_evolution = False
        elif scene == "break":
            kick_vel, hat_vel, bass_vel = 70, 40, 60
            kick_pulses, hat_pulses = 1, 3
            use_evolution = False
        elif scene == "build":
            kick_vel, hat_vel, bass_vel = 110, 95, 110
            kick_pulses, hat_pulses = 5, 12
            use_evolution = True  # Use evolving pattern for rising energy
        elif scene == "atmosphere":
            kick_vel, hat_vel, bass_vel = 50, 30, 50
            kick_pulses, hat_pulses = 1, 2
            use_evolution = False
        elif scene == "outro":
            kick_vel, hat_vel, bass_vel = 60, 35, 55
            kick_pulses, hat_pulses = 1, 3
            use_evolution = True  # Fade out pattern
        else:  # drop
            kick_vel, hat_vel, bass_vel = 120, 85, 110
            kick_pulses, hat_pulses = 4, 11
            use_evolution = False
        
        # Kick - Euclidean rhythm with optional evolution
        kick_gen = ClipGenerator(tempo, length_beats)
        kick_gen.scale = scale
        
        if use_evolution:
            # Build/Outro: Use evolving pattern for rising/falling energy
            if scene == "build":
                kick_gen.add_evolving_pattern("euclidean", 2, 8, 36, kick_vel, "exponential")
            else:  # outro
                kick_gen.add_evolving_pattern("euclidean", 4, 1, 36, kick_vel - 20, "logarithmic")
        else:
            kick_timing = euclidean_rhythm(16, kick_pulses, rotation=0)
            for bar in range(length_bars):
                for pos in kick_timing:
                    beat = bar * 4 + pos
                    if beat < length_beats:
                        kick_gen.notes.append(MIDINote(36, beat, 0.3, kick_vel))
        
        pipeline.tracks["kick"] = kick_gen
        
        # Hi-hats - shuffled 16ths
        hat_gen = ClipGenerator(tempo, length_beats)
        
        if use_evolution and scene == "build":
            # Build: Hats increase in density with evolving pattern
            hat_gen.add_evolving_pattern("euclidean", 4, 14, 42, hat_vel, "exponential")
        elif use_evolution and scene == "outro":
            # Outro: Hats decrease
            hat_gen.add_evolving_pattern("euclidean", 8, 2, 42, max(30, hat_vel - 20), "logarithmic")
        else:
            hat_timing = euclidean_rhythm(16, hat_pulses, rotation=2)
            velocity_pattern = GrooveGenerator.basic_pattern(hat_vel, 8)
            for bar in range(length_bars):
                for i, pos in enumerate(hat_timing):
                    beat = bar * 4 + pos
                    if beat < length_beats:
                        vel = velocity_pattern[i % len(velocity_pattern)]
                        hat_gen.notes.append(MIDINote(42, beat, 0.125, vel))
        pipeline.tracks["hat"] = hat_gen
        
        # Snare on 3 (beat 4 in quarter note grid)
        snare_gen = ClipGenerator(tempo, length_beats)
        for bar in range(length_bars):
            snare_gen.notes.append(MIDINote(40, bar * 4 + 2, 0.25, 100))
        pipeline.tracks["snare"] = snare_gen
        
        # Clap
        clap_gen = ClipGenerator(tempo, length_beats)
        for bar in range(length_bars):
            clap_gen.notes.append(MIDINote(39, bar * 4 + 2, 0.2, 95))
        pipeline.tracks["clap"] = clap_gen
        
        # Bass - chord progression
        bass_gen = ClipGenerator(tempo, length_beats)
        chords = ChordProgression.from_preset(scale.root, "i-VII-VI-V")
        bass_gen.add_chord_progression(chords, beats_per_chord=length_beats/4, velocity=bass_vel, octave=-1)
        pipeline.tracks["bass"] = bass_gen
        
        # Chords - higher octave
        chord_gen = ClipGenerator(tempo, length_beats)
        chord_gen.add_chord_progression(chords, beats_per_chord=length_beats/4, velocity=80, octave=1)
        pipeline.tracks["chords"] = chord_gen
        
        # Melody - textural pad with Markov chain for musical coherence
        melody_gen = ClipGenerator(tempo, length_beats)
        melody_gen.scale = scale
        # Use Markov melody for build/outro scenes (more organic variation)
        if scene in ("build", "outro"):
            melody_gen.add_markov_melody(
                length=int(length_beats / 2),
                velocity=70,
                octave=1,
                start_degree=0,
                scale_type=ScaleType.DORIAN
            )
        else:
            melody_degrees = [0, 4, 5, 4, 3, 4, 5, 7]  # Dorian movement
            for bar in range(length_bars):
                for i, deg in enumerate(melody_degrees):
                    pos = bar * 4 + i * 1.5
                    if pos < length_beats:
                        pitch = scale.degree_to_midi(deg, octave_offset=1)
                        melody_gen.notes.append(MIDINote(pitch, pos, 1.0, 70 + (i % 3) * 5))
        pipeline.tracks["melody"] = melody_gen
        
        # Percussion - shakers
        perc_gen = ClipGenerator(tempo, length_beats)
        perc_timing = euclidean_rhythm(16, 6, rotation=4)
        for bar in range(length_bars):
            for pos in perc_timing:
                beat = bar * 4 + pos
                if beat < length_beats:
                    perc_gen.notes.append(MIDINote(37, beat, 0.1, 70))
        pipeline.tracks["perc"] = perc_gen
        
        return pipeline.generate()