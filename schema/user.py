from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    avatar_url: str | None = None
    bio: str | None = None
    is_vendor: bool = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    avatar_url: str | None = None
    bio: str | None = None
    location_sharing: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    full_name: str
    email: EmailStr
    phone: str | None
    avatar_url: str | None
    bio: str | None
    is_vendor: bool
    location_sharing: bool
    created_at: datetime
