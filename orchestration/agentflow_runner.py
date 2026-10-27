"""
AgentFlow-style DAG runner (pure Python, in-process).

Replaces the earlier Node.js bridge, which depended on a non-existent
`agentflow` npm package (TaskFleet symlink), with a stdlib DAG executor:

  - sequential DAG execution (linear chain; the section loop stays
    inside the handler task)
  - per-task circuit breakers (orchestration.circuit_breaker)
  - retry with exponential backoff
  - in-memory checkpoints (optional JSON observability)

Workflow: configure -> setup_session -> generate_clips -> construct_arrangement
          -> execute_section_loop -> analyze_and_adapt

Usage:
    from orchestration.agentflow_runner import AgentFlowRunner

    runner = AgentFlowRunner()
    result = runner.run(config_dict)

Or from CLI:
    python -m orchestration.agentflow_runner --genre dub_techno --tempo 126 --duration 120
    python -m orchestration.agentflow_runner --self-check
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from .circuit_breaker import AbletonCircuitBreakerRegistry, CircuitOpenError

logger = logging.getLogger(__name__)


# -- Dry-run mocks (patch TCP/UDP/audio so the pipeline runs without Live) -----

def _dry_run_tcp(cmd, params=None):
    """Canned TCP responses: success for setters, minimal data for getters."""
    if cmd == "get_return_tracks":
        return {"status": "success", "return_tracks": [{"index": 0, "name": "A"}]}
    if cmd == "get_session_info":
        return {"status": "success", "tempo": 126, "tracks": 4}
    if cmd == "get_all_tracks":
        return {"status": "success", "tracks": []}
    if cmd == "get_all_scenes":
        return {"status": "success", "scenes": []}
    if cmd == "get_crossfader_position":
        return {"status": "success", "position": 0.5}
    return {"status": "success"}


def _dry_run_udp(cmd, params):
    return None


def _dry_run_capture(config):
    """Valid AudioAnalysisData-shaped snapshot (mid-range values)."""
    return {
        "timestamp": 0.0,
        "bpm": None,
        "beat": None,
        "rms": 0.5,
        "loudness_lufs": -18.0,
        "key": None,
        "key_confidence": None,
        "spectral_centroid_hz": 5000.0,
        "spectral_rolloff_hz": 1000.0,
        "semantic_mert_features": {"mert_available": False},
    }


# -- Task model ---------------------------------------------------------------

@dataclass(frozen=True)
class RetryPolicy:
    """Per-task retry policy with exponential backoff."""
    max_attempts: int = 2
    initial_delay_ms: int = 2000
    backoff_multiplier: float = 2.0


@dataclass(frozen=True)
class Task:
    """A single workflow step, dispatched to a handler method by name."""
    id: str
    action: str  # handler method name
    name: str = ""
    depends_on: Tuple[str, ...] = ()
    retry: RetryPolicy = RetryPolicy()
    critical: bool = True  # failure stops the workflow


MIX_WORKFLOW = (
    Task("configure", "configure", "Configure Mix"),
    Task("setup-session", "setup_session", "Setup Session", depends_on=("configure",)),
    Task("generate-clips", "generate_clips", "Generate Clips",
         depends_on=("setup-session",), retry=RetryPolicy(3, 3000, 2.0)),
    Task("construct-arrangement", "construct_arrangement", "Construct Arrangement",
         depends_on=("generate-clips",)),
    Task("execute-section-loop", "execute_section_loop", "Section Execution Loop",
         depends_on=("construct-arrangement",), retry=RetryPolicy(1, 1000, 1.0)),
    Task("analyze-and-adapt", "analyze_and_adapt", "Analyze and Adapt",
         depends_on=("execute-section-loop",)),
)


def _validate_dag(tasks) -> None:
    """Reject duplicate ids and dependencies that are not declared earlier."""
    seen = set()
    for t in tasks:
        missing = [d for d in t.depends_on if d not in seen]
        if missing:
            raise ValueError(
                f"task '{t.id}' depends on {missing} - deps must be declared earlier"
            )
        if t.id in seen:
            raise ValueError(f"duplicate task id: {t.id}")
        seen.add(t.id)


# -- DAG execution engine -----------------------------------------------------

class DAGExecutionEngine:
    """Executes tasks in declaration order, verifying dependencies are met.

    Each task runs through a per-task circuit breaker (a failed task never
    poisons unrelated tasks) with the task's retry policy on top.

    ponytail: linear-chain assumption - tasks run in declaration order with a
    dependency check, no topological sort or parallelism. If the workflow ever
    branches, topo-sort the task list first.
    """

    def __init__(
        self,
        tasks,
        breakers: Optional[AbletonCircuitBreakerRegistry] = None,
        checkpoint_path: Optional[str] = None,
        timeout_s: float = 7200.0,
    ):
        _validate_dag(tasks)
        self.tasks = list(tasks)
        self.breakers = breakers or AbletonCircuitBreakerRegistry()
        self.checkpoint_path = checkpoint_path
        self.timeout_s = timeout_s

    def run(self, handler: Any, context: Optional[Dict[str, Any]] = None,
            on_progress: Optional[Callable] = None) -> Dict[str, Any]:
        """Run all tasks. Returns {status, task_results, errors, elapsed_s}.

        on_progress(task_id, result, elapsed_s) fires after each completed task.
        """
        context = context or {}
        completed: Dict[str, Any] = {}
        errors: List[str] = []
        started = time.time()

        for task in self.tasks:
            if self.timeout_s and time.time() - started > self.timeout_s:
                errors.append(f"workflow timeout after {self.timeout_s:.0f}s at task '{task.id}'")
                break

            fn = getattr(handler, task.action, None)
            if fn is None:
                errors.append(f"handler has no action '{task.action}' (task '{task.id}')")
                if task.critical:
                    break
                continue

            result, err = self._execute(task, fn, context)
            if err is None:
                completed[task.id] = result
                self._checkpoint(completed)
                if on_progress:
                    on_progress(task.id, result, time.time() - started)
                logger.info("[dag] %s done", task.id)
            else:
                errors.append(f"{task.id}: {err}")
                logger.error("[dag] %s failed permanently: %s", task.id, err)
                if task.critical:
                    break

        status = "completed" if len(completed) == len(self.tasks) and not errors else "failed"
        return {
            "status": status,
            "task_results": completed,
            "errors": errors,
            "elapsed_s": round(time.time() - started, 1),
        }

    def _execute(self, task, fn: Callable, context: Dict[str, Any]):
        """Run one task with retries. Returns (result, None) or (None, error)."""
        last_err = None
        for attempt in range(1, task.retry.max_attempts + 1):
            try:
                return self.breakers.call(task.id, fn, context), None
            except CircuitOpenError as e:
                return None, f"circuit open: {e}"
            except Exception as e:  # task errors must not kill the engine
                last_err = str(e)
                if attempt < task.retry.max_attempts:
                    delay = task.retry.initial_delay_ms / 1000.0 * (
                        task.retry.backoff_multiplier ** (attempt - 1)
                    )
                    logger.warning(
                        "[dag] %s attempt %d failed: %s; retrying in %.1fs",
                        task.id, attempt, e, delay,
                    )
                    time.sleep(delay)
        return None, last_err

    def _checkpoint(self, completed: Dict[str, Any]) -> None:
        # ponytail: observability-only checkpoint (matches the old
        # InMemoryCheckpointStore - it never survived restarts either).
        # True crash-resume needs serializable handler state; upgrade path:
        # pickle GraphState per task and replay skipped tasks.
        if not self.checkpoint_path:
            return
        try:
            with open(self.checkpoint_path, "w", encoding="utf-8") as f:
                json.dump({"completed": sorted(completed)}, f)
        except OSError as e:
            logger.debug("checkpoint write failed: %s", e)


# -- Public runner (drop-in replacement for the bridge-based API) -------------

class AgentFlowRunner:
    """Runs the agentic mix workflow in-process with circuit breakers."""

    def __init__(self, checkpoint_path=None):
        self.checkpoint_path = checkpoint_path
        self.engine = None

    def run(self, config, handler=None, timeout=7200.0, on_progress=None, dry_run=False):
        """Execute the full mix workflow. Returns status/results/feedback/metrics.

        on_progress(task_id, result, elapsed_s) fires after each completed task.
        dry_run=True mocks all Ableton TCP/UDP/audio calls (no Live needed).
        """
        if handler is None:
            handler = self._default_handler()
        self.engine = DAGExecutionEngine(
            MIX_WORKFLOW, checkpoint_path=self.checkpoint_path, timeout_s=timeout
        )
        if dry_run:
            from unittest.mock import patch
            patches = [
                patch("agentic_mix.tools._client.tcp_command", _dry_run_tcp),
                patch("agentic_mix.tools._client.udp_command", _dry_run_udp),
                patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot", _dry_run_capture),
            ]
            for p in patches:
                p.start()
            try:
                outcome = self.engine.run(handler, context={"config": dict(config)}, on_progress=on_progress)
            finally:
                for p in patches:
                    p.stop()
        else:
            outcome = self.engine.run(handler, context={"config": dict(config)}, on_progress=on_progress)
        # Surface section-level errors from inside execute-section-loop
        execute_result = outcome["task_results"].get("execute-section-loop") or {}
        section_errors = execute_result.get("errors", [])
        adapt = outcome["task_results"].get("analyze-and-adapt") or {}
        return {
            "status": outcome["status"],
            "results": outcome["task_results"],
            "errors": list(outcome["errors"]) + list(section_errors),
            "sections": execute_result.get("sections", 0),
            "feedback": adapt.get("feedback", []),
            "metrics": adapt.get("metrics", {}),
        }

    def _default_handler(self):
        """Create a handler from the existing agentic_mix node functions."""
        from agentic_mix.state import (
            Config, GraphState, create_playback_metrics,
            create_session_info, create_track_state,
        )

        class MixHandler:
            """Wraps existing agentic_mix nodes as an AgentFlow task handler."""

            def __init__(self):
                from agentic_mix.nodes.analyze_adapt import analyze_and_adapt_node
                from agentic_mix.nodes.analyze_section import analyze_section_node
                from agentic_mix.nodes.configure import configure_node
                from agentic_mix.nodes.construct_arrangement import construct_arrangement_node
                from agentic_mix.nodes.execute_section import execute_section_node
                from agentic_mix.nodes.generate_clips import generate_clips_node
                from agentic_mix.nodes.setup_session import setup_session_node
                self._configure = configure_node
                self._setup_session = setup_session_node
                self._generate_clips = generate_clips_node
                self._construct_arrangement = construct_arrangement_node
                self._execute_section = execute_section_node
                self._analyze_section = analyze_section_node
                self._analyze_and_adapt = analyze_and_adapt_node
                self._state = None  # state passed between calls

            def _init_state(self, config_dict):
                config = Config(**{k: v for k, v in config_dict.items() if k in Config.__annotations__})
                return {
                    "config": config,
                    "session_info": create_session_info(),
                    "arrangement": [],
                    "track_states": [create_track_state() for _ in range(config["track_count"])],
                    "playback_metrics": create_playback_metrics(),
                    "feedback": [],  # List[str] — human-readable progress messages
                    "analysis_history": [],  # List[Tuple[int, AudioAnalysisData]]
                    "energy_trend": [],  # List[float]
                    "adaptations": [],  # List[Adaptation]
                    "errors": [],
                    "complete": False,
                    "current_section_index": 0,
                    "audio_snapshot": None,
                    "client": None,
                }

            def configure(self, context):
                self._state = self._init_state(context.get("config", {}))
                return {"state_update": self._configure(self._state)}

            def setup_session(self, context):
                return {"state_update": self._setup_session(self._state)}

            def generate_clips(self, context):
                return {"state_update": self._generate_clips(self._state)}

            def construct_arrangement(self, context):
                return {"state_update": self._construct_arrangement(self._state)}

            def execute_section_loop(self, context):
                arrangement = self._state.get("arrangement", [])
                if not arrangement:
                    return {"error": "No arrangement defined"}
                errors = []
                total = len(arrangement)
                for i, section in enumerate(arrangement):
                    self._state["current_section_index"] = i
                    name = section.get("name", "?")
                    logger.info("[dag] section %d/%d: %s", i + 1, total, name)
                    try:
                        self._execute_section(self._state)
                        self._analyze_section(self._state)
                    except Exception as e:
                        errors.append(f"section {i} ({name}): {e}")
                        logger.warning("Section %d (%s) error: %s", i, name, e)
                self._state["complete"] = True
                return {"state_update": self._state, "errors": errors, "sections": total}

            def analyze_and_adapt(self, context):
                self._analyze_and_adapt(self._state)
                return {
                    "state_update": self._state,
                    "feedback": self._state.get("feedback", []),
                    "metrics": self._state.get("playback_metrics", {}),
                    "complete": self._state.get("complete", False),
                    "errors": self._state.get("errors", []),
                }

        return MixHandler()


# -- Self-check ---------------------------------------------------------------

class _FakeHandler:
    """Records call order; returns canned results."""

    def __init__(self):
        self.calls = []

    def configure(self, ctx):
        self.calls.append("configure")
        return {"ok": True}

    def setup_session(self, ctx):
        self.calls.append("setup_session")
        return {"ok": True}

    def generate_clips(self, ctx):
        self.calls.append("generate_clips")
        return {"clips": 8}

    def construct_arrangement(self, ctx):
        self.calls.append("construct_arrangement")
        return {"sections": 5}

    def execute_section_loop(self, ctx):
        self.calls.append("execute_section_loop")
        return {"sections_played": 5}

    def analyze_and_adapt(self, ctx):
        self.calls.append("analyze_and_adapt")
        return {"feedback": ["all good"], "metrics": {"sections": 5}}


def _self_check():
    """Runnable check: happy path, runner API, critical-failure stop, DAG validation."""
    # Happy path: all 6 tasks run in dependency order
    handler = _FakeHandler()
    outcome = DAGExecutionEngine(MIX_WORKFLOW).run(handler, context={"config": {}})
    assert outcome["status"] == "completed", outcome
    assert handler.calls == [
        "configure", "setup_session", "generate_clips",
        "construct_arrangement", "execute_section_loop", "analyze_and_adapt",
    ], handler.calls

    # Runner API extracts feedback/metrics from the adapt task
    result = AgentFlowRunner().run({"tempo": 126}, handler=_FakeHandler(), timeout=60)
    assert result["status"] == "completed", result
    assert result["feedback"] == ["all good"], result
    assert result["metrics"] == {"sections": 5}, result
    assert result["errors"] == [], result

    # Failure path: critical task fails -> workflow stops, later tasks skipped
    class BoomHandler(_FakeHandler):
        def setup_session(self, ctx):
            self.calls.append("setup_session")
            raise RuntimeError("live down")

    boom = BoomHandler()
    outcome = DAGExecutionEngine(MIX_WORKFLOW).run(boom, context={"config": {}})
    assert outcome["status"] == "failed", outcome
    assert outcome["task_results"].get("configure") == {"ok": True}
    assert "setup-session" not in outcome["task_results"]
    assert "generate-clips" not in outcome["task_results"]
    assert outcome["errors"] and outcome["errors"][0].startswith("setup-session: live down"), outcome["errors"]
    assert boom.calls == ["configure", "setup_session", "setup_session"], boom.calls

    # on_progress fires after every completed task, in order
    progress_log = []
    DAGExecutionEngine(MIX_WORKFLOW).run(
        _FakeHandler(), context={"config": {}},
        on_progress=lambda tid, res, elapsed: progress_log.append(tid),
    )
    assert progress_log == [
        "configure", "setup-session", "generate-clips",
        "construct-arrangement", "execute-section-loop", "analyze-and-adapt",
    ], progress_log

    # Dry-run: full pipeline executes with mocked TCP/UDP/audio, no Live needed
    result = AgentFlowRunner().run(
        {"tempo": 126, "duration_minutes": 5, "genre": "dub_techno",
         "track_count": 4, "key": "Fm", "energy_curve": "gradual",
         "variation_level": 0.5, "section_duration_beats": 4.0},
        timeout=60, dry_run=True,
    )
    assert result["status"] == "completed", result
    assert result["errors"] == [], result
    assert result["sections"] > 0, result

    # DAG validation rejects forward references and duplicate ids
    for bad in (
        (Task("a", "configure", depends_on=("b",)), Task("b", "setup_session")),
        (Task("a", "configure"), Task("a", "setup_session")),
    ):
        try:
            DAGExecutionEngine(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid DAG not rejected: {bad}")

    print("self-check OK (happy path, runner API, progress callback, dry-run, "
          "critical-failure stop, DAG validation)")


# -- CLI entry point ----------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run Ableton mix with in-process AgentFlow-style orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--genre", default="dub_techno",
                        choices=["dub_techno", "house", "techno", "ambient"])
    parser.add_argument("--tempo", type=int, default=126)
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--tracks", type=int, default=8)
    parser.add_argument("--key", default="Fm")
    parser.add_argument("--energy", default="gradual",
                        choices=["gradual", "aggressive", "gentle"])
    parser.add_argument("--variation", type=float, default=0.5)
    parser.add_argument("--section-beats", type=float, default=64.0, dest="section_beats",
                        help="Beats per section (e.g. 16 = 4 bars). Must be shorter "
                             "than the total mix or 0 sections get planned")
    parser.add_argument("--checkpoint", default=None,
                        help="JSON file recording completed tasks (observability)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mock Ableton TCP/UDP responses (no Live needed)")
    parser.add_argument("--self-check", action="store_true",
                        help="Run built-in self-check and exit")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return

    config = {
        "tempo": args.tempo,
        "duration_minutes": args.duration,
        "genre": args.genre,
        "track_count": args.tracks,
        "key": args.key,
        "energy_curve": args.energy,
        "variation_level": args.variation,
        "section_duration_beats": args.section_beats,
    }

    print(f"Starting orchestration: {args.genre} @ {args.tempo}BPM, {args.duration}min"
          + (" [DRY RUN]" if args.dry_run else ""))

    def on_progress(task_id, result, elapsed):
        errors = result.get("errors", []) if isinstance(result, dict) else []
        status = "ok" if not errors else f"{len(errors)} errors"
        print(f"  [{task_id}] {status} ({elapsed:.1f}s)")

    result = AgentFlowRunner(checkpoint_path=args.checkpoint).run(
        config, timeout=args.duration * 60,
        on_progress=on_progress, dry_run=args.dry_run,
    )

    print(f"\nSections played: {result.get('sections', 0)}")
    for err in result.get("errors", []):
        print(f"[ERROR] {err}")
    for msg in result.get("feedback", []):
        print(f"  {msg}")

    if result.get("status") == "completed":
        print("\n[SUCCESS] Mix orchestration complete!")
        sys.exit(0)

    print(f"\n[WARN] Status: {result.get('status')}")
    sys.exit(1)


if __name__ == "__main__":
    main()
