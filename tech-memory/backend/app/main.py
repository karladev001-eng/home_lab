from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ingest import router as ingest_router
from app.api.search import router as search_router
from app.api.technologies import router as tech_router

app = FastAPI(
    title="Tech Memory API",
    description="Technology knowledge collection and search system",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(tech_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
