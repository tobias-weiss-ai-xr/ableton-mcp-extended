# Music Theory Research Notes

Grounding Ableton MCP Extended in Music Research Literature

This document summarizes how specific papers from the music-research corpus map to Ableton MCP Extended modules.

## Overview

This research grounding connects the music-research corpus (C:/Users/Tobias/git/music-research) to the Ableton MCP Extended codebase.

## 1. Non-Destructive Clip Editing

**Paper:** BeatEdit - Symbolic Music Generation as Explicit Editing (Gu et al., 2026)
- URL: https://arxiv.org/abs/2607.11124
- **Key Contribution:** Generation as explicit editing with beat-grid-anchored BEAT encoding
- **Application:** Non-destructive clip editing roadmap
- **Code:** MCP_Server/commands.py, MCP_Server/clip_tools.py, music_theory/harmonization.py

## 2. Arrangement Planning

**Paper:** MusicLayout - Explicit Structural Planning (Li et al., 2026)
- URL: https://arxiv.org/abs/2608.09035
- **Key Contribution:** Time-aligned layout with sections, textures, repetitions, variations
- **Application:** create_10min_mix scene-based arrangement
- **Code:** scripts/create_10min_mix.py, scripts/genre_mix_generator_fixed.py

## 3. Evaluation and Scoring

**Papers:**
- Aligning Generative Music AI with Human Preferences (Herremans and Roy, 2025) arXiv:2511.15038
- A Survey on Evaluation Metrics for Music Generation (Kader and Karmaker, 2025) arXiv:2509.00051
- **Application:** polish_suite scoring rubric
- **Code:** scripts/polish_suite.py

## 4. Chord Recognition

**Paper:** Enhancing Automatic Chord Recognition through LLM Chain-of-Thought Reasoning (Chang et al., 2025)
- URL: https://arxiv.org/abs/2509.18700
- **Application:** harmonization.py multi-step process
- **Code:** music_theory/harmonization.py

## 5. Low-Latency Generation

**Paper:** SAGE-Music (Tan et al., 2025)
- URL: https://arxiv.org/abs/2510.00395
- **Application:** midi_effects.py arpeggiator
- **Code:** MCP_Server/midi_effects.py

## References

All papers from: C:/Users/Tobias/git/music-research/papers.yaml
Last updated: August 2026
For full mapping table: docs/research/GROUNDING.md
