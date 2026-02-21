"""Progression analyzer utility."""

# Common chord progressions by genre
_PROGRESSION_PATTERNS = {
    "blues": {
        "pattern": ["i", "VII", "VI", "V"],  # A min: Amin → Gmaj → Fmaj → Emaj
        "key": "Amin",
    },
    "pop": {
        "pattern": ["I", "vi", "ii", "V"],  # C major: Cmaj → Amin → Dmin → Gmaj
        "key": "Cmaj",
    },
    "jazz": {
        "pattern": ["ii", "V", "I"],  # C major: Dm7 → G7 → Cmaj
        "key": "Cmaj",
    },
}

# Roman numeral normalization
_ROMAN_NUMERALS = {
    "I": 0,
    "II": 2,
    "III": 4,
    "IV": 5,
    "V": 7,
    "VI": 9,
    "VII": 11,
    "i": 0,
    "ii": 2,
    "iii": 4,
    "iv": 5,
    "v": 7,
    "vi": 9,
    "vii": 11,
    "VI": 8,
    "VII": 10,
}


def analyze_progression(progression: list) -> dict:
    """
    Analyze chord progression and estimate key/style.

    Args:
        progression: List of Roman numerals (e.g., ["I", "vi", "ii", "V"])

    Returns:
        Dict with keys:
        - valid: bool
        - key: estimated key (e.g., "Cmaj" or "Amin")
        - style: estimated style ("blues", "pop", "jazz")
        - error: only present if invalid
    """
    if not progression:
        return {"valid": False, "error": "Empty progression"}

    for numeral in progression:
        normalized_numeral = (
            numeral.upper()
            if numeral.lower() in ["i", "ii", "iii", "iv", "v", "vi", "vii"]
            else numeral
        )
        if normalized_numeral not in _ROMAN_NUMERALS:
            return {"valid": False, "error": f"Unknown roman numeral: {numeral}"}

    # Default: assume progression in A minor (blues)
    key = "Amin"  # Default
    style = "blues"  # Default

    # Try to match known progression patterns
    matched = False
    for progression_name, pattern_data in _PROGRESSION_PATTERNS.items():
        if progression == pattern_data["pattern"]:
            key = pattern_data["key"]
            style = progression_name
            matched = True
            break

    return {"valid": True, "key": key, "style": style, "matched": matched}
