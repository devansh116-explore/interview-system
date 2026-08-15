# Demo Video — Shot List

The assignment requires a mandatory demo video showing the complete system
flow, key features, and how components interact. Suggested run-through
(~4-6 minutes):

1. **Intro (15s)** — one sentence on what the system does and the stack
   (FastAPI + RAG backend, React frontend, SQLite persistence).
2. **Architecture (30s)** — screen-share the diagram in README.md section 1,
   narrate the request flow for one interview turn.
3. **Boot both services (20s)** — show `uvicorn app.main:app --reload` and
   `npm run dev` starting cleanly, briefly show `/docs` (Swagger UI).
4. **Resume upload (30s)** — upload a real or sample resume, point out the
   extracted skills chips confirming resume parsing worked.
5. **Role selection (15s)** — show the available roles pulled live from the
   knowledge base via `/api/roles`.
6. **Interview walkthrough (2 min)** — answer 2-3 questions live. For at
   least one, click "Show retrieved source" to prove the question is
   grounded in an actual retrieved chunk, not canned. Give one deliberately
   short/weak answer and one detailed one to show the quality heuristic
   differs.
7. **Adaptive behavior (20s)** — point out that the next question's topic
   differs from the previous one (breadth) and, for the detailed answer,
   that it follows up on what was just said (adaptivity).
8. **Summary screen (30s)** — show the insights (completion rate, topics
   covered, quality breakdown) and the full Q&A record.
9. **Traceability / DB (20s)** — briefly show a row in `data/app.db`
   (e.g. via a SQLite browser) with `retrieved_context` populated, to
   demonstrate the traceability requirement from the brief.
10. **Close (10s)** — mention the pluggable LLM question-generation mode
    and TF-IDF→embedding-model swap point as forward-looking design notes.

Record with OBS, QuickTime screen recording, or Loom — anything that
captures both screen and (optionally) voice narration.
