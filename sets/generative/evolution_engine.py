"""
Main orchestrator for the generative dub techno evolution system.

Ties together all generative components into a cohesive 30+ minute
evolving musical experience with state machine control.

Usage:
    # Run with Ableton Live
    python -m dub_techno_2h.generative.evolution_engine --duration 30

    # Simulate without Ableton
    python -m dub_techno_2h.generative.evolution_engine --simulate --verbose

    # Quick import test
    python -c "from dub_techno_2h.generative.evolution_engine import EvolutionEngine; print('OK')"
"""

import logging
import os
import random
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Handle both module and direct script execution
try:
    from .config import (
        BASELINE_VALUES,
        CLIPS_PER_TRACK,
        PATTERN_DURATIONS,
        TEMPO,
        TRACKS,
    )
    from .mcp_client import MCPClient, MCPConnectionError
except ImportError:
    # When running as a script directly
    from config import (
        BASELINE_VALUES,
        CLIPS_PER_TRACK,
        PATTERN_DURATIONS,
        TEMPO,
        TRACKS,
    )
    from mcp_client import MCPClient, MCPConnectionError


# =============================================================================
# STATE MACHINE DEFINITION
# =============================================================================

STATES = {
    "intro": {"duration_min": 4, "filter_range": (0.3, 0.5), "volume_mult": 0.8},
    "build": {"duration_min": 4, "filter_range": (0.4, 0.6), "volume_mult": 0.9},
    "peak": {"duration_min": 4, "filter_range": (0.5, 0.8), "volume_mult": 1.0},
    "breakdown": {"duration_min": 4, "filter_range": (0.2, 0.4), "volume_mult": 0.6},
    "build2": {"duration_min": 4, "filter_range": (0.4, 0.7), "volume_mult": 0.9},
    "journey": {"duration_min": 4, "filter_range": (0.5, 0.7), "volume_mult": 0.95},
    "final": {"duration_min": 4, "filter_range": (0.6, 0.9), "volume_mult": 1.0},
    "winddown": {"duration_min": 4, "filter_range": (0.3, 0.5), "volume_mult": 0.7},
}

STATE_ORDER = [
    "intro",
    "build",
    "peak",
    "breakdown",
    "build2",
    "journey",
    "final",
    "winddown",
]


# =============================================================================
# STATE DATA CLASS
# =============================================================================


@dataclass
class EngineState:
    """Holds the current state of the evolution engine."""

    running: bool = False
    paused: bool = False
    current_state: str = "intro"
    state_index: int = 0
    start_time: float = 0.0
    elapsed_seconds: float = 0.0
    clips_played: int = 0
    patterns_generated: int = 0
    sweeps_started: int = 0
    errors: int = 0
    last_error: str = ""


# =============================================================================
# EVOLUTION ENGINE CLASS
# =============================================================================


