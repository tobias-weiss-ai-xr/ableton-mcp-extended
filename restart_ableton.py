#!/usr/bin/env python
"""
Automated Ableton Live restart with Remote Script verification.

Usage:
    python restart_ableton.py [wait_seconds]

Example:
    python restart_ableton.py 20  # Wait 20 seconds after launch
"""

import subprocess
import time
import sys
import socket
import requests

def kill_ableton():
    """Kill Ableton Live process."""
    print("🛑 Killing Ableton Live...")
    # Try WMIC first
    try:
        subprocess.run(
            ['wmic', 'process', 'where', "name='Ableton Live 12 Suite.exe'", 'call', 'terminate'],
            timeout=5, capture_output=True, check=False
        )
    except:
        pass
    
    # Also try taskkill as fallback
    try:
        subprocess.run(
            ['taskkill', '/F', '/IM', 'Ableton Live 12 Suite.exe'],
            timeout=5, capture_output=True, check=False
        )
    except:
        pass
    
    print("✅ Ableton kill command sent")

def wait_for_port_free(port=9877, timeout=15):
    """Wait for port to become free."""
    print(f"⏳ Waiting for port {port} to become free...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result != 0:  # Connection failed = port is free or not listening
                    print(f"✅ Port {port} is free")
                    return True
        except:
            pass
        time.sleep(0.5)
    print(f"⚠️  Port {port} still in use after {timeout}s")
    return False

def start_ableton():
    """Start Ableton Live."""
    ableton_path = r"C:\ProgramData\Ableton\Live 12 Suite\Program\Ableton Live 12 Suite.exe"
    print(f"🚀 Starting Ableton from: {ableton_path}")
    subprocess.Popen([ableton_path],shell=True)
    print("✅ Ableton started")

def wait_for_port_listening(port=9877, timeout=30):
    """Wait for port to start listening."""
    print(f"⏳ Waiting for Remote Script on port {port}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:  # Connection succeeded
                    print(f"✅ Remote Script is listening on port {port}")
                    return True
        except:
            pass
        time.sleep(1)
        # Print progress
        elapsed = int(time.time() - start)
        if elapsed % 5 == 0:
            print(f"   Still waiting... ({elapsed}/{timeout}s)")
    print(f"⚠️  Remote Script not ready after {timeout}s")
    return False

def test_connection():
    """Test the MCP connection."""
    print("\n🧪 Testing MCP connection...")
    try:
        import sys
        sys.path.insert(0, '.')
        from MCP_Server.server import get_ableton_connection
        ableton = get_ableton_connection()
        result = ableton.send_command('get_session_info', {})
        print(f"✅ Connection successful!")
        print(f"   Tempo: {result.get('tempo', 'N/A')} BPM")
        print(f"   Tracks: {result.get('num_tracks', 0)}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)[:100]}")
        return False

def main():
    wait_seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    
    print("=" * 60)
    print("ABLETON LIVE RESTART SCRIPT")
    print("=" * 60)
    print()
    
    # Step 1: Kill Ableton
    kill_ableton()
    
    # Step 2: Wait for port to free up
    wait_for_port_free()
    
    # Step 3: Start Ableton
    start_ableton()
    
    # Step 4: Wait for Remote Script to initialize
    print(f"\n⏰ Waiting {wait_seconds} seconds for Remote Script initialization...")
    time.sleep(wait_seconds)
    
    # Step 5: Check if port is listening
    if not wait_for_port_listening():
        print("\n⚠️  Remote Script may need more time. Try manually checking.")
        return 1
    
    # Step 6: Test connection
    if test_connection():
        print("\n" + "=" * 60)
        print("✅ ABLETON IS READY!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  CONNECTION ISSUE - Try running test_connection_now.py")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
