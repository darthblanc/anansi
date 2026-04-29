import json
from agent.llm_factory import create_llm
from agent.state import AgentState
from agent.logging_config import get_logger

logger = get_logger(__name__)
llm = create_llm(with_thinking=True)

_SYSTEM_PROMPT = """You are a strict but fair quiz evaluator for a learning system.
Given a question, the student's answer, and the source material, evaluate the answer.
Return ONLY a JSON object with two keys:
- score: a float between 0.0 and 1.0
- feedback: a short explanation of what was correct, incorrect, or missing

No explanation, no markdown.
Example:
{
    "score": 0.7,
    "feedback": "You correctly identified context management and parallelisation but missed distributed development. You also didn't explain the tradeoff of added complexity."
}"""


def _extract_text(content) -> str:
    if isinstance(content, list):
        return next(block["text"] for block in content if block.get("type") == "text")
    return content


def evaluate_one_node(state: AgentState) -> dict:
    i = state["current_question_index"]
    q = state["questions"][i]
    logger.debug("evaluator — scoring Q%d: %r", i + 1, q["question"])

    content_str = "\n\n---\n\n".join([
        f"# {concept_id}\n{content}"
        for concept_id, content in state["loaded_content"].items()
        if content
    ])

    response = llm.invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Question: {q['question']}\n\n"
                f"Student answer: {q['user_answer']}\n\n"
                f"Source material:\n{content_str}\n\n"
                "Evaluate the answer strictly based on the source material, not general knowledge."
            ),
        },
    ])

    result = json.loads(_extract_text(response.content))
    logger.debug("evaluator — Q%d score: %.0f%%", i + 1, result["score"] * 100)

    return {
        "evaluated_questions": [{
            "question": q["question"],
            "user_answer": q["user_answer"],
            "score": result["score"],
            "feedback": result["feedback"],
            "question_index": i,
        }]
    }


def collect_node(state: AgentState) -> dict:
    evaluated = state["evaluated_questions"]
    final_score = sum(q["score"] for q in evaluated) / len(evaluated)
    logger.info("evaluator — done, final score: %.0f%%", final_score * 100)
    return {
        "final_score": final_score,
        "status": "persisting",
    }
