#!/usr/bin/env python3
"""validate_server.py -- Static CI gate for MCP Server tool contracts.

Introspects @mcp.tool() registrations across MCP_Server/*.py and validates:
  1. UDP transport: tools using send_command_udp() only send UDP-whitelisted commands
  2. Command names: every send_command() first arg matches a known command (Remote Script dispatch)
  3. Docstrings: every @mcp.tool() function has a docstring
  4. Normalized params: no float defaults outside 0.0-1.0 for normalized params

Usage:
    python MCP_Server/validate_server.py              # Check against baseline
    python MCP_Server/validate_server.py --baseline   # Generate baseline
    python MCP_Server/validate_server.py --remote      # Also check Remote Script handlers

Exit codes:
    0 -- all checks pass (or only pre-baseline warnings)
    1 -- new violations detected
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

TOOL_FILES = [
    "MCP_Server/server.py",
    "MCP_Server/advanced_tools.py",
    "MCP_Server/arrangement_tools.py",
    "MCP_Server/optimization_tools.py",
    "MCP_Server/fat_beatz_tools.py",
    "MCP_Server/mixer_tools.py",
    "MCP_Server/midi_effects.py",
    "MCP_Server/groove_tools.py",
    "MCP_Server/automation_tools.py",
    "MCP_Server/audio_analysis_tools.py",
    "MCP_Server/server_audio_analysis.py",
    "MCP_Server/arrangement_performance.py",
]

REMOTE_SCRIPT_FILE = "AbletonMCP_Remote_Script/__init__.py"

BASELINE_PATH = Path(__file__).resolve().parent / "validate_baseline.json"

# Canonical UDP whitelist -- the 10 commands from AGENTS.md / command_registry.py
UDP_WHITELIST: Set[str] = {
    "set_device_parameter",
    "set_track_volume",
    "set_track_pan",
    "set_track_mute",
    "set_track_solo",
    "set_track_arm",
    "set_master_volume",
    "set_send_amount",
    "fire_clip",
    "set_clip_launch_mode",
}

# Param names whose float defaults MUST be in [0.0, 1.0].
# Matched as whole underscore-separated words (e.g. "kick_volume" -> ["kick", "volume"]).
NORMALIZED_WORDS: Set[str] = {
    "volume", "vol", "pan", "amount", "value",
    "drive", "saturation", "mix", "wet", "dry",
    "depth", "feedback", "width", "level", "threshold",
    "resonance", "position", "crossfade", "decay",
    "intensity", "presence", "swing",
}

# Substrings that disqualify a param from being "normalized"
# regardless of suffix matches.
NON_NORMALIZED_INDICATORS: List[str] = [
    "ms", "hz", "db", "beats", "bars", "bpm", "tempo",
    "length", "duration", "ratio", "cutoff", "frequency",
    "freq", "percent", "time_span", "density", "boost",
    "index", "count", "rate", "phase", "offset", "time",
    "number", "num", "max_time", "key_input", "per_chord",
    "span", "max_depth", "min_depth",
]

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ToolInfo:
    """Extracted information about a single @mcp.tool() function."""

    name: str
    tool_name: Optional[str]  # explicit name if @mcp.tool("name"), else same as func name
    file: str  # relative path from repo root
    line: int
    has_docstring: bool
    udp_commands: List[str] = field(default_factory=list)  # send_command_udp() command names
    tcp_commands: List[str] = field(default_factory=list)  # send_command() command names
    float_defaults: Dict[str, float] = field(default_factory=dict)  # param -> default


@dataclass
class Violation:
    """A single validation violation."""

    check: str  # "udp_transport", "unknown_command", "missing_docstring", "normalized_param"
    file: str
    function: str
    detail: str

    @property
    def fingerprint(self) -> str:
        return f"{self.check}:{self.file}:{self.function}:{self.detail}"

    def __str__(self) -> str:
        return f"[{self.check}] {self.file}:{self.function} -- {self.detail}"


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _is_tool_decorator(decorator: ast.expr) -> bool:
    """Return True if the decorator is @mcp.tool() or @server.tool() etc."""
    if isinstance(decorator, ast.Call):
        func = decorator.func
        if isinstance(func, ast.Attribute) and func.attr == "tool":
            return True
        if isinstance(func, ast.Name) and func.id == "tool":
            return True
    return False


def _get_explicit_tool_name(decorator: ast.expr) -> Optional[str]:
    """Extract explicit name from @mcp.tool("name") if present."""
    if isinstance(decorator, ast.Call) and decorator.args:
        first_arg = decorator.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            return first_arg.value
    return None


def _find_send_calls(func_node: ast.FunctionDef) -> Tuple[List[str], List[str]]:
    """Walk a function body and collect send_command() / send_command_udp() command names.

    Returns (udp_commands, tcp_commands).
    Only collects DIRECT calls in the function body (not transitive through helpers).
    """
    udp_cmds: List[str] = []
    tcp_cmds: List[str] = []

    for node in ast.walk(func_node):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        method = func.attr
        if method not in ("send_command", "send_command_udp"):
            continue
        # Extract first positional arg (command name)
        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            cmd = node.args[0].value
            if method == "send_command_udp":
                udp_cmds.append(cmd)
            else:
                tcp_cmds.append(cmd)

    return udp_cmds, tcp_cmds


def _find_float_defaults(func_node: ast.FunctionDef) -> Dict[str, float]:
    """Extract all float default values from function parameters."""
    defaults: Dict[str, float] = {}

    # Regular args + posonlyargs
    all_args = list(func_node.args.posonlyargs) + list(func_node.args.args) + list(func_node.args.kwonlyargs)
    num_defaults = len(func_node.args.defaults)
    num_kw_defaults = len(func_node.args.kw_defaults)

    # Positional defaults align from the right
    regular_args = list(func_node.args.posonlyargs) + list(func_node.args.args)
    defaults_start = len(regular_args) - num_defaults
    for i, default in enumerate(func_node.args.defaults):
        arg_idx = defaults_start + i
        if arg_idx < len(regular_args):
            arg = regular_args[arg_idx]
            if isinstance(default, ast.Constant) and isinstance(default.value, (int, float)):
                defaults[arg.arg] = float(default.value)

    # Keyword-only defaults
    for i, default in enumerate(func_node.args.kw_defaults):
        if default is None:
            continue
        arg_idx = i
        if arg_idx < len(func_node.args.kwonlyargs):
            arg = func_node.args.kwonlyargs[arg_idx]
            if isinstance(default, ast.Constant) and isinstance(default.value, (int, float)):
                defaults[arg.arg] = float(default.value)

    return defaults


def is_normalized_param(name: str) -> bool:
    """Heuristic: does this param name represent a 0.0-1.0 normalized Ableton parameter?

    Uses word-boundary matching (underscore-split parts) to avoid false positives
    like 'pitch_span' matching 'pan' or 'feedback' matching 'db'.
    """
    lower = name.lower().strip()
    if not lower:
        return False
    parts = lower.split("_")
    # Must contain at least one underscore-separated word that is a normalized indicator
    has_normalized = any(part in NORMALIZED_WORDS for part in parts)
    if not has_normalized:
        return False
    # Must NOT contain any non-normalized indicator
    # Short indicators checked as whole words; compound ones (with _) as substrings
    for ind in NON_NORMALIZED_INDICATORS:
        if "_" in ind:
            if ind in lower:
                return False
        else:
            if ind in parts:
                return False
    return True


def _parse_registry_commands(path: Path) -> Set[str]:
    """Extract command names from command_registry.py via AST parsing.

    Matches _register(CommandSpec(name="cmd_name", ...)) calls.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    commands: Set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # Look for: _register(CommandSpec(name="...", ...))
        if not (isinstance(node.func, ast.Name) and node.func.id == "_register"):
            continue
        if not node.args:
            continue
        # First arg should be CommandSpec(...) call
        spec_call = node.args[0]
        if not isinstance(spec_call, ast.Call):
            continue
        # Extract keyword arg: name="..."
        for kw in spec_call.keywords:
            if kw.arg == "name" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                commands.add(kw.value.value)

    return commands


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse_tools(filepath: str) -> List[ToolInfo]:
    """Parse @mcp.tool() decorated functions from a Python source file."""
    full_path = REPO_ROOT / filepath
    if not full_path.exists():
        return []

    source = full_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(full_path))
    except SyntaxError as e:
        print(f"  WARNING: Cannot parse {filepath}: {e}", file=sys.stderr)
        return []

    tools: List[ToolInfo] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Check for @mcp.tool() or @mcp.tool("name") decorator
        tool_decorator = None
        for dec in node.decorator_list:
            if _is_tool_decorator(dec):
                tool_decorator = dec
                break
        if tool_decorator is None:
            continue

        explicit_name = _get_explicit_tool_name(tool_decorator)
        tool_name = explicit_name if explicit_name else node.name

        # Skip 'ctx' param for default checking
        has_docstring = (
            ast.get_docstring(node) is not None
            and ast.get_docstring(node).strip() != ""
        )

        udp_cmds, tcp_cmds = _find_send_calls(node)
        float_defaults = _find_float_defaults(node)

        tools.append(ToolInfo(
            name=node.name,
            tool_name=tool_name,
            file=filepath,
            line=node.lineno,
            has_docstring=has_docstring,
            udp_commands=udp_cmds,
            tcp_commands=tcp_cmds,
            float_defaults=float_defaults,
        ))

    return tools


