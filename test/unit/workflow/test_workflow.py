import pytest

from tracardi.context import ServerContext, Context
from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.flow import Flow
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.time import Time
from tracardi.process_engine.action.v1.end_action import EndAction
from tracardi.process_engine.action.v1.flow.start.start_action import StartAction
from tracardi.process_engine.action.v1.increase_views_action import IncreaseViewsAction
from tracardi.process_engine.action.v1.operations.update_profile_action import UpdateProfileAction
from tracardi.service.wf.domain.flow_history import FlowHistory
from tracardi.service.wf.domain.work_flow import WorkFlow
from tracardi.service.wf.service.builders import action


def test_build_workflow():
    start = action(StartAction)
    increase_views = action(IncreaseViewsAction)
    update_profile = action(UpdateProfileAction)

    flow = Flow.build("End2End flow", id="1")
    flow += start('payload') >> increase_views('payload')
    flow += increase_views('payload') >> update_profile('payload')

    assert len(flow.flowGraph.edges) == 2
    assert len(flow.flowGraph.nodes) == 3

@pytest.mark.asyncio
async def test_workflow_invoke():
    with ServerContext(Context(production=False)):
        ep = EventPayload(type="111222", properties={})
        tracker_payload = TrackerPayload(
            source=Entity(id="@1"),
            session=None,
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="2"),
            context={},
            request={},
            properties={},
            events=[ep],
            # options={"saveSession": False, 'scheduledFlowId': 'aaabbb', 'scheduledNodeId': "111"}
        )

        workflow = WorkFlow(
            FlowHistory(history=[]),
            tracker_payload=tracker_payload
        )

        # Build flow

        start = action(StartAction)
        increase_views = action(IncreaseViewsAction)
        update_profile = action(UpdateProfileAction)
        end = action(EndAction, {"result": "profile@id"})

        flow = Flow.build("End2End flow", id="1")
        flow += start('payload') >> increase_views('payload')
        flow += increase_views('payload') >> update_profile('payload')
        flow += increase_views('payload') >> end('payload')

        ux = []
        profile = Profile.new()
        session = Session.new()
        event = ep.to_event(
            tracker_payload.metadata,
            tracker_payload.source,
            session,
            profile,
            profile_less=False
        )
        flow_invoke_result = await workflow.invoke(flow, event, profile, session, ux, debug=True)
        assert flow_invoke_result.profile.stats.views == 1
        assert flow_invoke_result.flow.state is None
