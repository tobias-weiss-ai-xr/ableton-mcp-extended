@echo off
echo DUB SONG - AUTOMATED RECORDING
echo ========================================
echo.
echo This script will:
echo   - Play all sections automatically
echo   - Time each section correctly
echo   - Complete in exactly 5 minutes
echo.
echo PREPARATION:
echo   1. Load instruments in Ableton
echo   2. Check track levels
echo   3. Press TAB for Session View
echo   4. Click Record on Master track
echo   5. Press Space to start recording
echo.
set /p ready="Ready? (press Enter when Ableton is recording)..."

echo.
echo Starting automated playback...
echo ========================================

python record_dub_song_automated.py

echo.
echo ========================================
echo RECORDING COMPLETE!
echo.
echo Press Space in Ableton to stop recording
echo.
pause