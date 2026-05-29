# Audio Analysis MCP Tools — Design Spec

> **Goal**: Expose existing real-time audio analysis as callable MCP tools so AI can query live session audio metrics (BPM, key, loudness, spectral).

**Status**: Design ready for review.

---

## Architecture

A single new file `MCP_Server/audio_analysis_tools.py` with a dedicated `register_audio_analysis_tools(mcp, get_ableton_connection)` function, registered in `server.py` alongside the existing `register_advanced_tools` and `register_midi_effect_tools` calls.

The file manages a module-level singleton `AudioAnalyzer` instance (lazy-init on first `start` call). No global state beyond this single instance.

**Dependencies**: Already in `setup.py` / `requirements.txt` — `sounddevice`, `numpy`. Optional: `aubio`, `librosa`, `pyloudnorm` (graceful fallback if missing).

**Existing tool already available**: `detect_clip_key(track_index, clip_index)` already exists in `server.py` — detects key by analyzing MIDI notes in a clip. No need to re-create.

---

## Tools

### 1. `audio_analysis_start(device_name: str = None) → str`

Start real-time audio capture and analysis.

- If `device_name` provided, search available sound devices for a match (substring, case-insensitive).
- If omitted, auto-detect VB-Audio Cable (existing behavior).
- Returns JSON with status, device info, sample rate.

**Error cases**: No suitable device found, device busy, missing dependencies (aubio/librosa).

### 2. `audio_analysis_stop() → str`

Stop audio capture and release the stream.

- Returns JSON with status and duration of capture session.
- Idempotent — safe to call if already stopped.

### 3. `audio_analysis_get() → str`

Get the latest analysis snapshot.

Returns JSON with:
- `bpm`: Detected BPM (0.0 if not yet stable)
- `beat`: Boolean, true on beat events
- `rms`: RMS energy (0.0-1.0)
- `key`: Detected key (e.g., "C", "F#") or "unknown"
- `key_confidence`: 0.0-1.0
- `spectral_centroid`: Hz
- `spectral_rolloff`: Hz
- `loudness_lufs`: Integrated LUFS (-100.0 if N/A)
- `timestamp`: Unix timestamp of last analysis update

**Error cases**: Analyzer not started (returns descriptive message).

### 4. `audio_analysis_status() → str`

Return analyzer configuration and state.

Returns JSON with:
- `running`: Boolean
- `device_index`: Sound device index or null
- `sample_rate`: Hz
- `buffer_size`: Samples per block
- `features`: Dict of enabled analysis feature flags

**Error cases**: None (always returns state).

### 5. `audio_analysis_configure(features: dict = None) → str`

Update analysis feature flags at runtime (which features are active).

- Accepts partial update — only specified keys change.
- Returns new config state.

**Error cases**: Invalid feature key names.

---

## Data Flow

```
AI → MCP Tool Call → audio_analysis_tools.py → AudioAnalyzer singleton → sounddevice stream
                                                          ↓
                                                    numpy audio buffer
                                                          ↓
                                            aubio → BPM / beat
                                            librosa → key, spectral
                                            pyloudnorm → LUFS
                                                          ↓
                                              thread-safe _analysis dict
                                                          ↓
AI ← JSON ← tool reads get_analysis()
```

- `start()`: Creates `sd.InputStream` with callback that updates `_analysis` dict under a lock.
- `get()`: Reads `_analysis` dict under same lock — non-blocking, fast.
- `stop()`: Closes stream, sets `_running = False`.

---

## Registration

Add to `MCP_Server/server.py`:

```python
from MCP_Server.audio_analysis_tools import register_audio_analysis_tools
register_audio_analysis_tools(mcp, get_ableton_connection)
```

Following the exact same pattern as `register_advanced_tools(mcp, get_ableton_connection)` at line 760.

---

## Error Handling

All tools follow the existing `advanced_tools.py` pattern:

```python
try:
    ...
    return json.dumps({"status": "success", ...}, indent=2)
except Exception as e:
    logger.error(f"Error in tool_name: {str(e)}")
    return json.dumps({"status": "error", "message": str(e)})
```

---

## Testing

Since audio analysis requires a physical audio loopback (VB-Cable), unit tests should mock `sd.InputStream`:

- `test_start_stop.py`: Verify state transitions, idempotent stop.
- `test_get_analysis.py`: Verify thread-safe read returns dict shape.
- `test_configure.py`: Verify feature toggles.
- `test_device_detection.py`: Verify device name matching logic.

Integration test (manual): Run `showcase_audio_analysis.py` to confirm Ableton loopback works, then test tools via MCP inspector.

---

## Open Questions

1. Single file or integrate into `advanced_tools.py`? **Recommend: separate file** — keeps concerns clean, avoids growing `advanced_tools.py` further (2701 lines).
2. Device input selection: auto-detect VB-Cable or allow explicit device name? **Both** — auto-detect with optional override.
