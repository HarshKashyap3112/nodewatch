
from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.auth.schemas import RegisterIn, LoginIn, TokenOut, UserOut, UserUpdateIn, ResetPasswordIn
from src.auth.service import AuthService
from src.database import get_db


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/reset-password", response_model=UserOut)
async def reset_password(
    payload: ResetPasswordIn,
    db: AsyncSession = Depends(get_db)
):
    user = await AuthService.reset_password(db, payload)
    return user



@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register_user(db, payload)
    return user


@router.post("/login", response_model=TokenOut)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    content_type = request.headers.get("content-type", "")
    email: Optional[str] = None
    password: Optional[str] = None

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = str(form.get("username") or form.get("email") or "")
        password = str(form.get("password") or "")
    else:
        try:
            body = await request.json()
            if isinstance(body, dict):
                email = str(body.get("email") or body.get("username") or "")
                password = str(body.get("password") or "")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email/username and password are required"
        )


    token = await AuthService.authenticate_user(db, email, password)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    payload: UserUpdateIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_user = await AuthService.update_user(db, current_user.id, payload)
    return updated_user

