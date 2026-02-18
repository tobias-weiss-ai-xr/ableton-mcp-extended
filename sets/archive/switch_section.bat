@echo off
echo DUB SONG - SECTION SWITCHER
echo ========================================
echo.
echo Select a section to play:
echo.
echo 1. INTRO (Minimal, spacey)
echo 2. BUILDUP (Adding energy)
echo 3. DROP (Maximum energy)
echo 4. BREAKDOWN (Space and atmosphere)
echo 5. FULL DROP (All elements)
echo.
set /p choice="Enter section number (1-5): "

if "%choice%"=="1" (
    python switch_section.py intro
) else if "%choice%"=="2" (
    python switch_section.py buildup
) else if "%choice%"=="3" (
    python switch_section.py drop
) else if "%choice%"=="4" (
    python switch_section.py breakdown
) else if "%choice%"=="5" (
    python switch_section.py fulldrop
) else (
    echo Invalid choice!
)
echo.
pause