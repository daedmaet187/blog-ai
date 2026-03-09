from datetime import datetime
from enum import Enum
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


class ModerationReasonCode(str, Enum):
    BLOCKED_WORD = "BLOCKED_WORD"
    TOO_MANY_LINKS = "TOO_MANY_LINKS"
    DUPLICATE_CONTENT = "DUPLICATE_CONTENT"
    TOO_MANY_MEDIA = "TOO_MANY_MEDIA"


class ModerationDecision(str, Enum):
    PASS = "PASS"
    FLAG = "FLAG"


class ModerationResult(BaseModel):
    decision: ModerationDecision
    reasons: list[ModerationReasonCode] = Field(default_factory=list)


class PublishPostResponse(BaseModel):
    post: PostOut
    moderation: ModerationResult


class ModerationQueueItemOut(BaseModel):
    id: int
    post_id: int
    decision: str
    reasons: list[ModerationReasonCode]
    status: str
    created_at: datetime
    updated_at: datetime
    resolved_by_user_id: int | None = None
    resolution_note: str | None = None


class ModerationOverrideIn(BaseModel):
    action: str = Field(pattern=r"^(approve|reject)$")
    note: str | None = Field(default=None, max_length=500)
