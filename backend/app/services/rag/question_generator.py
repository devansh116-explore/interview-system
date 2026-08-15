"""
Question generation (7.3): turns retrieved context + resume signal into
an interview question.

Two interchangeable strategies, selected by settings.question_gen_mode:

- "template" (default): fully offline, deterministic, zero API cost.
  Avoids being generic by (a) always grounding the question in a real
  sentence pulled from the *actually retrieved* chunk -- never a fixed
  bank of canned questions -- and (b) rotating through question
  "angles" (conceptual / applied-scenario / resume-linked / tradeoff)
  so consecutive questions don't all read the same way.

- "llm": delegates phrasing to an LLM (Anthropic or OpenAI, whichever
  key is configured), given the same retrieved context + resume + angle
  as the prompt, for noticeably more natural, varied phrasing. Falls
  back to "template" automatically if no key is configured or the call
  fails, so the system is never left without a question.
"""
import re
from dataclasses import dataclass
from typing import List, Optional

from app.config import settings
from app.services.rag.retriever import RetrievalResult

ANGLES = ["conceptual", "applied_scenario", "resume_linked", "tradeoff"]


@dataclass
class GeneratedQuestion:
    question_text: str
    topic: str


def _first_sentence(text: str) -> str:
    match = re.split(r"(?<=[.!?])\s+", text.strip())
    return match[0] if match else text[:160]


def _key_phrase(text: str) -> str:
    """Pull a short, quotable-length concept phrase out of a chunk to
    ground the question in retrieved content without just repeating
    the whole chunk verbatim."""
    sentence = _first_sentence(text)
    words = sentence.split()
    return " ".join(words[:18])


def _template_question(
    role: str,
    skills: List[str],
    retrieval: RetrievalResult,
    question_number: int,
) -> GeneratedQuestion:
    if not retrieval.chunks:
        return GeneratedQuestion(
            question_text=f"Tell me about a project where you applied skills relevant to the {role.replace('_',' ')} role.",
            topic="general",
        )

    top_chunk, _score = retrieval.chunks[0]
    phrase = _key_phrase(top_chunk.text)
    angle = ANGLES[question_number % len(ANGLES)]
    matched_skill = next((s for s in skills if s.lower() in top_chunk.text.lower()), None)

    if angle == "conceptual":
        q = f"In your own words, explain the following in the context of {role.replace('_',' ')} work: \"{phrase}\". What problem does it actually solve?"
    elif angle == "applied_scenario":
        q = f"Suppose you're building a system and need to reason about \"{phrase}\". Walk me through how you'd approach that in practice, and what could go wrong."
    elif angle == "resume_linked" and matched_skill:
        q = f"Your resume mentions {matched_skill}. How does that experience relate to \"{phrase}\"? Give a concrete example from something you've built."
    elif angle == "resume_linked":
        q = f"Given your background, how would you relate your experience to this idea: \"{phrase}\"?"
    else:  # tradeoff
        q = f"What are the tradeoffs involved in \"{phrase}\"? When would you choose a different approach, and why?"

    return GeneratedQuestion(question_text=q, topic=top_chunk.source)


def _llm_question(
    role: str,
    skills: List[str],
    retrieval: RetrievalResult,
    question_number: int,
) -> Optional[GeneratedQuestion]:
    """Best-effort LLM-phrased question. Returns None on any failure so
    the caller can fall back to the template strategy."""
    if not retrieval.chunks:
        return None
    try:
        import httpx

        context_text = "\n\n".join(c.text for c, _ in retrieval.chunks[:3])
        angle = ANGLES[question_number % len(ANGLES)]
        prompt = (
            f"You are interviewing a candidate for a {role.replace('_',' ')} role.\n"
            f"Candidate resume skills: {', '.join(skills) if skills else 'not specified'}.\n"
            f"Reference material (retrieved from the role's knowledge base):\n{context_text}\n\n"
            f"Write ONE interview question with a '{angle}' angle, grounded in the reference "
            f"material above, personalized using the candidate's skills where relevant. "
            f"Return only the question text, nothing else."
        )

        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=20,
            )
            resp.raise_for_status()
            text = resp.json()["content"][0]["text"].strip()
            top_chunk, _ = retrieval.chunks[0]
            return GeneratedQuestion(question_text=text, topic=top_chunk.source)

        if settings.llm_provider == "openai" and settings.openai_api_key:
            resp = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                },
                timeout=20,
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"].strip()
            top_chunk, _ = retrieval.chunks[0]
            return GeneratedQuestion(question_text=text, topic=top_chunk.source)

    except Exception:
        return None
    return None


def generate_question(
    role: str,
    skills: List[str],
    retrieval: RetrievalResult,
    question_number: int,
) -> GeneratedQuestion:
    if settings.question_gen_mode == "llm":
        result = _llm_question(role, skills, retrieval, question_number)
        if result is not None:
            return result
    return _template_question(role, skills, retrieval, question_number)
