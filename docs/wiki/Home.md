In West African folklore, Anansi is a spider — keeper of all stories, font of wisdom, and a trickster who demands proof of understanding from those who seek knowledge. This project takes that name: an adversarial examiner, a rite of passage between you and the knowledge you claim to hold.

Point Anansi at your own wiki and it will quiz you on what you know — or think you know. You bring the knowledge base; Anansi decides whether you've earned it.

## How it works

A pipeline of agents reads your wiki, plans questions tailored to the material, conducts an interactive quiz, and scores your answers with written feedback. Results persist to PostgreSQL so you can track your mastery of each concept over time.

Questions are a mix of free-answer and MCQ, chosen per question by the planner: MCQ for factual recall, free answer for anything requiring explanation or analysis.

## Pages

- [[Getting Started]] — install, configure, and run Anansi
- [[Your Knowledge Base]] — how to structure your wiki and index
- [[How It Works]] — a closer look at the agent pipeline
