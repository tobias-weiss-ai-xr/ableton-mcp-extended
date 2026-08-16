# Audio Feedback Loop for Agentic Mix

**Date**: July 9, 2026
**Priority**: P1 (Post-comp-merge feature)
**Status**: Design Approved, Pending Implementation

## Overview

Section-level audio feedback loop for the LangGraph agentic mix pipeline. Captures real-time audio output between sections via VB-Audio Cable, analyzes spectral/energy characteristics, and adaptive-tunes the next section's parameters (energy level, filter cutoffs, mixing technique selection) rather than structural arrangement changes.

## 1. Architecture

### 1.1 Graph Topology

**Before (Linear, no feedback):**
```
configure → setup_session → generate_clips → construct_arrangement → 
  execute_mix_loop → analyze_adapt → END
```

**After (Loop-back with conditional edge):**
```
configure → setup_session → generate_clips → construct_arrangement → 
  LOOP: [execute_section → analyze_section → more_sections?] → END
```

**Conditional edge function `more_sections?`:**
```python
def more_sections(state: GraphState) -> str:
    if state["current_section_index"] < len(state["arrangement"]) - 1:
        state["current_section_index"] += 1
        return "execute_section"  # Loop back
    else:
        return "END"  # All sections done
```

### 1.2 Node Responsibilities

| Node | Input | Output | Responsibility |
|------|-------|--------|----------------|
| `execute_section` | Current section index, arrangement | Updated playback metrics | Trigger scene, apply mixing technique, record transition |
| `analyze_section` | Section index, arrangement, audio snapshot | Feedback history, adapted next section | Capture audio, analyze readings, decide/apply adaptations |

### 1.3 Integration Points

**Audio Analyzer wrapper:**
- `MCP_Server/audio_analysis/analyzer.py` has `AudioAnalyzer.get_analysis()`
- Returns: `bpm`, `beat`, `rms`, `key`, `key_confidence`, `spectral_centroid_hz`, `spectral_rolloff_hz`, `loudness_lufs`
- New function `capture_audio_snapshot()` wraps this call with validation

**Existing tools used:**
- ` AbletonClient.trigger_scene(scene_index)`
- Mixing technique functions from `agentic_mix/tools/__init__.py`

## 2. State Changes

### 2.1 New State Fields

```python
from typing import Optional, List, Tuple

class AudioAnalysisData(TypedDict):
    """Single snapshot of audio readings from AudioAnalyzer"""
    timestamp: float
    bpm: Optional[float]
    beat: Optional[float]
    rms: float
    loudness_lufs: float
    key: Optional[str]
    key_confidence: Optional[float]
    spectral_centroid_hz: float
    spectral_rolloff_hz: float

class Adaptation(TypedDict):
    """Action applied to a future section"""
    type: str  # "energy_boost", "energy_reduct", "filter_adjust_down", etc.
    target_section: int  # Section index to modify
    value: float  # Magnitude of adjustment
    tracks: Optional[List[int]]  # For track-specific adjustments
    from: Optional[str]  # For technique changes
    to: Optional[str]  # For technique changes

class FeedbackState(TypedDict):
    """Accumulated feedback across sections"""
    history: List[Tuple[int, AudioAnalysisData]]  # [(section_idx, snapshot), ...]
    adaptations: List[Adaptation]  # Description of actions applied
    energy_trend: List[float]  # RMS readings from each section

class GraphState(TypedDict):
    # ... existing fields (config, session_info, arrangement, track_states, playback_metrics, errors, complete) ...

    current_section_index: int  # NEW: which section we're executing (0-based)
    audio_snapshot: Optional[AudioAnalysisData]  # NEW: latest analysis from current section
    feedback: FeedbackState  # REPLACE: was simple List[str], now structured
```

### 2.2 Initialization

```python
# In construct_arrangement_node (existing), add after creating arrangement:
state["current_section_index"] = 0
state["feedback"] = FeedbackState(history=[], adaptations=[], energy_trend=[])
state["audio_snapshot"] = None
```

## 3. Node Implementations

### 3.1 Execute Section Node

**File**: `agentic_mix/nodes/execute_section.py` (NEW)

Extracted single-section execution from existing `execute_mix_loop.py`:

