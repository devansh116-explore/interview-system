"""
Resume parsing (Resume Processing stage).

Extracts raw text from PDF/text resumes and pulls out a skills list and
approximate years of experience using a curated skill-keyword match
against a per-domain vocabulary, plus a regex for experience phrases.

Design decision: rather than depending on a heavyweight/download-heavy
NER model for a 48-hour assignment, skill extraction is keyword-based
against a maintained SKILL_VOCAB list. This is transparent, fast, has
zero external dependency, and is easy to extend -- adding a new skill
is a one-line change. The tradeoff is that it can miss skills phrased
in unusual ways; a production system would likely swap this for a
fine-tuned NER model or an LLM extraction call behind the same
`extract_skills` function signature.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pdfplumber

SKILL_VOCAB = [
    # AI/ML
    "python", "pytorch", "tensorflow", "scikit-learn", "keras", "machine learning",
    "deep learning", "nlp", "computer vision", "llm", "large language model",
    "transformers", "huggingface", "rag", "retrieval augmented generation",
    "langchain", "vector database", "faiss", "chroma", "pandas", "numpy",
    "data science", "statistics", "sql", "mlops", "generative ai",
    # Backend
    "fastapi", "flask", "django", "node.js", "express", "rest api",
    "microservices", "postgresql", "mysql", "mongodb", "redis", "docker",
    "kubernetes", "aws", "gcp", "azure", "ci/cd", "system design",
    "graphql", "celery", "kafka", "websocket",
    # Frontend
    "react", "next.js", "javascript", "typescript", "vue", "angular",
    "html", "css", "tailwind", "redux", "webpack", "vite",
    # General SWE
    "java", "c++", "golang", "git", "github", "linux", "agile", "testing",
    "unit testing", "distributed systems",
]

EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*years?\s+of\s+experience",
    r"(\d+)\+?\s*years?\s+experience",
]


@dataclass
class ParsedResume:
    raw_text: str
    skills: List[str]
    years_experience: Optional[int]


def _extract_text_from_pdf(path: Path) -> str:
    text_parts = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_text_from_pdf(file_path)
    return file_path.read_text(encoding="utf-8", errors="ignore")


def extract_skills(text: str) -> List[str]:
    lowered = text.lower()
    found = []
    for skill in SKILL_VOCAB:
        if skill in lowered:
            found.append(skill)
    return found


def extract_years_experience(text: str) -> Optional[int]:
    lowered = text.lower()
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            return int(match.group(1))
    return None


def parse_resume(file_path: Path) -> ParsedResume:
    text = extract_text(file_path)
    skills = extract_skills(text)
    years = extract_years_experience(text)
    return ParsedResume(raw_text=text, skills=skills, years_experience=years)
