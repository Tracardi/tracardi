from hashlib import sha1


class SHA1Encoder:

    @classmethod
    def encode(cls, data: str):
        return sha1(("6qO.IwmWg=#..R7/zICi" + data).encode()).hexdigest()