```python
import time
from typing import List, Dict

from agentic_mix.state import GraphState, Section
from agentic_mix.tools import (
    AbletonClient,
    apply_bass_forward_mix,
    apply_dub_drop,
    apply_crossfade,
    apply_send_sweep,
    apply_strip_and_build,
    apply_filter_buildup,
    apply_volume_automation,
    apply_scene_transition,
)

TECHNIQUE_TO_FUNCTION = {
    "bass_forward": apply_bass_forward_mix,
    "dub_drop": apply_dub_drop,
    "crossfade": apply_crossfade,
    "send_sweep": apply_send_sweep,
    "strip_and_build": apply_strip_and_build,
    "filter_sweep": apply_filter_buildup,
    "volume_automation": apply_volume_automation,
    "scene_transition": apply_scene_transition,
    "none": lambda *_: None,  # No-op for مت técnicos
}

def execute_section_node(state: GraphState) -> GraphState:
    """Execute ONE section: trigger scene, apply technique, record metrics"""

    section_idx = state["current_section_index"]
    section: Section = state["arrangement"][section_idx]
    client: AbletonClient = state["client"]

    # 1. Trigger the scene
    client.trigger_scene(section["scene_index"])
    time.sleep(0.5)  # Let Ableton transition settle

    # 2. Apply mixing technique if specified
    technique = section.get("mixing_technique", "none")
    if technique in TECHNIQUE_TO_FUNCTION:
        TECHNIQUE_TO_FUNCTION[technique](client, section)

    # 3. Record section transition in metrics
    timestamp = time.time()
    state["playback_metrics"]["section_transitions"].append({
        "section_index": section_idx,
        "section_name": section["name"],
        "technique": technique,
        "start_time": timestamp,
        "scene_index": section["scene_index"],
    })

    # NOTE: Audio capture happens in NEXT node (analyze_section_node)
    # while this section plays out

    return state
```

### 3.2 Analyze Section Node

**File**: `agentic_mix/nodes/analyze_section.py` (NEW)

```python
import time
import logging
from typing import List

from agentic_mix.state import (
    GraphState,
    Section,
    AudioAnalysisData,
    Adaptation,
    FeedbackState,
)
from agentic_mix.audio_capture import capture_audio_snapshot
from agentic_mix.adaptation_logic import (
    decide_adaptations,
    apply_adaptations_to_section,
    is_valid_snapshot,
)

logger = logging.getLogger(__name__)

VALID_TECHNIQUES = [
    "bass_forward", "dub_drop", "crossfade", "send_sweep",
    "strip_and_build", "filter_sweep", "volume_automation", "scene_transition", "none"
]

DEFAULT_ANALYSIS: AudioAnalysisData = {
    "timestamp": 0.0,
    "bpm": None,
    "beat": None,
    "rms": 0.5,
    "loudness_lufs": -18.0,
    "key": None,
    "key_confidence": None,
    "spectral_centroid_hz": 5000.0,
    "spectral_rolloff_hz": 1000.0,
}

def analyze_section_node(state: GraphState) -> GraphState:
    """Analyze audio output, decide on adaptation, store feedback"""

    section_idx = state["current_section_index"]
    section = state["arrangement"][section_idx]
    arrangement = state["arrangement"]

    try:
        # 1. Capture current audio snapshot
        analysis_raw = capture_audio_snapshot(state["config"])
        analysis_data = AudioAnalysisData(**analysis_raw)

        # 2. Validate readings (filter out nonsense)
        if not is_valid_snapshot(analysis_data):
            logger.warning(
                f"Invalid audio snapshot for section {section_idx}: {analysis_data}"
            )
            # Use last valid reading or fallback default
            if state["feedback"]["history"]:
                last_valid = state["feedback"]["history"][-1][1]
                analysis_data = last_valid
            else:
                analysis_data = AudioAnalysisData(**DEFAULT_ANALYSIS)

        state["audio_snapshot"] = analysis_data

        # 3. Store in feedback history
        state["feedback"]["history"].append((section_idx, analysis_data))
        state["feedback"]["energy_trend"].append(analysis_data["rms"])

        # 4. Analyze and adapt for NEXT section (if any remains)
        if section_idx < len(arrangement) - 1:
            next_section = arrangement[section_idx + 1]

            try:
                adaptations = decide_adaptations(
                    analysis_data, section, next_section, state["config"]
                )

                # Apply adaptations directly to next_section (modifies arrangement in-place)
                apply_adaptations_to_section(adaptations, next_section)

                # Record what we did
                for adapt in adaptations:
                    state["feedback"]["adaptations"].append(adapt)

                logger.info(
                    f"Section {section_idx} → applied {len(adaptations)} adaptations to section {section_idx + 1}"
                )

            except Exception as e:
                logger.error(f"Adaptation logic failed for section {section_idx}: {e}")
                state["feedback"]["adaptations"].append({
                    "type": "error",
                    "message": f"Failed to adapt: {e}"
                })
                state["errors"].append(f"analyze_section_node: {e}")

    except Exception as e:
        logger.error(f"Audio capture failed for section {section_idx}: {e}")
        state["errors"].append(f"analyze_section_node: {e}")
        # Continue with mix anyway, skip adaptive tuning for this section
        state["audio_snapshot"] = None

    return state
```

