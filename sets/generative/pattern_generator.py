"""
Algorithmic MIDI pattern generator using Markov chains and probabilistic note generation.

Generates dub techno patterns with humanization and variation.
"""

import random
from typing import Dict, List, Optional

from .config import (
    CHORD_INTERVALS,
    GHOST_NOTE_PROBABILITY,
    MARKOV_MATRICES,
    MICRO_TIMING_VARIATION,
    MINOR_SCALE_INTERVALS,
    PATTERN_DURATIONS,
    SCALE_ROOT,
    TEMPO,
    TRACKS,
    VELOCITY_HUMANIZATION,
    VARIATION_BALANCE,
)


class PatternGenerator:
    """
    Generative pattern creator for dub techno MIDI patterns.

    Uses Markov chains for melodic evolution and probabilistic methods
    for rhythm and texture. Supports reproducible output via optional seed.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the pattern generator.

        Args:
            seed: Optional random seed for reproducibility.
                  If None, uses system time for true randomness.
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self._rng = random.Random(seed)

    def _apply_timing_variation(self, start_time: float) -> float:
        """Apply Gaussian micro-timing variation to a note start time."""
        offset = self._rng.gauss(0, MICRO_TIMING_VARIATION)
        return max(0.0, start_time + offset)

    def _apply_velocity_humanization(self, velocity: int) -> int:
        """Apply uniform velocity humanization."""
        offset = self._rng.randint(-VELOCITY_HUMANIZATION, VELOCITY_HUMANIZATION)
        return max(1, min(127, velocity + offset))

    def _should_add_ghost_note(self) -> bool:
        """Determine if a ghost note should be added based on probability."""
        return self._rng.random() < GHOST_NOTE_PROBABILITY

    def _markov_next_state(
        self, current: str, transitions: Dict[str, Dict[str, float]]
    ) -> str:
        """Select next state based on Markov transition probabilities."""
        probs = transitions[current]
        roll = self._rng.random()
        cumulative = 0.0
        for state, prob in probs.items():
            cumulative += prob
            if roll < cumulative:
                return state
        # Fallback to last state if rounding errors
        return list(probs.keys())[-1]

    def generate_kick(self, bars: int = 4) -> List[Dict]:
        """
        Generate a 4/4 kick pattern with ghost notes.

        Args:
            bars: Number of bars (supports prime lengths: 3, 5, 7).

        Returns:
            List of note dictionaries with pitch, start_time, duration, velocity, mute.
        """
        notes = []
        base_velocity = 110
        ghost_velocity = 75

        for bar in range(bars):
            bar_start = bar * 4.0

            # Main four-on-the-floor kicks
            for beat in range(4):
                start = bar_start + beat
                start = self._apply_timing_variation(start)

                # Velocity variation per bar position
                velocity = base_velocity
                if bar % 4 == 2:
                    velocity += 5
                elif bar % 4 == 3:
                    velocity -= 5

                velocity = self._apply_velocity_humanization(velocity)

                notes.append(
                    {
                        "pitch": 36,
                        "start_time": round(start, 4),
                        "duration": 0.25,
                        "velocity": velocity,
                        "mute": False,
                    }
                )

            # Ghost notes on offbeats (beats 1.5, 2.5, 3.5)
            for offbeat in [0.5, 1.5, 2.5, 3.5]:
                if self._should_add_ghost_note():
                    start = self._apply_timing_variation(bar_start + offbeat)
                    notes.append(
                        {
                            "pitch": 36,
                            "start_time": round(start, 4),
                            "duration": 0.15,
                            "velocity": self._apply_velocity_humanization(
                                ghost_velocity
                            ),
                            "mute": False,
                        }
                    )

        return sorted(notes, key=lambda x: x["start_time"])

    def generate_bass(self, bars: int = 4, root: int = 36) -> List[Dict]:
        """
        Generate a bass pattern using Markov chain melody evolution.

        Uses 2nd-order Markov for scale degree transitions.
        States: I (root), III (3rd), V (5th), VII (7th).

        Args:
            bars: Number of bars.
            root: MIDI note number for root note.

        Returns:
            List of note dictionaries.
        """
        notes = []
        bass_config = MARKOV_MATRICES["bass"]
        states = bass_config["states"]
        transitions = bass_config["transitions"]

        # Map states to scale degrees (minor scale)
        state_to_interval = {
            "I": 0,  # Root
            "III": 3,  # Minor 3rd
            "V": 7,  # Perfect 5th
            "VII": 10,  # Minor 7th
        }

        # Start on root
        current_state = "I"

        # Generate notes per beat (one note per beat for dub bass feel)
        for bar in range(bars):
            bar_start = bar * 4.0

            for beat in range(4):
                start = self._apply_timing_variation(bar_start + beat)

                # Get interval for current state
                interval = state_to_interval[current_state]
                pitch = root + interval

                # Determine note duration (longer for root, shorter for others)
                if current_state == "I":
                    duration = self._rng.uniform(0.8, 1.2)
                    velocity = self._rng.randint(100, 115)
                else:
                    duration = self._rng.uniform(0.3, 0.6)
                    velocity = self._rng.randint(85, 100)

                notes.append(
                    {
                        "pitch": pitch,
                        "start_time": round(start, 4),
                        "duration": round(duration, 3),
                        "velocity": self._apply_velocity_humanization(velocity),
                        "mute": False,
                    }
                )

                # Transition to next state
                current_state = self._markov_next_state(current_state, transitions)

        return sorted(notes, key=lambda x: x["start_time"])

    def generate_hihat(self, bars: int = 4, density: str = "medium") -> List[Dict]:
        """
        Generate a hi-hat pattern with density evolution (sparse -> dense).

        Args:
            bars: Number of bars.
            density: Density level - "sparse", "medium", or "dense".

        Returns:
            List of note dictionaries.
        """
        notes = []

        # Density affects how many subdivisions per beat
        density_config = {
            "sparse": {"divisions": 2, "probability": 0.3},
            "medium": {"divisions": 4, "probability": 0.5},
            "dense": {"divisions": 8, "probability": 0.7},
        }

        config = density_config.get(density, density_config["medium"])
        divisions = config["divisions"]
        base_prob = config["probability"]

        for bar in range(bars):
            bar_start = bar * 4.0

            # Density evolution: start sparse, get denser
            evolution_factor = min(1.0, (bar / bars) * 0.5 + 0.5)
            current_prob = base_prob * evolution_factor

            for beat in range(4):
                beat_start = bar_start + beat

                # Main hi-hat on each beat
                if self._rng.random() < 0.9:  # High probability for main hits
                    start = self._apply_timing_variation(beat_start)
                    notes.append(
                        {
                            "pitch": 42,  # Closed hi-hat
                            "start_time": round(start, 4),
                            "duration": 0.1,
                            "velocity": self._apply_velocity_humanization(90),
                            "mute": False,
                        }
                    )

                # Subdivisions
                subdivision_length = 1.0 / divisions
                for sub in range(1, divisions):
                    sub_time = beat_start + (sub * subdivision_length)
                    if self._rng.random() < current_prob:
                        start = self._apply_timing_variation(sub_time)
                        # Alternate between closed and open hi-hat
                        pitch = 42 if self._rng.random() < 0.7 else 46
                        notes.append(
                            {
                                "pitch": pitch,
                                "start_time": round(start, 4),
                                "duration": 0.1 if pitch == 42 else 0.25,
                                "velocity": self._apply_velocity_humanization(
                                    self._rng.randint(60, 80)
                                ),
                                "mute": False,
                            }
                        )

        return sorted(notes, key=lambda x: x["start_time"])

    def generate_pads(self, bars: int = 4, chord_type: str = "minor") -> List[Dict]:
        """
        Generate chord progressions using Markov chain for chord changes.

        Uses minor key progression: i, VII, VI, V.

        Args:
            bars: Number of bars.
            chord_type: Chord quality - "minor" (default) or "major".

        Returns:
            List of note dictionaries representing chords.
        """
        notes = []
        pads_config = MARKOV_MATRICES["pads"]
        states = pads_config["states"]
        transitions = pads_config["transitions"]

        # Root note for chord progressions (C3 area for pads)
        pad_root = 48  # C3

        # Start on i chord
        current_chord = "i"

        for bar in range(bars):
            bar_start = bar * 4.0

            # Get chord intervals
            chord_intervals = CHORD_INTERVALS[current_chord]

            # Play full chord for duration of bar
            for interval in chord_intervals:
                start = self._apply_timing_variation(bar_start)
                notes.append(
                    {
                        "pitch": pad_root + interval,
                        "start_time": round(start, 4),
                        "duration": 3.8,  # Slightly less than bar to avoid overlap
                        "velocity": self._apply_velocity_humanization(70),
                        "mute": False,
                    }
                )

            # Add occasional top note variation
            if self._rng.random() < 0.3:
                # Add octave or 9th
                extra_interval = chord_intervals[0] + 12  # Octave up
                start = self._apply_timing_variation(bar_start + 2.0)
                notes.append(
                    {
                        "pitch": pad_root + extra_interval,
                        "start_time": round(start, 4),
                        "duration": 1.5,
                        "velocity": self._apply_velocity_humanization(50),
                        "mute": False,
                    }
                )

            # Transition to next chord
            current_chord = self._markov_next_state(current_chord, transitions)

        return sorted(notes, key=lambda x: (x["start_time"], x["pitch"]))

    def generate_fx(self, bars: int = 4, fx_type: str = "sweep") -> List[Dict]:
        """
        Generate FX patterns (sweeps, impacts, risers) probabilistically.

        Args:
            bars: Number of bars.
            fx_type: Type of FX - "sweep", "impact", or "riser".

        Returns:
            List of note dictionaries.
        """
        notes = []

        # FX probability per bar (30% chance)
        fx_probability = 0.3

        # FX note mappings (using C2-C4 range for FX samples)
        fx_pitches = {
            "sweep": [36, 37, 38],
            "impact": [39, 40, 41],
            "riser": [42, 43, 44],
        }

        pitches = fx_pitches.get(fx_type, fx_pitches["sweep"])

        for bar in range(bars):
            # 30% chance per bar for FX
            if self._rng.random() < fx_probability:
                bar_start = bar * 4.0

                # Random position within bar
                beat_offset = self._rng.choice([0, 1, 2, 3])
                start = self._apply_timing_variation(bar_start + beat_offset)

                # Random FX pitch
                pitch = self._rng.choice(pitches)

                # Duration depends on FX type
                if fx_type == "sweep":
                    duration = self._rng.uniform(2.0, 3.5)
                    velocity = self._rng.randint(70, 90)
                elif fx_type == "impact":
                    duration = self._rng.uniform(0.5, 1.0)
                    velocity = self._rng.randint(100, 120)
                else:  # riser
                    duration = self._rng.uniform(3.0, 4.0)
                    velocity = self._rng.randint(60, 80)

                notes.append(
                    {
                        "pitch": pitch,
                        "start_time": round(start, 4),
                        "duration": round(duration, 2),
                        "velocity": self._apply_velocity_humanization(velocity),
                        "mute": False,
                    }
                )

        return sorted(notes, key=lambda x: x["start_time"])

    def generate_all_patterns(self, bars: int = 4) -> Dict[str, List[Dict]]:
        """
        Generate all pattern types in a single call.

        Args:
            bars: Number of bars for all patterns.

        Returns:
            Dictionary with pattern names as keys and note lists as values.
        """
        return {
            "kick": self.generate_kick(bars),
            "bass": self.generate_bass(bars),
            "hihat": self.generate_hihat(bars),
            "pads": self.generate_pads(bars),
            "fx": self.generate_fx(bars),
        }


# Convenience function for quick pattern generation
def generate_patterns(
    seed: Optional[int] = None, bars: int = 4
) -> Dict[str, List[Dict]]:
    """
    Quick pattern generation function.

    Args:
        seed: Optional random seed for reproducibility.
        bars: Number of bars for all patterns.

    Returns:
        Dictionary with pattern names as keys and note lists as values.
    """
    generator = PatternGenerator(seed=seed)
    return generator.generate_all_patterns(bars)
