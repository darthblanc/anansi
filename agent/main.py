import json
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from agent.state import AgentState
from agent.nodes.selector import selector_node
from agent.tools.file_loader import loader_node
from agent.nodes.planner import planner_node
from agent.nodes.generator import generator_node
from agent.nodes.interviewer import interviewer_node
from agent.nodes.evaluator import evaluate_one_node, collect_node
from agent.nodes.persister import persister_node
from agent.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def _fan_out_evaluations(state: AgentState) -> list[Send]:
    return [
        Send("evaluate_one", {**state, "current_question_index": i})
        for i in range(len(state["questions"]))
    ]


def build_graph():
    graph = StateGraph(AgentState)

    # register nodes
    graph.add_node("selector", selector_node)
    graph.add_node("loader", loader_node)
    graph.add_node("planner", planner_node)
    graph.add_node("generator", generator_node)
    graph.add_node("interviewer", interviewer_node)
    graph.add_node("evaluate_one", evaluate_one_node)
    graph.add_node("collect", collect_node)
    graph.add_node("persister", persister_node)

    # wire edges
    graph.set_entry_point("selector")
    graph.add_edge("selector", "loader")
    graph.add_edge("loader", "planner")
    graph.add_edge("planner", "generator")
    graph.add_edge("generator", "interviewer")
    graph.add_conditional_edges("interviewer", _fan_out_evaluations, ["evaluate_one"])
    graph.add_edge("evaluate_one", "collect")
    graph.add_edge("collect", "persister")
    graph.add_edge("persister", END)

    return graph.compile()


def run_quiz(user_prompt: str):
    logger.info("run_quiz — starting: %r", user_prompt)
    app = build_graph()

    initial_state: AgentState = {
        "user_prompt": user_prompt,
        "selected_concepts": [],
        "loaded_content": {},
        "quiz_plan": [],
        "questions": [],
        "current_question_index": 0,
        "evaluated_questions": [],
        "final_score": None,
        "status": "selecting"
    }

    final_state = app.invoke(initial_state, {"max_concurrency": 4})

    # print results
    print(f"\n{'='*50}")
    print(f"Quiz Complete — Final Score: {final_state['final_score']:.0%}")
    print(f"{'='*50}\n")

    evaluated = sorted(final_state["evaluated_questions"], key=lambda q: q["question_index"])
    for i, q in enumerate(evaluated, 1):
        print(f"Q{i}: {q['question']}")
        print(f"Your answer: {q['user_answer']}")
        print(f"Score: {q['score']:.0%}")
        print(f"Feedback: {q['feedback']}")
        print()

    return final_state


if __name__ == "__main__":
    prompt = input("What would you like to be quizzed on? ")
    run_quiz(prompt)