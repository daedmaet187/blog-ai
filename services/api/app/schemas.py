from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    slug: str = Field(min_length=3, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    content: str = Field(min_length=1)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, pattern=r"^(draft|published)$")


class PostOut(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    status: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
