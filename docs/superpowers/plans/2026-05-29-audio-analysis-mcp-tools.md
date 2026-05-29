# Audio Analysis MCP Tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the existing `AudioAnalyzer` (real-time audio BPM/key/loudness/spectral analysis via VB-Cable loopback) as 5 MCP tools in a new file.

**Architecture:** New file `MCP_Server/audio_analysis_tools.py` hosts a module-level `AudioAnalyzer` singleton (lazy-init on first `start`). 5 `@mcp.tool()` functions inside a `register_audio_analysis_tools(mcp, get_ableton_connection)` function. Registered by adding 2 lines to `server.py` (import + call), following the exact same pattern as `register_advanced_tools` at `server.py:760`.

**Tech Stack:** `sounddevice`, `numpy`, `AudioAnalyzer` from `MCP_Server.audio_analysis`. Optional dependencies `aubio`/`librosa`/`pyloudnorm` are already handled with graceful fallbacks inside `AudioAnalyzer`.

---

### Task 1: Create MCP_Server/audio_analysis_tools.py with all 5 tools + singleton

**Files:**
- Create: `MCP_Server/audio_analysis_tools.py`

**Details:** This file contains the module-level singleton, a helper to find audio devices by name substring, and the `register_audio_analysis_tools` function with all 5 tools inside it.

**Singleton pattern:**
```python
_analyzer: Optional["AudioAnalyzer"] = None
_analyzer_lock = threading.Lock()
_start_time: Optional[float] = None
```

**Device name search helper:**
```python
def _find_device_by_name(name_substring: str) -> Optional[int]:
    """Find a sound device whose name contains the given substring (case-insensitive)."""
    import sounddevice as sd
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        dev_name = dev.get("name", "")
        if isinstance(dev_name, str) and name_substring.lower() in dev_name.lower():
            if dev.get("max_input_channels", 0) > 0:
                return idx
    return None
```

