def filter_event(result):
    for i, event in enumerate(result['list']):
        yield {
            "id": i,
            "eventId": event['itemId'] if 'itemId' in event else 0,
            'scope': event['scope'],
            "type": event['eventType'],
            'version': 1,
            'session': event['sessionId'],
            'profile': event['profileId'],
            'timestamp': event['timeStamp']
        }


def filter_segment(result):
    for i, segment in enumerate(result):
        yield {
            "metadata": segment
        }


def filter_profile(result):
    for i, rule in enumerate(result['list']):
        yield {
            "id": i,
            "profileId": rule['itemId'] if 'itemId' in rule else 0,
            "systemProperties": rule['systemProperties'] if 'systemProperties' in rule else {},
            "properties": rule['properties'],
            "segments": rule['segments'],
            "scores": rule['scores'],
            "mergedWith": rule['mergedWith'],
            "consents": rule['consents'],
        }
