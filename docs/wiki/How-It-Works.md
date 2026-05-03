# How It Works

When you enter a topic, Anansi runs a LangGraph pipeline of six agents in sequence.

## The pipeline

### 1. Selector
Reads your `index.json` and uses an LLM to match your request against the concept descriptions and tags. Returns a list of matching concept IDs. The `description` field is the primary signal — write it to capture the terms someone would use when asking about that topic.

### 2. File Loader
Resolves each selected concept ID to its markdown file via the `file` field in the index, then loads the content from your wiki directory.

### 3. Planner
Uses extended thinking to read the loaded wiki content and outline 3–5 questions. For each question it decides the type: MCQ for factual recall, free answer for anything requiring explanation or analysis.

### 4. Generator
Turns each outline item into a fully formed question. MCQ questions include four lettered options (A–D).

### 5. Interviewer
Conducts the quiz interactively in the terminal, collecting your answers one question at a time.

### 6. Evaluator
Scores all answers in parallel using extended thinking. Free-answer questions are graded 0.0–1.0 with written feedback. MCQ questions are exact match: 1.0 or 0.0.

## Results

Your score for each attempt is recorded in PostgreSQL. Per-concept mastery is tracked as an exponential moving average, so your score reflects recent performance more than older attempts.

## Question types

| Type | Format | Scoring |
|---|---|---|
| **Free answer** | Open-ended — type a full response | LLM-graded 0.0–1.0 with feedback |
| **MCQ** | Four options (A/B/C/D) — type a letter | Exact match, 1.0 or 0.0 |
