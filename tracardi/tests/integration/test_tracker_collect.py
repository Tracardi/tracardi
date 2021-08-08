import pytest

from tracardi.domain.entity import Entity
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload


@pytest.mark.asyncio
async def test_tracker_collect():

    source = Entity(id="scope")
    await source.storage("source").save({})

    session = Entity.new()
    profile = Entity.new()

    tracker_payload = TrackerPayload(
        session=session,
        profile=profile,
        source=source,
        events=[
            EventPayload(
                type="click",
                properties={"btn": [1, 2, 3]},
                options={"save": False}
            ),
            EventPayload(
                type="click",
                properties={"btn": [3, 4, 5]},
                options={"save": True}
            )
        ]
    )

    profile, session, events, result = await tracker_payload.collect()

    # assert profile.id == result.profile.ids[0]
    assert session.id == result.session.ids[0]

    assert result.session.saved == 1
    # assert result.profile.saved == 1
    assert result.events.saved == 1  # Only one event is marked to saved

    for id in result.events.ids:
        entity = Entity(id=id)
        await entity.storage("event").delete()

    # for id in result.profile.ids:
    #     entity = Entity(id=id)
    #     await entity.storage("profile").delete()

    for id in result.session.ids:
        entity = Entity(id=id)
        await entity.storage("session").delete()



