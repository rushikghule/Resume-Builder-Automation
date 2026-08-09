# Setup — Run With a Real LLM

This gets Part 1 running end-to-end in your browser, using whichever LLM
provider you prefer.

---

## 0. Prerequisites

- Python 3.10+
- Node.js 18+
- One of: a free Groq API key, a free OpenRouter API key, or Ollama installed locally

---

## 1. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1a. Configure your LLM provider

Copy the example env file:

```bash
cp .env.example .env
```

Open `.env` and pick **one** provider block to fill in (the others can stay empty).

---

### Option A — Groq (fastest to set up, free tier)

1. Go to https://console.groq.com/keys
2. Sign up / log in, click **Create API Key**, copy it.
3. Edit `backend/.env`:
   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_your_actual_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

---

### Option B — OpenRouter (access to Claude, GPT, etc. through one key)

1. Go to https://openrouter.ai/keys
2. Sign up / log in, click **Create Key**, copy it.
3. Edit `backend/.env`:
   ```env
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-your_actual_key_here
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   ```
   (Swap `OPENROUTER_MODEL` for any model slug from https://openrouter.ai/models — e.g. `meta-llama/llama-3.3-70b-instruct` for a cheaper option.)

---

### Option C — Ollama (fully local, no API key, no internet needed after setup)

1. Install Ollama: https://ollama.com/download
2. Pull the model:
   ```bash
   ollama pull qwen3:4b-q4_K_M
   ```
3. Make sure Ollama is running (it usually starts automatically; otherwise `ollama serve`).
4. Edit `backend/.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen3:4b-q4_K_M
   ```

> Note: qwen3:4b is a small model — good for validating the flow works, but
> expect lower-quality parsing/tailoring than Groq/OpenRouter's larger models.
> You can also pick the provider **per request** from the UI dropdown, so you
> don't have to commit to one in `.env` — just fill in whichever key(s) you
> want available and choose in the browser.

---

### 1b. Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

Check it's alive: open http://localhost:8000/health — you should see
`{"status": "ok", "llm_provider": "groq"}` (or whichever you set).

---

## 2. Frontend setup

Open a **new terminal**:

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (usually **http://localhost:5173**).

---

## 3. Use it

1. Pick a built-in template or upload your own resume (PDF/DOCX/TXT).
2. Paste a real job description.
3. Pick your LLM provider from the dropdown (must match one you configured — you can leave all three keys filled in `.env` and switch freely in the UI, since `llm_provider` is sent per-request).
4. Click **Analyze match** → see your baseline ATS score + gaps.
5. Answer the clarifying questions (skip any that don't apply).
6. Click through to get your tailored resume, before/after score comparison, and a `.docx` download.

---

## Switching providers without restarting

The `llm_provider` field is sent with every `/analyze` call — so as long as
you've filled in credentials for more than one provider in `.env`, you can
switch the dropdown per session without touching the backend again. Only
`ollama` also requires the local server actually running at the configured
`OLLAMA_BASE_URL`.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ADZUNA_APP_ID / ADZUNA_APP_KEY not set` | Not relevant to this app — that error is from the separate job-search MCP project, not this one. |
| `GROQ_API_KEY not set` error in browser | Check `.env` was saved and the backend was restarted after editing it. |
| Ollama: connection refused | Run `ollama serve` in a terminal, or check `ollama list` shows the model pulled. |
| CORS error in browser console | Confirm `CORS_ORIGINS` in `.env` includes `http://localhost:5173` (it does by default). |
| Frontend shows blank template list | Backend isn't running or isn't reachable — check http://localhost:8000/health directly. |
