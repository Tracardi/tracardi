import copy
import json
from typing import Union, List
from collections.abc import MutableMapping
import dotdict_parser


class DotDict(MutableMapping):
    def __init__(self, dictionary: Union[dict | list]):
        if not isinstance(dictionary, (dict, list)):
            raise TypeError(f"Expected dictionary or list as DotDict. Got {type(dictionary)}.")
        self.root = dictionary

    def _set_path_value(self, path, value):
        """
        Walks through `root` (which should be a dict or list at the top level),
        creating intermediate dicts/lists as needed so that each element in `path`
        is valid. The final element of `path` will be set to `value`.
        """
        node = self.root

        for i in range(len(path) - 1):
            key = path[i]
            next_key = path[i + 1]

            if isinstance(key, str):
                # Ensure `node` is a dict if we are using a string key
                if not isinstance(node, dict):
                    raise TypeError(f"Cannot use string key on non-dict: {node}")
                # If key doesn't exist, create either a dict or list based on the next key
                if key not in node:
                    node[key] = [] if isinstance(next_key, int) else {}
                node = node[key]

            elif isinstance(key, int):
                # Ensure `node` is a list if we are using an integer key
                if not isinstance(node, list):
                    raise TypeError(f"Cannot use integer key on non-list: {node}")
                # Expand the list if needed
                while len(node) <= key:
                    node.append(None)
                # If there's nothing at node[key], create either a dict or list for the next step
                if node[key] is None:
                    node[key] = [] if isinstance(next_key, int) else {}
                node = node[key]

            else:
                raise TypeError(f"Keys must be str or int, got {type(key)}")

        # Convert DotDict to dict
        if isinstance(value, DotDict):
            value = value.to_dict()

        # Handle the last key in the path and set `value`
        last_key = path[-1]
        if isinstance(last_key, str):
            if not isinstance(node, dict):
                raise TypeError(f"Cannot assign string-key '{last_key}' to non-dict: {node}")
            node[last_key] = value
        elif isinstance(last_key, int):
            if not isinstance(node, list):
                raise TypeError(f"Cannot assign integer-key '{last_key}' to non-list: {node}")
            while len(node) <= last_key:
                node.append(None)
            node[last_key] = value
        else:
            raise TypeError(f"Keys must be str or int, got {type(last_key)}")

    def _set_reference(self, path, key):
        data = self.root
        print(path)
        for item_no, item in enumerate(path):
            print(item)
            if isinstance(item, int):
                if not isinstance(data, list):
                    data = []
                data[item] = []
                # if not isinstance(data, list) and item == 0:
                #     data = [{}]
                #     data = data[item]
                #     continue
                #
                # if len(data) >= item:
                #     raise ValueError(f"Cannot set value to {item} in {path}. Position {item} out of range. List has only {len(data)} items.")
                # else:
                #     data[item] = {}
            elif isinstance(item, str):
                if item not in data:
                    data[item] = {}
                data = data[item]
            else:
                raise KeyError(f"Only string keys are allowed. Got {item} of type {type(item)}.")
        return data

    def _has_reference(self, keys) -> bool:
        data = self.root
        last = len(keys) - 1
        for pos, key in enumerate(keys):
            if isinstance(key, int):
                # Is int but dat is not list
                if not isinstance(data, list):
                    return False
                # Is last so check number of items
                if pos == last:
                    return len(data) > key
                else:
                    # Not last so check if key not out of range
                    if len(data) <= key:
                        return False

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

    @staticmethod
    def as_list(data: List[dict]) -> List['DotDict']:
        return list(map(DotDict, data))

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
        # path, key = self._path_key(keys)
        self._set_path_value(keys, value)
        # _pointer = self._set_reference(path, key)
        # try:
        #     if isinstance(value, DotDict):
        #         value = value.to_dict()
        #     if isinstance(key, int) and not isinstance(_pointer, list) and key == 0:
        #         _pointer = [value]
        #     elif isinstance(key, (str, int)):
        #         _pointer[key] = value
        # except Exception as e:
        #     raise KeyError(f"Error at path {path} for key {key}: {str(e)}")

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