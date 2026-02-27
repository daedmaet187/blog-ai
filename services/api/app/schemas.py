from pydantic import BaseModel, EmailStr


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str
    slug: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None


class PostOut(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    status: str
    author_id: int

    class Config:
        from_attributes = True
