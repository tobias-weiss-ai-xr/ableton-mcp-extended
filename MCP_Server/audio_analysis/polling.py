"""
Audio Analysis Parameter Poller

Continuously polls VST plugin parameters at configurable rates for real-time
audio analysis in Ableton Live sessions.

This module provides the polling infrastructure that reads audio analysis parameters
from VST plugins and dispatches them to rule engines for decision-making.
"""

import time
import threading
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from collections import deque
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ParameterConfig:
    """Configuration for a monitored parameter"""

    index: int  # Parameter index in VST device
    name: str  # Parameter name
    min_value: float = 0.0  # Raw minimum value
    max_value: float = 1.0  # Raw maximum value
    unit: str = ""  # Unit (e.g., "LUFS", "dB", "Hz")


@dataclass
class ParameterSnapshot:
    """Snapshot of parameter values at a specific time"""

    timestamp: float  # Unix timestamp
    values: Dict[int, float]  # Normalized values by param index
    raw_values: Dict[int, float]  # Raw values by param index


class CircularBuffer:
    """Circular buffer for storing time-series parameter history"""

    def __init__(self, max_size: int = 1000):
        """
        Initialize circular buffer

        Args:
            max_size: Maximum number of snapshots to store
        """
        self.max_size = max_size
        self.buffer: deque = deque(maxlen=max_size)
        self.lock = threading.Lock()

    def push(self, snapshot: ParameterSnapshot):
        """Add snapshot to buffer"""
        with self.lock:
            self.buffer.append(snapshot)

    def get_latest(self, n: int = 1) -> List[ParameterSnapshot]:
        """Get n most recent snapshots"""
        with self.lock:
            return (
                list(self.buffer)[-n:] if len(self.buffer) >= n else list(self.buffer)
            )

    def get_time_range(self, duration_seconds: float) -> List[ParameterSnapshot]:
        """Get snapshots within time duration"""
        cutoff_time = time.time() - duration_seconds
        with self.lock:
            return [s for s in self.buffer if s.timestamp >= cutoff_time]

    def clear(self):
        """Clear buffer"""
        with self.lock:
            self.buffer.clear()

    def size(self) -> int:
        """Get current buffer size"""
        with self.lock:
            return len(self.buffer)


