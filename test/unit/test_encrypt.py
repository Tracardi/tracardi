from tracardi.domain.destination import DestinationConfig
from tracardi.service.secrets import encrypt, decrypt


def test_encrypt_base_model_object():
    # Setup
    base_model = DestinationConfig(package="1",init={}, form={})

    # Exercise
    result = encrypt(base_model)

    # Verify
    assert isinstance(result, str)

    assert decrypt(result) == {'form': {}, 'init': {}, 'package': '1', 'pro': False}