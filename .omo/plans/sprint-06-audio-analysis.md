# sprint-06-audio-analysis - Work Plan

## TL;DR (For humans)

**What you'll get:** Ableton MCP gains intelligent audio analysis: BPM detection (±1 BPM for loops), key detection (Krumhansl-Schmuckler), transient/onset detection with beat grid and spectral classification, monophonic audio-to-MIDI conversion (the crown jewel — no other MCP server has this), and full spectral feature extraction (MFCCs, centroid, flux, rolloff, loudness). All powered by numpy-only signal processing — zero external binary dependencies.

**Why this approach:** Musical feature extraction is the #1 gap in current Ableton MCP servers. BPM/key/transient detection unlocks DJ tools, beatmatching, key-mixing, and automated arrangement. Audio-to-MIDI is unique — no competitor offers it. The numpy-only constraint keeps installation trivial (no FFmpeg, no external binaries). The modular design (one file per detector) makes each unit independently testable and maintainable.

**What it will NOT do:** Polyphonic audio-to-MIDI (research area, not production-ready), audio rendering/export (use Max device), modify existing `audio_analysis/` module structure, require FFmpeg or external binaries, analyze more than 60s of audio.

**Effort:** Medium (5 days, 8 todos across 4 waves)
**Risk:** High — BPM/key detection accuracy on real-world material is inherently probabilistic; audio-to-MIDI quality varies with input cleanliness
**Decisions to sanity-check:** BPM detection method (autocorrelation vs onset peak picking), key profile set (Krumhansl-Schmuckler vs Temperley), audio-to-MIDI peak tracking algorithm (McAulay-Quatieri with what threshold policy)

Your next move: Approve this plan, then run `$start-work` to begin execution.

---

> TL;DR (machine): Medium effort, High risk (detection accuracy on real-world audio). 8 deliverables across 4 waves. Wave 1: 4 core detection modules in parallel (bpm, key, transient, features). Wave 2: audio-to-midi + Remote Script clip audio handler. Wave 3: MCP tool registration surface (5 new tools). Wave 4: test fixtures + unit tests + example scripts. numpy-only, no external deps.

## Scope

### Must have
- `MCP_Server/audio_analysis/bpm_detector.py` — BPM detection via onset strength + autocorrelation (60-200 BPM, half/double-time correction, confidence + alternatives)
- `MCP_Server/audio_analysis/key_detector.py` — Krumhansl-Schmuckler key-finding via chromagram + key profile correlation (12 keys, major/minor, top 2 candidates, temperature smoothing)
- `MCP_Server/audio_analysis/transient_detector.py` — Spectral flux + adaptive threshold onset detection, beat grid with bar-aligned times, transient classification (kick/snare/hat by spectral centroid)
- `MCP_Server/audio_analysis/audio_to_midi.py` — Monophonic pitch tracking via McAulay-Quatieri: frame-based FFT → peak picking → pitch tracking → note segmentation → MIDI note list
- `MCP_Server/audio_analysis/feature_extract.py` — Spectral centroid, rolloff, flux, zero-crossing rate, RMS loudness envelope, 13 MFCC coefficients
- `AbletonMCP_Remote_Script/__init__.py` — Add `_get_clip_audio_data(track_index, clip_index)` handler: exports clip audio as 44.1kHz 16-bit WAV bytes (max 60s, error on MIDI clips)
- `MCP_Server/audio_analysis_tools.py` — 5 new MCP tools: `detect_clip_bpm`, `detect_clip_key`, `analyze_clip_audio` (full analysis + 30s cache), `convert_audio_to_midi` (creates MIDI clip on target track), `detect_bpm_from_file`
- `tests/test_audio_analysis.py` — Unit tests with numpy-generated test signals (impulse train for BPM, synthesized chord for key)
- `tests/fixtures/test_440hz.wav` + `tests/fixtures/test_drum_loop.wav` — Audio fixtures for testing

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT attempt polyphonic audio-to-MIDI (research area, not production-ready)
- Do NOT modify the existing `audio_analysis/` module structure (extend it with new files)
- Do NOT add audio rendering/export (use Max device for that)
- Do NOT require FFmpeg or external binaries (numpy-only signal processing; use scipy.io.wavfile for WAV I/O)
- Do NOT analyze more than 60s of audio (performance bound)
- Do NOT auto-set Live tempo from BPM detection (return as information only)
- Do NOT add new pip dependencies beyond numpy/scipy already in pyproject.toml
- Do NOT modify LSP server configuration
- Do NOT add new UDP commands
- Do NOT add a `_get_clip_audio_data` handler that blocks for >5s — must handle large clips gracefully

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after + numpy-generated signal verification for each detector
- Evidence: `.omo/evidence/task-<N>-sprint-06-audio-analysis.<ext>`

