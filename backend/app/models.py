"""
ORM models. Four tables capture the full lifecycle described in the
assignment brief: a candidate (resume), an interview session (one per
candidate+role attempt), the individual Q&A turns within that session,
and a traceability link from each question back to the knowledge-base
chunks that were retrieved to generate it (see 7.5 "Output Structuring
... Ensure traceability of how questions were generated").
"""
import datetime
import uuid

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=gen_id)
    resume_filename = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    extracted_skills = Column(JSON, nullable=False, default=list)
    extracted_years_experience = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("InterviewSession", back_populates="candidate")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True, default=gen_id)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, default="in_progress")  # in_progress | completed
    current_question_number = Column(Integer, default=0)
    total_questions = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    candidate = relationship("Candidate", back_populates="sessions")
    qa_items = relationship("QAItem", back_populates="session", order_by="QAItem.question_number")


class QAItem(Base):
    __tablename__ = "qa_items"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, ForeignKey("interview_sessions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    topic = Column(String, nullable=True)
    question_text = Column(Text, nullable=False)
    retrieved_context = Column(JSON, nullable=False, default=list)  # list of {source, chunk_id, snippet, score}
    answer_text = Column(Text, nullable=True)
    answer_quality = Column(String, nullable=True)  # weak | adequate | strong (heuristic, see scoring.py)
    asked_at = Column(DateTime, default=datetime.datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)

    session = relationship("InterviewSession", back_populates="qa_items")
