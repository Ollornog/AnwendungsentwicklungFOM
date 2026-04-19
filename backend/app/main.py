from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import auth as auth_router
from app.routers import pricing as pricing_router
from app.routers import products as products_router

settings = get_settings()

app = FastAPI(title="KI-gestützte Preisoptimierung", version="0.1.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=settings.app_env == "production",
    max_age=60 * 60 * 8,
)

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(products_router.router, prefix="/api/v1")
app.include_router(pricing_router.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


frontend_dir = Path(settings.frontend_dir)
if frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
