# Sprint 03: MCP Prompts + Workflow Templates

**Theme:** Make the AI useful without programming — guided workflows via MCP Prompts.
**Est. days:** 4 | **New prompts:** 5 | **New tools:** 1 | **Risk:** Low
**Dependencies:** None

## Goal
Register the first MCP Prompts on the FastMCP instance. Currently we have 0 prompts vs livemcp's 11. Prompts are lightweight templates that guide the LLM to perform multi-step workflows correctly. They're the fastest way to make the tool useful for non-experts.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/server.py` | Modify | Add `@mcp.prompt()` decorators + prompt functions |
| `MCP_Server/prompts/` | Create | Prompt template directory |
| `MCP_Server/prompts/__init__.py` | Create | Lazy-loaded prompt renderer |
| `MCP_Server/prompts/session_setup.md` | Create | Template: build a new session from scratch |
| `MCP_Server/prompts/mix_drums.md` | Create | Template: mix/produce drum tracks |
| `MCP_Server/prompts/sound_design_bass.md` | Create | Template: design a bass patch |
| `MCP_Server/prompts/arrange_track.md` | Create | Template: arrange track into full song |
| `MCP_Server/prompts/dj_transition.md` | Create | Template: DJ transition workflow |
| `tests/test_prompts.py` | Create | Unit tests for prompt loading + rendering |

## Deliverables

### 3.1 Prompt Registration Pattern
Register prompts on the FastMCP `mcp` instance using `@mcp.prompt()`:

```python
@mcp.prompt()
def session_setup(ctx: Context) -> list[PromptMessage]:
    """Build a new Ableton session from scratch: clean slate, tracks, instruments, patterns."""
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=load_prompt_template("session_setup")
            )
        )
    ]
```

Each prompt accepts optional `**kwargs` for context-specific parameters:
- `genre: str` — for drum pattern selection
- `bpm_range: tuple[int, int]` — for tempo suggestion
- `track_count: int` — number of tracks to create
- `key: str` — for instrument/scale selection

### 3.2 Session Setup Prompt
**Template:** Guides LLM to build a session from scratch following AGENTS.md workflow order:
1. `delete_all_tracks()` — clean slate
2. `create_midi_track(n)` for each track
3. `set_track_name(i, "Name")`
4. `load_instrument_or_effect(i, "query:...")` — with FileId guidance
5. `set_tempo(bpm)`
6. `create_drum_pattern()` with variant selection
7. `create_clip()` + `add_notes_to_clip()`

Accepts: `genre`, `bpm`, `track_count`, `drum_pattern_variant`

### 3.3 Mix Drums Prompt
**Template:** EQ and compress drum tracks:
1. `get_track_info("Drums")` to verify
2. `load_instrument_or_effect(drums_track, "query:EQ Eight")`
3. `set_device_parameter(...)` for HPF at 40Hz on kick
4. `set_device_parameter(...)` for sidechain
5. Compressor settings for glue

Accepts: `drum_style` ("techno", "house", "dub", "hiphop", "acoustic")

### 3.4 Sound Design Bass Prompt
**Template:** Create and shape a bass patch:
1. Create bass track
2. Load synth (Wavetable, Operator, Drift)
3. Set oscillator parameters
4. Add effects (saturator, compressor)
5. Create bass pattern

Accepts: `bass_type` ("sub", "acid", "reese", "pluck", "fm"), `synth_preference` (optional)

### 3.5 Arrange Track Prompt
**Template:** Turn a loop/idea into a full arrangement:
1. Duplicate clips across scenes
2. Build intro, verse, chorus, bridge sections
3. Apply fills and transitions
4. Set clip follow actions for performance
5. Create automation builds

Accepts: `structure` ("4x4_techno", "pop_verse_chorus", "ambient_evolve", "dub_build"), `length_bars`

### 3.6 DJ Transition Prompt
**Template:** Professional transition between two tracks:
1. Identify current and next track
2. Match tempo (or plan ramp)
3. Plan EQ/filter transition
4. Execute crossfade with timing
5. Mix in new track elements

Accepts: `transition_type` ("hard_cut", "eq_sweep", "filter_fade", "loop_roll", "beat_match")
          , `transition_bars` (4, 8, 16)

### 3.7 Prompt Loading System
`MCP_Server/prompts/__init__.py` provides:
- `load_prompt_template(name: str, **kwargs) -> str` — loads .md template, renders Jinja2-like `{placeholders}` or simple `{genre}` style
- `get_available_prompts() -> list[str]` — lists available prompt names
- Caches loaded templates in dict (file read once, then in-memory)

### 3.8 Prompt Tool
Register `get_workflow_prompt(ctx, template_name, **kwargs)` that:
- Loads the template
- Renders with provided kwargs
- Returns rendered prompt string
- Falls back to helpful error if template not found

## API Surface

### New Prompts (via `@mcp.prompt()`)
| Prompt ID | Description | Parameters |
|-----------|-------------|------------|
| `session_setup` | Build session from scratch | genre, bpm, track_count, drum_pattern |
| `mix_drums` | Mix drum tracks with EQ/compression | drum_style |
| `sound_design_bass` | Design bass patch from scratch | bass_type, synth_preference |
| `arrange_track` | Arrange loop into full song | structure, length_bars |
| `dj_transition` | Professional DJ transition | transition_type, transition_bars |

### New Tool
| Tool | Signature | Returns |
|------|-----------|---------|
| `get_workflow_prompt` | `(ctx, template_name, **kwargs) -> str` | Rendered prompt text |

## Acceptance Criteria
```bash
# All prompts register
grep -c "@mcp.prompt()" MCP_Server/server.py  # == 5

# Prompt rendering
python -c "
from MCP_Server.prompts import load_prompt_template
text = load_prompt_template('session_setup', genre='techno', bpm=130)
assert '130' in text and 'techno' in text
print('Prompt rendering OK')
"

# Tool works
# Call get_workflow_prompt("session_setup", genre="house", bpm=125)
# → Returns Markdown-formatted workflow steps
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Prompt templates become stale as tools change | Medium | Version-pin prompts; add `prompt_version` field |
| Poor prompt quality misleads users | Medium | Test each prompt with Claude to verify output quality |
| Too many parameters overwhelm users | Low | Keep max 3 params per prompt; sensible defaults |

## Must NOT Do
- Do NOT put executable commands in prompt templates (they're guidance text, not scripts)
- Do NOT attempt to auto-execute prompts (LLM reads and acts, we don't run them)
- Do NOT add external dependencies for template rendering (stdlib string formatting only)
- Do NOT create prompts that could damage the session (no destructive defaults)
