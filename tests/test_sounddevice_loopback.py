"""
Test script for VB-Cable WASAPI loopback detection on Windows.

Tests:
1. VB-Cable detection with enumerate available devices
2. Find VB-Cable device index
3. Test capture 1 second at different sample rates
4. Verify capture works

Usage:
    python tests/test_sounddevice_loopback.py

Requirements:
    pip install sounddevice numpy
"""

import platform
import sys

import sounddevice as sd


def find_vb_cable_index() -> int | None:
    """Enumerate devices and find VB-Cable INPUT device (CABLE Output) for capture."""
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        name = dev.get("name", "")
        if isinstance(name, str):
            nm = name.upper()
            # Look for VB-Audio/CABLE devices
            if "VB-AUDIO" in nm or "CABLE" in nm:
                # We need an INPUT device (CABLE Output) to capture audio
                # NOT an output device (CABLE Input) which is for sending audio
                if dev.get("max_input_channels", 0) > 0:
                    print(f"Found VB-Cable INPUT device: [{idx}] {name}")
                    return idx
    return None


def test_vb_cable_detection():
    """Test that VB-Cable can be detected."""
    print("\n=== VB-Cable Detection Test ===")

    vb_index = find_vb_cable_index()

    if vb_index is None:
        print("VB-Audio Cable not found.")
        print("Install from: https://vb-audio.com/Cable/")
        print("After installation, restart your computer.")
        return False

    print(f"VB-Cable detected at device index: {vb_index}")

    # Get device info
    dev_info = sd.query_devices(vb_index)
    print(f"Device name: {dev_info['name']}")
    print(f"Max input channels: {dev_info['max_input_channels']}")
    print(f"Max output channels: {dev_info['max_output_channels']}")
    print(f"Default samplerate: {dev_info['default_samplerate']}")

    return True


def test_audio_capture():
    """Test capturing audio from VB-Cable at different sample rates."""
    print("\n=== Audio Capture Test ===")

    vb_index = find_vb_cable_index()

    if vb_index is None:
        print("SKIP: VB-Audio Cable not found.")
        print("Install from: https://vb-audio.com/Cable/")
        return None

    # Test capture at common sample rates
    sample_rates = [44100, 48000]
    success_rate = None

    for rate in sample_rates:
        try:
            print(f"\nTesting capture at {rate} Hz...")

            frames = rate // 4  # 0.25 seconds of audio

            with sd.InputStream(
                samplerate=rate,
                channels=1,
                dtype="float32",
                blocksize=2048,
                device=vb_index,
            ) as stream:
                data, overflowed = stream.read(frames)

                if data is not None and len(data) >= frames:
                    print(f"CAPTURE_OK at {rate} Hz - captured {len(data)} frames")
                    print(f"  Overflow: {overflowed}")
                    print(f"  Data shape: {data.shape}")
                    print(f"  Peak amplitude: {abs(data).max():.4f}")
                    success_rate = rate
                    break
                else:
                    print(f"CAPTURE_FAIL at {rate} Hz - insufficient data")
                    continue

        except sd.PortAudioError as e:
            print(f"CAPTURE_ERROR at {rate} Hz: {e}")
            continue
        except Exception as e:
            print(f"UNEXPECTED_ERROR at {rate} Hz: {e}")
            continue

    if success_rate is None:
        print("\nAll sample rates failed. Possible issues:")
        print("  - VB-Cable not properly installed")
        print("  - No audio playing through VB-Cable")
        print("  - Audio settings misconfigured")
        return False

    print(f"\nCapture successful at {success_rate} Hz")
    return True


def test_device_enumeration():
    """List all available audio devices for debugging."""
    print("\n=== Available Audio Devices ===")

    devices = sd.query_devices()
    print(f"\nTotal devices: {len(devices)}")

    print("\n--- Input Devices ---")
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            print(
                f"  [{idx}] {dev['name']} (in: {dev['max_input_channels']}, sr: {dev['default_samplerate']})"
            )

    print("\n--- Output Devices ---")
    for idx, dev in enumerate(devices):
        if dev.get("max_output_channels", 0) > 0:
            print(
                f"  [{idx}] {dev['name']} (out: {dev['max_output_channels']}, sr: {dev['default_samplerate']})"
            )


def main():
    """Run all tests."""
    print("=" * 60)
    print("Sounddevice WASAPI Loopback Test")
    print("=" * 60)

    # Check platform
    if platform.system() != "Windows":
        print(
            f"WARNING: This test is designed for Windows. Current platform: {platform.system()}"
        )

    # Run tests
    test_device_enumeration()

    detection_ok = test_vb_cable_detection()

    if detection_ok:
        capture_ok = test_audio_capture()

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"  VB-Cable Detection: {'PASS' if detection_ok else 'FAIL'}")
        print(f"  Audio Capture: {'PASS' if capture_ok else 'FAIL/SKIP'}")

        if detection_ok and capture_ok:
            print("\nAll tests passed! Audio analysis should work correctly.")
            return 0
        else:
            print("\nSome tests failed. See above for details.")
            return 1
    else:
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("  VB-Cable Detection: FAIL")
        print("\nVB-Cable must be installed before audio analysis can work.")
        print("Download from: https://vb-audio.com/Cable/")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(130)
    finally:
        # Cleanup sounddevice
        sd._terminate()
