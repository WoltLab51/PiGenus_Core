from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel
from pigenus.security.dependencies import get_db, get_current_user
from pigenus.models.user import User
from pigenus.services.user_service import create_user, authenticate_user, get_user_count
from pigenus.security.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    is_admin: bool


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, session: Session = Depends(get_db)):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    count = get_user_count(session)
    is_admin = count == 0
    user = create_user(data.username, data.email, data.password, session, is_admin=is_admin)
    return UserResponse(id=user.id, username=user.username, email=user.email,
                        is_active=user.is_active, is_admin=user.is_admin)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user.id, "username": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
    )
