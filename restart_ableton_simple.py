#!/usr/bin/env python
"""Simple Ableton Live restart script - handles recovery dialog"""

import subprocess
import time
import socket
import sys
import ctypes

sys.path.insert(0, 'C:/Users/Tobias/git/ableton-mcp-extended')

def send_enter():
    """Send Enter key to dismiss any dialogs using Windows API."""
    try:
        # Virtual key code for Enter
        VK_RETURN = 0x0D
        # Key down
        ctypes.windll.user32.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.1)
        # Key up
        ctypes.windll.user32.keybd_event(VK_RETURN, 0, 2, 0)
        time.sleep(0.3)
    except Exception as e:
        print(f"  Warning: Could not send Enter key: {e}")

def main():
    print("Step 1: Killing Ableton...")
    
    # Kill Ableton
    subprocess.run(['wmic', 'process', 'where', "name='Ableton Live 12 Suite.exe'", 
                   'call', 'terminate'], capture_output=True, timeout=5)
    time.sleep(2)
    
    print("Step 2: Starting Ableton...")
    proc = subprocess.Popen([
        r"C:\ProgramData\Ableton\Live 12 Suite\Program\Ableton Live 12 Suite.exe"
    ])
    
    # Wait for Ableton window to appear
    print("Step 3: Waiting for Ableton window...")
    time.sleep(10)
    
    # Send Enter to dismiss any recovery dialog
    print("Step 4: Dismissing any recovery dialog...")
    send_enter()
    time.sleep(2)
    
    # Sometimes there's a second dialog
    send_enter()
    time.sleep(2)
    
    print("Step 5: Waiting for Remote Script (port 9877)...")
    max_wait = 30
    for attempt in range(max_wait):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(('localhost', 9877))
                print(f"  Port 9877 is listening! (after {attempt+1} checks)")
                
                # Test connection
                from MCP_Server.server import get_ableton_connection
                ableton = get_ableton_connection()
                result = ableton.send_command('get_session_info', {})
                print(f"  Connection verified! Tempo: {result.get('tempo', 'N/A')} BPM")
                print("\nAbleton is ready!")
                return 0
        except:
            time.sleep(1)
            if (attempt + 1) % 5 == 0:
                print(f"  Still waiting... ({attempt+1}/{max_wait})")
    
    print(f"\nPort 9877 not ready after {max_wait} seconds")
    return 1

if __name__ == "__main__":
    sys.exit(main())
