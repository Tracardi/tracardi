from tracardi.domain.ref_value import RefValue


def test_ref_value_empty():

    v = RefValue(value="", ref=True)
    assert not v.has_value()

    v = RefValue(value="", ref=False)
    assert not v.has_value()

    v = RefValue(value="   ", ref=False)
    assert not v.has_value()

    v = RefValue(value=None, ref=False)
    assert not v.has_value()

    v = RefValue(value="None", ref=False)
    assert v.has_value()

    v = RefValue(value="  None  ", ref=False)
    assert v.has_value()

