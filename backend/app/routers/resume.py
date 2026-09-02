"""Candidate Entry + Resume Processing stages."""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session as DBSession

from app import models
from app.config import settings
from app.database import get_db
from app.schemas import ResumeUploadResponse
from app.services.resume_parser import parse_resume

router = APIRouter(prefix="/api/resume", tags=["resume"])

ALLOWED_SUFFIXES = {".pdf", ".txt"}
UPLOAD_DIR = Path(settings.base_dir) / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), db: DBSession = Depends(get_db)):
    if file.filename is None or not file.filename.strip():
        raise HTTPException(status_code=422, detail="A resume filename is required.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=422, detail="Only .pdf and .txt resumes are supported.")

    temp_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        parsed = parse_resume(temp_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse resume: {exc}") from exc
    finally:
        temp_path.unlink(missing_ok=True)

    if not parsed.raw_text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in the uploaded file.")

    candidate = models.Candidate(
        resume_filename=file.filename,
        raw_text=parsed.raw_text,
        extracted_skills=parsed.skills,
        extracted_years_experience=parsed.years_experience,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return ResumeUploadResponse(
        candidate_id=candidate.id,
        extracted_skills=parsed.skills,
        years_experience=parsed.years_experience,
        text_preview=parsed.raw_text[:400],
    )
