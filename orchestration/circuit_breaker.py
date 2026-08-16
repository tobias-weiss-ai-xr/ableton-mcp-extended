"""
Circuit breaker for Ableton MCP calls.

Provides resilience for the AgentFlow orchestration layer, protecting against
repeated Ableton MCP failures (transport errors, timeout, Ableton crashes).

Pattern from AgentFlow (TaskFleet) CircuitBreaker:
- CLOSED → open after N consecutive failures → HALF_OPEN (test with limited calls)
- HALF_OPEN → if test succeeds → CLOSED; if fails → OPEN
- OPEN → wait recovery_timeout → HALF_OPEN

Usage:
    from orchestration.circuit_breaker import AbletonCircuitBreaker

    breaker = AbletonCircuitBreaker("create_track")
    try:
        result = breaker.call(mcp_client.create_midi_track, index=-1)
    except CircuitOpenError:
        print("Ableton MCP track creation is temporarily circuit-broken")
"""

from __future__ import annotations

import enum
import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when a circuit is open and the call is rejected."""

    def __init__(self, operation: str, failure_count: int, recovery_timeout: float):
        self.operation = operation
        self.failure_count = failure_count
        self.recovery_timeout = recovery_timeout
        super().__init__(
            f"Circuit open for '{operation}' "
            f"(failures: {failure_count}, "
            f"recovery in {recovery_timeout:.0f}s)"
        )


class AbletonCircuitBreaker:
    """
    Circuit breaker for MCP calls, grounded in AgentFlow's circuit breaker pattern.

    Protects against cascading failures when Ableton Live is unresponsive,
    the Remote Script crashes, or the MCP server restarts. Each operation
    (e.g., "create_track", "fire_clip", "set_parameter") gets its own breaker,
    so a failure in clip creation doesn't block transport control.

    Args:
        operation: Name of the MCP operation (for logging/identification)
        failure_threshold: Consecutive failures before opening circuit
        recovery_timeout_ms: Seconds to wait in OPEN before trying again
        half_open_max_calls: Test calls allowed in HALF_OPEN
    """

    def __init__(
        self,
        operation: str,
        failure_threshold: int = 3,
        recovery_timeout_ms: int = 30000,
        half_open_max_calls: int = 2,
    ):
        self.operation = operation
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_ms / 1000.0
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        self._last_failure_time: float = 0
        self._total_failures = 0
        self._total_successes = 0
        self._last_success_time: float = 0

    @property
    def state(self) -> CircuitState:
        return self._state

    @property
    def is_available(self) -> bool:
        """Whether calls are allowed right now."""
        if self._state == CircuitState.CLOSED:
            return True
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                return True  # Recovery timeout elapsed, will transition to HALF_OPEN
            return False
        if self._state == CircuitState.HALF_OPEN:
            return self._half_open_calls < self.half_open_max_calls
        return False

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a call through the circuit breaker.

        Raises CircuitOpenError if the circuit is open and recovery
        timeout hasn't elapsed.

        Args:
            func: Callable to execute (e.g., mcp_client.create_midi_track)
            *args, **kwargs: Arguments for the callable

        Returns:
            Result from the callable

        Raises:
            CircuitOpenError: If circuit is open
        """
        if not self.is_available:
            # Check if we should transition to HALF_OPEN
            if self._state == CircuitState.OPEN and \
               time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info(
                    f"[circuit] {self.operation}: OPEN → HALF_OPEN "
                    f"(testing after {self.recovery_timeout:.0f}s cooldown)"
                )
            else:
                raise CircuitOpenError(
                    self.operation,
                    self._failure_count,
                    self.recovery_timeout,
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _on_success(self) -> None:
        """Handle a successful call."""
        self._total_successes += 1
        self._last_success_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                self._state = CircuitState.CLOSED
                logger.info(
                    f"[circuit] {self.operation}: HALF_OPEN → CLOSED "
                    f"({self.half_open_max_calls} successful test calls)"
                )
            # Keep in HALF_OPEN if not enough test calls yet
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success in CLOSED state
            if self._failure_count > 0:
                logger.debug(
                    f"[circuit] {self.operation}: failure_count reset "
                    f"(was {self._failure_count})"
                )
            self._failure_count = 0

    def _on_failure(self, error: Exception) -> None:
        """Handle a failed call."""
        self._total_failures += 1
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.CLOSED:
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    f"[circuit] {self.operation}: CLOSED → OPEN "
                    f"(threshold={self.failure_threshold} failures)"
                )

        elif self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning(
                f"[circuit] {self.operation}: HALF_OPEN → OPEN "
                f"(failure during test)"
            )

    @property
    def stats(self) -> Dict[str, Any]:
        """Return circuit breaker statistics."""
        return {
            "operation": self.operation,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
            "last_failure_time": self._last_failure_time,
            "last_success_time": self._last_success_time,
        }

    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        logger.info(f"[circuit] {self.operation}: manually reset to CLOSED")


# ── Registry for per-operation breakers ─────────────────────────────────────

class AbletonCircuitBreakerRegistry:
    """
    Registry of circuit breakers keyed by MCP operation name.

    Usage:
        registry = AbletonCircuitBreakerRegistry()
        registry.call("create_midi_track", mcp.create_midi_track, index=-1)
    """

    def __init__(self, default_threshold: int = 3, default_timeout_ms: int = 30000):
        self._default_threshold = default_threshold
        self._default_timeout = default_timeout_ms
        self._breakers: Dict[str, AbletonCircuitBreaker] = {}

    def get(self, operation: str) -> AbletonCircuitBreaker:
        """Get or create a breaker for an operation."""
        if operation not in self._breakers:
            self._breakers[operation] = AbletonCircuitBreaker(
                operation,
                failure_threshold=self._default_threshold,
                recovery_timeout_ms=self._default_timeout,
            )
        return self._breakers[operation]

    def call(self, operation: str, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Call a function through its circuit breaker."""
        return self.get(operation).call(func, *args, **kwargs)

    def stats(self) -> Dict[str, Dict[str, Any]]:
        """Return all breaker stats."""
        return {op: b.stats for op, b in self._breakers.items()}

    def reset_all(self) -> None:
        """Reset all breakers to CLOSED."""
        for b in self._breakers.values():
            b.reset()

    @property
    def operations(self) -> list[str]:
        return list(self._breakers.keys())
