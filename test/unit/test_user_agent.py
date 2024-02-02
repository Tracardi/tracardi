from user_agents.parsers import UserAgent

from tracardi.domain.entity import Entity
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import Session, SessionMetadata
from tracardi.service.tracking.session_data_computation import _get_user_agent

def test_user_agent_string_from_tracker_payload():
    # Setup
    session = Session(
        id="1",
        metadata=SessionMetadata()
    )
    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
        request={
            'headers': {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        }
    )

    # Execute
    result = tracker_payload.get_user_agent()

    # Assert
    assert isinstance(result, UserAgent)
    assert result.browser.family == 'Chrome'
    assert result.browser.version_string == '58.0.3029'


def test_user_agent_string():
    # Setup
    session = Session(
        id="1",
        metadata=SessionMetadata()
    )
    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
    )
    tracker_payload.request = {
        'headers': {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    }

    # Execute
    result = _get_user_agent(session, tracker_payload)

    # Assert
    assert isinstance(result, UserAgent)
    assert result.browser.family == 'Chrome'
    assert result.browser.version_string == '58.0.3029'


def test_fail_user_agent_string():
    # Setup
    session = Session(
        id="1",
        metadata=SessionMetadata()
    )
    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
    )
    tracker_payload.request = {
        'headers': {
            'user-agent': 'Msdasdfsdg029.110 Safari/537.3'
        }
    }

    # Execute
    result = _get_user_agent(session, tracker_payload)

    # Assert
    assert isinstance(result, UserAgent)
    assert result.browser.family == 'Safari'

    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
    )

    # Execute
    result = _get_user_agent(session, tracker_payload)

    # Assert
    assert result is None

def test_user_agent_string_bot():
    # Setup
    session = Session(
        id="1",
        metadata=SessionMetadata()
    )
    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
        request={
            'headers': {
                'user-agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'
            }
        }
    )

    # Execute
    result = tracker_payload.get_user_agent()

    # Assert
    assert isinstance(result, UserAgent)
    assert result.is_bot

