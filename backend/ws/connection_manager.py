from fastapi import WebSocket
from backend.db.models import User

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections[str(user.id)] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, user_id: str, message: dict):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict, exclude_user_id: str | None = None):
        for user_id, ws in self.active_connections.items():
            if user_id != exclude_user_id:
                await ws.send_json(message)

manager = ConnectionManager()