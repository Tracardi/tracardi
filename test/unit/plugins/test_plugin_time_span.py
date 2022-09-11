from datetime import datetime, timedelta
from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.process_engine.action.v1.time.local_time_span.plugin import LocalTimeSpanAction


def test_time_span_ok():
    start = datetime.now() - timedelta(minutes=2)
    end = datetime.now() + timedelta(minutes=2)

    init = {
        "timezone": 'europe/warsaw',
        "start": start.strftime("%H:%M:%S"),
        "end": end.strftime("%H:%M:%S")
    }

    payload = {}

    plugin = run_plugin(LocalTimeSpanAction, init, payload)
    result = plugin.output
    assert result.port == 'in'
    assert result.value == payload


def test_time_span_fail():
    init = {
        "timezone": 'europe/warsaw',
        "start": (datetime.now() + timedelta(minutes=2)).strftime("%H:%M:%S"),
        "end": (datetime.now() + timedelta(minutes=4)).strftime("%H:%M:%S"),
    }

    payload = {}

    plugin = run_plugin(LocalTimeSpanAction, init, payload)
    result = plugin.output
    assert result.port == 'out'
    assert result.value == payload
