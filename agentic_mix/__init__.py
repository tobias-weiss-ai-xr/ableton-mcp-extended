"""
Agentic Mix Pipeline

AI-driven Ableton Live session generation and automated mixing.
Nodes are plain Python functions; graph.py requires langgraph (optional).
"""

from .state import GraphState

try:
    from .graph import create_mix_pipeline
except ImportError:
    create_mix_pipeline = None

__all__ = ["GraphState", "create_mix_pipeline"]
