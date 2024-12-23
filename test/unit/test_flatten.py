import dotdict_parser

def test_flatten():
    d = {
        "a": {
            "b": {
                "c": [1]
            },
            "d": None,
            "e": {}
        }
    }
    assert dotdict_parser.flatten(d) == {'a.b.c': [1], 'a.d': None, "a.e": {}}
    # Mutable
    assert d == {
        "a": {
            "b": {
                "c": [1]
            },
            "d": None,
            "e": {}
        }
    }