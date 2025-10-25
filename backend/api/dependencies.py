from fastapi import HTTPException, status
from sqlmodel import Session, select
from ..db.models import User
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError 
from bcrypt import hashpw, gensalt


SECRET_KEY = "72a29ca393337573268c0c33b2df524037a40ce0d7b286ef0114d3a83f08e8d2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Helper functions for authentication
def get_password_hash(password):
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return hashpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')) == hashed_password.encode('utf-8')


def get_user(id: int, session: Session):
    query = select(User).where(User.id == id)
    user = session.exec(query).one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def decode_token(session: Session, token: str):
    print("Decoding token:", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    # user_data dictionary contains the username and id of the user
    to_encode = user_data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt