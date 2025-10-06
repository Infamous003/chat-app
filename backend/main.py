from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .connection_manager import ConnectionManager
from fastapi import WebSocket, WebSocketDisconnect

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

manager = ConnectionManager()

@app.get("/")
async def get():
    return {"detail": "Welcome to the Chat Application API"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message("Message received", websocket)
            await manager.broadcast(f"Client says: {data}", websocket.client)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected.")