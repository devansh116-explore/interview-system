"""FastAPI application entrypoint."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 -- ensures models are registered before create_all
from app.routers import resume, interview, knowledge_base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PGAGI AI Interview System",
    description="RAG-powered role-based candidate screening system.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred.", "error_type": type(exc).__name__},
    )


app.include_router(resume.router)
app.include_router(interview.router)
app.include_router(knowledge_base.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
