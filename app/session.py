from uuid import uuid4
from agent.state import AgentState

# In-memory only — sessions may carry live user-supplied API keys via
# AgentState's llm_override/embeddings_override fields. Never back this with
# persistent storage (disk, DB, cache) without first stripping those fields.
_sessions: dict[str, AgentState] = {}


def create_session(state: AgentState) -> str:
    sid = str(uuid4())
    _sessions[sid] = state
    return sid


def get_session(session_id: str) -> AgentState:
    return _sessions[session_id]
