"""
Error Handling and Recovery Module

Provides robust error detection, recovery strategies, and session stabilization
for 2-hour autonomous dub techno session.
"""

import sys
import time
import logging
from typing import Optional, Callable, List
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"           # Minor automation glitch, recoverable
    MEDIUM = "medium"     # Track/clip state compromised
    HIGH = "high"         # Session state corrupted
    CRITICAL = "critical" # Complete session failure


class RecoveryStrategy(Enum):
    """Recovery strategies."""
    RETRY = "retry"                       # Retry failed operation (max 3x)
    RESET_TRACK = "reset_track"           # Reset single track to default
    RESET_SCENE = "reset_scene"           # Reset all scene triggers
    ABORT_SESSION = "abort_session"       # Stop session completely
    CONTINUE_SAFE = "continue_safe"       # Continue with safe fallback


class ErrorContext:
    """Error context information."""
    def __init__(self, error_type: str, message: str, severity: ErrorSeverity,
                 operation: str, timestamp: float):
        self.error_type = error_type
        self.message = message
        self.severity = severity
        self.operation = operation
        self.timestamp = timestamp
        self.retry_count = 0
        self.max_retries = 3


class SessionErrorHandler:
    """Handles errors during 2-hour session automation."""

    # Safe default states
    SAFE_TRACK_VOLUMES = [0.7, 0.7, 0.6, 0.5, 0.4, 0.3]
    SAFE_FILTER_VALUES = 0.5
    SAFE_REVERB_VALUES = 0.3

    def __init__(self, log_file: str = "session_errors.log"):
        self.error_log: List[ErrorContext] = []
        self.log_file = log_file
        self.total_errors = 0
        self.session_aborted = False

        # Setup logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def handle_error(self, error_context: ErrorContext,
                    mcp_client) -> bool:
        """
        Handle error based on severity and context.

        Returns:
            True if recovery succeeded, False if session must abort
        """
        self.error_log.append(error_context)
        self.total_errors += 1

        self.logger.error(
            f"[{error_context.severity.value.upper()}] "
            f"{error_context.operation}: {error_context.message}"
        )

        # Determine recovery strategy
        strategy = self._determine_strategy(error_context)

        self.logger.info(f"Recovery strategy: {strategy.value}")

        # Execute recovery
        recovery_success = self._execute_recovery(error_context, strategy, mcp_client)

        if recovery_success:
            self.logger.info("Recovery successful, continuing session")
        else:
            self.logger.error("Recovery failed, aborting session")
            self.session_aborted = True

        return recovery_success

    def _determine_strategy(self, error: ErrorContext) -> RecoveryStrategy:
        """Determine recovery strategy based on error severity."""
        if error.severity == ErrorSeverity.LOW:
            # Low severity - retry or continue
            if error.retry_count < error.max_retries:
                return RecoveryStrategy.RETRY
            return RecoveryStrategy.CONTINUE_SAFE

        elif error.severity == ErrorSeverity.MEDIUM:
            # Medium severity - reset track or scene
            if "track" in error.operation.lower():
                return RecoveryStrategy.RESET_TRACK
            elif "clip" in error.operation.lower():
                return RecoveryStrategy.RESET_SCENE
            return RecoveryStrategy.CONTINUE_SAFE

        elif error.severity == ErrorSeverity.HIGH:
            # High severity - attempt safe state or abort
            if self.total_errors < 5:
                return RecoveryStrategy.RESET_SCENE
            return RecoveryStrategy.ABORT_SESSION

        else:  # CRITICAL
            # Critical - always abort
            return RecoveryStrategy.ABORT_SESSION

    def _execute_recovery(self, error: ErrorContext, strategy: RecoveryStrategy,
                         mcp_client) -> bool:
        """Execute recovery strategy."""
        try:
            if strategy == RecoveryStrategy.RETRY:
                return self._retry_operation(error)

            elif strategy == RecoveryStrategy.RESET_TRACK:
                return self._reset_track(error, mcp_client)

            elif strategy == RecoveryStrategy.RESET_SCENE:
                return self._reset_scene(error, mcp_client)

            elif strategy == RecoveryStrategy.CONTINUE_SAFE:
                return self._continue_safe(error, mcp_client)

            elif strategy == RecoveryStrategy.ABORT_SESSION:
                return self._abort_session(error, mcp_client)

        except Exception as recovery_error:
            self.logger.error(f"Recovery strategy failed: {recovery_error}")
            return False

        return False

    def _retry_operation(self, error: ErrorContext) -> bool:
        """Retry failed operation with exponential backoff."""
        error.retry_count += 1

        if error.retry_count > error.max_retries:
            self.logger.warning(f"Max retries exceeded for {error.operation}")
            return False

        backoff = 2 ** error.retry_count  # Exponential backoff
        self.logger.info(f"Retrying {error.operation} (attempt {error.retry_count})")

        time.sleep(backoff)
        return True  # Caller should retry operation

    def _reset_track(self, error: ErrorContext, mcp_client) -> bool:
        """Reset single track to safe default state."""
        try:
            # Extract track index from error message if possible
            track_idx = error.severity  # Hack: store track_idx in severity

            # Reset volume
            if track_idx < len(self.SAFE_TRACK_VOLUMES):
                mcp_client.set_track_volume(track_idx, self.SAFE_TRACK_VOLUMES[track_idx])

            # Reset pan
            mcp_client.set_track_pan(track_idx, 0.0)

            # Reset mute/solo
            mcp_client.set_track_mute(track_idx, False)
            mcp_client.set_track_solo(track_idx, False)

            self.logger.info(f"Track {track_idx} reset to safe state")
            return True

        except Exception as e:
            self.logger.error(f"Track reset failed: {e}")
            return False

    def _reset_scene(self, error: ErrorContext, mcp_client) -> bool:
        """Reset all scene triggers and automation to safe state."""
        try:
            # Stop playback
            mcp_client.stop_playback()

            # Reset all track volumes
            for track_idx, volume in enumerate(self.SAFE_TRACK_VOLUMES):
                try:
                    mcp_client.set_track_volume(track_idx, volume)
                except Exception:
                    pass

            Reset all filters to mid range
            for track_idx in range(5):
                # Attempt to reset filter cutoff (device 0, param 2)
                try:
                    mcp_client.set_device_parameter(track_idx, 0, 2, 0.5)
                except Exception:
                    pass

            # Reset to intro scene
            mcp_client.fire_scene(0)

            self.logger.info("Scene reset to safe state")
            return True

        except Exception as e:
            self.logger.error(f"Scene reset failed: {e}")
            return False

    def _continue_safe(self, error: ErrorContext, mcp_client) -> bool:
        """Continue session with safe fallback operation."""
        self.logger.warning("Continuing with safe fallback")

        # Ensure playback stopped
        try:
            mcp_client.stop_playback()
        except Exception:
            pass

        return True

    def _abort_session(self, error: ErrorContext, mcp_client) -> bool:
        """Abort session - clean shutdown."""
        self.logger.critical("Aborting session")

        try:
            # Stop everything
            mcp_client.stop_playback()

            # Mute all tracks
            for track_idx in range(6):
                try:
                    mcp_client.set_track_volume(track_idx, 0.0)
                except Exception:
                    pass

            return True

        except Exception as e:
            self.logger.error(f"Session abort error: {e}")
            return False

    def get_error_summary(self) -> dict:
        """Get error summary statistics."""
        # Count by severity
        severity_counts = {s.value: 0 for s in ErrorSeverity}
        for error in self.error_log:
            severity_counts[error.severity.value] += 1

        return {
            'total_errors': self.total_errors,
            'by_severity': severity_counts,
            'session_aborted': self.session_aborted,
            'errors_log': len(self.error_log)
        }


# Convenience error context factory
def create_error_context(error_type: str, message: str, severity: ErrorSeverity,
                        operation: str) -> ErrorContext:
    """Create error context with automatic timestamp."""
    return ErrorContext(
        error_type=error_type,
        message=message,
        severity=severity,
        operation=operation,
        timestamp=time.time()
    )


# Decorator for error-wrapped operations
def with_error_handling(error_handler: SessionErrorHandler, operation: str):
    """Decorator wrapping operations with error handling."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Determine error severity
                if "timeout" in str(e).lower() or "connection" in str(e).lower():
                    severity = ErrorSeverity.HIGH
                elif "track" in str(e).lower() or "clip" in str(e).lower():
                    severity = ErrorSeverity.MEDIUM
                else:
                    severity = ErrorSeverity.LOW

                error_context = create_error_context(
                    error_type=type(e).__name__,
                    message=str(e),
                    severity=severity,
                    operation=operation
                )

                # Handle error
                recovery_success = error_handler.handle_error(error_context, args[0])  # mcp_client is first arg

                if recovery_success:
                    # Retry if low/medium severity
                    if severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]:
                        return func(*args, **kwargs)
                    return None
                else:
                    # Abort - exit the session
                    sys.exit(1)

        return wrapper
    return decorator