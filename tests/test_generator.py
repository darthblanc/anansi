import json

from agent.nodes import generator


def _fake_llm(responses):
    iterator = iter(responses)
    return type("FakeLLM", (), {"invoke": staticmethod(lambda messages: next(iterator))})()


def test_generator_node_builds_mcq_and_free_questions(monkeypatch, make_state, fake_llm_response):
    state = make_state(
        loaded_content={"concept-a": "Concept A material", "concept-b": "Concept B material"},
        quiz_plan=[
            {"concept": "concept-a", "type": "mcq", "focus": "basics"},
            {"concept": "concept-b", "type": "free", "focus": "deep dive"},
        ],
    )

    mcq_response = fake_llm_response(json.dumps({
        "question": "Which is correct?",
        "options": ["A", "B", "C", "D"],
        "correct_option": 2,
    }))
    free_response = fake_llm_response(json.dumps({"question": "Explain concept B."}))

    monkeypatch.setattr(generator, "_cached_llm", _fake_llm([mcq_response, free_response]))

    result = generator.generator_node(state)

    questions = result["questions"]
    assert len(questions) == 2

    mcq_q = questions[0]
    assert mcq_q == {
        "question": "Which is correct?",
        "question_type": "mcq",
        "options": ["A", "B", "C", "D"],
        "correct_option": 2,
        "user_answer": "",
        "score": None,
        "feedback": None,
    }

    free_q = questions[1]
    assert free_q == {
        "question": "Explain concept B.",
        "question_type": "free",
        "options": None,
        "correct_option": None,
        "user_answer": "",
        "score": None,
        "feedback": None,
    }

    assert result["current_question_index"] == 0
    assert result["status"] == "evaluating"
