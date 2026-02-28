# Dub Techno Infinite DJ Automation

These scripts keep the DJ mix running even when OpenCode stops unexpectedly.

## Quick Start

### Option 1: Batch Script (Simplest)
```cmd
cd sets\dub_techno_2h
run_dj_automation.bat
```

### Option 2: PowerShell (Recommended)
```powershell
cd sets\dub_techno_2h
.\run_dj_automation.ps1
```

### Option 3: Python (Most Features)
```bash
cd sets\dub_techno_2h
python infinite_dj_automation.py
```

## How It Works

All scripts repeatedly call `opencode run` with DJ commands to:
1. Fire different clips on each track
2. Adjust volumes dynamically
3. Evolve patterns over time

## Configuration

### PowerShell Script
Edit these parameters at the top of `run_dj_automation.ps1`:
```powershell
$IntervalSeconds = 30    # Time between commands
$MaxVariations = 10000  # Max variations before restart
$LogFile = "dj_automation.log"
```

### Python Script
Edit these constants in `infinite_dj_automation.py`:
```python
INTERVAL_SECONDS = 30
MAX_VARIATIONS = 1000
```

### Batch Script
Edit the timeout value in `run_dj_automation.bat`:
```batch
timeout /t 30 /nobreak >nul
```

## Stopping the Automation

Press **Ctrl+C** to stop any of the scripts.

## Log Files

All scripts create log files:
- `dj_automation.log` - PowerShell and Python logs
- Console output shows current variation

## Rules Enforced

1. **Bass**: Volume 0.85-0.95 (main focus)
2. **Lead**: Max volume 0.5
3. **Stabs**: Volume 0.45, change rarely
4. **One clip change at a time** (DJ rule)

## Troubleshooting

If the automation stops working:
1. Check that `opencode` is in your PATH
2. Make sure Ableton is running
3. Check the log file for errors
4. Restart the script

## Advanced: Custom Commands

Edit the `$DJ_COMMANDS` array in PowerShell or `DJ_COMMANDS` list in Python to customize the automation.
