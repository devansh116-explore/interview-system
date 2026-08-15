"""
Session/orchestration layer -- the "conductor" that ties resume data,
retrieval, and question generation together into the interactive
interview flow described in the brief (Expected System Flow, points
5-7). Routers stay thin and simply call into this module.
"""
import datetime
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app import models
from app.config import settings
from app.services.rag.retriever import retrieve_for_question
from app.services.rag.question_generator import generate_question
from app.utils.scoring import score_answer


def start_interview(db: DBSession, candidate: models.Candidate, role: str) -> models.QAItem:
    session = models.InterviewSession(
        candidate_id=candidate.id,
        role=role,
        status="in_progress",
        current_question_number=1,
        total_questions=settings.questions_per_interview,
    )
    db.add(session)
    db.flush()

    qa_item = _generate_and_store_question(db, session, candidate, question_number=1, previous_topics=[])
    db.commit()
    db.refresh(qa_item)
    return qa_item


def _generate_and_store_question(
    db: DBSession,
    session: models.InterviewSession,
    candidate: models.Candidate,
    question_number: int,
    previous_topics: list[str],
    last_answer: Optional[str] = None,
) -> models.QAItem:
    retrieval = retrieve_for_question(
        role=session.role,
        skills=candidate.extracted_skills or [],
        previous_topics=previous_topics,
        last_answer=last_answer,
    )
    generated = generate_question(
        role=session.role,
        skills=candidate.extracted_skills or [],
        retrieval=retrieval,
        question_number=question_number - 1,
    )

    retrieved_context = [
        {"source": chunk.source, "snippet": chunk.text[:280], "score": round(score, 4)}
        for chunk, score in retrieval.chunks[:3]
    ]

    qa_item = models.QAItem(
        session_id=session.id,
        question_number=question_number,
        topic=generated.topic,
        question_text=generated.question_text,
        retrieved_context=retrieved_context,
    )
    db.add(qa_item)
    db.flush()
    return qa_item


def submit_answer(db: DBSession, session: models.InterviewSession, qa_item: models.QAItem, answer_text: str):
    context_text = " ".join(c.get("snippet", "") for c in (qa_item.retrieved_context or []))
    qa_item.answer_text = answer_text
    qa_item.answer_quality = score_answer(answer_text, context_text)
    qa_item.answered_at = datetime.datetime.utcnow()
    db.add(qa_item)

    is_last = session.current_question_number >= session.total_questions
    if is_last:
        session.status = "completed"
        session.completed_at = datetime.datetime.utcnow()
        db.add(session)
        db.commit()
        return None

    candidate = session.candidate
    previous_topics = [item.topic for item in session.qa_items if item.topic]
    next_number = session.current_question_number + 1
    session.current_question_number = next_number
    db.add(session)

    next_qa_item = _generate_and_store_question(
        db,
        session,
        candidate,
        question_number=next_number,
        previous_topics=previous_topics,
        last_answer=answer_text,
    )
    db.commit()
    db.refresh(next_qa_item)
    return next_qa_item


def build_insights(session: models.InterviewSession) -> dict:
    items = session.qa_items
    answered = [i for i in items if i.answer_text]
    quality_counts = {"weak": 0, "adequate": 0, "strong": 0}
    for item in answered:
        if item.answer_quality in quality_counts:
            quality_counts[item.answer_quality] += 1

    topics_covered = sorted({i.topic for i in items if i.topic})
    avg_answer_len = (
        sum(len((i.answer_text or "").split()) for i in answered) / len(answered)
        if answered else 0
    )

    return {
        "quality_breakdown": quality_counts,
        "topics_covered": topics_covered,
        "average_answer_length_words": round(avg_answer_len, 1),
        "completion_rate": f"{len(answered)}/{session.total_questions}",
    }