### 3.3 Conditional Edge Function

**File**: `agentic_mix/graph.py` (MODIFIED)

```python
def more_sections(state: GraphState) -> str:
    """Decide whether to continue with next section or end mix"""

    if state["current_section_index"] < len(state["arrangement"]) - 1:
        # Move to next section
        state["current_section_index"] += 1
        return "execute_section"
    else:
        # All sections done
        return "END"
```

### 3.4 Audio Capture Wrapper

**File**: `agentic_mix/audio_capture.py` (NEW)

```python
from typing import Dict, Any

from agentic_mix.state import Config

def capture_audio_snapshot(config: Config) -> Dict[str, Any]:
    """Capture audio analysis using MCP AudioAnalyzer

    Wraps the MCP server's audio_analysis_start/get_analysis/stop sequence.
    Returns a dictionary compatible with AudioAnalysisData TypedDict.
    """

    import time

    # 1. Start audio capture (uses VB-Audio Cable default device)
    # Assuming MCP tools are accessible via client or direct import
    from ableton_mcp_extended import audio_analysis_start, audio_analysis_get, audio_analysis_stop

    start_result = audio_analysis_start()
    if not start_result.get("running"):
        raise RuntimeError("Failed to start audio analyzer")

    # 2. Wait for audio to settle and capture a snapshot
    # Short duration since we're capturing between-section output
    time.sleep(1.0)  # 1 second of audio analysis

    # 3. Get latest analysis
    analysis_dict = audio_analysis_get()
    # Expected format from MCP endpoint:
    # { "bpm": 120.5, "beat": 3.0, "rms": 0.5, "key": "Am", "key_confidence": 0.8,
    #   "spectral_centroid": 4203.2, "spectral_rolloff": 892.1, "loudness_lufs": -16.4 }

    # 4. Map MCP format to AudioAnalysisData
    snapshot = {
        "timestamp": time.time(),
        "bpm": analysis_dict.get("bpm"),
        "beat": analysis_dict.get("beat"),
        "rms": analysis_dict.get("rms", 0.5),
        "loudness_lufs": analysis_dict.get("loudness_lufs", -18.0),
        "key": analysis_dict.get("key"),
        "key_confidence": analysis_dict.get("key_confidence"),
        "spectral_centroid_hz": analysis_dict.get("spectral_centroid", 5000.0),
        "spectral_rolloff_hz": analysis_dict.get("spectral_rolloff", 1000.0),
    }

    # 5. Stop capture
    audio_analysis_stop()

    return snapshot
```

### 3.5 Adaptation Logic

**File**: `agentic_mix/adaptation_logic.py` (NEW)

