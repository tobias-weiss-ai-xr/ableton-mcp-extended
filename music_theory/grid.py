"""Grid layouts for MIDI controllers (Push, Launchpad, APC)."""

from typing import List, Dict, Optional

# Camelot Wheel: major/minor key mapping
_CAMELOT_WHEEL = {
    f"{i}{mode}": (
        f"{i}{'A' if mode == 'B' else 'B'}",
        f"{(i % 12) + 1}{mode}",
        f"{(i - 2) % 12 + 1}{mode}",
    )
    for i in range(1, 13)
    for mode in ["A", "B"]
}

# MIDI note to note name
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def generate_camelot_grid(device: str, key: str) -> List[List[Dict]]:
    """
    Generate grid layout for Camelot Wheel (harmonic mixing).

    Args:
        device: "Push", "Launchpad", "APC"
        key: Active key (e.g., "8A", "12B")

    Returns:
        Grid cells: [
            [{"label": "8A", "active": True, "color": "red"}, ...],
            ...
        ]
    """
    # Device-specific dimensions
    grids = {
        "Push": (8, 8),  # 8x8 RGB grid
        "Launchpad": (8, 8),  # 8x8 RGB grid
        "APC": (4, 8),  # 4x8 drum pad grid
    }
    rows, cols = grids.get(device, (8, 8))

    # Position active key in center
    center_row, center_col = rows // 2, cols // 2
    grid = []

    for i in range(rows):
        row = []
        for j in range(cols):
            cell = {"label": "", "active": False, "color": "black"}

            # Position calculation for adjacent keys
            if (i, j) == (center_row, center_col):
                cell["label"] = key
                cell["active"] = True
                cell["color"] = "red"
            elif (i, j) in [
                (center_row - 1, center_col),
                (center_row + 1, center_col),
                (center_row, center_col - 1),
            ]:
                # One-hour up, down, relative
                compass_dir = ["one_up", "one_down", "relative"][
                    [
                        (center_row - 1, center_col),
                        (center_row + 1, center_col),
                        (center_row, center_col - 1),
                    ].index((i, j))
                ]

                rel_key, down_key, up_key = _CAMELOT_WHEEL.get(key, ("", ""))
                key_map = {"one_up": up_key, "one_down": down_key, "relative": rel_key}
                if key_map[compass_dir]:
                    cell["label"] = key_map[compass_dir]
                    cell["color"] = "yellow"

            row.append(cell)
        grid.append(row)

    return grid


def generate_chromatic_grid(device: str, root: int = 60) -> List[List[Dict]]:
    """
    Generate chromatic scale grid.

    Args:
        device: "Launchpad", "Push"
        root: MIDI root note (60 = C4)

    Returns:
        Grid cells: [
            [{"midi_note": 60, "note_name": "C", "color": "blue"}, ...],
            ...
        ]
    """
    grids = {
        "Launchpad": (8, 8),
        "Push": (8, 8),
    }
    rows, cols = grids.get(device, (8, 8))

    grid = []
    for i in range(rows):
        row = []
        for j in range(cols):
            midi_note = root + (i * cols) + j
            if midi_note <= 127:
                note_index = midi_note % 12
                note_name = _NOTE_NAMES[
                    note_index
                ]  # Single octave display for Launchpad/Push
                cell = {"midi_note": midi_note, "note_name": note_name, "color": "blue"}
            else:
                cell = {"midi_note": -1, "note_name": "", "color": "black"}
            row.append(cell)
        grid.append(row)

    return grid


def generate_drum_grid(device: str, kit: str = "techno") -> List[List[Dict]]:
    """
    Generate drum pad layout.

    Args:
        device: "APC"
        kit: "techno", "house", "dub", "hiphop"

    Returns:
        Grid cells: [
            [{"sound": "kick", "midi_note": 36, "color": "red"}, ...],
            ...
        ]
    """
    # APC Mini has 4x8 drum pads
    rows, cols = 4, 8

    # Kit layouts differ in placement but share same mapping
    drum_kits = {
        "techno": [("kick", 36), ("snare", 40), ("hat", 42), ("clap", 39)],
        "house": [("kick", 36), ("snare", 40), ("rim", 41), ("hat", 44)],
    }

    kit_layout = dict(drum_kits.get(kit, drum_kits["techno"]))

    grid = []
    for i in range(rows):
        row = []
        for j in range(cols):
            # Default to kick/snare/hat/percussion based on position
            sound_keys = ["kick", "snare", "hat", "perc"]
            cell_sound = "perc"  # fallback

            if i == 0 and j == 0:
                cell_sound = "kick"
                midi_note = kit_layout.get("kick", 36)
            elif i == 0 and j == 1:
                cell_sound = "snare"
                midi_note = kit_layout.get("snare", 40)
            elif i == 1 and j == 0:
                cell_sound = "hat"
                midi_note = kit_layout.get("hat", 44)
            else:
                midi_note = 40 + (i * cols + j)  # Generic percussion default

            cell = {
                "sound": cell_sound,
                "midi_note": midi_note,
                "color": {"kick": "red", "snare": "orange", "hat": "yellow"}.get(
                    cell_sound, "green"
                ),
            }
            row.append(cell)
        grid.append(row)

    return grid
