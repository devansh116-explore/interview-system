"""
Per-role vector store. Each role gets its own TF-IDF matrix built from
that role's knowledge-base chunks, persisted to disk with joblib so we
don't re-ingest/re-vectorize on every server restart.
"""
import json
import math
from pathlib import Path
from typing import List, Tuple

import joblib

from app.config import settings
from app.services.rag.embeddings import TfidfEmbedder
from app.services.rag.ingestion import Chunk, load_role_documents


class VectorStore:
    def __init__(self, role: str):
        self.role = role
        self.embedder = TfidfEmbedder()
        self.chunks: List[Chunk] = []
        self.matrix = None

    def _paths(self):
        base = Path(settings.base_dir) / settings.vector_store_dir.lstrip("./")
        return (
            base / f"{self.role}_matrix.joblib",
            base / f"{self.role}_vectorizer.joblib",
            base / f"{self.role}_chunks.json",
        )

    def build(self) -> None:
        self.chunks = load_role_documents(self.role)
        texts = [c.text for c in self.chunks]
        if not texts:
            self.matrix = None
            return
        self.matrix = self.embedder.fit_transform(texts)
        self._persist()

    def _persist(self) -> None:
        matrix_path, vec_path, chunks_path = self._paths()
        joblib.dump(self.matrix, matrix_path)
        joblib.dump(self.embedder.vectorizer, vec_path)
        chunks_path.write_text(
            json.dumps([c.__dict__ for c in self.chunks]), encoding="utf-8"
        )

    def load(self) -> bool:
        matrix_path, vec_path, chunks_path = self._paths()
        if not (matrix_path.exists() and vec_path.exists() and chunks_path.exists()):
            return False
        self.matrix = joblib.load(matrix_path)
        self.embedder.vectorizer = joblib.load(vec_path)
        self.embedder._fitted = True
        raw_chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
        self.chunks = [Chunk(**rc) for rc in raw_chunks]
        return True

    def ensure_ready(self) -> None:
        if not self.load():
            self.build()

    def search(self, query: str, top_k: int) -> List[Tuple[Chunk, float]]:
        if self.matrix is None or not self.chunks:
            return []

        query_vec = self.embedder.transform([query])[0]
        if not query_vec or all(value == 0 for value in query_vec):
            return []

        query_norm = math.sqrt(sum(value * value for value in query_vec))
        if query_norm == 0:
            return []

        scored: List[Tuple[float, int]] = []
        for idx, doc_vec in enumerate(self.matrix):
            doc_norm = math.sqrt(sum(value * value for value in doc_vec))
            if doc_norm == 0:
                continue
            dot = sum(a * b for a, b in zip(doc_vec, query_vec))
            score = dot / (doc_norm * query_norm)
            if math.isfinite(score) and score > 0:
                scored.append((score, idx))

        ranked = sorted(scored, key=lambda item: item[0], reverse=True)[:top_k]
        return [(self.chunks[idx], float(score)) for score, idx in ranked]


_store_cache: dict[str, VectorStore] = {}


def get_vector_store(role: str) -> VectorStore:
    """Cached accessor so each role's store is built/loaded only once per process."""
    if role not in _store_cache:
        store = VectorStore(role)
        store.ensure_ready()
        _store_cache[role] = store
    return _store_cache[role]
