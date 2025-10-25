from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db.database import create_db_and_tables
from .api.routes import auth, ws
from .core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database and tables created.")
    
    yield
    
    print("Shutting down...")


app = FastAPI(title=settings.APP_NAME, 
              description="This is a simple API for chat-application",
              lifespan=lifespan)

app.include_router(auth.router)
app.include_router(ws.router)

@app.get("/")
async def get():
    return {"detail": "Welcome to the Chat Application API"}