## Execution strategy

### Parallel execution waves
| Wave | Focus | Todos | Est. |
|------|-------|-------|------|
| 1 | Core detection modules | 1, 2, 3, 4 | 2d |
| 2 | Audio-to-MIDI + Remote Script handler | 5, 6 | 1.5d |
| 3 | MCP tool surface | 7 | 0.5d |
| 4 | Tests + fixtures + example scripts | 8 | 1d |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. BPM detector | None | None | 2, 3, 4, 5, 6 |
| 2. Key detector | None | None | 1, 3, 4, 5, 6 |
| 3. Transient detector | None | None | 1, 2, 4, 5, 6 |
| 4. Feature extractor | None | None | 1, 2, 3, 5, 6 |
| 5. Audio-to-MIDI | None | None | 1, 2, 3, 4, 6 |
| 6. Remote Script handler | None | 7 | 1, 2, 3, 4, 5 |
| 7. MCP tools | 1, 2, 3, 4, 5, 6 | None | 8 |
| 8. Tests + fixtures | 1, 2, 3, 4, 5 | None | 7 |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Add BPM detection module (`bpm_detector.py`)
  What to do / Must NOT do:
  Create `MCP_Server/audio_analysis/bpm_detector.py` with function:
  ```python
  def detect_bpm(audio_data: np.ndarray, sample_rate: int) -> dict:
      """Returns {'bpm': float, 'confidence': float, 'alternatives': [float], 'tempo_range': str}"""
  ```
  Implementation:
  - Normalize audio to [-1.0, 1.0] float range
  - Compute onset strength envelope via spectral flux (STFT magnitude difference across frames)
  - Apply autocorrelation to onset envelope to find periodicities
  - Convert peak autocorrelation lags to BPM candidates
  - Apply half-time/double-time correction: if candidate BPM < 60, double it; if > 200, halve it
  - Return best BPM + confidence (0.0-1.0 from normalized autocorrelation peak) + up to 3 alternatives
  - Handle: 60-200 BPM range, silent input (return confidence=0), very short audio (<1s returns error)
  - scipy.signal spectrogram or STFT for onset computation
  - Must NOT: use librosa or external audio libraries (numpy/scipy only)
  - Must NOT: modify existing files in audio_analysis/

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 2, 3, 4, 5, 6
  References:
  - Spec: Sprint 06 §6.1
  - Existing module: `MCP_Server/audio_analysis/` directory structure
  - scipy.signal: stft, correlate, find_peaks
  - NumPy: np.fft, np.correlate

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.audio_analysis.bpm_detector import detect_bpm
  import numpy as np
  # 120 BPM test: impulse train every 0.5s
  sr = 44100; t = np.linspace(0, 4, int(sr*4), endpoint=False)
  signal = np.zeros_like(t)
  for beat in range(8):
      idx = int(beat * 0.5 * sr)
      if idx < len(signal): signal[idx] = 1.0
  result = detect_bpm(signal, sr)
  assert abs(result['bpm'] - 120) < 3, f'bpm={result[\"bpm\"]}'
  assert result['confidence'] > 0.5
  assert len(result['alternatives']) >= 0
  print(f'BPM detection OK: {result}')
  "
  ```
  QA scenarios:
  - HAPPY: 120 BPM impulse train → detect ~120 BPM, confidence > 0.5
  - HAPPY: 140 BPM impulse train → detect ~140 BPM
  - HAPPY: Silent input → confidence ≈ 0, bpm = 0 or None
  - FAILURE: Empty array → raises ValueError with descriptive message
  - FAILURE: Sample rate < 1000 → handles gracefully or raises ValueError
  Evidence: .omo/evidence/task-1-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add BPM detection via onset autocorrelation

- [ ] 2. Add key detection module (`key_detector.py`)
  What to do / Must NOT do:
  Create `MCP_Server/audio_analysis/key_detector.py` with function:
  ```python
  def detect_key(audio_data: np.ndarray, sample_rate: int) -> dict:
      """Returns {'key': str, 'mode': str, 'confidence': float, 'alternatives': [{'key': str, 'mode': str, 'confidence': float}]}"""
  ```
  Implementation:
  - Compute chromagram: divide spectrum into 12 pitch class bins (C, C#, D, ..., B)
  - Use FFT → map frequency bins to nearest semitone → accumulate magnitude per pitch class
  - Apply Krumhansl-Schmuckler key profiles (24 profiles: 12 major + 12 minor)
  - Correlate chroma vector with each profile → find best match
  - Temperature smoothing: average chroma over multiple windows for stability
  - Return: best key name (e.g., "C", "F#"), mode ("major"/"minor"), confidence (0.0-1.0)
  - Top 2 alternative candidates with their confidence scores
  - Key names: C, C#, D, D#, E, F, F#, G, G#, A, A#, B (use enharmonic equivalents based on mode — e.g., Db→C# for major)
  - Must NOT: use external key detection libraries (numpy/scipy only)
  - Must NOT: claim certainty on atonal/noisy material (return confidence=0 + key="Uncertain")

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 3, 4, 5, 6
  References:
  - Spec: Sprint 06 §6.2
  - Krumhansl & Schmuckler (1990) key profiles
  - Chroma feature computation: STFT → frequency-to-pitch-class mapping
  - scipy.signal: spectrogram, periodogram

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.audio_analysis.key_detector import detect_key
  import numpy as np
  # C major chord: C4(261.63) + E4(329.63) + G4(392.00)
  sr = 44100; t = np.linspace(0, 1, sr, endpoint=False)
  signal = (np.sin(2*np.pi*261.63*t) + np.sin(2*np.pi*329.63*t) + np.sin(2*np.pi*392.00*t))
  result = detect_key(signal, sr)
  assert result['key'] in ('C',) or any(a['key'] == 'C' for a in result['alternatives']), f'Expected C key candidate, got {result}'
  assert result['confidence'] >= 0
  assert len(result['alternatives']) >= 1
  print(f'Key detection OK: {result}')
  "
  ```
  QA scenarios:
  - HAPPY: Synthesized C major chord → key="C" with mode="major"
  - HAPPY: Synthesized A minor chord → key="A" with mode="minor" (or top alternative)
  - HAPPY: White noise → confidence ≈ 0, key="Uncertain"
  - FAILURE: Empty audio → raises ValueError
  - FAILURE: Very short audio (<0.25s) → handles gracefully with warning
  Evidence: .omo/evidence/task-2-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add key detection via Krumhansl-Schmuckler chroma correlation