def parse_remote_script_dispatch(filepath: str) -> Set[str]:
    """Extract all handled command names from the Remote Script dispatch table.

    Matches patterns like:
        if command_type == "create_midi_track":
        elif command_type == "set_tempo":
    """
    full_path = REPO_ROOT / filepath
    if not full_path.exists():
        print(f"  WARNING: Remote Script not found at {filepath}", file=sys.stderr)
        return set()

    source = full_path.read_text(encoding="utf-8")

    # Match: command_type == "..." patterns
    pattern = re.compile(r'command_type\s*==\s*"([^"]+)"')
    commands = set(pattern.findall(source))

    # Also match: command_type in ["cmd1", "cmd2"] patterns
    in_pattern = re.compile(r'command_type\s+in\s*\[([^\]]+)\]')
    for match in in_pattern.finditer(source):
        bracket_content = match.group(1)
        inner_cmds = re.findall(r'"([^"]+)"', bracket_content)
        commands.update(inner_cmds)

    return commands


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_udp_transport(tools: List[ToolInfo]) -> List[Violation]:
    """Check 1: every send_command_udp() call uses a UDP-whitelisted command."""
    violations: List[Violation] = []
    for tool in tools:
        for cmd in tool.udp_commands:
            if cmd not in UDP_WHITELIST:
                violations.append(Violation(
                    check="udp_transport",
                    file=tool.file,
                    function=tool.name,
                    detail=f"send_command_udp('{cmd}') -- not in UDP whitelist",
                ))
    return violations


