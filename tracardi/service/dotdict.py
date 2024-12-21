import json
from typing import Union

import dotdict_parser


class DotDict:
    def __init__(self, dictionary: Union[dict|list]):
        self.root = dictionary

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
        keys = dotdict_parser.parse_unified_path(key)
        try:
            return self._reference(keys)
        except ValueError as e:
            if args:
                return args[0]
            raise e

    def set(self, key, value):
        keys = dotdict_parser.parse_unified_path(key)
        path, key = self._path_key(keys)
        _pointer = self._reference(path)
        _pointer[key] = value

    def delete(self, key):
        if isinstance(key, int):
            del self.root[key]
        else:
            keys = dotdict_parser.parse_unified_path(key)
            path, key = self._path_key(keys)
            data = self._reference(path)
            del data[key]

    def copy(self):
        return DotDict(self.root.copy())

    def to_dict(self):
        return self.root

    def to_json(self, default=None):
        return json.dumps(self.root, default=default)

    def __getattr__(self, item) -> 'DotDict':
        try:
            return DotDict(self.root[item])
        except TypeError:
            print(type(self.root))
            return getattr(self.root, item)

    def __contains__(self, item):
        keys = dotdict_parser.parse_unified_path(item)
        path, key = self._path_key(keys)
        data = self._reference(path)
        if isinstance(key, int):
            return len(data) >= key
        return key in data

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.root[item]
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

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
