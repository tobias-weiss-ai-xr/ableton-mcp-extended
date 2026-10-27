# Research Findings: GitHub & Online Resources for ableton-mcp-extended

*Method: GitHub API repo search + README analysis of top projects, gap analysis
against this repo's ~266 tools.*

## Projects surveyed

| Stars | Repo | What it is | Status in this repo |
|------:|------|------------|---------------------|
| 3136 | ahujasid/ableton-mcp | The original MCP for Live; track/clip/arrangement basics | Fully covered + exceeded |
| 528 | leolabs/ableton-js | Node.js Live control via M4L/OSC | N/A (we're Python) |
| 438 | ideoforms/isobar | Python pattern library: Euclidean, L-systems, Markov, Timeline | Mostly covered |
| 395 | Simon-Kansara/ableton-live-mcp-server | OSC-based MCP server | Alternative transport |
| 274 | uisato/ableton-mcp-extended | Likely our upstream origin | - |
| 227 | bschoepke/ableton-live-mcp | General-purpose MCP bridge | Covered |
| 76 | dreamrec/LivePilot | 474 tools, audio listening, taste learning, version A/B | **Partial - best ideas here** |
| 53 | jpoindexter/ableton-mcp | 200+ tools, near-full LOM: rack macros, drum pads, Simpler, fade, take lanes | **Best feature checklist** |
| 37 | fadelabs/phantom | Audio measurement MCP: LUFS, masking, phase, reference matching, Demucs stems | **Partial - we have LUFS, not the rest** |
| 34 | glincker/ableton-skills | Claude Skills for producers (workflow prompts, not code) | Worth reading for skill patterns |
| 17 | Ziforge/ableton-liveapi-tools | 220 LiveAPI tools, thread-safe queue, take lanes, annotations | Reference for Live 12 APIs |
| 16 | sunflower-of-parchman/codex-live-bridge | Local-first M4L OSC bridge | Alternative to our max_bridge |
| 2 | pawelknorps/maxmsp-mcp | MCP for Max/MSP, 75 tools, templates, undo | Pattern for max_bridge expansion |

## Gap analysis - what we ALREADY have (don't rebuild)

- Euclidean rhythms (`music_generation.py`: `euclidean_rhythm`, `generate_euclidean_pattern`)
- Markov chains 1st + 2nd order with diatonic transitions, pattern classes
- Groove pool: list/apply/remove grooves, global groove amount (`groove_tools.py`)
- LUFS + loudness analysis, frequency collisions, level snapshots (`audio_analysis_tools.py`)
- Output metering (mixer_tools), freeze track (optimization_tools), fades
- Asset index: fuzzy search, usage popularity, scene presets, preload (`asset_index.py`)
- Genre effect chains incl. dedicated dub techno return/master chains (`effect_management.py`)
- Command registry with TCP/UDP validation (`command_registry.py`)
- OSC bridge to Max for Live with allowlist (`max_bridge.py`)
- Follow actions: random/energy/harmonic setups
- Crossfader + track crossfade assign, arrangement view position

## Confirmed gaps, prioritized for dub techno live use

### Tier 1 - direct live-performance value

1. **Rack macro control** (`macro`: 0 hits anywhere)
   `RackDevice.macros[i]` -> get/set name+value. A dub filter-sweep macro or FX-send
   macro mapped to one knob is THE dub performance gesture. One remote-script handler
   + 2-3 tools (`get_rack_macros`, `set_rack_macro`, `set_rack_macro_by_name`).
   Source: jpoindexter.

2. **Drum rack pad control** (only `can_have_drum_pads` checked, no pad ops)
   `DrumDevice.drum_pads` -> mute/solo/name per pad, `get_drum_pad_info`. Enables
   muting kick/hat per pad for builds/breaks without track-level mutes.
   Source: jpoindexter, Ziforge.

3. **View & selection control** (`set_view`: 0; only one `focus_view("Arranger")`
   and a `selected_track` assignment inside `load_browser_item`)
   `song.view.selected_track/scene/detail_clip`, `app.view.focus_view("Session"/"Arranger")`,
   `show_view("Detail/Clip")`. Needed to script the live workflow (select -> arm -> focus).
   Source: jpoindexter, Ziforge.

4. **Clip fades for audio clips** (`clip_fade`: 0)
   `clip.fade_in/fade_out` - essential for the live-recorded takes we already capture
   into arrangement (see `create_live_dub_8lanes.py` workflow). Source: jpoindexter.

### Tier 2 - production quality

5. **Mix reference comparison / A-B**
   LivePilot's core loop: "Make the change. Hear what happened. Keep what works."
   We have LUFS + spectrum analyzers but no snapshot->compare->report tool. Add
   `snapshot_mix_state` + `compare_mix_snapshots` (LUFS delta, band balance delta).
   phantom's genre profiles as reference targets - a dub techno profile is one YAML.

6. **Problem detection beyond frequency collisions**
   phantom checks clipping, DC offset, mains hum, noise, stereo polarity, masking
   ranking (weighted octave-band overlap). Our `analyze_frequency_collisions` covers
   one slice; extend `audio_analysis/analyzer.py` with polarity + clipping + masking-rank.

7. **MIDI file import/export** (0 hits)
   isobar does this via mido. Lets dub patterns travel between scripts, DAWs, and the
   generative engine. Also enables "load pattern set from disk" instead of hard-coded
   CLIPS dicts.

### Tier 3 - nice to have

8. **Stem separation** (0) - Demucs as optional extra like phantom's `[separation]`.
9. **L-systems** (0) - our Markov + Euclidean cover most dub needs; add only if
   evolving textures become a focus.
10. **Take lanes** (0, Live 12+) - comping; low priority.
11. **Track annotations** (0) - metadata text; trivial via Ziforge reference.
12. **Punch in/out** (0) - recording workflow; skip.

## Architectural ideas worth stealing (not features)

- **LivePilot's context economy**: 474 tools but advertises only ~28 entry points per
  session; rest stay searchable/callable. Our 266-tool MCP server could adopt the same
  pattern (small curated surface + search) to cut client context bloat.
- **Ziforge's queue-based thread safety** in the Remote Script - explicit queue design
  handles schedule_message races (relevant to our "Changes cannot be triggered by
  notifications" bug).
- **jpoindexter's 3 interfaces from one backend**: MCP + REST + M4L chat device. Our
  `command_registry.py` already centralizes command specs - a REST shim would be small
  FastAPI, useful for scripts that bypass MCP.
- **phantom's optional-extras pattern** (`[processing]`, `[separation]`): heavy audio
  deps as extras, core stays light. Apply to audio_analysis for librosa/Demucs.
- **glincker/ableton-skills**: workflow-level Skills (not tools). Ship skills like
  "build a dub session" that orchestrate our existing tools.

## Known bugs to fix first (blockers found this session)

- `build_arrangement`: `duplicate_clip_to_arrangement` fails after first call per track
  ("Changes cannot be triggered by notifications") -> defer each call via
  `schedule_message` (Ziforge's queue pattern).
- `get_device_parameters` returns device[0] for all indices -> breaks automation param
  resolution on multi-device tracks.
- `delete_device` broken on RackDevices.

## Recommended adoption order

1. Rack macro + drum pad tools (Tier 1, small diff, big dub payoff)
2. Fix the 3 bugs above (they block the automation/arrangement roadmap)
3. View/selection + clip fades (completes the live workflow)
4. Mix snapshot/compare with a dub techno reference profile (phantom-style)
5. MIDI file I/O (mido; unlocks pattern portability)
6. Context-economy tool curation for the MCP surface
