import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

ALPHA = 0.3


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )


def persist_results(state: dict):
    conn = get_connection()
    cur = conn.cursor()

    try:
        for q in state["evaluated_questions"]:
            cur.execute("""
                INSERT INTO quiz_attempts 
                    (concept, question, user_answer, score, evaluator_feedback)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                ", ".join(state["selected_concepts"]),
                q["question"],
                q["user_answer"],
                q["score"],
                q["feedback"]
            ))

        for concept in state["selected_concepts"]:
            cur.execute("""
                INSERT INTO concept_profile (concept, rolling_score, attempts, last_attempted)
                VALUES (%s, %s, 1, NOW())
                ON CONFLICT (concept) DO UPDATE SET
                    rolling_score = concept_profile.rolling_score * %s + EXCLUDED.rolling_score * %s,
                    attempts = concept_profile.attempts + 1,
                    last_attempted = NOW()
            """, (concept, state["final_score"], 1 - ALPHA, ALPHA))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()