"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import compare, health, ingest, recommend, search, technologies


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: DB connection pool is managed by SQLAlchemy
    yield
    # Shutdown


app = FastAPI(
    title="Tech Memory API",
    description="技術収集・検索DBシステム API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(technologies.router, prefix="/api/v1/technologies", tags=["technologies"])
app.include_router(compare.router, prefix="/api/v1", tags=["compare"])
app.include_router(recommend.router, prefix="/api/v1", tags=["recommend"])