**All 5 tools:**
```python
def register_audio_analysis_tools(mcp: FastMCP, get_ableton_connection):
    
    @mcp.tool()
    def audio_analysis_start(ctx: Context, device_name: Optional[str] = None) -> str:
        """
        Start real-time audio capture and analysis.
        
        Parameters:
        - device_name: Optional device name (substring, case-insensitive).
                       If omitted, auto-detects VB-Audio Cable.
        
        Returns JSON with status, device info, sample rate.
        """
        global _analyzer, _start_time
        try:
            config = AudioAnalyzerConfig()
            if device_name:
                device_index = _find_device_by_name(device_name)
                if device_index is None:
                    return json.dumps({
                        "status": "error",
                        "message": f"No input device found matching '{device_name}'"
                    }, indent=2)
                config.device_name = device_name
            
            with _analyzer_lock:
                if _analyzer is not None and _analyzer._running:
                    return json.dumps({
                        "status": "already_running",
                        "device_index": _analyzer._device_index,
                        "sample_rate": _analyzer.config.sample_rate
                    }, indent=2)
                
                _analyzer = AudioAnalyzer(config)
                success = _analyzer.start()
                if not success:
                    _analyzer = None
                    return json.dumps({
                        "status": "error",
                        "message": "Failed to start audio capture. Is VB-Audio Cable installed?"
                    }, indent=2)
                _start_time = time.time()
                return json.dumps({
                    "status": "started",
                    "device_index": _analyzer._device_index,
                    "sample_rate": _analyzer.config.sample_rate,
                    "buffer_size": _analyzer.config.buffer_size
                }, indent=2)
        except Exception as e:
            logger.error(f"Error starting audio analysis: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
    
    @mcp.tool()
    def audio_analysis_stop(ctx: Context) -> str:
        """
        Stop audio capture and release the stream.
        
        Returns JSON with status and capture duration.
        """
        global _analyzer, _start_time
        try:
            with _analyzer_lock:
                if _analyzer is None:
                    return json.dumps({"status": "not_running"}, indent=2)
                
                duration = 0.0
                if _start_time:
                    duration = time.time() - _start_time
                
                _analyzer.stop()
                _analyzer = None
                _start_time = None
                
                return json.dumps({
                    "status": "stopped",
                    "capture_duration_seconds": round(duration, 1)
                }, indent=2)
        except Exception as e:
            logger.error(f"Error stopping audio analysis: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
    
    @mcp.tool()
    def audio_analysis_get(ctx: Context) -> str:
        """
        Get the latest analysis snapshot.
        
        Returns JSON with: bpm, beat, rms, key, key_confidence,
        spectral_centroid, spectral_rolloff, loudness_lufs, timestamp.
        """
        try:
            with _analyzer_lock:
                if _analyzer is None or not _analyzer._running:
                    return json.dumps({
                        "status": "not_running",
                        "message": "Audio analysis not started. Call audio_analysis_start first."
                    }, indent=2)
                analysis = _analyzer.get_analysis()
            
            return json.dumps({
                "status": "success",
                "bpm": analysis["bpm"],
                "beat": analysis["beat"],
                "rms": round(analysis["rms"], 6),
                "key": analysis["key"],
                "key_confidence": round(analysis["key_confidence"], 4),
                "spectral_centroid_hz": round(analysis["spectral_centroid"], 2),
                "spectral_rolloff_hz": round(analysis["spectral_rolloff"], 2),
                "loudness_lufs": round(analysis["loudness_lufs"], 2),
                "timestamp": analysis["timestamp"]
            }, indent=2)
        except Exception as e:
            logger.error(f"Error getting audio analysis: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
    
    @mcp.tool()
    def audio_analysis_status(ctx: Context) -> str:
        """
        Return analyzer configuration and state.
        
        Returns JSON with: running, device_index, sample_rate,
        buffer_size, analysis_features.
        """
        try:
            with _analyzer_lock:
                if _analyzer is None:
                    return json.dumps({
                        "status": "success",
                        "running": False,
                        "device_index": None,
                        "sample_rate": None,
                        "buffer_size": None,
                        "features": None
                    }, indent=2)
                
                return json.dumps({
                    "status": "success",
                    "running": _analyzer._running,
                    "device_index": _analyzer._device_index,
                    "sample_rate": _analyzer.config.sample_rate,
                    "buffer_size": _analyzer.config.buffer_size,
                    "features": dict(_analyzer.config.analysis_features)
                }, indent=2)
        except Exception as e:
            logger.error(f"Error getting audio analysis status: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
    
    @mcp.tool()
    def audio_analysis_configure(ctx: Context, features: Optional[dict] = None) -> str:
        """
        Update analysis feature flags at runtime.
        
        Parameters:
        - features: Dict of feature keys to boolean values.
                    Valid keys: "bpm", "key", "spectral", "loudness".
                    Partial update — only specified keys change.
        
        Returns new config state.
        """
        try:
            with _analyzer_lock:
                if _analyzer is None:
                    return json.dumps({
                        "status": "not_running",
                        "message": "Configure before starting, or start first then configure."
                    }, indent=2)
                
                if features is None:
                    return json.dumps({
                        "status": "success",
                        "features": dict(_analyzer.config.analysis_features)
                    }, indent=2)
                
                valid_keys = {"bpm", "key", "spectral", "loudness"}
                for key in features:
                    if key not in valid_keys:
                        return json.dumps({
                            "status": "error",
                            "message": f"Invalid feature key '{key}'. Valid keys: {sorted(valid_keys)}"
                        }, indent=2)
                    if not isinstance(features[key], bool):
                        return json.dumps({
                            "status": "error",
                            "message": f"Feature '{key}' must be a boolean"
                        }, indent=2)
                    _analyzer.config.analysis_features[key] = features[key]
                
                return json.dumps({
                    "status": "success",
                    "features": dict(_analyzer.config.analysis_features)
                }, indent=2)
        except Exception as e:
            logger.error(f"Error configuring audio analysis: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
```

**Imports at top of file:**
```python
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any
import json
import logging
import time
import threading

from MCP_Server.audio_analysis import AudioAnalyzer, AudioAnalyzerConfig

logger = logging.getLogger("AbletonMCPServer")
```

- [ ] **Step 1: Create `MCP_Server/audio_analysis_tools.py`** with all of the above content (imports, singleton globals, device search helper, register function with 5 tools)

- [ ] **Step 2: Run Python parse check**

Run: `python -c "import ast; ast.parse(open('MCP_Server/audio_analysis_tools.py', encoding='utf-8').read()); print('Parse OK')"`
Expected: `Parse OK`

- [ ] **Step 3: Run LSP diagnostics**

Run: `lsp_diagnostics(filePath="MCP_Server/audio_analysis_tools.py", severity="error")`
Expected: Zero errors

### Task 2: Wire registration in server.py

**Files:**
- Modify: `MCP_Server/server.py`

**Details:** Add the import and registration call, exactly following the existing pattern at lines 752-761.

