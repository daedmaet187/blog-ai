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


class ProjectRequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    package: str = Field(pattern=r"^(starter|growth|premium)$")
    brief_en: str = Field(min_length=10)
    brief_ar: str = Field(min_length=10)


class ProjectRequestOut(BaseModel):
    id: int
    client_user_id: int
    title: str
    package: str
    brief_en: str
    brief_ar: str
    state: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepositSessionCreate(BaseModel):
    project_id: int


class DepositSessionOut(BaseModel):
    project_id: int
    state: str
    session_id: str
    checkout_url: str


class FinalPaymentSessionCreate(BaseModel):
    project_id: int


class FinalPaymentSessionOut(BaseModel):
    project_id: int
    state: str
    session_id: str
    checkout_url: str


class ClarificationQuestionOut(BaseModel):
    id: int
    project_id: int
    question_key: str
    question_text: str
    answer_text: str | None

    class Config:
        from_attributes = True


class ClarificationStartOut(BaseModel):
    project_id: int
    state: str
    questions: list[ClarificationQuestionOut]


class ClarificationAnswerIn(BaseModel):
    question_id: int
    answer_text: str = Field(min_length=1)


class ClarificationAnswersSubmitIn(BaseModel):
    answers: list[ClarificationAnswerIn]


class ClarificationAnswersSubmitOut(BaseModel):
    project_id: int
    state: str
    pending_questions: list[ClarificationQuestionOut]


class DesignBriefGenerateOut(BaseModel):
    project_id: int
    state: str
    brief_id: int
    brief_text: str


class AdminDesignDecisionOut(BaseModel):
    project_id: int
    state: str


class BuildGenerateOut(BaseModel):
    project_id: int
    state: str
    repo_full_name: str
    repo_url: str
    generated_files: list[str]


class DeploySubmitOut(BaseModel):
    project_id: int
    state: str
    deploy_status: str
    preview_url: str


class AdminDeployDecisionOut(BaseModel):
    project_id: int
    state: str
    deploy_status: str
    preview_url: str


class DomainMappingOut(BaseModel):
    project_id: int
    state: str
    deploy_status: str
    domain: str


class AdminApprovalQueueItemOut(BaseModel):
    project_id: int
    title: str
    state: str
    updated_at: datetime
