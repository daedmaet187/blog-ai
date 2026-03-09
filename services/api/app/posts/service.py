from sqlalchemy.orm import Session

from ..models import Post
from ..moderation.engine import evaluate_content
from ..schemas import ModerationResult


def evaluate_post_moderation(db: Session, post: Post) -> ModerationResult:
    existing_contents = [
        row[0]
        for row in db.query(Post.content)
        .filter(Post.id != post.id)
        .all()
    ]
    return evaluate_content(post.content, existing_contents=existing_contents)
