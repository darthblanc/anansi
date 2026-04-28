import json
from langchain_anthropic import ChatAnthropic
from agent.state import AgentState
from agent.logging_config import get_logger

logger = get_logger(__name__)
llm = ChatAnthropic(model="claude-sonnet-4-6")


def generator_node(state: AgentState) -> AgentState:
    logger.info("generator — generating %d question(s)", len(state["quiz_plan"]))
    questions = []

    for i, outline in enumerate(state["quiz_plan"], 1):
        concept_id = outline["concept"]
        content = state["loaded_content"].get(concept_id, "")
        logger.debug("generator — Q%d: concept=%s type=%s focus=%r", i, concept_id, outline["type"], outline["focus"])

        response = llm.invoke([
            {
                "role": "system",
                "content": """You are a quiz question generator for a learning system.
Given a question outline and learning material, generate a single clear question.
Return ONLY a JSON object with one key: "question".
No explanation, no markdown.
Example: {"question": "What are the three legitimate reasons to use a multi-agent system over a single agent?"}"""
            },
            {
                "role": "user",
                "content": f"""Question outline:
- concept: {outline['concept']}
- type: {outline['type']}
- focus: {outline['focus']}

Learning material:
{content}

Generate the question."""
            }
        ])

        result = json.loads(response.content)
        logger.debug("generator — Q%d generated: %r", i, result["question"])

        questions.append({
            "question": result["question"],
            "user_answer": "",
            "score": None,
            "feedback": None
        })

    logger.info("generator — done, %d question(s) ready", len(questions))
    return {
        **state,
        "questions": questions,
        "current_question_index": 0,
        "status": "evaluating"
    }
