"""
Pattern Sequence Orchestration

Coordinates pattern sequences for 2-hour session.
Defines wave structures, transition timings, and clip firing schedules.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class WaveType(Enum):
    """Session wave types."""
    INTRO = "intro"
    MAIN = "main"
    CLIMAX = "climax"
    OUTRO = "outro"


@dataclass
class PatternBlock:
    """Single pattern block definition."""
    id: str
    duration_beats: int
    scene_indices: List[int]
    automation_patterns: List[str]
    track_volumes: Dict[int, float]


@dataclass
class WaveStructure:
    """Complete wave structure - sequence of pattern blocks."""
    wave_type: WaveType
    duration_beats: int
    pattern_blocks: List[PatternBlock]
    transition_in_beats: int = 32
    transition_out_beats: int = 32


class PatternOrchestrator:
    """Orchestrates pattern sequences for 2-hour session."""

    # Session configuration
    TOTAL_SESSION_BEATS = 9600  # ~2 hours at 125 BPM

    def __init__(self):
        self.waves = self._build_session_structure()
        self.current_wave_index = 0
        self.current_block_index = 0

    def _build_session_structure(self) -> List[WaveStructure]:
        """Build complete 2-hour session wave structure."""
        waves = []

        # Wave 1: Intro (4 minutes - 8 bars × 8 = 64 bars)
        waves.append(self._build_intro_wave())

        # Wave 2: Main core (96 minutes - 80% of session)
        waves.append(self._build_main_wave())

        # Wave 3: Climax (16 minutes - peak energy)
        waves.append(self._build_climax_wave())

        # Wave 4: Outro (4 minutes - fade out)
        waves.append(self._build_outro_wave())

        return waves

    def _build_intro_wave(self) -> WaveStructure:
        """Intro wave structure."""
        blocks = [
            PatternBlock(
                id="intro_fade_in",
                duration_beats=320,
                scene_indices=[0],
                automation_patterns=["fade_in", "filter_subtle"],
                track_volumes={0: 0.3, 1: 0.2, 2: 0.1, 3: 0.1, 4: 0.0}
            ),
            PatternBlock(
                id="intro_build",
                duration_beats=320,
                scene_indices=[0, 1],
                automation_patterns=["filter_sweep", "delay_intro"],
                track_volumes={0: 0.5, 1: 0.4, 2: 0.3, 3: 0.2, 4: 0.1}
            )
        ]

        return WaveStructure(
            wave_type=WaveType.INTRO,
            duration_beats=640,
            pattern_blocks=blocks,
            transition_in_beats=0,
            transition_out_beats=64
        )

    def _build_main_wave(self) -> WaveStructure:
        """Main wave structure - 6 blocks of 1280 beats each."""
        blocks = []

        # Block 1-2: Core grooves
        blocks.append(PatternBlock(
            id="main_block_1",
            duration_beats=1280,
            scene_indices=[1, 2],
            automation_patterns=["filter_main", "delay_eighth"],
            track_volumes={0: 0.7, 1: 0.7, 2: 0.6, 3: 0.5, 4: 0.4}
        ))

        # Block 2: Breakdown 1
        blocks.append(PatternBlock(
            id="main_breakdown_1",
            duration_beats=640,
            scene_indices=[1],
            automation_patterns=["breakdown_bass", "filter_closed"],
            track_volumes={0: 0.3, 1: 0.8, 2: 0.1, 3: 0.1, 4: 0.0}
        ))

        # Block 3-4: Intensity build
        blocks.append(PatternBlock(
            id="main_block_2",
            duration_beats=1280,
            scene_indices=[2, 3],
            automation_patterns=["filter_open", "reverb_wash", "gate_trance"],
            track_volumes={0: 0.7, 1: 0.7, 2: 0.7, 3: 0.6, 4: 0.5}
        ))

        # Block 3: Breakdown 2
        blocks.append(PatternBlock(
            id="main_breakdown_2",
            duration_beats=640,
            scene_indices=[2],
            automation_patterns=["breakdown_pad", "formant_sweep"],
            track_volumes={0: 0.2, 1: 0.2, 2: 0.8, 3: 0.7, 4: 0.3}
        ))

        # Block 5-6: Peak approaches
        blocks.append(PatternBlock(
            id="main_block_3",
            duration_beats=1280,
            scene_indices=[3, 4],
            automation_patterns=["filter_sweep_build", "delay_syncopated", "sidechain"],
            track_volumes={0: 0.8, 1: 0.8, 2: 0.7, 3: 0.7, 4: 0.6}
        ))

        return WaveStructure(
            wave_type=WaveType.MAIN,
            duration_beats=5120,
            pattern_blocks=blocks,
            transition_in_beats=64,
            transition_out_beats=128
        )

    def _build_climax_wave(self) -> WaveStructure:
        """Climax wave structure - maximum energy."""
        blocks = [
            # Climax buildup
            PatternBlock(
                id="climax_build",
                duration_beats=480,
                scene_indices=[4, 5],
                automation_patterns=["filter_max", "reverb_max", "synchronized_sweep"],
                track_volumes={0: 0.9, 1: 0.9, 2: 0.8, 3: 0.8, 4: 0.7}
            ),
            # Peak
            PatternBlock(
                id="climax_peak",
                duration_beats=480,
                scene_indices=[6, 7],
                automation_patterns=["gate_aggressive", "sidechain_max", "frequency_mod"],
                track_volumes={0: 1.0, 1: 0.9, 2: 0.9, 3: 0.8, 4: 0.8}
            ),
            # Resolution
            PatternBlock(
                id="climax_resolve",
                duration_beats=480,
                scene_indices=[5, 6],
                automation_patterns=["filter_retract", "delay_wash", "volume_fade"],
                track_volumes={0: 0.7, 1: 0.7, 2: 0.6, 3: 0.6, 4: 0.5}
            )
        ]

        return WaveStructure(
            wave_type=WaveType.CLIMAX,
            duration_beats=1440,
            pattern_blocks=blocks,
            transition_in_beats=128,
            transition_out_beats=192
        )

    def _build_outro_wave(self) -> WaveStructure:
        """Outro wave structure - fade to silence."""
        blocks = [
            PatternBlock(
                id="outro_sparse",
                duration_beats=320,
                scene_indices=[0],
                automation_patterns=["filter_tight", "delay_decay"],
                track_volumes={0: 0.4, 1: 0.3, 2: 0.2, 3: 0.2, 4: 0.1}
            ),
            PatternBlock(
                id="outro_atmospheric",
                duration_beats=320,
                scene_indices=[0],
                automation_patterns=["volume_fade_out", "reverb_long"],
                track_volumes={0: 0.2, 1: 0.1, 2: 0.1, 3: 0.0, 4: 0.0}
            )
        ]

        return WaveStructure(
            wave_type=WaveType.OUTRO,
            duration_beats=640,
            pattern_blocks=blocks,
            transition_in_beats=192,
            transition_out_beats=0
        )

    def get_current_wave(self) -> WaveStructure:
        """Get current wave."""
        return self.waves[self.current_wave_index]

    def advance_to_next_wave(self) -> bool:
        """Advance to next wave, return False if session complete."""
        if self.current_wave_index < len(self.waves) - 1:
            self.current_wave_index += 1
            self.current_block_index = 0
            return True
        return False

    def get_current_block(self) -> PatternBlock:
        """Get current pattern block."""
        wave = self.get_current_wave()
        if self.current_block_index < len(wave.pattern_blocks):
            return wave.pattern_blocks[self.current_block_index]
        return None

    def advance_to_next_block(self) -> bool:
        """Advance to next block, move to next wave if needed."""
        wave = self.get_current_wave()
        if self.current_block_index < len(wave.pattern_blocks) - 1:
            self.current_block_index += 1
            return True
        else:
            # End of current wave - try to advance
            return self.advance_to_next_wave()

    def get_session_progress(self) -> Tuple[int, int]:
        """Get session progress (current_beat, total_beats)."""
        completed_beats = 0

        # Add completed waves
        for i in range(self.current_wave_index):
            completed_beats += self.waves[i].duration_beats

        # Add current wave pattern blocks
        wave = self.get_current_wave()
        for i in range(self.current_block_index):
            completed_beats += wave.pattern_blocks[i].duration_beats

        return (completed_beats, self.TOTAL_SESSION_BEATS)

    def get_remaining_blocks(self) -> int:
        """Calculate remaining pattern blocks in session."""
        remaining = 0

        # Current wave remaining blocks
        wave = self.get_current_wave()
        remaining += len(wave.pattern_blocks) - self.current_block_index - 1

        # Future waves all blocks
        for i in range(self.current_wave_index + 1, len(self.waves)):
            remaining += len(self.waves[i].pattern_blocks)

        return remaining


# Standalone orchestration functions
def get_wave_schedule() -> List[Dict]:
    """Simplified wave schedule for script integration."""
    orchestrator = PatternOrchestrator()
    schedule = []

    for wave in orchestrator.waves:
        wave_data = {
            'type': wave.wave_type.value,
            'duration_beats': wave.duration_beats,
            'blocks': []
        }

        for block in wave.pattern_blocks:
            block_data = {
                'id': block.id,
                'duration_beats': block.duration_beats,
                'scenes': block.scene_indices,
                'automation': block.automation_patterns,
                'volumes': block.track_volumes
            }
            wave_data['blocks'].append(block_data)

        schedule.append(wave_data)

    return schedule