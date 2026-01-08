    def _get_device_parameters(self, track_index, device_index):
        """Get all parameters for a specific device on a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            # Get all parameters from the device
            parameters = []
            if hasattr(device, "parameters"):
                for i, param in enumerate(device.parameters):
                    if param.is_enabled:
                        try:
                            param_info = {
                                "index": i,
                                "name": param.name if hasattr(param, "name") else "Parameter {}".format(i),
                                "value": param.value,
                                "min": param.min if hasattr(param, "min") else 0.0,
                                "max": param.max if hasattr(param, "max") else 1.0,
                                "is_quantized": hasattr(param, "is_quantized") and param.is_quantized,
                            }
                            parameters.append(param_info)
                        except Exception as e:
                            self.log_message("Error reading parameter {}: {}".format(i, str(e)))
                            continue

            result = {
                "device_name": device.name if hasattr(device, "name") else "Device {}".format(device_index),
                "device_index": device_index,
                "parameters": parameters,
            }
            return result
        except Exception as e:
            self.log_message("Error getting device parameters: " + str(e))
            raise

    def _set_device_parameter(self, track_index, device_index, parameter_index, value):
        """Set a device parameter value (normalized 0.0-1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            if hasattr(device, "parameters"):
                if parameter_index < 0 or parameter_index >= len(device.parameters):
                    raise IndexError("Parameter index out of range")

                parameter = device.parameters[parameter_index]

                # Set the parameter value
                parameter.value = value

                result = {
                    "device_name": device.name if hasattr(device, "name") else "Device {}".format(device_index),
                    "parameter_index": parameter_index,
                    "parameter_name": parameter.name if hasattr(parameter, "name") else "Parameter {}".format(parameter_index),
                    "value": value,
                }
                return result
            else:
                raise Exception("Device has no parameters")
        except Exception as e:
            self.log_message("Error setting device parameter: " + str(e))
            raise

    def _set_track_volume(self, track_index, volume):
        """Set track volume (normalized 0.0-1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.mixer_device.volume.value = volume

            result = {
                "track_name": track.name if hasattr(track, "name") else "Track {}".format(track_index),
                "volume": volume,
                "db": "TODO: convert to dB",
            }
            return result
        except Exception as e:
            self.log_message("Error setting track volume: " + str(e))
            raise

    def _set_track_mute(self, track_index, mute):
        """Mute or unmute a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.mute = mute

            result = {
                "track_name": track.name if hasattr(track, "name") else "Track {}".format(track_index),
                "mute": mute,
            }
            return result
        except Exception as e:
            self.log_message("Error setting track mute: " + str(e))
            raise

    def _set_track_solo(self, track_index, solo):
        """Solo or unsolo a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.solo = solo

            result = {
                "track_name": track.name if hasattr(track, "name") else "Track {}".format(track_index),
                "solo": solo,
            }
            return result
        except Exception as e:
            self.log_message("Error setting track solo: " + str(e))
            raise

    def _set_track_arm(self, track_index, arm):
        """Arm or unarm a track for recording"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.arm = arm

            result = {
                "track_name": track.name if hasattr(track, "name") else "Track {}".format(track_index),
                "arm": arm,
            }
            return result
        except Exception as e:
            self.log_message("Error setting track arm: " + str(e))
            raise

    def _load_instrument_preset(self, track_index, device_index, preset_name):
        """Load a preset for a device on a track by name"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            if not hasattr(device, "presets"):
                raise Exception("Device has no presets")

            # Search through presets to find matching name
            found_preset = None
            for preset in device.presets:
                if hasattr(preset, "name") and preset.name.lower() == preset_name.lower():
                    found_preset = preset
                    break

            if found_preset:
                # Found preset, load it
                device.presets = found_preset
                self.log_message("Loaded preset '{}' for device '{}' on track '{}'".format(
                    preset_name, device.name if hasattr(device, "name") else str(device_index), track.name
                ))

                result = {
                    "track_name": track.name if hasattr(track, "name") else "Track {}".format(track_index),
                    "device_name": device.name if hasattr(device, "name") else "Device {}".format(device_index),
                    "preset_name": preset_name,
                    "loaded": True,
                }
            else:
                # Preset not found
                self.log_message("Preset '{}' not found for device '{}' on track '{}'. Available presets:".format(
                    preset_name, device.name if hasattr(device, "name") else str(device_index), track.name
                ))

                # List available presets
                available_presets = []
                for preset in device.presets:
                    if hasattr(preset, "name"):
                        available_presets.append(preset.name)

                result = {
                    "track_name": track.name if hasattr(track, "name") else "Track {}".format(track_index),
                    "device_name": device.name if hasattr(device, "name") else "Device {}".format(device_index),
                    "preset_name": preset_name,
                    "loaded": False,
                    "error": "Preset not found",
                    "available_presets": available_presets,
                }

            return result
        except Exception as e:
            self.log_message("Error loading instrument preset: " + str(e))
            raise
