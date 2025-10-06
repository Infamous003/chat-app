from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..models import Token, User, UserRead, UserCreate
import jwt
from jwt.exceptions import InvalidTokenError
from ..dependencies import authenticate_user, create_access_token, get_user, get_password_hash
from sqlmodel import Session, select
from ..database import get_session

SECRET_KEY = "72a29ca393337573268c0c33b2df524037a40ce0d7b286ef0114d3a83f08e8d2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter(prefix="/auth" ,tags=["Authentication"])


def get_current_user(session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate the credentials")
        username=username
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate the credentials")
    user = get_user(username=username, session=session)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate the credentials")
    return user

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
        user.password = get_password_hash(user.password)
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

    access_token = create_access_token(user_data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

# This route is responsible for displaying the Authorize button in Swagger UI
@router.get("/users/me",
            response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user