- [ ] 3. Add transient detection module (`transient_detector.py`)
  What to do / Must NOT do:
  Create `MCP_Server/audio_analysis/transient_detector.py` with function:
  ```python
  def detect_transients(audio_data: np.ndarray, sample_rate: int) -> dict:
      """Returns {'onsets': [float], 'beat_grid': [{'time': float, 'bar': int}],
                   'onset_count': int, 'classifications': [{'time': float, 'type': str, 'centroid': float}]}"""
  ```
  Implementation:
  - Compute spectral flux onset detection function: frame-to-frame magnitude difference in STFT
  - Apply adaptive threshold (median + local moving average) to detect onset peaks
  - Return onset times in seconds (sample-accurate via interpolation)
  - Build beat grid: estimate tempo from onset intervals, align beat grid to nearest onsets
  - Return beat_grid as [{time: float, bar: int}] with bar numbers
  - Classify each onset by spectral centroid value: low (<500Hz) = "kick", mid (500-4000Hz) = "snare", high (>4000Hz) = "hat"
  - Handle: polyphonic material (multiple simultaneous onsets merge into one), variable dynamics
  - Must NOT: use librosa or external onset detectors
  - Must append all onset data to beat_grid regardless of bar alignment

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 2, 4, 5, 6
  References:
  - Spec: Sprint 06 §6.3
  - Spectral flux onset detection: Dixo(n) 2006 "Onset Detection"
  - scipy.signal: stft, find_peaks
  - Spectral centroid: weighted mean of frequencies

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.audio_analysis.transient_detector import detect_transients
  import numpy as np
  # Simple test: impulse at known positions
  sr = 44100; t = np.linspace(0, 2, int(sr*2), endpoint=False)
  signal = np.zeros_like(t)
  signal[int(0.5*sr)] = 1.0  # impulse at 0.5s
  signal[int(1.0*sr)] = 1.0  # impulse at 1.0s
  signal[int(1.5*sr)] = 1.0  # impulse at 1.5s
  result = detect_transients(signal, sr)
  assert result['onset_count'] >= 1, f'Expected >=1 onset, got {result[\"onset_count\"]}'
  assert len(result['beat_grid']) > 0, 'Expected non-empty beat_grid'
  print(f'Transient detection OK: {result[\"onset_count\"]} onsets')
  "
  ```
  QA scenarios:
  - HAPPY: Impulse train → onsets detected at impulse positions
  - HAPPY: Synthesized kick drum (low freq burst) → classified as "kick"
  - HAPPY: Silent input → empty onsets, beat_grid empty, onset_count=0
  - FAILURE: Empty array → raises ValueError
  Evidence: .omo/evidence/task-3-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add transient/onset detection with beat grid and spectral classification

- [ ] 4. Add feature extraction module (`feature_extract.py`)
  What to do / Must NOT do:
  Create `MCP_Server/audio_analysis/feature_extract.py` with function:
  ```python
  def extract_features(audio_data: np.ndarray, sample_rate: int) -> dict:
      """Returns dict with all spectral and temporal features."""
  ```
  Implementation — compute and return:
  - `spectral_centroid`: weighted mean of frequencies per frame (array + mean)
  - `spectral_rolloff`: frequency below which 85% of spectral energy is contained (array + value)
  - `spectral_flux`: frame-to-frame squared magnitude difference (array + mean)
  - `zero_crossing_rate`: rate of sign changes (scalar)
  - `rms_loudness`: RMS energy envelope per frame (array + overall dB)
  - `mfccs`: 13 MFCC coefficients (via DCT of log-mel filterbank energies using scipy)
  - Return all as dict with array fields as lists and scalar fields as floats
  - Must handle: silence gracefully (MFCC may be NaN — replace with 0.0)
  - Must NOT: use librosa (implement MFCCs via scipy.fft.dct + triangular mel filters)

  Parallelization: Wave 1 | Blocked by: None | Blocks: 7 | Can parallelize with: 1, 2, 3, 5, 6
  References:
  - Spec: Sprint 06 §6.5
  - MFCC computation: triangular mel filterbank → log energy → DCT
  - scipy.signal: spectrogram, periodogram
  - scipy.fft: dct

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.audio_analysis.feature_extract import extract_features
  import numpy as np
  sr = 44100; t = np.linspace(0, 1, sr, endpoint=False)
  signal = np.sin(2*np.pi*440*t)  # 440Hz sine
  result = extract_features(signal, sr)
  assert 'spectral_centroid' in result, 'Missing spectral_centroid'
  assert 'mfccs' in result, 'Missing mfccs'
  assert len(result['mfccs']) == 13, f'Expected 13 MFCCs, got {len(result[\"mfccs\"])}'
  assert 'rms_loudness' in result, 'Missing rms_loudness'
  assert 'zero_crossing_rate' in result, 'Missing zero_crossing_rate'
  print(f'Feature extraction OK: {list(result.keys())}')
  "
  ```
  QA scenarios:
  - HAPPY: 440Hz sine wave → spectral centroid near 440Hz, 13 MFCCs returned
  - HAPPY: White noise → high spectral centroid, high zero-crossing rate
  - HAPPY: Silence → MFCC NaN values replaced with 0.0, rms ≈ 0
  - FAILURE: Empty array → raises ValueError
  Evidence: .omo/evidence/task-4-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add spectral feature extraction (MFCC, centroid, flux, rolloff, loudness)

