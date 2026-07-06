# Sprint 05: Songwriter Workflow — End-to-End Song Creation

**Theme:** From a single brief to a full arrangement in one command.
**Est. days:** 5 | **New tools:** 3-4 | **Risk:** Medium-High
**Dependencies:** Sprint 04 (composition tools)

## Goal
Build an orchestrator that takes a high-level song brief (genre, BPM, key, structure) and creates a complete Ableton session with intro, verse, chorus, bridge, outro, full arrangement automation, and scene structure. Extends the existing `@ableton-songwriter` skill from a template helper into a standalone MCP-powered composer.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/songwriter.py` | Create | Core orchestration engine (compose_song_from_brief) |
| `MCP_Server/songwriter_presets.py` | Create | Song structure templates + instrument recipes |
| `MCP_Server/server.py` | Modify | Import + register songwriter tools |
| `scripts/songwriter_example.py` | Create | End-to-end demo script |
| `MCP_Server/knowledge/song_structure.json` | Create | Structure templates per genre |
| `MCP_Server/knowledge/instrument_recipes.json` | Create | Genre-appropriate instrument chains |
| `tests/test_songwriter.py` | Create | Integration tests with mocked Live connection |

## Deliverables

### 5.1 Song Structure Templates
`song_structure.json` defines named templates:

```json
{
  "techno_peak": {
    "sections": ["intro", "build_1", "drop_1", "breakdown", "build_2", "drop_2", "outro"],
    "bars_per_section": [8, 4, 16, 8, 4, 16, 8],
    "energy_curve": [0.2, 0.5, 1.0, 0.3, 0.6, 1.0, 0.1],
    "track_types": {
      "kick": {"count": 1, "pattern": "techno_4x4"},
      "percussion": {"count": 3},
      "bass": {"count": 1, "type": "synth"},
      "pad": {"count": 1},
      "fx": {"count": 2}
    }
  },
  "pop_song": {
    "sections": ["intro", "verse", "pre_chorus", "chorus", "verse", "chorus", "bridge", "chorus_outro"],
    "bars_per_section": [4, 8, 4, 8, 8, 8, 8, 8],
    "energy_curve": [0.3, 0.5, 0.7, 1.0, 0.5, 1.0, 0.6, 0.8],
    "track_types": {
      "drums": {"count": 1},
      "bass": {"count": 1},
      "chords": {"count": 1, "type": "keys"},
      "lead": {"count": 1},
      "vocals": {"count": 1, "optional": true}
    }
  },
  "ambient_scape": {
    "sections": ["build", "evolve", "peak", "decay", "resolve"],
    "bars_per_section": [16, 16, 24, 16, 16],
    "energy_curve": [0.2, 0.5, 0.9, 0.6, 0.1],
    "track_types": {
      "pad": {"count": 3},
      "texture": {"count": 2},
      "bass": {"count": 1},
      "fx": {"count": 1}
    }
  },
  "dub_delay": {
    "sections": ["intro", "verses", "chorus", "dub", "outro"],
    "bars_per_section": [4, 16, 8, 16, 8],
    "energy_curve": [0.3, 0.5, 0.7, 0.9, 0.2],
    "track_types": {
      "drums": {"count": 1, "pattern": "rockers"},
      "bass": {"count": 1, "type": "sub"},
      "rhythm_guitar": {"count": 1, "optional": true},
      "organ": {"count": 1, "optional": true},
      "fx": {"count": 2, "delay_reverb": true}
    }
  }
}
```

Plus 6 more templates: `house_anthem`, `dnb_roller`, `hiphop_trap`, `lo-fi_study`, `cinematic`, `minimal_deep`.

### 5.2 Instrument Recipes (`instrument_recipes.json`)
Genre-appropriate device chains:
```json
{
  "techno_kick": {"device": "Drum Rack", "kit": "query:909#FileId_..."},
  "techno_bass": {"device": "Operator", "preset": "query:Deep Mono"},
  "house_chords": {"device": "Wavetable", "preset": "query:Warm Pad"},
  "ambient_pad": {"device": "Hybrid Reverb", "chain": ["Reverb", "Delay"]},
  "dub_bass": {"device": "Drift", "preset": "query:Deep Sub"},
  ...
}
```

### 5.3 Core Engine (`songwriter.py`)

**Function: `compose_song_from_brief(brief: dict) -> str`**

Accepts:
```python
brief = {
    "genre": "techno",
    "bpm": 130,
    "key": "D",
    "scale": "minor",
    "structure": "techno_peak",  # or custom dict
    "complexity": 0.6,           # 0.0-1.0
    "mood": "dark",              # affects instrument selection
    "track_count": 8,
}
```

Orchestration flow (calls existing tools):
1. `delete_all_tracks()` — clean slate
2. `create_midi_track()` x N tracks
3. `set_track_name(i, name)` — naming per template
4. `load_instrument_or_effect(i, "query:...")` — from instrument_recipes
5. `set_tempo(brief.bpm)`
6. `create_drum_pattern(track, scene, "techno_4x4")` on kick track
7. `generate_chord_progression(key=D, scale=minor, genre=techno)` on chords track
8. `generate_melody(key=D, scale=minor, bars=16, complexity=0.6)` on lead track
9. Creates scene structure per template's sections
10. Sets clip follow actions for automated section progression
11. Returns session summary JSON

**Function: `generate_arrangement(track_count: int, sections: list) -> str`**
Lays out scenes in order with:
- Clip duplication per section
- Scene naming (intro, verse, etc.)
- Follow action configuration (auto-progression)
- Basic automation curves per section type

**Function: `generate_automation_build(track_index, clip_index, bars, parameter)`**
Creates rising/falling automation envelope:
- HF filter sweep (build)
- Volume fade (intro/outro)
- Reverb send (breakdown)
- Distortion / drive (drop)
Returns envelope points.

### 5.4 Tool Registration

**Tool: `compose_song_from_brief`**
```
(ctx, genre: str = "techno", bpm: int = 130, key: str = "C",
 scale: str = "minor", structure: str = "techno_peak",
 complexity: float = 0.5, mood: str = "neutral",
 track_count: int = 8) -> str
