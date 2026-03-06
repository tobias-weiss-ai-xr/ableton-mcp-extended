# Music Theory Toolkit
#
# Comprehensive music theory resources for Ableton MCP Extended
#
## Modules
#
# - chord.py - Chord naming and construction
# - progression.py - Chord progression analysis
# - voicing.py - Chord voicing generation
# - arpeggiator.py - Arpeggiation utilities
# - grid.py - Controller grid layouts
# - extensions.py - Extended chords (9ths, 11ths, 13ths, altered)
# - exotic_scales.py - Exotic scale definitions
# - harmonization.py - Melody harmonization utilities
# - polyrhythm.py - Polyrhythm and tuplet generators
# - composition_utils.py - Composition and arrangement utilities
#
## Usage
#
# ```python
# from music_theory.chord import generate_chord_name
# from music_theory.voicing import generate_voicing
# from music_theory.extensions import create_extended_chord
# from music_theory.exotic_scales import generate_exotic_scale_notes
# from music_theory.composition_utils import generate_melody, get_arrangement_sections
# ```

# Export main functions for convenience
from .chord import generate_chord_name, _NOTE_NAMES, _CHORD_QUALITIES
from .progression import analyze_progression, _PROGRESSION_PATTERNS
from .voicing import generate_voicing, VOICING_TEMPLATES
from .arpeggiator import arpeggiate_chord
from .grid import generate_camelot_grid, generate_chromatic_grid, generate_drum_grid
from .composition_utils import (
    generate_melody,
    generate_bass_line,
    generate_arp_pattern,
    generate_variation,
    get_arrangement_sections,
    ARRANGEMENT_TEMPLATES,
)

__all__ = [
    # Chord
    "generate_chord_name",
    "_NOTE_NAMES",
    "_CHORD_QUALITIES",
    # Progression
    "analyze_progression",
    "_PROGRESSION_PATTERNS",
    # Voicing
    "generate_voicing",
    "VOICING_TEMPLATES",
    # Arpeggiator
    "arpeggiate_chord",
    # Grid
    "generate_camelot_grid",
    "generate_chromatic_grid",
    "generate_drum_grid",
    # Composition
    "generate_melody",
    "generate_bass_line",
    "generate_arp_pattern",
    "generate_variation",
    "get_arrangement_sections",
    "ARRANGEMENT_TEMPLATES",
]

