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
    auth_service = AuthService(session=session)
    chat_service = ChatService(manager=manager)

    user = auth_service.decode_access_token(token=token)
    await manager.connect(websocket, user)
    
    try:
        while True:
            data = await websocket.receive_json()
            await chat_service.handle_incoming_message(user, data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(str(user.id)) # converting UUID to string
        await manager.broadcast(f"#{user.username} has left the chat", str(user.id))