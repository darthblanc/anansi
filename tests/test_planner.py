import json

from agent.nodes import planner


def test_planner_node_parses_quiz_plan_from_fenced_json(monkeypatch, make_state, fake_llm_response):
    state = make_state(
        user_prompt="quiz me on transformers",
        loaded_content={"transformers": "Transformers are a neural network architecture..."},
    )

    plan = [
        {"concept": "transformers", "type": "mcq", "focus": "self-attention"},
        {"concept": "transformers", "type": "free", "focus": "positional encoding"},
    ]
    response = fake_llm_response([
        {"type": "thinking", "text": "Let me design a good quiz plan..."},
        {"type": "text", "text": "```json\n" + json.dumps(plan) + "\n```"},
    ])
    monkeypatch.setattr(planner, "_cached_thinking_llm", type("FakeLLM", (), {"invoke": staticmethod(lambda messages: response)})())

    result = planner.planner_node(state)

    assert result["quiz_plan"] == plan
    assert result["status"] == "quizzing"
    assert result["user_prompt"] == "quiz me on transformers"


def test_planner_node_skips_empty_loaded_content(monkeypatch, make_state, fake_llm_response):
    state = make_state(loaded_content={"empty": "", "filled": "Some content"})

    captured = {}

    def fake_invoke(messages):
        captured["user_message"] = messages[1]["content"]
        return fake_llm_response("[]")

    monkeypatch.setattr(planner, "_cached_thinking_llm", type("FakeLLM", (), {"invoke": staticmethod(fake_invoke)})())

    planner.planner_node(state)

    assert "empty" not in captured["user_message"]
    assert "filled" in captured["user_message"]
    assert "Some content" in captured["user_message"]
