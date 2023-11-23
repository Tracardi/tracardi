from tracardi.domain.identification_point import IdentificationField
from tracardi.domain.ref_value import RefValue
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json


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