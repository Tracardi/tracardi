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
    record = 0
    async for event in storage.driver.event.scan(settings.query):
        record += 1
        print(record, event['id'])
        event = dotty(event)
        try:

            if event['profile'] is None:
                print("no profile")
                continue

            profile_id = event['profile']['id']
            profile = await storage.driver.profile.load_by_id(profile_id)

            if profile is None:
                print("empty profile")
                continue

            profile_meta = profile.get_meta_data()
            print("profile_meta", profile_meta)
            profile = dotty(profile)

            for mapping in mappings:
                try:
                    profile[mapping.profile.value] = event[mapping.event.value]
                    print(mapping.profile.value, "=", mapping.event.value)
                except KeyError as e:
                    print(repr(e))
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
                            message=f"While coping event data from event type {event['type']} to profile, "
                                    f"system could not find data event@{mapping.event.value}. "
                                    f"Data was not copied. Details: {repr(e)}",
                            traceback=get_traceback(e)
                        )
                    )
            profile = Profile(**profile)
            profile.set_meta_data(profile_meta)
            asyncio.create_task(storage.driver.profile.save(profile))

        except Exception as e:
            print(repr(e))
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
