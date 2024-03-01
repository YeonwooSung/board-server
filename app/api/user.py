from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# custom imports
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserSchema,
    UserResponse,
    UserLogin,
    TokenResponse,
    RefreshTokenSchema,
    create_token_response
)
from app.services.auth import create_access_token, create_refresh_token, get_user_info_by_refresh_token


router = APIRouter(prefix="/v1/user")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(payload: UserSchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    _user: User = User(**payload.model_dump())
    await _user.save(db_session)

    # _user.access_token = await create_access_token(_user, request)
    # _user.refresh_token = await create_refresh_token(_user, _user.access_token, request)
    return _user


@router.post("/signin", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def get_token_for_user(user: UserLogin, request: Request, db_session: AsyncSession = Depends(get_db)):
    _user: User = await User.find(db_session, [User.email == user.email])

    if not _user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not _user.check_password(user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect")

    _token = await create_access_token(_user, request)
    _refresh_token = await create_refresh_token(_user, _token, request)
    return create_token_response(_token, _refresh_token)


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenSchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    # refresh token
    refresh_token = payload.refresh_token
    user_email = await get_user_info_by_refresh_token(refresh_token, request)
    _user = await User.find(db_session, [User.email == user_email])

    # create new access token
    _token = await create_access_token(_user, request)
    # create new refresh token
    _refresh_token = await create_refresh_token(_user, _token, request)
    return create_token_response(_token, _refresh_token)
