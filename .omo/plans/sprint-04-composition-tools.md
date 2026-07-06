# sprint-04-composition-tools - Work Plan

## TL;DR (For humans)

**What you'll get:** Your AI co-writer gains generative music superpowers — chord progressions in any genre, Markov-chain melodies that don't suck, scale-aware MIDI quantization that fixes wrong notes automatically, chord detection ("what chord is that clip playing?"), and root-note basslines that follow the harmony. Five new MCP tools backed by a deterministic music theory engine (no ML, no audio, no external libraries).

**Why this approach:** Pure music theory + deterministic algorithms = reliable, predictable output that the Songwriter workflow (Sprint 05) can orchestrate as atomic building blocks. The Markov melody generator uses weighted scale-tone transitions and contextual constraints (no big jumps unless complexity demands it) so results are musical by default. Chord detection returns confidence scores so agents know when to trust it. Scale quantization is intentionally destructive (documented as "rough sketch only") to avoid false expectations.

**What it will NOT do:** Detect keys from audio (Sprint 06), use external music theory libraries, generate audio (MIDI only), or use ML/deep learning — everything is deterministic music theory.

**Effort:** Medium (5 days, 5 new tools, ~4 new files, 2 modified files)
**Risk:** Medium — generated content quality is subjective; music theory constraints mitigate the worst sounds
**Decisions to sanity-check:** Genre progression templates (are these musically correct?), Markov chain parameters (complexity scaling), chord detection confidence threshold

Your next move: Approve this plan, then run `$start-work` to begin execution.

---

> TL;DR (machine): Med effort, Med risk (subjective quality). 8 deliverables across 3 parallel waves. Wave 1 (Foundation): music theory engine + knowledge files. Wave 2 (Infrastructure): Remote Script handler + composition tools (5 tools). Wave 3 (Integration): server registration + tests.

## Scope
### Must have
- Music theory engine (`composition.py`): scale definitions (all 12 major/minor + modes), note-in-scale checking, snap-to-scale, chord note computation (11 chord types), chord name detection, genre-based progression templates (5 genres), Markov melody generator with complexity control
- Composition tools (`composition_tools.py`): 5 MCP tools — `generate_chord_progression`, `generate_melody`, `quantize_to_scale`, `analyze_chord`, `generate_bassline` — registered via `register_composition_tools(mcp, get_ableton_connection)`
- Remote Script handler: `_quantize_to_scale(track_index, clip_index, scale_notes)` in `__init__.py` that snaps MIDI notes to a provided scale note set
- Knowledge files: `scales.json` (interval definitions for all scales/modes) + `chord_templates.json` (genre-specific chord progression templates)
- Server integration: import + register composition tools in `server.py`
- Unit tests for music theory engine: scale functions, chord functions, melody generation
- Integration tests for tool registration: all 5 tools registered, proper signatures

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT attempt key detection from audio — that's Sprint 06
- Do NOT add external music theory libraries (stdlib + hand-coded knowledge only; no `music21`, `mingus`, etc.)
- Do NOT generate audio — MIDI only, usable with any instrument
- Do NOT add ML-based generation — deterministic music theory only (Markov chains are math, not ML)
- Do NOT create new TCP/UDP commands — tools call existing Remote Script handlers for clip/track operations
- Do NOT exceed 256 notes per quantize call (performance guard)
- Do NOT modify existing tool bodies in server.py
- Do NOT add new pip dependencies
- Do NOT modify LSP server configuration

## Verification strategy
> Zero human intervention — all verification is agent-executed.
- Test decision: tests-after + static analysis for each wave
- Evidence: `.omo/evidence/task-<N>-sprint-04-composition-tools.<ext>`

