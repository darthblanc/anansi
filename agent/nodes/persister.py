from agent.state import AgentState
from agent.db import persist_results


def persister_node(state: AgentState) -> AgentState:
    persist_results(state)

    return {
        **state,
        "status": "done"
    }