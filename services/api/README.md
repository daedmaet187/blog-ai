# API Service (FastAPI)

## Run locally
```bash
pip install -r requirements.txt
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints
- `GET /` - service info
- `GET /health` - healthcheck
- `POST /auth/register` - create first admin user
- `POST /auth/login` - get JWT token
- `GET /auth/me` - current user
- `GET /posts` - list published posts
- `GET /posts/admin` - list all posts for admin/editor
- `GET /posts/{slug}` - public post detail
- `POST /posts` - create draft post (admin/editor)
- `PATCH /posts/{id}` - update/publish post (admin/editor)
- `DELETE /posts/{id}` - delete post (admin/editor)
- `POST /media/presign` - get S3 presigned upload URL (admin/editor)

## Environment
- `DATABASE_URL` - postgres/sqlite DSN
- `MEDIA_BUCKET` - S3 bucket used for image uploads
- `AWS_REGION` - defaults to `eu-central-1`
