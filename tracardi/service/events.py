import glob
import json
import logging
import os
from typing import Optional, Tuple, Union

from dotty_dict import dotty

from tracardi.config import tracardi
from tracardi.context import ServerContext, get_context
from tracardi.domain.event import Event, Tags
from tracardi.domain.profile import Profile
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.change_monitoring.field_change_monitor import FieldChangeMonitor
from tracardi.service.module_loader import load_callable, import_package
from tracardi.service.storage.driver.elastic import event as event_db
from tracardi.service.string_manager import capitalize_event_type_id

_local_dir = os.path.dirname(__file__)
_predefined_event_types = {}

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def call_function(call_string, event: Event, profile: Union[Profile, dict]):
    state = call_string[5:]
    module, function = state.split(',')
    module = import_package(module)
    state_function = load_callable(module, function)

    return state_function(event, profile)


def cache_predefined_event_types():
    if not _predefined_event_types:
        path = os.path.join(f"{_local_dir}/setup/events/*.json")
        for file_path in glob.glob(path):
            with open(file_path, "r") as file:
                try:
                    content = json.load(file)
                    for item in content:
                        _predefined_event_types[item['id']] = item
                except Exception as e:
                    raise ValueError(f"Could not decode JSON for file {file_path}. Error: {repr(e)}")


def get_predefined_event_types():
    if not _predefined_event_types:
        cache_predefined_event_types()

    return _predefined_event_types.items()


def get_event_type_names():
    if not _predefined_event_types:
        cache_predefined_event_types()

    for _, event_def in _predefined_event_types.items():
        yield event_def['id'], event_def['name']


async def get_event_types(query: str = None, limit: int = 1000):
    pre_defined = list(get_event_type_names())
    pre_defined_ids = [item[0] for item in pre_defined]

    context = get_context()

    with ServerContext(context.switch_context(production=True)):
        production_event_types = await event_db.unique_field_value(query, limit)

        for item in production_event_types:
            if item not in pre_defined_ids:
                pre_defined.append((item, capitalize_event_type_id(item)))
                pre_defined_ids.append(item)

    with ServerContext(context.switch_context(production=False)):
        test_event_types = await event_db.unique_field_value(query, limit)

        for item in test_event_types:
            if item not in pre_defined_ids:
                pre_defined.append((item, capitalize_event_type_id(item)))

    events_types = [{"id": item[0], "name": item[1]} for item in sorted(pre_defined)]
    return {
        "total": len(events_types),
        "result": events_types
    }


def get_default_mappings_for(event_type, type) -> Optional[dict]:
    if not _predefined_event_types:
        cache_predefined_event_types()

    schema = _predefined_event_types.get(event_type, None)

    if schema is None:
        return None

    return schema.get(type, None)


def get_default_event_type_schema(event_type) -> Optional[dict]:
    if event_type not in _predefined_event_types:
        cache_predefined_event_types()

    schema = _predefined_event_types.get(event_type, None)
    return schema


def _append_value(values, value):
    # Append list to list
    if isinstance(values, list):
        values += value
        # make it unique
        values = list(set(values))
    else:
        # Add value if not exists
        if value not in values:
            values.append(value)

    return values


