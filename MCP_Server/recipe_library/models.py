"""TypedDicts and validation for recipe library categories."""
from typing import TypedDict, Optional, List
import json


class ChordProgression(TypedDict):
    key: str
    scale: str
    chords: List[str]
    voicing: str
    mood: str


class DrumPattern(TypedDict):
    pattern_type: str
    kit_query: str
    bars: int
    grid: str
    tempo_range: List[int]
    mood: str


class MixTemplate(TypedDict):
    genre: str
    track_count: int
    structure: List[str]
    mixing_techniques: List[str]
    energy_curve: str
    description: str


class SoundDesign(TypedDict):
    device_type: str
    preset_name: str
    parameters: dict
    tags: List[str]


class RecipeSummary(TypedDict):
    id: int
    category: str
    name: str
    tags: str
    description: str


CATEGORY_VALIDATORS = {
    "chord_progression": {
        "required": ["key", "scale", "chords", "voicing", "mood"],
        "type": ChordProgression,
    },
    "drum_pattern": {
        "required": ["pattern_type", "kit_query", "bars", "grid", "tempo_range", "mood"],
        "type": DrumPattern,
    },
    "mix_template": {
        "required": ["genre", "track_count", "structure", "mixing_techniques", "energy_curve", "description"],
        "type": MixTemplate,
    },
    "sound_design": {
        "required": ["device_type", "preset_name", "parameters", "tags"],
        "type": SoundDesign,
    },
}


def validate_category_data(category: str, data_json: str) -> bool:
    """Validate JSON data against category schema. Raises ValueError on failure."""
    if category not in CATEGORY_VALIDATORS:
        raise ValueError(f"Unknown category: {category}")

    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")

    if not isinstance(data, dict):
        raise ValueError("Data must be a JSON object")

    validator = CATEGORY_VALIDATORS[category]
    for field in validator["required"]:
        if field not in data:
            raise ValueError(f"Missing required field '{field}' for category '{category}'")

    return True
