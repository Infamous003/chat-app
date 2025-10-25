from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4, UUID
from datetime import datetime, timezone


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
