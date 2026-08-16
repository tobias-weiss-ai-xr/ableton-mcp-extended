#!/usr/bin/env python3
"""
Autogenerate tool documentation from MCP tool decorators and command registry.

This script introspects:
1. All @mcp.tool() decorated functions across MCP_Server/*.py
2. The command registry (command_registry.py) for transport info

Generates:
- docs/TOOLS.md: Full inventory with name, transport, category, description, params
- docs/QUICK_REFERENCE.md: Compact cheatsheet grouped by category

Usage:
    python MCP_Server/docgen.py
    python MCP_Server/docgen.py --check  # Verify idempotency (exit non-zero if diff)
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Root directory
ROOT_DIR = Path(__file__).parent.parent
MCP_SERVER_DIR = ROOT_DIR / "MCP_Server"
DOCS_DIR = ROOT_DIR / "docs"

# UDP commands from AGENTS.md - these are the ONLY commands that use UDP
UDP_COMMANDS = {
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


def get_mcp_server_files() -> List[Path]:
    """Get all Python files in MCP_Server directory."""
    files = []
    for f in sorted(MCP_SERVER_DIR.glob("*.py")):
        if f.name.startswith("_") or f.name == "__init__.py" or f.name == "docgen.py":
            continue
        files.append(f)
    return files


def extract_tools_from_file(filepath: Path) -> List[Dict[str, Any]]:
    """Extract tool definitions from a Python file using AST parsing."""
    tools = []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Find all function definitions with @mcp.tool or @server.tool decorator
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for decorators
                for decorator in node.decorator_list:
                    # Handle @mcp.tool() or @mcp.tool("name")
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr == "tool":
                                tool_name = node.name
                                # Extract explicit tool name if provided
                                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                    tool_name = decorator.args[0].value
                                
                                # Extract docstring
                                docstring = ast.get_docstring(node) or ""
                                
                                # Extract parameters from function signature (skip 'ctx' and 'self')
                                params = []
                                
                                # Process positional-only args
                                for arg in node.args.posonlyargs:
                                    if arg.arg in ('ctx', 'self'):
                                        continue
                                    params.append(extract_param_info(arg, node.args, 'posonly'))
                                
                                # Process positional args
                                for arg in node.args.args:
                                    if arg.arg in ('ctx', 'self'):
                                        continue
                                    params.append(extract_param_info(arg, node.args, 'args'))
                                
                                # Process keyword-only args
                                if hasattr(node.args, 'kw_onlyargs'):
                                    for arg in node.args.kw_onlyargs:
                                        if arg.arg in ('ctx', 'self'):
                                            continue
                                        params.append(extract_param_info(arg, node.args, 'kw_only'))
                                
                                # Process kwarg
                                if node.args.kwarg and node.args.kwarg.arg not in ('ctx', 'self'):
                                    params.append({
                                        "name": node.args.kwarg.arg,
                                        "type": "dict",
                                        "default": None,
                                        "description": "Keyword arguments"
                                    })
                                
                                tools.append({
                                    "name": tool_name,
                                    "function_name": node.name,
                                    "docstring": docstring.strip(),
                                    "params": params,
                                    "file": filepath.name,
                                    "line": node.lineno,
                                })
                                break
    except Exception as e:
        print(f"Warning: Error parsing {filepath}: {e}")
        import traceback
        traceback.print_exc()
    
    return tools


def extract_param_info(arg: ast.arg, args: ast.arguments, arg_type: str) -> Dict[str, Any]:
    """Extract parameter information from AST arg node."""
    param_info = {
        "name": arg.arg,
        "type": "Any",
        "default": None,
        "description": ""
    }
    
    return param_info


def get_command_transport(tool_name: str) -> str:
    """Get transport (tcp/udp) for a command."""
    if tool_name in UDP_COMMANDS:
        return "udp"
    return "tcp"


def categorize_tool(tool_name: str, docstring: str) -> str:
    """Categorize a tool based on its name and docstring."""
    tool_lower = tool_name.lower()
    doc_lower = docstring.lower()
    
    # Check in order of priority
    
    # 1. UDP commands
    if tool_name in UDP_COMMANDS:
        return "udp"
    
    # 2. Session setup
    if any(kw in tool_lower for kw in ["track", "scene", "clip", "session"]) and \
       any(kw in tool_lower for kw in ["create", "delete", "duplicate", "set_"]):
        return "session-setup"
    
    # 3. Arrangement
    if any(kw in tool_lower for kw in ["arrangement", "capture", "record", "locator", "automation"]):
        return "arrangement"
    
    # 4. Mixing
    if any(kw in tool_lower for kw in ["mix", "volume", "pan", "mute", "solo", 
                                         "send", "crossfader", "meter", "level"]):
        return "mixing"
    
    # 5. Effects
    if any(kw in tool_lower for kw in ["effect", "device", "reverb", "delay", 
                                         "eq", "compressor", "filter", "load_"]):
        return "effects"
    
    # 6. MIDI
    if any(kw in tool_lower for kw in ["midi", "note", "chord", "scale", 
                                         "arpeggiator", "quantize"]):
        return "midi"
    
    # 7. Generation
    if any(kw in tool_lower for kw in ["generate", "create_", "build", "pattern", 
                                         "groove", "drum", "bass", "melodic"]):
        return "generation"
    
    # 8. Optimization
    if any(kw in tool_lower for kw in ["optimize", "polish", "balance", "analysis"]):
        return "optimization"
    
    # 9. Dub specific
    if "dub" in tool_lower or "fat_beatz" in tool_lower or "fat_beats" in tool_lower:
        return "dub"
    
    # 10. Performance
    if any(kw in tool_lower for kw in ["performance", "live", "dj"]):
        return "performance"
    
    # 11. Advanced
    if any(kw in tool_lower for kw in ["advanced", "smart", "intelligent", "ai"]):
        return "advanced"
    
    # Default
    return "other"


def get_tool_description(tool_name: str, docstring: str) -> str:
    """Get a clean description for a tool."""
    if docstring:
        lines = docstring.split("\n")
        first_line = lines[0].strip()
        # Remove backticks and formatting
        first_line = first_line.replace("`", "").replace("*", "")
        return first_line
    return tool_name


def generate_tools_md(tools: List[Dict[str, Any]]) -> str:
    """Generate the full TOOLS.md document."""
    lines = []
    
    # Header
    lines.append("# AUTOGENERATED — do not edit by hand")
    lines.append("")
    lines.append("# Ableton MCP Extended — Tool Inventory")
    lines.append("")
    lines.append("This file is autogenerated from MCP tool decorators and the command registry.")
    lines.append("For changes, edit the source Python files or command_registry.py, then run `python MCP_Server/docgen.py`.")
    lines.append("")
    
    # Statistics
    udp_count = sum(1 for t in tools if get_command_transport(t["name"]) == "udp")
    tcp_count = len(tools) - udp_count
    categories = {}
    for t in tools:
        cat = categorize_tool(t["name"], t["docstring"])
        categories[cat] = categories.get(cat, 0) + 1
    
    lines.append("## Statistics")
    lines.append("")
    lines.append(f"- **Total Tools**: {len(tools)}")
    lines.append(f"- **TCP Transport**: {tcp_count}")
    lines.append(f"- **UDP Transport**: {udp_count}")
    lines.append(f"- **Categories**: {len(categories)}")
    lines.append("")
    lines.append("### Tools by Category")
    lines.append("")
    for cat, count in sorted(categories.items()):
        lines.append(f"- **{cat}**: {count}")
    lines.append("")
    
    # UDP Commands Section
    udp_tools = [t for t in tools if get_command_transport(t["name"]) == "udp"]
    if udp_tools:
        lines.append("## UDP Commands (Fire-and-Forget)")
        lines.append("")
        lines.append("These commands use UDP transport for low-latency, fire-and-forget operations.")
        lines.append("")
        lines.append("| Name | Category | Description | File |")
        lines.append("|------|----------|-------------|------|")
        for tool in sorted(udp_tools, key=lambda t: t["name"]):
            desc = get_tool_description(tool["name"], tool["docstring"])
            cat = categorize_tool(tool["name"], tool["docstring"])
            lines.append(f"| `{tool['name']}` | {cat} | {desc} | `{tool['file']}` |")
        lines.append("")
    
    # TCP Commands Section
    tcp_tools = [t for t in tools if get_command_transport(t["name"]) == "tcp"]
    if tcp_tools:
        lines.append("## TCP Commands (Request/Response)")
        lines.append("")
        lines.append("These commands use TCP transport for reliable, request/response operations.")
        lines.append("")
        lines.append("| Name | Category | Description | File |")
        lines.append("|------|----------|-------------|------|")
        for tool in sorted(tcp_tools, key=lambda t: t["name"]):
            desc = get_tool_description(tool["name"], tool["docstring"])
            cat = categorize_tool(tool["name"], tool["docstring"])
            lines.append(f"| `{tool['name']}` | {cat} | {desc} | `{tool['file']}` |")
        lines.append("")
    
    # All Tools by Name
    lines.append("## Tool Index (Alphabetical)")
    lines.append("")
    lines.append("| Name | Transport | Category | File |")
    lines.append("|------|-----------|----------|------|")
    for tool in sorted(tools, key=lambda t: t["name"]):
        transport = get_command_transport(tool["name"])
        cat = categorize_tool(tool["name"], tool["docstring"])
        lines.append(f"| `{tool['name']}` | {transport} | {cat} | `{tool['file']}` |")
    lines.append("")
    
    # Detailed Tool Reference
    lines.append("## Detailed Tool Reference")
    lines.append("")
    
    # Group by category
    category_groups = {}
    for tool in tools:
        cat = categorize_tool(tool["name"], tool["docstring"])
        if cat not in category_groups:
            category_groups[cat] = []
        category_groups[cat].append(tool)
    
    for category in sorted(category_groups.keys()):
        category_tools = category_groups[category]
        
        lines.append(f"### {category}")
        lines.append("")
        
        for tool in sorted(category_tools, key=lambda t: t["name"]):
            lines.append(f"#### `{tool['name']}`")
            lines.append("")
            transport = get_command_transport(tool["name"])
            lines.append(f"- **Transport**: `{transport}`")
            lines.append(f"- **File**: `{tool['file']}`")
            desc = get_tool_description(tool["name"], tool["docstring"])
            lines.append(f"- **Description**: {desc}")
            lines.append("")
            
            if tool["docstring"]:
                # Format docstring - extract first paragraph
                doc_lines = [l.strip() for l in tool["docstring"].split("\n") if l.strip()]
                if doc_lines:
                    # Skip the first line (already used as description)
                    remaining_doc = doc_lines[1:] if len(doc_lines) > 1 else []
                    if remaining_doc:
                        lines.append("**Full Documentation**:")
                        lines.append("")
                        for doc_line in remaining_doc:
                            lines.append(f"> {doc_line}")
                        lines.append("")
            
            if tool["params"]:
                lines.append("**Parameters**:")
                lines.append("")
                lines.append("| Name | Type | Default | Description |")
                lines.append("|------|------|--------|-------------|")
                for param in tool["params"]:
                    required = "Required" if param.get("default") is None else "Optional"
                    param_type = param.get("type", "Any")
                    default = param.get("default")
                    default_str = "N/A" if default is None else f"`{default}`"
                    desc = param.get("description", "")
                    lines.append(f"| `{param['name']}` | {param_type} | {default_str} | {desc} |")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    return "\n".join(lines)


def generate_quick_reference_md(tools: List[Dict[str, Any]]) -> str:
    """Generate the compact QUICK_REFERENCE.md cheatsheet."""
    lines = []
    
    # Header
    lines.append("# AUTOGENERATED — do not edit by hand")
    lines.append("")
    lines.append("# Ableton MCP Extended — Quick Reference")
    lines.append("")
    lines.append("Compact cheatsheet for Ableton MCP Extended tools.")
    lines.append("Generated from MCP tool decorators and command registry.")
    lines.append("")
    
    # Top Commands by Category
    lines.append("## Top Commands by Category")
    lines.append("")
    lines.append("*(UDP = low-latency fire-and-forget, TCP = reliable request/response)*")
    lines.append("")
    
    # Define category groups and their priority commands
    category_groups = {
        "Session Setup": [
            "delete_all_tracks", "create_midi_track", "create_audio_track",
            "set_track_name", "set_tempo", "create_clip", "create_scene",
            "duplicate_track", "delete_track", "set_track_color",
            "set_track_fold", "set_track_monitoring_state"
        ],
        "Arrangement": [
            "capture_and_insert_arrangement", "capture_scenes_to_arrangement",
            "get_arrangement_clips", "set_loop", "create_locator",
            "jump_to_locator", "start_recording", "stop_recording",
            "start_playback", "stop_playback", "set_playhead_position",
            "get_playhead_position"
        ],
        "Mixing": [
            "set_track_volume", "set_track_pan", "set_track_mute",
            "set_track_solo", "set_master_volume", "get_level_snapshot",
            "set_crossfader_position", "apply_crossfader_sweep",
            "get_track_sends", "apply_send_sweep"
        ],
        "UDP": [
            "set_device_parameter", "set_track_volume", "set_track_pan",
            "set_track_mute", "set_track_solo", "set_track_arm",
            "set_master_volume", "set_send_amount", "fire_clip",
            "set_clip_launch_mode"
        ],
        "Effects": [
            "load_audio_effect", "load_instrument_or_effect",
            "get_device_parameters", "duplicate_device", "delete_device",
            "move_device", "load_instrument_preset"
        ],
        "MIDI": [
            "add_notes_to_clip", "create_drum_pattern", "apply_midi_effect",
            "set_global_quantization", "quantize_clip", "transpose_clip",
            "delete_notes_from_clip", "get_clip_notes"
        ],
    }
    
    for category, priority_tools in category_groups.items():
        # Get tools in this category
        category_tools = []
        for tool in tools:
            if tool["name"] in priority_tools:
                category_tools.append(tool)
        
        if not category_tools:
            continue
        
        lines.append(f"### {category}")
        lines.append("")
        
        # Sort by name
        category_tools.sort(key=lambda t: t["name"])
        
        # Display in compact form
        for tool in category_tools:
            transport = get_command_transport(tool["name"])
            desc = get_tool_description(tool["name"], tool["docstring"])
            icon = "[UDP]" if transport == "udp" else "[TCP]"
            lines.append(f"- `{tool['name']}` {icon} — {desc}")
        
        lines.append("")
    
    # List all remaining tools
    lines.append("## All Tools")
    lines.append("")
    
    lines.append("### By Transport")
    lines.append("")
    
    udp_tools = [t for t in tools if get_command_transport(t["name"]) == "udp"]
    tcp_tools = [t for t in tools if get_command_transport(t["name"]) == "tcp"]
    
    lines.append("**UDP (10 commands - fire-and-forget)**:")
    for tool in sorted(udp_tools, key=lambda t: t["name"]):
        lines.append(f"  - `{tool['name']}`")
    lines.append("")
    
    lines.append("**TCP (all other commands - request/response)**:")
    for tool in sorted(tcp_tools, key=lambda t: t["name"]):
        lines.append(f"  - `{tool['name']}`")
    lines.append("")
    
    # Transport Rules
    lines.append("## Transport Rules")
    lines.append("")
    lines.append("- **UDP**: Fire-and-forget, low latency (~0.2ms), no response")
    lines.append("  - Use for: parameter changes, track controls, clip triggering")
    lines.append("  - Only 10 commands support UDP (listed above)")
    lines.append("")
    lines.append("- **TCP**: Request/response, reliable (~20-50ms), awaits ACK")
    lines.append("  - Use for: all state-querying, creation, deletion, modifications")
    lines.append("  - Required for: `get_*`, `delete_*`, `create_*`, `quantize`, `undo/redo`, recording")
    lines.append("")
    lines.append("CAUTION: NEVER use UDP for `get_*`, `delete_*`, `quantize`, `undo/redo`, or recording operations.")
    lines.append("")
    
    return "\n".join(lines)


def extract_all_tools() -> List[Dict[str, Any]]:
    """Extract all tools from MCP_Server Python files."""
    all_tools = []
    
    mcp_server_files = get_mcp_server_files()
    print(f"Scanning {len(mcp_server_files)} files for tools...")
    
    for filepath in mcp_server_files:
        tools = extract_tools_from_file(filepath)
        if tools:
            print(f"  {filepath.name}: {len(tools)} tools")
        all_tools.extend(tools)
    
    # Deduplicate by name (keep first occurrence)
    seen_names = set()
    unique_tools = []
    for tool in all_tools:
        if tool["name"] not in seen_names:
            seen_names.add(tool["name"])
            unique_tools.append(tool)
        else:
            # Debug: show duplicates
            pass
    
    print(f"Total unique tools: {len(unique_tools)}")
    return unique_tools


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate tool documentation for Ableton MCP Extended"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check idempotency (exit non-zero if generated files differ)"
    )
    args = parser.parse_args()
    
    # Extract tools
    tools = extract_all_tools()
    
    if not tools:
        print("Error: No tools found!")
        sys.exit(1)
    
    # Generate documentation
    print("Generating TOOLS.md...")
    tools_md = generate_tools_md(tools)
    
    print("Generating QUICK_REFERENCE.md...")
    quick_ref_md = generate_quick_reference_md(tools)
    
    # Ensure docs directory exists
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write files
    tools_path = DOCS_DIR / "TOOLS.md"
    quick_ref_path = DOCS_DIR / "QUICK_REFERENCE.md"
    
    if args.check:
        # Check mode: compare with existing files
        if not tools_path.exists() or not quick_ref_path.exists():
            print("Error: Generated files do not exist yet. Run without --check first.")
            sys.exit(1)
        
        existing_tools = tools_path.read_text(encoding="utf-8")
        existing_quick = quick_ref_path.read_text(encoding="utf-8")
        
        if existing_tools == tools_md and existing_quick == quick_ref_md:
            print("Documentation is up to date (idempotent)")
            sys.exit(0)
        else:
            print("Documentation has changed (not idempotent)")
            sys.exit(1)
    else:
        # Write mode
        tools_path.write_text(tools_md, encoding="utf-8")
        quick_ref_path.write_text(quick_ref_md, encoding="utf-8")
        print(f"Written {tools_path}")
        print(f"Written {quick_ref_path}")
        
        # Verify the files were written
        assert tools_path.exists(), f"Failed to write {tools_path}"
        assert quick_ref_path.exists(), f"Failed to write {quick_ref_path}"


if __name__ == "__main__":
    main()
