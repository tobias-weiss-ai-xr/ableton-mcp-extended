# Sprint 04: Composition Tools (Chord Progressions + Melody)

**Theme:** Make the AI a useful co-writer with generative music tools.
**Est. days:** 5 | **New tools:** 4-5 | **Risk:** Medium
**Dependencies:** None

## Goal
Add generative composition tools that create chord progressions, melodies, and handle scale-aware MIDI operations. These are the atomic units that the songwriter workflow (Sprint 05) will orchestrate.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/composition_tools.py` | Create | register_composition_tools(): 4-5 generative tools |
| `MCP_Server/composition.py` | Create | Core music theory engine (scales, chords, progressions, Markov melody) |
| `MCP_Server/server.py` | Modify | Import + register composition tools |
| `AbletonMCP_Remote_Script/__init__.py` | Modify | Add scaling/quantize handler |
| `MCP_Server/knowledge/scales.json` | Create | All 12 major + 12 minor + modes scale definitions |
| `MCP_Server/knowledge/chord_templates.json` | Create | Genre-based chord progression templates |
| `tests/test_composition.py` | Create | Unit tests for music theory engine |
| `tests/test_composition_tools.py` | Create | Tool registration + integration tests |

## Deliverables

### 4.1 Music Theory Engine (`composition.py`)

**Scales module:**
- `SCALE_DEFINITIONS` dict: all 12 major, 12 natural minor, 12 harmonic minor, 12 melodic minor, modes
- `get_scale_notes(key: str, scale: str) -> list[int]` — returns MIDI note numbers in scale
- `is_note_in_scale(note: int, key: str, scale: str) -> bool`
- `snap_to_scale(note: int, key: str, scale: str) -> int` — nearest scale tone

**Chords module:**
- `get_chord_notes(root: int, chord_type: str) -> list[int]` — returns MIDI notes
  - chord_types: "maj", "min", "dim", "aug", "sus2", "sus4", "7", "maj7", "min7", "dim7", "m7b5"
- `get_chord_name(notes: list[int]) -> str` — detect chord from note set (basic)
- `PROGRESSIONS` dict per genre:
  - techno: [i, vii, vi, v], [i, v, vi, iv], [i, iv, vii, i]
  - house: [I, vi, IV, V], [I, IV, V, IV]
  - dub: [i, iv, v], [i, vii, VI, v]
  - pop: [I, V, vi, IV], [vi, IV, I, V]
  - ambient: [I, III, vi, IV], [I, ii, vi, V]

**Markov Melody Generator:**
- `generate_melody(key: str, scale: str, bars: int, complexity: float = 0.5) -> list[dict]`
  - Returns list of dicts: `{pitch, start_time, duration, velocity}`
  - Uses Markov chain weighted toward scale tones
  - `complexity` (0.0-1.0) controls: note density, interval size, rhythmic variety
  - Default note grid: 16th notes
  - Range: 2 octaves around key center (C3-C5)
  - Avoids large jumps (> 5 semitones) unless complexity > 0.8

### 4.2 Composition Tools (`composition_tools.py`)

Follows `register_composition_tools(mcp, get_ableton_connection)` pattern.

**Tool: `generate_chord_progression`**
```
(ctx, key: str = "C", scale: str = "minor", genre: str = "techno",
 length: int = 4, bars_per_chord: int = 4, octave: int = 3) -> str
```
- Returns JSON: chords with MIDI notes + creates MIDI clip on a track
- Creates new MIDI track if no track specified
- Each chord spans `bars_per_chord` bars
- `length` = number of chords

**Tool: `generate_melody`**
```
(ctx, key: str = "C", scale: str = "minor", bars: int = 8,
 complexity: float = 0.5, track_index: int = None, clip_index: int = 0) -> str
```
- If track_index provided, adds notes to existing clip
- If not, creates new MIDI track + clip
- Returns JSON: melody notes + clip info

**Tool: `quantize_to_scale`**
```
(ctx, track_index: int, clip_index: int, key: str = "C",
 scale: str = "minor") -> str
```
- Snaps every MIDI note in clip to nearest scale tone
- Returns count of notes moved
- Non-MIDI clips return error

**Tool: `analyze_chord`**
```
(ctx, track_index: int, clip_index: int, bar_start: int = 0) -> str
```
- Analyzes MIDI notes in a bar
- Returns detected chord name + confidence + notes found
- Returns "Unknown" if notes don't form a recognizable chord

**Tool: `generate_bassline`**
```
(ctx, key: str = "C", scale: str = "minor", bars: int = 4,
 track_index: int = None) -> str
```
- Generates bassline following root notes of implied chords
- Root-octave-root pattern with passing tones
- Creates new MIDI track + clip if no track

### 4.3 Remote Script Handler
Add `_quantize_to_scale(track_index, clip_index, scale_notes: list[int])` in `__init__.py`:
- Iterates all MIDI notes in clip
- Snaps pitch to nearest value in `scale_notes`
- Returns count of modified notes

### 4.4 Knowledge Files
**`scales.json`**:
```json
{
  "major": {"intervals": [0, 2, 4, 5, 7, 9, 11], "modes": ["ionian", "dorian", ...]},
  "minor": {"intervals": [0, 2, 3, 5, 7, 8, 10], "harmonic_minor": [...], ...}
}
```

**`chord_templates.json`**:
```json
{
  "techno": [{"progression": [0, 6, 5, 4], "description": "Minor descending"}],
  "house": [{"progression": [0, 5, 3, 4], "description": "Classic house"}]
}
```

## API Surface

### New Tools
| Tool | Signature | Returns |
|------|-----------|---------|
| `generate_chord_progression` | (key, scale, genre, length, bars_per_chord, octave) | JSON chords + clip |
| `generate_melody` | (key, scale, bars, complexity, track_index, clip_index) | JSON melody + clip |
| `quantize_to_scale` | (track_index, clip_index, key, scale) | Notes modified count |
| `analyze_chord` | (track_index, clip_index, bar_start) | Chord name + confidence |
| `generate_bassline` | (key, scale, bars, track_index) | JSON bassline + clip |

## Acceptance Criteria
```bash
python -c "
from MCP_Server.composition import get_scale_notes, snap_to_scale, generate_melody
notes = get_scale_notes('C', 'major')
assert len(notes) == 7 and min(notes) >= 60
assert snap_to_scale(61, 'C', 'major') == 60  # F# → F in C major

melody = generate_melody('A', 'minor', 4, complexity=0.5)
assert len(melody) > 0
assert all('pitch' in n and 'start_time' in n for n in melody)
print('Music theory engine OK')
"
```

```bash
grep -c "def generate_chord_progression\|def generate_melody\|def quantize_to_scale\|def analyze_chord\|def generate_bassline" MCP_Server/composition_tools.py
# 5 tools defined
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Generated melodies sound bad | Medium | Use music theory constraints (voicing, range, stepwise motion bias) |
| Chord detection is inaccurate | Medium | Return confidence score; fall back to "Unknown" |
| Scale quantization destroys intentional chromaticism | Low | Document: "only for rough sketches" |
| Performance issues with large note sets | Low | Limit to 256 notes per quantize call |

## Must NOT Do
- Do NOT attempt key detection from audio (that's Sprint 06)
- Do NOT add external music theory libraries (stdlib + music theory knowledge only)
- Do NOT generate audio (MIDI only — usable with any instrument)
- Do NOT add ML-based generation — use deterministic music theory