```
Returns: JSON with session summary, tracks, sections, estimated duration.

**Tool: `generate_arrangement`**
```
(ctx, structure_template: str, section_overrides: str = "") -> str
```
- `structure_template`: named template from song_structure.json
- `section_overrides`: optional JSON string to override specific sections
- Returns: arrangement layout JSON with scenes, clips, follow actions

**Tool: `generate_automation_build`**
```
(ctx, track_index: int, clip_index: int, bars: int = 8,
 parameter_type: str = "filter_sweep") -> str
```
- `parameter_type`: "filter_sweep", "volume_fade", "reverb_send", "drive"
- Returns: envelope point count + parameter targeted

### 5.5 Script Integration
`scripts/songwriter_example.py`:
```python
# Example: compose a dark techno track in one call
import json
from MCP_Server.songwriter import compose_song_from_brief

result = compose_song_from_brief({
    "genre": "techno", "bpm": 132, "key": "G", "scale": "minor",
    "structure": "techno_peak", "complexity": 0.7, "mood": "dark"
})
print(json.dumps(result, indent=2))
```

## API Surface

### New Tools
| Tool | Signature | Returns |
|------|-----------|---------|
| `compose_song_from_brief` | (genre, bpm, key, scale, structure, complexity, mood, track_count) | Session summary JSON |
| `generate_arrangement` | (structure_template, section_overrides) | Arrangement layout JSON |
| `generate_automation_build` | (track_index, clip_index, bars, parameter_type) | Envelope info JSON |

## Acceptance Criteria
```bash
python -c "
from MCP_Server.songwriter import compose_song_from_brief
from MCP_Server.songwriter_presets import STRUCTURE_TEMPLATES
assert 'techno_peak' in STRUCTURE_TEMPLATES
assert 'pop_song' in STRUCTURE_TEMPLATES
assert len(STRUCTURE_TEMPLATES) >= 10
print(f'{len(STRUCTURE_TEMPLATES)} structure templates loaded')
"
```

```bash
grep -c "def compose_song_from_brief\|def generate_arrangement\|def generate_automation_build" MCP_Server/songwriter.py
# 3 core functions
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Session creation fails midway (invalid FileId, etc.) | High | Wrap each step in try/except; session stays partially built |
| Composition sounds generic | Medium | complexity param, mood param, randomization seeds |
| Lots of tool calls = slow | Medium | Show progress messages; allow async with status updates |
| Heavy session takes 30+ seconds | Low | Timeout per step; parallelize independent tracks |

## Must NOT Do
- Do NOT generate audio files (MIDI-only composition)
- Do NOT attempt to "master" or finalize the session (mixing is user's job)
- Do NOT delete existing sessions without prompt
- Do NOT hardcode FileIds (they differ per Live version)