```python
from typing import List

from agentic_mix.state import (
    AudioAnalysisData,
    Section,
    Config,
    Adaptation,
)

VALID_TECHNIQUES = [
    "bass_forward", "dub_drop", "crossfade", "send_sweep",
    "strip_and_build", "filter_sweep", "volume_automation", "scene_transition", "none"
]

def decide_adaptations(
    current_analysis: AudioAnalysisData,
    current_section: Section,
    next_section: Section,
    config: Config
) -> List[Adaptation]:
    """Analyze current section readings, return adaptations for next section"""

    adaptations = []

    # --- Rule 1: Energy feedback ---
    # If current section was too quiet, boost next section's energy
    if current_analysis["rms"] < 0.3:
        energy_boost = 0.15  # +1.5 on 0-10 energy scale
        adaptations.append({
            "type": "energy_boost",
            "target_section": next_section["index"],
            "value": energy_boost,
            "tracks": None,
            "from": None,
            "to": None,
        })
        logger.info(f"Low energy detected (RMS={current_analysis['rms']:.2f}), boosting next section")

    # If current section was too loud (near clipping), reduce energy
    elif current_analysis["rms"] > 0.9:
        energy_reduction = -0.15
        adaptations.append({
            "type": "energy_reduct",
            "target_section": next_section["index"],
            "value": energy_reduction,
            "tracks": None,
            "from": None,
            "to": None,
        })
        logger.warning(f"High energy detected (RMS={current_analysis['rms']:.2f}), reducing next section")

    # --- Rule 2: Spectral balance ---
    # Spectral ratio = centroid / rolloff. High ratio = too bright, cut highs
    spectral_ratio = (
        current_analysis["spectral_centroid_hz"] /
        (current_analysis["spectral_rolloff_hz"] or 1.0)
    )

    if spectral_ratio > 0.8:  # Too bright, high frequencies dominant
        # Reduce filter cutoff on lead/pad tracks (indices 0-2 typically)
        adaptations.append({
            "type": "filter_adjust_down",
            "target_section": next_section["index"],
            "value": -0.1,  # -10% of filter cutoff
            "tracks": [0, 1, 2],  # Lead, pad, effects
            "from": None,
            "to": None,
        })
        logger.info(f"Bright spectrum (ratio={spectral_ratio:.2f}), cutting highs")

    elif spectral_ratio < 0.3:  # Too dark, thin sound, boost lows
        adaptations.append({
            "type": "filter_adjust_up",
            "target_section": next_section["index"],
            "value": 0.1,
            "tracks": [0, 1, 2],
            "from": None,
            "to": None,
        })
        logger.info(f"Dark spectrum (ratio={spectral_ratio:.2f}), boosting mid/highs")

    # --- Rule 3: Technique feedback ---
    # If clipping occurred, switch to safer technique for next section
    if current_analysis["rms"] > 0.95:
        current_technique = current_section.get("mixing_technique", "none")
        safer_technique = "volume_automation"  # Most conservative

        if current_technique != safer_technique:
            adaptations.append({
                "type": "technique_change",
                "target_section": next_section["index"],
                "value": 0.0,  # N/A for technique changes
                "tracks": None,
                "from": current_technique,
                "to": safer_technique,
            })
            logger.warning(
                f"Clipping risk detected (RMS={current_analysis['rms']:.2f}), "
                f"switching {current_technique} → {safer_technique}"
            )

    return adaptations


def apply_adaptations_to_section(adaptations: List[Adaptation], section: Section):
    """Apply adaptation list to a section (modifies in-place)"""

    for adapt in adaptations:
        if adapt["type"] == "energy_boost":
            current_energy = section.get("energy_level", 5.0)
            new_energy = min(10.0, current_energy + adapt["value"])
            section["energy_level"] = new_energy

        elif adapt["type"] == "energy_reduct":
            current_energy = section.get("energy_level", 5.0)
            new_energy = max(0.0, current_energy + adapt["value"])  # value is negative
            section["energy_level"] = new_energy

        elif adapt["type"] == "filter_adjust_down":
            # Reduce filter cutoff on specified tracks
            # Note: Section doesn't store per-track filter state; this would need
            # to be applied via GraphState["track_states"] when executing the section
            section["_filter_adjust"] = adapt.get("value", -0.1)
            section["_filter_tracks"] = adapt.get("tracks", [])

        elif adapt["type"] == "filter_adjust_up":
            section["_filter_adjust"] = adapt.get("value", 0.1)
            section["_filter_tracks"] = adapt.get("tracks", [])

        elif adapt["type"] == "technique_change":
            section["mixing_technique"] = adapt["to"]


def is_valid_snapshot(snapshot: AudioAnalysisData) -> bool:
    """Validate audio readings are sensible"""

    # Skip if all readings are zero (no audio signal)
    all_zero = all(
        v == 0 or v is None
        for v in snapshot.values()
        if k != "timestamp"
    )
    if all_zero:
        return False

    # Key readings only if confident threshold met
    if snapshot.get("key_confidence", 1.0) < 0.5:
        # Low confidence → ignore key field
        snapshot["key"] = None

    # RMS must be in reasonable normalized range
    if not (0.0 <= snapshot.get("rms", 0.0) <= 1.0):
        return False

    # Spectral values must be positive non-zero
    if snapshot.get("spectral_centroid_hz", 0) <= 0:
        return False
    if snapshot.get("spectral_rolloff_hz", 0) <= 0:
        return False

    return True
```

