import json
from agent.llm_factory import create_llm
from agent.state import AgentState
from agent.logging_config import get_logger

logger = get_logger(__name__)
llm = create_llm()

def load_index(index_path: str = "index.json") -> list[dict]:
    with open(index_path, "r") as f:
        return json.load(f)["concepts"]

def selector_node(state: AgentState) -> AgentState:
    logger.info("selector — prompt: %r", state["user_prompt"])
    concepts = load_index()
    logger.debug("selector — %d concepts available", len(concepts))

    # build a compact index string for the LLM
    index_str = "\n".join([
        f"- id: {c['id']} | description: {c['description']}"
        for c in concepts
    ])

    response = llm.invoke([
        {
            "role": "system",
            "content": """You are a concept selector for a learning system.
Given a user request and a list of concepts, return ONLY a JSON array of concept ids that are relevant.
Example: ["multi-agent-systems", "react-agents"]
Return nothing else. No explanation, no markdown."""
        },
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