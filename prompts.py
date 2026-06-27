"""Prompt construction + Groq API calls for the detective terminal."""

from __future__ import annotations

import os
from typing import Any, Dict, List

import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

# Strict grounding + hardboiled detective persona, per AGENTS.md.
SYSTEM_PROMPT = (
    "You are a hardboiled detective terminal working the Ashworth homicide. "
    "Answer ONLY using the provided context. Never use outside knowledge, never "
    "speculate, and never invent facts. Cite case-file details when relevant. "
    "Keep the voice terse, cynical, and noir. "
    "If the context is empty or does not contain the answer, reply exactly: "
    "'NO DATA FOUND IN CASE FILES.'"
)

# Sentinel reply when there is no context to ground on.
NO_DATA_REPLY = "NO DATA FOUND IN CASE FILES."


def build_context(retrieved: List[Dict[str, Any]]) -> str:
    """Stitch retrieved chunks into a labeled context block."""
    if not retrieved:
        return ""
    blocks: List[str] = []
    for i, item in enumerate(retrieved, start=1):
        blocks.append(f"[CASE FILE {i}: {item['source']}]\n{item['chunk']}")
    return "\n\n".join(blocks)


def build_payload(question: str, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the Groq chat-completions request payload."""
    context = build_context(retrieved)
    user_content = (
        f"Case file context:\n{context}\n\n"
        f"Detective query: {question}"
    )
    return {
        "model": GROQ_MODEL,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    }


def get_api_key() -> str | None:
    """Pull the Groq key from the environment (loaded from .env on startup)."""
    return os.environ.get("GROQ_API_KEY")


def call_groq(question: str, retrieved: List[Dict[str, Any]]) -> str:
    """Send the grounded prompt to Groq and return the detective's answer.

    When there is no retrieved context we short-circuit to the no-data reply so
    we never burn an API call on an empty context.
    """
    if not retrieved:
        return NO_DATA_REPLY

    api_key = get_api_key()
    if not api_key:
        return "ERROR: GROQ_API_KEY missing from environment."

    payload = build_payload(question, retrieved)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        GROQ_API_URL, headers=headers, json=payload, timeout=30
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
