#!/usr/bin/env python3
"""
PRODUCTION PIPELINE - QUICK START

Simplified pipeline for quick mix-to-MP3 workflow.

Usage:
    python scripts/production_pipeline_quick.py dub_techno          # Basic setup
    python scripts/production_pipeline_quick.py techno --mp3       # + MP3 export
    python scripts/production_pipeline_quick.py dub --title "Mix"  # Custom title
"""

import sys
sys.path.insert(0, str(__file__).parent.parent))

from production_pipeline import main as _main

if __name__ == "__main__":
    # Quick start: ply maintenance
    _main()
