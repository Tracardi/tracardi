import asyncio

from dotty_dict import dotty
from tracardi.exceptions.exception_service import get_traceback

from tracardi.domain.console import Console
from tracardi.service.console_log import ConsoleLog

from tracardi.domain.profile import Profile
from tracardi.domain.storage.event_to_profile_copy_settings import EventToProfileCopySettings
from tracardi.service.storage.driver import storage
from tracardi.service.storage.drivers.elastic.operations.console_log import save_console_log


async def copy_events_to_profiles(settings: EventToProfileCopySettings):
    if not settings.query:
        settings.query = {
            "query": {
                "match_all": {}
            }
        }
    else:
        settings.query = {
            "query": {
                "query_string": {
                    "query": settings.query
                }
            }
        }

    mappings = list(settings.get_mappings())
    console_log = ConsoleLog()
    print(settings.query)
    async for event in storage.driver.event.scan(settings.query):
        print(event)
        event = dotty(event)
        try:
            profile_id = event['profile']['id']
            profile = await storage.driver.profile.load_by_id(profile_id)
            profile = dotty(profile)

            for mapping in mappings:
                try:
                    profile[mapping.profile.value] = event[mapping.event.value]
                except KeyError as e:
                    console_log.append(
                        Console(
                            flow_id=None,
                            node_id=None,
                            event_id=event['id'] if 'id' in event else None,
                            profile_id=profile_id,
                            origin='copy',
                            class_name='copy_events_to_profiles',
                            module=__name__,
                            type='warning',
                            message=f"While coping event data to profile system could not find data "
                                    f"event@{mapping.event.value}. Data was not copied. Details: {repr(e)}",
                            traceback=get_traceback(e)
                        )
                    )

            asyncio.create_task(storage.driver.profile.save(Profile(**profile)))

        except KeyError as e:
            console_log.append(
                Console(
                    flow_id=None,
                    node_id=None,
                    event_id=event['id'] if 'id' in event else None,
                    profile_id=None,
                    origin='destination',
                    class_name='copy_events_to_profiles',
                    module=__name__,
                    type='error',
                    message=repr(e),
                    traceback=get_traceback(e)
                )
            )

    save_console_log(console_log)
