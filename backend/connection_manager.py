from fastapi import WebSocket, WebSocketDisconnect
from .dependencies import decode_token
from .database import get_session
from sqlmodel import Session
from .schemas import Message

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, token: str, session: Session):
        await websocket.accept()
        self.active_connections.append(websocket)
        user = decode_token(token=token, session=session)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, sender_websocket: WebSocket):
        for connection in self.active_connections:
            if connection.client != sender_websocket.client:
                await connection.send_json(message)