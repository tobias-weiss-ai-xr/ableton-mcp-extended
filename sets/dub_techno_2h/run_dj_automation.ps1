# Infinite Dub Techno DJ Automation Script
# PowerShell version with logging and error handling

param(
    [int]$IntervalSeconds = 30,
    [int]$MaxVariations = 10000,
    [string]$LogFile = "dj_automation.log"
)

# Logging function
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# DJ commands to execute
$DJ_COMMANDS = @(
    "fire_clip track_index=1 clip_index=0",
    "fire_clip track_index=1 clip_index=1",
    "fire_clip track_index=1 clip_index=4",
    "fire_clip track_index=1 clip_index=5",
    "fire_clip track_index=1 clip_index=6",
    "fire_clip track_index=2 clip_index=1",
    "fire_clip track_index=2 clip_index=2",
    "fire_clip track_index=2 clip_index=3",
    "fire_clip track_index=2 clip_index=4",
    "fire_clip track_index=6 clip_index=0",
    "fire_clip track_index=6 clip_index=1",
    "fire_clip track_index=6 clip_index=2",
    "fire_clip track_index=6 clip_index=3",
    "fire_clip track_index=6 clip_index=4",
    "fire_clip track_index=6 clip_index=5",
    "fire_clip track_index=4 clip_index=0",
    "fire_clip track_index=4 clip_index=1",
    "fire_clip track_index=4 clip_index=3",
    "set_track_volume track_index=1 volume=0.90",
    "set_track_volume track_index=1 volume=0.92",
    "set_track_volume track_index=1 volume=0.88",
    "set_track_volume track_index=6 volume=0.45",
    "set_track_volume track_index=6 volume=0.48",
    "set_track_volume track_index=6 volume=0.42",
    "set_track_volume track_index=2 volume=0.55",
    "set_track_volume track_index=2 volume=0.60",
    "set_master_volume volume=0.82",
    "set_master_volume volume=0.85"
)

# Main loop
$variationCount = 0

Write-Host ""
Write-Host "==============================================="
Write-Host "  DUB TECHNO INFINITE DJ AUTOMATION"
Write-Host "  PowerShell Edition"
Write-Host "  Press Ctrl+C to stop"
Write-Host "==============================================="
Write-Host ""

try {
    while ($variationCount -lt $MaxVariations) {
        # Select random commands (3-5 at a time)
        $numCommands = Get-Random -Minimum 3 -Maximum 6
        $selectedCommands = $DJ_COMMANDS | Get-Random -Count $numCommands
        
        # Build the prompt
        $commandsStr = $selectedCommands -join "`n"
        $prompt = "You are the DJ. Execute these commands and continue the mix:`n`n$commandsStr`n`nKeep the mix evolving. Rules:`n- Bass: Volume 0.85-0.95 (main focus)`n- Lead: Max volume 0.5`n- Stabs: Volume 0.45, change rarely`n- Evolve all patterns over time`n`nCurrent variation: $variationCount"

        Write-Log "Variation $variationCount - Executing $numCommands commands..."
        
        # Run opencode
        try {
            $result = & opencode run $prompt 2>&1
            Write-Log "Command executed successfully"
        }
        catch {
            Write-Log "Error: $_"
        }
        
        $variationCount++
        
        # Wait before next command
        $waitTime = Get-Random -Minimum ($IntervalSeconds - 10) -Maximum ($IntervalSeconds + 10)
        Write-Log "Waiting $waitTime seconds..."
        Start-Sleep -Seconds $waitTime
    }
    
    Write-Log "Reached $MaxVariations variations. Restarting..."
    $variationCount = 0
}
catch [KeyboardInterrupt] {
    Write-Log "Automation stopped by user at variation $variationCount"
}
catch {
    Write-Log "Error: $_"
    Write-Log "Restarting in 10 seconds..."
    Start-Sleep -Seconds 10
    & $PSCommandPath
}
