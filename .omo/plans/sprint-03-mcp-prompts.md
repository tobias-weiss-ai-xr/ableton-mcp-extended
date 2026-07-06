# Sprint 03: MCP Prompts + Workflow Templates

## TL;DR (For humans)

**What you'll get:** 5 guided workflow templates (session_setup, mix_drums, sound_design_bass, arrange_track, dj_transition) registered as MCP Prompts so the AI can walk through multi-step Ableton sessions without hallucinating the order of operations. Plus a `get_workflow_prompt` tool for manually fetching a workflow. Currently 0 prompts → 5 prompts.

**Why this approach:** Prompts are the fastest way to make the toolchain useful for non-experts. Rather than the LLM guessing which tool to call and in what order, each prompt provides a battle-tested step-by-step template that follows the AGENTS.md workflow rules. The prompt loading system caches templates in-memory (stdlib only, no deps).

**What it will NOT do:** Auto-execute prompts (LLM reads and acts, we don't run them). Put executable commands in templates. Add external dependencies for template rendering (stdlib string formatting only). Create destructive defaults.

**Effort:** Small (1 sprint, ~4 days)
**Risk:** Low — no new Remote Script handlers, no socket protocol changes, no tool body rewrites
**Decisions to sanity-check:** Prompt template placeholders syntax (`{genre}` vs Jinja2), parameterization style per prompt

---

> TL;DR (machine): Small effort, Low risk. 8 todos across 2 waves. Wave 1: prompt loading system + 5 markdown templates (all parallel). Wave 2: registration + tool + tests.

## Scope

### Must have
- `MCP_Server/prompts/__init__.py` — lazy-loaded template cache with `load_prompt_template(name, **kwargs) -> str` and `get_available_prompts() -> list[str]`
- 5 prompt template `.md` files in `MCP_Server/prompts/`:
  - `session_setup.md` — build a session from scratch (AGENTS.md workflow order)
  - `mix_drums.md` — EQ and compress drum tracks
  - `sound_design_bass.md` — design a bass patch from scratch
  - `arrange_track.md` — arrange a loop into a full song
  - `dj_transition.md` — professional DJ transition between two tracks
- 5 `@mcp.prompt()` decorators in `MCP_Server/server.py` using `PromptMessage` / `TextContent` from `mcp.types`
- Tool `get_workflow_prompt(ctx, template_name, **kwargs) -> str` that renders and returns a prompt template
- `tests/test_prompts.py` — unit tests for loading + rendering

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT put executable commands in prompt templates (they're guidance text, not scripts)
- Do NOT attempt to auto-execute prompts (LLM reads and acts, we don't run them)
- Do NOT add external dependencies for template rendering (stdlib string formatting with `.format()` or `%` only)
- Do NOT create prompts that could damage the session (no destructive defaults)
- Do NOT modify existing tool bodies, socket handlers, or Remote Script code

## Verification strategy
> Zero human intervention — all verification is agent-executed.
- Test decision: tests-after (test_prompts.py runs after implementation)
- Evidence: `.omo/evidence/task-<N>-sprint-03-mcp-prompts.<ext>`

## Execution strategy (parallel waves, dependency matrix)

### Parallel execution waves
| Wave | Focus | Todos | Est. days |
|------|-------|-------|-----------|
| 1 | Prompt loading system + templates | 1, 2, 3, 4, 5, 6 | 2 |
| 2 | Registration + tool + tests | 7, 8 | 2 |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Prompt loading system | None | 7, 8 | 2, 3, 4, 5, 6 |
| 2. session_setup.md template | None | 7 | 1, 3, 4, 5, 6 |
| 3. mix_drums.md template | None | 7 | 1, 2, 4, 5, 6 |
| 4. sound_design_bass.md template | None | 7 | 1, 2, 3, 5, 6 |
| 5. arrange_track.md template | None | 7 | 1, 2, 3, 4, 6 |
| 6. dj_transition.md template | None | 7 | 1, 2, 3, 4, 5 |
| 7. `@mcp.prompt()` registrations + tool | 1, 2, 3, 4, 5, 6 | 8 | None |
| 8. Tests | 1, 7 | None | None |

## Todos (5-8 atomic items with acceptance criteria, QA scenarios, commit msgs)

> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Create prompt rendering system `MCP_Server/prompts/__init__.py`
  What to do / Must NOT do:
  Create `MCP_Server/prompts/__init__.py` with:
  - `load_prompt_template(name: str, **kwargs) -> str`:
    1. Resolves `MCP_Server/prompts/{name}.md` from the file alongside the module
    2. Reads file content (or serves from in-memory `_template_cache: dict[str, str]`)
    3. Renders with `content.format(**kwargs)` (stdlib only — simple `{placeholder}` syntax)
    4. Falls back to `content % kwargs` if `.format()` raises KeyError (backward compat)
    5. Caches: file read once, then in-memory. Cache invalidation on `load_prompt_template(name, _reload=True)`.
  - `get_available_prompts() -> list[str]`:
    1. Lists `.md` files in `MCP_Server/prompts/` directory
    2. Strips `.md` extension
    3. Returns sorted list of prompt names
  - `DEFAULT_PARAMS: dict[str, dict]` — default parameter values per template:
    ```python
    DEFAULT_PARAMS = {
        "session_setup": {"genre": "techno", "bpm": 128, "track_count": 8, "drum_pattern": "four_on_floor"},
        "mix_drums": {"drum_style": "techno"},
        "sound_design_bass": {"bass_type": "sub", "synth_preference": ""},
        "arrange_track": {"structure": "4x4_techno", "length_bars": 32},
        "dj_transition": {"transition_type": "eq_sweep", "transition_bars": 8},
    }
    ```

  Must NOT: Import external templating engines (jinja2, mako, etc.). Must NOT execute code during template load. Must handle missing template files with clear error messages.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7, 8 | Can parallelize with: 2, 3, 4, 5, 6
  References:
  - FastMCP prompt registration: `MCP_Server/server.py:751` mcp = FastMCP(...)
  - Stdlib pattern: `import os`, `__file__` for module path resolution, `str.format()`
  - Existing submodule location: `MCP_Server/prompts/` (new directory)
  - No existing `MCP_Server/prompts/` directory yet
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.prompts import load_prompt_template, get_available_prompts
  # get_available_prompts should return an empty list (no .md files yet)
  names = get_available_prompts()
  assert isinstance(names, list), 'get_available_prompts should return list'
  print(f'Available prompts: {names}')

  # Try loading a non-existent template
  try:
      load_prompt_template('nonexistent')
      assert False, 'Should raise FileNotFoundError'
  except FileNotFoundError:
      print('FileNotFoundError correctly raised for missing template')
  print('Prompt loading system OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call get_available_prompts() with empty directory → returns []
  - HAPPY: Call get_available_prompts() after adding .md files → returns list of template names
  - FAILURE: Call load_prompt_template("missing") → FileNotFoundError with helpful message
  - FAILURE: Call load_prompt_template("session_setup", unknown_param="x") → renders template with {unknown_param} left as-is
  Evidence: `.omo/evidence/task-1-sprint-03-mcp-prompts.txt`
  Commit: Y | feat(prompts): add prompt rendering system with caching and template loading

- [ ] 2. Create `session_setup.md` prompt template
  What to do / Must NOT do:
  Create `MCP_Server/prompts/session_setup.md` — guides the LLM to build a session from scratch.
  Follows the AGENTS.md workflow order exactly:
  1. `delete_all_tracks()` — clean slate
  2. `create_midi_track(n)` for each track
  3. `set_track_name(i, "Name")` — semantic naming
  4. `load_instrument_or_effect(i, "query:...")` — with FileId guidance reminder
  5. `set_tempo(bpm)`
  6. `create_drum_pattern()` with variant selection (`one_drop`, `rockers`, `steppers`, `house_basic`, `techno_4x4`, `dub_techno`)
  7. `create_clip()` + `add_notes_to_clip()` — add MIDI notes for melody/bass

  Template content (Markdown with `{placeholder}` syntax):
  - Title: "Session Setup Workflow — `{genre}` at `{bpm}` BPM, `{track_count}` tracks"
  - Context block explaining the goal
  - Step-by-step numbered instructions with tool names in backticks
  - Parameter guidance per step (e.g., "For drum pattern variant, choose from: one_drop, rockers, steppers, house_basic, techno_4x4, dub_techno")
  - Drum pattern variant hint referencing the AGENTS.md variant table
  - Anti-pattern warning: NEVER load empty Drum Rack, always use specific FileId
  - Final verification steps for the LLM to check its work

  Accepts: `{genre}` (str), `{bpm}` (int), `{track_count}` (int), `{drum_pattern}` (str — variant name)

  Must NOT: Include executable Python commands. Must NOT hardcode track count (use `{track_count}`). Must NOT suggest audio export.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 3, 4, 5, 6
  References:
  - AGENTS.md workflow order (reproduced at top of this plan)
  - Drum pattern variants: AGENTS.md table (one_drop, rockers, steppers, house_basic, techno_4x4, dub_techno)
  - Anti-pattern: "NEVER load empty Drum Rack — must load a kit preset with specific FileId"
  - Template location: `MCP_Server/prompts/session_setup.md`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.prompts import load_prompt_template, get_available_prompts
  names = get_available_prompts()
  assert 'session_setup' in names, 'session_setup not in available prompts'

  text = load_prompt_template('session_setup', genre='techno', bpm=130, track_count=8, drum_pattern='techno_4x4')
  assert 'techno' in text, 'genre placeholder not rendered'
  assert '130' in text, 'bpm placeholder not rendered'
  assert '8' in text, 'track_count placeholder not rendered'
  assert 'techno_4x4' in text, 'drum_pattern placeholder not rendered'
  assert 'delete_all_tracks()' in text, 'workflow step missing'
  assert 'create_midi_track' in text, 'workflow step missing'
  assert 'load_instrument_or_effect' in text, 'workflow step missing'
  assert 'Drum Rack' in text or 'FileId' in text, 'anti-pattern warning missing'
  print('session_setup.md template OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Load with genre="house", bpm=125, track_count=6, drum_pattern="house_basic" → all params rendered, correct workflow steps
  - HAPPY: Load with defaults (no kwargs) → defaults applied from DEFAULT_PARAMS
  - FAILURE: Template file malformed → KeyError for missing placeholders caught gracefully
  Evidence: `.omo/evidence/task-2-sprint-03-mcp-prompts.txt`
  Commit: Y | feat(prompts): add session_setup.md workflow template

- [ ] 3. Create `mix_drums.md` prompt template
  What to do / Must NOT do:
  Create `MCP_Server/prompts/mix_drums.md` — guides EQ and compression for drum tracks.
  Workflow steps:
  1. `get_track_info("Drums")` to verify drums track exists and identify the drum track index
  2. `load_instrument_or_effect(drums_track, "query:Audio Effects#EQ Eight")` for EQ
  3. `set_device_parameter(...)` for high-pass filter at ~40Hz on kick channel
  4. `set_device_parameter(...)` for sidechain compression setup
  5. `load_instrument_or_effect(drums_track, "query:Audio Effects#Glue Compressor")` for glue compression
  6. Compressor settings: threshold, ratio, attack, release guidance per style

  Accepts: `{drum_style}` — one of "techno", "house", "dub", "hiphop", "acoustic"

  Include style-specific compressor settings in a table:
  | Style | Attack | Release | Ratio | Threshold |
  |-------|--------|---------|-------|-----------|
  | techno | 0.1ms | 10ms | 4:1 | -12dB |
  | house | 1ms | 50ms | 3:1 | -8dB |
  | dub | 5ms | 100ms | 2:1 | -6dB |
  | hiphop | 2ms | 30ms | 5:1 | -15dB |
  | acoustic | 10ms | 150ms | 2.5:1 | -4dB |

  Must NOT: Suggest specific parameter indices (those depend on device). Must NOT include exact parameter index numbers.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 2, 4, 5, 6
  References:
  - Existing EQ tool: `load_instrument_or_effect` with "query:Audio Effects#EQ Eight"
  - Compressor tool: `load_instrument_or_effect` with "query:Audio Effects#Glue Compressor"
  - Template location: `MCP_Server/prompts/mix_drums.md`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.prompts import load_prompt_template
  text = load_prompt_template('mix_drums', drum_style='techno')
  assert 'techno' in text, 'drum_style not rendered'
  assert 'EQ Eight' in text or 'EQ' in text, 'EQ step missing'
  assert 'Glue Compressor' in text or 'compressor' in text.lower(), 'compressor step missing'
  assert 'high-pass' in text.lower() or 'HPF' in text, 'HPF guidance missing'
  assert '0.1ms' in text, 'techno attack time not in template'
  print('mix_drums.md template OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Load with drum_style="house" → house-specific compressor settings rendered
  - HAPPY: Load with drum_style="dub" → longer attack/release settings rendered
  - FAILURE: No kwargs → default "techno" style used from DEFAULT_PARAMS
  Evidence: `.omo/evidence/task-3-sprint-03-mcp-prompts.txt`
  Commit: Y | feat(prompts): add mix_drums.md workflow template

- [ ] 4. Create `sound_design_bass.md` prompt template
  What to do / Must NOT do:
  Create `MCP_Server/prompts/sound_design_bass.md` — guides creating and shaping a bass patch.
  Workflow steps:
  1. `create_midi_track()` to create a new track for bass
  2. `set_track_name(bass_track, "Bass")`
  3. Load synth based on preference or default to Wavetable:
     - `load_instrument_or_effect(bass_track, "query:Wavetable")`
     - Alternative: Operator, Drift (mention as options)
  4. Set oscillator parameters per bass_type (guidance, not exact indices)
  5. Add effects: `load_instrument_or_effect(bass_track, "query:Saturator")`, compressor
  6. `create_clip(bass_track, ...)` + `add_notes_to_clip(bass_track, ...)` — create a bassline pattern
  7. Set filter and amp envelope for the specific bass type

  Accepts: `{bass_type}` — one of "sub", "acid", "reese", "pluck", "fm"
  `{synth_preference}` — optional, one of "Wavetable", "Operator", "Drift", "Auto"

  Include a bass-type parameter table:
  | Type | Osc Shape | Filter | Envelope | Character |
  |------|-----------|--------|----------|-----------|
  | sub | Sine | LP 80Hz | Slow attack | Deep, clean |
  | acid | Saw | BP resonant | Fast decay | Squelchy |
  | reese | Detuned saws | LP mid | Medium | Thick, wide |
  | pluck | Square | BP fast | Very fast decay | Percussive |
  | fm | Sine-FM | LP | Medium | Metallic, growly |

  Must NOT: Hardcode parameter indices. Must NOT suggest specific synths as "the only option".

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 2, 3, 5, 6
  References:
  - Synth loading: `load_instrument_or_effect(track, "query:Wavetable")`
  - Effect chain: Saturator, Compressor after synth
  - Template location: `MCP_Server/prompts/sound_design_bass.md`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.prompts import load_prompt_template
  text = load_prompt_template('sound_design_bass', bass_type='reese')
  assert 'reese' in text, 'bass_type not rendered'
  assert 'detuned' in text.lower(), 'reese character missing'
  assert 'Wavetable' in text, 'synth guidance missing'
  assert 'Saturator' in text, 'effect chain step missing'
  assert 'create_midi_track' in text, 'track creation missing'

  text2 = load_prompt_template('sound_design_bass', bass_type='acid', synth_preference='Drift')
  assert 'acid' in text2, 'acid type not rendered'
  assert 'Drift' in text2, 'synth preference not rendered'
  print('sound_design_bass.md template OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Load with bass_type="sub" → sine wave, slow attack, LP filter guidance
  - HAPPY: Load with bass_type="fm" → FM synthesis, metallic character guidance
  - HAPPY: Load with synth_preference="Operator" → Operator mentioned as primary synth
  - FAILURE: Invalid bass_type → renders with default "sub" from DEFAULT_PARAMS
  Evidence: `.omo/evidence/task-4-sprint-03-mcp-prompts.txt`
  Commit: Y | feat(prompts): add sound_design_bass.md workflow template

- [ ] 5. Create `arrange_track.md` prompt template
  What to do / Must NOT do:
  Create `MCP_Server/prompts/arrange_track.md` — guides turning a loop/idea into a full arrangement.
  Workflow steps:
  1. Duplicate clips across scenes to build arrangement structure
  2. Build sections: intro, verse, chorus, bridge, outro
  3. Apply fills and transitions between sections
  4. Set clip follow actions for performance
  5. Create automation builds (filter sweeps, volume rides)
  6. Add effects sends for depth and space

  Accepts: `{structure}` — one of "4x4_techno", "pop_verse_chorus", "ambient_evolve", "dub_build"
  `{length_bars}` — int, total target length in bars

  Structure-specific section layout table:
  | Structure | Sections | Bars per section |
  |-----------|----------|------------------|
  | 4x4_techno | Intro → Break → Build → Drop → Outro | 8-16-8-16-8 |
  | pop_verse_chorus | Intro → Verse → Chorus → Verse → Chorus → Bridge → Chorus → Outro | 4-8-8-8-8-8-8-4 |
  | ambient_evolve | Intro → Layer 1 → Layer 2 → Climax → Decay | 8-16-16-16-8 |
  | dub_build | Intro → Verse → Dub → Verse → Dub → Outro | 8-8-8-8-8-8 |

  Must NOT: Suggest audio export. Must NOT include arrangement automation via Remote Script (read-only).

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 2, 3, 4, 6
  References:
  - Scene/track duplication: `create_scene`, `duplicate_clip` tools
  - Clip follow actions: `set_clip_launch_mode`, clip follow action settings
  - Automation: `get_clip_envelope`, `set_clip_envelope_point`
  - Template location: `MCP_Server/prompts/arrange_track.md`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.prompts import load_prompt_template
  text = load_prompt_template('arrange_track', structure='4x4_techno', length_bars=64)
  assert '4x4_techno' in text, 'structure not rendered'
  assert '64' in text, 'length_bars not rendered'
  assert 'Intro' in text, 'section layout missing'
  assert 'Break' in text, 'techno break section missing'
  assert 'Drop' in text, 'techno drop section missing'
  assert 'Outro' in text, 'outro section missing'
  assert 'follow action' in text.lower(), 'clip follow actions missing'
  print('arrange_track.md template OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Load with structure="pop_verse_chorus" → verse-chorus section layout rendered
  - HAPPY: Load with structure="dub_build" → dub-specific intro/verse/dub sections rendered
  - HAPPY: Load with length_bars=32 → 32-bar total mentioned
  - FAILURE: Invalid structure → default "4x4_techno" used from DEFAULT_PARAMS
  Evidence: `.omo/evidence/task-5-sprint-03-mcp-prompts.txt`
  Commit: Y | feat(prompts): add arrange_track.md workflow template

- [ ] 6. Create `dj_transition.md` prompt template
  What to do / Must NOT do:
  Create `MCP_Server/prompts/dj_transition.md` — guides a professional transition between two tracks.
  Workflow steps:
  1. Identify current and next track (use `get_session_info()`, `get_track_info()`)
  2. Match tempo between tracks (`set_tempo()`) or plan a ramp
  3. Plan EQ/filter transition strategy
  4. Load transition effects (EQ Eight, Filter Delay, Reverb)
  5. Execute crossfade within transition_bars
  6. Mix in new track elements progressively
  7. Transition completion check

  Accepts: `{transition_type}` — one of "hard_cut", "eq_sweep", "filter_fade", "loop_roll", "beat_match"
  `{transition_bars}` — int, 4, 8, or 16

  Transition-type guidance table:
  | Type | Duration | Technique | Best for |
  |------|----------|-----------|----------|
  | hard_cut | Instant | Abrupt switch | Build energy, genre change |
  | eq_sweep | 4-8 bars | HPF on outgoing, LPF on incoming | Smooth key-matched tracks |
  | filter_fade | 8-16 bars | Both filters cross | Ambient, deep house |
  | loop_roll | 4-8 bars | Loop outgoing phrase, filter drop | Techno, peak-time |
  | beat_match | 8-16 bars | Sync tempos, phrase-matched EQ | Long blends, progressive |

  Must NOT: Suggest transport controls that risk dropping out. Must NOT mention audio export.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 2, 3, 4, 5
  References:
  - Session info: `get_session_info()` → tempo, track list
  - Track info: `get_track_info(index)` → device chain, clip state
  - EQ effects: `load_instrument_or_effect(track, "query:Audio Effects#EQ Eight")`
  - Template location: `MCP_Server/prompts/dj_transition.md`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.prompts import load_prompt_template
  text = load_prompt_template('dj_transition', transition_type='eq_sweep', transition_bars=8)
  assert 'eq_sweep' in text, 'transition_type not rendered'
  assert '8' in text, 'transition_bars not rendered'
  assert 'EQ' in text, 'EQ step missing'
  assert 'crossfade' in text.lower(), 'crossfade missing'
  assert 'tempo' in text.lower(), 'tempo matching missing'

  text2 = load_prompt_template('dj_transition', transition_type='beat_match', transition_bars=16)
  assert 'beat_match' in text2, 'beat_match not rendered'
  assert '16' in text2, '16 bars not rendered'
  print('dj_transition.md template OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Load with transition_type="hard_cut" → instant cut guidance, no EQ steps
  - HAPPY: Load with transition_type="filter_fade" → filter crossfade technique
  - HAPPY: Load with transition_type="loop_roll", transition_bars=4 → loop roll with 4-bar guidance
  - FAILURE: Load with transition_bars=32 → defaults to 8 (or renders as-is)
  Evidence: `.omo/evidence/task-6-sprint-03-mcp-prompts.txt`
  Commit: Y | feat(prompts): add dj_transition.md workflow template

- [ ] 7. Register 5 `@mcp.prompt()` decorators + `get_workflow_prompt` tool in server.py
  What to do / Must NOT do:
  In `MCP_Server/server.py`:

  1. Add imports at top:
  ```python
  from mcp.types import PromptMessage, TextContent
  from MCP_Server.prompts import load_prompt_template, get_available_prompts, DEFAULT_PARAMS
  ```

  2. After `# Register tools from submodules` block (line ~775), register 5 prompts using `@mcp.prompt()`:
  ```python
  # ------------------------------------------------------------------
  # MCP Prompts — Guided workflow templates
  # ------------------------------------------------------------------

  @mcp.prompt()
  def session_setup(ctx: Context, genre: str = "techno", bpm: int = 128, track_count: int = 8, drum_pattern: str = "techno_4x4") -> list[PromptMessage]:
      """Build a new Ableton session from scratch: clean slate, tracks, instruments, patterns."""
      text = load_prompt_template("session_setup", genre=genre, bpm=bpm, track_count=track_count, drum_pattern=drum_pattern)
      return [PromptMessage(role="user", content=TextContent(type="text", text=text))]

  @mcp.prompt()
  def mix_drums(ctx: Context, drum_style: str = "techno") -> list[PromptMessage]:
      """Mix drum tracks with EQ and compression. Guides EQ Eight, Glue Compressor, and style-specific settings."""
      text = load_prompt_template("mix_drums", drum_style=drum_style)
      return [PromptMessage(role="user", content=TextContent(type="text", text=text))]

  @mcp.prompt()
  def sound_design_bass(ctx: Context, bass_type: str = "sub", synth_preference: str = "Auto") -> list[PromptMessage]:
      """Design a bass patch from scratch. Guides synth selection, oscillator settings, effects chain, and pattern creation."""
      text = load_prompt_template("sound_design_bass", bass_type=bass_type, synth_preference=synth_preference)
      return [PromptMessage(role="user", content=TextContent(type="text", text=text))]

  @mcp.prompt()
  def arrange_track(ctx: Context, structure: str = "4x4_techno", length_bars: int = 32) -> list[PromptMessage]:
      """Arrange a loop or idea into a full song structure. Guides section building, transitions, and automation."""
      text = load_prompt_template("arrange_track", structure=structure, length_bars=length_bars)
      return [PromptMessage(role="user", content=TextContent(type="text", text=text))]

  @mcp.prompt()
  def dj_transition(ctx: Context, transition_type: str = "eq_sweep", transition_bars: int = 8) -> list[PromptMessage]:
      """Professional DJ transition between two tracks. Guides tempo matching, EQ planning, and crossfade execution."""
      text = load_prompt_template("dj_transition", transition_type=transition_type, transition_bars=transition_bars)
      return [PromptMessage(role="user", content=TextContent(type="text", text=text))]
  ```

  3. Also register utility tool `get_workflow_prompt`:
  ```python
  @mcp.tool()
  def get_workflow_prompt(ctx: Context, template_name: str, **kwargs) -> str:
      """Load and render a workflow prompt template by name. Returns markdown-formatted workflow steps.

      Available templates: session_setup, mix_drums, sound_design_bass, arrange_track, dj_transition
      Use `get_available_prompts()` to list all templates.

      Examples:
      - get_workflow_prompt("session_setup", genre="house", bpm=125, track_count=6, drum_pattern="house_basic")
      - get_workflow_prompt("mix_drums", drum_style="techno")
      - get_workflow_prompt("arrange_track", structure="4x4_techno", length_bars=64)
      """
      try:
          if template_name not in get_available_prompts():
              return json.dumps({"status": "error", "message": f"Template '{template_name}' not found. Available: {get_available_prompts()}"}, indent=2)
          # Merge kwargs with defaults for any missing params
          default_params = DEFAULT_PARAMS.get(template_name, {})
          merged = {**default_params, **kwargs}
          text = load_prompt_template(template_name, **merged)
          return json.dumps({"status": "success", "template": template_name, "content": text}, indent=2)
      except FileNotFoundError:
          return json.dumps({"status": "error", "message": f"Template file '{template_name}.md' not found"}, indent=2)
      except KeyError as e:
          return json.dumps({"status": "error", "message": f"Missing required parameter: {e}"}, indent=2)
      except Exception as e:
          return json.dumps({"status": "error", "message": str(e)}, indent=2)
  ```

  Must NOT: Modify existing tool bodies. Must NOT add new Remote Script handlers. Must NOT change the `get_ableton_connection` pattern.

  Parallelization: Wave 2 | Blocked by: 1, 2, 3, 4, 5, 6 | Blocks: 8 | Can parallelize with: None
  References:
  - FastMCP instance: `MCP_Server/server.py:751` mcp = FastMCP(...)
  - Existing submodule registration pattern: `MCP_Server/server.py:756-775`
  - Imports section: top of `MCP_Server/server.py` (~line 11-30)
  - Context type: `from mcp.server.fastmcp import Context` (already imported at line 11)
  - PromptMessage/TextContent: `from mcp.types import PromptMessage, TextContent`
  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  import re
  code = open('MCP_Server/server.py').read()
  prompt_count = len(re.findall(r'@mcp\.prompt\(\)', code))
  assert prompt_count >= 5, f'Expected >=5 @mcp.prompt() decorators, got {prompt_count}'
  assert 'get_workflow_prompt' in code, 'get_workflow_prompt tool missing'
  assert 'from MCP_Server.prompts import' in code, 'prompts import missing'
  assert 'from mcp.types import PromptMessage, TextContent' in code or 'from mcp.types import' in code, 'PromptMessage import missing'
  print(f'{prompt_count} @mcp.prompt() decorators found')
  print('get_workflow_prompt tool found')
  print('Prompts registered via @mcp.prompt():', re.findall(r'def (\w+)\(ctx: Context', code[code.index('@mcp.prompt()'):]))
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call `get_workflow_prompt("session_setup", genre="house", bpm=125)` → returns rendered markdown with steps
  - HAPPY: Call `get_workflow_prompt("mix_drums")` → returns rendered template with default "techno" style
  - FAILURE: Call `get_workflow_prompt("nonexistent")` → returns error with available templates list
  - FAILURE: Call `get_workflow_prompt("session_setup", invalid_param=True)` → renders with {invalid_param} left as-is (graceful)
  Evidence: `.omo/evidence/task-7-sprint-03-mcp-prompts.txt`
  Commit: Y | feat(prompts): register 5 MCP Prompts + get_workflow_prompt tool

- [ ] 8. Create `tests/test_prompts.py`
  What to do / Must NOT do:
  Create `tests/test_prompts.py` with the following test cases (follow the existing standalone test pattern — no pytest discovery):

  Tests:
  1. `test_prompt_loading_system()` — verify `load_prompt_template` and `get_available_prompts` work
  2. `test_session_setup_renders_all_params()` — load with all 4 params, verify each is rendered
  3. `test_session_setup_workflow_steps()` — verify all 7 workflow steps are present
  4. `test_mix_drums_renders_style()` — load each drum_style, verify style-specific content
  5. `test_sound_design_bass_renders_all_types()` — load each bass_type, verify correct oscillator/envelope guidance
  6. `test_arrange_track_renders_structure()` — load each structure, verify correct section layout
  7. `test_dj_transition_renders_type()` — load each transition_type, verify technique guidance
  8. `test_get_available_prompts_returns_five()` — verify all 5 prompts are discoverable
  9. `test_invalid_template_raises_error()` — verify FileNotFoundError for missing template
  10. `test_param_defaults_merged()` — test that DEFAULT_PARAMS are used when kwargs omitted

  Must NOT: Require pytest or external test runners. Must use `python test_prompts.py` as standalone invocation.
  Each test function must print "PASS: <test_name>" on success and "FAIL: <test_name>: <reason>" on failure with `sys.exit(1)` for failures.

  Parallelization: Wave 2 | Blocked by: 1, 7 | Blocks: None | Can parallelize with: None
  References:
  - Existing standalone test pattern: `scripts/test/test_connection.py` (standalone, no pytest)
  - Test directory: `tests/` (already exists with other tests)
  - Template loading API: `MCP_Server.prompts.load_prompt_template`, `MCP_Server.prompts.get_available_prompts`
  Acceptance criteria (agent-executable):
  ```bash
  python tests/test_prompts.py
  # Expected output: All 10 tests PASS
  # Exit code 0 on success, 1 on failure
  ```
  QA scenarios: happy + failure
  - HAPPY: Run tests with all templates created → all 10 tests pass, printed PASS lines
  - FAILURE: Missing template file → specific test fails with FileNotFoundError
  Evidence: `.omo/evidence/task-8-sprint-03-mcp-prompts.txt`
  Commit: Y | test(prompts): add test suite for prompt loading, rendering, and template content

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: Verify all 8 deliverables exist, all scope boundaries respected
- [ ] F2. Prompt count audit: `grep -c "@mcp.prompt()" MCP_Server/server.py` == 5
- [ ] F3. Rendering test: Run `python tests/test_prompts.py` — all tests pass
- [ ] F4. Syntax check: All .py files pass `python -c "compile(open(f).read(), f, 'exec')"` for `MCP_Server/server.py`, `MCP_Server/prompts/__init__.py`, `tests/test_prompts.py`
- [ ] F5. Scope fidelity: grep for Must NOT have violations (no executable code in .md files, no jinja2 imports, no tool body modifications)

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(prompts): add prompt rendering system with caching and template loading
- feat(prompts): add session_setup.md workflow template
- feat(prompts): add mix_drums.md workflow template
- feat(prompts): add sound_design_bass.md workflow template
- feat(prompts): add arrange_track.md workflow template
- feat(prompts): add dj_transition.md workflow template
- feat(prompts): register 5 MCP Prompts + get_workflow_prompt tool
- test(prompts): add test suite for prompt loading, rendering, and template content

No squashing — each commit is independently testable. Tags: none.

## Success criteria
- `grep -c "@mcp.prompt()" MCP_Server/server.py` == 5
- `python tests/test_prompts.py` exits with code 0 (all 10 tests pass)
- `load_prompt_template("session_setup", genre="techno", bpm=130)` renders "techno" and "130" in output
- `load_prompt_template("mix_drums", drum_style="techno")` contains style-specific compressor settings
- `get_workflow_prompt("session_setup", genre="house", bpm=125)` returns valid JSON with "status": "success" and "content" with workflow steps
- `get_workflow_prompt("nonexistent")` returns error JSON with available templates list
- `get_available_prompts()` returns `["arrange_track", "dj_transition", "mix_drums", "session_setup", "sound_design_bass"]`
- No external dependencies added for template rendering
- No executable commands in .md template files
