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
from app.services.auth import (
    create_access_token,
    create_refresh_token,
    get_cached_data_by_refresh_token,
    invalidate_access_token,
    invalidate_refresh_token
)


router = APIRouter(prefix="/v1/user")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(payload: UserSchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    _user: User = User(**payload.model_dump())
    await _user.save(db_session)
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


@router.post("/signout", status_code=status.HTTP_200_OK)
async def signout(request: Request):
    # invalidate access token
    access_token = request.state.jwt_payload.get("access_token")
    await invalidate_access_token(access_token, request)
    # invalidate refresh token
    refresh_token = request.state.jwt_payload.get("refresh_token")
    await invalidate_refresh_token(refresh_token, request)
    return {"message": "User signed out successfully"}


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenSchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    # refresh token
    refresh_token = payload.refresh_token
    # get user by refresh token
    user_id, prev_access_token = await get_cached_data_by_refresh_token(refresh_token, request)
    # get user by id
    _user = await User.find(db_session, [User.id == user_id])

    # invalidate previous access token
    await invalidate_access_token(prev_access_token, request)
    # invalidate previous refresh token
    await invalidate_refresh_token(refresh_token, request)

    # create new access token
    _token = await create_access_token(_user, request)
    # create new refresh token
    new_refresh_token = await create_refresh_token(_user, _token, request)

    return create_token_response(_token, new_refresh_token)
