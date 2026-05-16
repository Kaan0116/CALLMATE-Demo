"""
WebSocket connection manager for multi-call, multi-client fan-out.
"""
import asyncio
import json
from collections import defaultdict
from fastapi import WebSocket
import structlog

log = structlog.get_logger()


class ConnectionManager:
    def __init__(self):
        # call_id -> list of WebSocket connections
        self._call_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, call_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._call_connections[call_id].append(websocket)
        log.info("ws_connected", call_id=call_id, total=len(self._call_connections[call_id]))

    async def disconnect(self, call_id: str, websocket: WebSocket):
        async with self._lock:
            connections = self._call_connections.get(call_id, [])
            if websocket in connections:
                connections.remove(websocket)
            if not connections:
                self._call_connections.pop(call_id, None)
        log.info("ws_disconnected", call_id=call_id)

    async def broadcast(self, call_id: str, message: dict):
        """Send JSON message to all clients subscribed to this call."""
        payload = json.dumps(message, ensure_ascii=False, default=str)
        async with self._lock:
            connections = list(self._call_connections.get(call_id, []))

        dead: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    try:
                        self._call_connections[call_id].remove(ws)
                    except ValueError:
                        pass

    async def send_personal(self, websocket: WebSocket, message: dict):
        payload = json.dumps(message, ensure_ascii=False, default=str)
        await websocket.send_text(payload)

    def active_call_ids(self) -> list[str]:
        return list(self._call_connections.keys())


call_manager = ConnectionManager()
coaching_manager = ConnectionManager()
