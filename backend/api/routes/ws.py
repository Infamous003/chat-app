from fastapi import WebSocket, Depends, Query, APIRouter, WebSocketDisconnect
from sqlmodel import Session
from backend.db.database import get_session
from backend.ws.connection_manager import manager
from backend.schemas.message import Message, MessageType
from backend.services.auth_service import AuthService
from backend.services.chat_service import ChatService

router = APIRouter(prefix="/ws", tags=["Websocket"])

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket,
                             session: Session = Depends(get_session),
                             token: str = Query(...)):
    service = AuthService(session=session)
    user = service.decode_access_token(token=token)
    user_id = str(user.id)

    await manager.connect(websocket, user)
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            message = Message(
                user_id=user_id,
                username=user.username,
                message=message
            )
            
            payload = message.model_dump(mode="json")
            payload["user_id"] = str(payload["user_id"])

            await manager.broadcast(payload, user_id)

            system_payload = Message(
                message_type=MessageType.SYSTEM,
                message="Received"
            )
            await manager.send_personal_message(
                user_id,
                system_payload.model_dump(mode="json")
            )

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"#{user.username} has left the chat", user_id)