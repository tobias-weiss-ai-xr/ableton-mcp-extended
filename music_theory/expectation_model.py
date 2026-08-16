"""
Expectation-based chord suggestion using information-theoretic principles.

Paper: GraphIDyOM — A graph-native Python reimplementation of IDyOM
       for musical expectation modelling (Rosselló, 2026)
       arXiv:2607.25787

Based on the Information Dynamics of Music (IDyOM) framework (Pearce &
   Wiggins, 2012), which models musical expectation as information
   content — how "surprising" a chord is given the context of what
   came before.

Enhances suggest_next_chord() with expectation scores that balance
predictability (boring) and surprise (jarring). The sweet spot is
"optimal surprise" — chords that are unexpected but still contextually
appropriate.

Usage:
    from music_theory.expectation_model import ChordExpectationModel

    model = ChordExpectationModel()
    suggestions = model.rank_by_expectation(
        current_chord={"root": 60, "quality": "maj"},
        key_root=60,
        scale="major",
        style="pop",
        candidates=[...]  # or use model.get_candidates()
    )
    # Returns list ranked by optimal surprise score
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from .harmonization import (
    DIATONIC_CHORDS,
    SCALE_INTERVALS,
    suggest_next_chord,
)


class ChordExpectationModel:
    """
    Information-theoretic chord expectation model.

    Models how "expected" or "surprising" a chord transition is, based on:
    1. **Tonal context**: How well the chord fits the current key/scale
    2. **Transition probability**: How common this transition is in the style
    3. **Recency**: How recently this chord was used (avoiding repetition)
    4. **Voice-leading distance**: How far the chord moves from the previous one

    Returns an "expectation score" (0-1) where:
    - 0.0 = highly predictable (boring, no tension)
    - 0.3-0.7 = "optimal surprise" (interesting but appropriate)
    - 1.0 = highly surprising (jarring, contextually inappropriate)
    """

    def __init__(self):
        # Transition probability tables (estimated from common practice)
        # These are simplified P(next | current) for common progressions
        self._transition_probs = self._build_transition_probs()

        # Optimal surprise range (from IDyOM research)
        self._optimal_min = 0.3
        self._optimal_max = 0.7

    def rank_by_expectation(
        self,
        current_chord: Dict[str, Any],
        key_root: int,
        scale: str = "major",
        style: str = "pop",
        candidates: Optional[List[Dict[str, Any]]] = None,
        chord_history: Optional[List[Dict[str, Any]]] = None,
        top_n: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        Rank chord candidates by optimal surprise score.

        Args:
            current_chord: Current chord with "root" and "quality"
            key_root: MIDI note of the key
            scale: Scale name (major, minor, etc.)
            style: Musical style for transition probabilities
            candidates: Optional list of candidate chords (auto-generated if None)
            chord_history: Previous chords in the progression (for recency)
            top_n: Max number of results

        Returns:
            List of candidate chords with added expectation_score and
            information_content fields, sorted by distance from optimal
            surprise range.
        """
        # Get or generate candidates
        if candidates is None:
            base_suggestions = suggest_next_chord(
                current_chord, key_root, scale, style
            )
            candidates = list(base_suggestions)
            # Also add diatonic chords not in suggestions
            candidates = self._ensure_diatonic_coverage(
                candidates, key_root, scale
            )

        chord_history = chord_history or []

        for candidate in candidates:
            ic = self._compute_information_content(
                candidate, current_chord, key_root, scale, style, chord_history
            )
            candidate["information_content"] = ic
            candidate["expectation_score"] = ic
            candidate["surprise_label"] = self._label_surprise(ic)

        # Sort by distance from optimal surprise range center
        optimal_center = (self._optimal_min + self._optimal_max) / 2.0
        candidates.sort(
            key=lambda c: abs(c["expectation_score"] - optimal_center)
        )

        return candidates[:top_n]

    def _compute_information_content(
        self,
        candidate: Dict[str, Any],
        current_chord: Dict[str, Any],
        key_root: int,
        scale: str,
        style: str,
        chord_history: List[Dict[str, Any]],
    ) -> float:
        """
        Compute information content (surprise) of a chord transition.

        IC = -log2(P(chord | context))

        Lower IC = more predictable = less surprise
        Higher IC = more surprising

        We combine four factors:
        1. Transition probability (dominant factor)
        2. Scale membership (how well it fits the key)
        3. Voice-leading distance (smooth vs. jumpy motion)
        4. Recency penalty (avoiding recent repetition)
        """
        # 1. Transition probability
        trans_prob = self._get_transition_probability(
            current_chord, candidate, style
        )

        # 2. Scale membership
        scale_score = self._scale_membership_score(
            candidate, key_root, scale
        )

        # 3. Voice-leading distance
        vl_distance = self._voice_leading_distance(current_chord, candidate)

        # 4. Recency penalty
        recency = self._recency_penalty(candidate, chord_history)

        # Combine: base surprise from transition prob, modulated by others
        if trans_prob > 0:
            base_ic = -math.log2(trans_prob)
        else:
            base_ic = 5.0  # Maximum surprise for impossible transitions

        # Normalize to 0-1 range (typical IC range is 0-5 bits)
        normalized_ic = min(base_ic / 5.0, 1.0)

        # Scale membership reduces surprise (in-key chords feel more expected)
        normalized_ic *= (1.0 - scale_score * 0.3)

        # Voice-leading smoothness reduces surprise slightly
        vl_factor = min(vl_distance / 12.0, 1.0)
        normalized_ic *= (1.0 + vl_factor * 0.1)

        # Recency increases surprise (repetition is "expected" but boring)
        normalized_ic += recency * 0.15

        return max(0.0, min(1.0, normalized_ic))

    def _get_transition_probability(
        self,
        current: Dict[str, Any],
        candidate: Dict[str, Any],
        style: str,
    ) -> float:
        """Look up transition probability from learned table."""
        key = self._chord_to_roman(current, style)
        cand = candidate.get("roman", self._chord_to_roman(candidate, style))

        style_probs = self._transition_probs.get(style, self._transition_probs["pop"])
        next_probs = style_probs.get(key, {})

        return next_probs.get(cand, 0.01)  # Low but non-zero base probability

    @staticmethod
    def _chord_to_roman(chord: Dict[str, Any], style: str) -> str:
        """Convert chord root to approximate Roman numeral."""
        # This is a simplified mapping — full implementation would need
        # the key context. We return a generic root-based key.
        root_pc = chord.get("root", 0) % 12
        roman_map = {
            0: "I",
            1: "I",
            2: "ii",
            3: "iii",
            4: "IV",
            5: "V",
            6: "vi",
            7: "VII",
            8: "I",
            9: "ii",
            10: "iii",
            11: "IV",
        }
        return roman_map.get(root_pc, "I")

    def _scale_membership_score(
        self, chord: Dict[str, Any], key_root: int, scale: str
    ) -> float:
        """
        How well does this chord fit the current scale? (0-1)
        1.0 = perfectly diatonic, 0.0 = completely outside
        """
        root_pc = (chord.get("root", 0) - key_root) % 12
        scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["major"])

        if root_pc in scale_intervals:
            return 1.0  # Root is on a scale degree — fully diatonic

        # Check if root is near a scale degree (chromatic neighbors)
        distances = [min(abs(root_pc - si), 12 - abs(root_pc - si)) for si in scale_intervals]
        min_dist = min(distances)
        return max(0.0, 1.0 - min_dist / 3.0)

    @staticmethod
    def _voice_leading_distance(
        current: Dict[str, Any], candidate: Dict[str, Any]
    ) -> float:
        """
        Root-motion distance in semitones (0-11).
        Smaller = smoother voice leading.
        """
        if "root" not in current or "root" not in candidate:
            return 6.0  # Unknown — assume moderate distance

        dist = abs(current["root"] - candidate["root"]) % 12
        return min(dist, 12 - dist)

    @staticmethod
    def _recency_penalty(
        candidate: Dict[str, Any], history: List[Dict[str, Any]]
    ) -> float:
        """
        Penalty for recently-used chords. Returns 0-1.
        0 = not recently used, 1 = was the last chord played.
        """
        if not history:
            return 0.0

        cand_root = candidate.get("root", -1)

        # Check last few chords
        lookback = min(len(history), 4)
        for i in range(1, lookback + 1):
            if history[-i].get("root") == cand_root:
                return 1.0 / i  # Decay: 1.0, 0.5, 0.33, 0.25

        return 0.0

    @staticmethod
    def _label_surprise(ic: float) -> str:
        """Label the surprise level for human readability."""
        if ic < 0.2:
            return "predictable"
        elif ic < 0.35:
            return "comfortable"
        elif ic < 0.55:
            return "interesting"
        elif ic < 0.7:
            return "surprising"
        else:
            return "jarring"

    def _ensure_diatonic_coverage(
        self, candidates: List[Dict[str, Any]], key_root: int, scale: str
    ) -> List[Dict[str, Any]]:
        """Add missing diatonic chords to the candidate list."""
        scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["major"])
        diatonic_qualities = DIATONIC_CHORDS.get(scale, DIATONIC_CHORDS["major"])

        existing_roots = {c.get("root", -1) % 12 for c in candidates}

        for i, interval in enumerate(scale_intervals):
            root = key_root + interval
            if root % 12 not in existing_roots:
                quality = diatonic_qualities[i] if i < len(diatonic_qualities) else "maj"
                candidates.append(
                    {
                        "root": root,
                        "quality": quality,
                        "name": f"{_note_name(root)}{quality}",
                        "probability": 0.05,
                        "roman": ["I", "ii", "iii", "IV", "V", "vi", "vii°"][
                            min(i, 6)
                        ],
                    }
                )
                existing_roots.add(root % 12)

        return candidates

    @staticmethod
    def _build_transition_probs() -> dict:
        """
        Build simplified transition probability tables by style.

        Based on common practice harmony (Kostka & Payne, Piston).
        Values are approximate P(next | current).
        """
        pop = {
            "I": {"V": 0.30, "IV": 0.25, "vi": 0.20, "ii": 0.15, "iii": 0.05, "vii°": 0.05},
            "ii": {"V": 0.50, "IV": 0.15, "vi": 0.15, "I": 0.10, "vii°": 0.10},
            "iii": {"vi": 0.35, "IV": 0.25, "I": 0.15, "ii": 0.15, "V": 0.10},
            "IV": {"V": 0.30, "I": 0.25, "ii": 0.15, "vi": 0.15, "vii°": 0.15},
            "V": {"I": 0.55, "vi": 0.20, "IV": 0.10, "vii°": 0.10, "ii": 0.05},
            "vi": {"IV": 0.25, "ii": 0.25, "V": 0.20, "I": 0.15, "iii": 0.15},
            "vii°": {"I": 0.40, "iii": 0.25, "V": 0.20, "vi": 0.15},
        }
        jazz = {
            "I": {"vi": 0.20, "ii": 0.20, "V": 0.15, "iii": 0.15, "IV": 0.15, "vii°": 0.15},
            "ii": {"V": 0.55, "vii°": 0.20, "I": 0.10, "iii": 0.10, "IV": 0.05},
            "V": {"I": 0.50, "vii°": 0.20, "vi": 0.10, "ix": 0.10, "ii": 0.10},
            "vi": {"ii": 0.35, "V": 0.20, "vii°": 0.20, "I": 0.15, "IV": 0.10},
            "vii°": {"iii": 0.35, "I": 0.25, "V": 0.15, "vi": 0.10, "ii": 0.15},
            "iii": {"vi": 0.40, "vii°": 0.20, "I": 0.15, "ii": 0.15, "IV": 0.10},
            "IV": {"iv7": 0.25, "I": 0.20, "V": 0.20, "ii": 0.15, "vii°": 0.20},
        }
        classical = {
            "I": {"IV": 0.30, "V": 0.25, "vi": 0.20, "ii": 0.15, "iii": 0.10},
            "IV": {"V": 0.35, "I": 0.25, "ii": 0.15, "vii°": 0.15, "vi": 0.10},
            "V": {"I": 0.60, "IV": 0.15, "vi": 0.10, "vii°": 0.10, "vi": 0.05},
            "vi": {"IV": 0.30, "V": 0.20, "ii": 0.20, "I": 0.15, "vii°": 0.15},
            "ii": {"V": 0.50, "vii°": 0.20, "IV": 0.15, "I": 0.10, "vi": 0.05},
        }
        electronic = {
            "I": {"iv": 0.25, "v": 0.25, "vi": 0.20, "III": 0.15, "VII": 0.15},
            "iv": {"v": 0.30, "I": 0.20, "vi": 0.20, "VII": 0.15, "v": 0.15},
            "v": {"I": 0.40, "vi": 0.25, "VII": 0.15, "iv": 0.10, "III": 0.10},
            "vi": {"iv": 0.30, "II": 0.20, "v": 0.20, "I": 0.15, "III": 0.15},
            "III": {"VI": 0.30, "vii": 0.25, "I": 0.20, "iv": 0.15, "II": 0.10},
        }
        return {
            "pop": pop,
            "jazz": jazz,
            "classical": classical,
            "electronic": electronic,
            "techno": electronic,  # Reuses electronic
            "house": electronic,
            "ambient": classical,  # Ambient uses classical voice-leading
            "dub_techno": electronic,
        }


