# Transfer Options: Music-Research Corpus → Ableton MCP Extended

Comprehensive mapping from 51-paper music-research corpus to concrete improvements.
Source: [music-research](https://github.com/tobias-weiss-ai-xr/music-research)

---

## Priority Matrix

| # | Paper | Transfer | Effort | Impact | Status |
|---|-------|----------|--------|--------|--------|
| 1 | MERT (2306.00107) | Semantic audio embeddings in feedback loop | Low | **High** | ✅ Implemented |
| 2 | GraphIDyOM (2607.25787) | Expectation-based chord suggestions | Low | **High** | ✅ Implemented |
| 3 | Libretto (2606.22708) | Symbolic grammar layer for agentic pipeline | Medium | **High** | 🔲 Planned |
| 4 | AgentFlow (npm package) | DAG/circuit-breaker/checkpoint orchestration | Medium | **High** | ✅ Implemented |
| 5 | WeaveMuse (2509.11183) | Multi-agent architecture for agentic_mix | High | **High** | 🔲 Planned |
| 5 | CompLex (2508.19603) | Agent-built music theory lexicon | Medium | Medium | 🔲 Planned |
| 6 | SongFormer (2510.02797) | Auto-detect section boundaries in Live Sets | Low | Medium | 🔲 Planned |
| 7 | Groove Ratings (2603.27237) | Groove scoring for drum patterns | Low | Medium | 🔲 Planned |
| 8 | ChatMusician (2402.16153) | Music-aware LLM prompting for MCP | Low | Medium | 🔲 Planned |
| 9 | Museformer (2210.10349) | Attention-based melody generation | Medium | Medium | 🔲 Planned |
| 10 | Music Transformer (1809.04281) | Relative attention for long-clip generation | Medium | Medium | 🔲 Planned |
| 11 | MUSE Benchmark (2510.19055) | Benchmark LLM music understanding in agent decisions | Low | Medium | 🔲 Planned |
| 12 | Preference Alignment (2511.15038) | RLHF-style tuning of arrangement agent | Medium | Medium | 🔲 Planned |
| 13 | MuScriptor (2607.08168) | Audio→MIDI transcription for agent editing | Medium | Medium | 🔲 Planned |
| 14 | Music Flamingo (2511.10289) | Richer audio descriptions for feedback loop | Medium | Medium | 🔲 Planned |
| 15 | AgentFlow Orchestration | DAG + circuit breakers + checkpoint for mix pipeline | Medium | **High** | ✅ Implemented |
| 16 | Full-Song Framework (2607.20253) | Lyrics-to-song with vocal generation | High | Low | 🔲 Planned |
| 17 | Diff-Symbo (2608.05222) | Diffusion-based symbolic generation | High | Low | 🔲 Planned |
| 18 | MindMelody (2605.01235) | EEG biofeedback in audio loop | High | Low | 🔲 Planned |

---

## Detailed Options

### ✅ Option 1 — MERT Semantic Embeddings in Feedback Loop [DONE]
**Paper:** MERT: Acoustic Music Understanding Model (Li et al., 2023) — arXiv:2306.00107
**What:** Self-supervised music embeddings encoding harmony, timbre, rhythm, emotion
**Transfers to:** `MCP_Server/audio_analysis/` → `agentic_mix/nodes/analyze_adapt.py`
**Why:** Current feedback loop only uses RMS + spectral features. MERT adds *semantic understanding* — detect tension/release, genre feel, mood — enabling richer adaptive decisions
**Effort:** ~150 lines. Load MERT model (transformers), extract embeddings from audio buffer, add `semantic_features` to `AudioAnalyzer.get_analysis()`, feed into `analyze_and_adapt_node`

### ✅ Option 2 — GraphIDyOM Expectation-Based Chord Suggestions [DONE]
**Paper:** GraphIDyOM (Rosselló, 2026) — arXiv:2607.25787
**What:** Information-theoretic musical expectation — surprise/entropy scores per chord
**Transfers to:** `music_theory/harmonization.py` → `suggest_next_chord()`
**Why:** Current chord suggestions use fixed Roman-numeral progressions. Adding expectation scores lets the agent choose chords that are "surprising but expected" — better tension/release than random selection
**Effort:** ~120 lines. Build context model from chord history, compute information content per candidate, rank suggestions by optimal surprise (0.3-0.7 bits)

---

### 🔲 Option 3 — Libretto Symbolic Grammar Layer
**Paper:** Libretto (Xu, 2026) — arXiv:2606.22708
**What:** LLM-native grammar with bars, voices, onset slots — agent-manipulable representation
**Transfers to:** `agentic_mix/nodes/` — new `SessionGrammar` layer between `construct_arrangement` and `generate_clips`
**Why:** Fixes the representation gap: arrangement decisions are currently opaque between nodes. A grammar layer makes them **inspectable and editable** before committing MIDI
**Effort:** ~400 lines. New `grammar.py` module, `plan_grammar_node` and `render_grammar_node`, integration into LangGraph pipeline

### ✅ Option 4 — AgentFlow Orchestration for Agentic Mix (replaces LangGraph)
**Package:** [agentflow](https://github.com/tobias-weiss-ai-xr/agentflow) (npm, formerly TaskFleet)
**What:** DAG-based workflow engine, circuit breakers, event bus, state machines, checkpoint persistence
**Transfers to:** `orchestration/` — new orchestration layer wrapping `agentic_mix/` nodes
**Why:** Current LangGraph pipeline is a linear chain with no resilience (Ableton MCP failures crash the mix). AgentFlow adds:
- **Circuit breakers** — auto-retry when Ableton MCP calls fail (e.g., transport control, clip creation)
- **Checkpoint/restore** — resume long 2-hour mixes after crashes
- **DAG execution** — specialist agents run as parallel DAG tasks instead of linear chain
- **Event bus** — loose coupling between arrangement, mixing, and audio analysis
**Effort:** ~600 lines implemented. Node.js bridge + Python agent server + circuit breaker
**Architecture:**
- `orchestration/agentflow_bridge/` — Node.js bridge using agentflow npm package
- `orchestration/agentflow_runner.py` — Python runner (starts bridge, submits workflow, polls)
- `orchestration/circuit_breaker.py` — Per-operation circuit breakers for Ableton MCP
- CLI: `--orchestrator agentflow` (default: langgraph for backward compat)
**Note:** AgentFlow is TypeScript; agentic_mix is Python. Integration via HTTP subprocess invoker (Node.js bridge calls Python agent server on localhost).

### 🔲 Option 5 — WeaveMuse Multi-Agent Architecture
**Paper:** WeaveMuse (Karystinaios, 2025) — arXiv:2509.11183
**What:** Specialist agents (one per concern) + manager agent coordinates
**Transfers to:** `agentic_mix/` — refactor linear chain into specialist/manager pattern
**Why:** Current pipeline is monolithic. Specialist agents (drums, harmony, FX, mixing) enable independent improvement and clearer reasoning
**Effort:** ~800 lines (significant refactor). New agent classes, manager node, state protocol changes. **Prerequisite (Option 4) now implemented**

### 🔲 Option 5 — CompLex Auto Music Theory Lexicon
**Paper:** CompLex (Hu et al., 2025) — arXiv:2508.19603
**What:** Multi-agent system builds 37K music-theory items from 9 keywords
**Transfers to:** `music_theory/exotic_scales.py`, `extensions.py`, `voicing.py`
**Why:** Hand-maintained theory tables could be augmented/validated by an agent pipeline that discovers voicings, scale compatibilities, and voice-leading patterns
**Effort:** ~500 lines. Agent pipeline + integration with existing theory modules

### 🔲 Option 6 — SongFormer Auto Section Detection
**Paper:** SongFormer (Hao et al., 2025) — arXiv:2510.02797
**What:** Music structure analysis from heterogeneous supervision
**Transfers to:** `MCP_Server/arrangement_tools.py` — new auto-section-tagging feature
**Why:** Detect section boundaries (verse/chorus/build) in existing Live Sets. Currently users manually tag sections
**Effort:** ~200 lines. New tool that analyzes clip content + audio to suggest section types

### 🔲 Option 7 — Groove Ratings for Drum Generation
**Paper:** Can pre-trained DL models predict groove ratings? (Marmoret et al., 2026) — arXiv:2603.27237
**What:** DL models predict groove perception from audio embeddings
**Transfers to:** `MCP_Server/advanced_tools.py` → `generate_drum_pattern()`
**Why:** Add a `groove` parameter (0.0-1.0) to drum pattern generation. Use pretrained embeddings or a lightweight groove classifier
**Effort:** ~150 lines. Optional pretrained model + groove scoring in pattern generator

### 🔲 Option 8 — ChatMusician Music-Aware LLM Prompting
**Paper:** ChatMusician (Yuan et al., 2024) — arXiv:2402.16153
**What:** LLM with intrinsic music ability via ABC notation tokenizer
**Transfers to:** MCP prompt templates, LLM system prompts
**Why:** The LLM driving Ableton via MCP could use music-aware prompting — describe arrangements in ABC notation for the LLM to understand and reason about
**Effort:** ~100 lines. Prompt template updates, optional ABC notation bridge

### 🔲 Option 9 — Museformer Attention-Based Melody Generation
**Paper:** Museformer (Yu et al., 2022) — arXiv:2210.10349
**What:** Fine/coarse attention for long symbolic sequences
**Transfers to:** `MCP_Server/advanced_tools.py` → `generate_melody_clip()`
**Why:** Replace template/random melody generation with attention-based model that respects long-range musical structure
**Effort:** ~400 lines. Local model + inference in melody generator

### 🔲 Option 10 — Music Transformer Relative Attention
**Paper:** Music Transformer (Huang et al., 2018) — arXiv:1809.04281
**What:** Relative attention captures repetition at multiple timescales
**Transfers to:** `generate_melody_clip()`, `generate_bass_line()` — long clip coherence
**Why:** Generated clips longer than 8 bars lose coherence. Relative attention naturally handles repetition/variation structure
**Effort:** ~400 lines. Similar to Option 9 — could be combined

### 🔲 Options 11-17 — See table above for details

---

## Already Implemented (from previous session)

| # | Paper | Module | Change |
|---|-------|--------|--------|
| 1 | BeatEdit (2607.11124) | clip_tools.py | Non-destructive clip editing |
| 2 | MusicLayout (2608.09035) | create_10min_mix.py | Scene-based arrangement |
| 3 | Preference Alignment (2511.15038) | polish_suite.py | Polish scoring rubric |
| 4 | LLM Chord CoT (2509.18700) | harmonization.py | Multi-step harmonization |
| 5 | SAGE-Music (2510.00395) | midi_effects.py | Low-latency arpeggiator |

---

*Generated: 2026-08-16. Source: music-research corpus (51 papers).*
