# Anansi

An extension of [Karpathy's LLM wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) with a quiz and evaluator agent. Where the wiki pattern focuses on ingesting and querying a persistent knowledge base, Anansi adds an active learning loop: it quizzes you on the material in your wiki and evaluates your answers.

## How it works

You're prompted for a topic. A LangGraph pipeline of agents handles the rest:

1. **Selector** — matches your request to a concept in `index.json` and loads the relevant `wiki/` page
2. **Planner** — uses extended thinking to outline 3–5 questions based on the material
3. **Generator** — turns each outline into a full question
4. **Interviewer** — conducts the quiz interactively in the terminal
5. **Evaluator** — scores each answer in parallel using extended thinking, with feedback
6. **Collector** — aggregates results and prints your final score

Results persist to PostgreSQL, tracking rolling per-concept scores via exponential moving average.

## Tech stack

- **Python 3.12**, [`uv`](https://github.com/astral-sh/uv) for package management
- **LangGraph** — agent orchestration and state management
- **LangChain Anthropic** — Claude Sonnet 4.6 (primary LLM, with extended thinking)
- **PostgreSQL 16** — learner progress tracking (via Docker)
- **LangSmith** — optional tracing

## Setup

```bash
# Install dependencies
uv sync

# Start PostgreSQL
docker-compose up -d

# Configure environment
cp .env.example .env
# Fill in ANTHROPIC_API_KEY (required), LANGSMITH_API_KEY (optional)
```

## Running

```bash
uv run python -m agent.main
```

You'll be prompted: `What would you like to be quizzed on?`

## Project structure

```
anansi/
├── main.py                   # Entry point
├── index.json                # Concept registry (id → description)
├── docker-compose.yml        # PostgreSQL service
│
├── agent/
│   ├── main.py               # LangGraph graph definition & run_quiz()
│   ├── state.py              # AgentState schema
│   ├── db.py                 # Persistence logic
│   ├── nodes/
│   │   ├── selector.py       # Topic → concept matching
│   │   ├── planner.py        # Quiz plan (extended thinking)
│   │   ├── generator.py      # Question generation
│   │   ├── interviewer.py    # Interactive CLI
│   │   ├── evaluator.py      # Parallel scoring (extended thinking)
│   │   └── persister.py      # DB writes (currently disabled)
│   └── tools/
│       └── file_loader.py    # Markdown file reader
│
├── db/
│   └── init.sql              # Schema: quiz_attempts + concept_profile
└── wiki/
    └── multi-agent-overview.md  # Learning material
```

## Roadmap

- **Provider-agnostic model support** — configurable model provider so the agent can run on OpenAI, Ollama, or any LangChain-compatible LLM, not just Anthropic

## Adding content

To add a new topic to quiz on:

1. Add a markdown page to `wiki/` (following the same format as existing pages)
2. Add an entry to `index.json` with a matching `id` and a short description
3. The selector will automatically route relevant quiz requests to the new material
