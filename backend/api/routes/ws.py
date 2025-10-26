from fastapi import WebSocket, Depends, Query, APIRouter, WebSocketDisconnect
from sqlmodel import Session
from backend.db.database import get_session
from backend.core.security import decode_access_token
from backend.ws.connection_manager import manager
from backend.schemas.message import Message, MessageType

router = APIRouter(prefix="/ws", tags=["Websocket"])

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket,
                             session: Session = Depends(get_session),
                             token: str = Query(...)):
    user = decode_access_token(session=session, token=token)
    await manager.connect(websocket, token, session=session)
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            message = Message(
                user_id=user.id,
                username=user.username,
                message=message
            )
            
            payload = message.model_dump(mode="json")
            payload["user_id"] = str(payload["user_id"])

            await manager.broadcast(payload, websocket)

            system_payload = Message(
                message_type=MessageType.SYSTEM,
                message="Received"
            )
            await manager.send_personal_message(system_payload.model_dump(mode="json"), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected.", websocket)