def check_command_names(tools: List[ToolInfo], known_commands: Set[str]) -> List[Violation]:
    """Check 2: every send_command() first arg matches a known command."""
    violations: List[Violation] = []
    for tool in tools:
        for cmd in tool.tcp_commands + tool.udp_commands:
            if cmd not in known_commands:
                violations.append(Violation(
                    check="unknown_command",
                    file=tool.file,
                    function=tool.name,
                    detail=f"send_command('{cmd}') -- no handler in Remote Script dispatch",
                ))
    return violations


def check_docstrings(tools: List[ToolInfo]) -> List[Violation]:
    """Check 3: every @mcp.tool() function has a docstring."""
    violations: List[Violation] = []
    for tool in tools:
        if not tool.has_docstring:
            violations.append(Violation(
                check="missing_docstring",
                file=tool.file,
                function=tool.name,
                detail="tool function has no docstring",
            ))
    return violations


def check_normalized_params(tools: List[ToolInfo]) -> List[Violation]:
    """Check 4: no normalized param has a float default outside [0.0, 1.0]."""
    violations: List[Violation] = []
    for tool in tools:
        for param_name, default_val in tool.float_defaults.items():
            if param_name == "ctx":
                continue
            if is_normalized_param(param_name):
                if not (0.0 <= default_val <= 1.0):
                    violations.append(Violation(
                        check="normalized_param",
                        file=tool.file,
                        function=tool.name,
                        detail=f"param '{param_name}' default={default_val} outside [0.0, 1.0]",
                    ))
    return violations


def check_remote_handlers(
    tools: List[ToolInfo],
    remote_commands: Set[str],
) -> List[Violation]:
    """--remote check: every command sent by tools has a handler in the Remote Script."""
    # This is essentially the same as check_command_names but explicit
    return check_command_names(tools, remote_commands)


def check_registry_vs_remote(
    registry_commands: Set[str],
    remote_commands: Set[str],
) -> List[Violation]:
    """--remote check: every command in the registry has a Remote Script handler."""
    violations: List[Violation] = []
    for cmd in sorted(registry_commands):
        if cmd not in remote_commands:
            violations.append(Violation(
                check="missing_remote_handler",
                file="command_registry.py",
                function="(registry)",
                detail=f"command '{cmd}' has no handler in Remote Script dispatch",
            ))
    return violations


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------