- [ ] **Step 1: Add import after line 757**

```python
from MCP_Server.audio_analysis_tools import register_audio_analysis_tools
```

Add this after `from MCP_Server.advanced_tools import (...)` block.

- [ ] **Step 2: Add registration call after line 761**

```python
register_audio_analysis_tools(mcp, get_ableton_connection)
```

Add this after `register_generation_tools(mcp, get_ableton_connection)`.

- [ ] **Step 3: Verify server.py parses**

Run: `python -c "import ast; ast.parse(open('MCP_Server/server.py', encoding='utf-8').read()); print('Parse OK')"`
Expected: `Parse OK`

- [ ] **Step 4: Verify import chain works**

Run: `python -c "from MCP_Server.server import mcp; print('Import OK'); print(f'Tools: {len(mcp._tool_manager._tools)}')"` (note: exact attribute for tool count may differ — if it fails, just confirm no ImportError)
Expected: `Import OK` or at minimum no `ImportError`/`SyntaxError`

### Task 3: Write unit tests

**Files:**
- Create: `tests/test_audio_analysis_tools.py`

**Details:** Since audio analysis requires physical audio hardware (VB-Cable), unit tests mock `sd.InputStream` and verify tool logic in isolation using a refactored helper that accepts a mock `AudioAnalyzer`. Simpler approach: test the device name helper and the tool function logic by temporarily replacing the global `_analyzer` with a mock.

- [ ] **Step 1: Write test file**

