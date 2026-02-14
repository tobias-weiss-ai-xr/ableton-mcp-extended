"""
Audio Analysis Module for Ableton MCP Extended

This module provides real-time audio analysis and responsive control capabilities
using VST plugins with exposed parameters.

Components:
- polling.py: Parameter polling from VST plugins
- rules.py: YAML-configurable rule engine for control decisions
- control_loop.py: Integration layer combining polling and rules
- example_control_loop.py: Usage examples

Usage:
    from MCP_Server.audio_analysis import (
        AudioAnalysisController,
        ParameterConfig,
    )

    # Configure parameters to monitor
    params = [ParameterConfig(index=0, name="LUFS", min_value=-70, max_value=5, unit="LUFS")]

    # Create controller
    controller = AudioAnalysisController(
        track_index=0,
        device_index=0,
        params_to_poll=params,
        mcp_client=mcp_client,
    )

    # Load rules from YAML
    controller.load_ruleset("MCP_Server/audio_analysis/example_rules.yaml")

    # Start control loop
    controller.start()

    # ... system runs autonomously ...

    # Stop when done
    controller.stop()
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
)

from .control_loop import (
    AudioAnalysisController,
    run_with_graceful_shutdown,
)

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
    # Control Loop
    "AudioAnalysisController",
    "run_with_graceful_shutdown",
]

__version__ = "1.0.0"
