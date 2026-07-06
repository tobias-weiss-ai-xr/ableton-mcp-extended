"""
Analyze and adapt node - Evaluate mix and make adaptive decisions.
"""
from agentic_mix.state import GraphState


def analyze_and_adapt_node(state: GraphState) -> GraphState:
    """
    Analyze mix progress and adapt parameters if needed.

    This node (conceptual extension):
    - Evaluates energy levels across sections
    - Checks for repetition or stagnation
    - Suggests adaptive changes for next run
    """
    feedback = state["feedback"]
    metrics = state["playback_metrics"]

    if not state["complete"]:
        # Don't adapt if mix didn't complete
        return state

    feedback.append("Analyzing mix performance...")

    # Analyze section transitions
    transitions = metrics.get("section_transitions", [])

    # Check energy distribution
    energies = [t.get("energy_level", 0.5) for t in transitions]
    if energies:
        avg_energy = sum(energies) / len(energies)
        min_energy = min(energies)
        max_energy = max(energies)

        feedback.append(f"Energy analysis: avg={avg_energy:.2f}, min={min_energy:.2f}, max={max_energy:.2f}")

        # Check if energy curve could be improved
        energy_range = max_energy - min_energy
        if energy_range < 0.3:
            feedback.append("Suggestion: Increase energy variation for more dynamic mix")

    # Count mixing technique usage
    technique_counts = {}
    for t in transitions:
        tech = t.get("technique", "unknown")
        technique_counts[tech] = technique_counts.get(tech, 0) + 1

    feedback.append("Mixing technique distribution:")
    for tech, count in technique_counts.items():
        pct = (count / len(transitions)) * 100 if transitions else 0
        feedback.append(f"  - {tech}: {pct:.1f}%")

    # Suggest improvements
    if len(set(technique_counts.keys())) < 3:
        feedback.append("Suggestion: Use more varied mixing techniques")

    return state
