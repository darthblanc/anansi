from unittest.mock import MagicMock

import pytest

from agent import db


def test_get_connection_uses_env_vars(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "quizdb")
    monkeypatch.setenv("POSTGRES_USER", "quizuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")

    fake_connect = MagicMock(return_value="connection")
    monkeypatch.setattr(db.psycopg2, "connect", fake_connect)

    result = db.get_connection()

    assert result == "connection"
    fake_connect.assert_called_once_with(
        dbname="quizdb",
        user="quizuser",
        password="secret",
        host="localhost",
        port="5432",
    )


def _state():
    return {
        "selected_concepts": ["concept-a", "concept-b"],
        "evaluated_questions": [
            {"question": "Q1?", "user_answer": "A1", "score": 1.0, "feedback": "Great"},
            {"question": "Q2?", "user_answer": "A2", "score": 0.5, "feedback": "Okay"},
        ],
        "final_score": 0.75,
    }


def test_persist_results_executes_inserts_and_commits(monkeypatch):
    fake_cursor = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(db, "get_connection", lambda: fake_conn)

    db.persist_results(_state())

    # 2 questions + 2 concepts = 4 inserts
    assert fake_cursor.execute.call_count == 4
    fake_conn.commit.assert_called_once()
    fake_conn.rollback.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_conn.close.assert_called_once()


def test_persist_results_rolls_back_and_reraises_on_error(monkeypatch):
    fake_cursor = MagicMock()
    fake_cursor.execute.side_effect = RuntimeError("boom")
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(db, "get_connection", lambda: fake_conn)

    with pytest.raises(RuntimeError, match="boom"):
        db.persist_results(_state())

    fake_conn.rollback.assert_called_once()
    fake_conn.commit.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_conn.close.assert_called_once()
