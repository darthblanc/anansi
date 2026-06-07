import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agent import embeddings


def test_cosine_similarity_identical_vectors():
    assert embeddings._cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    assert embeddings._cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector_returns_zero():
    assert embeddings._cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_get_cache_path_swaps_suffix_for_embeddings_json():
    assert embeddings._get_cache_path("/data/index.json") == Path("/data/index.embeddings.json")


def test_load_or_build_cache_returns_existing_cache_on_id_match(tmp_path):
    index_path = tmp_path / "index.json"
    cache_path = tmp_path / "index.embeddings.json"
    concepts = [{"id": "a", "description": "Concept A"}, {"id": "b", "description": "Concept B"}]
    cache_path.write_text(json.dumps({"a": [0.1, 0.2], "b": [0.3, 0.4]}))

    embed_model = MagicMock()
    cache = embeddings._load_or_build_cache(concepts, embed_model, str(index_path))

    assert cache == {"a": [0.1, 0.2], "b": [0.3, 0.4]}
    embed_model.embed_documents.assert_not_called()


def test_load_or_build_cache_rebuilds_when_ids_change(tmp_path):
    index_path = tmp_path / "index.json"
    cache_path = tmp_path / "index.embeddings.json"
    concepts = [{"id": "a", "description": "Concept A"}, {"id": "b", "description": "Concept B"}]
    cache_path.write_text(json.dumps({"a": [0.1, 0.2]}))

    embed_model = MagicMock()
    embed_model.embed_documents.return_value = [[1.0, 0.0], [0.0, 1.0]]

    cache = embeddings._load_or_build_cache(concepts, embed_model, str(index_path))

    embed_model.embed_documents.assert_called_once_with(["a: Concept A", "b: Concept B"])
    assert cache == {"a": [1.0, 0.0], "b": [0.0, 1.0]}
    assert json.loads(cache_path.read_text()) == {"a": [1.0, 0.0], "b": [0.0, 1.0]}


def test_load_or_build_cache_builds_when_no_cache_exists(tmp_path):
    index_path = tmp_path / "index.json"
    concepts = [{"id": "a", "description": "Concept A"}]

    embed_model = MagicMock()
    embed_model.embed_documents.return_value = [[1.0, 2.0]]

    cache = embeddings._load_or_build_cache(concepts, embed_model, str(index_path))

    assert cache == {"a": [1.0, 2.0]}
    assert (tmp_path / "index.embeddings.json").exists()


def test_rag_retrieve_ranks_by_similarity_and_truncates_to_top_k(monkeypatch, tmp_path):
    concepts = [
        {"id": "low", "description": "low match"},
        {"id": "high", "description": "high match"},
        {"id": "mid", "description": "mid match"},
    ]
    cache = {
        "low": [0.0, 1.0],
        "high": [1.0, 0.0],
        "mid": [0.7, 0.7],
    }

    embed_model = MagicMock()
    embed_model.embed_query.return_value = [1.0, 0.0]

    monkeypatch.setattr(embeddings, "_load_config", lambda: {"embeddings": {"top_k": 2}})
    monkeypatch.setattr(embeddings, "_create_embedding_model", lambda cfg: embed_model)
    monkeypatch.setattr(embeddings, "_load_or_build_cache", lambda concepts, model, path: cache)

    results = embeddings.rag_retrieve("query about high match", concepts, index_path=str(tmp_path / "index.json"))

    assert [c["id"] for c in results] == ["high", "mid"]
