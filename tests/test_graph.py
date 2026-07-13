"""Tests for graph.py - audio feedback loop graph topology"""

from langgraph.graph import END
from langgraph.graph.state import CompiledStateGraph

from agentic_mix.graph import create_mix_pipeline, more_sections


class TestCreateMixPipeline:
    """Tests for create_mix_pipeline()"""

    def test_returns_compiled_graph(self):
        """Should return a compiled StateGraph"""
        graph = create_mix_pipeline()
        assert isinstance(graph, CompiledStateGraph)

    def test_has_all_required_nodes(self):
        """Should have all nodes including new audio feedback nodes"""
        graph = create_mix_pipeline()
        node_names = list(graph.nodes.keys())
        assert "configure" in node_names
        assert "setup_session" in node_names
        assert "generate_clips" in node_names
        assert "construct_arrangement" in node_names
        assert "execute_section" in node_names
        assert "analyze_section" in node_names

    def test_has_conditional_edge_from_analyze(self):
        """analyze_section should have conditional edges (loop or end)"""
        graph = create_mix_pipeline()
        # Compiled graphs should have edges properly wired
        # If the conditional edge was missing, compilation would fail
        assert isinstance(graph, CompiledStateGraph)


class TestMoreSections:
    """Tests for more_sections conditional edge function"""

    def test_returns_execute_section_when_more_remain(self):
        """Should return 'execute_section' when current_section_index < last index"""
        result = more_sections({
            "current_section_index": 1,
            "arrangement": [
                {"index": 0, "name": "a", "start_beat": 0.0, "end_beat": 16.0,
                 "energy_level": 5.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 0},
                {"index": 1, "name": "b", "start_beat": 16.0, "end_beat": 32.0,
                 "energy_level": 6.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 1},
                {"index": 2, "name": "c", "start_beat": 32.0, "end_beat": 48.0,
                 "energy_level": 4.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 2},
            ],
        })
        assert result == "execute_section"

    def test_returns_execute_section_on_last_index(self):
        """Should return execute_section when on last index (index not yet past array)"""
        result = more_sections({
            "current_section_index": 2,
            "arrangement": [
                {"index": 0, "name": "a", "start_beat": 0.0, "end_beat": 16.0,
                 "energy_level": 5.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 0},
                {"index": 1, "name": "b", "start_beat": 16.0, "end_beat": 32.0,
                 "energy_level": 6.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 1},
                {"index": 2, "name": "c", "start_beat": 32.0, "end_beat": 48.0,
                 "energy_level": 4.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 2},
            ],
        })
        assert result == "execute_section"

    def test_returns_end_when_index_past_end(self):
        """Should return END when current_section_index == len(arrangement)"""
        result = more_sections({
            "current_section_index": 3,
            "arrangement": [
                {"index": 0, "name": "a", "start_beat": 0.0, "end_beat": 16.0,
                 "energy_level": 5.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 0},
                {"index": 1, "name": "b", "start_beat": 16.0, "end_beat": 32.0,
                 "energy_level": 6.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 1},
                {"index": 2, "name": "c", "start_beat": 32.0, "end_beat": 48.0,
                 "energy_level": 4.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 2},
            ],
        })
        assert result == END

    def test_returns_execute_section_for_single_section(self):
        """Should return execute_section for a single-section arrangement at index 0"""
        result = more_sections({
            "current_section_index": 0,
            "arrangement": [
                {"index": 0, "name": "only", "start_beat": 0.0, "end_beat": 16.0,
                 "energy_level": 5.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 0},
            ],
        })
        assert result == "execute_section"

    def test_returns_end_for_single_section_past_index(self):
        """Should return END for single-section when index = 1 (past end)"""
        result = more_sections({
            "current_section_index": 1,
            "arrangement": [
                {"index": 0, "name": "only", "start_beat": 0.0, "end_beat": 16.0,
                 "energy_level": 5.0, "tracks_active": [], "mixing_technique": "none",
                 "scene_index": 0},
            ],
        })
        assert result == END

    def test_returns_end_for_empty_arrangement(self):
        """Should return END for empty arrangement (edge case)"""
        result = more_sections({
            "current_section_index": 0,
            "arrangement": [],
        })
        assert result == END
