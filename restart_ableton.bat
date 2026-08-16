@echo off
setlocal

:: Ableton Live Restart Script
:: This script kills Ableton Live, waits, and restarts it
:: Usage: restart_ableton.bat [wait_seconds]

set WAIT_TIME=15
if not "%1"=="" set WAIT_TIME=%1%

echo Killing Ableton Live...
taskkill /F /IM "Ableton Live 12 Suite.exe" >nul 2>&1
timeout /T 3 /NOBREAK >nul

:: Wait for process to fully terminate
echo Waiting 3 seconds for cleanup...
timeout /T 3 /NOBREAK >nul

:: Check if port 9877 is free
set PORT_FREE=0
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9877" ^| findstr LISTENING') do (
    set PORT_FREE=1
)

if %PORT_FREE%==1 (
    echo Port 9877 still in use, waiting longer...
    timeout /T 5 /NOBREAK >nul
)

echo Starting Ableton Live 12 Suite...
start "" "C:\ProgramData\Ableton\Live 12 Suite\Program\Ableton Live 12 Suite.exe"

echo Waiting %WAIT_TIME% seconds for Remote Script to initialize...
timeout /T %WAIT_TIME% /NOBREAK >nul

echo.
echo Ableton Live should now be ready!
echo Check port 9877:
netstat -ano | findstr ":9877" | findstr LISTENING

if %ERRORLEVEL% EQU 0 (
    echo Remote Script is listening on port 9877
) else (
    echo WARNING: Remote Script may not be ready yet
)

endlocal
