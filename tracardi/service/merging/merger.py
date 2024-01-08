from collections import defaultdict

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Any
from deepdiff import DeepDiff
from deepdiff.model import DiffLevel
from dotty_dict import dotty


class MergingStrategy(BaseModel):
    make_lists_uniq: Optional[bool] = True
    no_single_value_list: Optional[bool] = True
    default_string_strategy: Optional[str] = 'override'
    default_number_strategy: Optional[str] = 'add'
    default_object_strategy: Optional[str] = 'override'
    default_list_strategy: Optional[str] = 'append'


class FieldMergingStrategy(BaseModel):
    field: str
    strategy: MergingStrategy


def validate_list_values(values):
    for value in values:
        if not isinstance(value, (str, int, float, bool)):
            raise ValueError("Invalid value in list `{}`".format(values))


def append(base, key, value, strategy: MergingStrategy):
    if base.get(key, None) == value:
        return base

    if not isinstance(base, dict):
        raise ValueError("Could not merge value `{}` and values `{}`".format(
            base,
            {key: value}))

    # Treat tuple and set as list
    if key in base:
        if type(base[key]) in [tuple, set]:
            base[key] = list(base[key])
        if isinstance(base[key], list):
            validate_list_values(base[key])

    if type(value) in [set, tuple]:
        value = list(value)
    if isinstance(value, list):
        validate_list_values(value)

    # Merge

    if key not in base:
        base[key] = value
    else:
        """
        Existing value can be only a list or a simple type
        """

        # Existing value is a list
        if isinstance(base[key], list):
            if strategy.default_list_strategy == 'override':
                base[key] = value
            elif strategy.default_list_strategy == 'append':
                if isinstance(value, list):
                    base[key] += value
                else:
                    base[key].append(value)
            else:
                raise ValueError(f"Unknown merging strategy `{strategy.default_list_strategy}` for list.")
            # Existing value is not a dict and value is a simple value
        elif not isinstance(base[key], dict) and isinstance(value, (str, int, float, bool, list, BaseModel, datetime)):

            # Value types

            if isinstance(value, list):  # Value that we append or override is a list
                if strategy.default_list_strategy == 'override':
                    base[key] = value
                elif strategy.default_list_strategy == 'append':

                    if isinstance(base[key], dict):
                        raise ValueError(f"Can not append data to dictionary.")

                    validate_list_values(values=value)
                    if isinstance(base[key], list):  # The current value is a list
                        base[key] += value
                    elif isinstance(base[key], (str, int, float, bool)):  # the current value is a primitive.
                        base[key] = [base[key]]
                        base[key] += value
                    elif isinstance(base[key], tuple):  # The current value is a list
                        base[key] = list(base[key])  # Convert tuple to list
                        base[key] += value  # Add value
                    else:
                        # Override if we do not know the type
                        base[key] = value

                else:
                    raise ValueError(f"Unknown merging strategy `{strategy.default_object_strategy}` for list.")
            elif isinstance(value, (BaseModel, bool, datetime)):
                if strategy.default_object_strategy == 'override':
                    # BaseModel and bool are not added to a list of values
                    base[key] = value
                else:
                    raise ValueError(f"Unknown merging strategy `{strategy.default_object_strategy}` for object type.")
            elif isinstance(value, (int, float)):
                if strategy.default_number_strategy == 'override':
                    base[key] = value
                elif strategy.default_number_strategy == 'add':
                    # numeric values are added together
                    base[key] += value
                elif strategy.default_number_strategy == 'append':
                    base[key] = [base[key]]
                    base[key].append(value)
                else:
                    raise ValueError(f"Unknown merging strategy {strategy.default_number_strategy} for number type.")
            elif value != base[key]:  # This is STR
                if strategy.default_string_strategy == 'override':
                    base[key] = value
                elif strategy.default_string_strategy == 'append':
                    base[key] = [base[key]]
                    base[key].append(value)
                else:
                    raise ValueError(f"Unknown merging strategy {strategy.default_string_strategy} for sting type.")
        else:
            raise ValueError("Could not merge `{}` with value `{}`".format(base[key], value))

    # make uniq
    if strategy.make_lists_uniq and isinstance(base[key], list):
        base[key] = list(set(base[key]))
        if strategy.no_single_value_list and len(base[key]) == 1:
            base[key] = base[key][0]

    return base


def merge(base: dict, dict_list: List[dict], strategy: MergingStrategy) -> dict:
    base = dict(base)
    for key in set().union(*dict_list):
        for data in dict_list:
            if key in data:
                # Null
                if data[key] is None:
                    continue
                # Simple types
                elif isinstance(data[key], (str, int, float, bool, tuple, list, set, BaseModel, datetime)):
                    append(base, key, data[key], strategy)
                # Dicts
                elif type(data[key]) in [dict]:
                    if key not in base:
                        base[key] = {}
                    base[key] = merge(base[key], [data[key]], strategy)
                # Objects
                elif isinstance(data[key], object):
                    raise ValueError("Object of type `{}: {}` can not be merged with value `{}: {}`".format(
                        key, type(data[key]),
                        key, base[key] if key in base else base))
                else:
                    raise ValueError("Unknown type `{}: {}`".format(key, type(data[key])))

    return base


def list_merge(base: List, new_list: List, strategy: MergingStrategy) -> list:
    if base == new_list:
        return new_list

    result = merge({"__root__": base},
                   [{"__root__": new_list}],
                   strategy)
    return result["__root__"]


def universal_merger(base: Any, delta: any, strategy: MergingStrategy):
    if isinstance(base, dict):
        return merge(base, [delta], strategy)
    elif isinstance(base, list):
        return list_merge(base, delta, strategy)
    else:
        return delta


def get_conflicted_values(old_dict: dict, new_dict: dict) -> dict:
    diff_result = DeepDiff(old_dict, new_dict, ignore_order=True, view="tree")
    changed_values = dotty()
    for change in diff_result.get("type_changes", []):  # type: DiffLevel
        path = [str(item) for item in change.path(output_format='list')]
        key = ".".join(path)
        value = change.t2
        changed_values[key] = value

    return changed_values.to_dict()


def get_changed_values(old_dict: dict, new_dict: dict) -> dict:
    diff_result = DeepDiff(old_dict, new_dict, ignore_order=True, view="tree")
    changed_values = dotty()
    for change in diff_result.get("values_changed", []):  # type: DiffLevel
        path = [str(item) for item in change.path(output_format='list')]
        key = ".".join(path)
        value = change.t2
        changed_values[key] = value

    return changed_values.to_dict()


def get_modifications(old_dict: dotty, new_dict: dotty) -> dict:
    print(old_dict)
    print(new_dict)
    diff_result = DeepDiff(old_dict, new_dict, ignore_order=True, view="tree")
    # print(diff_result)
    modifications = defaultdict(dict)
    for type, changes in diff_result.items():
        for change in changes:
            path = [str(item) for item in change.path(output_format='list') if item != '_data']
            key = ".".join(path)

            modifications[type][key] = {
                "before": old_dict.get(key),
                "after": new_dict.get(key),
                "ch": (change.t1, change.t2)
            }

    return dict(modifications)


def get_added_values(old_dict: dict, new_dict: dict) -> dict:
    diff_result = DeepDiff(old_dict, new_dict, ignore_order=True, view="tree")
    changed_values = dotty()
    for change in diff_result.get("dictionary_item_added", []):  # type: DiffLevel
        path = [str(item) for item in change.path(output_format='list')]
        key = ".".join(path)
        value = change.t2
        changed_values[key] = value

    return changed_values.to_dict()
