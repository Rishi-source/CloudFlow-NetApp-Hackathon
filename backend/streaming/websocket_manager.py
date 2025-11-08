from fastapi import WebSocket
from typing import List, Dict
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_ids: Dict[WebSocket, str] = {}
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_ids[websocket] = client_id
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            del self.connection_ids[websocket]
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)
    async def send_personal(self, message: dict, user_id: str):
        disconnected = []
        for connection in self.active_connections:
            if self.connection_ids.get(connection) == user_id:
                try:
                    await connection.send_json(message)
                    print(f"Sent message to user {user_id}: {message}")
                except Exception as e:
                    print(f"Error sending to {user_id}: {e}")
                    disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)
    async def broadcast_dashboard_update(self, data: dict):
        await self.broadcast({"type": "dashboard_update", "data": data})
    async def broadcast_migration_progress(self, job_id: str, progress: float, status: str):
        await self.broadcast({"type": "migration_progress", "job_id": job_id, "progress": progress, "status": status})
    async def broadcast_alert(self, alert: dict):
        await self.broadcast({"type": "alert", "data": alert})
    async def broadcast_stream_event(self, event: dict):
        await self.broadcast({"type": "stream_event", "data": event})
    def get_connection_count(self) -> int:
        return len(self.active_connections)

websocket_manager = WebSocketManager()