## 4. Graph Wiring

**File**: `agentic_mix/graph.py` (MODIFIED)

```python
from langgraph.graph import StateGraph, END

from agentic_mix.state import GraphState
from agentic_mix.nodes import (
    configure_node,
    setup_session_node,
    generate_clips_node,
    construct_arrangement_node,
    execute_mix_loop_node,  # REPLACED by execute_section_node
    analyze_adapt_node,    # REPLACED by analyze_section_node
)

# NEW imports
from agentic_mix.nodes.execute_section import execute_section_node
from agentic_mix.nodes.analyze_section import analyze_section_node

# Conditional edge function
def more_sections(state: GraphState) -> str:
    if state["current_section_index"] < len(state["arrangement"]) - 1:
        state["current_section_index"] += 1
        return "execute_section"
    else:
        return END

def create_agentic_mix_graph(checkpointer=None) -> StateGraph:
    """Build LangGraph StateGraph with audio feedback loop"""

    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("configure", configure_node)
    workflow.add_node("setup_session", setup_session_node)
    workflow.add_node("generate_clips", generate_clips_node)
    workflow.add_node("construct_arrangement", construct_arrangement_node)
    workflow.add_node("execute_section", execute_section_node)  # NEW
    workflow.add_node("analyze_section", analyze_section_node)  # NEW

    # Define edges
    workflow.set_entry_point("configure")
    workflow.add_edge("configure", "setup_session")
    workflow.add_edge("setup_session", "generate_clips")
    workflow.add_edge("generate_clips", "construct_arrangement")

    # FEEDBACK LOOP: construct_arrangement → execute_section → analyze_section → [loop or END]
    workflow.add_edge("construct_arrangement", "execute_section")
    workflow.add_edge("execute_section", "analyze_section")
    workflow.add_conditional_edges(
        "analyze_section",
        more_sections,  # Conditional edge function
        {
            "execute_section": "execute_section",
            END: END
        }
    )

    return workflow.compile(checkpointer=checkpointer)
```

## 5. Error Handling & Fallbacks

### 5.1 Fail-Open Policy

**Principle**: If audio capture or adaptation logic fails, continue mixing. The primary goal is completing the arrangement execution, not perfect adaptive tuning.

**Strategies:**

1. **Audio capture failure**: Log error, skip adaptive tuning for this section, use last valid reading or default. Graph continues to next section.

2. **Invalid readings**: Detect nonsense data (all zeros, out-of-range RMS) and reject. Fall back to last known good reading.

3. **Adaptation failures**: If `decide_adaptations()` or `apply_adaptations_to_section()` throws, log error, skip adaptations, continue to next section.

### 5.2 Error Recovery

All errors are logged to `state["errors"]` for post-mix analysis:

```python
# In analyze_section_node
except Exception as e:
    logger.error(f"Audio analysis failed for section {section_idx}: {e}")
    state["errors"].append(f"analyze_section_node: {e}")
    state["audio_snapshot"] = None  # No valid snapshot this round
    # Continue with mix anyway
```

## 6. Testing Strategy

### 6.1 Unit Tests

**File**: `tests/test_adaptation_logic.py`

