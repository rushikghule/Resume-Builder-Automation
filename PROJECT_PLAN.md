# Resume ⇄ JD Intelligence Platform — Project Plan

A web app where a user pastes a job description, picks a resume (from templates or
their own upload), gets an ATS score + gap analysis, answers a few clarifying
questions, and receives a tailored resume with a before/after ATS score comparison.

No platform automation, no scraping, no auto-apply — this is pure document
intelligence, which is why it's fully buildable and safe end-to-end.

---

## Tech stack

**Frontend:** React + TypeScript, Vite, TailwindCSS, shadcn/ui components
**Backend:** FastAPI (Python) — hosts the LangGraph app behind a REST/WebSocket API
**Orchestration:** LangGraph (multi-agent, supervisor + specialist nodes, human-in-the-loop checkpoint)
**LLM:** Claude (Anthropic API) for all analysis/generation nodes
**Resume parsing:** `pypdf` / `python-docx` for uploads, our own templates as structured JSON/Jinja for the built-ins
**State/session:** LangGraph checkpointer (in-memory or SQLite for Part 1; Postgres if this grows)
**File export:** the `docx` skill (or WeasyPrint for PDF) to produce the final tailored resume as a real downloadable file

---

## High-level flow

```
User Journey:
1. Land on app → choose resume source:
   a. Pick one of 2-3 built-in templates (fill in their own details), or
   b. Upload their own resume (PDF/DOCX)
2. Paste target Job Description
3. Click "Analyze" →
   → Parser Agent extracts structured resume data
   → JD Agent extracts structured requirements (skills, keywords, experience level)
   → ATS Scorer Agent computes baseline ATS score + gap list
4. UI shows: ATS score (0-100), matched keywords, missing keywords,
   section-by-section gaps
5. System asks 2-4 targeted clarifying questions (human-in-the-loop node)
   e.g. "You're missing 'Kubernetes' — do you have any relevant experience
   we should include, even informally?"
6. User answers via UI form
7. Tailoring Agent rewrites resume sections using original content + JD + user's answers
8. New ATS Scorer pass on the tailored resume
9. UI shows: Before vs After score, diff view, download button (DOCX/PDF)
```

---

## LangGraph agent architecture

```
                         ┌─────────────────┐
                         │   Supervisor     │
                         │  (routes flow)   │
                         └───────┬──────────┘
                 ┌───────────────┼────────────────┐
                 ▼               ▼                ▼
        ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Resume Parser│  │  JD Analyzer │  │  ATS Scorer  │
        │    Agent     │  │    Agent     │  │    Agent     │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               └─────────────────┴─────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  Human-in-the-loop node  │
                    │  (clarifying questions)  │
                    └────────────┬─────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   Resume Tailoring Agent │
                    └────────────┬─────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  ATS Scorer Agent (v2)   │
                    └────────────┬─────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  Export / Format Agent   │
                    └─────────────────────────┘
```

