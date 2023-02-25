from tracardi.domain.event_source import EventSource
from tracardi.service.storage.driver import storage


def event_source_types():
    standard_inbound_sources = {
        "imap": {
            "name": "IMAP Bridge",
            "tags": ["imap", "inbound"]
        },
        "mqtt": {
            "name": "MQTT Bridge",
            "tags": ["mqtt", "inbound"]
        },
        "queue": {
            "name": "Queue Bridge",
            "tags": ["queue", "inbound"]
        },
        "rest": {
            "name": "Rest Api Call",
            "tags": ["rest", "inbound"]
        },
        "redirect": {
            "name": "Redirect Link",
            "tags": ["link", "inbound"]
        },
        "webhook": {
            "name": "Webhook",
            "tags": ["webhook", "inbound"]
        },
        "internal": {
            "name": "Internal",
            "tags": ["internal", "inbound"]
        },
    }

    return standard_inbound_sources


async def save_source(event_source: EventSource):
    types = event_source_types()
    if event_source.is_allowed(types):
        result = await storage.driver.event_source.save(event_source)
        if result is None or result.is_nothing_saved():
            raise OSError("Could not save event source.")
        await storage.driver.event_source.refresh()
        return result
    else:
        raise ValueError(f"Unknown event source types {event_source.type}. Available {types}.")
