"""Quick end-to-end smoke test for the RAG-augmented selector."""
from unittest.mock import patch

TOPIC = "retrieval augmented generation"


def _auto_answer(prompt=""):
    print(prompt, end="", flush=True)
    # MCQ prompts contain "A/B/C/D"
    ans = "A" if "/" in prompt else "not sure"
    print(ans)
    return ans


with patch("builtins.input", side_effect=_auto_answer):
    from agent.main import run_quiz
    run_quiz(TOPIC)
