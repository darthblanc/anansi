import json
import os
from pathlib import Path

from agent.logging_config import get_logger

logger = get_logger(__name__)

INDEX_PATH = os.getenv("INDEX_PATH")


def _get_cache_path(index_path: str) -> Path:
    return Path(index_path).with_suffix(".embeddings.json")


def _load_config() -> dict:
    config_path = Path(__file__).parent.parent / "agent_config.json"
    with open(config_path) as f:
        return json.load(f)


def _create_embedding_model(cfg: dict):
    provider = cfg.get("provider", "openai")
    model = cfg.get("model", "text-embedding-3-small")

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        api_key_env = cfg.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.environ.get(api_key_env)
        return OpenAIEmbeddings(model=model, api_key=api_key)

    elif provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=model)

    else:
        raise ValueError(f"Unknown embeddings provider: {provider!r}. Supported: 'openai', 'ollama'")


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _load_or_build_cache(
    concepts: list[dict],
    embed_model,
    index_path: str,
) -> dict[str, list[float]]:
    cache_path = _get_cache_path(index_path)
    current_ids = {c["id"] for c in concepts}

    if cache_path.exists():
        with open(cache_path) as f:
            cache = json.load(f)
        if current_ids == set(cache.keys()):
            logger.debug("embeddings — cache hit (%d concepts)", len(cache))
            return cache
        logger.info("embeddings — index changed, rebuilding cache")

    logger.info("embeddings — building cache for %d concepts", len(concepts))
    texts = [f"{c['id']}: {c['description']}" for c in concepts]
    vectors = embed_model.embed_documents(texts)
    cache = {c["id"]: vec for c, vec in zip(concepts, vectors)}

    with open(cache_path, "w") as f:
        json.dump(cache, f)
    logger.info("embeddings — cache written to %s", cache_path)
    return cache


def rag_retrieve(
    query: str,
    concepts: list[dict],
    index_path: str = INDEX_PATH,
) -> list[dict]:
    cfg = _load_config().get("embeddings", {})
    top_k = cfg.get("top_k", 10)
    embed_model = _create_embedding_model(cfg)

    cache = _load_or_build_cache(concepts, embed_model, index_path)
    query_vec = embed_model.embed_query(query)

    scored = sorted(
        [(c, _cosine_similarity(query_vec, cache[c["id"]])) for c in concepts if c["id"] in cache],
        key=lambda x: x[1],
        reverse=True,
    )

    results = [c for c, _ in scored[:top_k]]
    logger.info(
        "embeddings — RAG shortlisted %d/%d concepts: %s",
        len(results),
        len(concepts),
        [c["id"] for c in results],
    )
    return results
