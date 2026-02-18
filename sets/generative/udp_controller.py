"""
Real-time UDP parameter controller for Ableton Live.

Provides high-frequency parameter sweeps with rate limiting,
smoothing, and emergency stop capabilities.

Usage:
    from dub_techno_2h.generative.udp_controller import UDPController

    controller = UDPController()
    controller.start_sweep(0, 0, 0, "sine", 10.0)  # 10s sine sweep
    controller.emergency_stop()  # Reset all to baseline
"""

import json
import math
import random
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from .config import (
    BASELINE_VALUES,
    TRACKS,
    UDP_PORT,
    UDP_RATE_LIMITS,
)


@dataclass
class SweepState:
    """Tracks the state of an active parameter sweep."""

    active: bool = False
    thread: Optional[threading.Thread] = None
    stop_event: threading.Event = field(default_factory=threading.Event)
    sweep_type: str = ""
    base_value: float = 0.5
    current_value: float = 0.5
    target_value: Optional[float] = None  # For return-to-center


class UDPController:
    """
    Real-time UDP parameter controller for Ableton Live.

    Provides high-frequency parameter sweeps with:
    - Rate limiting per parameter type (filter: 200Hz, volume: 100Hz)
    - Multiple sweep types (sine, triangle, ramp, random_walk)
    - Smoothing to avoid audio glitches
    - Emergency stop to reset all parameters to baseline
    - Return-to-center after sweep stops

    Thread-safe: All sweep operations run in background threads.
    """

    HOST = "localhost"
    SMOOTHING_INTERVAL = 0.01  # 10ms smoothing interval

    def __init__(self):
        """Initialize UDP socket and internal state."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sweeps: Dict[Tuple[int, int, int], SweepState] = {}
        self._rate_limit_timestamps: Dict[str, float] = {
            "filter": 0.0,
            "volume": 0.0,
        }
        self._lock = threading.Lock()
        self._return_to_center_threads: Dict[
            Tuple[int, int, int], threading.Thread
        ] = {}

    def _send_udp(self, command: dict) -> None:
        """Send a command via UDP (fire-and-forget)."""
        try:
            payload = json.dumps(command).encode("utf-8")
            self._socket.sendto(payload, (self.HOST, UDP_PORT))
        except Exception:
            pass  # UDP is fire-and-forget, ignore errors

    def set_parameter(
        self, track_index: int, device_index: int, param_index: int, value: float
    ) -> None:
        """
        Send a single parameter update via UDP.

        Args:
            track_index: Track index in Ableton
            device_index: Device index on the track
            param_index: Parameter index on the device
            value: Normalized value (0.0-1.0)
        """
        value = max(0.0, min(1.0, value))  # Clamp to valid range
        command = {
            "type": "set_device_parameter",
            "params": {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": param_index,
                "value": value,
            },
        }
        self._send_udp(command)

    def set_track_volume(self, track_index: int, volume: float) -> None:
        """
        Send a track volume update via UDP.

        Args:
            track_index: Track index in Ableton
            volume: Normalized volume (0.0-1.0)
        """
        volume = max(0.0, min(1.0, volume))
        command = {
            "type": "set_track_volume",
            "params": {
                "track_index": track_index,
                "volume": volume,
            },
        }
        self._send_udp(command)

    def _enforce_rate_limit(self, param_type: str) -> bool:
        """
        Check and enforce rate limiting for a parameter type.

        Args:
            param_type: "filter" or "volume"

        Returns:
            True if update is allowed, False if rate limited
        """
        rate_key = f"{param_type}_hz"
        max_hz = UDP_RATE_LIMITS.get(rate_key, 100)
        min_interval = 1.0 / max_hz

        with self._lock:
            now = time.time()
            last_update = self._rate_limit_timestamps.get(param_type, 0.0)

            if now - last_update < min_interval:
                return False

            self._rate_limit_timestamps[param_type] = now
            return True

    def _wait_for_rate_limit(self, param_type: str) -> None:
        """Wait until rate limit allows next update."""
        rate_key = f"{param_type}_hz"
        max_hz = UDP_RATE_LIMITS.get(rate_key, 100)
        min_interval = 1.0 / max_hz

        with self._lock:
            now = time.time()
            last_update = self._rate_limit_timestamps.get(param_type, 0.0)
            elapsed = now - last_update

            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

    def _get_rate_limit_hz(self, param_type: str) -> float:
        """Get the rate limit in Hz for a parameter type."""
        rate_key = f"{param_type}_hz"
        return float(UDP_RATE_LIMITS.get(rate_key, 100))

    def _sine_sweep(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
        base_value: float,
        amplitude: float,
        freq_hz: float,
        duration: float,
        state: SweepState,
        param_type: str,
    ) -> None:
        """
        Sinusoidal parameter sweep (ideal for filter cutoff).

        value = base + amplitude * sin(2π * freq * t)
        """
        rate_limit_hz = self._get_rate_limit_hz(param_type)
        interval = 1.0 / rate_limit_hz
        start_time = time.time()

        while not state.stop_event.is_set():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break

            # Calculate sine wave value
            value = base_value + amplitude * math.sin(2 * math.pi * freq_hz * elapsed)
            value = max(0.0, min(1.0, value))

            # Apply smoothing: interpolate from current to target
            if state.current_value is not None:
                smoothed = state.current_value + (value - state.current_value) * 0.3
                value = max(0.0, min(1.0, smoothed))

            state.current_value = value
            self.set_parameter(track_index, device_index, param_index, value)

            time.sleep(interval)

        # Store final value for return-to-center
        state.target_value = base_value

    def _triangle_sweep(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
        base_value: float,
        amplitude: float,
        freq_hz: float,
        duration: float,
        state: SweepState,
        param_type: str,
    ) -> None:
        """
        Triangle wave parameter sweep (ideal for delay feedback).

        Linear oscillation between base-amplitude and base+amplitude.
        """
        rate_limit_hz = self._get_rate_limit_hz(param_type)
        interval = 1.0 / rate_limit_hz
        start_time = time.time()

        while not state.stop_event.is_set():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break

            # Triangle wave: 4 * abs((t * f) % 1 - 0.5) - 0.5 gives [-0.5, 0.5]
            phase = (elapsed * freq_hz) % 1.0
            triangle = 4 * abs(phase - 0.5) - 1.0  # Range [-1, 1]
            value = base_value + amplitude * triangle
            value = max(0.0, min(1.0, value))

            # Apply smoothing
            if state.current_value is not None:
                smoothed = state.current_value + (value - state.current_value) * 0.3
                value = max(0.0, min(1.0, smoothed))

            state.current_value = value
            self.set_parameter(track_index, device_index, param_index, value)

            time.sleep(interval)

        state.target_value = base_value

    def _ramp_sweep(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
        start_value: float,
        end_value: float,
        duration: float,
        state: SweepState,
        param_type: str,
    ) -> None:
        """
        Linear ramp from start to end value (ideal for reverb size).

        value = start + (end - start) * (t / duration)
        """
        rate_limit_hz = self._get_rate_limit_hz(param_type)
        interval = 1.0 / rate_limit_hz
        start_time = time.time()

        while not state.stop_event.is_set():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break

            # Linear interpolation
            progress = elapsed / duration
            value = start_value + (end_value - start_value) * progress
            value = max(0.0, min(1.0, value))

            state.current_value = value
            self.set_parameter(track_index, device_index, param_index, value)

            time.sleep(interval)

        state.target_value = start_value  # Return to start

    def _random_walk_sweep(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
        base_value: float,
        step_size: float,
        duration: float,
        state: SweepState,
        param_type: str,
    ) -> None:
        """
        Random walk parameter sweep (ideal for LFO rate).

        Each step moves ±step_size from current value.
        """
        rate_limit_hz = self._get_rate_limit_hz(param_type)
        interval = 1.0 / rate_limit_hz
        start_time = time.time()
        current = base_value

        while not state.stop_event.is_set():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break

            # Random step ±step_size
            delta = random.uniform(-step_size, step_size)
            current = max(0.0, min(1.0, current + delta))

            # Apply additional smoothing
            if state.current_value is not None:
                smoothed = state.current_value + (current - state.current_value) * 0.5
                current = max(0.0, min(1.0, smoothed))

            state.current_value = current
            self.set_parameter(track_index, device_index, param_index, current)

            time.sleep(interval)

        state.target_value = base_value

    def _return_to_center(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
        target_value: float,
        key: Tuple[int, int, int],
    ) -> None:
        """
        Gradually return parameter to baseline value.

        Drifts at 0.1/s until target is reached.
        """
        state = self._sweeps.get(key)
        if not state:
            return

        drift_rate = 0.1  # Per second
        interval = 0.05  # 50ms updates

        while not state.stop_event.is_set():
            if state.current_value is None:
                break

            diff = target_value - state.current_value
            if abs(diff) < 0.01:  # Close enough
                state.current_value = target_value
                self.set_parameter(track_index, device_index, param_index, target_value)
                break

            # Move towards target
            step = drift_rate * interval
            if diff > 0:
                state.current_value = min(target_value, state.current_value + step)
            else:
                state.current_value = max(target_value, state.current_value - step)

            self.set_parameter(
                track_index, device_index, param_index, state.current_value
            )
            time.sleep(interval)

        # Cleanup
        with self._lock:
            if key in self._return_to_center_threads:
                del self._return_to_center_threads[key]

    def start_sweep(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
        sweep_type: str,
        duration_sec: float,
        base_value: float = 0.5,
        amplitude: float = 0.3,
        freq_hz: float = 0.5,
        param_type: str = "filter",
    ) -> bool:
        """
        Start a parameter sweep in a background thread.

        Args:
            track_index: Track index in Ableton
            device_index: Device index on the track
            param_index: Parameter index on the device
            sweep_type: "sine", "triangle", "ramp", or "random_walk"
            duration_sec: Duration of sweep in seconds
            base_value: Starting/center value (0.0-1.0)
            amplitude: Sweep amplitude (0.0-1.0)
            freq_hz: Sweep frequency in Hz (for oscillating types)
            param_type: "filter" or "volume" for rate limiting

        Returns:
            True if sweep started, False if already active
        """
        key = (track_index, device_index, param_index)

        with self._lock:
            if key in self._sweeps and self._sweeps[key].active:
                return False

            state = SweepState(
                active=True,
                sweep_type=sweep_type,
                base_value=base_value,
                current_value=base_value,
                stop_event=threading.Event(),
            )
            self._sweeps[key] = state

        def sweep_thread():
            try:
                if sweep_type == "sine":
                    self._sine_sweep(
                        track_index,
                        device_index,
                        param_index,
                        base_value,
                        amplitude,
                        freq_hz,
                        duration_sec,
                        state,
                        param_type,
                    )
                elif sweep_type == "triangle":
                    self._triangle_sweep(
                        track_index,
                        device_index,
                        param_index,
                        base_value,
                        amplitude,
                        freq_hz,
                        duration_sec,
                        state,
                        param_type,
                    )
                elif sweep_type == "ramp":
                    end_value = base_value + amplitude
                    self._ramp_sweep(
                        track_index,
                        device_index,
                        param_index,
                        base_value,
                        end_value,
                        duration_sec,
                        state,
                        param_type,
                    )
                elif sweep_type == "random_walk":
                    self._random_walk_sweep(
                        track_index,
                        device_index,
                        param_index,
                        base_value,
                        amplitude * 0.5,
                        duration_sec,  # step_size
                        state,
                        param_type,
                    )
                else:
                    return

                # Start return-to-center after sweep completes
                if state.target_value is not None and not state.stop_event.is_set():
                    return_thread = threading.Thread(
                        target=self._return_to_center,
                        args=(
                            track_index,
                            device_index,
                            param_index,
                            state.target_value,
                            key,
                        ),
                        daemon=True,
                    )
                    with self._lock:
                        self._return_to_center_threads[key] = return_thread
                    return_thread.start()

            finally:
                with self._lock:
                    if key in self._sweeps:
                        self._sweeps[key].active = False

        thread = threading.Thread(target=sweep_thread, daemon=True)
        state.thread = thread
        thread.start()

        return True

    def stop_sweep(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
    ) -> bool:
        """
        Stop an active parameter sweep.

        Args:
            track_index: Track index in Ableton
            device_index: Device index on the track
            param_index: Parameter index on the device

        Returns:
            True if sweep was stopped, False if not active
        """
        key = (track_index, device_index, param_index)

        with self._lock:
            if key not in self._sweeps:
                return False

            state = self._sweeps[key]
            if not state.active:
                return False

            state.stop_event.set()
            state.active = False

            # Wait for thread to finish (with timeout)
            if state.thread and state.thread.is_alive():
                state.thread.join(timeout=0.5)

            return True

    def emergency_stop(self) -> None:
        """
        Emergency stop: set all parameters to baseline within 100ms.

        Stops all active sweeps and sends baseline values for all
        configured tracks in rapid succession via UDP.
        """
        # Stop all active sweeps
        with self._lock:
            for key, state in self._sweeps.items():
                if state.active:
                    state.stop_event.set()
                    state.active = False

            # Clear return-to-center threads
            for key, thread in self._return_to_center_threads.items():
                if key in self._sweeps:
                    self._sweeps[key].stop_event.set()

        # Send baseline values for all configured tracks
        # Using UDP fire-and-forget for speed
        volume_baselines = BASELINE_VALUES.get("volume", {})

        for track_name, volume in volume_baselines.items():
            if track_name == "master":
                # Master volume via separate command
                command = {"type": "set_master_volume", "params": {"volume": volume}}
            else:
                track_index = TRACKS.get(track_name, -1)
                if track_index < 0:
                    continue
                command = {
                    "type": "set_track_volume",
                    "params": {"track_index": track_index, "volume": volume},
                }

            self._send_udp(command)

        # Reset filter parameters to default
        filter_defaults = BASELINE_VALUES.get("filter", {})
        pads_track = TRACKS.get("pads", -1)
        if pads_track >= 0 and filter_defaults:
            # Send filter default (device/param indices depend on setup)
            # This is a best-effort reset
            default_hz = filter_defaults.get("pads_default_hz", 800)
            # Normalize: assume 100-5000 Hz range mapped to 0-1
            normalized = (default_hz - 100) / (5000 - 100)
            normalized = max(0.0, min(1.0, normalized))
            # Note: Actual device/param indices need to be configured per setup
            # For now, we reset the internal state
            for key in list(self._sweeps.keys()):
                if key[0] == pads_track:
                    self.set_parameter(key[0], key[1], key[2], normalized)

    def is_sweep_active(
        self,
        track_index: int,
        device_index: int,
        param_index: int,
    ) -> bool:
        """Check if a sweep is currently active for the given parameter."""
        key = (track_index, device_index, param_index)
        with self._lock:
            return key in self._sweeps and self._sweeps[key].active

    def get_active_sweeps(self) -> list:
        """Get list of all active sweep keys."""
        with self._lock:
            return [key for key, state in self._sweeps.items() if state.active]

    def close(self) -> None:
        """Close the UDP socket and stop all sweeps."""
        # Stop all sweeps
        with self._lock:
            for state in self._sweeps.values():
                state.stop_event.set()
                state.active = False

        # Close socket
        try:
            self._socket.close()
        except Exception:
            pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# Module-level singleton for convenience
_controller: Optional[UDPController] = None


def get_controller() -> UDPController:
    """Get or create the module-level UDP controller singleton."""
    global _controller
    if _controller is None:
        _controller = UDPController()
    return _controller
