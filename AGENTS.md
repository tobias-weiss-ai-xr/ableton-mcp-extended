# AGENTS.md - Agent Guidelines for ableton-mcp-extended

This file provides coding guidelines and commands for agentic coding agents working in this repository.

## Build, Lint, and Test Commands

### Installation
```bash
pip install -e .
```

### Running the MCP Server
```bash
python MCP_Server/server.py
```

### Running Automation Scripts
```bash
# 2-Hour Dub Techno Project (all scripts in dub_techno_2h/)
cd dub_techno_2h

# Create 2-hour dub techno project
python create_2h_dub_techno_fixed.py

# Load instruments and effects
python load_instruments_and_effects.py

# Run full automation
python auto_play_2h_dub_techno.py

# Test and utility scripts
cd ../scripts
python test/test_connection.py
python util/check_tracks.py
```

### Testing
This project currently does not have automated tests. Test by:
1. Ensure Ableton Live 11+ is running with the AbletonMCP Remote Script loaded
2. Run individual scripts to verify functionality
3. Test MCP tools via Claude Desktop or Cursor IDE

### Linting/Type Checking
No linting or type checking is currently configured. You may manually run:
```bash
# Optional: Install and run ruff for linting
pip install ruff
ruff check .

# Optional: Install and run mypy for type checking
pip install mypy
mypy MCP_Server/
```

## Code Style Guidelines

### Python Version
- **Required**: Python 3.10+
- **Tested on**: Python 3.12.2

### Import Organization
- Standard library imports first (socket, json, time, logging, threading)
- Third-party imports second (mcp, elevenlabs)
- Local imports last (if any)
- Use absolute imports where possible

Example:
```python
import socket
import json
import time
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Union

from mcp.server.fastmcp import FastMCP, Context
```

### Naming Conventions
- **Functions**: `snake_case` (send_command, get_session_info, create_midi_track)
- **Classes**: `PascalCase` (AbletonMCP, AbletonConnection)
- **Constants**: `UPPER_SNAKE_CASE` (DEFAULT_PORT, HOST)
- **Variables**: `snake_case` (track_index, device_index, normalized_volume)
- **Private methods**: `_leading_underscore` (_server_thread, _handle_client)

### Type Hints
- Use type hints for function parameters and return values (especially in MCP_Server/)
- Import from `typing` module: `Dict, Any, List, Union, Optional`
- For MCP tool functions, use `Context` parameter from FastMCP

Example:
```python
def send_command(cmd_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send a command and return the response"""
    pass
```

### Error Handling
- Use try-except blocks for operations that may fail (socket operations, Ableton commands)
- Log errors using the `logger` object from logging module
- For non-critical errors (automation warnings), print with `[WARNING]` prefix
- Re-raise critical exceptions after logging

Example:
```python
try:
    result = send_command("get_session_info")
    return json.dumps(result, indent=2)
except Exception as e:
    logger.error(f"Error getting session info: {str(e)}")
    return f"Error: {str(e)}"
```

### Socket Communication Pattern
All scripts follow this pattern for communicating with Ableton:
1. Create socket: `s = socket.socket()`
2. Connect: `s.connect(("localhost", 9877))`
3. Define helper: `send_command(cmd_type, params)`
4. Send JSON: `json.dumps({"type": cmd_type, "params": params}).encode("utf-8")`
5. Receive response: `s.recv(8192)` (may need chunked receive for large responses)
6. Parse JSON: `json.loads(data.decode("utf-8"))`
7. Close socket: `s.close()` (or keep persistent connection for multiple commands)

### Docstrings and Comments
- Use triple-quoted docstrings for functions (especially in MCP_Server/)
- Keep docstrings concise, describing purpose and parameters
- Use section dividers for major code sections:
  ```python
  # ============================================================================
  # SECTION TITLE
  # ============================================================================
  ```

### Data Structures
- **MIDI notes**: List of dicts with keys: `pitch`, `start_time`, `duration`, `velocity`, `mute`
- **Section definitions**: Dicts with `name`, `description`, `clips`, `filter_freq`, `reverb_send`, etc.
- **Track/clip indices**: 0-based integers

### Logging Configuration
Use the standard logging module with consistent formatting:
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ModuleName")
```

### Threading (AbletonMCP Remote Script)
- Use daemon threads for background tasks
- Keep track of client threads in a list
- Clean up finished threads regularly
- Use socket timeouts to allow graceful shutdown

### MCP Tool Decorators
For tools in MCP_Server/, use the `@mcp.tool()` decorator:
```python
@mcp.tool()
def get_session_info(ctx: Context) -> str:
    """Get detailed information about the current Ableton session"""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
```

### File Organization
- `MCP_Server/server.py`: Main MCP server implementation
- `AbletonMCP_Remote_Script/__init__.py`: Ableton Live Remote Script (Python 2/3 compatible)
- `dub_techno_2h/`: 2-hour dub techno automation scripts
  - `create_2h_dub_techno_fixed.py`: Creates tracks and clips
  - `load_instruments_and_effects.py`: Loads instruments and effects
  - `auto_play_2h_dub_techno.py`: Full 2-hour automation
  - `automate_all_setup.py`: All-in-one setup script
  - `archive/`: Older versions and deprecated scripts
- `scripts/`: Utility and test scripts
  - `test/`: Test scripts
  - `util/`: Utility scripts
- ElevenLabs integration in `elevenlabs_mcp/server.py`

### Specific Guidelines for This Codebase

1. **Ableton Connection**: Always validate connection before sending commands
2. **Normalized Values**: Device parameters use 0.0-1.0 range
3. **Delay Commands**: Add `time.sleep(0.1)` after state-modifying commands
4. **Large Responses**: Use chunked receive for responses > 8192 bytes
5. **Recovery**: Continue execution on non-critical automation errors
6. **Progress Indicators**: Print clear status messages during long operations

### Python 2/3 Compatibility (AbletonMCP_Remote_Script)
The Remote Script must run in Python 2:
```python
from __future__ import absolute_import, print_function, unicode_literals
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3
```

### When in Doubt
- Follow existing patterns in similar files
- Look at `MCP_Server/server.py` for MCP tool examples
- Check `dub_techno_2h/create_2h_dub_techno_fixed.py` for automation script structure
- Reference `dub_techno_2h/auto_play_2h_dub_techno.py` for advanced automation patterns
