#!/usr/bin/env python3
"""
Poll Plugin Parameters for VST Audio Analysis

This script continuously queries plugin parameters from Ableton Live via TCP socket,
logging all readings to a CSV file for analysis.

Usage:
    python poll_plugin_params.py --plugin=YouleanLoudnessMeter --track=0 --device=0 --rate=15 --duration=60

Output:
    logs/poll_plugin_params_YYYYMMDD_HHMMSS.log (CSV format)
"""

import socket
import json
import time
import argparse
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path


class ParameterPoller:
    """Polls VST plugin parameters from Ableton Live via TCP socket"""

    def __init__(self, track_index, device_index, update_rate_hz, duration_seconds):
        """
        Initialize the parameter poller.

        Args:
            track_index: Track index containing the plugin
            device_index: Device index on the track
            update_rate_hz: Polling rate in Hz (10-20 Hz recommended)
            duration_seconds: Total duration to poll (None = infinite)
        """
        self.track_index = track_index
        self.device_index = device_index
        self.update_rate_hz = update_rate_hz
        self.duration_seconds = duration_seconds
        self.update_interval = 1.0 / update_rate_hz

        # Connection
        self.host = "127.0.0.1"
        self.port = 9877
        self.sock = None

        # State
        self.running = False
        self.readings_count = 0
        self.start_time = None
        self.last_params = {}  # Parameter caching

        # Error handling
        self.timeout_retries = 3
        self.consecutive_errors = 0

        # Statistics
        self.poll_times = []

    def connect(self) -> bool:
        """
        Connect to Ableton Remote Script TCP server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)  # 5 second connection timeout
            self.sock.connect((self.host, self.port))
            print(f"[OK] Connected to Ableton at {self.host}:{self.port}")
            return True
        except socket.timeout:
            print(
                f"[ERROR] Connection timeout: Could not connect to Ableton at {self.host}:{self.port}"
            )
            return False
        except ConnectionRefusedError:
            print(
                f"[ERROR] Connection refused: Ableton Remote Script not running on port {self.port}"
            )
            return False
        except Exception as e:
            print(f"[ERROR] Connection error: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from Ableton Remote Script"""
        if self.sock:
            try:
                self.sock.close()
                print(f"[OK] Disconnected from Ableton")
            except Exception as e:
                print(f"[WARN] Warning during disconnect: {str(e)}")
            finally:
                self.sock = None

    def get_device_parameters(self) -> dict:
        """
        Get all parameters from the specified device.

        Returns:
            Dictionary with device parameters, or None on error

        Raises:
            SystemExit on fatal errors
        """
        if not self.sock:
            print("[ERROR] Not connected to Ableton")
            raise SystemExit(1)

        command = {
            "type": "get_device_parameters",
            "params": {
                "track_index": self.track_index,
                "device_index": self.device_index,
            },
        }

        try:
            # Send command
            command_json = json.dumps(command).encode("utf-8")
            self.sock.sendall(command_json)

            # Receive response (with timeout)
            self.sock.settimeout(15.0)  # 15 second response timeout
            response_data = b""
            while True:
                chunk = self.sock.recv(8192)
                if not chunk:
                    break
                response_data += chunk

                # Check if we have complete JSON
                try:
                    json.loads(response_data.decode("utf-8"))
                    break
                except json.JSONDecodeError:
                    # Incomplete JSON, continue receiving
                    continue

            # Parse response
            response = json.loads(response_data.decode("utf-8"))

            # Check for error
            if response.get("status") == "error":
                message = response.get("message", "Unknown error")
                print(f"[ERROR] Ableton error: {message}")
                return None

            # Return parameters
            result = response.get("result", {})
            device_name = result.get("device_name", "Unknown")
            parameters = result.get("parameters", [])

            print(f"[OK] Retrieved {len(parameters)} parameters from {device_name}")
            return {
                "device_name": device_name,
                "parameters": parameters,
            }

        except socket.timeout:
            print("[ERROR] Socket timeout: No response from Ableton")
            self.consecutive_errors += 1
            if self.consecutive_errors >= self.timeout_retries:
                print(f"[ERROR] {self.timeout_retries} consecutive timeouts, exiting")
                raise SystemExit(1)
            return None
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            print(f"[ERROR] Socket connection error: {str(e)}")
            self.disconnect()
            self.consecutive_errors += 1
            if self.consecutive_errors >= self.timeout_retries:
                print(
                    f"[ERROR] {self.timeout_retries} consecutive connection errors, exiting"
                )
                raise SystemExit(1)
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON response from Ableton: {str(e)}")
            return None
        except Exception as e:
            print(f"[ERROR] Error getting device parameters: {str(e)}")
            return None

    def format_timestamp(self) -> str:
        """Format timestamp in ISO 8601 format"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"

    def log_parameters(self, log_file, params_data):
        """
        Log parameters to CSV file.

        Args:
            log_file: File object to write to
            params_data: Dictionary containing device_name and parameters list
        """
        if not params_data:
            return

        parameters = params_data.get("parameters", [])
        device_name = params_data.get("device_name", "Unknown")

        timestamp = self.format_timestamp()

        # Write header if file is empty
        log_file.seek(0, 2)  # Go to end of file
        if log_file.tell() == 0:
            log_file.write(
                "timestamp,track_index,device_index,parameter_index,parameter_name,value,min,max\n"
            )

        # Log each parameter
        for param in parameters:
            line = f"{timestamp},{self.track_index},{self.device_index},{param.get('index', '')},{param.get('name', '')},{param.get('value', '')},{param.get('min', '')},{param.get('max', '')}\n"
            log_file.write(line)

        log_file.flush()  # Ensure data is written immediately

    def has_parameters_changed(self, new_params) -> bool:
        """
        Check if any parameters have changed since last poll.

        Args:
            new_params: List of parameter dictionaries

        Returns:
            True if any parameter changed, False otherwise
        """
        if not self.last_params:
            return True

        for param in new_params:
            param_index = param.get("index")
            if param_index not in self.last_params:
                return True
            if self.last_params[param_index] != param.get("value"):
                return True

        return False

    def poll_once(self, log_file, cache_enabled=True):
        """
        Perform a single polling operation.

        Args:
            log_file: File object to write logs to
            cache_enabled: If True, only log when parameters change

        Returns:
            True if successful, False otherwise
        """
        poll_start = time.time()

        # Get parameters
        params_data = self.get_device_parameters()
        if not params_data:
            return False

        parameters = params_data.get("parameters", [])

        # Check if parameters changed (caching)
        if cache_enabled:
            if not self.has_parameters_changed(parameters):
                print(
                    f"[INFO] Parameters unchanged (rate: {self.update_rate_hz} Hz), skipping log"
                )
                self.poll_times.append(time.time() - poll_start)
                return True

        # Update last parameters cache
        self.last_params = {p.get("index"): p.get("value") for p in parameters}

        # Log parameters
        try:
            self.log_parameters(log_file, params_data)
            self.readings_count += 1
        except Exception as e:
            print(f"[ERROR] Error writing to log file: {str(e)}")
            return False

        # Reset consecutive errors on success
        self.consecutive_errors = 0

        # Track poll time
        poll_time = time.time() - poll_start
        self.poll_times.append(poll_time)

        return True

    def run(self, log_file_path):
        """
        Run the polling loop.

        Args:
            log_file_path: Path to log file
        """
        # Connect to Ableton
        if not self.connect():
            sys.exit(1)

        # Open log file in append mode
        try:
            log_file = open(log_file_path, "a", encoding="utf-8")
            print(f"[OK] Logging to: {log_file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to open log file: {str(e)}")
            sys.exit(1)

        self.start_time = time.time()
        self.running = True
        poll_iteration = 0

        try:
            while self.running:
                poll_iteration += 1

                # Check duration limit
                if self.duration_seconds:
                    elapsed = time.time() - self.start_time
                    if elapsed >= self.duration_seconds:
                        print(
                            f"[OK] Duration reached ({self.duration_seconds}s), stopping..."
                        )
                        break

                # Perform poll
                if not self.poll_once(log_file):
                    print("[INFO] Poll failed, retrying...")
                    time.sleep(1.0)  # Wait before retry
                    continue

                # Display progress
                if poll_iteration % 50 == 0:
                    elapsed = time.time() - self.start_time
                    avg_poll_time = (
                        sum(self.poll_times[-50:]) / min(len(self.poll_times), 50)
                        if self.poll_times
                        else 0
                    )
                    actual_rate = 1.0 / avg_poll_time if avg_poll_time > 0 else 0
                    print(
                        f"[INFO] Progress: {self.readings_count} readings, {elapsed:.1f}s elapsed, ~{actual_rate:.1f} Hz avg"
                    )

                # Sleep for next poll
                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user (Ctrl+C)")
            pass
        finally:
            # Cleanup
            self.stop()
            log_file.close()

    def stop(self):
        """Stop polling and print summary"""
        self.running = False

        if self.sock:
            self.disconnect()

        # Print summary
        elapsed = time.time() - self.start_time if self.start_time else 0
        avg_rate = self.readings_count / elapsed if elapsed > 0 else 0
        avg_poll_time = (
            sum(self.poll_times) / len(self.poll_times) if self.poll_times else 0
        )

        print("\n" + "=" * 60)
        print("POLLING SUMMARY")
        print("=" * 60)
        print(f"Total readings collected: {self.readings_count}")
        print(f"Total duration: {elapsed:.2f} seconds")
        print(f"Average update rate: {avg_rate:.2f} Hz")
        print(f"Target update rate: {self.update_rate_hz:.2f} Hz")
        print(f"Average poll time: {avg_poll_time * 1000:.2f} ms")
        print("=" * 60)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Poll VST plugin parameters from Ableton Live",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python poll_plugin_params.py --plugin=YouleanLoudnessMeter --track=0 --device=0 --rate=15 --duration=60
  python poll_plugin_params.py --plugin=LoudnessMeter --track=2 --device=0 --rate=10 --duration=300
        """,
    )

    parser.add_argument(
        "--plugin",
        type=str,
        required=True,
        help="Plugin name (for logging, e.g., YouleanLoudnessMeter)",
    )

    parser.add_argument(
        "--track",
        type=int,
        required=True,
        help="Track index containing the plugin",
    )

    parser.add_argument(
        "--device",
        type=int,
        required=True,
        help="Device index on the track",
    )

    parser.add_argument(
        "--rate",
        type=float,
        default=15.0,
        choices=[float(x) for x in range(10, 21)],  # 10-20 Hz
        metavar="HZ",
        help="Update rate in Hz (10-20, default: 15)",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Duration in seconds (0 = infinite polling, default: 0)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="logs",
        help="Output directory for log files (default: logs)",
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()

    print("=" * 60)
    print("VST PARAMETER POLLER")
    print("=" * 60)
    print(f"Plugin: {args.plugin}")
    print(f"Track index: {args.track}")
    print(f"Device index: {args.device}")
    print(f"Update rate: {args.rate} Hz")
    print(
        f"Duration: {'Infinite' if args.duration == 0 else f'{args.duration} seconds'}"
    )
    print("=" * 60)
    print()

    # Validate rate
    if args.rate < 10 or args.rate > 20:
        print("[ERROR] Invalid rate: Must be between 10-20 Hz")
        sys.exit(2)

    # Create output directory
    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Failed to create output directory: {str(e)}")
        sys.exit(3)

    # Generate log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"poll_plugin_params_{timestamp}.log"
    log_path = output_dir / log_filename

    # Setup signal handler for graceful exit
    poller = ParameterPoller(
        track_index=args.track,
        device_index=args.device,
        update_rate_hz=args.rate,
        duration_seconds=args.duration if args.duration > 0 else None,
    )

    # Register signal handlers
    def signal_handler(signum, frame):
        print("\n\n[INFO] Signal received, stopping gracefully...")
        poller.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start polling
    print(f"[OK] Starting polling loop at {args.rate} Hz...")
    if args.duration > 0:
        print(f"[OK] Will stop after {args.duration} seconds")
    else:
        print("[OK] Polling infinitely (Ctrl+C to stop)")
    print(f"[OK] Log file: {log_path}")
    print()
    print("Press Ctrl+C to stop gracefully")
    print("-" * 60)
    print()

    try:
        poller.run(log_path)
    except SystemExit as e:
        sys.exit(e.code)


if __name__ == "__main__":
    main()
