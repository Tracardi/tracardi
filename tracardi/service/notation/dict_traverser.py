from typing import List, Dict, Union

from dotty_dict import dotty
from .dot_accessor import DotAccessor


class DictTraverser:

    def __init__(self, dot: DotAccessor, include_none=True, **kwargs):
        self.include_none = include_none
        self.dot = dot
        if 'default' in kwargs:
            self.default = kwargs['default']
            self.throw_error = False
        else:
            self.throw_error = True

    def _get_value(self, path):
        if self.throw_error is True:
            return self.dot[path]

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

            value = self._get_value(value)

            if value is None and self.include_none is False:
                continue

            out_dot[f"{path}.{key}"] = value

        result = out_dot.to_dict()
        return result['root'] if 'root' in result else {}
