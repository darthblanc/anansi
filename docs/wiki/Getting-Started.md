# Getting Started

## Prerequisites

- Python 3.12
- [`uv`](https://github.com/astral-sh/uv) for package management
- Docker (for PostgreSQL)
- An API key for your chosen LLM provider (Anthropic, OpenAI, or Ollama running locally)

## Install

```bash
uv sync
```

## Start PostgreSQL

```bash
docker-compose up -d
```

## Configure your environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

| Variable | Required | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | If using Anthropic | |
| `OPENAI_API_KEY` | If using OpenAI | |
| `WIKI_PATH` | Yes | Path to your wiki directory |
| `INDEX_PATH` | Yes | Path to your `index.json` |
| `LANGSMITH_API_KEY` | No | For tracing |

`WIKI_PATH` and `INDEX_PATH` are required — Anansi cannot run without them. See [[Your Knowledge Base]] for how to structure these files.

## Configure your LLM provider

Edit `agent_config.json` and set `provider`, `api_key_env`, and `model` for each profile. Supported providers: `anthropic`, `openai`, `ollama`.

## Run

```bash
uv run python -m agent.main
```

You'll be prompted: `What would you like to be quizzed on?`
