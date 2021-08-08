import base64
import json
import gzip


def b64_encoder(data):
    json_init = json.dumps(data, default=str)
    gziped = gzip.compress(bytes(json_init, 'utf-8'))
    b64 = base64.b64encode(gziped)
    return b64.decode("utf-8")


def encrypt(data):
    return b64_encoder(data)


def b64_decoder(data):
    if data is None:
        return None
    decoded = base64.b64decode(data)
    try:
        decoded = gzip.decompress(decoded)
    except OSError:
        pass
    finally:
        return json.loads(decoded)


def decrypt(data):
    # This is for future decryptor
    return b64_decoder(data)
