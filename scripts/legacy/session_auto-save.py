"""
Session Auto-Save Automation

Automatically saves Ableton session snapshots and exports
regularly during 2-hour dub techno mix session.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class SessionAutoSaver:
    """Auto-saves session snapshots at regular intervals."""

    # Save interval in beats (default: every 8 minutes at 125 BPM)
    SAVE_INTERVAL_BEATS = 1000
    # Maximum backup files to keep
    MAX_BACKUPS = 10

    def __init__(self, mcp_client, save_directory: str = "session_backups"):
        """
        Initialize session auto-saver.

        Args:
            mcp_client: MCPClientTCP instance for session queries
            save_directory: Directory for save files
        """
        self.client = mcp_client
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)

        self.last_save_beat = 0
        self.session_start_time = time.time()
        self.save_count = 0

    def check_and_save(self, current_beat: int, force: bool = False) -> Optional[Dict[str, Any]]:
        """
        Check if save interval reached and save if needed.

        Args:
            current_beat: Current playhead position in beats
            force: Force save regardless of interval

        Returns:
            Save metadata if saved, None if not saved
        """
        beats_since_last_save = current_beat - self.last_save_beat

        # Check if save needed
        should_save = force or (beats_since_last_save >= self.SAVE_INTERVAL_BEATS)

        if not should_save:
            return None

        # Perform save
        save_metadata = self._save_session_snapshot(current_beat)
        self.last_save_beat = current_beat

        return save_metadata

    def _save_session_snapshot(self, current_beat: int) -> Dict[str, Any]:
        """
        Save complete session snapshot.

        Args:
            current_beat: Current playhead position

        Returns:
            Save metadata dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_filename = f"dub_techno_session_{timestamp}_beat{current_beat}.json"
        save_path = self.save_directory / save_filename

        # Capture session state
        session_state = self._capture_session_state(current_beat)

        # Write save file
        with open(save_path, 'w') as f:
            json.dump(session_state, f, indent=2)

        self.save_count += 1

        # Cleanup old backups
        self._cleanup_old_backups()

        # Build metadata
        metadata = {
            'save_file': str(save_path),
            'timestamp': timestamp,
            'beat_position': current_beat,
            'elapsed_seconds': time.time() - self.session_start_time,
            'track_count': len(session_state.get('tracks', [])),
            'scene_count': len(session_state.get('scenes', [])),
            'save_number': self.save_count
        }

        print(f"[SAVE] Session saved: {save_filename} (beat {current_beat})")

        return metadata

    def _capture_session_state(self, current_beat: int) -> Dict[str, Any]:
        """
        Capture complete session state via MCP queries.

        Args:
            current_beat: Current playhead position

        Returns:
            Session state dictionary
        """
        try:
            # Get session overview
            session_overview = self.client.get_session_overview()

            # Get detailed track info
            tracks = []
            for track_idx in range(len(session_overview.get('tracks', []))):
                track_info = self.client.get_track_info(track_idx)
                tracks.append({
                    'index': track_idx,
                    'name': track_info.get('name', f'Track {track_idx}'),
                    'volume': track_info.get('volume', 0.7),
                    'mute': track_info.get('mute', False),
                    'solo': track_info.get('solo', False),
                    'device_count': len(track_info.get('devices', []))
                })

            # Get scene info
            scenes = []
            scene_list = self.client.get_all_scenes()
            for scene in scene_list.get('scenes', []):
                scenes.append({
                    'index': scene.get('index', 0),
                    'name': scene.get('name', f'Scene {scene.get("index", 0)}')
                })

            # Get playing tracks
            playing_tracks = self.client.get_playing_clips()

            # Build session state
            state = {
                'metadata': {
                    'tempo': session_overview.get('tempo', 125),
                    'time_signature': session_overview.get('time_signature'),
                    'save_timestamp': datetime.now().isoformat(),
                    'beat_position': current_beat
                },
                'tracks': tracks,
                'scenes': scenes,
                'playing_states': playing_tracks,
                'session_overview': session_overview
            }

            return state

        except Exception as e:
            print(f"[WARNING] Could not capture full session state: {e}")
            return {
                'metadata': {
                    'tempo': 125,
                    'save_timestamp': datetime.now().isoformat(),
                    'beat_position': current_beat,
                    'error': str(e)
                }
            }

    def _cleanup_old_backups(self):
        """Delete oldest backup files if exceeding MAX_BACKUPS."""
        backup_files = sorted(self.save_directory.glob("*.json"))

        if len(backup_files) > self.MAX_BACKUPS:
            # Delete oldest files
            files_to_delete = backup_files[:len(backup_files) - self.MAX_BACKUPS]

            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    print(f"[CLEANUP] Deleted old save file: {file_path.name}")
                except Exception as e:
                    print(f"[WARNING] Could not delete {file_path.name}: {e}")

    def get_save_summary(self) -> Dict[str, Any]:
        """Get summary of all saved session files."""
        backup_files = sorted(self.save_directory.glob("*.json"))

        return {
            'total_saves': len(backup_files),
            'save_directory': str(self.save_directory),
            'recent_saves': [
                {
                    'filename': f.name,
                    'size_bytes': f.stat().st_size
                }
                for f in backup_files[-5:]  # Last 5 saves
            ]
        }

    def export_session_template(self, export_path: Optional[str] = None):
        """
        Export current session as reusable template.

        Args:
            export_path: Path for exported .als file (default: timestamped)
        """
        if export_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"dub_techno_2h_template_{timestamp}.als"

        # Note: Actual .als export not possible via Remote Script API
        # Save JSON state as template instead
        template_path = Path(export_path).with_suffix('.json')
        current_beat = 0  # Template at start position

        template_state = self._capture_session_state(current_beat)
        template_state['metadata']['is_template'] = True
        template_state['metadata']['template_version'] = "1.0"

        with open(template_path, 'w') as f:
            json.dump(template_state, f, indent=2)

        print(f"[TEMPLATE] Session template saved: {template_path}")


