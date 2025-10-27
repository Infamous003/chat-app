from datetime import datetime, timezone
from backend.schemas.message import Message, MessageType
from backend.ws.connection_manager import manager, ConnectionManager
from fastapi import WebSocket

class ChatService:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
    
    async def handle_message(self, user, data: dict, websocket: WebSocket):
        message_text = data.get("message")

        if not message_text:
            await self.send_system_message("Empty message ignored", websocket)
        
        msg = Message(
            user_id=user.id,
            username=user.username,
            message=message_text
        )

        await self.manager.broadcast(msg.model_dump(mode="json"), sender=websocket)
    
    async def send_system_message(self, text: str, websocket, msg_type: MessageType):
        sys_message = Message(
            message=text,
            message_type=msg_type,
        )
        await self.manager.send_personal_message(sys_message.model_dump(mode="json"), websocket)
        