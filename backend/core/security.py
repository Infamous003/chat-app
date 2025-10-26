from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlmodel import Session, select
from backend.db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_user(id: int, session: Session):
    query = select(User).where(User.id == id)
    user = session.exec(query).one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
