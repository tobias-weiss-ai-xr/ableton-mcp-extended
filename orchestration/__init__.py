"""
Orchestration layer for Ableton MCP Extended.

Pure-Python in-process DAG orchestration with circuit breakers and
retry (replaces the earlier Node.js AgentFlow bridge, which depended
on a non-existent `agentflow` npm package).

Architecture:
    DAGExecutionEngine (orchestration/agentflow_runner.py, stdlib only)
        ↕ per-task circuit breakers (orchestration/circuit_breaker.py)
    agentic_mix nodes -> Ableton Live (via MCP)

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
from .agentflow_runner import AgentFlowRunner, DAGExecutionEngine, MIX_WORKFLOW, Task, RetryPolicy

__all__ = [
    "AgentFlowRunner",
    "DAGExecutionEngine",
    "MIX_WORKFLOW",
    "Task",
    "RetryPolicy",
    "AbletonCircuitBreaker",
    "AbletonCircuitBreakerRegistry",
    "CircuitOpenError",
    "CircuitState",
]
