"""Small, dependency-free retrieval and summarization utilities."""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text or "")]


def cosine_similarity(query: str, document: str) -> float:
    q = Counter(tokenize(query))
    d = Counter(tokenize(document))
    if not q or not d:
        return 0.0
    dot = sum(q[token] * d.get(token, 0) for token in q)
    q_norm = math.sqrt(sum(value * value for value in q.values()))
    d_norm = math.sqrt(sum(value * value for value in d.values()))
    return dot / (q_norm * d_norm) if q_norm and d_norm else 0.0


def retrieve(query: str, documents: Iterable[dict], limit: int = 3) -> list[dict]:
    """Rank documents by lexical cosine similarity and return bounded evidence."""
    ranked = []
    for document in documents:
        searchable = f"{document.get('title', '')} {document.get('text', '')}"
        score = cosine_similarity(query, searchable)
        # Ignore weak lexical matches instead of presenting unrelated text as evidence.
        if score >= 0.25:
            ranked.append({**document, "score": round(score, 4)})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]


def extract_summary(text: str, max_sentences: int = 3) -> str:
    """Create an extractive summary using sentence scoring and source position."""
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if not cleaned:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    all_tokens = tokenize(cleaned)
    frequencies = Counter(all_tokens)
    scored = []
    for index, sentence in enumerate(sentences):
        words = tokenize(sentence)
        score = sum(frequencies[word] for word in words) / (len(words) or 1)
        scored.append((index, sentence, score))

    best = sorted(scored, key=lambda item: item[2], reverse=True)[:max_sentences]
    best.sort(key=lambda item: item[0])
    return " ".join(sentence for _, sentence, _ in best)


def load_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
