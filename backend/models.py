from sqlmodel import SQLModel, Field
from uuid import uuid4, UUID

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str = Field(max_length=128)