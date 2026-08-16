"""
Orchestration layer for Ableton MCP Extended.

Provides AgentFlow-based DAG orchestration with circuit breakers,
checkpoint persistence, and event-driven coordination.

Architecture:
    Python Agent Server (HTTP)
        ↕
    Node.js AgentFlow Bridge (DAG engine, circuit breakers, checkpoints)
        ↕
    Ableton Live (via MCP)

Usage:
    from orchestration.agentflow_runner import AgentFlowRunner

    runner = AgentFlowRunner()
    result = runner.run(config_dict)
"""

from .circuit_breaker import (
    AbletonCircuitBreaker,
    AbletonCircuitBreakerRegistry,
    CircuitOpenError,
    CircuitState,
)
from .agentflow_runner import AgentFlowRunner

__all__ = [
    "AgentFlowRunner",
    "AbletonCircuitBreaker",
    "AbletonCircuitBreakerRegistry",
    "CircuitOpenError",
    "CircuitState",
]
