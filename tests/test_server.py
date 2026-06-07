from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app import server


@pytest.fixture
def client():
    return TestClient(server.app)


def test_start_quiz_returns_session_id_and_stripped_questions(monkeypatch, client, make_state):
    final_state = make_state(
        questions=[
            {
                "question": "What is attention?",
                "question_type": "mcq",
                "options": ["A", "B", "C", "D"],
                "correct_option": 1,
                "user_answer": "",
                "score": None,
                "feedback": None,
            },
            {
                "question": "Explain transformers.",
                "question_type": "free",
                "options": None,
                "correct_option": None,
                "user_answer": "",
                "score": None,
                "feedback": None,
            },
        ],
    )

    fake_graph = MagicMock()
    fake_graph.invoke.return_value = final_state
    monkeypatch.setattr(server, "build_generation_graph", lambda: fake_graph)
    monkeypatch.setattr(server, "create_session", lambda state: "session-123")

    response = client.post("/api/quiz/start", json={"topic": "transformers"})

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "session-123"
    assert body["questions"] == [
        {"question": "What is attention?", "question_type": "mcq", "options": ["A", "B", "C", "D"]},
        {"question": "Explain transformers.", "question_type": "free", "options": None},
    ]
    # answer-key fields must not leak to the client
    assert "correct_option" not in body["questions"][0]

    fake_graph.invoke.assert_called_once()
    invoked_state = fake_graph.invoke.call_args[0][0]
    assert invoked_state["user_prompt"] == "transformers"


def test_submit_quiz_merges_answers_and_returns_evaluated_results(monkeypatch, client, make_state):
    stored_state = make_state(
        questions=[
            {"question": "Q1?", "question_type": "free", "options": None, "correct_option": None,
             "user_answer": "", "score": None, "feedback": None},
            {"question": "Q2?", "question_type": "free", "options": None, "correct_option": None,
             "user_answer": "", "score": None, "feedback": None},
        ],
    )
    monkeypatch.setattr(server, "get_session", lambda sid: stored_state)

    final_state = make_state(
        final_score=0.75,
        evaluated_questions=[
            {"question": "Q2?", "question_type": "free", "user_answer": "second answer",
             "score": 0.5, "feedback": "okay", "question_index": 1},
            {"question": "Q1?", "question_type": "free", "user_answer": "first answer",
             "score": 1.0, "feedback": "great", "question_index": 0},
        ],
    )
    fake_graph = MagicMock()
    fake_graph.invoke.return_value = final_state
    monkeypatch.setattr(server, "build_evaluation_graph", lambda: fake_graph)

    response = client.post("/api/quiz/submit", json={
        "session_id": "session-123",
        "answers": ["first answer", "second answer"],
    })

    assert response.status_code == 200
    body = response.json()
    assert body["final_score"] == 0.75
    # results are sorted by question_index, regardless of graph output order
    assert [q["question"] for q in body["evaluated"]] == ["Q1?", "Q2?"]
    assert body["evaluated"][0]["user_answer"] == "first answer"
    assert body["evaluated"][1]["user_answer"] == "second answer"

    invoked_state = fake_graph.invoke.call_args[0][0]
    assert invoked_state["questions"][0]["user_answer"] == "first answer"
    assert invoked_state["questions"][1]["user_answer"] == "second answer"
    assert invoked_state["status"] == "evaluating"
