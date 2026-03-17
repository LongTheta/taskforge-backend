"""TaskForge FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, health, notes, tasks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    yield


app = FastAPI(
    title="TaskForge API",
    description="Secure task and notes platform backend",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Routes
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
