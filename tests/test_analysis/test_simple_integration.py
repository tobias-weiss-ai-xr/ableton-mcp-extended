#!/usr/bin/env python3
"""
Simple integration test for VST analysis system.
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
    from test_analysis import MockMCPServer

    # Test basic integration
    mock_server = MockMCPServer()
    mock_server.start()

    print("Test completed successfully!")

except Exception as e:
    print(f"Error: {e}")
    print(f"Scripts path: {scripts_analysis_path}")
