# 1. Introduction and Goals

## 1.1 Overview

**Ableton MCP Extended** bridges AI assistants (Claude, Cursor, any MCP-compatible
client) to **Ableton Live** for music production. It exposes Live's session view,
arrangement view, transport, devices, MIDI, and browser as Model Context Protocol
(MCP) tools, so an LLM can create tracks, program drums, load instruments, generate
full mixes, and perform live parameter automation — all through natural language.

The project extends the upstream `ableton-mcp` (by Matt Twomey / uisato) with a much
larger tool surface, a dual TCP/UDP transport, an agentic mix-generation pipeline
(LangGraph + AgentFlow), ElevenLabs voice integration, and a library of
production-grade helper modules (arrangement, fat-beatz mastering, optimization).

## 1.2 Goals

| # | Goal | Satisfied by |
|---|------|--------------|
| G1 | Let an LLM drive Ableton Live end-to-end (create → arrange → mix) | 250+ MCP tools across 14 modules |
| G2 | Provide both **reliable** and **low-latency** command channels | Dual TCP (9877) + UDP (9878) servers |
| G3 | Generate complete multi-minute mixes autonomously | `agentic_mix` LangGraph pipeline + `orchestration` AgentFlow runner |
| G4 | Support dub-techno, house, techno, ambient, hip-hop genres | Genre templates, drum patterns, music-theory engine |
| G5 | Integrate AI voice/SFX generation | `elevenlabs_mcp` server |
| G6 | Remain robust against Live API version differences | Three-tier fallback for capture, command registry contracts |
| G7 | Be installable and reproducible | `pyproject.toml`, CI lint + validation + tests |

## 1.3 Non-Goals (out of scope)

- **Audio file export to MP3/WAV via the Remote Script API** — fundamentally
  impossible; handled by Max for Live device or manual export (see §11).
- **A GUI** — the project is entirely headless / API-driven.
- **Multi-host Ableton control** — one Live instance per MCP server (localhost only).
- **Replacing a DAW** — the system orchestrates Live; it is not a DAW itself.

## 1.4 Stakeholders

| Role | Interest |
|------|----------|
| Producer / musician | Natural-language control of Live; generative composition |
| AI-assistant user | A rich, well-documented MCP tool surface |
| Developer / contributor | Extensible tool modules, test coverage, clear architecture |
| Upstream maintainer (uisato) | Base `ableton-mcp` extended without breaking changes |

## 1.5 Top-level requirements summary

1. **R1 – Tool breadth:** ≥ 100 MCP tools covering session, tracks, clips, devices,
   browser, transport, arrangement, automation, audio analysis, and generation.
2. **R2 – Transport split:** Critical/feedback operations over TCP; high-frequency
   reversible parameter updates over UDP (10-command whitelist).
3. **R3 – Agentic generation:** Produce structured arrangements (sections, clips,
   automation) for a target genre/length without human intervention.
4. **R4 – Live 11–12 compatibility:** Degrade gracefully when newer Live 12 APIs
   (e.g. `capture_to_arrangement`) are unavailable.
5. **R5 – Determinism:** Same inputs + same Live state → same musical result
   (modulo timing jitter from UDP).
6. **R6 – Installability:** `pip install -e .` exposes `ableton-mcp-extended` and
   `langgraph-mix` console entry points.
