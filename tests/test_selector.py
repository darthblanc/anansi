import json
from unittest.mock import MagicMock

from agent import embeddings
from agent.nodes import selector


def test_load_index_reads_concepts_from_json(tmp_path):
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"concepts": [{"id": "a", "description": "Concept A"}]}))

    concepts = selector.load_index(str(index_path))

    assert concepts == [{"id": "a", "description": "Concept A"}]


def test_selector_node_filters_rag_candidates_with_llm(monkeypatch, make_state, fake_llm_response):
    state = make_state(user_prompt="quiz me on attention")
    concepts = [{"id": "a", "description": "Concept A"}, {"id": "b", "description": "Concept B"}]
    candidates = [{"id": "a", "description": "Concept A"}]

    monkeypatch.setattr(selector, "load_index", lambda: concepts)
    rag_retrieve_mock = lambda query, all_concepts: candidates
    monkeypatch.setattr(selector, "rag_retrieve", rag_retrieve_mock)

    response = fake_llm_response(json.dumps(["a"]))
    monkeypatch.setattr(selector, "llm", type("FakeLLM", (), {"invoke": staticmethod(lambda messages: response)})())

    result = selector.selector_node(state)

    assert result["selected_concepts"] == ["a"]
    assert result["status"] == "loading"
    assert result["user_prompt"] == "quiz me on attention"


def test_selector_node_feeds_llm_with_cached_embedding_rankings(monkeypatch, make_state, fake_llm_response, tmp_path):
    """End-to-end through the real rag_retrieve: the LLM prompt must reflect the
    candidates ranked from the on-disk embeddings cache, and that cache must be
    reused rather than rebuilt."""
    cache_path = tmp_path / "index.embeddings.json"
    concepts = [
        {"id": "transformers", "description": "Transformer architectures"},
        {"id": "rnns", "description": "Recurrent neural networks"},
        {"id": "gans", "description": "Generative adversarial networks"},
    ]
    cache_path.write_text(json.dumps({
        "transformers": [1.0, 0.0],
        "rnns": [0.0, 1.0],
        "gans": [0.6, 0.6],
    }))

    embed_model = MagicMock()
    embed_model.embed_query.return_value = [1.0, 0.0]  # closest to "transformers", then "gans"

    monkeypatch.setattr(selector, "load_index", lambda: concepts)
    monkeypatch.setattr(embeddings, "_get_cache_path", lambda index_path: cache_path)
    monkeypatch.setattr(embeddings, "_load_config", lambda: {"embeddings": {"top_k": 2}})
    monkeypatch.setattr(embeddings, "_create_embedding_model", lambda cfg: embed_model)

    response = fake_llm_response(json.dumps(["transformers"]))
    captured = {}

    def fake_invoke(messages):
        captured["messages"] = messages
        return response

    monkeypatch.setattr(selector, "llm", type("FakeLLM", (), {"invoke": staticmethod(fake_invoke)})())

    state = make_state(user_prompt="explain attention in transformers")
    result = selector.selector_node(state)

    # cached vectors were reused, not rebuilt from scratch
    embed_model.embed_documents.assert_not_called()

    # the LLM only sees the top_k candidates ranked by cosine similarity over the cached embeddings
    prompt_content = captured["messages"][1]["content"]
    assert "id: transformers" in prompt_content
    assert "id: gans" in prompt_content
    assert "id: rnns" not in prompt_content

    assert result["selected_concepts"] == ["transformers"]
