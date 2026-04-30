from typing import TypedDict, Optional, Literal, Annotated
import operator


class QuizQuestion(TypedDict):
    question: str
    question_type: Literal["free", "mcq"]
    options: Optional[list[str]]     # MCQ only — 4 answer strings
    correct_option: Optional[int]    # MCQ only — 0-indexed
    user_answer: str
    score: Optional[float]
    feedback: Optional[str]
    question_index: Optional[int]


class AgentState(TypedDict):
    # Input
    user_prompt: str                        # "quiz me on multi agent systems"

    # Topic selection
    selected_concepts: list[str]            # concept ids from index.json
    loaded_content: dict[str, str]          # concept id → markdown content

    # Planning
    quiz_plan: list[str]                    # outline of questions to generate

    # Quiz
    questions: list[QuizQuestion]           # built up during generation
    current_question_index: int

    # Evaluation
    evaluated_questions: Annotated[list[QuizQuestion], operator.add]
    final_score: Optional[float]            # 0.0 to 1.0

    # Control
    status: Literal[
        "selecting",
        "loading",
        "planning",
        "quizzing",
        "evaluating",
        "persisting",
        "done"
    ]