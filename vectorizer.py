"""TF-IDF vectorizer for the case file corpus.

Reads every file under case_data/, splits the content into chunks, tracks the
source filename for every chunk, and fits a TF-IDF matrix over the corpus.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer

# case_data/ lives next to this file.
CASE_DATA_DIR: Path = Path(__file__).parent / "case_data"


def _flatten_object(obj: dict) -> str:
    """Turn a JSON object into a readable, indexable text chunk."""
    parts: List[str] = []
    for key, value in obj.items():
        label = str(key).replace("_", " ").title()
        if isinstance(value, list):
            value = "; ".join(str(item) for item in value)
        parts.append(f"{label}: {value}")
    return ". ".join(parts)


def _chunk_text_file(text: str) -> List[str]:
    """Split a plain-text witness statement into paragraph-sized chunks."""
    return [para.strip() for para in text.split("\n\n") if para.strip()]


def _chunk_json_file(text: str) -> List[str]:
    """Split a JSON file into one chunk per top-level object/entry."""
    data = json.loads(text)
    chunks: List[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                flat = _flatten_object(item)
                if flat.strip():
                    chunks.append(flat)
            elif isinstance(item, str) and item.strip():
                chunks.append(item)
    elif isinstance(data, dict):
        flat = _flatten_object(data)
        if flat.strip():
            chunks.append(flat)
    return chunks


def load_chunks() -> Tuple[List[str], List[str]]:
    """Read all case files and return (chunks, source_filenames)."""
    chunks: List[str] = []
    sources: List[str] = []

    if not CASE_DATA_DIR.exists():
        return chunks, sources

    for path in sorted(CASE_DATA_DIR.rglob("*")):
        if not path.is_file():
            continue
        # Track the filename relative to case_data/ for the "ACCESSING FILE" UI.
        rel_source = str(path.relative_to(CASE_DATA_DIR))
        raw = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            file_chunks = _chunk_json_file(raw)
        elif path.suffix in {".txt", ".md"}:
            file_chunks = _chunk_text_file(raw)
        else:
            file_chunks = [raw.strip()] if raw.strip() else []

        for chunk in file_chunks:
            chunks.append(chunk)
            sources.append(rel_source)

    return chunks, sources


def build_vectorizer() -> Tuple[TfidfVectorizer, "object", List[str], List[str]]:
    """Fit the TF-IDF vectorizer and return (vectorizer, matrix, chunks, sources)."""
    chunks, sources = load_chunks()
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(chunks)
    return vectorizer, matrix, chunks, sources


if __name__ == "__main__":
    vec, mat, ch, src = build_vectorizer()
    print(f"Loaded {len(ch)} chunks from {len(set(src))} files.")
    print(f"Matrix shape: {mat.shape}")
