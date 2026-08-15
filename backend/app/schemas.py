"""Pydantic request/response models (the API's public contract)."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    candidate_id: str
    extracted_skills: List[str]
    years_experience: Optional[int] = None
    text_preview: str


class RoleInfo(BaseModel):
    role_id: str
    label: str
    document_count: int


class StartInterviewRequest(BaseModel):
    candidate_id: str
    role: str


class RetrievedChunkOut(BaseModel):
    source: str
    snippet: str
    score: float


class QuestionOut(BaseModel):
    session_id: str
    question_number: int
    total_questions: int
    topic: Optional[str]
    question_text: str
    retrieved_context: List[RetrievedChunkOut]
    status: str


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer_text: str


class QAItemOut(BaseModel):
    question_number: int
    topic: Optional[str]
    question_text: str
    answer_text: Optional[str]
    answer_quality: Optional[str]

    class Config:
        from_attributes = True


class SessionSummaryOut(BaseModel):
    session_id: str
    candidate_id: str
    role: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    total_questions: int
    questions_answered: int
    qa_items: List[QAItemOut]
    insights: dict
