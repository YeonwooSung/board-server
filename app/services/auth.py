import time
import jwt

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# custom imports
from app.config import settings as global_settings
from app.models.user import User


async def verify_jwt(request: Request, token: str) -> bool:
    _payload = await request.app.state.redis.get(token)
    if _payload:
        return True
    else:
        return False


class AuthBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not await verify_jwt(request, credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


async def create_access_token(user: User, request: Request):
    _payload = {
        "id": user.id,
        "email": user.email,
        "expiry": time.time() + global_settings.jwt_expire,
        "platform": request.headers.get("User-Agent"),
    }
    _token = jwt.encode(_payload, str(user.password), algorithm=global_settings.jwt_algorithm)

    _bool = await request.app.state.redis.set(_token, str(_payload), ex=global_settings.jwt_expire)
    if _bool:
        return _token


async def create_refresh_token(user: User, access_token: str, request: Request):
    _payload = {
        "access_token": access_token,
        "email": user.email,
        "expiry": time.time() + global_settings.jwt_refresh_expire,
        "platform": request.headers.get("User-Agent"),
    }
    _refresh_token_key = global_settings.jwt_refresh_key
    _token = jwt.encode(_payload, _refresh_token_key, algorithm=global_settings.jwt_algorithm)

    _bool = await request.app.state.redis.set(_token, str(_payload), ex=global_settings.jwt_refresh_expire)
    if _bool:
        return _token


async def get_user_info_by_refresh_token(refresh_token: str, request: Request) -> str:
    _data = await request.app.state.redis.get(refresh_token)
    if not _data:
        raise HTTPException(status_code=403, detail="Invalid refresh token or expired token.")
    # decode the data
    _decoded = jwt.decode(_data, global_settings.jwt_refresh_key, algorithms=[global_settings.jwt_algorithm])
    email = _decoded.get("email", None)
    if not email:
        raise HTTPException(status_code=403, detail="Invalid refresh token or expired token.")
    return email
