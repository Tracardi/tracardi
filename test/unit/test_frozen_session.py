import pytest
from pydantic import ValidationError

from tracardi.context import Context, ServerContext
from tracardi.domain.session import FrozenSession, Session


def test_frozen_session():
    with ServerContext(Context(production=True)):
        session = FrozenSession(**Session.new().model_dump())
        assert session.is_new()
        with pytest.raises(ValidationError):
            session.id = "1"