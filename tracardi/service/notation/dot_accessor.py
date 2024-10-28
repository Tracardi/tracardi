import re
from typing import Union

from dotty_dict import dotty, Dotty
from pydantic import BaseModel

dot_notation_regex = re.compile(
    r"(?:payload|profile|event|session|flow|memory)@([\[\]0-9a-zA-a_\-\.]+(?<![\.\[])|\.\.\.)")


class NotDotNotation:
    pass


class DotAccessor:

    @staticmethod
    def validate(dot_notation: str) -> bool:
        return dot_notation_regex.match(dot_notation) is not None

    def _convert(self, data, label):
        if data is None:
            return {}
        elif isinstance(data, dict):
            return dotty(data)
        elif isinstance(data, BaseModel):
            return dotty(data.model_dump(mode="json"))
        elif isinstance(data, Dotty):
            return data
        else:
            raise ValueError("Could not convert {} to dict. Expected: None, dict or BaseModel got {}.".format(
                label, type(data)
            ))

    def convert_to_dict(self, object: Union[dict, dotty]) -> dict:
        if isinstance(object, dict):
            return object

        return object.to_dict()

    def get_all(self, dot_notation):
        if dot_notation.startswith('flow@...'):
            return self.convert_to_dict(self.flow)
        elif dot_notation.startswith('profile@...'):
            return self.convert_to_dict(self.profile)
        elif dot_notation.startswith('session@...'):
            return self.convert_to_dict(self.session)
        elif dot_notation.startswith('payload@...'):
            return self.convert_to_dict(self.payload)
        elif dot_notation.startswith('event@...'):
            return self.convert_to_dict(self.event)
        elif dot_notation.startswith('memory@...'):
            return self.convert_to_dict(self.memory)

        return None

    def _get_value(self, dot_notation, prefix):
        if dot_notation.startswith(prefix):
            value = dot_notation[len(prefix):]
            try:
                if isinstance(value, str):
                    if value in self.storage[prefix]:
                        return self.storage[prefix][value]
                    else:
                        raise KeyError(f"Invalid data reference. Dot notation `{prefix}{value}` could not find data. ")
                return value
            except TypeError as e:
                raise KeyError(f"Invalid dot notation. You are trying to access {value} "
                               f"when it its value is not a dictionary. Details: `{str(e)}`.")

        return NotDotNotation()

    def __init__(self, profile=None, session=None, payload=None, event=None, flow=None, memory=None):
        self.flow = self._convert(flow, 'flow')
        self.event = self._convert(event, 'event')
        self.payload = self._convert(payload, 'payload')
        self.session = self._convert(session, 'session')
        self.profile = self._convert(profile, 'profile')
        self.memory = self._convert(memory, 'memory')

        self.storage = {
            'profile@': self.profile,
            'event@': self.event,
            'payload@': self.payload,
            'session@': self.session,
            'flow@': self.flow,
            'memory@': self.memory,
        }

    def set_storage(self, name, data):

        storage = f"{name}@"
        if storage not in self.storage.keys():
            raise ValueError("Unknown storage")

        if name == 'profile':
            self.profile = data
        elif name == 'event':
            self.event = data
        elif name == 'session':
            self.session = data
        elif name == 'flow':
            self.flow = data
        elif name == 'payload':
            self.payload = data
        elif name == 'memory':
            self.memory = data

        self.storage[storage] = self._convert(data, name)

        if name == 'profile':
            self.profile = self.storage[storage]
        elif name == 'event':
            self.event = self.storage[storage]
        elif name == 'session':
            self.session = self.storage[storage]
        elif name == 'flow':
            self.flow = self.storage[storage]
        elif name == 'payload':
            self.payload = self.storage[storage]
        elif name == 'memory':
            self.memory = self.storage[storage]

    @staticmethod
    def source(key):
        if key.startswith('profile@'):
            return 'profile'
        elif key.startswith('session@'):
            return 'session'
        elif key.startswith('flow@'):
            return 'flow'
        elif key.startswith('payload@'):
            return 'payload'
        elif key.startswith('event@'):
            return 'event'
        elif key.startswith('memory@'):
            return 'memory'

        return None

    def __delitem__(self, key):
        if key.startswith('profile@'):
            key = key[len('profile@'):]
            del self.profile[key]
        elif key.startswith('session@'):
            key = key[len('session@'):]
            del self.session[key]
        elif key.startswith('flow@'):
            raise KeyError("Could not set flow, flow is read only")
        elif key.startswith('payload@'):
            key = key[len('payload@'):]
            del self.payload[key]
        elif key.startswith('event@'):
            key = key[len('event@'):]
            del self.event[key]
        elif key.startswith('memory@'):
            key = key[len('memory@'):]
            del self.memory[key]
        else:
            try:
                _source, _value = key.split('@')
            except Exception:
                _source = 'unknown'
                _value = 'unknown'
            raise ValueError(
                f"Invalid data reference. Dot notation `{key}` could not access data. The reason for this may be that "
                f"there is no data in {_source} at `{_value}`. " +
                "Please start dotted path with one of the accessors: [profile@, session@, payload@, event@] ")

    def __setitem__(self, key, value):
        if key.startswith('profile@'):
            key = key[len('profile@'):]
            self.profile[key] = self.__getitem__(value) if not isinstance(value, dict) else value
        elif key.startswith('session@'):
            key = key[len('session@'):]
            self.session[key] = self.__getitem__(value) if not isinstance(value, dict) else value
        elif key.startswith('flow@'):
            raise KeyError("Could not set flow, flow is read only")
        elif key.startswith('payload@'):
            key = key[len('payload@'):]
            self.payload[key] = self.__getitem__(value) if not isinstance(value, dict) else value
        elif key.startswith('event@'):
            key = key[len('event@'):]
            self.event[key] = self.__getitem__(value) if not isinstance(value, dict) else value
        elif key.startswith('memory@'):
            key = key[len('memory@'):]
            self.memory[key] = self.__getitem__(value) if not isinstance(value, dict) else value
        else:
            raise ValueError(
                "Invalid dot notation. Source not available. " +
                "Please start dotted path with one of the sources: [profile@, session@, payload@, event@] ")

    def __getitem__(self, dot_notation):
        cast = False

        if isinstance(dot_notation, str):

            if dot_notation.startswith("`") and dot_notation.endswith("`"):
                dot_notation = dot_notation.strip("`")
                cast = True

            all_data = self.get_all(dot_notation)

            if all_data is not None:
                return all_data

            for prefix in self.storage.keys():
                value = self._get_value(dot_notation, prefix)
                if not isinstance(value, NotDotNotation):
                    if value is None:
                        return None
                    return self.cast(value) if cast else value

        return self.cast(dot_notation) if cast else dot_notation

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except (KeyError, TypeError):
            return False

    @staticmethod
    def get(dot_notation, payload, prefix):
        value = dot_notation[len(prefix + '@'):]
        try:
            return payload[value]
        except KeyError:
            raise KeyError("Could not find value for `{}` in {}".format(value, prefix))

    @staticmethod
    def set(key, value, payload, prefix):
        key = key[len(prefix + '@'):]
        payload[key] = value

    @classmethod
    def cast(cls, value):
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            elif value.lower() in ["null", "none"]:
                return None
            elif value.replace(".", "").isnumeric() and value.count(".") == 1:
                try:
                    return float(value)
                except ValueError:
                    return value
            elif value.isnumeric():
                try:
                    return int(value)
                except ValueError:
                    return value
        return value
