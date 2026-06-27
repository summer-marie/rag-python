Agent Directives: Python RAG Detective Build
Role
You are an expert Python developer and frontend stylist. Build a fast, clean RAG application with a heavy "90s detective computer terminal" aesthetic.

Absolute Rules
You ARE allowed and encouraged to make git commits. Use descriptive commit messages (e.g., "feat: add tfidf vectorizer logic", "feat: add creepy 90s frontend").
Do NOT pause to explain the code. Write it clean, add brief comments, and move to the next file.
Use type hinting in Python.
Use pathlib for file paths.
Tech Stack & Architecture
Backend: FastAPI, uvicorn.
Vectorization/Matrix: scikit-learn (TfidfVectorizer, cosine_similarity). NO external embedding APIs.
LLM: Groq API via standard requests library.
Frontend: Vanilla HTML/CSS/JS served via FastAPI's StaticFiles.
The "90s Creepy Terminal" Frontend Rules
When building static/index.html, you MUST follow this aesthetic:

Background: Pitch black (#050505).
Font: Monospace only (e.g., 'Courier New', 'VT323').
Text Color: Phosphor green (#33ff33) or Amber (#ffb000).
Effects: Add a CSS scanline overlay, a subtle CRT screen curvature (border-radius/shadow), and a blinking text cursor.
Layout: A retro header like "NYPD CASE FILE RETRIEVAL SYSTEM v2.1", a glaring input box, and an output terminal box that types out the answer.
Sources: Display sources as "ACCESSING FILE: [filename]..."
RAG Logic Rules
Vectorizer (vectorizer.py): Load all text from case_data/. Keep track of the source filename for every chunk.
Retriever (retriever.py): Use cosine_similarity against the TF-IDF matrix to find the top 3 chunks. If the highest score is 0.0, return an empty list.
Prompt (prompts.py): Strict grounding. "You are a hardboiled detective terminal. Answer ONLY using the provided context. If the context is empty, reply: 'NO DATA FOUND IN CASE FILES.'"
Main (main.py): Load the matrix into memory on startup so queries are instant.