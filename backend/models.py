from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str = Field(max_length=128)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    id: int
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
    user_id: int
    username: str
    message: str
    time: str