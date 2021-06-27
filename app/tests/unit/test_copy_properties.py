from ...process_engine.actions.copy_property_action import CopyPropertyAction


def test_copy_properties():
    event_properties = {
        "a": {
            "b": {
                "c": 1
            },
            "d": [1, 2, 3]
        }
    }

    profile_properties = {
        "a": {
            "e": 2
        }
    }

    config = {
        # event.property -> profile.traits
        'a.b.c': ['a.b.d'],
        'a.d': ["d"]
    }

    new_properties = CopyPropertyAction.copy_properties(event_properties, profile_properties, config)

    assert new_properties['a']['b']['d'] == 1
    assert new_properties['d'] == [1, 2, 3]

    config = {
        'a.b.c': ['d.1']
    }

    new_properties = CopyPropertyAction.copy_properties(event_properties, new_properties, config)
    assert new_properties['d'] == [1, 1, 3]

    config = {
        'a.b': ['d.1']
    }

    new_properties = CopyPropertyAction.copy_properties(event_properties, new_properties, config)
    assert new_properties['d'] == [1, {"c": 1}, 3]
