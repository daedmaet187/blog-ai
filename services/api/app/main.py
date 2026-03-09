from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, posts, media, projects, payments
from .moderation import routes as moderation

app = FastAPI(title="Blog Mission Control API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.stuff187.com",
        "https://admin.stuff187.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {"service": "blog-api", "version": "0.2.0"}


app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(media.router)
app.include_router(projects.router)
app.include_router(payments.router)
app.include_router(moderation.router)
