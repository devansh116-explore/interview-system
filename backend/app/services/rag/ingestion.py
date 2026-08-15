"""
Knowledge ingestion: loads role-specific documents from the knowledge
base directory and chunks them.

Chunking strategy (Design decision, see README):
We chunk on paragraph boundaries first (a paragraph is usually one
coherent idea in our curated knowledge base), then merge/split to a
target word count with overlap, so that:
  - Each chunk stays semantically coherent (context preservation),
  - Chunks are small enough for fast, focused retrieval,
  - Overlap prevents a concept from being awkwardly split across a
    chunk boundary and losing context for whichever half is retrieved.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List

from app.config import settings


@dataclass
class Chunk:
    chunk_id: str
    role: str
    source: str
    text: str


def _split_into_word_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap  # overlap preserves boundary context
    return chunks


def load_role_documents(role: str) -> List[Chunk]:
    """Load and chunk every .txt file under knowledge_base/<role>/."""
    kb_dir = Path(settings.base_dir) / settings.knowledge_base_dir.lstrip("./") / role
    chunks: List[Chunk] = []
    if not kb_dir.exists():
        return chunks

    for file_path in sorted(kb_dir.glob("*.txt")):
        raw = file_path.read_text(encoding="utf-8")
        # First split on blank-line-delimited paragraphs to respect natural
        # topic boundaries authored into the corpus.
        paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
        for p_idx, paragraph in enumerate(paragraphs):
            sub_chunks = _split_into_word_chunks(
                paragraph, settings.chunk_size_words, settings.chunk_overlap_words
            )
            for s_idx, sub in enumerate(sub_chunks):
                chunks.append(
                    Chunk(
                        chunk_id=f"{file_path.stem}_p{p_idx}_c{s_idx}",
                        role=role,
                        source=file_path.stem,
                        text=sub,
                    )
                )
    return chunks


def list_available_roles() -> List[str]:
    kb_root = Path(settings.base_dir) / settings.knowledge_base_dir.lstrip("./")
    if not kb_root.exists():
        return []
    return sorted([p.name for p in kb_root.iterdir() if p.is_dir()])
