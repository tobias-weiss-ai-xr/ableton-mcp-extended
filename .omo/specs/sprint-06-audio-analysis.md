# Sprint 06: Audio Analysis Pipeline

**Theme:** Extract musical information from audio clips in real-time.
**Est. days:** 5 | **New tools:** 4-5 | **Risk:** High
**Dependencies:** None

## Goal
Add intelligent audio analysis: detect BPM, key, transients from clips. The current `audio_analysis/` module does basic spectral analysis; we need musical feature extraction. Audio-to-MIDI conversion is the crown jewel that no other MCP server has.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/audio_analysis_tools.py` | Extend | Add detection tools |
| `MCP_Server/audio_analysis/bpm_detector.py` | Create | BPM via autocorrelation + onset detection |
| `MCP_Server/audio_analysis/key_detector.py` | Create | Key via chroma features + Krumhansl-Schmuckler |
| `MCP_Server/audio_analysis/transient_detector.py` | Create | Onset detection + beat grid |
| `MCP_Server/audio_analysis/audio_to_midi.py` | Create | Monophonic pitch tracking (McAulay-Quatieri) |
| `MCP_Server/audio_analysis/feature_extract.py` | Create | Spectral features, loudness, MFCCs |
| `AbletonMCP_Remote_Script/__init__.py` | Modify | Add clip audio data extraction handler |
| `scripts/analysis/` | Add | Example analysis scripts |
| `tests/test_audio_analysis.py` | Create | Unit tests with fixture audio files |
| `tests/fixtures/test_440hz.wav` | Create | 2s 440Hz sine wave |
| `tests/fixtures/test_drum_loop.wav` | Create | 4-bar drum loop at 120 BPM |

## Deliverables

### 6.1 BPM Detection (`bpm_detector.py`)
- **Method:** Onset strength + autocorrelation
- Read audio from .wav clip (export from Live or offline file)
- Compute onset detection function (spectral flux)
- Autocorrelation of onset envelope → BPM candidates
- Return: bpm, confidence (0.0-1.0), alternative bpm, tempo_range
- Handles: 60-200 BPM range, half-time/double-time correction
- Accuracy goal: ±1 BPM for steady loops, ±3 BPM for full tracks

```python
def detect_bpm(audio_data: np.ndarray, sample_rate: int) -> dict:
    """Returns {'bpm': float, 'confidence': float, 'alternatives': [float]}"""
```

### 6.2 Key Detection (`key_detector.py`)
- **Method:** Krumhansl-Schmuckler key-finding algorithm
- Compute chromagram (12-bin pitch class profile)
- Correlate with key profiles (major/minor)
- Return: key name (e.g., "C", "F#"), mode ("major"/"minor"), confidence
- Temperature smoothing for ambiguous keys
- Returns top 2 candidates with confidence

```python
def detect_key(audio_data: np.ndarray, sample_rate: int) -> dict:
    """Returns {'key': str, 'mode': str, 'confidence': float, 'alternatives': [dict]}"""
```

Allowed output keys: C, C#, D, D#, E, F, F#, G, G#, A, A#, B (using enharmonic equivalents based on mode).

### 6.3 Transient Detection (`transient_detector.py`)
- **Method:** Spectral flux + adaptive threshold
- Detect onset times (sample-accurate)
- Return: beat_grid (beat times in seconds + bars), transient_count, average_peak_db
- Classify onsets as kick/snare/hat based on spectral centroid
- Handles: polyphonic material, variable dynamics

```python
def detect_transients(audio_data: np.ndarray, sample_rate: int) -> dict:
    """Returns {'onsets': [float], 'beat_grid': [{'time': float, 'bar': int}],
                 'onset_count': int, 'classifications': [dict]}"""
```

### 6.4 Audio-to-MIDI (`audio_to_midi.py`)
- **Method:** Monophonic pitch tracking (McAulay-Quatieri algorithm)
- Frame-based FFT → peak picking → pitch tracking
- Note segmentation: onset detection + pitch stability
- Return: MIDI-like notes list `[{pitch, start_time, duration, velocity}]`
- **Limitation:** Monophonic only (single note at a time — melody, bass, vocal)
- Target accuracy: 90%+ for clean monophonic input

```python
def audio_to_midi(audio_data: np.ndarray, sample_rate: int) -> list[dict]:
    """Returns notes: [{pitch: int, start_time: float, duration: float, velocity: int}]"""
