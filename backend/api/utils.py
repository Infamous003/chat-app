from fastapi import HTTPException, status
from sqlmodel import Session, select
from backend.db.models import User
from backend.core.security import verify_password


def get_user(id: int, session: Session):
    query = select(User).where(User.id == id)
    user = session.exec(query).one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

    
def authenticate_user(username: str, password: str, session: Session):
    user = None
    
    query = select(User).where(User.username == username)
    user = session.exec(query).one_or_none()

    if user is None:
        return False
    if not verify_password(password, user.password):
        return False
    return user