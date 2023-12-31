from tracardi.domain.identification_point import IdentificationField
from tracardi.domain.ref_value import RefValue
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json, to_model, from_model


def test_from_to_json_array():

    fields = [
        IdentificationField(
            profile_trait=RefValue(ref=True, value="Test Event"),
            event_property=RefValue(ref=True, value="Test Profile"),
        )
    ]

    j = to_json(fields)
    assert isinstance(j, str)
    assert from_json(j, IdentificationField) == fields


def test_from_to_model_array():

    obj = IdentificationField(
            profile_trait=RefValue(ref=True, value="Test Event"),
            event_property=RefValue(ref=True, value="Test Profile"),
        )

    j = from_model(obj)
    assert isinstance(j, dict)
    assert to_model(j, IdentificationField) == obj