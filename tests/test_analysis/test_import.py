#!/usr/bin/env python3
"""
Simplified test for parameter polling system.
"""

import sys
import os

# Add the scripts/analysis directory to path for imports
scripts_analysis_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "analysis")
)
if scripts_analysis_path not in sys.path:
    sys.path.insert(0, scripts_analysis_path)

try:
    from poll_plugin_params import ParameterPoller

    print("OK Import successful")
    print(f"Scripts path: {scripts_analysis_path}")

    # Test basic initialization
    poller = ParameterPoller(
        track_index=2, device_index=1, update_rate_hz=15.0, duration_seconds=60
    )

    print(f"Initialization successful:")
    print(f"  track_index: {poller.track_index}")
    print(f"  device_index: {poller.device_index}")
    print(f"  update_rate_hz: {poller.update_rate_hz}")

except ImportError as e:
    print(f"✗ Import error: {e}")
    print(f"Scripts path: {scripts_analysis_path}")
