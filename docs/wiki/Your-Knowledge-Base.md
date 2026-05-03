# Your Knowledge Base

Anansi reads two things: an index file and a directory of markdown pages. You own and maintain these; Anansi is read-only.

## Index file (`INDEX_PATH`)

The index is a JSON file with a root `concepts` array. Each entry has four fields:

```json
{
  "concepts": [
    {
      "id": "hybrid-search",
      "file": "hybrid-search.md",
      "description": "Combining dense (vector) and sparse (BM25/TF-IDF) retrieval for better recall. Covers when to use hybrid over pure vector search and tradeoffs.",
      "tags": ["rag", "retrieval", "vector", "search", "bm25"]
    }
  ]
}
```

| Field | Purpose |
|---|---|
| `id` | Unique identifier used to match quiz requests |
| `file` | The markdown filename in `WIKI_PATH` |
| `description` | What the selector reads to route requests — write it to capture the key terms someone would use |
| `tags` | Additional keywords to aid matching |

## Wiki directory (`WIKI_PATH`)

Each concept needs a markdown file inside your wiki directory. The filename must match the `file` field in the index entry:

```
your-wiki/
├── hybrid-search.md
└── llm-evaluation.md
```

Anansi loads these files to generate questions — the richer and more detailed the page, the better the questions.

## Writing good wiki pages

- Write in your own words, as if explaining the concept to a peer — Anansi will probe that understanding back at you
- Cover definitions, mechanisms, tradeoffs, and examples; the planner draws on all of it
- No required format — prose, bullets, and code snippets all work

## Building your wiki with an agent

Since Anansi is read-only, you manage the wiki and index with your own tooling. A natural workflow is to use an AI coding agent (Claude Code, Codex, etc.) to generate and maintain these files — point it at a topic, a codebase, or a set of documents and have it produce the markdown pages and keep the index in sync.

Anansi then serves as the examiner: your agent builds the knowledge base, Anansi tests whether you've absorbed it.
