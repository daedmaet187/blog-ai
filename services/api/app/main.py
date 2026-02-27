from fastapi import FastAPI
from .db import Base, engine
from .routers import auth, posts

app = FastAPI(title="Blog Mission Control API", version="0.2.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {"service": "blog-api", "version": "0.2.0"}


app.include_router(auth.router)
app.include_router(posts.router)
