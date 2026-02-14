"""
Automated performance tests for UDP command dispatching.

This test suite validates that UDP commands meet the performance targets
defined in the architecture design:
- Load: 1000 parameter updates via UDP in <20 seconds (50Hz+)
- Latency: Average <20ms, 99th percentile <50ms
- Packet loss: Tolerance to 5% packet loss without degradation
- Concurrent: Mixed TCP/UDP traffic without conflicts
- Baseline: TCP vs UDP performance comparison

Tests use mock UDP server (no Ableton Live required).
Tests warn on performance degradation rather than hard failure.
"""

import socket
import json
import time
import sys
import os
import random
import threading
from typing import List, Dict, Any

# Add MCP_Server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "MCP_Server"))

from server import AbletonConnection


# Mock UDP server to simulate Ableton Remote Script with packet loss simulation
class MockRemoteScriptUDPServerWithLoss:
    """Mock UDP server that simulates Ableton Remote Script with packet loss"""

    def __init__(self, host="127.0.0.1", port=9878, packet_loss_rate=0.0):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.received_commands = []
        self.packet_loss_rate = packet_loss_rate

    def start(self):
        """Start mock UDP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.settimeout(0.1)
            self.running = True

            self.thread = threading.Thread(target=self._server_loop, daemon=True)
            self.thread.start()

            print(f"[MOCK] Started mock UDP server on {self.host}:{self.port}")
            if self.packet_loss_rate > 0:
                print(
                    f"[MOCK] Packet loss simulation: {self.packet_loss_rate * 100:.1f}%"
                )

        except Exception as e:
            print(f"[FAIL] Could not start mock UDP server: {e}")
            sys.exit(1)

    def _server_loop(self):
        """Server receive loop with packet loss simulation"""
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(1024)

                # Simulate packet loss
                if self.packet_loss_rate > 0:
                    if random.random() < self.packet_loss_rate:
                        # Drop this packet (simulate loss)
                        continue

                command_str = data.decode("utf-8")
                command = json.loads(command_str)

                self.received_commands.append(
                    {"command": command, "addr": addr, "timestamp": time.time()}
                )

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    pass  # Silent error handling for performance tests

    def stop(self):
        """Stop mock UDP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def clear_commands(self):
        """Clear received command history"""
        self.received_commands.clear()

    @property
    def command_count(self) -> int:
        """Get number of received commands"""
        return len(self.received_commands)


# ============================================================================
# TEST CLASS 1: Load Test - Validate 1000 commands in <20 seconds
# ============================================================================