```

### 6.5 Feature Extraction (`feature_extract.py`)
- Spectral centroid, rolloff, flux, zero-crossing rate
- RMS loudness envelope
- MFCCs (13 coefficients) for timbre analysis
- Returns all features as dict for downstream processing

### 6.6 Remote Script Handler
Add `_get_clip_audio_data(track_index, clip_index) -> bytes`:
- Exports clip audio as 44.1kHz 16-bit WAV bytes via Live API
- Only works for audio clips (not MIDI)
- Returns error for MIDI clips: "cannot export MIDI as audio"
- Max duration: 60 seconds (clips longer are truncated)

### 6.7 MCP Tools

**Tool: `detect_clip_bpm`**
```
(ctx, track_index: int, clip_index: int) -> str
```
- Grabs audio from clip via Remote Script
- Runs BPM detection
- Returns: `{bpm, confidence, alternative_bpm}`

**Tool: `detect_clip_key`**
```
(ctx, track_index: int, clip_index: int) -> str
```
- Grabs audio from clip
- Runs key detection
- Returns: `{key, mode, confidence}`

**Tool: `analyze_clip_audio`**
```
(ctx, track_index: int, clip_index: int) -> str
```
- Full analysis: BPM + key + transients + features
- Returns comprehensive dict with all results
- Caches per (track, clip) key (30s TTL)

**Tool: `convert_audio_to_midi`**
```
(ctx, track_index: int, clip_index: int, target_track_index: int = None,
 min_pitch: int = 36, max_pitch: int = 84) -> str
```
- Extracts audio from clip
- Runs monophonic pitch detection
- Creates MIDI clip with detected notes on target track
- If no target track, creates new MIDI track
- Returns: note count, pitch range, duration

**Tool: `detect_bpm_from_file`**
```
(ctx, file_path: str) -> str
```
- Analyzes .wav file directly (useful for offline loops)
- Same algorithm as detect_clip_bpm

## API Surface

### New Tools
| Tool | Signature | Returns |
|------|-----------|---------|
| `detect_clip_bpm` | (track_index, clip_index) | BPM + confidence |
| `detect_clip_key` | (track_index, clip_index) | Key + mode + confidence |
| `analyze_clip_audio` | (track_index, clip_index) | Full analysis |
| `convert_audio_to_midi` | (track_index, clip_index, target_track_index, min_pitch, max_pitch) | MIDI notes + clip |
| `detect_bpm_from_file` | (file_path) | BPM + confidence |

### New Handler
- `_get_clip_audio_data(track_index, clip_index) -> bytes` (in __init__.py)

## Acceptance Criteria
```bash
# BPM detection with fixture
python -c "
from MCP_Server.audio_analysis.bpm_detector import detect_bpm
import numpy as np
# 120 BPM test signal: impulse train every 0.5s
sr = 44100
t = np.linspace(0, 4, int(sr*4), endpoint=False)
signal = np.zeros_like(t)
for beat in range(8):
    idx = int(beat * 0.5 * sr)  # 120 BPM = 0.5s per beat
    if idx < len(signal):
        signal[idx] = 1.0
result = detect_bpm(signal, sr)
assert abs(result['bpm'] - 120) < 3, f'bpm={result[\"bpm\"]}'
assert result['confidence'] > 0.5
print(f'BPM detection OK: {result}')
"
```

```bash
# Key detection with synthesized chord
python -c "
from MCP_Server.audio_analysis.key_detector import detect_key
import numpy as np
# C major chord (C4=261.63, E4=329.63, G4=392.00)
sr = 44100
t = np.linspace(0, 1, sr, endpoint=False)
signal = (np.sin(2*np.pi*261.63*t) + np.sin(2*np.pi*329.63*t) + np.sin(2*np.pi*392.00*t))
result = detect_key(signal, sr)
print(f'Key detection result: {result}')
assert result['key'] == 'C'  # may fail → check alternative candidates
"
```

```bash
grep -c "@mcp.tool()" MCP_Server/audio_analysis_tools.py
# 5+ tools
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| BPM detection wrong for complex music | Medium | Return confidence + alternatives; don't auto-set tempo |
| Key detection fails on atonal/noisy material | Low | Return confidence=0 + "Uncertain" |
| Audio-to-MIDI only monophonic | Medium | Document limitation clearly; return error for polyphonic |
| numpy/scipy deps conflict with existing | Medium | Pin versions; check against pyproject.toml |
| Audio extraction from Live is slow | Medium | Cache results; process asynchronously |
| FFmpeg/Pydub/soundfile not installed | Low | Graceful fallback: "install optional dep"; test coverage uses numpy-generated signals |

## Must NOT Do
- Do NOT attempt polyphonic audio-to-MIDI (research area, not production-ready)
- Do NOT modify the audio_analysis module structure (extend it)
- Do NOT add audio rendering/export (use Max device for that)
- Do NOT require FFmpeg or external binaries (numpy-only signal processing)
- Do NOT analyze more than 60s of audio (performance bound)
