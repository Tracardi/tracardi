import re

from dotty_dict import dotty
from pydantic import BaseModel

dot_notation_regex = re.compile(
    r"(?:payload|profile|event|session|flow|memory)@([\[\]0-9a-zA-a_\-\.]+(?<![\.\[])|\.\.\.)")


class NotDotNotation:
    pass


class DotAccessor:

    @staticmethod
    def validate(dot_notation: str):
        return dot_notation_regex.match(dot_notation) is not None

    def _convert(self, data, label):
        if data is None:
            return {}
        elif isinstance(data, dict):
            return dotty(data)
        elif isinstance(data, BaseModel):
            return dotty(data.dict())
        else:
            raise ValueError("Could not convert {} to dict. Expected: None, dict or BaseModel got {}.".format(
                label, type(data)
            ))

    def get_all(self, dot_notation):
        if dot_notation.startswith('flow@...'):
            return self.flow
        elif dot_notation.startswith('profile@...'):
            return self.profile
        elif dot_notation.startswith('session@...'):
            return self.session
        elif dot_notation.startswith('payload@...'):
            return self.payload
        elif dot_notation.startswith('event@...'):
            return self.event

        return None

    def _get_value(self, dot_notation, prefix):
        if dot_notation.startswith(prefix):
            value = dot_notation[len(prefix):]
            try:
                if isinstance(value, str):
                    return self.storage[prefix][value]
                return value
            except KeyError:
                raise KeyError("Invalid dot notation. Could not find value for `{}` in {}...".format(value, prefix))
            except TypeError as e:
                raise KeyError("Invalid dot notation. You are trying to access {} "
                               "when it its value is not a dictionary `{}`.".format(value, str(e)))

        return NotDotNotation()

    def __init__(self, profile=None, session=None, payload=None, event=None, flow=None):
        self.flow = self._convert(flow, 'flow')
        self.event = self._convert(event, 'event')
        self.payload = self._convert(payload, 'payload')
        self.session = self._convert(session, 'session')
        self.profile = self._convert(profile, 'profile')

        self.storage = {
            'profile@': self.profile,
            'event@': self.event,
            'payload@': self.payload,
            'session@': self.session,
            'flow@': self.flow,
        }

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
        else:
            raise ValueError(
                "Invalid dot notation. Accessor not available. " +
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
        else:
            raise ValueError(
                "Invalid dot notation. Accessor not available. " +
                "Please start dotted path with one of the accessors: [profile@, session@, payload@, event@] ")

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
