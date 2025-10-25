from pydantic import BaseModel, Field, UUID4
from enum import Enum
from uuid import uuid4, UUID


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


class Message(BaseModel):
    user_id: UUID4
    username: str
    message: str
    time: str