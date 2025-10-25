from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4, UUID
from datetime import datetime, timezone


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    id: UUID
    username: str
    email: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None


# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str


class MessageType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ERROR = "error"

class Message(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    user_id: UUID | None = None
    message: str
    username: str | None = None

    message_type: MessageType = Field(default=MessageType.USER)
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

