from agent.state import AgentState
from agent.logging_config import get_logger

logger = get_logger(__name__)


def interviewer_node(state: AgentState) -> AgentState:
    answered_questions = []
    logger.info("interviewer — starting quiz with %d question(s)", len(state["questions"]))

    print(f"\nQuiz starting — {len(state['questions'])} questions\n")

    for i, q in enumerate(state["questions"], 1):
        print(f"Q{i}: {q['question']}")
        answer = input("Your answer: ").strip()
        print()
        logger.debug("interviewer — Q%d answered (%d chars)", i, len(answer))

        answered_questions.append({
            **q,
            "user_answer": answer
        })

    logger.info("interviewer — all questions answered")
    return {
        **state,
        "questions": answered_questions,
        "status": "evaluating"
    }
