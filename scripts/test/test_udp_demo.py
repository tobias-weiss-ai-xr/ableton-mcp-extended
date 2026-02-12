"""
Demonstration script for UDP command dispatching.

This example shows how to use send_command_udp() for high-frequency
parameter updates in Ableton Live.

UDP is fire-and-forget: no response, very low latency (<1ms per command)
Use UDP for:
- Real-time filter sweeps
- Volume envelopes
- High-frequency parameter modulation
- Any reversible parameter updates

Commands that support UDP (from architecture design):
1. set_device_parameter - Single parameter update
2. batch_set_device_parameters - Multi-parameter update
3. set_track_volume - Track volume control
4. set_track_pan - Track panning
5. set_track_mute - Track mute state
6. set_track_solo - Track solo state
7. set_track_arm - Track arm state
8. set_clip_launch_mode - Clip launch mode
9. fire_clip - Clip firing

(Higher-level requirement: set_master_volume also documented as UDP-allowed)
"""

import sys
import os
import time

# Add MCP_Server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "MCP_Server"))

from server import AbletonConnection

print("=" * 80)
print("UDP COMMAND DISPATCHING - DEMONSTRATION")
print("=" * 80)

# Example 1: Single parameter update via UDP
print("\n[EXAMPLE 1] Single parameter update via UDP")
print("-" * 80)

try:
    conn = AbletonConnection(host="127.0.0.1", port=9877)
    udp_port = getattr(conn, "udp_port", 9878)

    print(f"Setting up connection to Ableton:")
    print(f"  - TCP port: {conn.port} (reliable, request/response)")
    print(f"  - UDP port: {udp_port} (fire-and-forget, low latency)")
    print()

    # Example: Set track volume to 0.75 via UDP
    print("Setting track 0 volume to 0.75 via UDP...")
    start_time = time.time()
    result = conn.send_command_udp(
        "set_track_volume", {"track_index": 0, "volume": 0.75}
    )
    elapsed = (time.time() - start_time) * 1000

    print(f"  - Command sent in {elapsed:.2f}ms")
    print(f"  - Return value: {result} (None = fire-and-forget)")
    print(f"  - UDP port used: {udp_port}")
    print()

except Exception as e:
    print(f"Note: This example requires Ableton Live with Remote Script running")
    print(f"Error: {e}")
    print()

# Example 2: High-frequency parameter sweep via UDP
print("[EXAMPLE 2] High-frequency parameter sweep (100 updates)")
print("-" * 80)

print("Simulating real-time filter sweep via UDP...")
print("If Ableton Live is running, track 0 volume will sweep from 0.5 to 1.5")
print()

try:
    conn = AbletonConnection(host="127.0.0.1", port=9877)

    num_updates = 100
    print(f"Sending {num_updates} UDP commands...")

    start_time = time.time()

    for i in range(num_updates):
        volume = 0.5 + (i * 0.01)  # Sweep 0.5 → 1.5
        conn.send_command_udp("set_track_volume", {"track_index": 0, "volume": volume})

    elapsed = (time.time() - start_time) * 1000
    avg_ms = elapsed / num_updates

    print(f"  - Total time: {elapsed:.2f}ms")
    print(f"  - Average per command: {avg_ms:.3f}ms")
    print(f"  - Commands per second: {1000 / avg_ms:.1f} Hz")
    print(f"  - Final volume: 1.5")
    print()

except Exception as e:
    print(f"Note: This example requires Ableton Live with Remote Script running")
    print(f"Error: {e}")
    print()

# Example 3: Comparison: TCP vs UDP performance
print("[EXAMPLE 3] Performance comparison (simulation)")
print("-" * 80)

print("Simulating 100 parameter updates:")
print("  - TCP (request/response): Each command waits for Ack (~20-50ms)")
print("  - UDP (fire-and-forget): Each command sends immediately (~<1ms)")
print()

print(" estimated performance:")
print("  Protocol | Latency  | 100 commands | Throughput")
print("  -------- | -------- | ------------ | ----------")
print("  TCP      | 20-50ms  | 2.0-5.0s     | 20-50 Hz")
print("  UDP      | <1ms     | <0.1s        | >1000 Hz")
print()

print("Speedup factor: 10-50x faster with UDP!")
print()

# Example 4: When to use TCP vs UDP
print("[EXAMPLE 4] When to use TCP vs UDP")
print("-" * 80)

print("Use TCP (port 9877) for:")
print("  [+] Irreversible operations (delete, create)")
print("  [+] Content operations (load instruments, add notes)")
print("  [+] Read operations (get_session_info, get_track_info)")
print("  [+] Complex operations (duplicate, move, group)")
print("  [+] Any operation that needs confirmation")
print()

print("Use UDP (port 9878) for:")
print("  [+] High-frequency parameter updates")
print("  [+] Real-time control (filter sweeps, volume envelopes)")
print("  [+] Reversible state changes (volume, pan, mute, solo, arm)")
print("  [+] Continuous parameter modulation")
print("  [+] Any operation where <5% packet loss is acceptable")
print()

# Summary
print("=" * 80)
print("UDP COMMAND DISPATCHING - SUMMARY")
print("=" * 80)
print()
print("Key Benefits of UDP:")
print("  1. Ultra-low latency ( <1ms per command)")
print("  2. High throughput (1000+ commands/second)")
print("  3. No response overhead (fire-and-forget)")
print("  4. Efficient for real-time control")
print()
print("Supported UDP Commands:")
print("  1. set_device_parameter")
print("  2. set_track_volume")
print("  3. set_track_pan")
print("  4. set_track_mute")
print("  5. set_track_solo")
print("  6. set_track_arm")
print("  7. set_clip_launch_mode")
print("  8. fire_clip")
print("  9. set_master_volume")
print()
print("Usage Pattern:")
print("  conn = AbletonConnection(host='127.0.0.1', port=9877)")
print("  conn.send_command_udp('set_track_volume', {'track_index': 0, 'volume': 0.75})")
print()
print("Note: UDP returns None (fire-and-forget). Use TCP if you need")
print("      confirmation of successful operation.")
print("=" * 80)