**Nodes:**
- **Resume Parser Agent** — turns raw PDF/DOCX/template into structured JSON (contact, summary, experience, skills, education).
- **JD Analyzer Agent** — extracts required skills, nice-to-haves, seniority signals, key terms/phrases (for keyword matching).
- **ATS Scorer Agent** — deterministic + LLM-assisted scoring: keyword overlap, section completeness, formatting compatibility (no tables/graphics flags), quantified achievements check. Returns score + explanation + missing items. Runs twice (before/after).
- **Human-in-the-loop node** — LangGraph interrupt; pauses graph, surfaces questions to the frontend, resumes on user's answers.
- **Resume Tailoring Agent** — rewrites/reorders resume content using original + JD + human answers, staying truthful (never invents experience the user didn't confirm).
- **Export/Format Agent** — renders the final structured resume into a template (DOCX/PDF).

**Supervisor** — a thin router node coordinating sequence (mostly linear here, supervisor pattern chosen so Part 2 can add branches like "select which template to export to" or "generate cover letter" without restructuring).

---

## PART 1 — Build now

**Scope: the core single-JD, single-resume analyze → clarify → tailor → re-score loop.**

### 1.1 Backend
- [ ] FastAPI app skeleton with endpoints:
  - `POST /session` — start a new analysis session
  - `POST /session/{id}/resume` — upload resume or select template
  - `POST /session/{id}/jd` — submit JD text
  - `POST /session/{id}/analyze` — run parser + JD + scorer nodes, return score + gaps + questions
  - `POST /session/{id}/answers` — submit answers to clarifying questions, resume graph
  - `GET /session/{id}/result` — get tailored resume + before/after scores
  - `GET /session/{id}/download` — download tailored resume as DOCX
- [ ] LangGraph graph wiring all 5 nodes + human-in-the-loop interrupt, using SQLite checkpointer
- [ ] Resume Parser Agent (PDF/DOCX → structured JSON via Claude + `pypdf`/`python-docx`)
- [ ] JD Analyzer Agent
- [ ] ATS Scorer Agent (with an explicit scoring rubric — see below)
- [ ] Resume Tailoring Agent
- [ ] Export Agent (DOCX output via template)
- [ ] 2-3 built-in resume templates as structured JSON + matching DOCX render templates

### 1.2 Frontend
- [ ] Landing page: "Upload resume" vs "Choose a template" (2-3 cards)
- [ ] JD paste screen (large textarea, "Analyze" button)
- [ ] Results screen: ATS score gauge, matched/missing keyword chips, section gap list
- [ ] Clarifying questions form (dynamic, 2-4 questions, textarea/short-answer inputs)
- [ ] Tailored resume screen: side-by-side or toggle before/after, score comparison (animated delta), download button
- [ ] Loading/progress states reflecting which agent is currently running (nice UX touch, also honest about multi-step nature)

### 1.3 ATS scoring rubric (v1, deterministic + explainable)
- Keyword/skill overlap (JD required skills found in resume): 40%
- Quantified achievements present (numbers/metrics in bullet points): 20%
- Section completeness (contact, summary, experience, education, skills all present): 15%
- Formatting ATS-compatibility (no tables/columns/images flagged, standard fonts): 15%
- Title/seniority alignment (resume title/summary matches JD seniority level): 10%

Score is computed with a mix of rule-based checks (keyword match, section presence,
formatting flags) and one LLM call to judge quality of quantified achievements and
title alignment — kept deterministic-ish by using low temperature and a strict rubric prompt.

### 1.4 Deliverable for Part 1
A working local app: `npm run dev` (frontend) + `uvicorn` (backend), full loop from
JD paste to tailored resume download, using either a template or uploaded resume.

---

## PART 2 — Build after Part 1 looks good

**Scope: polish, multi-resume/JD management, and platform-grade features.**

- [ ] User accounts / auth (so sessions and resume history persist)
- [ ] Resume history — save multiple resume versions, compare across JDs
- [ ] Multiple export formats (DOCX, PDF, plain text ATS-safe version)
- [ ] Cover letter generation agent (reuses Tailoring Agent's context)
- [ ] Batch mode — paste multiple JDs, get ranked fit scores across all of them
- [ ] Diff view — inline highlighted diff between original and tailored resume text
- [ ] More resume templates + custom template builder
- [ ] Analytics dashboard — track ATS score improvements over time, most common gaps across your JDs
- [ ] Integrate with the job-search MCP server (Part 1 of that project) — pull JD directly from a searched job instead of pasting
- [ ] Streaming responses in UI (LangGraph streaming → WebSocket → live-updating agent status)
- [ ] Production deployment (containerize FastAPI + LangGraph, deploy frontend to Vercel/Netlify)

---

## Repo structure (Part 1)

```
resume-ats-platform/
├── PROJECT_PLAN.md          (this file)
├── backend/
│   ├── app/
│   │   ├── main.py                  (FastAPI app)
│   │   ├── graph/
│   │   │   ├── state.py             (LangGraph state schema)
│   │   │   ├── graph.py             (graph wiring)
│   │   │   └── nodes/
│   │   │       ├── resume_parser.py
│   │   │       ├── jd_analyzer.py
│   │   │       ├── ats_scorer.py
│   │   │       ├── tailoring.py
│   │   │       └── export.py
│   │   ├── templates/
│   │   │   ├── template_1.json
│   │   │   ├── template_2.json
│   │   │   └── template_3.json
│   │   └── api/
│   │       └── routes.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── ResumeSelect.tsx
    │   │   ├── JDInput.tsx
    │   │   ├── AnalysisResult.tsx
    │   │   ├── ClarifyingQuestions.tsx
    │   │   └── TailoredResult.tsx
    │   ├── components/
    │   │   ├── ATSScoreGauge.tsx
    │   │   ├── KeywordChips.tsx
    │   │   └── ScoreComparison.tsx
    │   └── api/client.ts
    ├── package.json
    └── tailwind.config.ts
```

---

## Design direction (frontend)

"Classic production web" — not generic SaaS-purple-gradient. Direction to aim for:
editorial/document-focused, calm neutral palette, serif or high-quality sans for
headings (this is a resume tool — typography credibility matters), generous
whitespace, subtle score-gauge animation as the one flashy moment. Think
Linear/Notion-adjacent restraint rather than a "growth-hacked" landing page.

---

## Next step

Confirm this plan, then Part 1 build order will be:
1. Backend graph + nodes (testable via CLI/script first, no UI needed)
2. FastAPI routes wrapping the graph
3. Frontend scaffold + wire to backend
4. End-to-end test with a real resume + real JD