class EvolutionEngine:
    """
    Main orchestrator for the generative dub techno system.

    Coordinates:
    - Pattern generation via PatternGenerator
    - Clip creation via MCPClient
    - Follow action chains via FollowActionSetup
    - Real-time parameter sweeps via UDPController

    State machine progresses through 8 musical states over ~32 minutes.

    Attributes:
        simulate: If True, run without connecting to Ableton
        verbose: If True, output detailed progress information
        seed: Random seed for reproducibility
    """

    def __init__(
        self,
        simulate: bool = False,
        verbose: bool = False,
        seed: Optional[int] = None,
    ):
        """
        Initialize the evolution engine.

        Args:
            simulate: Run without Ableton connection (for testing)
            verbose: Enable detailed logging output
            seed: Random seed for reproducibility
        """
        self.simulate = simulate
        self.verbose = verbose
        self.seed = seed

        if seed is not None:
            random.seed(seed)

        # State management
        self._state = EngineState()
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Components (initialized in _initialize_components)
        self._client: Optional[MCPClient] = None
        self._pattern_generator = None
        self._follow_action_setup = None
        self._udp_controller = None

        # Logging setup
        self._setup_logging()

        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self) -> None:
        """Configure logging to file and console."""
        log_dir = Path(__file__).parent
        log_file = log_dir / "evolution.log"

        # Create logger
        self._logger = logging.getLogger("EvolutionEngine")
        self._logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        # Clear existing handlers
        self._logger.handlers = []

        # File handler (always on)
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)

        # Console handler (if verbose)
        if self.verbose:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter("[EvolutionEngine] %(message)s")
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)

    def _log(self, level: int, message: str) -> None:
        """Log a message at the specified level."""
        self._logger.log(level, message)

    def _signal_handler(self, signum, frame) -> None:
        """Handle interrupt signals for graceful shutdown."""
        self._log(
            logging.INFO, f"Received signal {signum}, initiating graceful shutdown"
        )
        self.stop()

    def _initialize_components(self) -> bool:
        """
        Initialize all generative components.

        Returns:
            True if all components initialized successfully
        """
        self._log(logging.INFO, "Initializing components...")

        if self.simulate:
            self._log(
                logging.INFO, "Running in SIMULATE mode - skipping Ableton connection"
            )
            # Create mock components for simulation
            self._client = None
            return True

        try:
            # Import components lazily to avoid import errors in simulate mode
            try:
                from .mcp_client import MCPClient
                from .pattern_generator import PatternGenerator
                from .follow_action_setup import FollowActionSetup
                from .udp_controller import UDPController
            except ImportError:
                # When running as a script directly
                from mcp_client import MCPClient
                from pattern_generator import PatternGenerator
                from follow_action_setup import FollowActionSetup
                from udp_controller import UDPController

            # Initialize MCP client
            self._client = MCPClient()
            self._client.connect()

            # Verify connection
            self._client.verify_connection()
            self._log(logging.INFO, "Connected to Ableton MCP")

            # Initialize pattern generator
            self._pattern_generator = PatternGenerator(seed=self.seed)
            self._log(logging.INFO, "PatternGenerator initialized")

            # Initialize follow action setup
            self._follow_action_setup = FollowActionSetup(self._client)
            self._log(logging.INFO, "FollowActionSetup initialized")

            # Initialize UDP controller
            self._udp_controller = UDPController()
            self._log(logging.INFO, "UDPController initialized")

            return True

        except MCPConnectionError as e:
            self._log(logging.ERROR, f"Failed to connect to Ableton: {e}")
            with self._lock:
                self._state.errors += 1
                self._state.last_error = str(e)
            return False
        except Exception as e:
            self._log(logging.ERROR, f"Component initialization failed: {e}")
            with self._lock:
                self._state.errors += 1
                self._state.last_error = str(e)
            return False

    def _startup_sequence(self) -> bool:
        """
        Execute the startup sequence.

        1. Generate patterns using PatternGenerator
        2. Create clips with generated patterns
        3. Configure follow actions via FollowActionSetup
        4. Start UDP parameter sweeps

        Returns:
            True if startup completed successfully
        """
        self._log(logging.INFO, "Executing startup sequence...")

        if self.simulate:
            self._log(logging.INFO, "Simulating startup sequence...")
            time.sleep(0.5)  # Simulate initialization time
            self._state.patterns_generated = 48
            return True

        try:
            # Step 1: Generate patterns
            self._log(logging.INFO, "Generating patterns...")
            patterns = self._generate_all_patterns()
            self._log(logging.INFO, f"Generated {len(patterns)} pattern sets")

            # Step 2: Create clips
            self._log(logging.INFO, "Creating clips...")
            clips_created = self._create_clips_from_patterns(patterns)
            self._log(logging.INFO, f"Created {clips_created} clips")

            # Step 3: Configure follow actions
            self._log(logging.INFO, "Configuring follow actions...")
            follow_stats = self._follow_action_setup.setup_all_chains()
            self._log(logging.INFO, f"Follow actions: {follow_stats}")

            # Step 4: Start initial parameter sweeps
            self._log(logging.INFO, "Starting initial parameter sweeps...")
            self._start_initial_sweeps()

            return True

        except Exception as e:
            self._log(logging.ERROR, f"Startup sequence failed: {e}")
            with self._lock:
                self._state.errors += 1
                self._state.last_error = str(e)
            return False

    def _generate_all_patterns(self) -> Dict[str, List[Dict]]:
        """Generate patterns for all tracks."""
        all_patterns = {}

        for track_name, track_index in TRACKS.items():
            # Use prime-length patterns for phase relationships
            bars = random.choice(PATTERN_DURATIONS)

            if track_name == "kick":
                all_patterns[track_name] = self._pattern_generator.generate_kick(bars)
            elif track_name == "bass":
                all_patterns[track_name] = self._pattern_generator.generate_bass(bars)
            elif track_name == "hihat":
                all_patterns[track_name] = self._pattern_generator.generate_hihat(bars)
            elif track_name == "pads":
                all_patterns[track_name] = self._pattern_generator.generate_pads(bars)
            elif track_name == "fx":
                all_patterns[track_name] = self._pattern_generator.generate_fx(bars)
            elif track_name == "delays":
                # Delays track uses pad-like patterns
                all_patterns[track_name] = self._pattern_generator.generate_pads(bars)

            with self._lock:
                self._state.patterns_generated += 1

        return all_patterns

    def _create_clips_from_patterns(self, patterns: Dict[str, List[Dict]]) -> int:
        """Create clips in Ableton from generated patterns."""
        clips_created = 0

        for track_name, notes in patterns.items():
            track_index = TRACKS.get(track_name, -1)
            if track_index < 0:
                continue

            # Create clips in slots 0-7 for each track
            for clip_index in range(CLIPS_PER_TRACK):
                try:
                    # Calculate clip length from pattern
                    if notes:
                        max_time = max(
                            n.get("start_time", 0) + n.get("duration", 0) for n in notes
                        )
                        clip_length = max(4.0, max_time)
                    else:
                        clip_length = 4.0

                    # Create clip
                    self._client.tcp_command(
                        "create_clip",
                        {
                            "track_index": track_index,
                            "clip_index": clip_index,
                            "length": clip_length,
                        },
                    )

                    # Add notes to clip
                    if notes:
                        self._client.tcp_command(
                            "add_notes_to_clip",
                            {
                                "track_index": track_index,
                                "clip_index": clip_index,
                                "notes": notes,
                            },
                        )

                    # Set clip name
                    self._client.tcp_command(
                        "set_clip_name",
                        {
                            "track_index": track_index,
                            "clip_index": clip_index,
                            "name": f"{track_name}_{clip_index}",
                        },
                    )

                    clips_created += 1

                except Exception as e:
                    self._log(
                        logging.WARNING,
                        f"Failed to create clip {track_name}/{clip_index}: {e}",
                    )

        return clips_created

    def _start_initial_sweeps(self) -> None:
        """Start initial parameter sweeps based on current state."""
        if self.simulate or not self._udp_controller:
            return

        state_config = STATES.get(self._state.current_state, STATES["intro"])
        filter_min, filter_max = state_config["filter_range"]

        # Start filter sweep on pads track
        pads_track = TRACKS.get("pads", -1)
        if pads_track >= 0:
            # Device/param indices: assuming Auto Filter is device 0, cutoff is param 0
            # In real setup, these would be discovered dynamically
            self._udp_controller.start_sweep(
                track_index=pads_track,
                device_index=0,
                param_index=0,
                sweep_type="sine",
                duration_sec=240.0,  # 4 minutes
                base_value=(filter_min + filter_max) / 2,
                amplitude=(filter_max - filter_min) / 2,
                freq_hz=0.05,  # Slow 20-second cycle
                param_type="filter",
            )
            with self._lock:
                self._state.sweeps_started += 1

    def _update_sweeps_for_state(self, state_name: str) -> None:
        """Update parameter sweeps for a new state."""
        if self.simulate or not self._udp_controller:
            return

        state_config = STATES.get(state_name, STATES["intro"])
        filter_min, filter_max = state_config["filter_range"]

        # Update filter sweep parameters
        pads_track = TRACKS.get("pads", -1)
        if pads_track >= 0 and self._udp_controller:
            # Stop existing sweep and start new one with updated parameters
            self._udp_controller.stop_sweep(pads_track, 0, 0)
            self._udp_controller.start_sweep(
                track_index=pads_track,
                device_index=0,
                param_index=0,
                sweep_type="sine",
                duration_sec=state_config["duration_min"] * 60,
                base_value=(filter_min + filter_max) / 2,
                amplitude=(filter_max - filter_min) / 2,
                freq_hz=0.05,
                param_type="filter",
            )

    def _update_volumes_for_state(self, state_name: str) -> None:
        """Update track volumes for a new state."""
        if self.simulate or not self._udp_controller:
            return

        state_config = STATES.get(state_name, STATES["intro"])
        volume_mult = state_config["volume_mult"]

        # Apply volume multiplier to baseline values
        volume_baselines = BASELINE_VALUES.get("volume", {})

        for track_name, base_volume in volume_baselines.items():
            if track_name == "master":
                continue

            track_index = TRACKS.get(track_name, -1)
            if track_index < 0:
                continue

            adjusted_volume = base_volume * volume_mult
            adjusted_volume = max(0.0, min(1.0, adjusted_volume))

            self._udp_controller.set_track_volume(track_index, adjusted_volume)

    def _transition_state(self) -> None:
        """Transition to the next state in the sequence."""
        with self._lock:
            self._state.state_index += 1

            if self._state.state_index >= len(STATE_ORDER):
                # Loop back to intro or stop
                self._state.state_index = 0
                self._log(logging.INFO, "State loop complete, returning to intro")

            self._state.current_state = STATE_ORDER[self._state.state_index]

        new_state = self._state.current_state
        self._log(logging.INFO, f"Transitioning to: {new_state}")

        # Update parameters for new state
        self._update_sweeps_for_state(new_state)
        self._update_volumes_for_state(new_state)

    def _check_state_transition(self) -> None:
        """Check if it's time to transition to the next state."""
        current_config = STATES.get(self._state.current_state, STATES["intro"])
        state_duration_sec = current_config["duration_min"] * 60

        # Calculate time in current state
        state_start_time = self._get_state_start_time()
        time_in_state = self._state.elapsed_seconds - state_start_time

        if time_in_state >= state_duration_sec:
            self._transition_state()

    def _get_state_start_time(self) -> float:
        """Calculate the start time of the current state."""
        elapsed = 0.0
        for i in range(self._state.state_index):
            state_name = STATE_ORDER[i]
            state_config = STATES.get(state_name, STATES["intro"])
            elapsed += state_config["duration_min"] * 60
        return elapsed

    def _fire_clips_for_state(self, state_name: str) -> None:
        """Fire initial clips for a state transition."""
        if self.simulate or not self._client:
            return

        state_index = STATE_ORDER.index(state_name) if state_name in STATE_ORDER else 0

        # Fire clips based on state (use scene-like behavior)
        for track_name, track_index in TRACKS.items():
            # Select clip based on state index (cycling through 8 clips)
            clip_index = state_index % CLIPS_PER_TRACK

            try:
                self._client.send(
                    "fire_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                    },
                )
                with self._lock:
                    self._state.clips_played += 1
            except Exception as e:
                self._log(
                    logging.WARNING,
                    f"Failed to fire clip {track_name}/{clip_index}: {e}",
                )

    def _main_loop(self) -> None:
        """
        Main evolution loop.

        - Monitors clip playback state
        - Updates UDP sweeps based on current state
        - Tracks time and transitions states
        - Logs progress
        """
        self._log(logging.INFO, "Starting main evolution loop")
        self._state.start_time = time.time()

        # Fire initial clips
        self._fire_clips_for_state(self._state.current_state)

        loop_interval = 1.0  # Check every second

        while not self._stop_event.is_set():
            loop_start = time.time()

            with self._lock:
                self._state.elapsed_seconds = time.time() - self._state.start_time
                self._state.running = True

            # Check for state transition
            self._check_state_transition()

            # Output progress
            self._output_progress()

            # Sleep until next loop iteration
            elapsed = time.time() - loop_start
            sleep_time = max(0, loop_interval - elapsed)
            if sleep_time > 0:
                self._stop_event.wait(sleep_time)

        self._log(logging.INFO, "Main loop terminated")

    def _output_progress(self) -> None:
        """Output current progress to console and log."""
        elapsed = self._state.elapsed_seconds
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        progress_msg = (
            f"State: {self._state.current_state} | "
            f"Elapsed: {elapsed_str} | "
            f"Clips: {self._state.clips_played}"
        )

        if self.verbose:
            print(f"[EvolutionEngine] {progress_msg}")

        self._log(logging.DEBUG, progress_msg)

    def _graceful_shutdown(self) -> None:
        """
        Execute graceful shutdown sequence.

        1. Stop all UDP sweeps
        2. Reset parameters to baseline
        3. Clear follow actions (optional)
        4. Close connections
        """
        self._log(logging.INFO, "Executing graceful shutdown...")

        # Stop all sweeps
        if self._udp_controller:
            self._log(logging.INFO, "Stopping all UDP sweeps...")
            self._udp_controller.emergency_stop()
            self._udp_controller.close()

        # Reset to baseline volumes
        if not self.simulate and self._client:
            self._log(logging.INFO, "Resetting parameters to baseline...")
            volume_baselines = BASELINE_VALUES.get("volume", {})
            for track_name, volume in volume_baselines.items():
                if track_name == "master":
                    continue
                track_index = TRACKS.get(track_name, -1)
                if track_index >= 0:
                    try:
                        self._client.send(
                            "set_track_volume",
                            {
                                "track_index": track_index,
                                "volume": volume,
                            },
                        )
                    except Exception:
                        pass

        # Optionally clear follow actions
        # (Commented out to preserve state for next run)
        # if self._follow_action_setup:
        #     self._follow_action_setup.clear_all_chains()

        # Close MCP connection
        if self._client:
            self._log(logging.INFO, "Closing MCP connection...")
            self._client.close()

        self._log(logging.INFO, "Shutdown complete")

    def run(self, duration_minutes: Optional[float] = None) -> None:
        """
        Run the evolution engine.

        Args:
            duration_minutes: Duration in minutes. None = run indefinitely.
        """
        self._log(logging.INFO, f"EvolutionEngine starting (simulate={self.simulate})")

        # Initialize components
        if not self._initialize_components():
            self._log(logging.ERROR, "Failed to initialize components, aborting")
            return

        # Execute startup sequence
        if not self._startup_sequence():
            self._log(logging.ERROR, "Startup sequence failed, aborting")
            return

        # Calculate total duration if specified
        if duration_minutes is not None:
            total_duration_sec = duration_minutes * 60
            self._log(logging.INFO, f"Running for {duration_minutes} minutes")

            # Set a timer to stop after duration
            def stop_timer():
                self._stop_event.wait(total_duration_sec)
                if not self._stop_event.is_set():
                    self._log(logging.INFO, "Duration reached, stopping...")
                    self.stop()

            timer_thread = threading.Thread(target=stop_timer, daemon=True)
            timer_thread.start()

        # Run main loop
        try:
            self._main_loop()
        except Exception as e:
            self._log(logging.ERROR, f"Error in main loop: {e}")
            with self._lock:
                self._state.errors += 1
                self._state.last_error = str(e)
        finally:
            self._graceful_shutdown()

    def stop(self) -> None:
        """Stop the evolution engine gracefully."""
        self._log(logging.INFO, "Stop requested")
        with self._lock:
            self._state.running = False
        self._stop_event.set()

    def get_state(self) -> Dict:
        """
        Get the current state of the engine.

        Returns:
            Dict with current state information
        """
        with self._lock:
            return {
                "running": self._state.running,
                "paused": self._state.paused,
                "current_state": self._state.current_state,
                "state_index": self._state.state_index,
                "elapsed_seconds": self._state.elapsed_seconds,
                "clips_played": self._state.clips_played,
                "patterns_generated": self._state.patterns_generated,
                "sweeps_started": self._state.sweeps_started,
                "errors": self._state.errors,
                "last_error": self._state.last_error,
                "simulate": self.simulate,
            }


# =============================================================================
# COMMAND-LINE INTERFACE
# =============================================================================


def _main():
    """Entry point for command-line execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Evolution Engine for Generative Dub Techno"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duration in minutes (default: run indefinitely)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run without Ableton connection (for testing)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )

    args = parser.parse_args()

    # Create and run engine
    engine = EvolutionEngine(
        simulate=args.simulate,
        verbose=args.verbose,
        seed=args.seed,
    )

    try:
        engine.run(duration_minutes=args.duration)
    except KeyboardInterrupt:
        print("\n[EvolutionEngine] Interrupted by user")
        engine.stop()


if __name__ == "__main__":
    _main()
