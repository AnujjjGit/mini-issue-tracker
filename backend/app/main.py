"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import app.models  # noqa: F401
from app.core.errors import register_exception_handlers
from app.database import Base, engine
from app.routers import auth, dashboard, issues, projects

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("issuetracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("application startup: database tables ready")
    yield
    logger.info("application shutdown")


app = FastAPI(
    title="Mini Issue Tracker API",
    version="1.0.0",
    description="REST API for a mini issue-tracking system (auth, projects, issues).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(dashboard.router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