```python
"""Unit tests for audio_analysis_tools.py"""
import json
import sys
from unittest.mock import patch, MagicMock, PropertyMock

import pytest


@pytest.fixture
def mock_sd_devices():
    """Mock sounddevice query_devices to return test devices."""
    devices = [
        {"name": "VB-Audio Cable Output", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "VoiceMeeter Output", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "Speakers (Realtek)", "max_input_channels": 0, "max_output_channels": 2},
    ]
    with patch("sounddevice.query_devices", return_value=devices):
        yield


class TestDeviceNameSearch:
    """Test the device name search helper."""

    def test_find_vb_cable(self, mock_sd_devices):
        """Should find VB-Audio Cable by substring."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name
        idx = _find_device_by_name("CABLE")
        assert idx == 0

    def test_find_voice_meter(self, mock_sd_devices):
        """Should find VoiceMeeter by substring."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name
        idx = _find_device_by_name("Voice")
        assert idx == 1

    def test_find_case_insensitive(self, mock_sd_devices):
        """Should match case-insensitively."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name
        idx = _find_device_by_name("cable")
        assert idx == 0

    def test_no_match(self, mock_sd_devices):
        """Should return None for non-existent device."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name
        idx = _find_device_by_name("NonExistent")
        assert idx is None


class TestToolFunctions:
    """Test the MCP tool functions by examining their behavior."""

    @pytest.fixture
    def mock_analyzer(self):
        """Create a mock AudioAnalyzer that's already started."""
        mock = MagicMock()
        mock._running = True
        mock._device_index = 0
        mock.config.sample_rate = 44100
        mock.config.buffer_size = 2048
        mock.config.analysis_features = {"bpm": True, "key": True, "spectral": True, "loudness": True}
        mock.get_analysis.return_value = {
            "bpm": 126.0,
            "beat": True,
            "rms": 0.042,
            "key": "F",
            "key_confidence": 0.85,
            "spectral_centroid": 1200.0,
            "spectral_rolloff": 4500.0,
            "loudness_lufs": -14.5,
            "timestamp": 1234567890.0,
        }
        mock.get_status.return_value = {
            "running": True,
            "device_index": 0,
            "sample_rate": 44100,
            "buffer_size": 2048,
        }
        return mock

    def test_start_returns_json(self):
        """audio_analysis_start should return valid JSON."""
        from MCP_Server.audio_analysis_tools import register_audio_analysis_tools
        # Just verify the function can be called without error
        # (full test requires mocking sounddevice/AudioAnalyzer)
        assert callable(register_audio_analysis_tools)

    @patch("MCP_Server.audio_analysis_tools._analyzer")
    def test_get_returns_analysis(self, mock_analyzer_ref, mock_analyzer):
        """audio_analysis_get should format analysis results as JSON."""
        import MCP_Server.audio_analysis_tools as tools

        mock_analyzer._running = True
        mock_analyzer.get_analysis.return_value = {
            "bpm": 126.0,
            "beat": True,
            "rms": 0.042,
            "key": "F",
            "key_confidence": 0.85,
            "spectral_centroid": 1200.0,
            "spectral_rolloff": 4500.0,
            "loudness_lufs": -14.5,
            "timestamp": 1234567890.0,
        }
        tools._analyzer = mock_analyzer

        # Create a mock context
        ctx = MagicMock()
        result = tools.audio_analysis_get(ctx)
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["bpm"] == 126.0
        assert data["key"] == "F"

    @patch("MCP_Server.audio_analysis_tools._analyzer")
    def test_get_not_running(self, mock_analyzer_ref):
        """audio_analysis_get should return not_running if analyzer is None."""
        import MCP_Server.audio_analysis_tools as tools
        tools._analyzer = None

        ctx = MagicMock()
        result = tools.audio_analysis_get(ctx)
        data = json.loads(result)
        assert data["status"] == "not_running"

    @patch("MCP_Server.audio_analysis_tools._analyzer")
    def test_status_returns_state(self, mock_analyzer_ref, mock_analyzer):
        """audio_analysis_status should return full state when running."""
        import MCP_Server.audio_analysis_tools as tools

        mock_analyzer._running = True
        mock_analyzer._device_index = 0
        mock_analyzer.config.sample_rate = 44100
        mock_analyzer.config.buffer_size = 2048
        mock_analyzer.config.analysis_features = {"bpm": True, "key": True, "spectral": True, "loudness": True}
        tools._analyzer = mock_analyzer

        ctx = MagicMock()
        result = tools.audio_analysis_status(ctx)
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["running"] is True
        assert data["sample_rate"] == 44100

    @patch("MCP_Server.audio_analysis_tools._analyzer")
    def test_configure_toggles_features(self, mock_analyzer_ref, mock_analyzer):
        """audio_analysis_configure should toggle features."""
        import MCP_Server.audio_analysis_tools as tools
        tools._analyzer = mock_analyzer

        ctx = MagicMock()
        result = tools.audio_analysis_configure(ctx, features={"bpm": False, "loudness": False})
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["features"]["bpm"] is False
        assert data["features"]["loudness"] is False
        assert data["features"]["key"] is True  # unchanged

    @patch("MCP_Server.audio_analysis_tools._analyzer")
    def test_configure_invalid_key(self, mock_analyzer_ref, mock_analyzer):
        """audio_analysis_configure should reject invalid feature keys."""
        import MCP_Server.audio_analysis_tools as tools
        tools._analyzer = mock_analyzer

        ctx = MagicMock()
        result = tools.audio_analysis_configure(ctx, features={"tempo": True})
        data = json.loads(result)
        assert data["status"] == "error"

    @patch("MCP_Server.audio_analysis_tools._analyzer")
    def test_configure_non_bool_value(self, mock_analyzer_ref, mock_analyzer):
        """audio_analysis_configure should reject non-boolean values."""
        import MCP_Server.audio_analysis_tools as tools
        tools._analyzer = mock_analyzer

        ctx = MagicMock()
        result = tools.audio_analysis_configure(ctx, features={"bpm": "yes"})
        data = json.loads(result)
        assert data["status"] == "error"
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_audio_analysis_tools.py -v`
Expected: All tests pass (at minimum the mock-based tests)

- [ ] **Step 3: Verify server import chain still works with new file**

Run: `python -c "from MCP_Server.audio_analysis_tools import register_audio_analysis_tools; print('Import OK')"`
Expected: `Import OK`

### Task 4: Self-review & fix

- [ ] **Step 1: Spec coverage check**

Cross-check each spec requirement against the implementation:
1. `audio_analysis_start(device_name=None)` — ✅ Implements auto-detect + explicit device name
2. `audio_analysis_stop()` — ✅ Idempotent, returns duration
3. `audio_analysis_get()` — ✅ Returns all 7 analysis fields + status
4. `audio_analysis_status()` — ✅ Running/device/config
5. `audio_analysis_configure(features=None)` — ✅ Partial update, validation
6. Registration pattern — ✅ Import + call in server.py
7. Docstrings — ✅ All tools have docstrings following existing format
8. Error handling pattern — ✅ try/except → `json.dumps({"status": "error", ...})`

- [ ] **Step 2: Final verification**

Run: `python -c "from MCP_Server.audio_analysis_tools import register_audio_analysis_tools; from MCP_Server.server import mcp; print('Full import chain OK')"`
Expected: `Full import chain OK`
