#!/usr/bin/env python3
"""
Repo hygiene check script for Ableton MCP Extended.

This script verifies that generated artifacts are properly organized in their
designated directories (exports/, logs/, projects/) and not cluttering the repo root.

Exits:
- 0: All checks passed (clean repo)
- 1: Stray artifacts found in repo root
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent

# Files that are ALLOWED in repo root (source files, docs, config, etc.)
ALLOWED_FILES = {
    ".env.example",
    ".gitignore",
    ".gitmodules",
    "AGENTS.md",
    "ABLETON_INSTRUMENTS_INVENTORY.md",
    "ABLETON_INVENTORY_RESULTS.txt",
    "ARRANGEMENT_INTEGRATION.md",
    "BREAKTHROUGH_SUMMARY.md",
    "COMPLETE_SYSTEM_SUMMARY.md",
    "DUB_FEATURES.md",
    "DUB_TRACK_SUMMARY.txt",
    "EFFECT_TESTING_SESSION.md",
    "error_handling.py",
    "FAT_BEATZ.md",
    "FAT_BEATZ_SUMMARY.md",
    "FEATURE_ROADMAP.md",
    "FINAL_SUMMARY.md",
    "FINE_DUB_COMPLETE.md",
    "FINE_DUB_REAGAE_TRACK.md",
    "follow_actions.py",
    "IMPLEMENTATION_PIPELINE.md",
    "IMPLEMENTATION_SUMMARY.md",
    "IMPROVED_ARRANGEMENT_FEATURES.md",
    "INDEX.md",
    "instruments_addressed.py",
    "INVENTORY_SCRIPT.py",
    "LICENSE",
    "MASTER_CONTROL.md",
    "OPTIMIZATION_SUMMARY.md",
    "parameter_sweeps.py",
    "pattern_orchestration.py",
    "PIPELINE_SUMMARY.md",
    "PIPELINEREADME.md",
    "PRODUCTION_PIPELINE.md",
    "pyproject.toml",
    "QUICK_REAGAE_GUIDE.md",
    "QUICK_REFERENCE.md",
    "QUICK_START.md",
    "README.md",
    "REAGAE_AI_GENERATOR_COMPLETE.md",
    "REGGAE_IMPLEMENTATION.md",
    "REGGAE_MIX_GUIDE.md",
    "REGGAE_QUICK_START.md",
    "restart_ableton.bat",
    "restart_ableton.py",
    "restart_ableton_simple.py",
    "_debug_integration.py",
    "10MIN_MIX_COMPLETE.md",
    "10MIN_MIX_GUIDE.md",
    "audio_analysis.py",
    "automation_patterns.py",
    "clip_patterns.py",
    "create_ableton_fine_dub.py",
    "create_complete_reggae.py",
    "create_final_fine_dub.py",
    "create_reggae_with_midi.py",
    "fine_dub_generator.py",
    "mcp_client.py",
    "session_auto-save.py",
    "session_setup.py",
    "run_basic_demo.py",
    "run_demo_clean.py",
    "run_demo_now.py",
    "TWEAKS_SUMMARY.md",
    "YES_WE_ADDRESS_INSTRUMENTS.md",
}

# Directories that are ALLOWED in repo root
ALLOWED_DIRS = {
    ".claude",
    ".git",
    ".github",
    ".omo",
    ".sisyphus",
    "AbletonMCP_Remote_Script",
    "agentic_mix",
    "configs",
    "docs",
    "elevenlabs_mcp",
    "exports",
    "examples",
    "logs",
    "max_devices",
    "MCP_Server",
    "music_theory",
    "projects",
    "scripts",
    "skills",
    "tests",
}

# File extensions/types that should NOT be in repo root (should be in subdirs)
FORBIDDEN_EXTENSIONS = {".json", ".log", ".als"}
FORBIDDEN_NAMES = {"nul"}


def check_repo_root():
    """Check repo root for stray artifacts."""
    issues = []
    
    for item in REPO_ROOT.iterdir():
        # Skip allowed files and directories
        if item.name in ALLOWED_FILES or item.name in ALLOWED_DIRS:
            continue
        
        # Check if this is a forbidden file type or name
        # First check by name (handles special files like 'nul' on Windows)
        if item.name.lower() in FORBIDDEN_NAMES:
            issues.append(f"  - FORBIDDEN FILE (by name): {item.name}")
            continue
        
        # Then check regular files
        if item.is_file():
            # Check extension
            if item.suffix.lower() in FORBIDDEN_EXTENSIONS:
                issues.append(f"  - FORBIDDEN FILE (by extension): {item.name}")
            # Also check name again for regular files
            elif item.name.lower() in FORBIDDEN_NAMES:
                issues.append(f"  - FORBIDDEN FILE (by name): {item.name}")
        
        # Check if this is a forbidden directory (like Fine_Dub_Reggae_Project)
        if item.is_dir():
            # Project directories should be in projects/
            # Check if this looks like a project directory
            if item.name.endswith("_Project") or item.name.endswith("_Studio") or \
               item.name == "Fine_Dub_Reggae_Project" or item.name == "GOLDEN_RATIO_STUDIO":
                # These should be in projects/ or already handled
                # GOLDEN_RATIO_STUDIO was moved, so it shouldn't be at root
                issues.append(f"  - FORBIDDEN DIRECTORY (should be in projects/): {item.name}")
    
    return issues


def main():
    """Run hygiene checks and report results."""
    print("=" * 70)
    print("Ableton MCP Extended - Repo Hygiene Check")
    print("=" * 70)
    print()
    
    # Check repo root
    issues = check_repo_root()
    
    # Also check that exports/runs/ exists and has json files
    exports_runs = REPO_ROOT / "exports" / "runs"
    if exports_runs.exists():
        json_files = list(exports_runs.glob("*.json"))
        print(f"[OK] exports/runs/ exists with {len(json_files)} JSON file(s)")
    else:
        print("[WARN] exports/runs/ directory does not exist")
    
    # Check logs directory
    logs_dir = REPO_ROOT / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"[OK] logs/ exists with {len(log_files)} log file(s)")
    else:
        print("[WARN] logs/ directory does not exist")
    
    # Check projects directory
    projects_dir = REPO_ROOT / "projects"
    if projects_dir.exists():
        project_items = [p for p in projects_dir.iterdir() if p.is_dir()]
        print(f"[OK] projects/ exists with {len(project_items)} project(s)")
    else:
        print("[WARN] projects/ directory does not exist")
    
    print()
    
    if issues:
        print("[FAIL] REPO HYGIENE CHECK FAILED")
        print()
        print("Stray artifacts found in repo root:")
        for issue in issues:
            print(issue)
        print()
        print("Please move these files to their appropriate directories:")
        print("  - *.json files -> exports/runs/")
        print("  - *.log files -> logs/")
        print("  - *.als files -> projects/")
        print("  - project directories -> projects/")
        print()
        return 1
    else:
        print("[PASS] REPO HYGIENE CHECK PASSED")
        print()
        print("All generated artifacts are properly organized:")
        print("  - JSON files are in exports/runs/")
        print("  - Log files are in logs/")
        print("  - Project files/dirs are in projects/")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
