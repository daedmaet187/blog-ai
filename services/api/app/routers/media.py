import os
import uuid
from datetime import datetime, timezone

import boto3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..deps import current_user
from ..models import User

router = APIRouter(prefix="/media", tags=["media"])


class MediaPresignIn(BaseModel):
    filename: str = Field(min_length=3, max_length=255)
    content_type: str = Field(default="image/jpeg", min_length=3, max_length=100)


class MediaPresignOut(BaseModel):
    upload_url: str
    public_url: str
    key: str
    expires_in: int = 900


def _ensure_editor(user: User):
    if user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/presign", response_model=MediaPresignOut)
def create_upload_url(payload: MediaPresignIn, user: User = Depends(current_user)):
    _ensure_editor(user)

    bucket = os.getenv("MEDIA_BUCKET")
    region = os.getenv("AWS_REGION", "eu-central-1")
    if not bucket:
        raise HTTPException(status_code=503, detail="MEDIA_BUCKET is not configured")

    ext = payload.filename.rsplit(".", 1)[-1].lower() if "." in payload.filename else "bin"
    safe_ext = "jpg" if ext == "jpeg" else ext
    key = f"uploads/{datetime.now(timezone.utc).strftime('%Y/%m/%d')}/{uuid.uuid4().hex}.{safe_ext}"

    s3 = boto3.client("s3", region_name=region)
    try:
        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket,
                "Key": key,
                "ContentType": payload.content_type,
            },
            ExpiresIn=900,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create upload URL: {e}")

    public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return MediaPresignOut(upload_url=upload_url, public_url=public_url, key=key)