def copy_default_event_to_profile(copy_schema: dict, profile_changes: FieldChangeMonitor, flat_event: dotty) -> Tuple[FieldChangeMonitor, bool]:
    profile_updated_flag = False
    _flat_profile = profile_changes.flat_profile

    if copy_schema is not None:

        for profile_path, (event_path, operation) in copy_schema.items():  # type: str, Tuple[str, str]

            # Skip none existing event properties.
            if isinstance(event_path, str):
                if event_path in flat_event:
                    profile_updated_flag = True
                    if operation == 'append':
                        if profile_path not in profile_changes or profile_changes[profile_path] is None:
                            profile_changes[profile_path] = _append_value(values=[],
                                                                          value=flat_event[event_path])
                        elif isinstance(profile_changes[profile_path], list):
                            profile_changes[profile_path] = _append_value(values=profile_changes[profile_path],
                                                                          value=flat_event[event_path])
                        elif not isinstance(profile_changes[profile_path], dict):
                            # data in profile exists but is not dict, list. It can be a string ot int.

                            _data = [profile_changes[profile_path], flat_event[event_path]]

                            profile_changes[profile_path] = _data
                        else:
                            raise KeyError(
                                f"Can not append data {flat_event[event_path]} to {profile_changes[profile_path]} "
                                f"at profile@{profile_path}")

                    elif operation == 'equals_if_not_exists':
                        if profile_path not in profile_changes:
                            profile_changes[profile_path] = flat_event[event_path]
                    elif operation == 'delete':
                        if profile_path in profile_changes:
                            profile_changes[profile_path] = None
                    elif operation == '+':
                        if profile_path in profile_changes:
                            try:
                                if profile_changes[profile_path] is None:
                                    profile_changes[profile_path] = 0
                                profile_changes[profile_path] += float(flat_event[event_path])
                            except Exception:
                                raise AssertionError(
                                    f"Can not add data {flat_event[event_path]} to {profile_changes[profile_path]} "
                                    f"at profile@{profile_path}")
                    elif operation == '-':
                        if profile_path in profile_changes:
                            try:
                                if profile_changes[profile_path] is None:
                                    profile_changes[profile_path] = 0
                                profile_changes[profile_path] = profile_changes[profile_path] - float(flat_event[event_path])
                            except Exception:
                                raise AssertionError(
                                    f"Can not add subtract {flat_event[event_path]} to {profile_changes[profile_path]} "
                                    f"at profile@{profile_path}")

                    else:
                        profile_changes[profile_path] = flat_event[event_path]
            elif isinstance(event_path, int) or isinstance(event_path, float):
                if profile_path in profile_changes:
                    if operation in ['increment', 'decrement']:
                        try:
                            if profile_changes[profile_path] is None:
                                profile_changes[profile_path] = 0

                            if operation == 'increment':
                                profile_changes[profile_path] = profile_changes[profile_path] + float(event_path)
                            else:
                                profile_changes[profile_path] = profile_changes[profile_path] - float(event_path)

                            profile_updated_flag = True

                        except Exception:
                            raise AssertionError(
                                f"Can not add increment/decrement {flat_event[event_path]} "
                                f"to {profile_changes[profile_path]} at profile@{profile_path}")

    return profile_changes, profile_updated_flag


def remove_empty_dicts(dictionary):
    keys_to_remove = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            remove_empty_dicts(value)  # Recursively check nested dictionaries
            if not value:  # Empty dictionary after recursive check
                keys_to_remove.append(key)
    for key in keys_to_remove:
        del dictionary[key]


def auto_index_default_event_type(event: Event, profile: Profile) -> Event:
    index_schema = get_default_mappings_for(event.type, 'copy')

    if index_schema is not None:

        flat_event = dotty(event.model_dump())

        for destination, source in index_schema.items():  # type: str, str
            try:

                # if destination not in flat_event:
                #     logger.warning(f"While indexing type {event.type}. "
                #                    f"Property destination {destination} could not be found in event schema.")

                # Skip none existing event properties.
                if source in flat_event:
                    flat_event[destination] = flat_event[source]
                    del flat_event[source]
            except KeyError:
                pass

        event_dict = flat_event.to_dict()
        remove_empty_dicts(event_dict)
        event = Event(**event_dict)

        state = get_default_mappings_for(event.type, 'state')

        if state:
            if isinstance(state, str):
                if state.startswith("call:"):
                    event.journey.state = call_function(call_string=state, event=event, profile=profile)
                else:
                    event.journey.state = state

        tags = get_default_mappings_for(event.type, 'tags')
        if tags:
            event.tags = Tags(values=tuple(tags), count=len(tags))

    return event
