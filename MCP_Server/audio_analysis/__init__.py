"""
Audio Analysis Module for Ableton MCP Extended

This module provides real-time audio analysis and responsive control capabilities
using VST plugins with exposed parameters.

Components:
- polling.py: Parameter polling from VST plugins
- rules.py: YAML-configurable rule engine for control decisions
- control_loop.py: Integration layer combining polling and rules
- analyzer.py: Real-time audio analysis (BPM, key, loudness, spectral)
- config.py: Configuration for audio analyzer
- websocket_server.py: WebSocket streaming for dashboards

Usage:
    from MCP_Server.audio_analysis import (
        AudioAnalysisController,
        AudioAnalyzer,
        AudioAnalyzerConfig,
    )

    # Real-time audio analysis
    config = AudioAnalyzerConfig(sample_rate=44100)
    analyzer = AudioAnalyzer(config)
    analyzer.start()

    # Get analysis results
    analysis = analyzer.get_analysis()
    print(f"BPM: {analysis['bpm']}, Key: {analysis['key']}")

    # Stop when done
    analyzer.stop()
"""

from .polling import (
    ParameterConfig,
    ParameterSnapshot,
    CircularBuffer,
    AudioAnalysisPoller,
    MultiPluginPoller,
)

from .rules import (
    Operator,
    Condition,
    Action,
    Rule,
    RuleSet,
    RuleEngine,
    # Audio analysis conditions (Task 8 - Auto-DJ Integration)
    AudioConditionType,
    AudioAnalysisCondition,
)

from .control_loop import (
    AudioAnalysisController,
    run_with_graceful_shutdown,
)

# Real-time audio analysis
from .config import AudioAnalyzerConfig
from .analyzer import AudioAnalyzer

__all__ = [
    # Polling
    "ParameterConfig",
    "ParameterSnapshot",
    "CircularBuffer",
    "AudioAnalysisPoller",
    "MultiPluginPoller",
    # Rules
    "Operator",
    "Condition",
    "Action",
    "Rule",
    "RuleSet",
    "RuleEngine",
    # Audio analysis conditions
    "AudioConditionType",
    "AudioAnalysisCondition",
    # Control Loop
    "AudioAnalysisController",
    "run_with_graceful_shutdown",
    # Real-time audio analysis
    "AudioAnalyzerConfig",
    "AudioAnalyzer",
]
__version__ = "1.0.0"
