#!/usr/bin/env python3
"""
Simplified test for rules parser.
"""

import sys
import os

# Add the scripts/analysis directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up to tests/
analysis_dir = os.path.join(project_root, "scripts", "analysis")
scripts_analysis_path = os.path.abspath(analysis_dir)

if scripts_analysis_path not in sys.path:
    sys.path.insert(0, scripts_analysis_path)

try:
    from rules_parser import RulesParser

    # Test basic functionality
    parser = RulesParser()

    # Simple YAML test
    yaml_data = {
        "rules": [
            {
                "name": "test_rule",
                "priority": 1,
                "condition": {"operator": ">", "param1": "test", "param2": "5"},
                "action": {"type": "set_volume", "params": {"track": 0}},
            }
        ]
    }

    # Write to temp file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        import yaml

        yaml.dump(yaml_data, f)
        f.flush()

        rules = parser.parse(f.name)

        print(f"Rules parsed successfully:")
        print(f"  Count: {len(rules)}")
        if rules:
            rule = rules[0]
            print(f"  First rule: {rule.name}")
            print(f"  Priority: {rule.priority}")
            print(f"  Operator: {rule.condition.operator}")
            print(f"  Action: {rule.action.type}")

except Exception as e:
    print(f"Error: {e}")
    print(f"Scripts path: {scripts_analysis_path}")
