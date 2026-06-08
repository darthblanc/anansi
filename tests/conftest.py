import os
from unittest.mock import MagicMock

from dotenv import load_dotenv
import pytest

load_dotenv()

os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("INDEX_PATH", "/tmp/anansi-test-index.json")
os.environ.setdefault("WIKI_PATH", "/tmp/anansi-test-wiki")


@pytest.fixture
def make_state():
    def _make_state(**overrides):
        state = {
            "user_prompt": "quiz me on multi agent systems",
            "llm_override": None,
            "embeddings_override": None,
            "selected_concepts": [],
            "loaded_content": {},
            "quiz_plan": [],
            "questions": [],
            "current_question_index": 0,
            "evaluated_questions": [],
            "final_score": None,
            "status": "selecting",
        }
        state.update(overrides)
        return state

    return _make_state


@pytest.fixture
def fake_llm_response():
    def _fake_llm_response(content):
        response = MagicMock()
        response.content = content
        return response

    return _fake_llm_response
