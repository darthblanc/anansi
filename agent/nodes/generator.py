import json
from agent.llm_factory import create_llm
from agent.state import AgentState
from agent.logging_config import get_logger
from agent.prompts import PROMPTS

logger = get_logger(__name__)
llm = create_llm()


def generator_node(state: AgentState) -> AgentState:
    logger.info("generator — generating %d question(s)", len(state["quiz_plan"]))
    questions = []

    for i, outline in enumerate(state["quiz_plan"], 1):
        concept_id = outline["concept"]
        content = state["loaded_content"].get(concept_id, "")
        logger.debug("generator — Q%d: concept=%s type=%s focus=%r", i, concept_id, outline["type"], outline["focus"])

        if outline["type"] == "mcq":
            response = llm.invoke([
                {"role": "system", "content": PROMPTS["generator_mcq"]},
                {
                    "role": "user",
                    "content": f"""Question outline:
- concept: {outline['concept']}
- type: mcq
- focus: {outline['focus']}

Learning material:
{content}

Generate the multiple-choice question."""
                }
            ])
            result = json.loads(response.content)
            logger.debug("generator — Q%d (mcq) generated: %r", i, result["question"])
            questions.append({
                "question": result["question"],
                "question_type": "mcq",
                "options": result["options"],
                "correct_option": result["correct_option"],
                "user_answer": "",
                "score": None,
                "feedback": None,
            })
        else:
            response = llm.invoke([
                {"role": "system", "content": PROMPTS["generator_free"]},
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
                "question_type": "free",
                "options": None,
                "correct_option": None,
                "user_answer": "",
                "score": None,
                "feedback": None,
            })

    logger.info("generator — done, %d question(s) ready", len(questions))
    return {
        **state,
        "questions": questions,
        "current_question_index": 0,
        "status": "evaluating"
    }
