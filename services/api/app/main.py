from fastapi import FastAPI

app = FastAPI(title="Blog Mission Control API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {"service": "blog-api", "version": "0.1.0"}
