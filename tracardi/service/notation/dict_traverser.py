from typing import List, Dict, Union

from dotty_dict import Dotty
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
        self.separator = "\u221E"

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
        if key is None and isinstance(value, list) and len(value) == 0:
            raise ValueError("Can not traverse empty list.")

        if isinstance(value, dict):
            for k, v in value.items():
                yield from self.traverse(v, k, path + self.separator + k)
        elif isinstance(value, list):
            # Return empty lists as they are.
            if not value:
                yield key, [], path
            for n, v in enumerate(value):
                k = str(n)
                yield from self.traverse(v, k, path + self.separator + k)
        else:
            yield key, value, path

    def reshape(self, reshape_template: Union[Dict, List, str]):

        if reshape_template is None:
            return None

        if isinstance(reshape_template, str):
            return self.dot[reshape_template]

        if not isinstance(reshape_template, dict) and not isinstance(reshape_template, list):
            raise ValueError("Reshape template is not object or list.")

        if isinstance(reshape_template, list) and len(reshape_template) == 0:
            return []

        out_dot = Dotty({}, self.separator, esc_char='\\', no_list=False)
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

            in_key = f"{path}{self.separator}{key}"
            if not value:
                if not optional:
                    out_dot[in_key] = value
            else:
                out_dot[in_key] = value

        result = out_dot.to_dict()
        return result['root'] if 'root' in result else {}
