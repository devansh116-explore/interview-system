"""
Embedding backend abstraction.

This project intentionally uses a lightweight TF-IDF implementation built on
NumPy rather than scikit-learn, so it remains easy to run in constrained or
offline environments without requiring a native C++ toolchain.
"""
import math
import re
from collections import Counter
from typing import List, Protocol

_ENGLISH_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that", "the",
    "their", "this", "to", "was", "were", "will", "with", "you", "your",
}
_TOKEN_RE = re.compile(r"\b[\w-]+\b")


class Embedder(Protocol):
    def fit(self, texts: List[str]) -> None: ...
    def transform(self, texts: List[str]) -> list[list[float]]: ...


class TfidfVectorizer:
    def __init__(self, stop_words=None, ngram_range=(1, 2), max_features=5000):
        self.stop_words = stop_words
        self.ngram_range = ngram_range
        self.max_features = max_features
        self.vocabulary_: dict[str, int] = {}
        self.idf_: list[float] | None = None

    def _tokenize(self, text: str) -> List[str]:
        tokens = _TOKEN_RE.findall(text.lower())
        if self.stop_words == "english":
            tokens = [token for token in tokens if token not in _ENGLISH_STOP_WORDS]
        return tokens

    def _ngrams(self, tokens: List[str]) -> List[str]:
        start, end = self.ngram_range
        ngrams: List[str] = []
        for n in range(start, end + 1):
            if n == 1:
                ngrams.extend(tokens)
                continue
            ngrams.extend(" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
        return ngrams

    def fit(self, texts: List[str]) -> "TfidfVectorizer":
        doc_frequency: Counter[str] = Counter()
        vocab_counter: Counter[str] = Counter()

        for text in texts:
            grams = self._ngrams(self._tokenize(text))
            unique_grams = set(grams)
            for gram in unique_grams:
                doc_frequency[gram] += 1
            vocab_counter.update(grams)

        vocab = sorted(vocab_counter.items(), key=lambda item: (-item[1], item[0]))[: self.max_features]
        self.vocabulary_ = {gram: idx for idx, (gram, _) in enumerate(vocab)}

        n_docs = max(len(texts), 1)
        idf = []
        for gram, _ in vocab:
            df = doc_frequency.get(gram, 0)
            idf.append(math.log((1 + n_docs) / (1 + df)) + 1.0)
        self.idf_ = idf
        return self

    def transform(self, texts: List[str]) -> list[list[float]]:
        if not self.vocabulary_ or self.idf_ is None:
            raise RuntimeError("Vectorizer must be fit before transform().")

        rows: List[List[float]] = []
        vocab_size = len(self.vocabulary_)
        for text in texts:
            counts = Counter(self._ngrams(self._tokenize(text)))
            row = [0.0] * vocab_size
            for gram, count in counts.items():
                idx = self.vocabulary_.get(gram)
                if idx is None:
                    continue
                row[idx] = float(count) * self.idf_[idx]
            norm = math.sqrt(sum(value * value for value in row))
            if norm > 0:
                row = [value / norm for value in row]
            rows.append(row)

        if not rows:
            return []
        return rows

    def fit_transform(self, texts: List[str]) -> list[list[float]]:
        self.fit(texts)
        return self.transform(texts)


class TfidfEmbedder:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
        )
        self._fitted = False

    def fit(self, texts: List[str]) -> None:
        self.vectorizer.fit(texts)
        self._fitted = True

    def transform(self, texts: List[str]) -> list[list[float]]:
        if not self._fitted:
            raise RuntimeError("Embedder must be fit before transform().")
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts: List[str]) -> list[list[float]]:
        matrix = self.vectorizer.fit_transform(texts)
        self._fitted = True
        return matrix
