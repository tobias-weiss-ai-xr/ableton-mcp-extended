"""
2-Hour Dub Techno Automation Script

Runs complete autonomous 2-hour dub techno mix session using MCP client.
Pattern sequencing, automation, clip triggering, and session management.
"""

import sys
import time
import json
from pathlib import Path

from mcp_client import MCPClientTCP
from session_setup import setup_dub_techno_session
from automation_patterns import AutomationSequencer
from follow_actions import configure_energy_follow_actions
import parameter_sweeps


class TwoHourDubTechnoSession:
    """Complete 2-hour autonomous dub techno session."""

    # Session Metadata
    TEMPO = 125
    KEY = "Fm"
    TOTAL_DURATION_BEATS = 9600  # ~2 hours at 125 BPM

    def __init__(self):
        self.client = MCPClientTCP()
        self.sequencer = AutomationSequencer(self.client)
        self.session_started = False
        self.error_count = 0

    def setup_session(self):
        """Initialize dub techno session - tracks, instruments, patterns."""
        print("[SETUP] Initializing dub techno session...")

        try:
            # Create session skeleton
            setup_dub_techno_session(self.client)

            # Set tempo
            self.client.set_tempo(self.TEMPO)
            print(f"[SETUP] Tempo set to {self.TEMPO} BPM")

            # Configure follow actions for 2-hour progression
            configure_energy_follow_actions(
                self.client,
                track_range_start=0,
                track_range_end=4,
                energy_pattern='build',
                num_clips=8
            )
            print("[SETUP] Follow actions configured for energy progression")

            self.session_started = True
            print("[SETUP] Session initialized successfully")

        except Exception as e:
            print(f"[ERROR] Session setup failed: {e}")
            raise

    def run_session(self):
        """Execute 2-hour session automation."""
        if not self.session_started:
            print("[ERROR] Must call setup_session() first")
            return

        print(f"[SESSION] Starting 2-hour dub techno session ({self.TOTAL_DURATION_BEATS} beats)")

        try:
            self._run_wave_intro()
            self._run_wave_main()
            self._run_wave_climax()
            self._run_wave_outro()

            print("[SESSION] 2-hour session completed successfully")

        except Exception as e:
            print(f"[ERROR] Session aborted: {e}")
            self.error_count += 1
            self._handle_recovery(e)

    def _run_wave_intro(self, duration_beats: int = 1280):
        """Intro wave - sparse, atmospheric, building energy."""
        print(f"[WAVE:INTRO] Running intro wave ({duration_beats} beats)")

        # Fade in from silence
        self.sequencer.sequence_intro_fade_in(duration_beats // 2)

        # Trigger minimal clips
        self.client.fire_scene(0)  # Intro clips
        time.sleep(120)  # 2 minutes at current tempo

        # First automation pass - subtle filter sweep
        self.sequencer.pattern_filter_drop([0, 1], intensity=0.4)
        time.sleep(120)

        print("[WAVE:INTRO] Intro wave complete")

    def _run_wave_main(self, duration_beats: int = 4800):
        """Main wave - driving dub techno core."""
        print(f"[WAVE:MAIN] Running main wave ({duration_beats} beats)")

        blocks = 8
        beats_per_block = duration_beats // blocks

        for block_num in range(blocks):
            print(f"[BLOCK] Main block {block_num + 1}/{blocks}")

            # Every 3rd block: breakdown
            if block_num % 3 == 0:
                print(f"[BLOCK] Breakdown - bass solo")
                self.sequencer.pattern_breakdown_solo('bass', beats_per_block // 2)

            # Progression: trigger scenes 1-7
            scene_idx = 1 + (block_num // 2)
            if scene_idx <= 7:
                self.client.fire_scene(scene_idx)

            # Automation blocks
            if block_num == 2:
                # Filter sweep buildup
                self.sequencer.pattern_synchronized_filter_sweep([0, 1, 2], 128)

            elif block_num == 4:
                # Reverb wash transition
                self.sequencer.pattern_reverb_wash([2, 3, 4], 96)

            elif block_num == 6:
                # Formant sweep on pads
                self.sequencer.pattern_formant_sweep([2, 3])

            # Sub-beat automation (dub subtlety)
            if block_num in [1, 5]:
                self.sequencer.pattern_delay_syncopation([0, 1])

            time.sleep(180)  # 3 minutes per block

        print("[WAVE:MAIN] Main wave complete")

    def _run_wave_climax(self, duration_beats: int = 1920):
        """Climax wave - maximum energy, massive automation."""
        print(f"[WAVE:CLIMAX] Running climax wave ({duration_beats} beats)")

        # Maximum filter/resonance sweep
        self.sequencer.sequence_climax_build(duration_beats // 2)

        # All clips firing (dense patterns)
        for scene_idx in range(6, 8):
            self.client.fire_scene(scene_idx)
            time.sleep(180)

        # Dub experimentation - gate effects
        self.sequencer.pattern_gate_effect(0, 'quarter')
        time.sleep(240)

        # Sidechain pumping (audio-reactive)
        try:
            self.sequencer.pattern_sidechain_pumping([1, 2, 3], intensity=0.85)
        except Exception:
            # Fallback if audio analysis unavailable
            print("[WARNING] Sidechain pumping unavailable, skipping")

        print("[WAVE:CLIMAX] Climax wave complete")

    def _run_wave_outro(self, duration_beats: int = 1600):
        """Outro wave - fading, minimal, atmospheric."""
        print(f"[WAVE:OUTRO] Running outro wave ({duration_beats} beats)")

        # Return to sparse patterns
        self.client.fire_scene(0)
        time.sleep(120)

        # Gradual fade out
        all_tracks = [0, 1, 2, 3, 4]
        for i in range(24):
            vol = 0.7 * (1 - i / 24)
            for track_idx in all_tracks:
                self.client.set_track_volume(track_idx, vol)
            time.sleep(5.0)

        print("[WAVE:OUTRO] Outro wave complete")

    def _handle_recovery(self, error: Exception):
        """Error recovery - attempt session salvage."""
        print(f"[RECOVERY] Handling error: {error}")

        if self.error_count > 3:
            print("[RECOVERY] Too many errors - aborting session")
            return

        try:
            # Stop current clips
            self.client.stop_playback()

            # Reset volumes to safe levels
            for track_idx in range(5):
                self.client.set_track_volume(track_idx, 0.7)

            # Return to intro state
            self.client.fire_scene(0)

            print("[RECOVERY] Session stabilized, 继续 normal progression")

        except Exception as recovery_error:
            print(f"[CRITICAL] Recovery failed: {recovery_error}")
            raise


def main():
    """Entry point for 2-hour dub techno session."""
    print("=" * 60)
    print("2-HOUR DUB TECHNOBO MIX - AUTONOMOUS SESSION")
    print("=" * 60)

    session = TwoHourDubTechnoSession()

    try:
        # Initialize session
        session.setup_session()

        # Confirm start
        print("\n[CONFIRM] Session ready. Press Enter to start 2-hour mix...")
        input()

        # Run session
        start_time = time.time()

        session.run_session()

        elapsed = time.time() - start_time
        print(f"\n[COMPLETE] 2-hour session finished in {elapsed:.1f} seconds")

    except KeyboardInterrupt:
        print("\n[INTERRUPT] Session stopped by user")

    except Exception as e:
        print(f"\n[FATAL] Session failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()