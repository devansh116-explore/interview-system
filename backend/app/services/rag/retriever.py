"""
Retrieval mechanism: turns (resume skills + role + interview progress)
into a concrete search query, queries the role's vector store, and
returns scored chunks together with the query that produced them, so
the question generator -- and the stored record -- can trace exactly
why a given chunk was surfaced (7.5 "Ensure traceability of how
questions were generated").
"""
import re
from dataclasses import dataclass
from typing import List, Optional

from app.services.rag.ingestion import Chunk
from app.services.rag.vector_store import get_vector_store
from app.config import settings


def _normalize_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    return re.sub(r"[\W_]+", " ", value.lower()).strip()


def _unique_terms(values: List[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for value in values:
        if not value or not value.strip():
            continue
        normalized = _normalize_text(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(value.strip())
    return ordered


@dataclass
class RetrievalResult:
    query: str
    chunks: List[tuple]  # List[(Chunk, score)]


def build_query(role: str, skills: List[str], previous_topics: List[str], last_answer: Optional[str]) -> str:
    """
    Dynamic query construction (6.7.2):
      - Always anchored on the role, so retrieval stays on-topic.
      - Weighted toward skills the candidate hasn't been asked about yet,
        so the interview explores breadth before repeating a topic.
      - If the candidate's previous answer was substantive, its content
        is folded in so the *next* question can probe deeper into
        whatever they just discussed (adaptive follow-up).
    """
    role_label = role.replace("_", " ")
    previous_topics_normalized = {_normalize_text(topic) for topic in previous_topics if topic}
    fresh_skills = []
    for skill in skills:
        normalized = _normalize_text(skill)
        if not normalized or normalized in previous_topics_normalized:
            continue
        fresh_skills.append(skill)

    skill_terms = _unique_terms(fresh_skills[:4] if fresh_skills else skills[:4])
    query_parts = [role_label] + skill_terms

    if last_answer and len(last_answer.split()) > 8:
        excluded_terms = {_normalize_text(term) for term in skill_terms}
        answer_tokens = []
        seen = set()

        for token in re.findall(r"[A-Za-z0-9]+", last_answer.lower()):
            normalized = _normalize_text(token)
            if not normalized or len(normalized) < 3:
                continue
            if normalized in excluded_terms or normalized in seen:
                continue
            answer_tokens.append(token)
            seen.add(normalized)

        if answer_tokens:
            query_parts.append(" ".join(answer_tokens[:20]))

    return " ".join(query_parts) if query_parts else role_label


def retrieve_for_question(
    role: str,
    skills: List[str],
    previous_topics: List[str],
    last_answer: Optional[str] = None,
) -> RetrievalResult:
    store = get_vector_store(role)
    query = build_query(role, skills, previous_topics, last_answer)
    results = store.search(query, top_k=settings.top_k_retrieval)

    # Avoid re-surfacing a source document already used as the primary
    # topic for a previous question, so the interview covers ground
    # rather than repeating the same chunk.
    used_sources = {t for t in previous_topics}
    filtered = [(c, s) for c, s in results if c.source not in used_sources]
    final = filtered if filtered else results

    return RetrievalResult(query=query, chunks=final)
