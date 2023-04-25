from tracardi.service.fake_data_maker.generate_payload import generate_payload


def test_fake_data_schema():
    payload = generate_payload("111")
    assert 'source' in payload
    assert 'profile' in payload
