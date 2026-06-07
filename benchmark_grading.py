"""Benchmark: sequential vs parallel grading (re-creating the lost LangSmith comparison).

Builds a fixed set of free-text questions and runs the evaluation graph
twice — once with max_concurrency=1 (sequential) and once with
max_concurrency=4 (parallel, matching agent/main.py) — timing each run
to show the speedup from fanning grading out via LangGraph's Send.
"""
import copy
import time

from agent.main import build_evaluation_graph
from agent.state import AgentState
from agent.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

LOADED_CONTENT = {
    "rag-overview": (
        "# Retrieval Augmented Generation\n"
        "RAG combines a retriever, which fetches relevant documents from an external "
        "knowledge source, with a generator, typically a large language model, which "
        "produces an answer conditioned on both the user query and the retrieved "
        "documents. This grounds the model's output in source material and reduces "
        "hallucination compared to relying on the model's parametric memory alone."
    ),
    "rag-pipeline": (
        "# RAG Pipeline Stages\n"
        "A typical RAG pipeline has three stages: indexing, where documents are split "
        "into chunks and embedded into a vector store; retrieval, where the user's "
        "query is embedded and the most similar chunks are fetched; and generation, "
        "where the LLM produces a response using the retrieved chunks as context."
    ),
}

QUESTIONS = [
    {
        "question": "What two components does a RAG system combine, and what does each do?",
        "user_answer": "A retriever that fetches relevant documents and a generator (an LLM) that writes an answer using those documents as context.",
    },
    {
        "question": "Why does grounding generation in retrieved documents reduce hallucination?",
        "user_answer": "Because the model bases its answer on real source material instead of only on what it memorized during training, so it's less likely to invent facts.",
    },
    {
        "question": "Name the three stages of a typical RAG pipeline.",
        "user_answer": "Indexing, retrieval, and generation.",
    },
    {
        "question": "What happens during the indexing stage of a RAG pipeline?",
        "user_answer": "Documents get split into smaller chunks and each chunk is turned into an embedding that's stored in a vector database.",
    },
    {
        "question": "How does the retrieval stage decide which chunks to return?",
        "user_answer": "It embeds the user's query and finds the chunks whose embeddings are most similar to the query embedding.",
    },
    {
        "question": "What is the role of the generator in a RAG system?",
        "user_answer": "It produces the final response by conditioning on the user's query together with the documents the retriever found.",
    },
    {
        "question": "How does RAG differ from relying purely on an LLM's parametric memory?",
        "user_answer": "RAG pulls in fresh, relevant information from an external source at query time, rather than depending only on facts baked into the model's weights during training.",
    },
    {
        "question": "Why might splitting documents into chunks before embedding them be necessary?",
        "user_answer": "Whole documents can be too large to embed or fit in context, so chunking keeps each piece small enough to embed accurately and to retrieve at a useful granularity.",
    },
]


def _build_initial_state() -> AgentState:
    return {
        "user_prompt": "quiz me on retrieval augmented generation",
        "selected_concepts": list(LOADED_CONTENT.keys()),
        "loaded_content": dict(LOADED_CONTENT),
        "quiz_plan": [],
        "questions": [
            {
                "question": q["question"],
                "question_type": "free",
                "options": None,
                "correct_option": None,
                "user_answer": q["user_answer"],
                "score": None,
                "feedback": None,
                "question_index": i,
            }
            for i, q in enumerate(QUESTIONS)
        ],
        "current_question_index": 0,
        "evaluated_questions": [],
        "final_score": None,
        "status": "evaluating",
    }


def _run(label: str, max_concurrency: int) -> float:
    state = copy.deepcopy(_build_initial_state())
    eval_graph = build_evaluation_graph()

    logger.info("benchmark — running %s (max_concurrency=%d)", label, max_concurrency)
    start = time.perf_counter()
    final_state = eval_graph.invoke(state, {"max_concurrency": max_concurrency})
    elapsed = time.perf_counter() - start

    n = len(final_state["evaluated_questions"])
    logger.info(
        "benchmark — %s done: %d question(s) in %.2fs (%.2fs/question avg)",
        label, n, elapsed, elapsed / n,
    )
    return elapsed


def main():
    n = len(QUESTIONS)

    sequential = _run("sequential", max_concurrency=1)
    parallel = _run("parallel", max_concurrency=4)

    print(f"\n{'='*50}")
    print("Grading benchmark — sequential vs parallel")
    print(f"{'='*50}")
    print(f"Questions graded:        {n}")
    print(f"Sequential (concurrency=1): {sequential:.2f}s  ({sequential / n:.2f}s/question)")
    print(f"Parallel   (concurrency=4): {parallel:.2f}s  ({parallel / n:.2f}s/question)")
    print(f"Speedup:                 {sequential / parallel:.2f}x")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
