import pytest

from app import session


@pytest.fixture(autouse=True)
def clear_sessions():
    session._sessions.clear()
    yield
    session._sessions.clear()


def test_create_session_stores_state_and_returns_id(make_state):
    state = make_state()

    sid = session.create_session(state)

    assert isinstance(sid, str)
    assert session.get_session(sid) == state


def test_create_session_returns_unique_ids(make_state):
    sid1 = session.create_session(make_state())
    sid2 = session.create_session(make_state())

    assert sid1 != sid2


def test_get_session_raises_for_unknown_id():
    with pytest.raises(KeyError):
        session.get_session("does-not-exist")
