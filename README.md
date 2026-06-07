# Anansi

In West African folklore, Anansi is a spider — keeper of all stories, font of wisdom, and a trickster who demands proof of understanding from those who seek knowledge. This project takes that name: an adversarial examiner that challenges you to prove mastery of your own material.

Built as an extension of [Karpathy's LLM wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), Anansi adds an active learning loop: it quizzes you on the material in your wiki and evaluates your answers.

## How it works

You supply a topic. A LangGraph pipeline of agents handles the rest:

1. **Selector** — embeds your request and concept descriptions, retrieves the top-k semantic matches via cosine similarity (RAG), then passes those candidates to an LLM for a final precise selection
2. **Planner** — uses extended thinking to outline 3–5 questions based on the material
3. **Generator** — turns each outline into a full question (free-answer or MCQ depending on the plan)
4. **Interviewer** — presents each question and collects your answers (terminal or browser)
5. **Evaluator** — scores each answer in parallel using extended thinking, with written feedback
6. **Collector** — aggregates results into a final score

Persistence to PostgreSQL — tracking rolling per-concept scores via exponential moving average — is implemented in `agent/db.py`, but the persister node is currently disabled in the pipeline (see Project structure).

### Grading benchmark — sequential vs parallel

The evaluator scores all questions concurrently via LangGraph's `Send` fan-out (`max_concurrency=4`). Run `python benchmark_grading.py` to reproduce the comparison against sequential grading (`max_concurrency=1`):

```
==================================================
Grading benchmark — sequential vs parallel
==================================================
Questions graded:        8
Sequential (concurrency=1): 26.84s  (3.35s/question)
Parallel   (concurrency=4): 11.98s  (1.50s/question)
Speedup:                 2.24x
==================================================
```

## Tech stack

**Backend**
- **Python 3.12**, [`uv`](https://github.com/astral-sh/uv) for package management
- **LangGraph** — agent orchestration and state management
- **LangChain** — provider-agnostic LLM (Anthropic, OpenAI, Ollama) and embeddings (OpenAI, Ollama) support; configured via `agent_config.json`
- **FastAPI** — REST API server for the web UI
- **PostgreSQL 16** — learner progress tracking (via Docker)
- **LangSmith** — optional tracing

**Frontend**
- **React 19** + **TypeScript**, bundled with **Vite**
- No UI framework — plain CSS with a dark theme

## Setup

### Backend

```bash
# Install Python dependencies
uv sync

# Start PostgreSQL
docker-compose up -d

# Configure environment
cp .env.example .env
# Fill in the API key for your chosen provider:
#   Anthropic → ANTHROPIC_API_KEY
#   OpenAI    → OPENAI_API_KEY
#   Ollama    → no key needed
# Optional: LANGSMITH_API_KEY for tracing
#
# Required: point the agent at your own wiki and index files:
#   WIKI_PATH  → path to the directory containing your wiki markdown files
#   INDEX_PATH → path to your index JSON file (concept registry)

# Configure LLM provider and model
# Edit agent_config.json — set the top-level "provider" and "api_key_env",
# and the "model" for each profile (standard, thinking)
# Supported LLM providers: anthropic, openai, ollama
#
# Configure embeddings provider (used by the selector for RAG retrieval)
# Edit the "embeddings" block in agent_config.json
# Supported embeddings providers: openai (text-embedding-3-small), ollama (nomic-embed-text)
# Concept embeddings are cached to disk next to INDEX_PATH (see "Adding content" for cache-rebuild details)
```

### Frontend

```bash
cd frontend
npm install
```

## Running

### CLI

```bash
uv run python -m agent.main
```

You'll be prompted: `What would you like to be quizzed on?` — answer in the terminal, get results in the terminal.

### Web UI

Start both servers:

```bash
# Terminal 1 — API server
uv run uvicorn app.server:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Then open **http://localhost:5173**.

The Vite dev server proxies all `/api/*` requests to the FastAPI backend on port 8000, so no CORS configuration is needed in development.

![Frontend demo](anansi_ui_demo.gif)

## Question types

| Type | Description | Scoring |
|---|---|---|
| **Free answer** | Open-ended — type a full response | LLM-graded 0.0–1.0 with written feedback |
| **MCQ** | Four lettered options (A/B/C/D) | Exact match, 1.0 or 0.0 |

The planner chooses the type per question: MCQ for factual/recall, free answer for anything requiring explanation or analysis. A quiz typically contains a mix of both.

## Project structure

```
anansi/
├── agent_config.json         # LLM provider + model config; embeddings provider + top_k
├── docker-compose.yml        # PostgreSQL service
│
├── agent/                    # Core pipeline
│   ├── main.py               # LangGraph graph definitions & run_quiz() (CLI entry)
│   ├── llm_factory.py        # LLM provider factory (Anthropic, OpenAI, Ollama)
│   ├── embeddings.py         # Embeddings factory + RAG retrieval + disk cache
│   ├── state.py              # AgentState + QuizQuestion schemas
│   ├── db.py                 # Persistence logic
│   ├── nodes/
│   │   ├── selector.py       # RAG shortlist → LLM final selection
│   │   ├── planner.py        # Quiz plan (extended thinking)
│   │   ├── generator.py      # Question generation
│   │   ├── interviewer.py    # Interactive CLI answer collection
│   │   ├── evaluator.py      # Parallel scoring (extended thinking)
│   │   └── persister.py      # DB writes (currently disabled)
│   └── tools/
│       └── file_loader.py    # Markdown file reader
│
├── app/                      # Web API
│   ├── server.py             # FastAPI routes (/api/quiz/start, /api/quiz/submit)
│   └── session.py            # In-memory quiz session store
│
├── frontend/                 # React + TypeScript + Vite
│   └── src/
│       ├── App.tsx           # Stage machine (topic → quiz → results)
│       ├── api.ts            # Fetch wrappers for the FastAPI backend
│       ├── types.ts          # Shared TypeScript types
│       └── components/
│           ├── TopicForm     # Topic input
│           ├── QuizView      # Question-by-question quiz with bubble nav
│           └── Results       # Score summary + per-question feedback
│
└── db/
    └── init.sql              # Schema: quiz_attempts + concept_profile
```

## Adding content

Anansi is read-only with respect to your wiki — it loads your files to generate questions but never writes to them. You manage the wiki and index yourself, or with your own tooling (Claude Code, Codex, etc.).

- **`INDEX_PATH`** — a JSON file with a `concepts` array. Each entry has four fields:

  | Field | Purpose |
  |---|---|
  | `id` | Unique identifier used to match quiz requests |
  | `file` | The markdown filename in `WIKI_PATH` |
  | `description` | What the selector embeds for RAG retrieval — write it to capture the key terms someone would use |
  | `tags` | Additional keywords to aid matching |

  On first run, Anansi embeds all concept descriptions and writes a cache file (`index.embeddings.json`) alongside `INDEX_PATH`. The cache is reused on subsequent runs and rebuilt automatically whenever the concept set changes.

- **`WIKI_PATH`** — a directory of markdown files; each file's name corresponds to the `file` field of its index entry

To add a new topic, update your wiki and index directly — Anansi picks it up on the next run.
