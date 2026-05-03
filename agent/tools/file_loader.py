from agent.state import AgentState
from agent.logging_config import get_logger
import json
import os

logger = get_logger(__name__)

WIKI_PATH = os.getenv("WIKI_PATH")
INDEX_PATH = os.getenv("INDEX_PATH")


def loader_node(state: AgentState) -> AgentState:
    loaded_content = {}
    logger.info("loader — loading %d concept(s): %s", len(state["selected_concepts"]), state["selected_concepts"])

    with open(INDEX_PATH, "r") as f:
        index = json.load(f)
    id_to_file = {c["id"]: c["file"] for c in index["concepts"]}

    for concept_id in state["selected_concepts"]:
        filename = id_to_file.get(concept_id, f"{concept_id}.md")
        path = f"{WIKI_PATH}/{filename}"

        try:
            with open(path, "r") as f:
                loaded_content[concept_id] = f.read()
            logger.debug("loader — loaded %s (%d chars)", concept_id, len(loaded_content[concept_id]))
        except FileNotFoundError:
            loaded_content[concept_id] = ""
            logger.warning("loader — %s not found, skipping", path)

    logger.info("loader — done, %d concept(s) loaded", len([v for v in loaded_content.values() if v]))
    return {
        **state,
        "loaded_content": loaded_content,
        "status": "planning"
    }
