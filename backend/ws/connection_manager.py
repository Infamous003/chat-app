from fastapi import WebSocket
from backend.db.models import User

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, User] = {}

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections[websocket] = user

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, sender_websocket: WebSocket):
        for connection, user in self.active_connections.items():
            if connection.client != sender_websocket.client:
                await connection.send_json(message)

manager = ConnectionManager()