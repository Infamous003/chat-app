from datetime import datetime, timezone
from backend.schemas.message import Message, MessageType
from backend.ws.connection_manager import manager, ConnectionManager
from fastapi import WebSocket
from backend.db.models import User

class ChatService:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
    
    async def handle_incoming_message(self, user: User, data: dict, websocket: WebSocket):
        if "message" not in data:
            await self.send_system_message(str(user.id), "Missing 'message' field", MessageType.ERROR)
            return
        
        message_text = data["message"]

        if not isinstance(message_text, str) or not message_text.strip():
            await self.send_system_message(str(user.id), "Empty or non-string messages are ignored", MessageType.ERROR)
            return
        
        msg = Message(
            user_id=user.id,
            username=user.username,
            message=message_text
        )
        payload = msg.model_dump(mode="json")

        await self.manager.broadcast(payload, exclude_user_id=str(user.id))
    
    async def send_system_message(self, user_id: str, text: str, message_type: MessageType):
        sys_message = Message(
            message=text,
            message_type=message_type,
        )
        payload = sys_message.model_dump(mode="json")
        await self.manager.send_personal_message(user_id, payload)
        