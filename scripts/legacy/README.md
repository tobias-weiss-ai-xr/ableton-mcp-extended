# Legacy one-off scripts

Single-use scripts that were run once against a live Ableton session and kept for
reference. They are **not** part of the packaged API (`pyproject.toml` packages only
`MCP_Server`, `elevenlabs_mcp`, `agentic_mix`), are not covered by tests, and may
reference track indices or clip layouts that no longer exist in any session.

Use them for the pattern, not as a command reference. For maintained equivalents:

| Legacy script | Use instead |
|---------------|-------------|
| `create_ableton_fine_dub.py`, `create_final_fine_dub.py`, `create_complete_reggae.py`, `create_reggae_with_midi.py`, `fine_dub_generator.py` | `scripts/fill_808_reggae_bass.py`, `scripts/build_dub_techno_bass.py` |
| `run_basic_demo.py`, `run_demo_clean.py`, `run_demo_now.py` | `scripts/quick_arrangement_demo.py` |
| `INVENTORY_SCRIPT.py`, `instruments_addressed.py` | `get_browser_*` commands + `MCP_Server/browser_cache.py` |
| `session_setup.py`, `session_auto-save.py` | `scripts/create_base_session.py` |
| `restart_ableton.py`, `restart_ableton_simple.py`, `restart_ableton.bat` | Reload the Remote Script from Live's Preferences (see `AGENTS.md`) |
| `_debug_integration.py` | `scripts/test/` |

Behavioural note that still applies everywhere: these scripts send raw commands over
TCP 9877 with `{"type": cmd, "params": {...}}` and genuine device values in each
device's native range — not normalized `0.0-1.0`.