- [ ] 5. Add audio-to-MIDI conversion module (`audio_to_midi.py`)
  What to do / Must NOT do:
  Create `MCP_Server/audio_analysis/audio_to_midi.py` with function:
  ```python
  def audio_to_midi(audio_data: np.ndarray, sample_rate: int,
                    min_pitch: int = 36, max_pitch: int = 84) -> list[dict]:
      """Returns notes: [{pitch: int, start_time: float, duration: float, velocity: int}]"""
  ```
  Implementation (McAulay-Quatieri monophonic pitch tracking):
  - Frame-based FFT (Hann window, 2048 samples, 50% hop)
  - Peak picking: find local maxima in magnitude spectrum above noise floor threshold
  - Pitch tracking: track peak trajectories across frames (frequency + amplitude continuity)
  - Note segmentation: detect note onsets from pitch jumps (>3 semitones) or amplitude drops
  - Convert each note segment to MIDI pitch (69 = A4 = 440Hz) using 12-TET
  - Clamp pitch to [min_pitch, max_pitch] range
  - Assign velocity based on average amplitude of segment (scaled to 1-127)
  - Duration: segment end minus segment start in seconds
  - Handle: silence (return empty list), noise (may produce erratic notes — accept as limitation)
  - **Limitation**: Monophonic only — document in docstring. For polyphonic material, tracks the loudest partial.
  - Target accuracy: 90%+ for clean monophonic input (solo melody, bass, vocal)
  - Must NOT: attempt polyphonic transcription
  - Must NOT: add external pitch-tracking dependencies

  Parallelization: Wave 2 | Blocked by: None | Blocks: 7 | Can parallelize with: 6
  References:
  - Spec: Sprint 06 §6.4
  - McAulay & Quatieri (1986) "Speech Analysis/Synthesis Based on a Sinusoidal Representation"
  - MIDI pitch: 69 + 12*log2(f/440)
  - Peak interpolation: parabolic interpolation around spectral peaks for sub-bin accuracy

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.audio_analysis.audio_to_midi import audio_to_midi
  import numpy as np
  # Simple monophonic test: A4 (440Hz) for 0.5s then C5 (523.25Hz) for 0.5s
  sr = 44100; t1 = np.linspace(0, 0.5, int(sr*0.5), endpoint=False)
  t2 = np.linspace(0, 0.5, int(sr*0.5), endpoint=False)
  note1 = np.sin(2*np.pi*440*t1)  # A4
  note2 = np.sin(2*np.pi*523.25*t2)  # C5
  signal = np.concatenate([note1, note2])
  result = audio_to_midi(signal, sr)
  assert len(result) >= 1, f'Expected >=1 note, got {len(result)}'
  pitches = [n['pitch'] for n in result]
  assert 69 in pitches or 72 in pitches, f'Expected A4(69) or C5(72), got {pitches}'
  print(f'Audio-to-MIDI OK: {len(result)} notes, pitches={pitches}')
  "
  ```
  QA scenarios:
  - HAPPY: Clean A4 sine → returns single note with pitch=69
  - HAPPY: Two-note melody (A4 → C5) → returns two notes with correct pitches and sequential timing
  - HAPPY: Silence → returns empty list
  - FAILURE: Polyphonic input (chord) → returns notes but may be inaccurate (documented limitation)
  - FAILURE: Empty array → raises ValueError
  Evidence: .omo/evidence/task-5-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add monophonic audio-to-MIDI conversion (McAulay-Quatieri)

- [ ] 6. Add Remote Script clip audio data handler
  What to do / Must NOT do:
  Add `_get_clip_audio_data(track_index, clip_index) -> bytes` handler in `AbletonMCP_Remote_Script/__init__.py`:
  - Gets the specified clip from Live's song.tracks[track_index].clip_slots[clip_index].clip
  - Verify clip exists → if not, return error "clip not found"
  - Verify it's an audio clip → if MIDI clip, return error "cannot export MIDI as audio"
  - Export clip audio data via Live API (Clip.waveform or similar) at 44.1kHz 16-bit WAV format
  - Max duration: 60s (clips longer are truncated; indicate in returned data)
  - Return raw WAV bytes that can be decoded by MCP server
  - Add command dispatch entry for `get_clip_audio_data` in the handler map
  - Must NOT: block for >5s — handle large clips with chunked reading if Live API supports it
  - Must NOT: attempt audio export for MIDI clips (return clear error)
  - Must NOT: modify any existing handler signatures

  Parallelization: Wave 2 | Blocked by: None | Blocks: 7 | Can parallelize with: 5
  References:
  - Spec: Sprint 06 §6.6
  - Existing handler pattern: `AbletonMCP_Remote_Script/__init__.py` command dispatch dict
  - Live API: Clip (AudioClip.waveform, Clip.length, Clip.is_midi_clip)
  - WAV format: 44.1kHz, 16-bit, mono, little-endian

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  # Verify handler function exists and is registered
  with open('AbletonMCP_Remote_Script/__init__.py') as f:
      content = f.read()
  assert '_get_clip_audio_data' in content, '_get_clip_audio_data handler not found'
  assert 'get_clip_audio_data' in content, 'command dispatch for get_clip_audio_data not found'
  assert 'cannot export MIDI as audio' in content, 'MIDI clip error message not found'
  print('Clip audio data handler registered')
  "
  ```
  QA scenarios:
  - HAPPY: Call `_get_clip_audio_data(0, 0)` on a valid audio clip → returns WAV bytes
  - HAPPY: Clip >60s → truncated to 60s, returned with indication
  - FAILURE: Non-existent clip → returns error "clip not found"
  - FAILURE: MIDI clip → returns error "cannot export MIDI as audio"
  - FAILURE: Negative track/clip index → returns error
  Evidence: .omo/evidence/task-6-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add _get_clip_audio_data Remote Script handler for WAV export

