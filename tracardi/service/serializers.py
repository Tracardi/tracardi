import base64
from typing import Protocol, Any, Tuple

import marshal

import pickle

import importlib

import json

from datetime import datetime
from dateutil import parser
from pydantic import BaseModel

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.protocol.json_serializable import JsonSerializable

preloaded_classes = {
    ("tracardi.domain.payload.tracker_payload", "TrackerPayload"): lambda data: TrackerPayload.model_construct(**data)
}


class SerializerProtocol(Protocol):

    @staticmethod
    def serialize(args, kwargs, context) -> Any:
        pass

    @staticmethod
    def deserialize(payload: Any) -> Tuple[tuple, dict, dict]:
        pass


def _implements_protocol(obj, protocol) -> bool:
    return all(hasattr(obj, method) for method in protocol)


def _create_base_model_object(class_name, module_name, data):
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    obj = cls.model_construct(**data)

    return obj


def _deserialize_object(class_name, module_name, data):
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    obj = cls.deserialize(data)

    return obj


class SerializationObject(str):
    pass


def _data_encoder(obj):
    if isinstance(obj, datetime):
        return f"$$datetime$${obj.isoformat()}"
    elif isinstance(obj, BaseModel):
        return SerializationObject(
            f"$$basemodel$${obj.__class__.__module__}$${obj.__class__.__name__}$${obj.model_dump_json()}")
    elif isinstance(obj, JsonSerializable):
        return f"$$serializable$${obj.__class__.__module__}$${obj.__class__.__name__}$${obj.serialize()}"
    raise TypeError(f"Object of type [{obj.__class__.__name__}] is not JSON serializable. Value: {obj}")


def _deserialize_from_string(value):
    if value.startswith("$$datetime$$"):
        return parser.parse(value[12:])
    elif value.startswith("$$ser"):
        value = value[16:]
        parts = value.split("$$")
        module = parts[0]
        data = "$$".join(parts[2:])
        class_name = parts[1]
        return _deserialize_object(class_name, module, data)
    elif value.startswith("$$basemodel$$"):
        value = value[13:]
        parts = value.split("$$")
        module = parts[0]
        data = "$$".join(parts[2:])
        class_name = parts[1]
        return _create_base_model_object(class_name, module, json.loads(data))

    raise ValueError("Could not deserialize")


def _data_decoder(dict):
    for key, value in dict.items():
        try:
            if isinstance(value, str):
                value = _deserialize_from_string(value)
                dict[key] = value
        except ValueError:
            pass
    return dict


def json_serializer(data) -> str:
    return json.dumps(data, default=_data_encoder)


def json_deserializer(data: str):
    try:
        unserialized = json.loads(data, object_hook=_data_decoder)
        if isinstance(unserialized, str) and unserialized.startswith("$$"):
            return _deserialize_from_string(unserialized)
        return unserialized
    except ValueError:
        return json.loads(data, object_hook=_data_decoder)


def _fast_pickle_data_encoder(obj):
    if isinstance(obj, BaseModel):
        return {
            "__$type__": (obj.__class__.__module__, obj.__class__.__name__),
            "__$data__": obj.model_dump(mode="json", exclude_defaults=True, exclude_unset=True)
        }, 'marshal'  # Data as dict
    return obj, 'pickle'


def _fast_pickle_data_decoder(obj):
    if isinstance(obj, dict) and "__$type__" in obj and '__$data__' in obj:
        module, class_name = obj['__$type__']
        data = obj['__$data__']

        if (module, class_name) in preloaded_classes:
            return preloaded_classes[(module, class_name)](data)

        return _create_base_model_object(class_name, module, data)
    return obj


class PickleSerializer:

    @staticmethod
    def serialize(obj):
        message_bytes = pickle.dumps(obj)
        base64_bytes = base64.b64encode(message_bytes)
        txt = base64_bytes.decode('ascii')
        return txt

    @staticmethod
    def deserialize(txt):
        base64_bytes = txt.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        obj = pickle.loads(message_bytes)
        return obj


class BinaryPickleSerializer:

    @staticmethod
    def serialize(obj):
        return pickle.dumps(obj)

    @staticmethod
    def deserialize(message_bytes):
        return pickle.loads(message_bytes)


class FastPickleSerializer:

    @staticmethod
    def serialize(obj):
        obj, serializer_type = _fast_pickle_data_encoder(obj)

        if serializer_type == 'marshal':
            message_bytes = marshal.dumps(obj)
        elif serializer_type == 'pickle':
            message_bytes = pickle.dumps(obj)
        else:
            raise ValueError(f"Unknown serialisation type {serializer_type}.")

        base64_bytes = base64.b64encode(message_bytes)
        txt = base64_bytes.decode('ascii')
        return f"{serializer_type}$${txt}"

    @staticmethod
    def deserialize(txt: str):

        if txt.startswith('marshal$$'):
            txt = txt[9:]
            serializer_type = 'marshal'
        elif txt.startswith('pickle$$'):
            txt = txt[8:]
            serializer_type = 'pickle'
        else:
            serializer_type = 'pickle'

        base64_bytes = txt.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)

        if serializer_type == 'pickle':
            obj = pickle.loads(message_bytes)
        else:
            obj = marshal.loads(message_bytes)

        return _fast_pickle_data_decoder(obj)
