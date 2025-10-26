from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.db.models import User
from backend.schemas.user import UserRead, UserCreate
from backend.schemas.security import Token
from backend.core.security import authenticate_user
from backend.core.security import create_access_token, hash_password
from sqlmodel import Session, select
from backend.db.database import get_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter(prefix="/auth" ,tags=["Authentication"])

@router.post("/register",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
def register(user_credentials: UserCreate, session: Session = Depends(get_session)):
    query = select(User).where(User.username == user_credentials.username)
    user = session.exec(query).one_or_none()

    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    else:
        user = User(**user_credentials.model_dump())
        user.password = hash_password(user.password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.post("/login",
             response_model=Token,
             status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(user_data={"sub": str(user.id), "username": user.username})
    return Token(access_token=access_token, token_type="bearer")
