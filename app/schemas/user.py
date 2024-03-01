from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, ConfigDict

config = ConfigDict(from_attributes=True)


# TODO: add pydantic field validator for strong password
class UserSchema(BaseModel):
    model_config = config
    email: EmailStr = Field(title="User’s email", description="User’s email")
    first_name: str = Field(title="User’s first name", description="User’s first name")
    last_name: str = Field(title="User’s last name", description="User’s last name")
    password: str = Field(title="User’s password", description="User’s password")
    nickname: str = Field(title="User’s nickname", description="User’s nickname")


class UserResponse(BaseModel):
    id: UUID = Field(title="User’s id", description="User’s id")
    email: EmailStr = Field(title="User’s email", description="User’s email")
    first_name: str = Field(title="User’s first name", description="User’s first name")
    last_name: str = Field(title="User’s last name", description="User’s last name")


class TokenResponse(BaseModel):
    access_token: str = Field(title="User’s access token", description="User’s access token")
    token_type: str = Field(title="User’s token type", description="User’s token type")
    refresh_token: str = Field(title="User’s refresh token", description="User’s refresh token")


class UserLogin(BaseModel):
    model_config = config
    email: EmailStr = Field(title="User’s email", description="User’s email")
    password: str = Field(title="User’s password", description="User’s password")


class RefreshTokenSchema(BaseModel):
    refresh_token: str = Field(title="User’s refresh token", description="User’s refresh token")


def create_token_response(token: str, refresh_token: str) -> dict:
    return {
        "access_token": token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }
