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


def _evaluate_mcq(q: dict, i: int) -> dict:
    letters = "ABCD"
    chosen = letters.find(q["user_answer"])
    correct = q["correct_option"]
    correct_letter = letters[correct]
    correct_text = q["options"][correct]

    if chosen == correct:
        score = 1.0
        feedback = f"Correct! {correct_letter}) {correct_text}"
    else:
        chosen_text = q["options"][chosen] if chosen >= 0 else "no answer"
        score = 0.0
        feedback = f"Incorrect. The right answer was {correct_letter}) {correct_text}. You chose: {chosen_text}."

    logger.debug("evaluator — Q%d (mcq) score: %.0f%%", i + 1, score * 100)
    return {
        "evaluated_questions": [{
            "question": q["question"],
            "question_type": "mcq",
            "options": q["options"],
            "correct_option": q["correct_option"],
            "user_answer": q["user_answer"],
            "score": score,
            "feedback": feedback,
            "question_index": i,
        }]
    }


def evaluate_one_node(state: AgentState) -> dict:
    i = state["current_question_index"]
    q = state["questions"][i]
    logger.debug("evaluator — scoring Q%d: %r", i + 1, q["question"])

    if q.get("question_type") == "mcq":
        return _evaluate_mcq(q, i)

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
            "question_type": q.get("question_type", "free"),
            "options": None,
            "correct_option": None,
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
