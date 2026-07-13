"""Tests for execute section node"""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_client():
    client = Mock()
    client.trigger_scene = Mock()
    return client


def test_execute_section_node_triggers_scene_and_applies_technique(mock_client):
    """Execute section with dub_drop technique"""

    from agentic_mix.nodes.execute_section import execute_section_node

    section = {
        "index": 0,
        "name": "groove_a",
        "start_beat": 0.0,
        "end_beat": 16.0,
        "energy_level": 5.0,
        "tracks_active": [0, 1, 2, 3],
        "mixing_technique": "dub_drop",
        "scene_index": 0,
    }

    state = {
        "current_section_index": 0,
        "arrangement": [section],
        "client": mock_client,
        "playback_metrics": {
            "start_time": 0.0,
            "current_time": 0.0,
            "section_transitions": [],
            "mixing_actions": [],
            "errors": [],
        },
    }

    with patch("agentic_mix.tools.apply_dub_drop") as mock_dub_drop:
        result = execute_section_node(state)

        mock_client.trigger_scene.assert_called_once_with(0)
        mock_dub_drop.assert_called_once()

        assert len(result["playback_metrics"]["section_transitions"]) == 1
        transition = result["playback_metrics"]["section_transitions"][0]
        assert transition["section_index"] == 0
        assert transition["technique"] == "dub_drop"


def test_execute_section_node_no_technique(mock_client):
    """Execute section with 'none' technique (no-op)"""

    from agentic_mix.nodes.execute_section import execute_section_node

    section = {
        "index": 0,
        "name": "groove_a",
        "start_beat": 0.0,
        "end_beat": 16.0,
        "energy_level": 5.0,
        "tracks_active": [],
        "mixing_technique": "none",
        "scene_index": 0,
    }

    state = {
        "current_section_index": 0,
        "arrangement": [section],
        "client": mock_client,
        "playback_metrics": {
            "start_time": 0.0,
            "current_time": 0.0,
            "section_transitions": [],
            "mixing_actions": [],
            "errors": [],
        },
    }

    with patch("agentic_mix.tools.apply_dub_drop") as mock_dub_drop:
        execute_section_node(state)

        mock_client.trigger_scene.assert_called_once_with(0)
        mock_dub_drop.assert_not_called()
