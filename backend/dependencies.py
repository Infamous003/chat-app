from fastapi import HTTPException, status
from sqlmodel import Session, select
from .models import User
from datetime import datetime, timedelta, timezone
import jwt
from bcrypt import hashpw, gensalt


SECRET_KEY = "72a29ca393337573268c0c33b2df524037a40ce0d7b286ef0114d3a83f08e8d2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Helper functions for authentication
def get_password_hash(password):
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return hashpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')) == hashed_password.encode('utf-8')

def get_user(username: str, session: Session):
    query = select(User).where(User.username == username)
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

def create_access_token(user_data: dict):
    # user_data dictionary contains the username
    to_encode = user_data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt