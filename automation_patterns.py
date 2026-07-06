"""
Automation Pattern Library for 2-Hour Dub Techno Mix

Provides reusable automation sequences for filter sweeps, reverb washes,
delay modulation, and dub-style treatment effects.
"""

from mcp_client import MCPClientTCP
from parameter_sweeps import (
    apply_filter_sweep,
    apply_format_filter,
    apply_repeat_delay,
    apply_reverb_decay,
    apply_synchronized_sweep
)
from audio_analysis import AudioAnalysisWrapper
import time


class AutomationSequencer:
    """Coordinates automation patterns for 2-hour session."""

    def __init__(self, client: MCPClientTCP):
        self.client = client
        self.tracks = {
            'drums': 0,
            'bass': 1,
            'pad1': 2,
            'pad2': 3,
            'fx': 4
        }
        self.audio_analyzer = AudioAnalysisWrapper()

    # Pattern 1: Filter Sweep (Dub Techno Drop)
    def pattern_filter_drop(self, track_indices: list, intensity: float = 0.7):
        """
        Classic dub techno filter drop - filter closes then gradually opens.

        Args:
            track_indices: List of track indices to apply sweep to
            intensity: Automation intensity (0.3-1.0)
        """
        start_filter = 0.3 if intensity > 0.5 else 0.4
        end_filter = 0.9

        apply_filter_sweep(
            self.client,
            track_indices=track_indices,
            start_filter=start_filter,
            end_filter=end_filter,
            duration_beats=32,
            steps=16
        )

    # Pattern 2: Reverb Wash (Transition)
    def pattern_reverb_wash(self, track_indices: list, wash_duration_beats: int = 16):
        """
        Reverb wash effect for seamless scene transitions.

        Args:
            track_indices: List of track indices to apply reverb wash to
            wash_duration_beats: Duration of wash in beats
        """
        apply_reverb_decay(
            self.client,
            track_indices=track_indices,
            start_decay=0.2,
            end_decay=0.9,
            duration_beats=wash_duration_beats,
            steps=8
        )

    # Pattern 3: Delay Syncopation (Dub Echoes)
    def pattern_delay_syncopation(self, track_indices: list):
        """
        Rhythmic delay syncopation - dub style echo patterns.

        Args:
            track_indices: List of track indices to apply delay modulation to
        """
        apply_repeat_delay(
            self.client,
            track_indices=track_indices,
            start_time=0.2,
            end_time=0.4,
            sync_mode='eighth',
            duration_beats=16,
            steps=8
        )

    # Pattern 4: Formant Texture (Resonance Sweep)
    def pattern_formant_sweep(self, track_indices: list):
        """
        Formant filter texture - creates talking synth character.

        Args:
            track_indices: List of track indices to apply formant sweep to
        """
        apply_format_filter(
            self.client,
            track_indices=track_indices,
            start_formant=0.3,
            end_formant=0.8,
            duration_beats=24,
            steps=12
        )

    # Pattern 5: Synchronized Multi-Track Filter
    def pattern_synchronized_filter_sweep(self, track_indices: list):
        """
        All tracks filter sweep in perfect sync - massive build energy.

        Args:
            track_indices: List of track indices for synchronized sweep
        """
        apply_synchronized_sweep(
            self.client,
            track_indices=track_indices,
            start_filter=0.25,
            end_filter=0.95,
            duration_beats=48,
            steps=24
        )

    # Pattern 6: Gate Effect (Rhythmic Muting)
    def pattern_gate_effect(self, track_index: int, gate_pattern: str = 'quarter'):
        """
        Dub techno gate effect - rhythmic volume muting.

        Args:
            track_index: Single track to gate
            gate_pattern: 'quarter', 'eighth', 'syncopated'
        """
        if gate_pattern == 'quarter':
            # Simple 4-on-the-floor gate
            for beat in range(16):
                if beat % 4 == 0:
                    self.client.set_track_volume(track_index, 0.8)
                else:
                    self.client.set_track_volume(track_index, 0.2)
                time.sleep(0.25)  # At 120 BPM
        elif gate_pattern == 'eighth':
            # Eighth-note trance gate
            for beat in range(32):
                if beat % 2 == 0:
                    self.client.set_track_volume(track_index, 0.7)
                else:
                    self.client.set_track_volume(track_index, 0.1)
                time.sleep(0.125)

    # Pattern 7: Sidechain Pumping (Based on Audio Analysis)
    def pattern_sidechain_pumping(self, track_indices: list, intensity: float = 0.8):
        """
        Audio-reaction sidechain pumping - tracks respond to kick energy.

        Args:
            track_indices: List of track indices to pump
            intensity: Pumping intensity (0.5-1.0)
        """
        for _ in range(64):  # 16 beats sub-beats
            rms = self.audio_analyzer.get_rms_level()
            ramp_depth = rms * intensity * 0.4

            for track_idx in track_indices:
                current_vol = 0.7
                pumped_vol = current_vol - ramp_depth
                self.client.set_track_volume(track_idx, max(0.1, pumped_vol))

            time.sleep(0.125)  # Eighth-note subdivision

    # Pattern 8: Crossfade Transition
    def pattern_crossfade_transition(self, track_a: int, track_b: int, duration_beats: int = 32):
        """
        Smooth crossfade between two tracks.

        Args:
            track_a: Track fading OUT
            track_b: Track fading IN
            duration_beats: Transition duration in beats
        """
        steps = 16
        vol_a_start, vol_a_end = 0.8, 0.0
        vol_b_start, vol_b_end = 0.0, 0.8

        for i in range(steps + 1):
            progress = i / steps
            vol_a = vol_a_start + (vol_a_end - vol_a_start) * progress
            vol_b = vol_b_start + (vol_b_end - vol_b_start) * progress

            self.client.set_track_volume(track_a, vol_a)
            self.client.set_track_volume(track_b, vol_b)

            time.sleep((duration_beats / steps) * 0.5)  # BPM adjustment

    # Preset Sequences
    def sequence_intro_fade_in(self, duration_beats: int = 64):
        """Intro automation - gradual fade in from silence."""
        all_tracks = list(self.tracks.values())

        for i in range(32):
            vol = (i / 32) * 0.7
            for track_idx in all_tracks:
                self.client.set_track_volume(track_idx, vol)
            time.sleep(2.0)  # Approx per beat

    def sequence_climax_build(self, duration_beats: int = 64):
        """Climax build - massive filter and resonance sweep."""
        all_tracks = list(self.tracks.values())

        self.pattern_synchronized_filter_sweep(all_tracks)

        # Add reverb wash
        self.pattern_reverb_wash([self.tracks['pad1'], self.tracks['pad2']], wash_duration_beats=48)

    def sequence_breakdown_solo(self, solo_track: str, duration_beats: int = 32):
        """Breakdown - solo one track, others fade down."""
        solo_idx = self.tracks[solo_track]
        other_tracks = [t for t in self.tracks.values() if t != solo_idx]

        # Ramp others down
        for i in range(16):
            vol = 0.7 * (1 - i / 16)
            for track_idx in other_tracks:
                self.client.set_track_volume(track_idx, vol)
            time.sleep(1.5)

        # Hold solo
        time.sleep(8.0)

        # Ramp others back in
        for i in range(16):
            vol = 0.0 + (0.7 * i / 16)
            for track_idx in other_tracks:
                self.client.set_track_volume(track_idx, vol)
            time.sleep(1.5)


# Standalone pattern functions (for script usage)
def apply_intro_fade_in(client: MCPClientTCP, track_indices: list, duration_beats: int = 64):
    """Standalone intro fade in."""
    sequencer = AutomationSequencer(client)
    sequencer.sequence_intro_fade_in(duration_beats)


def apply_climax_build(client: MCPClientTCP, track_indices: list, duration_beats: int = 64):
    """Standalone climax build."""
    sequencer = AutomationSequencer(client)
    sequencer.sequence_climax_build(duration_beats)


def apply_breakdown_solo(client: MCPClientTCP, solo_track: int, other_tracks: list, duration_beats: int = 32):
    """Standalone breakdown solo."""
    sequencer = AutomationSequencer(client)
    sequencer.pattern_crossfade_transition(solo_track, other_tracks[0], duration_beats)