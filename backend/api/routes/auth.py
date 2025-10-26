from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.schemas.user import UserRead, UserCreate
from backend.schemas.security import Token
from sqlmodel import Session
from backend.db.database import get_session
from backend.services.auth_service import AuthService
from backend.services.exceptions import UsernameTakenError, InvalidCredentialsError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter(prefix="/auth" ,tags=["Authentication"])


@router.post("/register",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    service = AuthService(session=session)
    try:
        return service.register_user(user_data=user_data)
    except UsernameTakenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login",
             response_model=Token,
             status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    service = AuthService(session=session)
    
    try:
        user = service.authenticate_user(form_data.username, form_data.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    access_token = service.create_access_token(user_data={"sub": str(user.id), "username": user.username})
    return Token(access_token=access_token, token_type="bearer")