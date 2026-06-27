"""Retriever: cosine-similarity search over the fitted TF-IDF matrix."""

from __future__ import annotations

from typing import Any, Dict, List

from sklearn.metrics.pairwise import cosine_similarity


def retrieve(
    query: str,
    vectorizer: Any,
    matrix: Any,
    chunks: List[str],
    sources: List[str],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """Return the top_k most relevant chunks for a query.

    If the highest similarity score is 0.0 (no overlap at all), return an
    empty list so the prompt layer can reply 'NO DATA FOUND IN CASE FILES.'
    """
    if not chunks:
        return []

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix)[0]

    # No signal at all -> nothing to ground on.
    if scores.max() == 0.0:
        return []

    # Highest-scoring chunks first.
    top_indices = scores.argsort()[::-1][:top_k]

    results: List[Dict[str, Any]] = []
    for idx in top_indices:
        results.append(
            {
                "chunk": chunks[idx],
                "source": sources[idx],
                "score": float(scores[idx]),
            }
        )
    return results
