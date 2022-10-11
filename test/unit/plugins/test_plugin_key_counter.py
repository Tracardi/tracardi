from tracardi.domain.profile import Profile
from tracardi.process_engine.action.v1.metrics.key_counter.service.key_counter import KeyCounter
from tracardi.service.plugin.service.plugin_runner import run_plugin

from tracardi.process_engine.action.v1.metrics.key_counter.plugin import KeyCounterAction


def test_key_counter():

    c = KeyCounter({"d": 1})
    c.count('a')
    c.count('b')
    c.count(['a', 'c'])
    c.count({"a": 10, "b": 1, "f": 1})
    try:
        c.count({"g": "asas"})
        assert False
    except ValueError:
        assert True

    result = c.counts

    assert result == {'d': 1, 'a': 12, 'b': 2, 'c': 1, 'f': 1}


def test_key_counter_plugin():
    init = {
        "key": ['mobile', 'desktop', 'mobile'],
        'save_in': 'profile@stats.counters.MobileVisits'
    }

    payload = {}
    profile = Profile(id="aaa")
    result = run_plugin(KeyCounterAction, init, payload, profile)
    assert result.profile.stats.counters['MobileVisits'] == {'mobile': 2, 'desktop': 1}
