"""FastAPI app: loads the TF-IDF matrix once on startup, serves /ask + UI."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from prompts import call_groq
from retriever import retrieve
from vectorizer import build_vectorizer

# Load GROQ_API_KEY (and anything else) from .env before anything reads it.
load_dotenv()

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# Global, in-memory state populated once on startup so queries are instant.
STATE: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the TF-IDF matrix once and cache it for the lifetime of the app."""
    vectorizer, matrix, chunks, sources = build_vectorizer()
    STATE.update(
        {
            "vectorizer": vectorizer,
            "matrix": matrix,
            "chunks": chunks,
            "sources": sources,
        }
    )
    print(f"[startup] loaded {len(chunks)} chunks / {len(set(sources))} case files")
    yield
    STATE.clear()


app = FastAPI(title="NYPD Case File Retrieval System", lifespan=lifespan)

# Mount static assets only if the folder exists (created in Phase 3).
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: AskRequest) -> Dict[str, Any]:
    """Retrieve relevant chunks, call Groq, and return the answer + sources."""
    retrieved = retrieve(
        req.question,
        STATE["vectorizer"],
        STATE["matrix"],
        STATE["chunks"],
        STATE["sources"],
    )
    answer = call_groq(req.question, retrieved)
    sources = [{"source": r["source"], "score": r["score"]} for r in retrieved]
    return {"answer": answer, "sources": sources}


@app.get("/")
def index():
    """Serve the terminal UI (falls back to a status message if absent)."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "online", "message": "static/index.html not built yet"}
