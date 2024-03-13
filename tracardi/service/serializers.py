import base64

import pickle

import importlib

import json

from datetime import datetime
from dateutil import parser
from pydantic import BaseModel

from tracardi.protocol.json_serializable import JsonSerializable


def _implements_protocol(obj, protocol) -> bool:
    return all(hasattr(obj, method) for method in protocol)

def _create_base_model_object(class_name, module_name, data):
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    obj = cls(**data)

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
        return SerializationObject(f"$$basemodel$${obj.__class__.__module__}$${obj.__class__.__name__}$${obj.model_dump_json()}")
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


def pickle_serializer(obj):
    message_bytes = pickle.dumps(obj)
    base64_bytes = base64.b64encode(message_bytes)
    txt = base64_bytes.decode('ascii')
    return txt

def pickle_deserializer(txt):
    base64_bytes = txt.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    obj = pickle.loads(message_bytes)
    return obj