"""
AgentFlow Python Runner

Starts the Node.js AgentFlow bridge and the Python agent HTTP server,
then submits the mix workflow for orchestration.

Usage:
    from orchestration.agentflow_runner import AgentFlowRunner
    runner = AgentFlowRunner()
    result = runner.run(config_dict)

Or from CLI:
    python -m orchestration.agentflow_runner --genre dub_techno --tempo 126 --duration 120
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

BRIDGE_DIR = os.path.join(os.path.dirname(__file__), "agentflow_bridge")
DEFAULT_BRIDGE_PORT = 7420
DEFAULT_AGENT_PORT = 7421


class AgentFlowRunner:
    """
    Manages the AgentFlow orchestration bridge and Python agent server.

    1. Starts the Node.js AgentFlow bridge (DAG engine + circuit breakers)
    2. Starts a lightweight Python HTTP server that handles agent tasks
    3. Submits the mix workflow to the bridge
    4. Polls for completion and returns results
    """

    def __init__(
        self,
        bridge_port: int = DEFAULT_BRIDGE_PORT,
        agent_port: int = DEFAULT_AGENT_PORT,
    ):
        self.bridge_port = bridge_port
        self.agent_port = agent_port
        self._bridge_process: Optional[subprocess.Popen] = None
        self._agent_process: Optional[subprocess.Popen] = None
        self._workflow_context: Dict[str, Any] = {}
        self._task_results: Dict[str, Dict[str, Any]] = {}

    def start_bridge(self) -> None:
        """Start the Node.js AgentFlow bridge."""
        npm = os.path.join(BRIDGE_DIR, "node_modules", ".bin", "npm")
        if not os.path.exists(npm):
            npm = "npm"

        logger.info(f"Starting AgentFlow bridge on port {self.bridge_port}")
        self._bridge_process = subprocess.Popen(
            [npm, "start"],
            cwd=BRIDGE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={**os.environ, "AGENTFLOW_PORT": str(self.bridge_port), "AGENT_PORT": str(self.agent_port)},
        )

        # Wait for the bridge to be ready
        self._wait_for_ready(f"http://127.0.0.1:{self.bridge_port}/health")

    def stop_bridge(self) -> None:
        """Stop the Node.js bridge."""
        if self._bridge_process:
            self._bridge_process.terminate()
            try:
                self._bridge_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._bridge_process.kill()
            self._bridge_process = None
            logger.info("AgentFlow bridge stopped")

    def start_agent_server(self, handler: Any) -> None:
        """Start the Python HTTP agent server with the given task handler.

        Args:
            handler: An object with methods matching task actions:
                - configure(context) -> dict
                - setup_session(context) -> dict
                - generate_clips(context) -> dict
                - construct_arrangement(context) -> dict
                - execute_section_loop(context) -> dict
                - analyze_and_adapt(context) -> dict
        """
        self._handler = handler
        # Import and start the agent server in a thread
        import threading

        def run_server():
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import json

            class AgentHandler(BaseHTTPRequestHandler):
                """HTTP handler that dispatches AgentFlow task invocations."""

                def do_POST(self):
                    content_length = int(self.headers.get("Content-Length", 0))
                    if content_length > 0:
                        body = self.rfile.read(content_length)
                        data = json.loads(body) if body else {}
                    else:
                        data = {}

                    task_id = data.get("taskId", "unknown")
                    action = data.get("action", "")
                    context = data.get("context", {})

                    try:
                        # Dispatch to handler method
                        if hasattr(handler, action):
                            func = getattr(handler, action)
                            result = func(context)
                        else:
                            logger.warning(f"No handler for action: {action}")
                            result = {"error": f"Unknown action: {action}"}

                        # Store result for next task
                        self._task_results = getattr(self, "_task_results", {})
                        self._task_results[task_id] = result
                        result["taskId"] = task_id

                        response = json.dumps(result).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(response)))
                        self.end_headers()
                        self.wfile.write(response)

                    except Exception as e:
                        logger.error(f"Task {task_id} ({action}) failed: {e}")
                        response = json.dumps({
                            "error": str(e), "taskId": task_id, "action": action
                        }).encode("utf-8")
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(response)))
                        self.end_headers()
                        self.wfile.write(response)

                def do_GET(self):
                    if self.path == "/health":
                        response = json.dumps({"status": "ok", "python": "ready"}).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(response)))
                        self.end_headers()
                        self.wfile.write(response)
                    else:
                        self.send_response(404)
                        self.end_headers()

            # Set _task_results as a class attribute for the handler to access
            AgentHandler._task_results = self._task_results

            self._agent_server = HTTPServer(("127.0.0.1", self.agent_port), AgentHandler)
            logger.info(f"Python agent server on port {self.agent_port}")
            self._agent_server.serve_forever()

        self._agent_thread = threading.Thread(target=run_server, daemon=True)
        self._agent_thread.start()

    def stop_agent_server(self) -> None:
        """Stop the Python agent server."""
        if hasattr(self, "_agent_server") and self._agent_server:
            self._agent_server.shutdown()
            logger.info("Python agent server stopped")

    def submit_workflow(self, config: Dict[str, Any]) -> str:
        """
        Submit a mix workflow to the AgentFlow bridge.

        Args:
            config: Workflow configuration (tempo, genre, duration, etc.)

        Returns:
            Execution ID
        """
        import json
        import urllib.request

        url = f"http://127.0.0.1:{self.bridge_port}/workflow/start"
        data = json.dumps(config).encode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            logger.info(f"Workflow submitted: executionId={result['executionId']}")
            return result["executionId"]

    def poll_status(self, execution_id: str, poll_interval: float = 3.0, timeout: float = 7200) -> Dict[str, Any]:
        """
        Poll the bridge until the workflow completes.

        Args:
            execution_id: Workflow execution ID
            poll_interval: Seconds between polls
            timeout: Max wait time in seconds

        Returns:
            Final execution dict with status, results, context
        """
        import json
        import urllib.request

        start = time.time()

        while time.time() - start < timeout:
            try:
                url = f"http://127.0.0.1:{self.bridge_port}/workflow/{execution_id}/status"
                with urllib.request.urlopen(url, timeout=5) as resp:
                    status = json.loads(resp.read().decode("utf-8"))

                if status["status"] in ("completed", "failed", "cancelled"):
                    return status

                time.sleep(poll_interval)
            except Exception as e:
                logger.debug(f"Poll error (retrying): {e}")
                time.sleep(poll_interval)

        raise TimeoutError(f"Workflow {execution_id} timed out after {timeout}s")

    def run(
        self,
        config: Dict[str, Any],
        handler: Any = None,
        poll_interval: float = 3.0,
        timeout: float = 7200,
    ) -> Dict[str, Any]:
        """
        Full orchestration: start bridge + agent server, submit workflow, wait.

        Args:
            config: Workflow configuration
            handler: Python task handler (defaults to importing agentic_mix nodes)
            poll_interval: Seconds between status polls
            timeout: Max wait time in seconds

        Returns:
            Dict with status, results, context, error (if any)
        """
        try:
            # Import default handler if none provided
            if handler is None:
                handler = self._default_handler()

            # Start services
            self.start_agent_server(handler)
            self.start_bridge()

            # Submit workflow
            execution_id = self.submit_workflow(config)

            # Wait for completion
            result = self.poll_status(execution_id, poll_interval, timeout)
            return result

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            self.stop_bridge()
            self.stop_agent_server()

    def _default_handler(self) -> Any:
        """Create a handler from the existing agentic_mix node functions."""
        from agentic_mix.state import GraphState, create_session_info, create_track_state, create_playback_metrics, Config

        class MixHandler:
            """Wraps existing agentic_mix nodes as an AgentFlow task handler."""

            def __init__(self):
                from agentic_mix.nodes.configure import configure_node
                from agentic_mix.nodes.setup_session import setup_session_node
                from agentic_mix.nodes.generate_clips import generate_clips_node
                from agentic_mix.nodes.construct_arrangement import construct_arrangement_node
                from agentic_mix.nodes.execute_section import execute_section_node
                from agentic_mix.nodes.analyze_section import analyze_section_node
                from agentic_mix.nodes.analyze_adapt import analyze_and_adapt_node
                self._configure = configure_node
                self._setup_session = setup_session_node
                self._generate_clips = generate_clips_node
                self._construct_arrangement = construct_arrangement_node
                self._execute_section = execute_section_node
                self._analyze_section = analyze_section_node
                self._analyze_and_adapt = analyze_and_adapt_node
                # State passed between calls
                self._state = None

            def _init_state(self, config_dict: Dict[str, Any]) -> GraphState:
                """Create initial GraphState from config dict."""
                config = Config(**{k: v for k, v in config_dict.items() if k in Config.__annotations__})
                return {
                    "config": config,
                    "session_info": create_session_info(),
                    "arrangement": [],
                    "track_states": [create_track_state() for _ in range(config["track_count"])],
                    "playback_metrics": create_playback_metrics(),
                    "feedback": {"history": [], "adaptations": [], "energy_trend": []},
                    "errors": [],
                    "complete": False,
                    "current_section_index": 0,
                    "audio_snapshot": None,
                    "client": None,
                }

            def configure(self, context: Dict[str, Any]) -> Dict[str, Any]:
                self._state = self._init_state(context.get("config", {}))
                result = self._configure(self._state)
                return {"state_update": result}

            def setup_session(self, context: Dict[str, Any]) -> Dict[str, Any]:
                result = self._setup_session(self._state)
                return {"state_update": result}

            def generate_clips(self, context: Dict[str, Any]) -> Dict[str, Any]:
                result = self._generate_clips(self._state)
                return {"state_update": result}

            def construct_arrangement(self, context: Dict[str, Any]) -> Dict[str, Any]:
                result = self._construct_arrangement(self._state)
                return {"state_update": result}

            def execute_section_loop(self, context: Dict[str, Any]) -> Dict[str, Any]:
                # Execute sections in a loop until done
                arrangement = self._state.get("arrangement", [])
                if not arrangement:
                    return {"error": "No arrangement defined"}

                errors = []
                for i, section in enumerate(arrangement):
                    self._state["current_section_index"] = i
                    try:
                        self._execute_section(self._state)
                        self._analyze_section(self._state)
                    except Exception as e:
                        errors.append(str(e))
                        logger.warning(f"Section {i} ({section.get('name', '?')}) error: {e}")

                self._state["complete"] = True
                return {"state_update": self._state, "errors": errors}

            def analyze_and_adapt(self, context: Dict[str, Any]) -> Dict[str, Any]:
                self._analyze_and_adapt(self._state)
                return {
                    "state_update": self._state,
                    "feedback": self._state.get("feedback", []),
                    "metrics": self._state.get("playback_metrics", {}),
                    "complete": self._state.get("complete", False),
                    "errors": self._state.get("errors", []),
                }

        return MixHandler()

    def _wait_for_ready(self, url: str, timeout: float = 30.0) -> None:
        """Wait for the bridge to be ready."""
        import json
        import urllib.request

        start = time.time()
        while time.time() - start < timeout:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("status") == "ok":
                        logger.info("AgentFlow bridge ready")
                        return
            except Exception:
                pass
            time.sleep(1)

        raise TimeoutError(
            f"AgentFlow bridge not ready after {timeout}s at {url}"
        )


# ── CLI entry point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run Ableton mix with AgentFlow orchestration",
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
    parser.add_argument("--bridge-port", type=int, default=DEFAULT_BRIDGE_PORT)
    parser.add_argument("--agent-port", type=int, default=DEFAULT_AGENT_PORT)
    parser.add_argument("--check", action="store_true",
                       help="Check if AgentFlow bridge is running")
    args = parser.parse_args()

    # Quick health check mode
    if args.check:
        import json
        import urllib.request
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{args.bridge_port}/health", timeout=3
            ) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(json.dumps(data, indent=2))
        except Exception:
            print(json.dumps({"status": "not running"}))
        return

    runner = AgentFlowRunner(
        bridge_port=args.bridge_port,
        agent_port=args.agent_port,
    )

    config = {
        "tempo": args.tempo,
        "duration_minutes": args.duration,
        "genre": args.genre,
        "track_count": args.tracks,
        "key": args.key,
        "energy_curve": args.energy,
        "variation_level": args.variation,
    }

    print(f"Starting AgentFlow orchestration: {args.genre} @ {args.tempo}BPM, {args.duration}min")
    print(f"Bridge: http://127.0.0.1:{args.bridge_port}")
    print(f"Agent server: http://127.0.0.1:{args.agent_port}")

    result = runner.run(config, timeout=args.duration * 60)

    if result.get("error"):
        print(f"\n[ERROR] {result['error']}")
        sys.exit(1)

    if result.get("status") == "completed":
        print(f"\n[SUCCESS] Mix orchestration complete!")
        if result.get("errors"):
            print(f"[WARN] {len(result['errors'])} section errors")
    else:
        print(f"\n[WARN] Status: {result.get('status')}")

    feedback = result.get("feedback", [])
    for msg in feedback:
        print(f"  {msg}")


if __name__ == "__main__":
    main()
