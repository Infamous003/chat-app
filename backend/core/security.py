from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from jose import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from backend.core.config import settings
from sqlmodel import Session, select
from backend.db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_data: dict):
    # user_data dictionary contains the username and id of the user
    to_encode = user_data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def decode_access_token(session: Session, token: str):
    print("Decoding token:", token)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except InvalidTokenError:
        print("Invalid token error")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = get_user(id=user_id, session=session)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

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