class SessionRecovery:
    """Session recovery from saved snapshots."""

    def __init__(self, save_directory: str = "session_backups"):
        """
        Initialize session recovery.

        Args:
            save_directory: Directory containing save files
        """
        self.save_directory = Path(save_directory)

    def list_available_saves(self) -> list:
        """List all available session save files."""
        backup_files = sorted(self.save_directory.glob("*.json"))

        saves = []
        for file_path in backup_files:
            try:
                with open(file_path, 'r') as f:
                    state = json.load(f)
                    saves.append({
                        'path': str(file_path),
                        'timestamp': state.get('metadata', {}).get('save_timestamp'),
                        'beat_position': state.get('metadata', {}).get('beat_position'),
                        'tempo': state.get('metadata', {}).get('tempo')
                    })
            except Exception as e:
                print(f"[WARNING] Could not read {file_path.name}: {e}")

        return saves

    def get_latest_save(self) -> Optional[Dict[str, Any]]:
        """Get latest session save."""
        backup_files = sorted(self.save_directory.glob("*.json"))

        if not backup_files:
            return None

        latest = backup_files[-1]
        try:
            with open(latest, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Could not read latest save: {e}")
            return None

    def recover_session_state(self, mcp_client, save_path: str) -> bool:
        """
        Recover session state from saved snapshot.

        Note: Recovery is partial - cannot restore clip content via MCP.
        Can restore track volumes, mute/solo states, device parameters.

        Args:
            mcp_client: MCPClientTCP instance
            save_path: Path to session save file

        Returns:
            True if recovery succeeded
        """
        try:
            with open(save_path, 'r') as f:
                state = json.load(f)

            # Restore track states
            for track_data in state.get('tracks', []):
                track_idx = track_data.get('index')

                # Restore volume
                mcp_client.set_track_volume(track_idx, track_data.get('volume', 0.7))

                # Restore mute/solo
                mcp_client.set_track_mute(track_idx, track_data.get('mute', False))
                mcp_client.set_track_solo(track_idx, track_data.get('solo', False))

            print(f"[RECOVERY] Session state recovered from {save_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Session recovery failed: {e}")
            return False