- [ ] 7. Add MCP tool surface for audio analysis
  What to do / Must NOT do:
  Create/extend `MCP_Server/audio_analysis_tools.py` with 5 tools (following existing submodule pattern from `MCP_Server/advanced_tools.py`):
  - `detect_clip_bpm(ctx, track_index, clip_index)` → grabs audio via `_get_clip_audio_data`, runs `detect_bpm`, returns `{bpm, confidence, alternative_bpm}` as JSON string
  - `detect_clip_key(ctx, track_index, clip_index)` → grabs audio, runs `detect_key`, returns `{key, mode, confidence}`
  - `analyze_clip_audio(ctx, track_index, clip_index)` → full pipeline: BPM + key + transients + features. Caches per (track, clip) with 30s TTL. Returns comprehensive dict.
  - `convert_audio_to_midi(ctx, track_index, clip_index, target_track_index=None, min_pitch=36, max_pitch=84)` → extracts audio → runs `audio_to_midi` → creates MIDI clip on target track (or new MIDI track). Returns `{note_count, pitch_range, duration, target_track}`
  - `detect_bpm_from_file(ctx, file_path)` → loads .wav file via scipy.io.wavfile, runs `detect_bpm`. Returns same as detect_clip_bpm.

  Tool registration: `register_audio_analysis_tools(mcp, get_ableton_connection)` called from `MCP_Server/server.py` at line ~752-765.

  Must NOT: Cache stale results (use 30s TTL per (track, clip) key). Must NOT: block server startup if numpy/scipy not available (graceful import error).
  Must NOT: Expose audio data in tool output (processed features only).

  Parallelization: Wave 3 | Blocked by: 1, 2, 3, 4, 5, 6 | Blocks: None | Can parallelize with: 8
  References:
  - Spec: Sprint 06 §6.7
  - Submodule pattern: `MCP_Server/advanced_tools.py:48` register_advanced_tools
  - Server registration: `MCP_Server/server.py:752-765`
  - Cache pattern: `MCP_Server/server.py:548-615` _browser_cache

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/audio_analysis_tools.py') as f:
      content = f.read()
  assert 'def register_audio_analysis_tools' in content, 'register function not found'
  assert 'detect_clip_bpm' in content, 'detect_clip_bpm not found'
  assert 'detect_clip_key' in content, 'detect_clip_key not found'
  assert 'analyze_clip_audio' in content, 'analyze_clip_audio not found'
  assert 'convert_audio_to_midi' in content, 'convert_audio_to_midi not found'
  assert 'detect_bpm_from_file' in content, 'detect_bpm_from_file not found'
  print('All 5 MCP tools registered in audio_analysis_tools.py')
  "
  ```
  ```bash
  # Verify registered in server.py
  grep -c "register_audio_analysis_tools" MCP_Server/server.py
  ```
  QA scenarios:
  - HAPPY: Call `detect_clip_bpm(0, 0)` on track with audio clip → returns {bpm, confidence, alternative_bpm}
  - HAPPY: Call `analyze_clip_audio(0, 0)` → returns full analysis with all sections
  - HAPPY: Call `convert_audio_to_midi(0, 0)` → creates MIDI clip, returns note count + pitch range
  - HAPPY: Call `detect_bpm_from_file("test.wav")` with valid WAV → returns BPM
  - FAILURE: Call `detect_clip_bpm(0, 0)` on MIDI track → returns error
  - FAILURE: Call `detect_bpm_from_file("nonexistent.wav")` → file not found error
  - FAILURE: Call `analyze_clip_audio(999, 0)` → track index out of range error
  Evidence: .omo/evidence/task-7-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add 5 MCP tools for BPM, key, transient, feature, and audio-to-MIDI

- [ ] 8. Add test fixtures and unit tests
  What to do / Must NOT do:
  Create test infrastructure:
  - `tests/fixtures/test_440hz.wav`: 2-second 440Hz sine wave at 44.1kHz, 16-bit mono WAV (generated via script)
  - `tests/fixtures/test_drum_loop.wav`: 4-bar drum loop at 120 BPM, generated programmatically (kick on 1, snare on 2&4, hats on 8ths)
  - `tests/test_audio_analysis.py`: Unit tests using numpy-generated signals (no fixture files needed for basic tests):
    - `test_bpm_detection_basic`: 120 BPM impulse train → bpm ≈ 120
    - `test_bpm_detection_half_time`: 60 BPM → correct detection or double-time correction
    - `test_bpm_detection_silence`: silence → confidence ≈ 0
    - `test_key_detection_c_major`: C major chord → key="C" in top candidates
    - `test_key_detection_a_minor`: A minor chord → key="A" minor in top candidates
    - `test_key_detection_noise`: white noise → low confidence, key="Uncertain"
    - `test_transient_detection_impulses`: impulse train → correct onset times
    - `test_transient_classification`: synthesized kick → classified as "kick"
    - `test_feature_extraction_sine`: 440Hz sine → centroid ≈ 440Hz
    - `test_feature_extraction_mfcc_count`: returns exactly 13 MFCCs
    - `test_audio_to_midi_single_note`: A4 sine → pitch=69
    - `test_audio_to_midi_two_notes`: two sequential pitches → two notes
    - `test_audio_to_midi_silence`: silence → empty list
  - `scripts/analysis/analyze_clip_demo.py`: Demo script that takes track+clip index from CLI and prints full analysis
  - `scripts/analysis/bpm_from_file_demo.py`: Demo script that takes a .wav path and prints BPM

  Must NOT: Require Ableton Live to run (all tests use numpy-generated signals)
  Must NOT: Use pytest (follow project convention of standalone scripts)
  Must NOT: Include large audio files in repo (generated programmatically by test scripts)

  Parallelization: Wave 4 | Blocked by: 1, 2, 3, 4, 5 | Blocks: None | Can parallelize with: 7
  References:
  - Spec: Sprint 06 §Key Files
  - Existing test pattern: `scripts/test/test_connection.py`
  - scipy.io.wavfile: write() for fixture generation
  - numpy: sin, linspace, zeros for signal generation

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  # Verify test file exists and import works
  from tests.test_audio_analysis import *
  print('Test imports OK')
  "
  ```
  ```bash
  # Generate and verify fixtures
  python -c "
  import numpy as np
  from scipy.io import wavfile
  import os
  for fixture in ['tests/fixtures/test_440hz.wav', 'tests/fixtures/test_drum_loop.wav']:
      assert os.path.exists(fixture), f'{fixture} not found'
      sr, data = wavfile.read(fixture)
      assert sr == 44100, f'Expected 44100, got {sr}'
      print(f'{fixture}: {len(data)} samples @ {sr}Hz')
  "
  ```
  ```bash
  # Run all tests (standalone)
  python tests/test_audio_analysis.py
  ```
  QA scenarios:
  - HAPPY: Run `test_bpm_detection_basic` → passes
  - HAPPY: Run `test_key_detection_c_major` → passes
  - HAPPY: Run `test_audio_to_midi_single_note` → passes
  - HAPPY: Fixture files exist at expected paths with correct sample rate
  - FAILURE: Incomplete detection module → test failure with clear message
  Evidence: .omo/evidence/task-8-sprint-06-audio-analysis.txt
  Commit: Y | feat(audio-analysis): add test fixtures, unit tests, and demo scripts for audio analysis pipeline

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: Verify all 8 deliverables exist (6 modules, 1 handler in __init__.py, 1 tools file), all scope boundaries respected (no polyphonic, no FFmpeg, no audio export)
- [ ] F2. Code quality review: All .py files pass `python -c "compile(open(f).read(), f, 'exec')"`, no syntax errors. All imports are clean (numpy/scipy only).
- [ ] F3. Signal processing smoke test: Run all 12+ test cases with numpy-generated signals — verify every detector produces valid output for known inputs
- [ ] F4. Scope fidelity: grep for Must NOT violations (no librosa, no FFmpeg, no polyphonic mentions in implementation, no audio_export, no deps beyond numpy/scipy)

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(audio-analysis): add BPM detection via onset autocorrelation
- feat(audio-analysis): add key detection via Krumhansl-Schmuckler chroma correlation
- feat(audio-analysis): add transient/onset detection with beat grid and spectral classification
- feat(audio-analysis): add spectral feature extraction (MFCC, centroid, flux, rolloff, loudness)
- feat(audio-analysis): add monophonic audio-to-MIDI conversion (McAulay-Quatieri)
- feat(audio-analysis): add _get_clip_audio_data Remote Script handler for WAV export
- feat(audio-analysis): add 5 MCP tools for BPM, key, transient, feature, and audio-to-MIDI
- feat(audio-analysis): add test fixtures, unit tests, and demo scripts for audio analysis pipeline

No squashing — each commit is independently testable. Tags: none.

## Success criteria
All 6 detection modules exist and import without errors (numpy/scipy only)
BPM detection: ±1 BPM for steady impulse trains, ±3 BPM for complex audio
Key detection: correct key identified (in top 2 candidates) for synthesized chords
Transient detection: onset times accurate within ±20ms for impulse signals
Feature extraction: returns spectral centroid, rolloff, flux, ZCR, RMS, and 13 MFCCs
Audio-to-MIDI: produces correct MIDI pitches for clean monophonic input (90%+ accuracy)
Remote Script handler: exports audio clips as 44.1kHz 16-bit WAV, errors on MIDI clips
All 5 MCP tools registered and callable via `@mcp.tool()`
Test suite passes: 12+ test cases using only numpy-generated signals (no Live dependency)
Demo scripts run and produce readable output
