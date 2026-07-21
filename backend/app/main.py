from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import analytics, redirect, shorten

app = FastAPI(title="URL Shortener")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Order matters: literal /api/... routes must be registered before the
# catch-all single-segment /{short_code} route.
app.include_router(shorten.router)
app.include_router(analytics.router)
app.include_router(redirect.router)
