"""WebSocket server for streaming audio analysis to dashboards."""

import asyncio
import json
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol


class AudioAnalysisWebSocketServer:
    """WebSocket server that broadcasts audio analysis data."""

    def __init__(self, port: int = 8765):
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self._running = False
        self._latest_analysis = {}

    async def handler(self, websocket: WebSocketServerProtocol):
        """Handle new WebSocket connection."""
        self.clients.add(websocket)
        try:
            # Send latest analysis on connect
            if self._latest_analysis:
                await websocket.send(json.dumps(self._latest_analysis))
            # Keep connection alive
            await websocket.wait_closed()
        finally:
            self.clients.discard(websocket)

    def broadcast(self, analysis: dict):
        """Broadcast analysis to all connected clients."""
        self._latest_analysis = analysis
        if self.clients:
            message = json.dumps(analysis)
            websockets.broadcast(self.clients, message)

    async def start(self):
        """Start the WebSocket server."""
        self._running = True
        async with websockets.serve(self.handler, "localhost", self.port):
            await asyncio.Future()  # Run forever

    def stop(self):
        """Stop the server."""
        self._running = False
