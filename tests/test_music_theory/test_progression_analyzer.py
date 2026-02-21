"""Tests for progression analyzer utility."""

import pytest
import sys
import os

# Add music_theory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestProgressionAnalyzer:
    """Tests for progression analyzer function."""

    def test_blues_progression_analysis(self):
        """Test blues progression analysis."""
        from music_theory.progression import analyze_progression

        result = analyze_progression(["i", "VII", "VI", "V"])
        assert result["key"] == "Amin"
        assert result["style"] == "blues"
        assert result["valid"] is True

    def test_major_progression_analysis(self):
        """Test major progression analysis."""
        from music_theory.progression import analyze_progression

        result = analyze_progression(["I", "vi", "ii", "V"])
        assert result["key"] == "Cmaj"  # Matches pop progression key
        assert result["style"] == "pop"  # Matches pop progression name
        assert result["valid"] is True

    def test_invalid_progression(self):
        """Test invalid progression."""
        from music_theory.progression import analyze_progression

        result = analyze_progression(["X"])
        assert result["valid"] is False
        assert "Unknown roman numeral" in result["error"]
