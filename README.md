# Aptitude — AI-Powered Role-Based Candidate Screening System

Built for the PGAGI AI/ML & Backend Engineering Intern assignment.

A candidate uploads a resume, picks a target role, and is walked through a
5-question interview whose questions are generated on the fly by a
Retrieval-Augmented Generation (RAG) pipeline — grounded in a role-specific
knowledge base and shaped by what's actually on the candidate's resume —
followed by a structured summary with basic insights.

---

## 1. System Architecture

```
┌──────────────────────┐        HTTP/JSON        ┌───────────────────────────────────────┐
│   Frontend (React)   │  ───────────────────▶   │            Backend (FastAPI)           │
│                       │                          │                                         │
│  ResumeUpload         │                          │  routers/  resume · interview · roles  │
│  RoleSelect           │  ◀───────────────────    │  services/ session_manager (orchestrator)│
│  Interview            │                          │            resume_parser                │
│  Summary              │                          │            rag/ ingestion, embeddings,   │
└──────────────────────┘                          │                vector_store, retriever,  │
                                                     │                question_generator        │
                                                     │  models.py — Candidate / Session / QAItem│
                                                     └───────────────┬─────────────────────────┘
                                                                     │
                                                     ┌───────────────▼─────────────────────────┐
                                                     │  SQLite (session/QA persistence)          │
                                                     │  Per-role TF-IDF vector stores (joblib)   │
                                                     │  knowledge_base/<role>/*.txt (source docs) │
                                                     └────────────────────────────────────────────┘
```

**Request flow for one interview turn:**
`candidate skills + role + prior topics/answer` → `retriever.build_query()` →
`vector_store.search()` (cosine similarity over TF-IDF) → top-k chunks →
`question_generator.generate_question()` → question stored with the exact
chunks that produced it (`QAItem.retrieved_context`) → returned to the
frontend, which also lets the candidate inspect that retrieved context.

---

## 2. Setup Instructions

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env        # defaults work out of the box, no keys required
uvicorn app.main:app --reload --port 8000
```

The first request to a given role builds and persists that role's TF-IDF
vector store under `data/vector_store/`; subsequent runs load it from disk.
SQLite database is created automatically at `data/app.db`.

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env        # points at the local backend by default
npm run dev
```

App: `http://localhost:5173`

### Live Deployment

- Frontend: https://aptitude-frontend-1.onrender.com
- Backend: https://aptitude-backend-1.onrender.com
- API health: https://aptitude-backend-1.onrender.com/api/health
- API docs: https://aptitude-backend-1.onrender.com/docs

Both `.env.example` files list every configurable value with inline comments.

---

## 3. Key Design Decisions

**Chunking strategy.** The knowledge base is split first on paragraph
boundaries (each paragraph in the curated corpus is one coherent idea), then
to a target word count (~120 words) with ~25-word overlap. Paragraph-first
splitting preserves semantic coherence; the word-count pass keeps chunks
small enough for focused retrieval; the overlap prevents an idea from being
awkwardly severed across a chunk boundary.

**Embeddings: TF-IDF instead of a neural embedding model.** This was a
deliberate tradeoff for a 48-hour, fully offline-runnable assignment: no
model download, no GPU, no API key, fully deterministic, and — because the
knowledge base is a small, topic-dense, curated corpus — lexical overlap
between a resume-derived query and the relevant chunk is usually high, so
TF-IDF performs well here. The `Embedder` interface in
`services/rag/embeddings.py` is narrow specifically so a stronger backend
(sentence-transformers, OpenAI/Anthropic embeddings) can be swapped in later
without touching retrieval, question generation, or anything upstream.

**Vector store.** Each role gets its own TF-IDF matrix, persisted with
`joblib` rather than run through a full vector-DB server — appropriate for a
few dozen chunks per role. `vector_store.py` exposes exactly `build` /
`load` / `search`, which is the surface a real FAISS/Chroma/Pinecone-backed
implementation would need to satisfy as well.

