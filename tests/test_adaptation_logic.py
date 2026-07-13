"""Tests for adaptation logic"""

from agentic_mix.state import AudioAnalysisData


def test_decide_adaptations_energy_boost():
    """Quiet RMS triggers energy boost for next section"""

    from agentic_mix.adaptation_logic import decide_adaptations

    current_analysis = AudioAnalysisData(
        timestamp=1.0, rms=0.2,
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-20.0
    )

    current_section = {"index": 0, "energy_level": 3.0, "mixing_technique": "none"}
    next_section = {"index": 1, "energy_level": 4.0, "mixing_technique": "none"}
    config = {"tempo": 120, "duration_minutes": 4, "genre": "techno"}

    adaptations = decide_adaptations(current_analysis, current_section, next_section, config)

    assert any(
        a["type"] == "energy_boost" and a["target_section"] == 1
        for a in adaptations
    )


def test_decide_adaptations_clipping_protection():
    """Clipping RMS triggers energy reduction AND technique change"""

    from agentic_mix.adaptation_logic import decide_adaptations

    current_analysis = AudioAnalysisData(
        timestamp=2.0, rms=0.97,
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-6.0
    )

    current_section = {"index": 10, "energy_level": 8.5, "mixing_technique": "dub_drop"}
    next_section = {"index": 11, "energy_level": 7.0, "mixing_technique": "dub_drop"}
    config = {"tempo": 120}

    adaptations = decide_adaptations(current_analysis, current_section, next_section, config)

    assert any(a["type"] == "energy_reduct" for a in adaptations)
    assert any(
        a["type"] == "technique_change" and a.get("to_technique") == "volume_automation"
        for a in adaptations
    )


def test_decide_adaptations_spectral_balance():
    """Bright spectrum triggers filter adjustment down"""

    from agentic_mix.adaptation_logic import decide_adaptations

    current_analysis = AudioAnalysisData(
        timestamp=3.0, rms=0.6,
        spectral_centroid_hz=8000.0, spectral_rolloff_hz=5000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-16.0
    )

    current_section = {"index": 5, "energy_level": 5.0, "mixing_technique": "none"}
    next_section = {"index": 6, "energy_level": 5.0, "mixing_technique": "none"}
    config = {"tempo": 120}

    adaptations = decide_adaptations(current_analysis, current_section, next_section, config)

    assert any(
        a["type"] == "filter_adjust_down" and a["target_section"] == 6
        for a in adaptations
    )


def test_is_valid_snapshot_all_zero():
    """Reject all-zero readings"""

    from agentic_mix.adaptation_logic import is_valid_snapshot

    snapshot = AudioAnalysisData(
        timestamp=1.0, rms=0.0, spectral_centroid_hz=0.0, spectral_rolloff_hz=0.0,
        key=None, key_confidence=None, bpm=0.0, beat=0.0, loudness_lufs=0.0
    )

    assert not is_valid_snapshot(snapshot)


def test_is_valid_snapshot_valid():
    """Accept normal readings"""

    from agentic_mix.adaptation_logic import is_valid_snapshot

    snapshot = AudioAnalysisData(
        timestamp=1.0, rms=0.5, spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-18.0
    )

    assert is_valid_snapshot(snapshot)


def test_is_valid_snapshot_invalid_rms():
    """Reject out-of-range RMS"""

    from agentic_mix.adaptation_logic import is_valid_snapshot

    snapshot = AudioAnalysisData(
        timestamp=1.0, rms=1.5,
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, bpm=120.0, beat=1.0, loudness_lufs=-18.0
    )

    assert not is_valid_snapshot(snapshot)


def test_is_valid_snapshot_low_key_confidence():
    """Snapshot with low key confidence clears key field"""

    from agentic_mix.adaptation_logic import is_valid_snapshot

    snapshot = AudioAnalysisData(
        timestamp=1.0, rms=0.5, spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key="Am", key_confidence=0.3,
        bpm=120.0, beat=1.0, loudness_lufs=-18.0
    )

    result = is_valid_snapshot(snapshot)
    assert result
    assert snapshot["key"] is None
