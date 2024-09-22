import glob
import json
import os
from typing import Optional, Tuple

from dotty_dict import dotty

from tracardi.context import ServerContext, get_context
from tracardi.domain.profile import FlatProfile
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.license import License
from tracardi.service.storage.elastic.interface.event import load_unique_field_value
from tracardi.service.string_manager import capitalize_event_type_id

if License.has_license():
    from com_tracardi.service.traits_update import update_dict_with_conflicts

_local_dir = os.path.dirname(__file__)
_predefined_event_types = {}

logger = get_logger(__name__)


# def call_function(call_string, event: Dotty, profile: Dotty):
#     state = call_string[5:]
#     module, function = state.split(',')
#     module = import_package(module)
#     state_function = load_callable(module, function)
#
#     return state_function(event, profile)


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
        production_event_types = await load_unique_field_value(query, limit)

        for item in production_event_types:
            if item not in pre_defined_ids:
                pre_defined.append((item, capitalize_event_type_id(item)))
                pre_defined_ids.append(item)

    with ServerContext(context.switch_context(production=False)):
        test_event_types = await load_unique_field_value(query, limit)

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


def copy_default_event_to_profile(copy_schema: dict, flat_profile: FlatProfile, flat_event: dotty) -> Tuple[
    FlatProfile, bool]:
    profile_updated_flag = False

    if copy_schema is not None:

        for profile_path, (event_path, operation) in copy_schema.items():  # type: str, Tuple[str, str]

            # Skip none existing event properties.
            if isinstance(event_path, str):
                if event_path in flat_event:
                    profile_updated_flag = True
                    if operation == 'append':

                        # Make sure the value is list
                        if isinstance(flat_event[event_path], (str, int, float)):
                            value_to_be_appended = [flat_event[event_path]]
                        else:
                            value_to_be_appended = flat_event[event_path]

                        # Convert profile property to list if string, int, etc.
                        if not isinstance(flat_profile[profile_path], list):
                            # Must have some value, not None, ""
                            if flat_profile[profile_path]:
                                flat_profile[profile_path] = [flat_profile[profile_path]]

                        if profile_path not in flat_profile or flat_profile[profile_path] is None:
                            flat_profile[profile_path] = _append_value(values=[],
                                                                       value=value_to_be_appended)

                        elif isinstance(flat_profile[profile_path], list):
                            flat_profile[profile_path] = _append_value(values=flat_profile[profile_path],
                                                                       value=value_to_be_appended)
                        else:
                            raise KeyError(
                                f"Can not append data {flat_event[event_path]} to {flat_profile[profile_path]} "
                                f"at profile@{profile_path}. Unexpected type {type(flat_event[event_path])}")

                    elif operation == 'equals_if_not_exists':
                        if profile_path not in flat_profile:
                            flat_profile[profile_path] = flat_event[event_path]
                    elif operation == 'delete':
                        if profile_path in flat_profile:
                            flat_profile[profile_path] = None
                    elif operation == '+':
                        if profile_path in flat_profile:
                            try:
                                if flat_profile[profile_path] is None:
                                    flat_profile[profile_path] = 0
                                flat_profile[profile_path] += float(flat_event[event_path])
                            except Exception:
                                raise AssertionError(
                                    f"Can not add data {flat_event[event_path]} to {flat_profile[profile_path]} "
                                    f"at profile@{profile_path}")
                    elif operation == '-':
                        if profile_path in flat_profile:
                            try:
                                if flat_profile[profile_path] is None:
                                    flat_profile[profile_path] = 0
                                flat_profile[profile_path] = flat_profile[profile_path] - float(flat_event[event_path])
                            except Exception:
                                raise AssertionError(
                                    f"Can not add subtract {flat_event[event_path]} to {flat_profile[profile_path]} "
                                    f"at profile@{profile_path}")
                    elif operation == 'update':
                        # Updates checking if there are ot conflicts

                        profile_data_as_dict = dict(flat_profile[profile_path]) if flat_profile[
                                                                                       profile_path] is not None else {}
                        event_data_as_dict = dict(flat_event[event_path]) if flat_event[event_path] is not None else {}

                        updated_dict, conflicts = update_dict_with_conflicts(profile_data_as_dict, event_data_as_dict,
                                                                             append_lists=False)
                        flat_profile[profile_path] = updated_dict
                        if conflicts:
                            conflicts = {
                                path: {
                                    "new": {
                                        "value": conflict.new_value,
                                        "type": str(conflict.new_type),
                                    },
                                    "old": {
                                        "value": conflict.original_value,
                                        "type": str(conflict.original_type),
                                    }
                                }
                                for path, conflict in conflicts.items()
                            }

                            # Update conflicts

                            try:
                                trash_conflicts = flat_profile['trash']['conflicts']
                            except (KeyError, TypeError):
                                trash_conflicts = {}

                            trash_conflicts.update(conflicts)
                            flat_profile['trash'] = {
                                "conflicts": trash_conflicts
                            }
                    else:
                        # Equal
                        flat_profile[profile_path] = flat_event[event_path]
            elif isinstance(event_path, int) or isinstance(event_path, float):
                if profile_path in flat_profile:
                    if operation in ['increment', 'decrement']:
                        try:
                            if flat_profile[profile_path] is None:
                                flat_profile[profile_path] = 0

                            if operation == 'increment':
                                flat_profile[profile_path] = flat_profile[profile_path] + float(event_path)
                            else:
                                flat_profile[profile_path] = flat_profile[profile_path] - float(event_path)

                            profile_updated_flag = True

                        except Exception:
                            raise AssertionError(
                                f"Can not add increment/decrement {flat_event[event_path]} "
                                f"to {flat_profile[profile_path]} at profile@{profile_path}")

    return flat_profile, profile_updated_flag
