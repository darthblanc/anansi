import json

from agent.nodes import evaluator


def _mcq_question(user_answer="A", correct_option=0):
    return {
        "question": "What is 2+2?",
        "question_type": "mcq",
        "options": ["4", "5", "6", "7"],
        "correct_option": correct_option,
        "user_answer": user_answer,
    }


def test_evaluate_mcq_correct_answer():
    q = _mcq_question(user_answer="A", correct_option=0)

    result = evaluator._evaluate_mcq(q, 0)

    evaluated = result["evaluated_questions"][0]
    assert evaluated["score"] == 1.0
    assert "Correct" in evaluated["feedback"]
    assert evaluated["question_index"] == 0


def test_evaluate_mcq_incorrect_answer():
    q = _mcq_question(user_answer="B", correct_option=0)

    result = evaluator._evaluate_mcq(q, 2)

    evaluated = result["evaluated_questions"][0]
    assert evaluated["score"] == 0.0
    assert "Incorrect" in evaluated["feedback"]
    assert "You chose: 5" in evaluated["feedback"]
    assert evaluated["question_index"] == 2


def test_evaluate_mcq_no_answer_given():
    q = _mcq_question(user_answer="not a letter", correct_option=1)

    result = evaluator._evaluate_mcq(q, 0)

    evaluated = result["evaluated_questions"][0]
    assert evaluated["score"] == 0.0
    assert "You chose: no answer" in evaluated["feedback"]


def test_evaluate_one_node_delegates_mcq_to_evaluate_mcq(make_state):
    q = _mcq_question(user_answer="A", correct_option=0)
    state = make_state(questions=[q], current_question_index=0)

    result = evaluator.evaluate_one_node(state)

    evaluated = result["evaluated_questions"][0]
    assert evaluated["question_type"] == "mcq"
    assert evaluated["score"] == 1.0


def test_evaluate_one_node_handles_free_text_questions(monkeypatch, make_state, fake_llm_response):
    free_question = {
        "question": "Explain attention.",
        "question_type": "free",
        "options": None,
        "correct_option": None,
        "user_answer": "It lets the model focus on relevant tokens.",
    }
    state = make_state(
        questions=[free_question],
        current_question_index=0,
        loaded_content={"attention": "Attention is a mechanism..."},
    )

    response = fake_llm_response(json.dumps({"score": 0.8, "feedback": "Mostly correct."}))
    monkeypatch.setattr(evaluator, "_cached_thinking_llm", type("FakeLLM", (), {"invoke": staticmethod(lambda messages: response)})())

    result = evaluator.evaluate_one_node(state)

    evaluated = result["evaluated_questions"][0]
    assert evaluated["question_type"] == "free"
    assert evaluated["score"] == 0.8
    assert evaluated["feedback"] == "Mostly correct."
    assert evaluated["options"] is None
    assert evaluated["correct_option"] is None


def test_collect_node_averages_scores_and_sets_status(make_state):
    state = make_state(evaluated_questions=[
        {"score": 1.0},
        {"score": 0.5},
        {"score": 0.0},
    ])

    result = evaluator.collect_node(state)

    assert result["final_score"] == 0.5
    assert result["status"] == "persisting"
