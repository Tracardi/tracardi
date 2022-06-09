from tracardi.domain.event_source import EventSource
from tracardi.service.storage.driver import storage


def event_source_types():
    standard_inbound_sources = {
        "mqtt": {
            "name": "Mqtt Subscriber",
            "tags": ["mqtt", "inbound"]
        },
        "rest": {
            "name": "Rest Api Call",
            "tags": ["rest", "inbound"]
        },
    }

    return standard_inbound_sources


async def save_source(event_source: EventSource):
    types = event_source_types()
    if event_source.type in types:
        result = await storage.driver.event_source.save(event_source)
        if result.is_nothing_saved():
            raise OSError("Could not save event source.")
        await storage.driver.event_source.refresh()
        return result
    else:
        raise ValueError("Unknown event source type {}. Available {}.".format(event_source.type, types))
