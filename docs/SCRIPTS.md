# Scripts

`scripts/` is not a package (`pyproject.toml` packages only `MCP_Server`,
`elevenlabs_mcp`, `agentic_mix`) — run these directly:

```bash
.venv/Scripts/python.exe scripts/<name>.py [--flags]
```

Most talk to a **live Ableton session** on TCP 9877 (UDP 9878) and need the Remote
Script enabled. Run them from the repo root: they do
`sys.path.insert(0, <repo root>)` to import `mcp_client`.

## Tier 1 — maintained, re-runnable

These are idempotent, resolve their target track by name, and verify their own
readback. Use them as the pattern for new work.

| Script | Does |
|--------|------|
| `build_dub_techno_bass.py` | Builds the dub-techno bass channel: instrument + FX chain (Sub Bass Drone → Saturator → Auto Filter → Echo → Reverb), sets 43 parameter values, writes 4 × 16-bar Bb-minor basslines (root-pulse / steppers / dub-wash / rolling). `--track N`, `--skip-chain`. |
| `fill_808_reggae_bass.py` | 10 × 16-bar reggae bassline clips from 8 one-bar cells (foundation, skank, dub_sparse, octave_pop, walk, steppers, fill, deep_drop) with dropout variants. |
| `fill_64pad_percussion.py` | 10 × 16-bar percussion grooves for the 64-Pad-Kit racks, 4 density styles, tom fills and a dub dropout bar. |
| `create_bass_clips.py`, `create_drum_clips.py`, `create_pad_clips.py`, `create_percussion_clips.py`, `create_dub_fx_clips.py` | Section-specific clip generators built on the same pattern. |
| `create_base_session.py` | Sets up a clean session skeleton. |
| `check_repo_hygiene.py` | Verifies nothing stray landed in the repo root. Run before committing. |

## Tier 2 — mix and arrangement pipelines

| Script | Does |
|--------|------|
| `e2e_mix_producer.py` | End-to-end mix production run. |
| `production_pipeline.py`, `production_pipeline_quick.py` | Mix → MP3 → video → upload chain (see `PIPELINEREADME.md`). |
| `mix_master.py`, `polish_suite.py`, `polish_live_set.py` | Mix balancing, stereo imaging, polish scoring. |
| `create_10min_mix*.py`, `create_90min_dub_techno*.py`, `create_5min_dub.py` | Long-form automated mixes. |
| `create_smart_mix.py`, `genre_mix_generator*.py` | Adaptive / genre-templated mixes. |
| `quick_arrangement_demo.py` | Smallest working session→arrangement demo. |
| `session_archive.py`, `session_stats.py`, `configure_follow_actions.py` | Session bookkeeping. |

## Tier 3 — probes and one-off diagnostics

`probe_*.py` (capture behaviour, LOM automation, duplicate notes, transfer
performance), `verify_notes.py`, `rework_clips_direct.py`, `reggae_solution.py`,
`direct_ableton_generator.py`, `enhanced_reggae_generator.py`,
`ai_reggae_generator.py`, `ableton_*.py`, `build_live_set.py`, `quick_test.py`,
`get_device_param_indices.py`, `add_drums_direct.py`.

Useful starting point, but track indices and clip layouts are hardcoded per session
and rot. Read them as recipes.

## Subfolders

| Folder | Contents |
|--------|----------|
| `test/` (24) | Standalone connectivity/protocol/UDP checks — no pytest discovery, run directly (e.g. `test/test_connection.py`) |
| `util/` (15) | Session inspection and Remote Script reload helpers (`check_session_state.py`, `reload_remote_script.py`, `verify_instruments.py`) |
| `analysis/` (7) | Audio-analysis rules engine, plugin param polling, benchmarks (has its own README) |
| `drum_tools/` (6) | Drum-kit specific experiments |
| `legacy/` (15) | Former root one-offs — not maintained, see its README for replacements |

## Shared building blocks

| Module | Purpose |
|--------|---------|
| `mcp_client.py` (repo root) | `MCPClientTCP` (9877, `send_command(type, params)`), `MCPClientUDP` (9878). Reads until the JSON payload parses — large responses are never truncated. |
| `clip_patterns.py`, `automation_patterns.py`, `parameter_sweeps.py`, `pattern_orchestration.py`, `follow_actions.py` | Pattern/sweep helpers imported by scripts |
| `audio_analysis.py` (repo root) | Analysis entry point; engine lives in `MCP_Server/audio_analysis/` |
| `error_handling.py` | Shared retry/error helpers |

## Session-change caveats

The Remote Script cannot export audio, and real-time `capture_and_insert_arrangement`
falls back to 10 seconds of recording — see `AGENTS.md`. Scripts that depend on
existing clip/scene layouts will silently do nothing useful if the session was
reset; check with `scripts/util/check_session_state.py` first.
