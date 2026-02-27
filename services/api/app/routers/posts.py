from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, current_user
from ..models import Post, User
from ..schemas import PostCreate, PostUpdate, PostOut

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.status == "published").order_by(Post.id.desc()).all()


@router.get("/{slug}", response_model=PostOut)
def get_post(slug: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug, Post.status == "published").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", response_model=PostOut)
def create_post(payload: PostCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    if db.query(Post).filter(Post.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="Slug already exists")
    post = Post(title=payload.title, slug=payload.slug, content=payload.content, author_id=user.id, status="draft")
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.patch("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(post, key, value)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
