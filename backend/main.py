from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine, create_db_and_tables
from .connection_manager import ConnectionManager
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "WHat's up!?"}


@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected.")