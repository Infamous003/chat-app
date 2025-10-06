from fastapi import FastAPI, APIRouter, Query, Depends
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .connection_manager import ConnectionManager
from fastapi import WebSocket, WebSocketDisconnect
from .routes import auth
from sqlmodel import Session
from .database import get_session
from .dependencies import decode_token
from datetime import datetime, timezone

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

            payload = {
                "username": user.username,
                "message": message,
                "time": datetime.now(timezone.utc).isoformat()
            }
        
            await manager.send_personal_message({
                "username": "system",
                "message": f"Message received",
                "time": datetime.now(timezone.utc).isoformat()
            }, websocket)

            await manager.broadcast(payload, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected.")