"""
Graph state definition for LangGraph agentic mix pipeline.

All state structures use TypedDict for LangGraph compatibility.
Values accessed as dict keys: state["config"]["tempo"]
"""
from typing import TypedDict, List, Dict, Any, Optional, Literal


# ============================================================================
# Type definitions for fixed string values
# ============================================================================

GenreLiteral = Literal["dub_techno", "house", "techno", "ambient"]
EnergyCurveLiteral = Literal["gradual", "aggressive", "gentle"]
KeyLiteral = Literal["Fm", "Cm", "Am", "Dm", "Gm", "Em", "F", "C", "D", "G", "E", "A"]
SectionTypeLiteral = Literal["intro", "groove_a", "groove_b", "build", "drop", "break", "outro"]
MixingTechniqueLiteral = Literal["dub_drop", "bass_forward", "strip_and_build", "send_sweep", "scene_transition", "none"]


# ============================================================================
# Config: User configuration parameters
# ============================================================================

class Config(TypedDict):
    """User configuration for the mix pipeline."""
    tempo: int
    duration_minutes: int
    genre: GenreLiteral
    track_count: int
    key: KeyLiteral
    energy_curve: EnergyCurveLiteral
    variation_level: float
    section_duration_beats: float


def create_config(
    tempo: int = 126,
    duration_minutes: int = 120,
    genre: GenreLiteral = "dub_techno",
    track_count: int = 8,
    key: KeyLiteral = "Fm",
    energy_curve: EnergyCurveLiteral = "gradual",
    variation_level: float = 0.5,
    section_duration_beats: float = 64.0,
) -> Config:
    """Create a Config instance with defaults."""
    return {
        "tempo": tempo,
        "duration_minutes": duration_minutes,
        "genre": genre,
        "track_count": track_count,
        "key": key,
        "energy_curve": energy_curve,
        "variation_level": variation_level,
        "section_duration_beats": section_duration_beats,
    }


# ============================================================================
# SessionInfo: Ableton session state
# ============================================================================

class SessionInfo(TypedDict):
    """Ableton session state."""
    initialized: bool
    track_indices: List[int]
    scene_indices: List[int]
    return_track_indices: List[int]
    tempo: Optional[int]
    time_signature: Optional[tuple]


def create_session_info() -> SessionInfo:
    """Create an initialized SessionInfo instance."""
    return {
        "initialized": False,
        "track_indices": [],
        "scene_indices": [],
        "return_track_indices": [],
        "tempo": None,
        "time_signature": None,
    }


# ============================================================================
# Section: Section in the arrangement
# ============================================================================

class Section(TypedDict):
    """Section in the arrangement."""
    index: int
    name: SectionTypeLiteral
    start_beat: float
    end_beat: float
    energy_level: float
    tracks_active: List[int]
    mixing_technique: Optional[MixingTechniqueLiteral]
    scene_index: Optional[int]


# ============================================================================
# TrackState: Current state of a track during playback
# ============================================================================

class TrackState(TypedDict):
    """Current state of a track during playback."""
    volume: float
    pan: float
    muted: bool
    solo: bool
    device_states: Dict[int, float]


def create_track_state(volume: float = 0.75) -> TrackState:
    """Create a TrackState instance."""
    return {
        "volume": volume,
        "pan": 0.0,
        "muted": False,
        "solo": False,
        "device_states": {},
    }


# ============================================================================
# PlaybackMetrics: Metrics collected during mix execution
# ============================================================================

class PlaybackMetrics(TypedDict):
    """Metrics collected during mix execution."""
    start_time: Optional[float]
    current_time: Optional[float]
    section_transitions: List[Dict[str, Any]]
    mixing_actions: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


def create_playback_metrics() -> PlaybackMetrics:
    """Create a PlaybackMetrics instance."""
    return {
        "start_time": None,
        "current_time": None,
        "section_transitions": [],
        "mixing_actions": [],
        "errors": [],
    }


# ============================================================================
# GraphState: Main state for the LangGraph graph
# ============================================================================

class GraphState(TypedDict):
    """Main state for the LangGraph graph."""
    config: Config
    session_info: SessionInfo
    arrangement: List[Section]
    current_section: int
    track_states: List[TrackState]
    playback_metrics: PlaybackMetrics
    feedback: List[str]
    errors: List[Dict[str, Any]]
    complete: bool