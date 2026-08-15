"""
Lightweight heuristic scoring of an answer, used to (a) drive adaptive
question difficulty and (b) populate the final summary's "insights".

This is intentionally simple and explainable rather than an opaque ML
scorer, since the assignment only asks for "basic insights or analysis"
(Expected System Flow, Final Output) -- not full automated grading of
free-text correctness, which would require careful handling to avoid
being misleading.
"""
import re
from typing import Optional


def score_answer(answer_text: str, context_text: str) -> str:
    if not answer_text or not answer_text.strip():
        return "weak"

    words = re.findall(r"\w+", answer_text.lower())
    word_count = len(words)

    context_words = set(re.findall(r"\w+", context_text.lower()))
    overlap = len(set(words) & context_words)

    if word_count < 12:
        return "weak"
    if word_count >= 12 and overlap >= 3:
        return "strong"
    return "adequate"
