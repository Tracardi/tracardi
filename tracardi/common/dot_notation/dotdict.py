import copy
import json
from typing import Union
from collections.abc import Mapping, MutableMapping
import dotdict_parser


class DotDict(MutableMapping):
    def __init__(self, dictionary: Union[dict | list]):
        if not isinstance(dictionary, (dict, list)):
            raise TypeError(f"Expected dictionary or list as DotDict. Got {type(dictionary)}.")
        self.root = dictionary

    def _set_reference(self, path, is_leaf_a_list_item: bool):
        data = self.root
        last_item = len(path) - 1
        for item_no, item in enumerate(path):
            if item not in data:
                if last_item == item_no and is_leaf_a_list_item:
                    data[item] = []
                else:
                    data[item] = {}
            data = data[item]
        return data

    def _has_reference(self, keys) -> bool:
        data = self.root
        last = len(keys) - 1
        for pos, key in enumerate(keys):
            if pos == last and isinstance(key, int):
                return len(data) >= key
            elif key not in data:
                return False
            data = data[key]
        return True

    def _reference(self, keys):
        data = self.root
        for key in keys:
            data = data[key]
        return data

    @staticmethod
    def _path_key(keys):
        path = keys[:-1]
        key = keys[-1]
        return path, key

    def get(self, key, *args):
        try:
            keys = dotdict_parser.parse_unified_path(key)
            return self._reference(keys)
        except (ValueError, KeyError) as e:
            if args:
                return args[0]
            raise KeyError(f"Could not get DotDict value for {key}. Default value: {args}. Details: {str(e)}")

    def copy(self):
        return DotDict(self.root.copy())

    def deep_copy(self):
        return DotDict(copy.deepcopy(self.root))

    def to_dict(self) -> dict:
        return self.root

    def to_json(self, default=None, cls=None):
        return json.dumps(self.root, default=default, cls=cls)

    # def __getattr__(self, item) -> 'DotDict':
    #     try:
    #         return DotDict(self.root[item])
    #     except TypeError:
    #         return getattr(self.root, item)

    def __contains__(self, item):
        keys = dotdict_parser.parse_unified_path(item)
        return self._has_reference(keys)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.root[item]
        return self.get(item)

    def __setitem__(self, key, value):
        keys = dotdict_parser.parse_unified_path(key)
        path, key = self._path_key(keys)
        is_leaf_a_list_item = key == ''
        _pointer = self._set_reference(path, is_leaf_a_list_item)
        try:
            if isinstance(value, DotDict):
                value = value.to_dict()
            if is_leaf_a_list_item:
                _pointer.append(value)
            else:
                _pointer[key] = value
        except Exception as e:
            raise KeyError(f"Error at path {path} for key {key}: {str(e)}")

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.root[key]
        else:
            keys = dotdict_parser.parse_unified_path(key)
            path, key = self._path_key(keys)
            data = self._reference(path)
            del data[key]

    def __repr__(self):
        return f'DotDict({self.root})'

    def __str__(self):
        return self.root.__str__()

    def __hash__(self):
        return self.root.__hash__()

    def __len__(self):
        return self.root.__len__()

    def __getstate__(self):
        return self.root

    def __setstate__(self, state):
        self.root = state

    def __iter__(self):
        # Return an iterator over the keys
        return self.root.__iter__()

    def __eq__(self, other):
        if isinstance(other, DotDict):
            return other.to_dict() == self.to_dict()
        elif isinstance(other, dict):
            return other == self.to_dict()
        else:
            return False