```python
import pytest
from agentic_mix.adaptation_logic import decide_adaptations, is_valid_snapshot
from agentic_mix.audio_capture import AudioAnalysisData, DEFAULT_ANALYSIS


def test_decide_adaptations_energy_boost():
    """Quiet RMS triggers energy boost for next section"""

    current_analysis = AudioAnalysisData(
        timestamp=1.0, rms=0.2,  # Too quiet
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-20.0
    )

    current_section = {"index": 0, "energy_level": 3.0, "mixing_technique": "none"}
    next_section = {"index": 1, "energy_level": 4.0, "mixing_technique": "none"}
    config = {"tempo": 120, "duration_minutes": 4, "genre": "techno"}

    adaptations = decide_adaptations(current_analysis, current_section, next_section, config)

    assert any(
        a["type"] == "energy_boost" and a["target_section"] == 1
        for a in adaptations
    )

    # Verify next section would be boosted after apply_adaptations_to_section
    from agentic_mix.adaptation_logic import apply_adaptations_to_section
    apply_adaptations_to_section(adaptations, next_section)
    assert next_section["energy_level"] > 4.0


def test_decide_adaptations_clipping_protection():
    """Clipping RMS triggers energy reduction AND technique change"""

    current_analysis = AudioAnalysisData(
        timestamp=2.0, rms=0.97,  # Near clipping
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-6.0
    )

    current_section = {"index": 0, "energy_level": 8.5, "mixing_technique": "dub_drop"}
    next_section = {"index": 1, "energy_level": 7.0, "mixing_technique": "dub_drop"}
    config = {"tempo": 120}

    adaptations = decide_adaptations(current_analysis, current_section, next_section, config)

    assert any(a["type"] == "energy_reduct" for a in adaptations)
    assert any(
        a["type"] == "technique_change" and a["to"] == "volume_automation"
        for a in adaptations
    )


def test_is_valid_snapshot():
    """Reject all-zero readings and out-of-range values"""

    # All zeros → invalid
    zeros = AudioAnalysisData(
        timestamp=1.0, rms=0.0, spectral_centroid_hz=0.0, spectral_rolloff_hz=0.0,
        key=None, key_confidence=None, bpm=0.0, beat=0.0, loudness_lufs=0.0
    )
    assert not is_valid_snapshot(zeros)

    # Valid snapshot
    valid = AudioAnalysisData(
        timestamp=1.0, rms=0.5, spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-18.0
    )
    assert is_valid_snapshot(valid)

    # RMS out of range (1.5 > 1.0)
    invalid_rms = AudioAnalysisData(
        timestamp=1.0, rms=1.5, spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-18.0
    )
    assert not is_valid_snapshot(invalid_rms)


def test_is_valid_snapshot_low_key_confidence():
    """Snapshot with low key confidence should mark key as None"""

    snapshot = AudioAnalysisData(
        timestamp=1.0, rms=0.5, spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key="Am", key_confidence=0.3,  # Low confidence
        bpm=120.0, beat=1.0, loudness_lufs=-18.0
    )

    result = is_valid_snapshot(snapshot)
    assert result  # Should still be valid overall
    assert snapshot["key"] is None  # But key field cleared
```

### 6.2 Integration Tests

**File**: `tests/test_feedback_loop_integration.py`

