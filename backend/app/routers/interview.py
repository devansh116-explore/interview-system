"""Context Construction -> Retrieval -> Question Generation -> Interactive
Interview -> Response Handling -> Final Output, exposed as a small,
stage-oriented set of endpoints (see README API Design Decisions)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app import models
from app.database import get_db
from app.schemas import (
    StartInterviewRequest,
    QuestionOut,
    SubmitAnswerRequest,
    SessionSummaryOut,
    RetrievedChunkOut,
    QAItemOut,
)
from app.services import session_manager
from app.services.rag.ingestion import list_available_roles

router = APIRouter(prefix="/api/interview", tags=["interview"])


def _qa_item_to_question_out(qa_item: models.QAItem, session: models.InterviewSession) -> QuestionOut:
    return QuestionOut(
        session_id=session.id,
        question_number=qa_item.question_number,
        total_questions=session.total_questions,
        topic=qa_item.topic,
        question_text=qa_item.question_text,
        retrieved_context=[RetrievedChunkOut(**c) for c in (qa_item.retrieved_context or [])],
        status=session.status,
    )


@router.post("/start", response_model=QuestionOut)
def start_interview(payload: StartInterviewRequest, db: DBSession = Depends(get_db)):
    candidate = db.get(models.Candidate, payload.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found. Upload a resume first.")

    if payload.role not in list_available_roles():
        raise HTTPException(status_code=422, detail=f"Unknown role '{payload.role}'.")

    qa_item = session_manager.start_interview(db, candidate, payload.role)
    session = db.get(models.InterviewSession, qa_item.session_id)
    return _qa_item_to_question_out(qa_item, session)


@router.post("/answer", response_model=QuestionOut)
def submit_answer(payload: SubmitAnswerRequest, db: DBSession = Depends(get_db)):
    session = db.get(models.InterviewSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    if session.status == "completed":
        raise HTTPException(status_code=409, detail="This interview session is already completed.")

    current_qa = next(
        (i for i in session.qa_items if i.question_number == session.current_question_number), None
    )
    if current_qa is None:
        raise HTTPException(status_code=500, detail="Current question could not be located.")

    next_qa = session_manager.submit_answer(db, session, current_qa, payload.answer_text)
    db.refresh(session)

    if next_qa is None:
        # Interview complete -- return the just-answered question's state with status=completed
        return QuestionOut(
            session_id=session.id,
            question_number=current_qa.question_number,
            total_questions=session.total_questions,
            topic=current_qa.topic,
            question_text=current_qa.question_text,
            retrieved_context=[RetrievedChunkOut(**c) for c in (current_qa.retrieved_context or [])],
            status="completed",
        )

    return _qa_item_to_question_out(next_qa, session)


@router.get("/summary/{session_id}", response_model=SessionSummaryOut)
def get_summary(session_id: str, db: DBSession = Depends(get_db)):
    session = db.get(models.InterviewSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    insights = session_manager.build_insights(session)
    answered_count = len([i for i in session.qa_items if i.answer_text])

    return SessionSummaryOut(
        session_id=session.id,
        candidate_id=session.candidate_id,
        role=session.role,
        status=session.status,
        created_at=session.created_at,
        completed_at=session.completed_at,
        total_questions=session.total_questions,
        questions_answered=answered_count,
        qa_items=[QAItemOut.model_validate(i) for i in session.qa_items],
        insights=insights,
    )
