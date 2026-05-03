"""
Integration Tests for Ableton MCP Extended

This module provides comprehensive integration tests for the Ableton MCP Extended system,
testing end-to-end workflows with actual Ableton Live sessions.

The tests verify:
- Track type validation (MIDI vs audio tracks)
- Clip creation and management
- Device and parameter control
- Session templates and presets
- Real-time parameter polling
- Error handling and recovery scenarios
"""

# Note: Individual test modules are imported by pytest during collection.
# The test_plugin_analysis module was removed; this package now contains:
# - test_track_validation.py: Track type validation tests
# - dub/: Dub techno integration tests

__all__ = []
