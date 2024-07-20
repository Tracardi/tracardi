from deepdiff import DeepDiff
from dotty_dict import dotty


def get_changed_values(old_dict: dict, new_dict: dict) -> dict:
    diff_result = DeepDiff(old_dict, new_dict, ignore_order=True, view="tree", exclude_paths=["root['aliases']"])
    changed_values = dotty()
    for _, diff in diff_result.items():
        for change in diff:
            key = ".".join(change.path(output_format='list'))
            value = change.t2
            changed_values[key] = value

    return changed_values.to_dict()
