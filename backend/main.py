from fastapi import FastAPI, Query, Depends
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .connection_manager import ConnectionManager
from fastapi import WebSocket, WebSocketDisconnect
from .routes import auth
from sqlmodel import Session
from .database import get_session
from .dependencies import decode_token
from datetime import datetime, timezone
from .schemas import Message

SECRET_KEY = "72a29ca393337573268c0c33b2df524037a40ce0d7b286ef0114d3a83f08e8d2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database and tables created.")
    
    yield
    
    print("Shutting down...")


app = FastAPI(title="My API", 
              description="This is a simple API for chat-application",
              lifespan=lifespan)

app.include_router(auth.router)

manager = ConnectionManager()

@app.get("/")
async def get():
    return {"detail": "Welcome to the Chat Application API"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             session: Session = Depends(get_session),
                             token: str = Query(...)):
    user = decode_token(session=session, token=token)
    await manager.connect(websocket, token, session=session)
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            message = Message(
                user_id=user.id,
                username=user.username,
                message=message,
                time=datetime.now(timezone.utc).isoformat()
            )

            payload = message.model_dump()
            payload["user_id"] = str(payload["user_id"])
        
            await manager.send_personal_message({
                "username": "system",
                "message": f"Message received",
                "time": datetime.now(timezone.utc).isoformat()
            }, websocket)

            await manager.broadcast(payload, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected.")