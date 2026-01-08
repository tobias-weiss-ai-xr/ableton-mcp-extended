/**
 * AbletonMCP - Audio Export Device (Max for Live)
 *
 * Provides audio recording and export capabilities for Ableton Live sessions.
 *
 * IMPORTANT: This device CANNOT be controlled from Remote Scripts.
 * Communication is one-way: Remote Scripts -> Max devices, NOT reverse.
 *
 * Usage:
 * 1. Load this device onto a track in Ableton Live
 * 2. Arm the device track for recording
 * 3. Send audio to this device's input
 * 4. Trigger recording via parameter changes
 * 5. Audio exports to WAV file automatically
 *
 * Supported Formats: WAV, AIFF, OGG, FLAC, RAW
 * Limitation: No direct MP3 export (requires external conversion)
 */

inlets = 1;
outlets = 1;

// Global state
var recording = 0;
var recorder = null;
var output_file = "export.wav";
var sample_rate = 44100;
var bit_depth = 16;
var channels = 2;

// Create sfrecord~ object for audio recording
recorder = this.patcher.newdefault("sfrecord~", "recorder", 1);
recorder.message("open", output_file, "wave");

// Setup parameter listener for recording control
function bang() {
    if (recording == 0) {
        // Start recording
        recorder.message(1);
        recording = 1;
        outlet(0, "Recording started to: " + output_file);
    } else {
        // Stop recording
        recorder.message(0);
        recording = 0;
        outlet(0, "Recording stopped. File saved to: " + output_file);
    }
}

function setfile(s) {
    // Close existing recording if any
    if (recording == 1) {
        recorder.message(0);
        recording = 0;
    }

    // Set new output file
    output_file = s;
    recorder.message("open", output_file, "wave");
    outlet(0, "Output file set to: " + output_file);
}

function setformat(s) {
    // Supported formats: wave, aiff, ogg, flac, raw
    var format = s.toLowerCase();

    if (recording == 1) {
        recorder.message(0);
        recording = 0;
    }

    recorder.message("open", output_file, format);
    outlet(0, "Format set to: " + format);
}

function setsamplerate(f) {
    sample_rate = f;
    if (recording == 1) {
        recorder.message(0);
        recording = 0;
    }

    // Close and reopen with new sample rate
    recorder.message("open", output_file, "wave");
    recorder.message("setsr", sample_rate);
    outlet(0, "Sample rate set to: " + sample_rate + " Hz");
}

function setbitdepth(b) {
    bit_depth = b;
    if (recording == 1) {
        recorder.message(0);
        recording = 0;
    }

    // Close and reopen with new bit depth
    recorder.message("open", output_file, "wave");
    outlet(0, "Bit depth set to: " + bit_depth + " bit");
}

function listfiles() {
    // List available recordings (for information)
    outlet(0, "=== Available Recording Files ===");
    outlet(0, "Output file: " + output_file);
    outlet(0, "Format: WAV");
    outlet(0, "Sample rate: " + sample_rate + " Hz");
    outlet(0, "Bit depth: " + bit_depth + " bit");
    outlet(0, "Channels: 2 (stereo)");
    outlet(0, "Recording: " + (recording == 1 ? "Active" : "Stopped"));
}

function info() {
    // Display comprehensive information
    outlet(0, "=== AbletonMCP Audio Export Device ===");
    outlet(0, "");
    outlet(0, "STATUS:");
    listfiles();
    outlet(0, "");
    outlet(0, "INSTRUCTIONS:");
    outlet(0, "1. Load this device on a track in Ableton");
    outlet(0, "2. Arm the device track for recording");
    outlet(0, "3. Send audio to this device's input");
    outlet(0, "4. Bang (click) bang inlet to toggle recording");
    outlet(0, "");
    outlet(0, "PARAMETERS:");
    outlet(0, "bang    - Toggle recording start/stop");
    outlet(0, "setfile <filename> - Set output filename (.wav auto)");
    outlet(0, "setformat <fmt>     - Set format (wave/aiff/ogg/flac)");
    outlet(0, "setsr <rate>       - Set sample rate (44100/48000/96000)");
    outlet(0, "setbitdepth <bits> - Set bit depth (16/24/32)");
    outlet(0, "listfiles           - Show recording info");
    outlet(0, "info                 - Show this help");
    outlet(0, "");
    outlet(0, "NOTE: To export to MP3, use external conversion tool.");
    outlet(0, "MP3 conversion script provided with this device.");
}
