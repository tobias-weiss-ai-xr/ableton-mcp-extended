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


class PMarkov2:
    """
    2nd-order Markov chain for melodies.
    
    Remembers the last 2 notes instead of 1, producing more coherent
    musical phrases with better contour and structure.
    
    Usage:
        transitions = {
            (0, 0): {0: 0.5, 1: 0.3, 2: 0.2},   # After two roots, likely stay
            (0, 1): {0: 0.3, 1: 0.2, 2: 0.5},   # After root-step, likely skip up
            ...
        }
        markov = PMarkov2(transitions, scale)
        melody = markov.generate(length=16)
    """
    
    def __init__(
        self,
        transitions: Dict[Tuple[int, int], Dict[int, float]],
        scale: Optional[Scale] = None
    ):
        """
        Initialize 2nd-order Markov generator.
        
        Args:
            transitions: Dict mapping (prev, curr) -> {next: probability}
            scale: Scale object for MIDI conversion
        """
        self.transitions = transitions
        self.scale = scale
        self._history: List[int] = [0, 0]  # Last two degrees
    
    def generate(
        self,
        length: int = 16,
        start_degrees: Optional[List[int]] = None
    ) -> List[int]:
        """
        Generate melodic sequence with 2nd-order transitions.
        
        Args:
            length: Number of notes to generate
            start_degrees: Starting pair of scale degrees [prev, curr]
            
        Returns:
            List of MIDI note numbers (if scale provided) or scale degrees
        """
        if start_degrees and len(start_degrees) >= 2:
            self._history = list(start_degrees[:2])
        else:
            self._history = [0, 0]
        
        notes = []
        for _ in range(length):
            prev, curr = self._history[-2], self._history[-1]
            
            # Add current note
            if self.scale:
                midi_note = self.scale.degree_to_midi(curr, octave_offset=1)
                notes.append(midi_note)
            else:
                notes.append(curr)
            
            # Transition to next note
            next_deg = self._next_degree(prev, curr)
            self._history.append(next_deg)
            if len(self._history) > 2:
                self._history.pop(0)
        
        return notes
    
    def _next_degree(self, prev: int, curr: int) -> int:
        """Get next degree based on 2nd-order transition probabilities."""
        key = (prev, curr)
        if key not in self.transitions:
            # Fallback to simple step-based transition
            return max(0, min(6, curr + random.choice([-1, 0, 1])))
        
        probs = self.transitions[key]
        degrees = list(probs.keys())
        weights = list(probs.values())
        return random.choices(degrees, weights=weights)[0]
    
    @staticmethod
    def create_diatonic_transitions(scale_type: ScaleType) -> Dict[Tuple[int, int], Dict[int, float]]:
        """
        Create 2nd-order diatonic transition matrix.
        
        Generates more structured phrases than 1st-order by encoding
        common melodic patterns (stepwise motion, arpeggiation, etc.).
        """
        # Base step probabilities
        step_probs = {0: 0.30, 1: 0.25, 2: 0.20, 3: 0.12, 4: 0.08, 5: 0.05}
        
        transitions = {}
        for prev in range(7):
            for curr in range(7):
                key = (prev, curr)
                transitions[key] = {}
                
                # Direction persistence: continue same direction as prev->curr
                direction = curr - prev
                for next_deg in range(7):
                    new_direction = next_deg - curr
                    prob = step_probs.get(abs(new_direction), 0.01)
                    
                    # Slight preference for continuing same direction
                    if direction * new_direction > 0:  # Same direction
                        prob *= 1.5
                    elif new_direction == 0:  # Same note
                        prob *= 1.2
                    elif direction != 0 and new_direction == -direction:  # Reversal
                        prob *= 0.8
                    
                    transitions[key][next_deg] = prob
                
                # Normalize
                total = sum(transitions[key].values())
                for k in transitions[key]:
                    transitions[key][k] /= total
        
        return transitions
    
    @staticmethod
    def create_from_1st_order(
        first_order: Dict[int, Dict[int, float]]
    ) -> Dict[Tuple[int, int], Dict[int, float]]:
        """
        Create 2nd-order transitions from existing 1st-order matrix.
        
        Useful for upgrading existing Markov models.
        """
        transitions = {}
        for prev in range(7):
            for curr in range(7):
                key = (prev, curr)
                # Use 1st-order transitions from 'curr' as base
                if curr in first_order:
                    transitions[key] = dict(first_order[curr])
                else:
                    transitions[key] = {d: 1.0/7 for d in range(7)}
        return transitions


