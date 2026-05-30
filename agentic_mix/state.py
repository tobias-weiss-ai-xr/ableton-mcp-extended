"""
Graph state definition for LangGraph agentic mix pipeline.
"""
from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """User configuration for the mix pipeline."""
    tempo: int = 126
    duration_minutes: int = 120
    genre: str = "dub_techno"  # dub_techno, house, techno, ambient
    track_count: int = 8
    key: str = "Fm"  # Musical key (Fm, Cm, Am, etc.)
    energy_curve: str = "gradual"  # gradual, aggressive, gentle
    variation_level: float = 0.5  # 0.0-1.0
    section_duration_beats: float = 64.0  # beats per section

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tempo": self.tempo,
            "duration_minutes": self.duration_minutes,
            "genre": self.genre,
            "track_count": self.track_count,
            "key": self.key,
            "energy_curve": self.energy_curve,
            "variation_level": self.variation_level,
            "section_duration_beats": self.section_duration_beats,
        }


@dataclass
class SessionInfo:
    """Ableton session state."""
    initialized: bool = False
    track_indices: List[int] = field(default_factory=list)
    scene_indices: List[int] = field(default_factory=list)
    return_track_indices: List[int] = field(default_factory=list)
    tempo: Optional[int] = None
    time_signature: Optional[tuple] = None


@dataclass
class Section:
    """Section in the arrangement."""
    index: int
    name: str  # intro, groove_a, build, drop, break, groove_b, outro
    start_beat: float
    end_beat: float
    energy_level: float  # 0.0-1.0
    tracks_active: List[int]
    mixing_technique: Optional[str] = None  # dub_drop, bass_forward, etc
    scene_index: Optional[int] = None


@dataclass
class TrackState:
    """Current state of a track during playback."""
    volume: float = 0.75
    pan: float = 0.0
    muted: bool = False
    solo: bool = False
    device_states: Dict[int, float] = field(default_factory=dict)  # device_index -> parameter_value


@dataclass
class PlaybackMetrics:
    """Metrics collected during mix execution."""
    start_time: Optional[float] = None
    current_time: Optional[float] = None
    section_transitions: List[Dict[str, Any]] = field(default_factory=list)
    mixing_actions: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class GraphState(TypedDict):
    """Main state for the LangGraph graph."""
    config: Config
    session_info: SessionInfo
    arrangement: List[Section]
    current_section: int
    track_states: List[TrackState]
    playback_metrics: PlaybackMetrics
    feedback: List[str]
    complete: bool
    error: Optional[str]
