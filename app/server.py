from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.main import build_generation_graph, build_evaluation_graph
from agent.state import AgentState
from app.session import create_session, get_session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    topic: str
    # Users supply their own cloud-provider API keys — the deployed backend
    # never uses its own. Keys are used only for this request/session and
    # are never written to disk, a database, or logs.
    llm_provider: Literal["anthropic", "openai"]
    llm_api_key: str = Field(min_length=1)
    embeddings_provider: Literal["openai"]
    embeddings_api_key: str = Field(min_length=1)


class SubmitRequest(BaseModel):
    session_id: str
    answers: list[str]


@app.post("/api/quiz/start")
async def start_quiz(body: StartRequest):
    initial_state: AgentState = {
        "user_prompt": body.topic,
        "llm_override": {"provider": body.llm_provider, "api_key": body.llm_api_key},
        "embeddings_override": {"provider": body.embeddings_provider, "api_key": body.embeddings_api_key},
        "selected_concepts": [],
        "loaded_content": {},
        "quiz_plan": [],
        "questions": [],
        "current_question_index": 0,
        "evaluated_questions": [],
        "final_score": None,
        "status": "selecting",
    }

    gen_graph = build_generation_graph()
    state = gen_graph.invoke(initial_state, {"max_concurrency": 4})
    session_id = create_session(state)

    questions = [
        {
            "question": q["question"],
            "question_type": q["question_type"],
            "options": q.get("options"),
        }
        for q in state["questions"]
    ]

    return {"session_id": session_id, "questions": questions}


@app.post("/api/quiz/submit")
async def submit_quiz(body: SubmitRequest):
    state = get_session(body.session_id)

    answered = [
        {**q, "user_answer": body.answers[i]}
        for i, q in enumerate(state["questions"])
    ]
    updated_state = {**state, "questions": answered, "status": "evaluating"}

    eval_graph = build_evaluation_graph()
    final_state = eval_graph.invoke(updated_state, {"max_concurrency": 4})

    evaluated = sorted(
        final_state["evaluated_questions"],
        key=lambda q: q["question_index"],
    )

    return {
        "final_score": final_state["final_score"],
        "evaluated": [
            {
                "question": q["question"],
                "question_type": q["question_type"],
                "user_answer": q["user_answer"],
                "score": q["score"],
                "feedback": q["feedback"],
            }
            for q in evaluated
        ],
    }