class RhythmMarkov:
    """
    Markov chain for generating rhythmic timing patterns.
    
    Transitions between note durations (16th, 8th, quarter, half, whole)
    to create natural-feeling rhythmic phrases.
    
    Usage:
        rm = RhythmMarkov()
        timings = rm.generate(16, 64.0)
        # Returns list of (start_time, duration) tuples spanning 64 beats
    """
    
    # Standard duration values in beats
    DURATIONS = {
        "16th": 0.25,
        "8th": 0.5,
        "8th_triplet": 0.333,
        "quarter": 1.0,
        "half": 2.0,
        "whole": 4.0,
    }
    
    # Genre-specific rhythm profiles
    PROFILES = {
        "dub_techno": {
            ("16th", "16th"): 0.4,
            ("16th", "8th"): 0.3,
            ("16th", "quarter"): 0.2,
            ("16th", "half"): 0.1,
            ("8th", "8th"): 0.3,
            ("8th", "16th"): 0.3,
            ("8th", "quarter"): 0.25,
            ("8th", "half"): 0.15,
            ("quarter", "quarter"): 0.3,
            ("quarter", "8th"): 0.4,
            ("quarter", "half"): 0.3,
            ("half", "quarter"): 0.5,
            ("half", "whole"): 0.5,
            ("whole", "whole"): 1.0,
        },
        "house": {
            ("16th", "16th"): 0.5,
            ("16th", "8th"): 0.3,
            ("16th", "quarter"): 0.2,
            ("8th", "8th"): 0.4,
            ("8th", "16th"): 0.4,
            ("8th", "quarter"): 0.2,
            ("quarter", "quarter"): 0.4,
            ("quarter", "8th"): 0.4,
            ("quarter", "half"): 0.2,
            ("half", "quarter"): 0.7,
            ("half", "whole"): 0.3,
        },
        "techno": {
            ("16th", "16th"): 0.6,
            ("16th", "8th"): 0.3,
            ("16th", "quarter"): 0.1,
            ("8th", "8th"): 0.5,
            ("8th", "16th"): 0.4,
            ("8th", "quarter"): 0.1,
            ("quarter", "quarter"): 0.5,
            ("quarter", "8th"): 0.3,
            ("quarter", "half"): 0.2,
        },
    }
    
    def __init__(self, profile: str = "dub_techno"):
        """Initialize rhythm Markov with genre profile."""
        self.profile = self.PROFILES.get(profile, self.PROFILES["dub_techno"])
        self._last_duration = "quarter"
    
    def generate(
        self,
        num_events: int = 16,
        length_beats: float = 64.0
    ) -> List[Tuple[float, float]]:
        """
        Generate rhythmic timing pattern.
        
        Args:
            num_events: Number of note events to generate
            length_beats: Maximum clip length
            
        Returns:
            List of (start_time, duration) tuples
        """
        result = []
        pos = 0.0
        duration_names = list(self.DURATIONS.keys())
        
        for _ in range(num_events * 2):  # Safety limit
            if pos >= length_beats or len(result) >= num_events:
                break
            
            # Choose next duration using transition probabilities
            candidates = []
            weights = []
            for dur_name, prob in self.profile.items():
                if dur_name[0] == self._last_duration:
                    candidates.append(dur_name[1])
                    weights.append(prob)
            
            if not candidates:
                chosen = "quarter"
            else:
                chosen = random.choices(candidates, weights=weights, k=1)[0]
            
            duration = self.DURATIONS[chosen]
            
            # Don't exceed clip length
            if pos + duration <= length_beats:
                result.append((pos, duration))
                pos += duration
                self._last_duration = chosen
            else:
                break
        
        return result


