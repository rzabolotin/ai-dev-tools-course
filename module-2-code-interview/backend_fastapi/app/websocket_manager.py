import json
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""

    def __init__(self):
        # session_id -> list of (websocket, client_id)
        self.active_connections: Dict[str, List[tuple[WebSocket, str]]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, client_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append((websocket, client_id))

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id] = [
                (ws, cid) for ws, cid in self.active_connections[session_id] if ws != websocket
            ]
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast_to_session(
        self, session_id: str, message: dict, exclude_client_id: str = None
    ):
        """Broadcast message to all clients in a session, optionally excluding the sender."""
        if session_id not in self.active_connections:
            return

        message_json = json.dumps(message)
        disconnected = []

        for websocket, client_id in self.active_connections[session_id]:
            if exclude_client_id and client_id == exclude_client_id:
                continue
            try:
                await websocket.send_text(message_json)
            except Exception:
                disconnected.append(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws, session_id)


manager = ConnectionManager()
