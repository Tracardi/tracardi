from typing import List, Dict, Union

from dotty_dict import dotty
from .dot_accessor import DotAccessor
import datetime


class DictTraverser:

    def __init__(self, dot: DotAccessor, include_none=True, **kwargs):
        self.include_none = include_none
        self.dot = dot
        if 'default' in kwargs:
            self.default = kwargs['default']
            self.throw_error = False
        else:
            self.throw_error = True

    def _get_value(self, path, optional):
        if self.throw_error is True:
            try:
                return self.dot[path]
            except KeyError as e:
                if optional is True:
                    return None
                raise e
        try:
            value = self.dot[path]
        except KeyError:
            value = self.default

        return value

    def traverse(self, value, key=None, path="root"):
        if isinstance(value, dict):
            for k, v in value.items():
                yield from self.traverse(v, k, path + "." + k)
        elif isinstance(value, list):
            for n, v in enumerate(value):
                k = str(n)
                yield from self.traverse(v, k, path + '.' + k)
        else:
            yield key, value, path

    def reshape(self, reshape_template: Union[Dict, List]):
        out_dot = dotty()
        for key, value, path in self.traverse(reshape_template):

            if key is not None:
                path = path[:-len(key)-1]

            optional = False
            if len(key) > 0 and key[-1] == '?':
                key = key[:-1]
                optional = True

            if len(path) > 0 and path[-1] == '?':
                path = path[:-1]
                optional = True

            value = self._get_value(value, optional)

            if value is None and self.include_none is False:
                continue

            if not value:
                if not optional:
                    out_dot[f"{path}.{key}"] = value
            else:
                out_dot[f"{path}.{key}"] = value

        # TODO THIS DOES NOT SUPPORT DATETIME
        result = out_dot.to_dict()
        return result['root'] if 'root' in result else {}
