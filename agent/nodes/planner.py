import json
from langchain_anthropic import ChatAnthropic
from agent.state import AgentState
from agent.logging_config import get_logger

logger = get_logger(__name__)
llm = ChatAnthropic(model="claude-sonnet-4-6", thinking={"type": "adaptive"})


def _extract_text(content) -> str:
    if isinstance(content, list):
        return next(block["text"] for block in content if block.get("type") == "text")
    return content


def planner_node(state: AgentState) -> AgentState:
    logger.info("planner — planning quiz from %d concept(s)", len(state["loaded_content"]))

    content_str = "\n\n---\n\n".join([
        f"# {concept_id}\n{content}"
        for concept_id, content in state["loaded_content"].items()
        if content
    ])

    response = llm.invoke([
        {
            "role": "system",
            "content": """You are a quiz planner for a learning system.
Given learning material, create a quiz plan as a JSON array of question outlines.
Each outline should specify:
- the concept being tested
- the type of question (conceptual, applied, compare-contrast)
- the key idea being tested

Return ONLY a JSON array. No explanation, no markdown.
Example:
[
    {"concept": "multi-agent-systems", "type": "conceptual", "focus": "when to use multi-agent over single agent"},
    {"concept": "react-agents", "type": "applied", "focus": "how the reason-act loop handles tool failures"}
]"""
        },
        {
            "role": "user",
            "content": f"""User request: {state['user_prompt']}

Learning material:
{content_str}

Create a quiz plan with 3-5 questions that test genuine understanding, not memorization."""
        }
    ])

    quiz_plan = json.loads(_extract_text(response.content))
    logger.info("planner — planned %d question(s): %s", len(quiz_plan), [q.get("focus") for q in quiz_plan])

    return {
        **state,
        "quiz_plan": quiz_plan,
        "status": "quizzing"
    }
