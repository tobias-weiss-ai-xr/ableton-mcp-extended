"""Tests for grid layout utility (Push, Launchpad, APC)."""

import pytest
import sys
import os

# Add music_theory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestGridLayouts:
    """Tests for grid layout functions."""

    def test_camelot_wheel_push_layout(self):
        """Test Push grid layout for Camelot Wheel."""
        from music_theory.grid import generate_camelot_grid

        grid = generate_camelot_grid(device="Push", key="8A")

        # Push has 8x8 matrix
        assert len(grid) == 8
        assert all(len(row) == 8 for row in grid)

        # 8A should illuminate (active key)
        active_positions = []
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell.get("active"):
                    active_positions.append((i, j))
        assert len(active_positions) == 1

        # One-hour up/down/relative should be adjacent
        row, col = active_positions[0]
        adjacent_keys = [grid[row - 1][col], grid[row + 1][col], grid[row][col - 1]]
        adjacent_labels = [adj.get("label") for adj in adjacent_keys if adj]
        assert "9A" in adjacent_labels  # One-hour up
        assert "7A" in adjacent_labels  # One-hour down
        assert "8B" in adjacent_labels  # Relative

    def test_launchpad_chromatic_scale(self):
        """Test Launchpad chromatic scale layout."""
        from music_theory.grid import generate_chromatic_grid

        grid = generate_chromatic_grid(device="Launchpad", root=60)  # C4

        # Launchpad has 8x8 RGB grid
        assert len(grid) == 8
        assert len(grid[0]) == 8

        # Check first few notes: C4 (60), C#4 (61), D4 (62)
        expected_midi = [60, 61, 62, 63, 64, 65, 66, 67]
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G"]
        for i, midi_note in enumerate(expected_midi):
            note_info = grid[0][i]
            assert note_info["midi_note"] == midi_note
            assert note_info["note_name"] == note_names[i]

    def test_apc_mini_drum_map(self):
        """Test APC Mini drum pad layout."""
        from music_theory.grid import generate_drum_grid

        grid = generate_drum_grid(device="APC", kit="techno")

        # APC Mini has 4x8 drum pad grid
        assert len(grid) == 4
        assert len(grid[0]) == 8

        # Check known drum assignments
        kick_cell = grid[0][0]
        assert kick_cell["sound"] == "kick"
        assert 36 <= kick_cell["midi_note"] <= 40

        snare_cell = grid[0][1]
        assert snare_cell["sound"] == "snare"

        hat_cell = grid[1][0]
        assert hat_cell["sound"] == "hat"