class AudioAnalysisPoller:
    """
    Main polling class for VST audio analysis parameters

    Continuously polls VST plugin parameters at configurable rates and
    dispatches values to registered callbacks (e.g., rule engine).
    """

    def __init__(
        self,
        track_index: int,
        device_index: int,
        params_to_poll: List[ParameterConfig],
        update_rate_hz: float = 10.0,
        buffer_size: int = 1000,
        mcp_client: Optional[Any] = None,
    ):
        """
        Initialize audio analysis poller

        Args:
            track_index: Ableton track index
            device_index: VST device index on track
            params_to_poll: List of parameter configurations to monitor
            update_rate_hz: Polling frequency in Hz (default: 10 Hz)
            buffer_size: Max snapshots in circular buffer
            mcp_client: MCP client instance for accessing Ableton (injected)
        """
        self.track_index = track_index
        self.device_index = device_index
        self.params_to_poll = {p.index: p for p in params_to_poll}  # index -> config
        self.update_rate_hz = update_rate_hz
        self.update_interval = 1.0 / update_rate_hz
        self.buffer = CircularBuffer(max_size=buffer_size)
        self.mcp_client = mcp_client

        # State
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.latest_snapshot: Optional[ParameterSnapshot] = None

        # Callbacks for rule engine integration
        self.callbacks: List[Callable[[ParameterSnapshot], None]] = []

        # Performance tracking
        self.last_poll_time: Optional[float] = None
        self.poll_count = 0

    def add_callback(self, callback: Callable[[ParameterSnapshot], None]):
        """Register callback to receive parameter snapshots"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            logger.debug(f"Registered callback: {callback.__name__}")

    def remove_callback(self, callback: Callable[[ParameterSnapshot], None]):
        """Unregister callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logger.debug(f"Removed callback: {callback.__name__}")

    def start(self):
        """Start polling thread"""
        if self.running:
            logger.warning("Poller already running")
            return

        logger.info(
            f"Starting poller: Track {self.track_index}, Device {self.device_index}, "
            f"Rate: {self.update_rate_hz} Hz, Parameters: {len(self.params_to_poll)}"
        )

        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop polling thread"""
        if not self.running:
            return

        logger.info("Stopping poller...")
        self.running = False

        if self.thread:
            self.thread.join(timeout=2.0)

            if self.thread.is_alive():
                logger.warning("Poller thread did not stop gracefully")

        logger.info(
            f"Poller stopped. Total polls: {self.poll_count}, "
            f"Avg rate: {self._calculate_actual_rate():.2f} Hz"
        )

    def _poll_loop(self):
        """Main polling loop (runs in separate thread)"""
        logger.debug("Poll loop started")

        while self.running:
            poll_start = time.time()

            try:
                # Poll parameters
                snapshot = self._poll_parameters()

                if snapshot:
                    # Store in buffer
                    self.buffer.push(snapshot)
                    self.latest_snapshot = snapshot

                    # Notify callbacks (rule engine)
                    for callback in self.callbacks:
                        try:
                            callback(snapshot)
                        except Exception as e:
                            logger.error(f"Callback error: {e}", exc_info=True)

                # Update performance tracking
                self.last_poll_time = time.time()
                self.poll_count += 1

                # Sleep to maintain target rate
                elapsed = time.time() - poll_start
                sleep_time = self.update_interval - elapsed

                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    logger.warning(
                        f"Poll took {elapsed * 1000:.1f}ms, exceeding interval {self.update_interval * 1000:.1f}ms"
                    )

            except Exception as e:
                logger.error(f"Polling error: {e}", exc_info=True)
                # Sleep to avoid tight error loop
                time.sleep(0.1)

        logger.debug("Poll loop stopped")

    def _poll_parameters(self) -> Optional[ParameterSnapshot]:
        """
        Poll parameters from VST device

        Returns:
            ParameterSnapshot with current values, or None on error
        """
        if self.mcp_client is None:
            logger.warning("MCP client not configured, no polling possible")
            return None

        try:
            # Call MCP tool to get device parameters
            params = self.mcp_client.call_tool(
                "ableton-mcp-server_get_device_parameters",
                {"track_index": self.track_index, "device_index": self.device_index},
            )

            # Extract monitored parameter values
            raw_values = {}
            normalized_values = {}

            for index, config in self.params_to_poll.items():
                if index < len(params):
                    raw_value = params[index].get("value", 0.0)
                    raw_values[index] = raw_value

                    # Normalize to 0.0-1.0 range
                    if config.max_value > config.min_value:
                        normalized = (raw_value - config.min_value) / (
                            config.max_value - config.min_value
                        )
                        normalized_values[index] = normalized
                    else:
                        normalized_values[index] = raw_value

                else:
                    logger.warning(f"Parameter index {index} not available from device")

            # Create snapshot
            snapshot = ParameterSnapshot(
                timestamp=time.time(), values=normalized_values, raw_values=raw_values
            )

            return snapshot

        except Exception as e:
            logger.error(f"Failed to poll parameters: {e}", exc_info=True)
            return None

    def get_latest_snapshot(self) -> Optional[ParameterSnapshot]:
        """Get most recent parameter snapshot"""
        return self.latest_snapshot

    def get_historical_snapshot(
        self, n_seconds_ago: float
    ) -> Optional[ParameterSnapshot]:
        """
        Get snapshot from n seconds ago

        Args:
            n_seconds_ago: How far back in time

        Returns:
            Closest snapshot to requested time, or None
        """
        snapshots = self.buffer.get_time_range(n_seconds_ago + 1.0)  # Buffer

        if not snapshots:
            return None

        # Find snapshot closest to requested time
        target_time = time.time() - n_seconds_ago
        closest = min(snapshots, key=lambda s: abs(s.timestamp - target_time))

        return closest

    def get_history(self, n: int = 10) -> List[ParameterSnapshot]:
        """Get n most recent snapshots"""
        return self.buffer.get_latest(n)

    def _calculate_actual_rate(self) -> float:
        """Calculate actual polling rate based on performance"""
        if self.poll_count == 0 or self.last_poll_time is None:
            return 0.0

        # Rough estimate based on total polls
        duration = time.time() - getattr(self, "start_time", time.time())
        if duration <= 0:
            return 0.0

        return self.poll_count / duration

    def get_status(self) -> Dict[str, Any]:
        """Get poller status and performance metrics"""
        return {
            "running": self.running,
            "track_index": self.track_index,
            "device_index": self.device_index,
            "update_rate_hz": self.update_rate_hz,
            "actual_rate_hz": self._calculate_actual_rate(),
            "parameters_polling": len(self.params_to_poll),
            "buffer_size": self.buffer.size(),
            "total_polls": self.poll_count,
            "callbacks_registered": len(self.callbacks),
        }


class MultiPluginPoller:
    """
    Manager for multiple pollers (multiple VST plugins/tracks)
    Coordinates polling across multiple audio analysis devices.
    """

    def __init__(self):
        """Initialize multi-plugin poller manager"""
        self.pollers: Dict[str, AudioAnalysisPoller] = {}  # name -> poller
        self.lock = threading.Lock()
        self.global_callbacks: List[Callable[[str, ParameterSnapshot], None]] = []

    def add_poller(self, name: str, poller: AudioAnalysisPoller):
        """Add poller to manager"""
        with self.lock:
            self.pollers[name] = poller

            # Wrap poller callback to include plugin name
            def wrapper(snapshot: ParameterSnapshot):
                for callback in self.global_callbacks:
                    try:
                        callback(name, snapshot)
                    except Exception as e:
                        logger.error(f"Global callback error: {e}", exc_info=True)

            poller.add_callback(wrapper)

    def remove_poller(self, name: str):
        """Remove poller from manager"""
        with self.lock:
            if name in self.pollers:
                self.pollers[name].stop()
                del self.pollers[name]

    def start_all(self):
        """Start all managed pollers"""
        with self.lock:
            for poller in self.pollers.values():
                poller.start()

    def stop_all(self):
        """Stop all managed pollers"""
        with self.lock:
            for poller in self.pollers.values():
                poller.stop()

    def add_global_callback(self, callback: Callable[[str, ParameterSnapshot], None]):
        """Register callback to receive snapshots from all pollers"""
        if callback not in self.global_callbacks:
            self.global_callbacks.append(callback)

    def remove_global_callback(
        self, callback: Callable[[str, ParameterSnapshot], None]
    ):
        """Unregister global callback"""
        if callback in self.global_callbacks:
            self.global_callbacks.remove(callback)

    def get_poller_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status of specific poller"""
        with self.lock:
            poller = self.pollers.get(name)
            return poller.get_status() if poller else None

    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all pollers"""
        with self.lock:
            return {name: poller.get_status() for name, poller in self.pollers.items()}
