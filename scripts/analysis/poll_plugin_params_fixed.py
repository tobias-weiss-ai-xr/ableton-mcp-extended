# NOTE: This is a PATCH showing the required changes
# Apply this edit to scripts/analysis/poll_plugin_params.py lines 300-366

# OLD CODE (replace this):
def run(self, log_file_path):
        # ... docstring ...
        if not self.connect():
            sys.exit(1)

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
                # ... loop ...
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            log_file.close()

# NEW CODE (replace with):
def run(self, log_file_path):
        # ... docstring ...
        if not self.connect():
            sys.exit(1)

        # Open log file in append mode using context manager
        try:
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                print(f"[OK] Logging to: {log_file_path}")

                self.start_time = time.time()
                self.running = True
                poll_iteration = 0

                try:
                    while self.running:
                        # ... all polling logic ...
                except KeyboardInterrupt:
                    print("\n\n[INFO] Interrupted by user (Ctrl+C)")
                    pass
                finally:
                    self.stop()
                    # log_file.close() removed - context manager handles cleanup

        except Exception as e:
            print(f"[ERROR] Failed to open log file: {str(e)}")
            sys.exit(1)
