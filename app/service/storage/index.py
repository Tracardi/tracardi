class Index:
    def __init__(self, name, mapping, object, rel):
        self.object = object
        self.rel = rel
        self.name = name
        self.mapping = mapping


class Resource:

    def __init__(self):
        self.resources = {
            "credential":   Index(name="tracardi-credential",          object=None, mapping=None, rel=None),
            "project":      Index(name="tracardi-flow-project",        object=None, mapping=None, rel=None),
            "action":       Index(name="tracardi-flow-action-plugins", object=None, mapping=None, rel=None),
            "token":        Index(name="tracardi-token",               object=None, mapping=None, rel=None),
            "source":       Index(name="tracardi-source",              object=None, mapping=None, rel=None),
            "session":      Index(name="tracardi-session",             object=None, mapping=None, rel='profile.id'),
            "profile":      Index(name="tracardi-profile",             object=None, mapping=None, rel='_id'),
            "event":        Index(name="tracardi-event",               object=None, mapping="mappings/event-index.json", rel=None),
            "flow":         Index(name="tracardi-flow",                object=None, mapping=None, rel=None),
            "rule":         Index(name="tracardi-rule",                object=None, mapping=None, rel=None),
            "segment":      Index(name="tracardi-segment",             object=None, mapping=None, rel=None),
            "consent":      Index(name="tracardi-consent",             object=None, mapping=None, rel=None),
            "stat-log":     Index(name="tracardi-stat-log",            object=None, mapping=None, rel=None),
            "debug-info":   Index(name="tracardi-debug-info",          object=None, mapping="mappings/debug-info-index.json", rel=None),
            "response":     Index(name="tracardi-response",            object=None, mapping=None, rel=None),
        }

    def __getitem__(self, item):
        return self.resources[item]

    def __contains__(self, item):
        return item in self.resources


resources = Resource()
