"""
Analyze and adapt node - Evaluate mix and make adaptive decisions.

Augmented with MERT semantic features (Li et al., 2023 — arXiv:2306.00107)
for richer feedback beyond RMS/energy analysis.
"""
from agentic_mix.state import GraphState


def analyze_and_adapt_node(state: GraphState) -> GraphState:
    """
    Analyze mix progress and adapt parameters if needed.

    Evaluates energy levels, technique distribution, and — when MERT
    semantic features are available — mood, groove, and harmonic context
    to provide richer adaptive suggestions.
    """
    feedback = state["feedback"]
    metrics = state["playback_metrics"]

    if not state["complete"]:
        return state

    feedback.append("Analyzing mix performance...")

    transitions = metrics.get("section_transitions", [])

    # ── Energy analysis (existing) ──────────────────────────────────────
    energies = [t.get("energy_level", 0.5) for t in transitions]
    if energies:
        avg_energy = sum(energies) / len(energies)
        min_energy = min(energies)
        max_energy = max(energies)

        feedback.append(
            f"Energy analysis: avg={avg_energy:.2f}, "
            f"min={min_energy:.2f}, max={max_energy:.2f}"
        )

        energy_range = max_energy - min_energy
        if energy_range < 0.3:
            feedback.append(
                "Suggestion: Increase energy variation for more dynamic mix"
            )

    # ── Technique distribution (existing) ─────────────────────────────
    technique_counts: dict[str, int] = {}
    for t in transitions:
        tech = t.get("technique", "unknown")
        technique_counts[tech] = technique_counts.get(tech, 0) + 1

    feedback.append("Mixing technique distribution:")
    for tech, count in technique_counts.items():
        pct = (count / len(transitions)) * 100 if transitions else 0
        feedback.append(f"  - {tech}: {pct:.1f}%")

    if len(set(technique_counts.keys())) < 3:
        feedback.append("Suggestion: Use more varied mixing techniques")

    # ── MERT semantic analysis (new — grounded in MERT paper) ───────────
    # Check if any snapshots included MERT features
    semantic_available = False
    for t in transitions:
        if isinstance(t, dict) and t.get("semantic_mert_features", {}).get(
            "mert_available"
        ):
            semantic_available = True
            mert = t["semantic_mert_features"]
            summary = t.get("mert_summary_line", "")

            feedback.append(f"Semantic audio analysis: {summary}")

            # Mood-based adaptation suggestions
            mood = mert.get("emotional_mood", "neutral")
            valence = mert.get("emotional_valence", 0.0)
            arousal = mert.get("emotional_arousal", 0.0)
            groove = mert.get("rhythmic_groove_estimate", 0.5)
            brightness = mert.get("timbral_brightness", 0.5)

            if arousal < -0.2 and mood == "calm":
                feedback.append(
                    "MERT adaptation: Mix feels too calm — consider "
                    "adding a build section with increasing energy"
                )
            elif arousal > 0.3 and mood == "tense":
                feedback.append(
                    "MERT adaptation: High tension detected — "
                    "consider a breakdown or filter sweep to release"
                )

            if groove < 0.3:
                feedback.append(
                    "MERT adaptation: Low groove detected — "
                    "tighten drum patterns or add syncopation"
                )

            if brightness > 0.7:
                feedback.append(
                    "MERT adaptation: Bright/harsh timbre — "
                    "consider rolling off high frequencies"
                )
            elif brightness < 0.3:
                feedback.append(
                    "MERT adaptation: Dark/muffled sound — "
                    "consider adding high-frequency content or brightness"
                )

            # Harmonic context suggestion
            tonic = mert.get("harmonic_likely_tonic", "?")
            tonic_conf = mert.get("harmonic_tonic_confidence", 0.0)
            if tonic_conf > 0.4:
                feedback.append(
                    f"MERT harmonic context: Detected tonal center {tonic} "
                    f"({tonic_conf:.0%} confidence) — ensure chord "
                    f"progressions resolve to this tonic"
                )
            break

    if not semantic_available:
        feedback.append(
            "MERT semantic analysis: unavailable — "
            "install transformers+torch for mood/groove feedback"
        )

    return state
