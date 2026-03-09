from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..deps import get_db, current_user
from ..models import Post, User
from ..schemas import (
    PostCreate,
    PostUpdate,
    PostOut,
    PublishPostResponse,
)
from ..posts.service import evaluate_post_moderation

router = APIRouter(prefix="/posts", tags=["posts"])


AUTHORING_ROLES = {"admin", "editor"}


def _ensure_editor(user: User):
    if (user.role or "").lower() not in AUTHORING_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("", response_model=list[PostOut])
def list_posts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(Post)
        .filter(Post.status == "published")
        .order_by(Post.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/admin", response_model=list[PostOut])
def admin_list_posts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status: str | None = Query(default=None, pattern=r"^(draft|published)$"),
    q: str | None = Query(default=None, min_length=1, max_length=255),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _ensure_editor(user)

    query = db.query(Post)
    if status:
        query = query.filter(Post.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Post.title.ilike(like), Post.slug.ilike(like)))

    return query.order_by(Post.id.desc()).offset(skip).limit(limit).all()


@router.get("/{slug}", response_model=PostOut)
def get_post(slug: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug, Post.status == "published").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", response_model=PostOut)
def create_post(payload: PostCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _ensure_editor(user)
    if db.query(Post).filter(Post.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="Slug already exists")
    post = Post(title=payload.title, slug=payload.slug, content=payload.content, author_id=user.id, status="draft")
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.patch("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _ensure_editor(user)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(post, key, value)
    post.updated_at = datetime.utcnow()

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.post(
    "/{post_id}/publish",
    response_model=PublishPostResponse,
    description="Publish a post. Allowed roles: admin, editor.",
    responses={403: {"description": "Forbidden for non-editor roles"}},
)
def publish_post(post_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _ensure_editor(user)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "published"
    post.updated_at = datetime.utcnow()
    db.add(post)
    db.commit()
    db.refresh(post)

    return PublishPostResponse(
        post=post,
        moderation=evaluate_post_moderation(db, post),
    )


@router.delete("/{post_id}")
def delete_post(post_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _ensure_editor(user)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"ok": True, "deleted_id": post_id}