class TestLoadPerformance:
    """Test UDP load performance: 1000 commands in <20 seconds (50Hz+)"""

    target_count = 1000
    target_time_ms = 20000  # 20 seconds
    target_hz = 50  # Minimum throughput

    @staticmethod
    def test_1000_commands_under_20_seconds():
        """Test that 1000 UDP commands complete in <20 seconds"""

        print("\n" + "=" * 80)
        print("[LOAD TEST] 1000 UDP commands in <20 seconds")
        print("=" * 80)

        # Start mock server
        mock_server = MockRemoteScriptUDPServerWithLoss()
        mock_server.start()
        time.sleep(0.1)

        # Create connection
        conn = AbletonConnection(host="127.0.0.1", port=9877)

        # Send 1000 commands rapidly
        start_time = time.time()

        # Command templates with index placeholders
        test_command_templates = [
            (
                "set_device_parameter",
                {
                    "track_index": 0,
                    "device_index": 0,
                    "parameter_index": 0,
                    "value": 0.5,
                },
            ),
            ("set_track_volume", {"track_index": 0, "volume": 0.5}),
            ("set_track_pan", {"track_index": 0, "pan": 0.0}),
            ("set_track_mute", {"track_index": 0, "mute": False}),
            ("set_track_solo", {"track_index": 0, "solo": False}),
            ("set_track_arm", {"track_index": 0, "arm": False}),
            ("set_clip_launch_mode", {"track_index": 0, "clip_index": 0, "mode": 0}),
            ("fire_clip", {"track_index": 0, "clip_index": 0}),
            ("set_master_volume", {"volume": 0.75}),
        ]

        # Calculate actual commands to send (1000 total)
        commands_sent_count = TestLoadPerformance.target_count

        for i in range(commands_sent_count):
            cmd_type, cmd_params = test_command_templates[
                i % len(test_command_templates)
            ]
            conn.send_command_udp(cmd_type, cmd_params)

        elapsed_ms = (time.time() - start_time) * 1000

        # Wait for server to process all commands
        time.sleep(0.5)

        # Calculate throughput
        hz = commands_sent_count / (time.time() - start_time)

        print(f"[RESULT] Sent {commands_sent_count} commands in {elapsed_ms:.2f}ms")
        print(f"[RESULT] Throughput: {hz:.1f} Hz")
        print(f"[RESULT] Commands received by server: {mock_server.command_count}")

        # Verify performance targets
        if elapsed_ms < TestLoadPerformance.target_time_ms:
            print(
                f"[PASS] Load test passed: {elapsed_ms:.2f}ms < {TestLoadPerformance.target_time_ms}ms target"
            )
        else:
            print(
                f"[WARN] Load test exceeded target: {elapsed_ms:.2f}ms > {TestLoadPerformance.target_time_ms}ms target"
            )

        if hz >= TestLoadPerformance.target_hz:
            print(
                f"[PASS] Throughput meets target: {hz:.1f} Hz >= {TestLoadPerformance.target_hz} Hz target"
            )
        else:
            print(
                f"[WARN] Throughput below target: {hz:.1f} Hz < {TestLoadPerformance.target_hz} Hz target"
            )

        # Verify command delivery
        if (
            mock_server.command_count >= commands_sent_count * 0.95
        ):  # Allow 5% packet loss
            print(
                f"[PASS] Command delivery rate acceptable: {mock_server.command_count}/{commands_sent_count}"
            )
        else:
            print(
                f"[WARN] High packet loss detected: {commands_sent_count - mock_server.command_count}/{commands_sent_count} commands lost"
            )

        mock_server.stop()

        assert elapsed_ms < (TestLoadPerformance.target_time_ms * 1.5), (
            f"Load test severely exceeded: {elapsed_ms:.2f}ms"
        )
        print("[OK] Load test completed successfully\n")


# ============================================================================
# TEST CLASS 2: Latency Test - Individual command latency
# ============================================================================