## Execution strategy
### Parallel execution waves
| Wave | Focus | Todos | Est. days |
|------|-------|-------|-----------|
| 1 | Music theory engine + Knowledge files | 1, 2, 3 | 2 |
| 2 | Remote Script handler + Composition tools | 4, 5, 6 | 2 |
| 3 | Server registration + Tests | 7, 8 | 1 |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Music theory engine — scales | None | 2, 5 | 3 |
| 2. Music theory engine — chords & melody | 1 | 5 | 3 |
| 3. Knowledge files (scales.json, chord_templates.json) | None | None | 1, 2 |
| 4. Remote Script quantize handler | None | 6 | 1, 2, 3 |
| 5. Composition tools (all 5 MCP tools) | 1, 2 | 7 | 4 |
| 6. quantize_to_scale + analyze_chord tools | 4 | 7 | 5 |
| 7. Server.py import + registration | 5, 6 | 8 | None |
| 8. Unit + integration tests | 1, 2, 3, 4, 5, 6, 7 | None | None |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [ ] 1. Music theory engine — scales module
  What to do / Must NOT do:
  Create `MCP_Server/composition.py` with the scales module:
  
  `SCALE_DEFINITIONS` dict covering:
  - 12 major scales (intervals: `[0, 2, 4, 5, 7, 9, 11]`)
  - 12 natural minor scales (intervals: `[0, 2, 3, 5, 7, 8, 10]`)
  - 12 harmonic minor scales (intervals: `[0, 2, 3, 5, 7, 8, 11]`)
  - 12 melodic minor scales (intervals: `[0, 2, 3, 5, 7, 9, 11]`)
  - Modes for each scale: ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian
  
  Functions:
  - `get_scale_notes(key: str, scale: str = "major") -> list[int]` — returns MIDI note numbers (C3-C5 range, 48-84) that belong to the scale. Key can be note name with optional accidental (e.g., "C", "F#", "Bb"). Raises `ValueError` for invalid key names or scale names.
  - `is_note_in_scale(note: int, key: str, scale: str = "major") -> bool`
  - `snap_to_scale(note: int, key: str, scale: str = "major") -> int` — snaps to nearest scale tone; if equidistant, snaps up
  - `NOTE_TO_MIDI` / `MIDI_TO_NOTE` utility dicts for note name <-> number conversion
  
  Must NOT: Use external music theory libraries. Must NOT hardcode all 12 keys for each scale type (compute from the interval pattern + root note). Must use note name parsing that handles sharps (#) and flats (b) correctly — `C#` = 61, `Db` = 61.
  
  Parallelization: Wave 1 | Blocked by: None | Blocks: 2, 5
  References:
  - MIDI note numbering: C0=12, C1=24, ..., C3=48, C4=60 (middle C), C5=72
  - Interval patterns: major `[0,2,4,5,7,9,11]`, natural minor `[0,2,3,5,7,8,10]`
  - Note name parsing: split on `b`/`#`, use semitone offsets from natural
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.composition import get_scale_notes, is_note_in_scale, snap_to_scale, NOTE_TO_MIDI
  
  # C major = C D E F G A B = notes 60,62,64,65,67,69,71
  notes = get_scale_notes('C', 'major')
  assert len(notes) == 7, f'Expected 7 notes, got {len(notes)}'
  assert 60 in notes and 64 in notes and 71 in notes, 'C major notes missing'
  assert notes[0] == 60 and notes[-1] == 71, 'C major range wrong'
  
  # F# is not in C major (C major has F natural)
  assert not is_note_in_scale(65, 'C', 'major'), 'F should not be in C major'
  assert is_note_in_scale(64, 'C', 'major'), 'E should be in C major'
  
  # snap: F# (66) is equidistant between F (65) and G (67) in C major — snaps up to G
  assert snap_to_scale(66, 'C', 'major') == 67, 'F# should snap to G in C major'
  
  # Bb (70) snaps to A (69) in C major (B is natural = 71, A = 69)
  assert snap_to_scale(70, 'C', 'major') == 69 or snap_to_scale(70, 'C', 'major') == 71, 'Bb should snap to A or B'
  
  # F# minor has F#, G#, A, B, C#, D, E
  fs_minor = get_scale_notes('F#', 'minor')
  assert 66 in fs_minor, 'F# should be in F# minor'
  assert 71 in fs_minor, 'B should be in F# minor'
  
  print('Scales module OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: get_scale_notes("C", "major") returns [60, 62, 64, 65, 67, 69, 71]
  - HAPPY: get_scale_notes("A", "minor") returns [57, 59, 60, 62, 64, 65, 67] (A natural minor)
  - HAPPY: snap_to_scale(61, "C", "major") returns 60 (C# → C in C major)
  - HAPPY: get_scale_notes("F#", "harmonic_minor") includes F#, G#, A, B, C#, D, E##
  - FAILURE: get_scale_notes("X", "major") raises ValueError for invalid key
  - FAILURE: get_scale_notes("C", "nonexistent") raises ValueError for invalid scale
  - FAILURE: snap_to_scale(-1, "C", "major") raises ValueError for out-of-range
  Evidence: .omo/evidence/task-1-sprint-04-composition-tools.txt
  Commit: Y | feat(composition): add scales module with get_scale_notes, is_note_in_scale, snap_to_scale

- [ ] 2. Music theory engine — chords, progressions & melody generator
  What to do / Must NOT do:
  Add to `MCP_Server/composition.py` the chords module and Markov melody generator:
  
  **Chords module:**
  - `get_chord_notes(root: int, chord_type: str = "maj") -> list[int]` — returns MIDI notes for a chord
    - chord_types: "maj", "min", "dim", "aug", "sus2", "sus4", "7", "maj7", "min7", "dim7", "m7b5"
    - Intervals: maj=[0,4,7], min=[0,3,7], dim=[0,3,6], aug=[0,4,8], sus2=[0,2,7], sus4=[0,5,7], 7=[0,4,7,10], maj7=[0,4,7,11], min7=[0,3,7,10], dim7=[0,3,6,9], m7b5=[0,3,6,10]
  - `get_chord_name(notes: list[int]) -> tuple[str, float]` — detects chord from note set, returns (name, confidence 0.0-1.0)
    - Compares against all chord types, picks best match
    - Confidence = ratio of matching notes to total chord notes
    - Returns `("Unknown", 0.0)` if no match above 0.5 threshold
    - Handles inversions (any octave of the same pitch class)
  - `PROGRESSIONS` dict per genre with scale-degree sequences:
    ```python
    PROGRESSIONS = {
        "techno": [
            {"progression": [0, 6, 5, 4], "description": "Minor descending"},
            {"progression": [0, 5, 6, 4], "description": "Dark minimal"},
            {"progression": [0, 4, 6, 5], "description": "Tension builder"},
        ],
        "house": [
            {"progression": [0, 5, 3, 4], "description": "Classic house"},
            {"progression": [0, 4, 5, 4], "description": "Looping house"},
        ],
        "dub": [
            {"progression": [0, 3, 4], "description": "One drop roots"},
            {"progression": [0, 6, 5, 4], "description": "Dub minor"},
        ],
        "pop": [
            {"progression": [0, 5, 3, 4], "description": "I-V-vi-IV"},
            {"progression": [3, 4, 0, 5], "description": "vi-IV-I-V"},
        ],
        "ambient": [
            {"progression": [0, 2, 3, 4], "description": "Dreamy ascent"},
            {"progression": [0, 1, 3, 5], "description": "Gentle wander"},
        ],
    }
    ```
  - `get_progression_notes(key: str, scale: str, genre: str, length: int, bars_per_chord: int, octave: int = 3) -> list[dict]`
    - Returns list: `[{root, chord_type, notes: [midi_ints], start_bar, duration_bars}]`
    - Picks a progression template matching `length` (or nearest), transposes to key
    - Default octave = 3 (C3=48..B3=59)
  
  **Markov Melody Generator:**
  - `generate_melody(key: str, scale: str = "minor", bars: int = 4, complexity: float = 0.5, rng_seed: int = None) -> list[dict]`
    - Returns list of dicts: `{pitch: int, start_time: float, duration: float, velocity: int}`
    - Uses a Markov chain with transition matrix weighted toward scale tones
      - Scale tones: high transition probability (0.7 baseline)
      - Non-scale tones: zero probability (melody stays in scale)
      - Stepwise motion (interval of 1-2 semitones): high probability
      - Leaps (>5 semitones): only allowed when complexity > 0.8
    - `complexity` (0.0-1.0) controls:
      - Note density: 0.0 = quarter notes, 0.5 = 8th notes, 1.0 = 16th notes
      - Interval size: 0.0 = mostly steps, 1.0 = allows leaps
      - Rhythmic variety: 0.0 = uniform grid, 1.0 = syncopated
    - Range: 2 octaves around key center (C3=48 to C5=72)
    - Default note grid: 16th notes (time quantized to 0.25 beat)
    - `rng_seed` for reproducible output (uses `random.seed`)
  
  Must NOT: Use any ML libraries. Must not use `random` for cryptographic purposes. Must not produce notes outside MIDI range [0, 127].
  
  Parallelization: Wave 1 | Blocked by: 1 | Blocks: 5
  References:
  - Chord interval formulas: https://en.wikipedia.org/wiki/Chord_(music)
  - MIDI note numbering: root=60 is middle C
  - Markov chain transition matrix: 2D dict `{current_pitch: {next_pitch: probability}}`
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.composition import get_chord_notes, get_chord_name, get_progression_notes, generate_melody
  
  # Test chord notes
  c_maj = get_chord_notes(60, 'maj')
  assert c_maj == [60, 64, 67], f'C major should be [60,64,67], got {c_maj}'
  
  c_min7 = get_chord_notes(60, 'min7')
  assert c_min7 == [60, 63, 67, 70], f'C min7 should be [60,63,67,70], got {c_min7}'
  
  # Test chord detection
  name, conf = get_chord_name([60, 64, 67])
  assert 'maj' in name.lower() or name == 'Unknown', f'Expected major chord, got {name}'
  assert conf > 0.5, f'Confidence should be > 0.5, got {conf}'
  
  name, conf = get_chord_name([60, 63, 67])
  assert 'min' in name.lower() or name == 'Unknown'
  
  # Test progression
  prog = get_progression_notes('C', 'major', 'pop', 4, 4, octave=3)
  assert len(prog) == 4, f'Expected 4 chords, got {len(prog)}'
  assert all(len(c['notes']) > 0 for c in prog), 'All chords should have notes'
  assert all('start_bar' in c for c in prog), 'Each chord needs start_bar'
  
  # Test melody generation
  melody = generate_melody('A', 'minor', 4, complexity=0.5, rng_seed=42)
  assert len(melody) > 0, 'Melody should have notes'
  assert all('pitch' in n and 'start_time' in n and 'duration' in n and 'velocity' in n for n in melody), 'Melody notes missing fields'
  
  # Reproducibility with same seed
  melody2 = generate_melody('A', 'minor', 4, complexity=0.5, rng_seed=42)
  assert melody == melody2, 'Same seed should produce same melody'
  
  print('Chords + progressions + melody module OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: get_chord_notes(60, "maj7") returns [60, 64, 67, 71]
  - HAPPY: get_chord_notes(65, "dim") returns [65, 68, 71]
  - HAPPY: get_chord_name([60, 63, 67, 70]) returns ("C min7", ~1.0)
  - HAPPY: get_progression_notes("C", "major", "pop", 4, 4) returns 4 chords with 4-bar durations
  - HAPPY: generate_melody("C", "major", 8, complexity=0.2) returns sparse, stepwise melody
  - HAPPY: generate_melody("C", "major", 8, complexity=0.9) returns dense, varied melody
  - FAILURE: get_chord_notes(200, "maj") raises ValueError for out-of-range root
  - FAILURE: get_chord_name([]) returns ("Unknown", 0.0)
  - FAILURE: get_progression_notes("C", "major", "invalid_genre", 4, 4) falls back to pop progression
  - FAILURE: generate_melody("C", "major", -1) raises ValueError for negative bars
  Evidence: .omo/evidence/task-2-sprint-04-composition-tools.txt
  Commit: Y | feat(composition): add chords module with detection, progressions, and Markov melody generator

- [ ] 3. Knowledge files (scales.json + chord_templates.json)
  What to do / Must NOT do:
  Create `MCP_Server/knowledge/scales.json`:
  ```json
  {
    "major": {"intervals": [0, 2, 4, 5, 7, 9, 11], "modes": ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]},
    "minor": {"intervals": [0, 2, 3, 5, 7, 8, 10], "modes": ["aeolian"]},
    "harmonic_minor": {"intervals": [0, 2, 3, 5, 7, 8, 11], "modes": []},
    "melodic_minor": {"intervals": [0, 2, 3, 5, 7, 9, 11], "modes": []},
    "dorian": {"intervals": [0, 2, 3, 5, 7, 9, 10], "parent": "major", "mode_index": 1},
    "phrygian": {"intervals": [0, 1, 3, 5, 7, 8, 10], "parent": "major", "mode_index": 2},
    "lydian": {"intervals": [0, 2, 4, 6, 7, 9, 11], "parent": "major", "mode_index": 3},
    "mixolydian": {"intervals": [0, 2, 4, 5, 7, 9, 10], "parent": "major", "mode_index": 4},
    "locrian": {"intervals": [0, 1, 3, 5, 6, 8, 10], "parent": "major", "mode_index": 6}
  }
  ```
  
  Create `MCP_Server/knowledge/chord_templates.json`:
  ```json
  {
    "techno": [
      {"progression": [0, 6, 5, 4], "description": "Minor descending"},
      {"progression": [0, 5, 6, 4], "description": "Dark minimal"},
      {"progression": [0, 4, 6, 5], "description": "Tension builder"},
      {"progression": [0, 6, 5, 4, 0, 6, 5, 4], "description": "8-bar repetition"}
    ],
    "house": [
      {"progression": [0, 5, 3, 4], "description": "Classic house I-V-vi-IV"},
      {"progression": [0, 4, 5, 4], "description": "Looping house I-vi-V-vi"},
      {"progression": [0, 4, 5, 3], "description": "Anthemic house"}
    ],
    "dub": [
      {"progression": [0, 3, 4], "description": "One drop roots"},
      {"progression": [0, 6, 5, 4], "description": "Dub minor"},
      {"progression": [0, 5, 6, 4], "description": "Dub tension"}
    ],
    "pop": [
      {"progression": [0, 5, 3, 4], "description": "I-V-vi-IV (Axis of Awesome)"},
      {"progression": [3, 4, 0, 5], "description": "vi-IV-I-V"},
      {"progression": [0, 4, 5, 4], "description": "I-vi-V-vi"},
      {"progression": [0, 5, 4, 3], "description": "I-V-vi-IV variation"}
    ],
    "ambient": [
      {"progression": [0, 2, 3, 4], "description": "Dreamy ascent"},
      {"progression": [0, 1, 3, 5], "description": "Gentle wander"},
      {"progression": [0, 2, 5, 1], "description": "Suspended drift"}
    ]
  }
  ```
  
  Also create `MCP_Server/knowledge/__init__.py` with a simple loader:
  ```python
  import json, os
  _dir = os.path.dirname(__file__)
  SCALES = json.load(open(os.path.join(_dir, "scales.json")))
  CHORD_TEMPLATES = json.load(open(os.path.join(_dir, "chord_templates.json")))
  ```
  
  Must NOT: Include any code beyond JSON data + simple loader. Must use valid JSON (double quotes, no trailing commas).
  
  Parallelization: Wave 1 | Blocked by: None | Blocks: None
  References:
  - Scale interval patterns: standard music theory
  - Genre progressions: derived from common electronic/pop music patterns
  - Existing knowledge dir: `MCP_Server/knowledge/` (check if exists, create if not)
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import json
  with open('MCP_Server/knowledge/scales.json') as f:
      scales = json.load(f)
  assert 'major' in scales, 'major scale missing'
  assert 'minor' in scales, 'minor scale missing'
  assert 'harmonic_minor' in scales, 'harmonic_minor missing'
  assert 'melodic_minor' in scales, 'melodic_minor missing'
  assert 'dorian' in scales, 'dorian mode missing'
  assert scales['major']['intervals'] == [0, 2, 4, 5, 7, 9, 11], 'major intervals wrong'
  assert len(scales['major']['modes']) == 7, 'should have 7 modes'
  
  with open('MCP_Server/knowledge/chord_templates.json') as f:
      templates = json.load(f)
  assert 'techno' in templates, 'techno missing'
  assert 'house' in templates, 'house missing'
  assert 'dub' in templates, 'dub missing'
  assert 'pop' in templates, 'pop missing'
  assert 'ambient' in templates, 'ambient missing'
  assert len(templates['techno']) >= 2, 'techno should have >= 2 progressions'
  assert all('progression' in p for p in templates['house']), 'all progressions need degree list'
  assert all('description' in p for p in templates['house']), 'all progressions need description'
  
  from MCP_Server.knowledge import SCALES, CHORD_TEMPLATES
  assert len(SCALES) >= 8, 'SCALES should have >= 8 entries'
  assert len(CHORD_TEMPLATES) == 5, 'CHORD_TEMPLATES should have 5 genres'
  print('Knowledge files OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: scales.json loads as valid JSON, all 8+ scale/mode definitions present
  - HAPPY: chord_templates.json loads as valid JSON, all 5 genres present with progressions
  - HAPPY: `from MCP_Server.knowledge import SCALES` works
  - FAILURE: scales.json with invalid JSON raises json.decoder.JSONDecodeError
  Evidence: .omo/evidence/task-3-sprint-04-composition-tools.txt
  Commit: Y | feat(knowledge): add scales.json and chord_templates.json with genre progressions

- [ ] 4. Remote Script quantize handler
  What to do / Must NOT do:
  Add `_quantize_to_scale` handler to `AbletonMCP_Remote_Script/__init__.py`:
  ```python
  def _quantize_to_scale(self, params):
      \"\"\"Snap MIDI notes in a clip to nearest scale tones.
      params: {track_index, clip_index, scale_notes: [int]}
      Returns: {notes_modified: int, total_notes: int}
      \"\"\"
      track_index = int(params['track_index'])
      clip_index = int(params['clip_index'])
      scale_notes = [int(n) for n in params['scale_notes']]  # list of valid MIDI note numbers
      
      track = self.song.tracks[track_index]
      clip_slot = track.clip_slots[clip_index]
      if not clip_slot.has_clip:
          return {'error': 'No clip at specified index'}
      clip = clip_slot.clip
      if not clip.is_midi_clip:
          return {'error': 'Clip is not a MIDI clip'}
      
      notes = clip.get_notes(0, 0, 100000, 127)
      modified = 0
      new_notes = []
      for note in notes:
          if note.pitch not in scale_notes:
              # Snap to nearest scale tone
              nearest = min(scale_notes, key=lambda x: (abs(x - note.pitch), x))
              note.pitch = nearest
              modified += 1
          new_notes.append(note)
      
      clip.replace_notes_extended(0, clip.length, notes, False) if modified > 0 else None
      return {'notes_modified': modified, 'total_notes': len(notes)}
  ```
  
  Add to command dispatch dict (find the existing pattern and add a `"quantize_to_scale"` entry pointing to this handler).
  
  Must NOT: Modify existing handlers. Must NOT exceed 256 notes per call (add early return if len(notes) > 256 with warning). Must use `clip.replace_notes_extended` for the replacement — NOT `clip.replace_notes` (the latter is deprecated in Live 12).
  
  Parallelization: Wave 2 | Blocked by: None | Blocks: 6
  References:
  - Existing handler pattern: `AbletonMCP_Remote_Script/__init__.py` — look for existing `def _get_*` methods
  - Command dispatch: look for dict mapping command strings to handler methods
  - Live API: `Clip.get_notes(start_pitch, start_time, pitch_span, time_span)` returns tuple of Note objects
  - Live API: `Clip.replace_notes_extended(start_time, duration, notes, remove_existing)`
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('AbletonMCP_Remote_Script/__init__.py') as f:
      content = f.read()
  assert 'def _quantize_to_scale' in content, '_quantize_to_scale handler not found'
  assert 'scale_notes' in content, 'scale_notes parameter missing'
  assert 'clip.replace_notes_extended' in content or 'replace_notes' in content, 'note replacement missing'
  assert \"'quantize_to_scale'\" in content or '\"quantize_to_scale\"' in content, 'command dispatch entry missing'
  print('Remote Script quantize handler registered')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Clip has notes {60,61,64}, scale_notes=[60,62,64,65,67,69,71], 61→62 (C#→D), 1 note modified
  - HAPPY: Clip has notes {60,64,67}, scale_notes=[60,62,64,65,67,69,71], 0 notes modified (all in scale)
  - FAILURE: clip_index with no clip, returns `{'error': 'No clip at specified slot'}`
  - FAILURE: audio track clip, returns `{'error': 'Clip is not a MIDI clip'}`
  - FAILURE: 300 notes in clip, returns warning about 256-note limit, processes first 256
  Evidence: .omo/evidence/task-4-sprint-04-composition-tools.txt
  Commit: Y | feat(remote-script): add _quantize_to_scale handler for MIDI note scale snapping

- [ ] 5. Composition tools — chord_progression, melody & bassline generators
  What to do / Must NOT do:
  Create `MCP_Server/composition_tools.py` with 3 generative tools:
  
  ```python
  def register_composition_tools(mcp, get_ableton_connection):
      \"\"\"Register composition tools with the MCP server.\"\"\"
      
      @server.tool
      def generate_chord_progression(ctx, key: str = "C", scale: str = "minor", genre: str = "techno",
                                      length: int = 4, bars_per_chord: int = 4, octave: int = 3,
                                      track_index: int = None) -> str:
          \"\"\"Generate a chord progression and create/update a MIDI clip.\"\"\"
          ...implementation...
  ```
  
  **Tool: `generate_chord_progression`**
  - Calls `get_progression_notes(key, scale, genre, length, bars_per_chord, octave)`
  - If `track_index` is None: creates new MIDI track via `create_midi_track(len(self.song.tracks))`, gets its index
  - Creates MIDI clip of `length * bars_per_chord` bars on the track's first empty clip slot
  - Adds chord notes to clip at the correct bar positions
  - Returns JSON: `{chords: [...], clip_info: {track_index, clip_index}, progression_name: str}`
  
  **Tool: `generate_melody`**
  - Calls `generate_melody(key, scale, bars, complexity)`
  - If `track_index` provided + existing clip at `clip_index`: adds notes to that clip
  - If not: creates new MIDI track + clip
  - Returns JSON: `{notes: [...], clip_info: {track_index, clip_index}}`
  
  **Tool: `generate_bassline`**
  - Generates a bassline following root notes: root-octave-root pattern with passing tones
  - Uses the implied chord roots from a generated progression or scale tones
  - Creates new MIDI track + clip if no track specified
  - Returns JSON: `{notes: [...], clip_info: {track_index, clip_index}}`
  
  Must NOT: Use absolute parameter values (always normalize 0.0-1.0). Must NOT create MIDI clips on audio tracks. Must NOT generate audio. Must import `create_midi_track`, `create_clip`, `add_notes_to_clip` from server.py (use `get_ableton_connection` to call existing remote handlers).
  
  Parallelization: Wave 2 | Blocked by: 1, 2 | Blocks: 7
  References:
  - Existing tool pattern: `MCP_Server/advanced_tools.py:48` register_advanced_tools
  - `MCP_Server/server.py` — `send_command` pattern for calling remote handlers
  - Clip creation: existing `create_midi_track(idx)`, `create_clip(ti, ci, length)` tools
  - `get_ableton_connection()` returns a function that sends TCP commands
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import ast
  with open('MCP_Server/composition_tools.py') as f:
      tree = ast.parse(f.read())
  funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
  assert 'register_composition_tools' in funcs, 'register function missing'
  # Check tool function definitions
  tool_funcs = [f for f in funcs if f.startswith('generate_')]
  assert 'generate_chord_progression' in tool_funcs, 'generate_chord_progression missing'
  assert 'generate_melody' in tool_funcs, 'generate_melody missing'
  assert 'generate_bassline' in tool_funcs, 'generate_bassline missing'
  print(f'Composition tools defined: {tool_funcs}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: generate_chord_progression("C", "minor", "techno", 4, 4) creates a 16-bar clip with 4 chords, returns JSON
  - HAPPY: generate_melody("A", "minor", 8, complexity=0.5) creates new track + 8-bar clip with melody notes
  - HAPPY: generate_melody("A", "minor", 4, complexity=0.5, track_index=0, clip_index=0) adds notes to existing clip
  - HAPPY: generate_bassline("C", "minor", 4) creates bassline with root-octave pattern
  - FAILURE: generate_chord_progression("X", "minor", "techno") returns error for invalid key
  - FAILURE: generate_chord_progression("C", "minor", "techno", -1) returns error for invalid length
  - FAILURE: generate_melody("C", "major", 0) returns error for zero bars
  - FAILURE: generate_bassline("C", "major", 8, track_index=999) returns error for invalid track
  Evidence: .omo/evidence/task-5-sprint-04-composition-tools.txt
  Commit: Y | feat(tools): add generative composition tools (chord_progression, melody, bassline)

- [ ] 6. Composition tools — quantize_to_scale + analyze_chord
  What to do / Must NOT do:
  Add to `MCP_Server/composition_tools.py` (same file as Todo 5) the remaining 2 tools:
  
  **Tool: `quantize_to_scale`**
  ```python
  @server.tool  
  def quantize_to_scale(ctx, track_index: int, clip_index: int, key: str = "C", scale: str = "minor") -> str:
      \"\"\"Snap every MIDI note in a clip to the nearest scale tone. Returns count of notes moved.\"\"\"
  ```
  - Gets scale notes from `composition.get_scale_notes(key, scale)`
  - Calls `send_command("quantize_to_scale", {track_index, clip_index, scale_notes})`
  - Validates track_index and clip_index exist before calling
  - Non-MIDI clips return error message
  - Returns JSON: `{notes_modified: int, total_notes: int, scale: str, key: str}`
  
  **Tool: `analyze_chord`**
  ```python
  @server.tool
  def analyze_chord(ctx, track_index: int, clip_index: int, bar_start: int = 0) -> str:
      \"\"\"Analyze MIDI notes in a bar and return detected chord name + confidence.\"\"\"
  ```
  - Gets MIDI notes from the clip for the bar at `bar_start`
  - Calls `composition.get_chord_name(notes)`
  - Returns JSON: `{chord_name: str, confidence: float, notes_found: [int], bar: int}`
  - If no notes found in bar: returns `{chord_name: "Silence", confidence: 0.0, notes_found: []}`
  
  Must NOT: Add new TCP commands (uses existing Remote Script handlers). Must NOT analyze audio clips (check `clip.is_midi_clip` first). Must limit bar_start to clip length.
  
  Parallelization: Wave 2 | Blocked by: 4 | Blocks: 7
  References:
  - `MCP_Server/server.py:send_command("quantize_to_scale", ...)` — uses the Remote Script handler from Todo 4
  - Existing clip reading pattern: `MCP_Server/advanced_tools.py:get_clip_notes` (if exists)
  - `composition.py:get_chord_name()` from Todo 2
  - `composition.py:get_scale_notes()` from Todo 1
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import ast
  with open('MCP_Server/composition_tools.py') as f:
      tree = ast.parse(f.read())
  funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
  assert 'quantize_to_scale' in funcs, 'quantize_to_scale missing'
  assert 'analyze_chord' in funcs, 'analyze_chord missing'
  # Check for 5 total tool functions
  tool_funcs = [f for f in funcs if f.startswith('generate_') or f.startswith('quantize_') or f.startswith('analyze_')]
  assert len(tool_funcs) >= 5, f'Expected >=5 tools, got {len(tool_funcs)}: {tool_funcs}'
  print(f'All 5 composition tools defined: {tool_funcs}')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: quantize_to_scale(track=0, clip=0, key="C", scale="major") snaps F#→F, returns {notes_modified: 2, total_notes: 8}
  - HAPPY: analyze_chord(track=0, clip=0, bar_start=0) returns {chord_name: "C min7", confidence: 0.86, notes_found: [...]}
  - FAILURE: quantize_to_scale(track=999, clip=0) returns "track index out of range"
  - FAILURE: quantize_to_scale(track=0, clip=0, key="X") returns error for invalid key
  - FAILURE: analyze_chord(track=0, clip=0, bar_start=999) returns error for bar beyond clip length
  - FAILURE: analyze_chord on audio track clip returns "clip is not a MIDI clip"
  Evidence: .omo/evidence/task-6-sprint-04-composition-tools.txt
  Commit: Y | feat(tools): add quantize_to_scale and analyze_chord composition tools

- [ ] 7. Server.py import + registration
  What to do / Must NOT do:
  Modify `MCP_Server/server.py`:
  
  1. Add import: `from MCP_Server.composition_tools import register_composition_tools`
  2. Add registration call in the tool registration section (around line 752-765 where other `register_*_tools` calls are made):
     ```python
     register_composition_tools(mcp, get_ableton_connection)
     ```
  
  Must NOT: Modify existing tool bodies. Must NOT change import order in a way that breaks existing imports. Must NOT modify the Remote Script command dispatch (that's Todo 4).
  
  Parallelization: Wave 3 | Blocked by: 5, 6 | Blocks: 8
  References:
  - Tool registration section: `MCP_Server/server.py:752-765`
  - Existing imports: `MCP_Server/server.py:1-50` (top of file)
  - Pattern from other registrations: `register_advanced_tools(mcp, get_ableton_connection)`
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'from MCP_Server.composition_tools import register_composition_tools' in content, 'import missing'
  assert 'register_composition_tools(mcp, get_ableton_connection)' in content, 'registration call missing'
  print('Server.py import + registration OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Import line present, registration call present
  - HAPPY: registration call uses correct pattern matching other registrations
  - FAILURE: Import references non-existent module — must be after composition_tools.py is created
  Evidence: .omo/evidence/task-7-sprint-04-composition-tools.txt
  Commit: Y | feat(server): import and register composition tools module

- [ ] 8. Unit + integration tests
  What to do / Must NOT do:
  Create `tests/test_composition.py`:
  ```python
  # Unit tests for music theory engine
  from MCP_Server.composition import (
      get_scale_notes, is_note_in_scale, snap_to_scale,
      get_chord_notes, get_chord_name, get_progression_notes,
      generate_melody
  )
  import pytest  # optional, use assert
  
  def test_c_major_scale():
      notes = get_scale_notes('C', 'major')
      assert len(notes) == 7
      assert notes[0] == 60 and notes[-1] == 71
      assert all(n >= 48 and n <= 84 for n in notes)  # C3-C5 range
  # ... more test functions covering: a_minor, f#_harmonic_minor, snap_edge_cases,
  #     chord_types_all, chord_detection, progressions_all_genres, melody_empty,
  #     melody_reproducible, melody_complexity_range
  ```
  
  Create `tests/test_composition_tools.py`:
  ```python
  # Integration tests for tool registration
  # Verifies tools exist and have correct signatures
  import ast, inspect
  
  def test_tools_registered():
      with open('MCP_Server/composition_tools.py') as f:
          tree = ast.parse(f.read())
      funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
      expected = ['register_composition_tools', 'generate_chord_progression', 
                  'generate_melody', 'quantize_to_scale', 'analyze_chord', 'generate_bassline']
      for e in expected:
          assert e in funcs, f'{e} not found in composition_tools.py'
  ```
  
  Must NOT: Use pytest fixtures (keep standalone). Must NOT require Ableton Live to be running (unit tests are pure Python). Must use `python tests/test_composition.py` runnable directly.
  
  Parallelization: Wave 3 | Blocked by: 1, 2, 3, 4, 5, 6, 7 | Blocks: None
  References:
  - Existing test pattern: `scripts/test/test_connection.py` (standalone, no pytest discovery)
  - Test file location: `tests/` directory (relative to project root)
  
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  # Verify test files exist and compile
  import os
  assert os.path.exists('tests/test_composition.py'), 'test_composition.py missing'
  assert os.path.exists('tests/test_composition_tools.py'), 'test_composition_tools.py missing'
  
  # Compile check
  for f in ['tests/test_composition.py', 'tests/test_composition_tools.py']:
      compile(open(f).read(), f, 'exec')
  print('Test files exist and compile OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: `python tests/test_composition.py` runs and all tests pass
  - HAPPY: `python tests/test_composition_tools.py` runs and verifies all 5 tools
  - FAILURE: Test catches regression — e.g., get_scale_notes signature changed, test fails with clear message
  - FAILURE: Fewer than 5 tools registered in composition_tools.py, test catches it
  Evidence: .omo/evidence/task-8-sprint-04-composition-tools.txt
  Commit: Y | test(composition): add unit tests for music theory engine and integration tests for tools

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: Verify all 8 deliverables exist, all scope boundaries respected
- [ ] F2. Code quality review: All .py files pass `python -c "compile(open(f).read(), f, 'exec')"` — no syntax errors
- [ ] F3. Unit test run: `python tests/test_composition.py` exits with code 0
- [ ] F4. Integration test run: `python tests/test_composition_tools.py` exits with code 0
- [ ] F5. Tool count verification: `grep -c "def generate_chord_progression\|def generate_melody\|def quantize_to_scale\|def analyze_chord\|def generate_bassline" MCP_Server/composition_tools.py` returns 5
- [ ] F6. Scope fidelity: grep for Must NOT have violations (no audio key detection, no external music theory libs, no audio generation, no ML imports)
- [ ] F7. Acceptance criteria check: Run the acceptance criteria from the spec — `get_scale_notes('C', 'major')` returns 7 notes, `snap_to_scale(61, 'C', 'major')` returns 60, `generate_melody('A', 'minor', 4)` returns non-empty notes with correct keys

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(composition): add scales module with get_scale_notes, is_note_in_scale, snap_to_scale
- feat(composition): add chords module with detection, progressions, and Markov melody generator
- feat(knowledge): add scales.json and chord_templates.json with genre progressions
- feat(remote-script): add _quantize_to_scale handler for MIDI note scale snapping
- feat(tools): add generative composition tools (chord_progression, melody, bassline)
- feat(tools): add quantize_to_scale and analyze_chord composition tools
- feat(server): import and register composition tools module
- test(composition): add unit tests for music theory engine and integration tests for tools

No squashing — each commit is independently testable. Tags: none.

## Success criteria
All 5 composition MCP tools exist with correct signatures and return valid JSON
Music theory engine produces correct scale notes for all 12 keys in all scale types
Chord detection identifies common chords (maj, min, 7th, min7) with > 50% confidence
Melody generator produces non-empty, in-scale melodies for any complexity level (0.0-1.0)
Scale quantization snaps off-key notes to nearest scale tone
Chord progression generator creates clips with correct note content
Knowledge files load as valid JSON and contain all required scale/mode/progression data
Remote Script quantize handler compiles and dispatches correctly
All unit tests pass without Ableton Live running
All integration tests verify tool registration
