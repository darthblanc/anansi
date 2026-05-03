from uuid import uuid4
from agent.state import AgentState

_sessions: dict[str, AgentState] = {}


def create_session(state: AgentState) -> str:
    sid = str(uuid4())
    _sessions[sid] = state
    return sid


def get_session(session_id: str) -> AgentState:
    return _sessions[session_id]
