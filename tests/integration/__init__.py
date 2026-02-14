"""
Integration Tests for VST Audio Analysis System

This module provides comprehensive integration tests for the VST audio analysis system,
testing end-to-end workflows with actual Ableton Live sessions.

The tests verify:
- Real-time parameter polling with actual VST plugins
- Responsive control loop with rule-based decisions
- Multiple scenarios (quiet audio, loud audio, frequency sweeps, tempo changes)
- Error handling and recovery scenarios
"""

from .test_plugin_analysis import main as main_test

__all__ = ["test_plugin_analysis"]