class ClipMutator:
    """
    Generate variations from existing clips.
    
    Takes existing MIDI notes and applies musical transformations
    to create related but distinct new patterns.
    
    Mutation operations:
    - transpose: Shift notes up/down
    - density: Add/remove notes
    - stretch: Time compress/expand
    - velocity: Scale velocities
    - groove: Apply swing/microtiming
    - displace: Rhythmic shift
    """
    
    @staticmethod
    def transpose(
        notes: List[Dict[str, Any]],
        semitones: int = 0,
        per_note_range: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Transpose all or some notes.
        
        Args:
            notes: Source notes
            semitones: Transposition amount (-24 to +24)
            per_note_range: Random shift within ±semitones per note
            
        Returns:
            Transposed notes
        """
        result = []
        for note in notes:
            n = dict(note)
            if per_note_range:
                shift = random.randint(-abs(semitones), abs(semitones))
            else:
                shift = semitones
            n["pitch"] = max(0, min(127, n["pitch"] + shift))
            result.append(n)
        return result
    
    @staticmethod
    def density(
        notes: List[Dict[str, Any]],
        factor: float = 1.0,
        length_beats: float = 64.0
    ) -> List[Dict[str, Any]]:
        """
        Change note density by adding or removing notes.
        
        Args:
            notes: Source notes
            factor: Density factor (>1 = more notes, <1 = fewer)
            length_beats: Clip length
            
        Returns:
            Modified notes
        """
        result = list(notes)
        
        if factor > 1.0:
            # Add notes by splitting existing ones
            added = []
            for note in notes:
                if random.random() < (factor - 1.0):
                    # Split this note into two
                    mid = note["start_time"] + note["duration"] * 0.5
                    if mid < length_beats:
                        added.append({
                            "pitch": note["pitch"],
                            "start_time": mid,
                            "duration": note["duration"] * 0.5,
                            "velocity": max(20, note["velocity"] - 10),
                            "mute": False,
                        })
            result.extend(added)
        
        elif factor < 1.0:
            # Remove notes randomly
            keep_count = max(1, int(len(result) * factor))
            result = random.sample(result, min(keep_count, len(result)))
        
        return sorted(result, key=lambda n: (n["start_time"], n["pitch"]))
    
    @staticmethod
    def stretch(
        notes: List[Dict[str, Any]],
        factor: float = 1.0,
        length_beats: float = 64.0
    ) -> List[Dict[str, Any]]:
        """
        Time stretch/compress notes.
        
        Args:
            notes: Source notes
            factor: Stretch factor (>1 = slower, <1 = faster)
            length_beats: Clip length
            
        Returns:
            Stretched notes
        """
        result = []
        for note in notes:
            n = dict(note)
            n["start_time"] = min(length_beats - 0.01, n["start_time"] * factor)
            n["duration"] = n["duration"] * factor
            if n["start_time"] + n["duration"] <= length_beats:
                result.append(n)
        return result
    
    @staticmethod
    def velocity(
        notes: List[Dict[str, Any]],
        scale: float = 1.0,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Scale and offset velocities with clamping.
        
        Args:
            notes: Source notes
            scale: Velocity multiplier
            offset: Velocity offset
            
        Returns:
            Modified notes
        """
        result = []
        for note in notes:
            n = dict(note)
            new_vel = int(n["velocity"] * scale + offset)
            n["velocity"] = max(10, min(127, new_vel))
            result.append(n)
        return result
    
    @staticmethod
    def groove(
        notes: List[Dict[str, Any]],
        swing_amount: float = 0.3,
        microtiming: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Apply swing and microtiming displacement.
        
        Args:
            notes: Source notes
            swing_amount: Swing intensity (0.0-0.5), shifts 8th note offbeats
            microtiming: Random timing displacement (0.0-0.1)
            
        Returns:
            Grooved notes
        """
        result = []
        for note in notes:
            n = dict(note)
            beat = n["start_time"]
            beat_in_bar = beat % 4
            
            # Swing: delay offbeat 8th notes
            if 0.4 < beat_in_bar % 1 < 0.6:
                n["start_time"] += swing_amount * 0.5
            
            # Microtiming: random displacement
            n["start_time"] += random.uniform(-microtiming, microtiming)
            n["start_time"] = max(0, n["start_time"])
            
            # Velocity variation
            n["velocity"] = max(10, min(127, n["velocity"] + random.randint(-5, 5)))
            
            result.append(n)
        return result
    
    @staticmethod
    def displace(
        notes: List[Dict[str, Any]],
        shift_beats: float = 0.0,
        length_beats: float = 64.0
    ) -> List[Dict[str, Any]]:
        """
        Shift notes rhythmically (offset or reverse).
        
        Args:
            notes: Source notes
            shift_beats: Positive=forward, negative=backward
            length_beats: Clip length
            
        Returns:
            Displaced notes
        """
        result = []
        for note in notes:
            n = dict(note)
            new_time = n["start_time"] + shift_beats
            # Wrap around the clip
            if new_time < 0:
                new_time += length_beats
            elif new_time >= length_beats:
                new_time -= length_beats
            n["start_time"] = new_time
            result.append(n)
        return sorted(result, key=lambda n: (n["start_time"], n["pitch"]))
    
    @staticmethod
    def mutate(
        notes: List[Dict[str, Any]],
        operations: Optional[List[str]] = None,
        intensity: float = 0.5,
        length_beats: float = 64.0
    ) -> List[Dict[str, Any]]:
        """
        Apply random combination of mutations.
        
        Args:
            notes: Source notes
            operations: Operations to use (default=all)
            intensity: Mutation intensity (0.0-1.0)
            length_beats: Clip length
            
        Returns:
            Mutated notes
        """
        if not notes:
            return []
        
        if operations is None:
            operations = ["transpose", "density", "stretch", "velocity", "groove", "displace"]
        
        result = list(notes)
        
        for op in operations:
            if not random.random() < 0.7:  # 70% chance per operation
                continue
                
            if op == "transpose":
                semitones = random.randint(-3, 3) * int(intensity * 2 + 1)
                result = ClipMutator.transpose(result, semitones)
            elif op == "density":
                factor = 1.0 + random.uniform(-0.5, 0.5) * intensity
                result = ClipMutator.density(result, factor, length_beats)
            elif op == "stretch":
                factor = 1.0 + random.uniform(-0.3, 0.3) * intensity
                result = ClipMutator.stretch(result, factor, length_beats)
            elif op == "velocity":
                scale = 1.0 + random.uniform(-0.3, 0.3) * intensity
                offset = random.randint(-15, 15) * int(intensity)
                result = ClipMutator.velocity(result, scale, offset)
            elif op == "groove":
                swing = 0.1 + 0.3 * intensity
                micro = 0.02 + 0.06 * intensity
                result = ClipMutator.groove(result, swing, micro)
            elif op == "displace":
                shift = random.uniform(-2, 2) * intensity
                result = ClipMutator.displace(result, shift, length_beats)
        
        return result


class InstrumentDefaults:
    """
    Instrument-aware generation defaults.
    
    Provides appropriate MIDI ranges, pattern types, and velocities
    for different instrument categories.
    """
    
    INSTRUMENTS = {
        "kick": {
            "pitch": 36,
            "range": (24, 48),
            "velocity_range": (100, 127),
            "pattern_type": "euclidean_kick",
            "groove": "basic",
            "description": "Kick drum",
        },
        "snare": {
            "pitch": 40,
            "range": (37, 42),
            "velocity_range": (80, 115),
            "pattern_type": "euclidean_snare",
            "groove": "basic",
            "description": "Snare drum",
        },
        "hihat": {
            "pitch": 42,
            "range": (42, 46),
            "velocity_range": (40, 95),
            "pattern_type": "euclidean_hat",
            "groove": "dub_techno",
            "description": "Hi-hat",
        },
        "clap": {
            "pitch": 39,
            "range": (39, 42),
            "velocity_range": (80, 115),
            "pattern_type": "euclidean_clap",
            "groove": "basic",
            "description": "Clap/snare",
        },
        "perc": {
            "pitch": 37,
            "range": (35, 60),
            "velocity_range": (50, 100),
            "pattern_type": "euclidean_perc",
            "groove": "basic",
            "description": "Percussion",
        },
        "bass": {
            "pitch": 36,
            "range": (24, 60),
            "velocity_range": (80, 120),
            "pattern_type": "arpeggiated",
            "groove": "dub_techno",
            "scale_type": ScaleType.MINOR,
            "description": "Bass synth",
        },
        "chord": {
            "pitch": 60,
            "range": (48, 84),
            "velocity_range": (60, 100),
            "pattern_type": "sustained",
            "groove": "basic",
            "scale_type": ScaleType.MINOR,
            "description": "Chord/pad",
        },
        "pad": {
            "pitch": 72,
            "range": (60, 96),
            "velocity_range": (50, 90),
            "pattern_type": "sustained",
            "groove": "basic",
            "scale_type": ScaleType.DORIAN,
            "description": "Atmospheric pad",
        },
        "lead": {
            "pitch": 72,
            "range": (60, 96),
            "velocity_range": (70, 110),
            "pattern_type": "melodic",
            "groove": "basic",
            "scale_type": ScaleType.DORIAN,
            "description": "Lead synth",
        },
        "fx": {
            "pitch": 60,
            "range": (24, 108),
            "velocity_range": (40, 100),
            "pattern_type": "random",
            "groove": "basic",
            "description": "FX/texture",
        },
    }
    
    @classmethod
    def get(cls, name: str) -> Dict[str, Any]:
        """Get defaults for an instrument by name."""
        return cls.INSTRUMENTS.get(name, cls.INSTRUMENTS["kick"])
    
    @classmethod
    def suggest_pitch(cls, name: str, octave: int = 0) -> int:
        """Suggest MIDI pitch for instrument."""
        defaults = cls.get(name)
        pitch = defaults.get("pitch", 60)
        if defaults.get("range"):
            low, high = defaults["range"]
            pitch = max(low, min(high, pitch + octave * 12))
        return pitch
    
    @classmethod
    def suggest_velocity(cls, name: str, intensity: float = 0.5) -> int:
        """Suggest velocity based on intensity (0.0-1.0)."""
        defaults = cls.get(name)
        v_range = defaults.get("velocity_range", (60, 100))
        return int(v_range[0] + (v_range[1] - v_range[0]) * intensity)
    
    @classmethod
    def suggest_scale(cls, name: str) -> Optional[ScaleType]:
        """Suggest scale type for instrument."""
        defaults = cls.get(name)
        return defaults.get("scale_type")
    
    @classmethod
    def list_instruments(cls) -> List[str]:
        """List all available instrument names."""
        return sorted(cls.INSTRUMENTS.keys())


class ArrangementGenerator:
    """
    Generate structural scene arrangements.
    
    Plans a complete set progression with energy curves, transition types,
    and scene-specific generation parameters.
    
    Usage:
        arr = ArrangementGenerator(126, "Fm")
        scene_plan = arr.generate_arrangement("dub_techno")
        # Returns list of scene descriptors with timing and intensity
    """
    
    # Arrangement templates
    ARRANGEMENTS = {
        "dub_techno": {
            "scenes": [
                {"type": "intro", "bars": 16, "energy": 2, "description": "Sparse intro pads"},
                {"type": "drop", "bars": 32, "energy": 7, "description": "Full drop with bass"},
                {"type": "break", "bars": 16, "energy": 3, "description": "Minimal breakdown"},
                {"type": "build", "bars": 16, "energy": 5, "description": "Rising tension"},
                {"type": "drop", "bars": 32, "energy": 9, "description": "Maximum drop"},
                {"type": "atmosphere", "bars": 16, "energy": 2, "description": "Atmospheric breather"},
                {"type": "rhythm_switch", "bars": 16, "energy": 6, "description": "Groove change"},
                {"type": "outro", "bars": 16, "energy": 1, "description": "Fade out"},
            ],
            "tempo_range": (120, 130),
            "key_compatible": True,
        },
        "techno": {
            "scenes": [
                {"type": "intro", "bars": 16, "energy": 3},
                {"type": "drop", "bars": 32, "energy": 8},
                {"type": "build", "bars": 8, "energy": 6},
                {"type": "drop", "bars": 32, "energy": 10},
                {"type": "break", "bars": 8, "energy": 2},
                {"type": "atmosphere", "bars": 8, "energy": 4},
                {"type": "drop", "bars": 32, "energy": 9},
                {"type": "outro", "bars": 16, "energy": 2},
            ],
            "tempo_range": (128, 140),
            "key_compatible": True,
        },
        "house": {
            "scenes": [
                {"type": "intro", "bars": 16, "energy": 3},
                {"type": "drop", "bars": 32, "energy": 7},
                {"type": "break", "bars": 16, "energy": 4},
                {"type": "build", "bars": 16, "energy": 6},
                {"type": "drop", "bars": 32, "energy": 8},
                {"type": "bridge", "bars": 16, "energy": 5},
                {"type": "drop", "bars": 32, "energy": 9},
                {"type": "outro", "bars": 16, "energy": 2},
            ],
            "tempo_range": (118, 130),
            "key_compatible": True,
        },
        "ambient": {
            "scenes": [
                {"type": "intro", "bars": 16, "energy": 1},
                {"type": "atmosphere", "bars": 32, "energy": 3},
                {"type": "atmosphere", "bars": 32, "energy": 4},
                {"type": "build", "bars": 16, "energy": 5},
                {"type": "drop", "bars": 16, "energy": 3},
                {"type": "atmosphere", "bars": 32, "energy": 2},
                {"type": "atmosphere", "bars": 16, "energy": 2},
                {"type": "outro", "bars": 16, "energy": 1},
            ],
            "tempo_range": (70, 100),
            "key_compatible": True,
        },
    }
    
    def __init__(self, tempo: float = 126.0, key: str = "Fm"):
        self.tempo = tempo
        self.key = key
    
    def generate_arrangement(
        self,
        genre: str = "dub_techno",
        key: Optional[str] = None,
        length: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Generate scene sequence for a complete arrangement.
        
        Args:
            genre: Genre template name
            key: Key signature (default: self.key)
            length: Number of scenes (max 8)
            
        Returns:
            List of scene plan dicts
        """
        template = self.ARRANGEMENTS.get(genre, self.ARRANGEMENTS["dub_techno"])
        scenes = template["scenes"][:length]
        
        # Apply tempo and key
        plan = []
        for i, scene in enumerate(scenes):
            scene_plan = dict(scene)
            scene_plan["tempo"] = self.tempo
            scene_plan["key"] = key or self.key
            scene_plan["scene_index"] = i
            
            # Add key transition info
            if i > 0:
                prev = scenes[i - 1]
                scene_plan["energy_change"] = scene["energy"] - prev["energy"]
            else:
                scene_plan["energy_change"] = 0
            
            plan.append(scene_plan)
        
        return plan
    
    @classmethod
    def list_genres(cls) -> List[str]:
        """List available arrangement genres."""
        return sorted(cls.ARRANGEMENTS.keys())
    
    @staticmethod
    def energy_to_params(energy: int) -> Dict[str, Any]:
        """Convert energy level (1-10) to generation parameters."""
        return {
            "kick_velocity": 30 + energy * 9,
            "hat_velocity": 20 + energy * 7,
            "bass_velocity": 25 + energy * 9,
            "chord_velocity": 20 + energy * 8,
            "melody_velocity": 20 + energy * 7,
            "kick_pulses": max(1, int(energy * 0.7)),
            "hat_pulses": max(2, int(energy * 1.3)),
            "snare_active": energy >= 4,
            "clap_active": energy >= 3,
            "perc_active": energy >= 2,
            "bass_active": energy >= 3,
            "chords_active": energy >= 2,
            "melody_active": energy >= 4,
        }


class MemorySystem:
    """
    Usage-pattern learning system.
    
    Tracks which generation parameters produce good results,
    learns user preferences, and recommends optimal settings.
    
    Usage:
        mem = MemorySystem()
        mem.record_success(genre="dub_techno", params={...}, quality=8)
        recommendation = mem.recommend("dub_techno")
    """
    
    def __init__(self):
        self._history: List[Dict[str, Any]] = []
        self._preferences: Dict[str, Dict[str, Any]] = {}
    
    def record_success(
        self,
        genre: str,
        params: Dict[str, Any],
        quality: int = 5
    ) -> None:
        """
        Record a successful generation.
        
        Args:
            genre: Genre used
            params: Parameters used
            quality: User rating (1-10)
        """
        record = {
            "genre": genre,
            "params": params,
            "quality": quality,
            "timestamp": __import__("time").time(),
        }
        self._history.append(record)
        
        # Update preferences for this genre
        if genre not in self._preferences:
            self._preferences[genre] = {}
        
        for key, value in params.items():
            if key not in self._preferences[genre]:
                self._preferences[genre][key] = {"sum": 0, "count": 0}
            self._preferences[genre][key]["sum"] += value if isinstance(value, (int, float)) else 0
            self._preferences[genre][key]["count"] += 1
    
    def recommend(self, genre: str) -> Dict[str, Any]:
        """
        Recommend optimal parameters for a genre.
        
        Args:
            genre: Genre to get recommendations for
            
        Returns:
            Dict of recommended parameter values
        """
        if genre not in self._preferences:
            return {}
        
        recommendations = {}
        for key, stats in self._preferences[genre].items():
            if stats["count"] > 0:
                recommendations[key] = stats["sum"] / stats["count"]
        
        return recommendations
    
    def get_popular_parameters(self, genre: str, top_n: int = 5) -> List[str]:
        """Get most frequently used parameter keys."""
        if genre not in self._preferences:
            return []
        
        sorted_keys = sorted(
            self._preferences[genre].keys(),
            key=lambda k: self._preferences[genre][k]["count"],
            reverse=True
        )
        return sorted_keys[:top_n]
    
    def get_history(self, genre: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get generation history, optionally filtered by genre."""
        records = self._history
        if genre:
            records = [r for r in records if r.get("genre") == genre]
        return records[-limit:]
    
    def clear(self) -> None:
        """Clear all history and preferences."""
        self._history.clear()
        self._preferences.clear()


class GrooveTemplateImporter:
    """
    Import groove templates from real MIDI patterns.
    
    Analyzes MIDI timing and velocity data to create
    GrooveGenerator-compatible templates with authentic feel.
    
    Usage:
        importer = GrooveTemplateImporter()
        # From a list of notes:
        template = importer.analyze_notes(notes_data)
        # Apply template:
        generator = GrooveGenerator()
        velocities = generator.apply_template(template, length=16)
    """
    
    @staticmethod
    def analyze_notes(
        notes: List[Dict[str, Any]],
        subdivision: float = 0.25
    ) -> Dict[str, Any]:
        """
        Analyze a set of MIDI notes to extract groove data.
        
        Args:
            notes: List of note dicts with velocity, start_time, duration
            subdivision: Grid subdivision for quantization reference
            
        Returns:
            Groove template dict with velocity_pattern and timing_offsets
        """
        if not notes:
            return {"velocity_pattern": [], "timing_offsets": [], "average_velocity": 80}
        
        # Extract velocities sorted by time
        sorted_notes = sorted(notes, key=lambda n: n["start_time"])
        
        velocity_pattern = [n["velocity"] for n in sorted_notes]
        timing_offsets = []
        
        for note in sorted_notes:
            beat = note["start_time"]
            # Find nearest grid position
            grid_pos = round(beat / subdivision) * subdivision
            offset = beat - grid_pos
            timing_offsets.append(offset)
        
        avg_velocity = sum(v for v in velocity_pattern) / len(velocity_pattern)
        max_velocity = max(velocity_pattern) if velocity_pattern else 100
        
        return {
            "velocity_pattern": velocity_pattern,
            "timing_offsets": timing_offsets,
            "average_velocity": int(avg_velocity),
            "max_velocity": max_velocity,
            "note_count": len(sorted_notes),
            "subdivision": subdivision,
        }
    
    @staticmethod
    def create_groove_template(
        velocities: List[int],
        timing_offsets: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Create a reusable groove template from extracted data.
        
        Args:
            velocities: List of velocity values for a bar
            timing_offsets: Microtiming offsets for each subdivision
            
        Returns:
            Template dict compatible with GrooveGenerator
        """
        length = len(velocities)
        if timing_offsets is None:
            timing_offsets = [0.0] * length
        
        return {
            "velocity_pattern": velocities,
            "timing_offsets": timing_offsets,
            "length": length,
        }
    
    @staticmethod
    def apply_template(
        template: Dict[str, Any],
        bars: int = 8
    ) -> List[int]:
        """
        Apply a groove template to generate velocities.
        
        Args:
            template: Groove template dict
            bars: Number of bars to generate
            
        Returns:
            List of velocity values for bars*bars_subdivisions
        """
        velocities = template.get("velocity_pattern", [])
        if not velocities:
            return [100] * (bars * 16)
        
        result = []
        for bar in range(bars):
            for vel in velocities:
                # Add subtle variation each bar
                variation = random.randint(-3, 3)
                result.append(max(20, min(127, vel + variation)))
        
        return result
    
    @staticmethod
    def generate_preset_library() -> Dict[str, Dict[str, Any]]:
        """
        Generate a library of common groove presets.
        
        Returns:
            Dict of preset name -> groove template
        """
        return {
            "straight_8th": GrooveTemplateImporter.create_groove_template(
                [100, 75, 90, 70, 100, 75, 90, 70],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ),
            "swung_8th": GrooveTemplateImporter.create_groove_template(
                [100, 70, 95, 65, 100, 70, 95, 65],
                [0.0, 0.05, 0.0, 0.05, 0.0, 0.05, 0.0, 0.05]
            ),
            "shuffle": GrooveTemplateImporter.create_groove_template(
                [100, 60, 85, 55, 100, 60, 85, 55],
                [0.0, 0.08, 0.0, 0.08, 0.0, 0.08, 0.0, 0.08]
            ),
            "dub_techno_swing": GrooveTemplateImporter.create_groove_template(
                [100, 65, 85, 55, 95, 70, 80, 50],
                [0.0, 0.04, 0.01, 0.06, 0.0, 0.03, 0.02, 0.05]
            ),
            "four_on_floor": GrooveTemplateImporter.create_groove_template(
                [110, 65, 105, 60, 108, 65, 103, 60],
                [0.0, 0.02, 0.0, 0.03, 0.0, 0.02, 0.0, 0.03]
            ),
        }


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
        scale_type: Optional[ScaleType] = None,
        order: int = 1,
    ) -> 'ClipGenerator':
        """
        Add melody generated using Markov chain for musically coherent motion.
        
        Args:
            length: Number of notes to generate
            velocity: Base velocity
            octave: Octave offset for MIDI notes
            start_degree: Starting scale degree
            scale_type: ScaleType to use for diatonic transitions
            order: Markov order - 1 (simpler) or 2 (more structured phrases)
        """
        # Use provided scale or default to self.scale
        scale = self.scale
        if scale_type:
            scale = Scale(self.key, scale_type)
        
        # Get or create transition matrix
        st = scale_type or self.scale.scale_type
        
        if order >= 2:
            transitions = PMarkov2.create_diatonic_transitions(st)
            markov = PMarkov2(transitions, scale)
            melody = markov.generate(length, [start_degree] if isinstance(start_degree, int) else start_degree)
        else:
            transitions = PMarkov.create_diatonic_transitions(st)
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