from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..middleware.age_verification import verify_age

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=Token)
async def register(
    email: str,
    password: str,
    birth_date: str,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if user exists
    if await get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify age
    if not await verify_age(birth_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must be 21 or older to register"
        )
    
    # Create user
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        birth_date=birth_date
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return JWT token."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return await db.query(User).filter(User.email == email).first()

async def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
