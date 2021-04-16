condition_mapper = {
    "event": {
        "condition": "eventPropertyCondition",
        "fields": {  # allowed fields
            'id': "itemId",
            'type': 'eventType',
            'timestamp': 'timeStamp',
            'profile.id': "profileId",
            'session.id': "sessionId",
            'source.id': "source.itemId",
            'target.id': "target.itemId",
            'source.scope': "source.scope",
            'target.scope': "target.scope",
            'source.type': "source.itemType",
            'target.type': "target.itemType",
            'target.profile.id': "target.profile.itemType",

            # original

            'itemId': 'itemId',
            'itemType': 'itemType',
            'eventType': 'eventType',
            'scope': "scope",
            'sessionId':'sessionId',
            'profileId': 'profileId',
            'timeStamp':'timeStamp',
            'version': 'version',
            'persistent': 'persistent',
        },
        "namespaces": {  # allowed fields namespace
            'properties': "properties",
            'source': "source",
            'target': "target",
            'profile': 'profile',
        },
    },
    "profile": {
        "condition": "profilePropertyCondition",
        "fields": {
            'id': "itemId",
            'timestamp': 'systemProperties.lastUpdated',
            'visits': 'properties.nbOfVisits'
        },
        "namespaces": {
            'systemProperties': "systemProperties",
            'system.properties': "systemProperties",
            'properties': "properties",
            'segments': "segments",
            'scores': "scores",
        },
    },
    "session": {
        "condition": "sessionPropertyCondition",
        "fields": {
            "duration": 'duration',
            'id': "itemId",
            'scope': "scope",
            'timestamp': 'timeStamp',
            'profile.id': "profileId",
            'profile.type': "profile.itemType",
            'profile.timestamp': "profile.systemProperties.lastUpdated",
        },
        "namespaces": {
            'properties': "properties",
            'profile.properties': "profile.properties",
            'profile.segments': "profile.segments",
            'profile.scores': "profile.scores",
        }
    },
    "rule": {
        "condition": 'eventPropertyCondition',
        "fields": {  # allowed fields

            'id': "itemId",
            'type': 'eventType',
            'name': 'metadata.name',
            'description': 'metadata.description',
            'scope': 'metadata.scope',
            'tag': 'metadata.tags',
            'system.tag': 'metadata.systemTags',

            # Original
            'itemId': 'itemId',
            'itemType': 'itemType',
            'eventType': 'eventType',
            'version': 'version',
            'priority': 'priority',
            'linkedItems': 'linkedItems'
        },
        "namespaces": {
            "metadata": "metadata"
        }
    },
    "segment": {
        "condition": 'profilePropertyCondition',
        "fields": {  # allowed fields

            # Segment
            'id': "itemId",
            'segment.id': "itemId",

            # Profile
            'profile.properties': "properties",

            # Original
            'itemType': 'itemType',
        },
        "namespaces": {
            'properties': "properties",
            'segments': "segments",
            'scores': "scores",
        }
    }
}
