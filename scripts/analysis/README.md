# VST Audio Analysis Scripts

This directory contains tools for analyzing VST plugin parameters in Ableton Live.

## Scripts

### poll_plugin_params.py

Polls VST plugin parameters from Ableton Live at a configurable rate, logging all readings to a CSV file.

#### Features

- **TCP Connection**: Connects to Ableton Remote Script on port 9877
- **Configurable Rate**: Polls at 10-20 Hz (default: 15 Hz)
- **Parameter Caching**: Only logs when parameters change (configurable)
- **Error Handling**: Gracefully handles connection errors, timeouts, and plugin not found
- **CSV Logging**: Appends readings with ISO 8601 timestamps
- **Graceful Exit**: Ctrl+C handling with summary statistics
- **Progress Display**: Shows readings count, elapsed time, and actual Hz every 50 polls

#### Usage

```bash
# Basic usage
python poll_plugin_params.py --plugin=YouleanLoudnessMeter --track=0 --device=0 --rate=15 --duration=60

# Example: Poll Loudness Meter for 1 minute at 15 Hz
python poll_plugin_params.py --plugin=YouleanLoudnessMeter --track=0 --device=0 --rate=15 --duration=60

# Example: Poll at 10 Hz for 5 minutes
python poll_plugin_params.py --plugin=LoudnessMeter --track=2 --device=0 --rate=10 --duration=300

# Example: Infinite polling (Ctrl+C to stop)
python poll_plugin_params.py --plugin=LoudnessMeter --track=0 --device=0 --rate=15 --duration=0
```

#### Arguments

- `--plugin`: Plugin name (for logging, e.g., YouleanLoudnessMeter)
- `--track`: Track index containing the plugin (required)
- `--device`: Device index on the track (required)
- `--rate`: Update rate in Hz (10-20, default: 15)
- `--duration`: Duration in seconds (0 = infinite, default: 0)
- `--output-dir`: Output directory for log files (default: logs)
- `-h, --help`: Show help message

#### Output

Creates a CSV log file with the following format:

```csv
timestamp,track_index,device_index,parameter_index,parameter_name,value,min,max
2026-02-10T20:43:00Z,0,0,0,Momentary LUFS,-14.5,-70.0,5.0
2026-02-10T20:43:067Z,0,0,0,Momentary LUFS,-14.2,-70.0,5.0
```

The log file is named: `poll_plugin_params_YYYYMMDD_HHMMSS.log`

#### Exit Codes

- `0`: Success (normal exit or Ctrl+C)
- `1`: Connection error (unable to connect to Ableton)
- `2`: Invalid rate (not 10-20 Hz)
- `3`: Failed to create output directory

#### Error Handling

The script handles the following error cases:

- **Connection timeout**: Retries up to 3 times before exiting
- **Connection refused**: Reports that Ableton Remote Script is not running
- **Track index out of range**: Reports error and exits
- **Device index out of range**: Reports error and exits
- **Socket timeout**: Warns and retries, exits after 3 consecutive timeouts
- **Plugin returns no parameters**: Logs warning, continues polling
- **Write errors**: Reports error, continues if possible

#### Performance Notes

- **Parameter Caching**: By default, the script only logs when parameters actually change, reducing disk I/O
- **Progress Display**: Every 50 polls, the script shows current statistics
- **Summary**: On exit, displays:
  - Total readings collected
  - Total duration
  - Average update rate achieved
  - Target update rate
  - Average poll time in milliseconds

#### Requirements

- Python 3.10+
- Ableton Live with Remote Script loaded on port 9877
- Write access to output directory

## Log Files

All log files are stored in the `logs/` directory (or custom output directory specified with `--output-dir`).

Log files are named with timestamps: `poll_plugin_params_YYYYMMDD_HHMMSS.log`