# ── Helper ────────────────────────────────────────────────────────────

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _note_name(midi_note: int) -> str:
    """Convert MIDI note number to note name."""
    return NOTE_NAMES[midi_note % 12]


# ── Convenience function for direct import ───────────────────────────────

def suggest_chords_with_expectation(
    current_chord: Dict[str, Any],
    key_root: int,
    scale: str = "major",
    style: str = "pop",
    chord_history: Optional[List[Dict[str, Any]]] = None,
    top_n: int = 8,
) -> List[Dict[str, Any]]:
    """
    High-level function: suggest next chords ranked by optimal surprise.

    This is the main entry point for integration with suggest_next_chord().
    Returns the same format as suggest_next_chord() but with added
    information_content and expectation_score fields.

    Paper grounding: GraphIDyOM (Rosselló, 2026) — arXiv:2607.25787
    """
    model = ChordExpectationModel()
    return model.rank_by_expectation(
        current_chord=current_chord,
        key_root=key_root,
        scale=scale,
        style=style,
        chord_history=chord_history,
        top_n=top_n,
    )


if __name__ == "__main__":
    print("Chord Expectation Model — GraphIDyOM-based\n")

    model = ChordExpectationModel()

    # Example: After C major, what should come next?
    current = {"root": 60, "quality": "maj"}
    results = model.rank_by_expectation(
        current_chord=current,
        key_root=60,
        scale="major",
        style="pop",
        top_n=8,
    )

    print(f"After {results[0].get('name', '?') if results else '?'}:\n")
    print(f"{'Chord':<12} {'IC':>6} {'Surprise':<14} {'Score':>6}")
    print("-" * 42)
    for r in results:
        name = r.get("name", "?")
        ic = r.get("information_content", 0)
        label = r.get("surprise_label", "?")
        score = r.get("expectation_score", 0)
        marker = " ◀ OPTIMAL" if 0.3 <= score <= 0.7 else ""
        print(f"{name:<12} {ic:>5.3f} {label:<14} {score:>5.3f}{marker}")

    print("\nWith chord history (C → Am → F):")
    history = [
        {"root": 60, "quality": "maj"},
        {"root": 57, "quality": "min"},
    ]
    current = {"root": 65, "quality": "maj"}
    results2 = model.rank_by_expectation(
        current_chord=current,
        key_root=60,
        scale="major",
        style="pop",
        chord_history=history,
        top_n=6,
    )
    for r in results2:
        name = r.get("name", "?")
        ic = r.get("information_content", 0)
        label = r.get("surprise_label", "?")
        score = r.get("expectation_score", 0)
        marker = " ◀ OPTIMAL" if 0.3 <= score <= 0.7 else ""
        print(f"  {name:<12} {ic:>5.3f} {label:<14} {score:>5.3f}{marker}")
