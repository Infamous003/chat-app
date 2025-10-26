from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from backend.db.models import User
from backend.schemas.user import UserCreate, UserRead
from backend.core.config import settings
from backend.core.security import hash_password, verify_password, get_user
from backend.services.exceptions import UsernameTakenError, InvalidCredentialsError
import jwt
from jose import JWTError

class AuthService:
    # injecting the db session
    def __init__(self, session: Session):
        self.session = session
    
    def register_user(self, user_data: UserCreate) -> UserRead:
        query = select(User).where(User.username == user_data.username)
        user = self.session.exec(query).one_or_none()

        if user is not None:
            raise UsernameTakenError()
        
        hashed_password = hash_password(user_data.password)
        user = User(**user_data.model_dump())
        user.password = hashed_password

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user
    
    def authenticate_user(self, username: str, password: str) -> UserRead:
        query = select(User).where(User.username == username)
        user = self.session.exec(query).one_or_none()
        
        if user is None or not verify_password(password, user.password):
            raise InvalidCredentialsError()
        return user   

    def create_access_token(self, user_data: dict) :
        
        to_encode = user_data.copy()

        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    def decode_access_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise InvalidCredentialsError("Invalid JWT token")
        except JWTError:
            raise InvalidCredentialsError("Invalid JWT token")
        
        user = get_user(id=user_id, session=self.session)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user