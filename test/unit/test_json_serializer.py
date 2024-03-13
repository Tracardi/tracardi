import json

from datetime import datetime
from tracardi.service.serializers import json_serializer, json_deserializer
from tracardi.service.wf.domain.entity import Entity


class Serial:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def serialize(self):
        return json.dumps({"a": self.a, "b": self.b})

    @staticmethod
    def deserialize(data):
        data = json.loads(data)
        return Serial(**data)


def test_serialize_deserialize():
    now = datetime.utcnow()

    # Arrange
    data = {"key1": "value1", "key2": now}

    # Act
    result = json_serializer(data)

    # Assert
    assert isinstance(result, str)
    deserialized = json_deserializer(result)
    assert deserialized == data


def test_serialize_deserialize_base_object():
    obj = Entity(id="1")

    # Arrange
    data = obj

    # Act
    result = json_serializer(data)

    # Assert
    assert isinstance(result, str)
    deserialized = json_deserializer(result)
    assert deserialized == data


def test_serialize_deserialize_object():
    obj = Serial(1,2)

    result = json_serializer(obj)
    # Assert
    assert isinstance(result, str)
    deserialized = json_deserializer(result)
    assert isinstance(deserialized, Serial)

    assert deserialized.a == 1
    assert deserialized.b == 2
