"""Device knowledge base — parameter schemas for Live 12 native devices."""
import json
import os
from pathlib import Path

_device_cache = None

def _load_all_devices():
    global _device_cache
    if _device_cache is not None:
        return _device_cache
    
    devices_dir = Path(__file__).parent / "devices"
    _device_cache = []
    
    for f in sorted(devices_dir.glob("*.json")):
        with open(f) as fh:
            _device_cache.extend(json.load(fh))
    
    return _device_cache


def get_device_knowledge(device_name: str, parameter_name: str = ""):
    """Look up a device by name and optionally filter a parameter."""
    devices = _load_all_devices()
    
    for dev in devices:
        if dev["name"].lower() == device_name.lower():
            if parameter_name:
                for param in dev.get("parameters", []):
                    if parameter_name.lower() in param["name"].lower():
                        return {"device": dev["name"], "parameter": param}
                return {"device": dev["name"], "error": f"Parameter '{parameter_name}' not found"}
            return dev
    
    return {"error": f"Device '{device_name}' not found", "available_devices": [d["name"] for d in devices]}


def get_available_devices():
    """Return list of all device names in the knowledge base."""
    devices = _load_all_devices()
    return [d["name"] for d in devices]
