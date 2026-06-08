import json
import os
from agent.llm_factory import create_llm
from agent.embeddings import rag_retrieve
from agent.state import AgentState
from agent.logging_config import get_logger
from agent.prompts import PROMPTS

logger = get_logger(__name__)

INDEX_PATH = os.getenv("INDEX_PATH")

_cached_llm = None


def _get_llm(state: AgentState):
    override = state.get("llm_override")
    if override:
        return create_llm(override=override)
    global _cached_llm
    if _cached_llm is None:
        _cached_llm = create_llm()
    return _cached_llm


def load_index(index_path: str = INDEX_PATH) -> list[dict]:
    with open(index_path, "r") as f:
        return json.load(f)["concepts"]

def selector_node(state: AgentState) -> AgentState:
    logger.info("selector — prompt: %r", state["user_prompt"])
    llm = _get_llm(state)
    concepts = load_index()
    logger.debug("selector — %d concepts available", len(concepts))

    # RAG: shortlist semantically relevant candidates before LLM filtering
    candidates = rag_retrieve(state["user_prompt"], concepts, override=state.get("embeddings_override"))
    logger.debug("selector — LLM filtering %d RAG candidates", len(candidates))

    index_str = "\n".join([
        f"- id: {c['id']} | description: {c['description']}"
        for c in candidates
    ])

    response = llm.invoke([
        {"role": "system", "content": PROMPTS["selector"]},
        {
            "role": "user",
            "content": f"""User request: {state['user_prompt']}

Available concepts:
{index_str}

Return the relevant concept ids as a JSON array."""
        }
    ])


    selected = json.loads(response.content)
    logger.info("selector — selected concepts: %s", selected)

    return {
        **state,
        "selected_concepts": selected,
        "status": "loading"
    }