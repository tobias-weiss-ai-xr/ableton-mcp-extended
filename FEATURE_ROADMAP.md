# 🗺️ Ableton MCP Extended - Feature Roadmap

## Last Updated: July 27, 2026
**Status: Arrangement View Integration ✅ COMPLETE**

---

## 🎯 Priority Matrix

| Priority | Impact | Effort | Category |
|----------|--------|--------|----------|
| 🔥 P0 | ⭐⭐⭐⭐⭐ | Any | **Critical Bugs** - Must fix immediately |
| ⚡ P1 | ⭐⭐⭐⭐ | Low-Medium | **High Impact / Quick Win** - 1-2 hours |
| 🚀 P2 | ⭐⭐⭐ | Medium | **Medium Impact** - 2-4 hours |
| 🌟 P3 | ⭐⭐⭐⭐ | High | **High Impact / Longer Effort** - 4-8 hours |
| 🎨 P4 | ⭐⭐ | Any | **Creative / Nice-to-Have** |

---

## 🔥 P0: Critical Bugs & Fixes

| ID | Feature | Status | Files | Notes |
|----|---------|--------|-------|-------|
| P0-1 | Fix `capture_and_insert_arrangement` in Live 12 | ✅ **DONE** | `AbletonMCP_Remote_Script/__init__.py` | Three-tier fallback implemented |
| P0-2 | Fix `get_arrangement_clips` crashing | ✅ **DONE** | `AbletonMCP_Remote_Script/__init__.py` | Returns empty array instead of crash |
| P0-3 | Fix command format in `run_basic_demo.py` | ✅ **DONE** | `run_basic_demo.py` | `{"type": cmd}` instead of `{"command": cmd}` |

---

## ⚡ P1: High Impact / Quick Win (1-2 hours)

### Next Up: P1-1 ✅ **START HERE**
| ID | Feature | Description | Status | Files | Estimated Time |
|----|---------|-------------|--------|-------|----------------|
| P1-1 | **Scene-Based Capture & Arrangement** | Trigger scenes in sequence while recording for structured arrangements (intro, verse, chorus, drop) | 🟡 **IN PROGRESS** | `AbletonMCP_Remote_Script/__init__.py`, `MCP_Server/arrangement_tools.py` | 2 hours |
| P1-2 | Loop Region-Based Recording | Set loop region and record for exact number of loops | ⏳ | Same as P1-1 | 1 hour |
| P1-3 | Clip warping & Tempo Matching | Auto-warp new clips to project tempo | ⏳ | New tool | 2 hours |
| P1-4 | Track Color & Routing Automation | Auto-color by instrument type, route to busses | ⏳ | `mixer_tools.py` | 1 hour |
| P1-5 | Non-Destructive Clip Editing | Slice, reverse, pitch-shift without new files | ⏳ | `arrangement_tools.py` | 2 hours |

### P1-1 Details: Scene-Based Capture

**Goal**: Enable users to build arrangements by triggering scenes in sequence

**New Commands**:
```python
# Capture scenes in order
capture_scenes_to_arrangement(
    scene_sequence=[0, 1, 2, 1, 3],  # Scene indices
    scene_bars=[4, 8, 4, 8, 16],     # Bars per scene
    start_bar=0
)

# Or with named scenes
capture_scenes_to_arrangement(
    scene_structure={
        "intro": {"scene": 0, "bars": 8},
        "verse": {"scene": 1, "bars": 16},
        "chorus": {"scene": 2, "bars": 16},
        "bridge": {"scene": 3, "bars": 8}
    },
    arrangement=["intro", "verse", "chorus", "verse", "chorus"]
)
```

**Implementation Plan**:
1. Add `_capture_scenes_to_arrangement` to Remote Script
2. Start recording, play through scenes with timing, stop recording
3. Add MCP tool wrapper
4. Test with `scripts/test_scene_capture.py`

---

## 🚀 P2: Medium Impact (2-4 hours)

| ID | Feature | Description | Status | Files | Time |
|----|---------|-------------|--------|-------|------|
| P2-1 | Automation Clip Creation | Create automation lanes for any parameter | ✅ **DONE** | `arrangement_tools.py` | - |
| P2-2 | AI-Powered Mix Suggestions | Analyze audio, suggest EQ/compression | ⏳ | `optimization_tools.py` + new | 4 hours |
| P2-3 | Template-Based Project Creation | Pre-built templates for genres | ⏳ | New `templates/` | 3 hours |
| P2-4 | VST Plugin Control | Control third-party plugins | ⏳ | `server.py` | 4 hours |
| P2-5 | MIDI Learn & Hardware Mapping | Map controllers to parameters | ⏳ | New `midi_mapping.py` | 3 hours |

---

## 🌟 P3: High Impact / Longer Effort (4-8 hours)

| ID | Feature | Description | Status | Files | Time |
|----|---------|-------------|--------|-------|------|
| P3-1 | Real-Time Parameter Automation Drawing | Draw complex automation curves | ⏳ | New `automation_drawing.py` | 6 hours |
| P3-2 | AI-Powered Stem Separation Import | Import separated stems | ⏳ | New `stem_import.py`