**Question generation, two interchangeable strategies.** Default is a fully
offline **template** mode: it never draws from a fixed question bank —
every question is grounded in a sentence extracted from the *actually
retrieved* chunk for that turn, and rotates through four angles
(conceptual / applied-scenario / resume-linked / tradeoff) so consecutive
questions don't read identically. An optional **LLM** mode
(`QUESTION_GEN_MODE=llm` + an Anthropic or OpenAI key) sends the same
retrieved context + resume + angle to an LLM for more natural phrasing, and
silently falls back to the template strategy if no key is configured or the
call fails — the system is never left without a question.

**Adaptive interview.** Each turn's retrieval query folds in resume skills
not yet covered and, if the candidate's previous answer was substantive
(>8 words), a snippet of their own answer — so retrieval steers toward
whatever they just discussed. Already-covered source documents are
deprioritized so the interview explores breadth rather than repeating a
topic.

**Traceability.** Every stored question keeps the exact chunks (source,
snippet, similarity score) that produced it, satisfying the brief's
"ensure traceability of how questions were generated," and the frontend
lets the candidate reveal that retrieved context per question.

**Answer scoring.** A deliberately simple, explainable heuristic (word
count + lexical overlap with the retrieved context) buckets each answer as
weak/adequate/strong. This is intentional: the brief only asks for "basic
insights," and a real correctness/quality grader for open-ended free text
would need much more care to avoid being misleading — better to be
transparent about what a simple heuristic is doing than to fake confidence.

**Skill extraction.** Keyword matching against a maintained per-domain
vocabulary (`resume_parser.py`) rather than a downloaded NER model —
transparent, dependency-free, and trivially extensible; production would
likely swap this for an LLM-based extraction call behind the same function
signature.

**Backend structure.** Routers stay thin (HTTP concerns only); all
orchestration lives in `services/session_manager.py`; the RAG pipeline is
fully isolated in `services/rag/`. This separation is what makes the
embedding/vector-store/question-generation swaps above possible without
touching the API layer or the database models.

**Frontend structure.** The whole flow is one explicit state machine
(`upload → role → interview → summary`) in `App.jsx`, so there is exactly
one source of truth for where the candidate is; each stage's data lives
next to the stage that produced it, and `api.js` is the single seam between
UI and backend.

**Knowledge base content.** The assignment's suggested textbooks are
copyrighted works, so this repo ships an original, curated knowledge base
(written for this project) covering the same topic areas per role, under
`backend/knowledge_base/<role>/*.txt`. Swapping in the real books is just a
matter of adding more `.txt` files to the same folders — no code changes
needed, since ingestion walks the directory automatically.

---

## 4. API Overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/resume/upload` | POST (multipart) | Parse a resume, extract skills/experience, create a Candidate |
| `/api/roles` | GET | List available roles and their knowledge-base document counts |
| `/api/interview/start` | POST | Create a session for a candidate+role, return question 1 |
| `/api/interview/answer` | POST | Store an answer, return the next question (or `status: completed`) |
| `/api/interview/summary/{session_id}` | GET | Structured Q&A history + insights |
| `/api/health` | GET | Liveness check |

Full interactive schema: `/docs` (Swagger UI) once the backend is running.

---

## 5. Project Structure

```
backend/
  app/
    main.py                 # FastAPI app, CORS, centralized error handler
    config.py                # env-driven settings
    database.py, models.py, schemas.py
    routers/                 # resume.py, interview.py, knowledge_base.py
    services/
      resume_parser.py
      session_manager.py     # orchestrates the interview lifecycle
      rag/
        ingestion.py          # load + chunk knowledge base docs
        embeddings.py         # TF-IDF embedder (swappable interface)
        vector_store.py       # per-role store: build/load/search
        retriever.py          # dynamic query construction + retrieval
        question_generator.py # template + optional LLM strategies
    utils/scoring.py
  knowledge_base/<role>/*.txt
frontend/
  src/
    App.jsx                  # 4-stage state machine
    api.js                   # backend client
    components/               # ResumeUpload, RoleSelect, Interview, Summary
    styles.css
```

## 6. Notes / Known Limitations

- Answer "quality" is a heuristic, not a correctness grader — see Key
  Design Decisions above.
- TF-IDF retrieval works well on this curated corpus but won't capture deep
  paraphrase the way a neural embedding model would; the codebase is
  structured so that's a contained swap, not a rewrite.
- Single-process in-memory vector store cache — fine for a take-home demo,
  would move to a persistent vector DB service for multi-instance
  deployment.
