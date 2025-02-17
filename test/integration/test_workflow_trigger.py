import pytest
from unittest.mock import patch, AsyncMock

from tracardi.domain.flat_session import FlatSession
from tracardi.service.wf.triggers import _run_workflows
from tracardi.context import ServerContext, Context
from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.event import Event
from tracardi.domain.event_metadata import EventPayloadMetadata, EventMetadata
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.rule import Rule
from tracardi.domain.time import Time, EventTime


@pytest.mark.asyncio
async def test_workflow_trigger():
    with ServerContext(Context(production=False)):
        profile = Profile.new()
        flat_session = FlatSession.new()
        source = Entity(id="@1")
        events = [Event(id="1", name="PageView", type="page-view", properties={},
                        metadata=EventMetadata(time=EventTime()),
                        source=source)]

        tp = TrackerPayload(
            source=source,
            session=Entity(id=flat_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id=profile.id),
            context={},
            request={},
            properties={},
            events=[EventPayload(type=event.type, properties=event.properties) for event in events],
            options={"saveSession": False}
        )

        with patch('tracardi.service.wf.triggers.workflow_trigger_dao.load_rule',
                   new_callable=AsyncMock,
                   return_value=[
                       Rule(flow=NamedEntity(id="w1", name="wf1"), id='r1', name='rule1')
                   ]) as mock_load_rule:
            'tracardi.service.wf.workflow_manager_async.invoke'
            result = await _run_workflows(tp, profile, flat_session, events)
            assert isinstance(result.flat_session, FlatSession)
            assert mock_load_rule.call_count == 1
