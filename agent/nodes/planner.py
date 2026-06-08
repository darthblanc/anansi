import json
from agent.llm_factory import create_llm, extract_text
from agent.state import AgentState
from agent.logging_config import get_logger
from agent.prompts import PROMPTS

logger = get_logger(__name__)

_cached_thinking_llm = None


def _get_llm(state: AgentState):
    override = state.get("llm_override")
    if override:
        return create_llm(with_thinking=True, override=override)
    global _cached_thinking_llm
    if _cached_thinking_llm is None:
        _cached_thinking_llm = create_llm(with_thinking=True)
    return _cached_thinking_llm


def planner_node(state: AgentState) -> AgentState:
    logger.info("planner — planning quiz from %d concept(s)", len(state["loaded_content"]))
    llm = _get_llm(state)

    content_str = "\n\n---\n\n".join([
        f"# {concept_id}\n{content}"
        for concept_id, content in state["loaded_content"].items()
        if content
    ])

    response = llm.invoke([
        {"role": "system", "content": PROMPTS["planner"]},
        {
            "role": "user",
            "content": f"""User request: {state['user_prompt']}

Learning material:
{content_str}

Create a quiz plan with 3-5 questions that test genuine understanding, not memorization."""
        }
    ])

    quiz_plan = json.loads(extract_text(response.content))
    logger.info("planner — planned %d question(s): %s", len(quiz_plan), [q.get("focus") for q in quiz_plan])

    return {
        **state,
        "quiz_plan": quiz_plan,
        "status": "quizzing"
    }