def load_baseline(path: Path) -> Set[str]:
    """Load baseline violation fingerprints from JSON file."""
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("violations", []))
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  WARNING: Cannot parse baseline {path}: {e}", file=sys.stderr)
        return set()


def write_baseline(path: Path, violations: List[Violation]) -> None:
    """Write baseline violation fingerprints to JSON file."""
    data = {
        "description": "Pre-existing violations recorded for CI baseline comparison.",
        "generated_by": "MCP_Server/validate_server.py --baseline",
        "violation_count": len(violations),
        "violations": sorted(v.fingerprint for v in violations),
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Static CI gate for MCP Server tool contracts."
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Generate validate_baseline.json with current violations (exit 0)",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Also validate Remote Script dispatch table coverage",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show per-tool details",
    )
    args = parser.parse_args()

    # ── Parse tool files ────────────────────────────────────────────────
    all_tools: List[ToolInfo] = []
    for filepath in TOOL_FILES:
        tools = parse_tools(filepath)
        if tools and args.verbose:
            print(f"  {filepath}: {len(tools)} tools")
        all_tools.extend(tools)

    print(f"Scanned {len(all_tools)} @mcp.tool() registrations "
          f"across {len(TOOL_FILES)} files")

    # ── Parse Remote Script dispatch table ──────────────────────────────
    remote_commands = parse_remote_script_dispatch(REMOTE_SCRIPT_FILE)
    if remote_commands:
        print(f"Remote Script dispatch: {len(remote_commands)} command handlers")

    # ── Run checks ───────────────────────────────────────────────────────
    violations: List[Violation] = []

    violations.extend(check_udp_transport(all_tools))
    violations.extend(check_command_names(all_tools, remote_commands))
    violations.extend(check_docstrings(all_tools))
    violations.extend(check_normalized_params(all_tools))

    if args.remote:
        # Check registry commands have Remote Script handlers
        try:
            registry_cmds = _parse_registry_commands(
                REPO_ROOT / "MCP_Server" / "command_registry.py"
            )
            violations.extend(check_registry_vs_remote(registry_cmds, remote_commands))
        except Exception as e:
            print(f"  WARNING: Cannot parse command_registry.py for --remote check: {e}",
                  file=sys.stderr)

    # ── Handle baseline ──────────────────────────────────────────────────
    if args.baseline:
        write_baseline(BASELINE_PATH, violations)
        if violations:
            print(f"\nBaseline written to {BASELINE_PATH.name} "
                  f"with {len(violations)} pre-existing violations:")
            for v in sorted(violations, key=lambda v: v.fingerprint):
                print(f"  WARN {v}")
        else:
            print(f"\nBaseline written to {BASELINE_PATH.name} -- no violations!")
        sys.exit(0)

    # ── Compare against baseline ──────────────────────────────────────────
    baseline_fingerprints = load_baseline(BASELINE_PATH)

    if not BASELINE_PATH.exists():
        # No baseline yet -- this is first run, treat all as errors
        # (user should run --baseline first)
        new_violations = violations
        old_violations: List[Violation] = []
    else:
        new_violations = [v for v in violations if v.fingerprint not in baseline_fingerprints]
        old_violations = [v for v in violations if v.fingerprint in baseline_fingerprints]

    # ── Report ───────────────────────────────────────────────────────────
    if new_violations:
        print(f"\nERRORS NEW VIOLATIONS ({len(new_violations)}):")
        for v in sorted(new_violations, key=lambda v: v.fingerprint):
            print(f"  FAIL {v}")

    if old_violations:
        print(f"\nWARN  PRE-EXISTING ({len(old_violations)} -- see baseline):")
        for v in sorted(old_violations, key=lambda v: v.fingerprint):
            print(f"  WARN {v}")

    if not violations:
        print(f"\nOK All {len(all_tools)} tools passed validation!")
    elif not new_violations:
        print(f"\nOK All checks pass ({len(old_violations)} pre-existing warnings in baseline)")
    else:
        # Fixed violations that were in baseline but no longer present
        fixed = baseline_fingerprints - {v.fingerprint for v in violations}
        if fixed:
            print(f"\nFIXED FIXED ({len(fixed)} -- previously in baseline):")
            for fp in sorted(fixed):
                print(f"  FIXED {fp}")

    sys.exit(1 if new_violations else 0)


if __name__ == "__main__":
    main()
