import base64
import json
import gzip


def b64_encoder(data):
    if data is None:
        data = {}
    json_init = json.dumps(data)
    gziped = gzip.compress(bytes(json_init, 'utf-8'))
    b64 = base64.b64encode(gziped)
    return b64.decode("utf-8")


def encrypt(data):
    return b64_encoder(data)


def decode_b64(data):
    if data is None:
        return {}
    decoded = base64.b64decode(data)
    try:
        decoded = gzip.decompress(decoded)
    except OSError:
        pass
    finally:
        return json.loads(decoded)


def decrypt(data):
    # This is for future decryptor
    return decode_b64(data)
