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

## 6. Semantic Audio Feedback [NEW]

**Paper:** MERT: Acoustic Music Understanding Model (Li et al., 2023) — arXiv:2306.00107
- **Key Contribution:** Self-supervised music embeddings encoding harmony, timbre, rhythm, emotion
- **Application:** Semantic understanding in the audio feedback loop — mood/groove/timbre detection beyond RMS
- **Code:** music_theory/mert_analyzer.py, agentic_mix/audio_capture.py, agentic_mix/nodes/analyze_adapt.py
- **Status:** Implemented (graceful fallback without transformers/torch)
- **How it works:** MertAnalyzer loads MERT-v1-95M, extracts 768-dim embeddings from audio, projects onto harmonic (tonic/chroma), rhythmic (groove/activity), timbral (brightness/warmth), and emotional (valence/arousal/mood) features. The analyze_and_adapt_node uses these for adaptive suggestions: "tension too high → add breakdown", "low groove → tighten drums", "bright → roll off highs".

## 7. Expectation-Based Chord Suggestions [NEW]

**Paper:** GraphIDyOM — A graph-native Python reimplementation of IDyOM for musical expectation modelling (Rosselló, 2026) — arXiv:2607.25787
- **Key Contribution:** Information-theoretic musical expectation — surprise/entropy per chord transition
- **Application:** Chord suggestions ranked by "optimal surprise" — interesting but contextually appropriate
- **Code:** music_theory/expectation_model.py
- **Status:** Implemented
- **How it works:** ChordExpectationModel computes information content (IC = -log2(P(chord|context))) combining transition probability tables (by style: pop/jazz/classical/electronic), scale membership, voice-leading distance, and recency penalty. The "optimal surprise" zone (0.3-0.7 IC) identifies chords that are unexpected enough to be interesting but not jarring. Integrates with existing suggest_next_chord() via suggest_chords_with_expectation().

## References

All papers from: C:/Users/Tobias/git/music-research/papers.yaml
Full mapping table: docs/research/GROUNDING.md
Transfer options: docs/research/TRANSFER_OPTIONS.md
Last updated: August 2026
