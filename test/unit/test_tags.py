from tracardi.domain.event import Tags


def test_event_tags():
    t = Tags(values=("a",))
    assert t.count == 1
    t.add("b")
    assert t.count == 2
    assert t.values == ('a', 'b')

    t = Tags()
    assert t.count == 0
    t.add("a")
    assert t.count == 1
    assert t.values == ('a',)
