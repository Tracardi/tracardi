import base64
import json


def b64_encoder(data):
    if data is None:
        data = {}
    json_init = json.dumps(data)
    return base64.b64encode(json_init.encode('utf-8'))


def encrypt(data):
    # This is for future encryptor
    return b64_encoder(data)


def decode_b64(data):
    if data is None:
        return {}
    decoded = base64.b64decode(data)
    return json.loads(decoded)


def decrypt(data):
    # This is for future decryptor
    return decode_b64(data)
