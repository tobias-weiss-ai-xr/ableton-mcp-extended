"""Tests for recipe library data models and validation."""
import pytest
import json
from MCP_Server.recipe_library.models import (
    ChordProgression,
    DrumPattern,
    MixTemplate,
    SoundDesign,
    validate_category_data,
    RecipeSummary,
)


class TestChordProgression:
    def test_valid(self):
        data = ChordProgression(
            key="C", scale="major", chords=["C", "Am", "F", "G"],
            voicing="open", mood="uplifting"
        )
        assert data["key"] == "C"
        assert len(data["chords"]) == 4

    def test_validation_pass(self):
        result = validate_category_data("chord_progression", json.dumps({
            "key": "C", "scale": "major", "chords": ["C", "Am", "F", "G"],
            "voicing": "open", "mood": "uplifting"
        }))
        assert result is True


class TestDrumPattern:
    def test_valid(self):
        data = DrumPattern(
            pattern_type="one_drop", kit_query="query:Drums#FileId_58622",
            bars=4, grid="|X---|---X---|", tempo_range=[70, 90], mood="dub"
        )
        assert data["pattern_type"] == "one_drop"

    def test_validation_pass(self):
        result = validate_category_data("drum_pattern", json.dumps({
            "pattern_type": "one_drop", "kit_query": "query:Drums#FileId_58622",
            "bars": 4, "grid": "|X---|", "tempo_range": [70, 90], "mood": "dub"
        }))
        assert result is True


class TestMixTemplate:
    def test_valid(self):
        data = MixTemplate(
            genre="deep_house", track_count=6,
            structure=["intro", "drop"],
            mixing_techniques=["bass_forward", "crossfade"],
            energy_curve="progressive_house",
            description="Warm deep house"
        )
        assert data["genre"] == "deep_house"

    def test_validation_pass(self):
        result = validate_category_data("mix_template", json.dumps({
            "genre": "deep_house", "track_count": 6,
            "structure": ["intro", "drop"],
            "mixing_techniques": ["bass_forward"],
            "energy_curve": "progressive_house",
            "description": "Deep house template"
        }))
        assert result is True


class TestSoundDesign:
    def test_valid(self):
        data = SoundDesign(
            device_type="Operator", preset_name="Deep Sub Bass",
            parameters={"filter_cutoff": 0.4, "filter_resonance": 0.2},
            tags=["bass", "sub"]
        )
        assert data["device_type"] == "Operator"

    def test_validation_pass(self):
        result = validate_category_data("sound_design", json.dumps({
            "device_type": "Operator", "preset_name": "Deep Sub Bass",
            "parameters": {"filter_cutoff": 0.4},
            "tags": ["bass"]
        }))
        assert result is True


class TestValidationEdgeCases:
    def test_invalid_category(self):
        with pytest.raises(ValueError, match="Unknown category"):
            validate_category_data("invalid_cat", "{}")

    def test_invalid_json(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            validate_category_data("chord_progression", "not json")

    def test_missing_required_field(self):
        with pytest.raises(ValueError, match="Missing required field"):
            validate_category_data("chord_progression", json.dumps({
                "key": "C"
            }))


class TestRecipeSummary:
    def test_fields(self):
        summary = RecipeSummary(
            id=1, category="chord_progression", name="Test Progression",
            tags="pop,verse", description="A test"
        )
        assert summary["id"] == 1
        assert summary["category"] == "chord_progression"

    def test_empty_description(self):
        summary = RecipeSummary(
            id=2, category="drum_pattern", name="Drum Test",
            tags="", description=""
        )
        assert summary["name"] == "Drum Test"
