CREATE TABLE quiz_attempts (
    id SERIAL PRIMARY KEY,
    concept TEXT NOT NULL,
    question TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    score FLOAT NOT NULL,
    evaluator_feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE concept_profile (
    concept TEXT PRIMARY KEY,
    rolling_score FLOAT NOT NULL,
    attempts INT DEFAULT 0,
    last_attempted TIMESTAMP
);