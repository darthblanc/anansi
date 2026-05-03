from agent.state import AgentState
from agent.logging_config import get_logger
import os
logger = get_logger(__name__)

WIKI_PATH = os.getenv("WIKI_PATH")


def loader_node(state: AgentState) -> AgentState:
    loaded_content = {}
    logger.info("loader — loading %d concept(s): %s", len(state["selected_concepts"]), state["selected_concepts"])

    for concept_id in state["selected_concepts"]:
        path = f"{WIKI_PATH}/{concept_id}.md"

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
