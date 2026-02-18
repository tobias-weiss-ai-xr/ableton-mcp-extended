"""
Verification script for pattern variation entropy.

Measures Shannon entropy of generated patterns to ensure sufficient variation.
Run with --simulate mode (always True) to test without Ableton connection.

Usage:
    cd dub_techno_2h && python -m generative.verify_variation --duration 30
    cd dub_techno_2h/generative && python verify_variation.py --duration 30
"""

import argparse
import math
import os
import sys
from collections import Counter
from typing import List, Dict, Tuple

# Support both module and direct execution
try:
    from .pattern_generator import PatternGenerator
    from .config import TEMPO
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from generative.pattern_generator import PatternGenerator
    from generative.config import TEMPO


def hash_pattern(notes: List[Dict]) -> Tuple:
    """
    Convert note list to hashable tuple for comparison.

    Args:
        notes: List of note dictionaries with pitch, start_time, duration, velocity, mute.

    Returns:
        Sorted tuple of (pitch, start_time, duration) tuples.
    """
    return tuple(
        sorted((n["pitch"], round(n["start_time"], 3), n["duration"]) for n in notes)
    )


def calculate_entropy(patterns: List[Tuple]) -> float:
    """
    Calculate Shannon entropy of pattern distribution.

    H = -sum(p * log2(p)) for each unique pattern probability p.

    Args:
        patterns: List of hashable pattern representations.

    Returns:
        Shannon entropy in bits.
    """
    counter = Counter(patterns)
    total = len(patterns)
    entropy = 0.0
    for count in counter.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def find_max_consecutive_repeats(patterns: List[Tuple]) -> int:
    """
    Find the maximum number of consecutive identical patterns.

    Args:
        patterns: List of hashable pattern representations.

    Returns:
        Maximum consecutive repeat count.
    """
    if not patterns:
        return 0

    max_repeats = 1
    current_repeats = 1

    for i in range(1, len(patterns)):
        if patterns[i] == patterns[i - 1]:
            current_repeats += 1
            max_repeats = max(max_repeats, current_repeats)
        else:
            current_repeats = 1

    return max_repeats


def count_unique_patterns(patterns: List[Tuple]) -> int:
    """
    Count unique patterns in the list.

    Args:
        patterns: List of hashable pattern representations.

    Returns:
        Number of unique patterns.
    """
    return len(set(patterns))


def verify_variation(
    duration_minutes: int = 30, verbose: bool = False
) -> Tuple[bool, float, int, int]:
    """
    Verify pattern variation meets entropy and repeat thresholds.

    Args:
        duration_minutes: Simulated duration in minutes.
        verbose: Enable detailed output.

    Returns:
        Tuple of (passed, entropy, max_repeats, unique_count).
    """
    # At 126 BPM, ~31 patterns per minute (one per 4-bar loop)
    # 4 bars at 126 BPM = ~7.6 seconds per pattern
    patterns_per_minute = int(60 / (4 * 4 / TEMPO * 60))

    num_patterns = duration_minutes * patterns_per_minute

    print(f"[verify] Generating {num_patterns} patterns for entropy analysis...")

    generator = PatternGenerator()
    patterns: List[Tuple] = []

    for i in range(num_patterns):
        # Generate kick patterns (4 bars each)
        notes = generator.generate_kick(bars=4)
        pattern_hash = hash_pattern(notes)
        patterns.append(pattern_hash)

        # Progress indicator for long runs
        if verbose and (i + 1) % 100 == 0:
            print(f"[verify]   Generated {i + 1}/{num_patterns} patterns...")

    # Calculate metrics
    unique_count = count_unique_patterns(patterns)
    entropy = calculate_entropy(patterns)
    max_repeats = find_max_consecutive_repeats(patterns)

    # Output results
    print(f"[verify] Pattern distribution: {unique_count} unique patterns")
    print(f"[verify] Shannon entropy: {entropy:.2f} bits")
    print(f"[verify] Max consecutive repeats: {max_repeats}")

    # Pass criteria
    entropy_pass = entropy > 2.0
    repeats_pass = max_repeats <= 3
    passed = entropy_pass and repeats_pass

    if passed:
        print(f"PASS: Entropy {entropy:.2f} > 2.0, max repeats {max_repeats} <= 3")
    else:
        failures = []
        if not entropy_pass:
            failures.append(f"entropy {entropy:.2f} <= 2.0")
        if not repeats_pass:
            failures.append(f"max repeats {max_repeats} > 3")
        print(f"FAIL: {', '.join(failures)}")

    if verbose:
        # Show pattern distribution details
        counter = Counter(patterns)
        print(f"\n[verify] Top 10 most common patterns:")
        for i, (pattern, count) in enumerate(counter.most_common(10)):
            pct = (count / len(patterns)) * 100
            print(f"  {i + 1}. {count} occurrences ({pct:.1f}%)")

    return passed, entropy, max_repeats, unique_count


def main():
    """Main entry point with command-line interface."""
    parser = argparse.ArgumentParser(description="Measure pattern variation entropy")
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Simulation duration in 'minutes' (default: 30)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        default=True,
        help="Run without Ableton (always True)",
    )
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    args = parser.parse_args()

    passed, entropy, max_repeats, unique_count = verify_variation(
        duration_minutes=args.duration, verbose=args.verbose
    )

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