```python
import time
from unittest.mock import patch, MagicMock

from agentic_mix.graph import create_agentic_mix_graph
from agentic_mix.state import AudioAnalysisData

# Mock audio readings: quiet → normal → clipping
MOCK_READINGS = [
    AudioAnalysisData(
        timestamp=1.0, rms=0.2,  # Section 0: too quiet
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-20.0
    ),
    AudioAnalysisData(
        timestamp=2.0, rms=0.6,  # Section 1: normal
        spectral_centroid_hz=4200.0, spectral_rolloff_hz=950.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-16.0
    ),
    AudioAnalysisData(
        timestamp=3.0, rms=0.95,  # Section 2: clipping risk
        spectral_centroid_hz=5500.0, spectral_rolloff_hz=1100.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-8.0
    ),
]


@patch("agentic_mix.audio_capture.capture_audio_snapshot")
def test_full_feedback_loop(mock_capture):
    """Run 3-section mix with mocked audio readings"""

    # Setup mock to return sequential readings
    mock_capture.side_effect = MOCK_READINGS

    # Initialize graph with 3-section arrangement
    config = {
        "tempo": 120,
        "duration_minutes": 2,  # 3 sections × 0.66 min each
        "genre": "techno",
        "track_count": 4,
        "key": "Fm",
        "energy_curve": "rise",
        "variation_level": 0.5,
        "section_duration_beats": 16,
    }

    graph = create_agentic_mix_graph()
    initial_state = {"config": config, "complete": False}

    # Run graph
    result = graph.invoke(initial_state)

    # Verify all sections executed
    assert result["current_section_index"] == 3  # 3 sections done (0, 1, 2)
    assert result["complete"] is True

    # Verify audio snapshots captured for all sections
    assert len(result["feedback"]["history"]) == 3
    assert all(s is not None for _, s in result["feedback"]["history"])

    # Verify adaptations were applied
    adaptations = result["feedback"]["adaptations"]
    assert len(adaptations) > 0

    # Check that first section (quiet) triggered energy boost for section 1
    energy_boosts = [a for a in adaptations if a["type"] == "energy_boost"]
    assert len(energy_boosts) > 0

    # Check that third section (clipping) triggered energy reduction
    energy_reductions = [a for a in adaptations if a["type"] == "energy_reduct"]
    assert len(energy_reductions) > 0


@patch("agentic_mix.audio_capture.capture_audio_snapshot")
def test_audio_capture_failure_robustness(mock_capture):
    """Verify graph continues even if audio capture fails"""

    # Mock to raise error on second section
    def side_effect(*args):
        if current_capture_call[0] == 1:  # Section 1 fails
            raise RuntimeError("VB-Audio Cable not connected")
        return MOCK_READINGS[current_capture_call[0]]

    current_capture_call = [0]
    mock_capture.side_effect = side_effect

    graph = create_agentic_mix_graph()
    initial_state = {
        "config": {"tempo": 120, "duration_minutes": 2, "genre": "techno", "track_count": 4},
        "complete": False,
    }

    result = graph.invoke(initial_state)

    # Graph should still complete all sections
    assert result["current_section_index"] == 3

    # One section should have None snapshot due to failure
    snapshots = [s for _, s in result["feedback"]["history"]]
    assert any(s is None for s in snapshots)

    # Error should be logged
    assert len(result["errors"]) > 0
    assert any("capture_audio_snapshot" in e or "analyze_section" in e for e in result["errors"])
```

### 6.3 Real-World Test (Optional)

Requires Ableton Live running with VB-Audio Cable configured. Not part of CI/CD, but documented for manual verification.

**Steps:**
1. Start Ableton, ensure Master output routed to VB-Audio Cable Input
2. Run full agentic mix graph with real audio capture
3. Verify VB-Audio Cable device detected and `audio_analysis_start()` succeeds
4. Check console logs for adaptation decisions
5. Post-mix: inspect `state["feedback"]["energy_trend"]` for expected progression

## 7. Non-Requirements (Explicitly Out of Scope)

- **Structural arrangement changes**: Section count, sequence, duration remain fixed
- **Real-time sub-section feedback**: No beat-level or bar-level analysis between-section only
- **Track-level adaptation granularities**: Technique-level and energy-level only, not per-device automation
- **MIDI/Clap feedback loop**: Only audio analysis via VB-Audio Cable
- **Key modulation**: Key detection for information only, no pitch-shifting adaptations

## 8. Success Criteria

1. Graph successfully loops through all sections with conditional edge
2. Audio snapshots captured for each section (or gracefully log failures)
3. Adaptations triggered when readings exceed thresholds (RMS, spectral ratio)
4. Next section parameters modified in-place (energy level, technique)
5. All errors logged to `state["errors"]` without halting execution
6. Post-mix `state["feedback"]` contains full history + applied adaptations
7. Unit tests pass for: adaptarion rules, snapshot validation, edge cases
8. Integration test runs 3-section mock mix successfully

## 9. Implementation Order

1. State changes (`agentic_mix/state.py`)
2. Audio capture wrapper (`agentic_mix/audio_capture.py`)
3. Adaptation logic (`agentic_mix/adaptation_logic.py`)
4. Nodes (`agentic_mix/nodes/execute_section.py`, `analyze_section.py`)
5. Graph wiring (`agentic_mix/graph.py`)
6. Tests (unit → integration)
7. Documentation update
