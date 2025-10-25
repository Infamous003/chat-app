from pydantic import BaseModel


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