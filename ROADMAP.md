RAG Detective Project Roadmap
Phase 1: Environment & Data

 Install Python dependencies (FastAPI, scikit-learn, requests, uvicorn)
Phase 2: Core RAG Pipeline (Backend)
 vectorizer.py: Build the TF-IDF matrix from the case files
 retriever.py: Calculate cosine similarity and return top K chunks
 prompts.py: Construct the grounded detective system prompt
 main.py: FastAPI endpoints, load matrix on startup, call Groq API
Phase 3: The Interface (Frontend)
 static/index.html: 90s CRT terminal aesthetic
 static/style.css: Scanlines, phosphor green text, blinking cursor
 static/app.js: Fetch calls to the backend, typing animation for answers
Phase 4: Testing & Debugging
 Test retrieval: Does asking about the murder weapon pull the right JSON/text?
 Test grounding: Does asking an unrelated question return "NO DATA FOUND"?
 Test contradictions: Can the RAG catch a witness lying based on the timeline?
