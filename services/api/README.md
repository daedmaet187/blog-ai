# API Service (FastAPI)

## Run locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints
- `GET /` - service info
- `GET /health` - healthcheck
- `POST /auth/register` - create first admin user
- `POST /auth/login` - get JWT token
- `GET /posts` - list published posts
- `GET /posts/{slug}` - public post detail
- `POST /posts` - create draft post (admin/editor)
- `PATCH /posts/{id}` - update/publish post (admin/editor)
