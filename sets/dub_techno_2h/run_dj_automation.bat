@echo off
REM Infinite Dub Techno DJ Automation
REM This script keeps calling opencode to run the DJ automation

echo ================================================
echo   DUB TECHNO INFINITE DJ AUTOMATION
echo   Press Ctrl+C to stop
echo ================================================
echo.

:loop
echo [%date% %time%] Running DJ automation...
opencode run "You are the DJ. Mix the dub techno track and evolve all patterns over time. Focus on: Bass volume 0.85-0.95 (main focus), Lead max 0.5, Stabs volume 0.45 change rarely. Continue from variation 250+. Execute 10 clip fires and parameter changes."
if %errorlevel% neq 0 (
    echo [%date% %time%] Command failed, waiting 5 seconds...
    timeout /t 5 /nobreak >nul
)
echo [%date% %time%] Waiting 30 seconds before next automation...
timeout /t 30 /nobreak >nul
goto loop