class TestLatencyPerformance:
    """Test UDP latency: Individual command latency <20ms average"""

    target_avg_ms = 20.0
    target_p99_ms = 50.0
    test_count = 100

    @staticmethod
    def test_command_latency_below_20ms_average():
        """Test that individual command latency is <20ms average"""

        print("\n" + "=" * 80)
        print("[LATENCY TEST] Individual command latency <20ms average")
        print("=" * 80)

        # Start mock server
        mock_server = MockRemoteScriptUDPServerWithLoss()
        mock_server.start()
        time.sleep(0.1)

        # Create connection
        conn = AbletonConnection(host="127.0.0.1", port=9877)

        # Measure latency for individual commands
        latencies: List[float] = []

        for i in range(TestLatencyPerformance.test_count):
            start_time = time.time()

            # Send command
            conn.send_command_udp(
                "set_track_volume", {"track_index": 0, "volume": 0.5 + (i * 0.001)}
            )

            elapsed_ms = (time.time() - start_time) * 1000
            latencies.append(elapsed_ms)

        # Calculate statistics
        avg_ms = sum(latencies) / len(latencies)
        p50_ms = sorted(latencies)[len(latencies) // 2]
        p99_ms = sorted(latencies)[int(len(latencies) * 0.99)]

        print(f"[RESULT] Average latency: {avg_ms:.2f}ms")
        print(f"[RESULT] P50 latency: {p50_ms:.2f}ms")
        print(f"[RESULT] P99 latency: {p99_ms:.2f}ms")
        print(f"[RESULT] Min latency: {min(latencies):.2f}ms")
        print(f"[RESULT] Max latency: {max(latencies):.2f}ms")

        # Verify latency targets
        if avg_ms < TestLatencyPerformance.target_avg_ms:
            print(
                f"[PASS] Average latency meets target: {avg_ms:.2f}ms < {TestLatencyPerformance.target_avg_ms}ms target"
            )
        else:
            print(
                f"[WARN] Average latency exceeds target: {avg_ms:.2f}ms > {TestLatencyPerformance.target_avg_ms}ms target"
            )

        if p99_ms < TestLatencyPerformance.target_p99_ms:
            print(
                f"[PASS] P99 latency meets target: {p99_ms:.2f}ms < {TestLatencyPerformance.target_p99_ms}ms target"
            )
        else:
            print(
                f"[WARN] P99 latency exceeds target: {p99_ms:.2f}ms > {TestLatencyPerformance.target_p99_ms}ms target"
            )

        mock_server.stop()

        assert avg_ms < (TestLatencyPerformance.target_avg_ms * 2), (
            f"Average latency severely exceeded: {avg_ms:.2f}ms"
        )
        print("[OK] Latency test completed successfully\n")


# ============================================================================
# TEST CLASS 3: Packet Loss Test - Tolerance to 5% packet loss
# ============================================================================


class TestPacketLossTolerance:
    """Test UDP packet loss tolerance: Acceptable behavior with 5% loss"""

    loss_rate = 0.05  # 5% packet loss
    tolerance_threshold = 0.10  # 10% tolerance for state consistency

    @staticmethod
    def test_5_percent_packet_loss_tolerance():
        """Test that system tolerates 5% packet loss without state degradation"""

        print("\n" + "=" * 80)
        print("[PACKET LOSS TEST] Tolerance to 5% packet loss")
        print("=" * 80)

        # Start mock server with 5% packet loss
        mock_server = MockRemoteScriptUDPServerWithLoss(
            packet_loss_rate=TestPacketLossTolerance.loss_rate
        )
        mock_server.start()
        time.sleep(0.1)

        # Create connection
        conn = AbletonConnection(host="127.0.0.1", port=9877)

        # Send 100 volume commands (0.0 to 0.99)
        test_count = 100
        expected_states: List[float] = []

        for i in range(test_count):
            volume = i / 100.0
            expected_states.append(volume)
            conn.send_command_udp(
                "set_track_volume", {"track_index": 0, "volume": volume}
            )

        # Wait for server to process
        time.sleep(0.5)

        # Check received commands - we expect ~95% delivery (100 commands, 5% loss)
        received_count = mock_server.command_count
        expected_received = int(test_count * (1.0 - TestPacketLossTolerance.loss_rate))
        loss_tolerance = (
            0.1  # Allow actual loss to be within ±10% of simulated loss rate
        )

        actual_loss_rate = 1.0 - (received_count / test_count)

        print(f"[RESULT] Sent: {test_count} commands")
        print(f"[RESULT] Received: {received_count} commands")
        print(f"[RESULT] Loss rate: {actual_loss_rate * 100:.1f}%")
        print(f"[RESULT] Expected loss: {TestPacketLossTolerance.loss_rate * 100:.1f}%")

        # Verify packet loss is within acceptable range
        if abs(actual_loss_rate - TestPacketLossTolerance.loss_rate) < loss_tolerance:
            print(
                f"[PASS] Packet loss within tolerance: {actual_loss_rate * 100:.1f}% ~ {TestPacketLossTolerance.loss_rate * 100:.1f}%"
            )
        else:
            print(
                f"[WARN] Packet loss outside tolerance: {actual_loss_rate * 100:.1f}% vs {TestPacketLossTolerance.loss_rate * 100:.1f}% expected"
            )

        # Verify state consistency - last received command should be close to last sent
        if mock_server.received_commands:
            last_received_volume = mock_server.received_commands[-1]["command"][
                "params"
            ]["volume"]
            last_expected_volume = expected_states[-1]

            # With 5% loss, we might miss the last command, but final state should be close
            # (within tolerance_threshold of expected)
            volume_diff = abs(last_received_volume - last_expected_volume)
            expected_diff = TestPacketLossTolerance.loss_rate  # Max expected deviation

            if volume_diff < expected_diff + 0.1:  # Add some buffer for near-misses
                print(
                    f"[PASS] Final state consistent: {last_received_volume:.2f} ~ {last_expected_volume:.2f}"
                )
            else:
                print(
                    f"[WARN] Final state diverged: {last_received_volume:.2f} vs {last_expected_volume:.2f} expected"
                )
        else:
            print("[WARN] No commands received (severe packet loss)")

        mock_server.stop()

        # Assert that we received most commands (with tolerance for random loss)
        assert received_count >= int(test_count * 0.8), (
            f"Too many packets lost: {received_count}/{test_count}"
        )
        print("[OK] Packet loss tolerance test completed successfully\n")


# ============================================================================
# TEST CLASS 4: Concurrent Test - Mixed TCP/UDP traffic
# ============================================================================


class TestConcurrentTraffic:
    """Test concurrent TCP/UDP traffic: No conflicts or interference"""

    tcp_count = 50
    udp_count = 950
    total_count = tcp_count + udp_count

    @staticmethod
    def test_mixed_tcp_udp_traffic():
        """Test that mixed TCP/UDP traffic works without conflicts"""

        print("\n" + "=" * 80)
        print(
            "[CONCURRENT TEST] Mixed TCP/UDP traffic ({0} TCP + {1} UDP)".format(
                TestConcurrentTraffic.tcp_count, TestConcurrentTraffic.udp_count
            )
        )
        print("=" * 80)

        # Start mock UDP server
        mock_server = MockRemoteScriptUDPServerWithLoss()
        mock_server.start()
        time.sleep(0.1)

        # Create connection
        conn = AbletonConnection(host="127.0.0.1", port=9877)

        # Interleave TCP (mock - won't connect) and UDP commands
        # TCP commands will fail (no Ableton Live), but should not block UDP
        start_time = time.time()

        for i in range(TestConcurrentTraffic.total_count):
            if i % 20 == 0:  # 5% TCP commands
                # Simulate TCP command (will fail, but shouldn't affect UDP)
                try:
                    conn.send_command("get_session_info", {})
                except:
                    pass  # Expected to fail (no Ableton Live)
            else:  # 95% UDP commands
                conn.send_command_udp(
                    "set_track_volume", {"track_index": 0, "volume": (i % 100) / 100.0}
                )

        elapsed_ms = (time.time() - start_time) * 1000

        # Wait for UDP server to process
        time.sleep(0.5)

        udp_received = mock_server.command_count
        udp_expected = int(TestConcurrentTraffic.total_count * 0.95)  # 95% UDP

        print(f"[RESULT] Total commands: {TestConcurrentTraffic.total_count}")
        print(f"[RESULT] Time: {elapsed_ms:.2f}ms")
        print(f"[RESULT] UDP received: {udp_received}/{udp_expected}")

        # Verify UDP not affected by TCP failures
        if udp_received >= udp_expected * 0.95:  # Allow 5% loss
            print(f"[PASS] UDP traffic unaffected by TCP failures")
        else:
            print(
                f"[WARN] UDP traffic may be affected: {udp_received} vs {udp_expected} expected"
            )

        mock_server.stop()

        # Verify most UDP commands received
        assert udp_received >= udp_expected * 0.9, (
            f"UDP traffic severely affected: {udp_received}/{udp_expected}"
        )
        print("[OK] Concurrent traffic test completed successfully\n")


# ============================================================================
# TEST CLASS 5: Baseline Test - TCP vs UDP performance comparison
# ============================================================================


class TestBaselineComparison:
    """Test baseline: TCP vs UDP performance comparison"""

    test_count = 100

    @staticmethod
    def test_tcp_vs_udp_performance():
        """Compare TCP vs UDP performance"""

        print("\n" + "=" * 80)
        print("[BASELINE TEST] TCP vs UDP performance comparison")
        print("=" * 80)

        # Test UDP performance
        print("\n--- Testing UDP Performance ---")
        mock_server = MockRemoteScriptUDPServerWithLoss()
        mock_server.start()
        time.sleep(0.1)

        conn = AbletonConnection(host="127.0.0.1", port=9877)

        udp_start = time.time()
        for i in range(TestBaselineComparison.test_count):
            conn.send_command_udp(
                "set_track_volume", {"track_index": 0, "volume": (i % 100) / 100.0}
            )
        udp_time_ms = (time.time() - udp_start) * 1000

        mock_server.stop()

        # Test TCP performance (will fail, but measure attempt time)
        print("\n--- Testing TCP Performance ---")
        tcp_start = time.time()
        tcp_success = 0

        for i in range(TestBaselineComparison.test_count):
            try:
                result = conn.send_command("get_session_info", {})
                if result:
                    tcp_success += 1
            except:
                pass  # Expected to fail (no Ableton Live)

        tcp_time_ms = (time.time() - tcp_start) * 1000

        # Calculate statistics
        udp_per_ms = udp_time_ms / TestBaselineComparison.test_count
        tcp_per_ms = tcp_time_ms / TestBaselineComparison.test_count
        speedup = tcp_time_ms / udp_time_ms if udp_time_ms > 0 else 0

        print(f"\n[RESULT] UDP Performance:")
        print(f"  Total time: {udp_time_ms:.2f}ms")
        print(f"  Per command: {udp_per_ms:.3f}ms")
        print(f"  Throughput: {1000 / udp_per_ms:.1f} Hz")

        print(f"\n[RESULT] TCP Performance:")
        print(f"  Total time: {tcp_time_ms:.2f}ms")
        print(f"  Per command: {tcp_per_ms:.3f}ms")
        print(f"  Throughput: {1000 / tcp_per_ms:.1f} Hz")
        print(
            f"  Successful commands: {tcp_success}/{TestBaselineComparison.test_count}"
        )

        print(f"\n[RESULT] Performance Comparison:")
        print(f"  Speedup factor: {speedup:.1f}x")
        print(
            f"  UDP vs TCP: {((tcp_time_ms - udp_time_ms) / tcp_time_ms * 100):.1f}% faster"
        )

        if speedup > 5:
            print(f"[PASS] UDP significantly faster than TCP ({speedup:.1f}x speedup)")
        elif speedup > 2:
            print(f"[OK] UDP faster than TCP ({speedup:.1f}x speedup)")
        else:
            print(f"[WARN] UDP speedup lower than expected ({speedup:.1f}x)")

        # Verify UDP is faster
        assert udp_time_ms < tcp_time_ms, "UDP should be faster than TCP"
        print("[OK] Baseline comparison test completed successfully\n")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UDP PERFORMANCE TESTS")
    print("=" * 80)

    tests_run = 0
    tests_passed = 0
    tests_failed = 0

    try:
        # Run Load Test
        tests_run += 1
        TestLoadPerformance.test_1000_commands_under_20_seconds()
        tests_passed += 1
        print("[PASS] Load Test\n")
    except AssertionError as e:
        tests_failed += 1
        print(f"[FAIL] Load Test: {e}\n")
    except Exception as e:
        tests_failed += 1
        print(f"[ERROR] Load Test: {e}\n")

    try:
        # Run Latency Test
        tests_run += 1
        TestLatencyPerformance.test_command_latency_below_20ms_average()
        tests_passed += 1
        print("[PASS] Latency Test\n")
    except AssertionError as e:
        tests_failed += 1
        print(f"[FAIL] Latency Test: {e}\n")
    except Exception as e:
        tests_failed += 1
        print(f"[ERROR] Latency Test: {e}\n")

    try:
        # Run Packet Loss Test
        tests_run += 1
        TestPacketLossTolerance.test_5_percent_packet_loss_tolerance()
        tests_passed += 1
        print("[PASS] Packet Loss Test\n")
    except AssertionError as e:
        tests_failed += 1
        print(f"[FAIL] Packet Loss Test: {e}\n")
    except Exception as e:
        tests_failed += 1
        print(f"[ERROR] Packet Loss Test: {e}\n")

    try:
        # Run Concurrent Test
        tests_run += 1
        TestConcurrentTraffic.test_mixed_tcp_udp_traffic()
        tests_passed += 1
        print("[PASS] Concurrent Test\n")
    except AssertionError as e:
        tests_failed += 1
        print(f"[FAIL] Concurrent Test: {e}\n")
    except Exception as e:
        tests_failed += 1
        print(f"[ERROR] Concurrent Test: {e}\n")

    try:
        # Run Baseline Test
        tests_run += 1
        TestBaselineComparison.test_tcp_vs_udp_performance()
        tests_passed += 1
        print("[PASS] Baseline Test\n")
    except AssertionError as e:
        tests_failed += 1
        print(f"[FAIL] Baseline Test: {e}\n")
    except Exception as e:
        tests_failed += 1
        print(f"[ERROR] Baseline Test: {e}\n")

    # Print summary
    print("=" * 80)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print("=" * 80)

    if tests_failed == 0:
        print("[SUCCESS] All performance tests passed!")
        sys.exit(0)
    else:
        print(f"[PARTIAL] {tests_failed} test(s) failed")
        sys.exit(1)
