class Index:
    def __init__(self, name, object, rel):
        self.object = object
        self.rel = rel
        self.name = name


class Resource:

    def __init__(self):
        self.resources = {
            "credential":   Index(name="tracardi-credential",          object=None, rel=None),
            "project":      Index(name="tracardi-flow-project",        object=None, rel=None),
            "action":       Index(name="tracardi-flow-action-plugins", object=None, rel=None),
            "token":        Index(name="tracardi-token",               object=None, rel=None),
            "source":       Index(name="tracardi-source",              object=None, rel=None),
            "session":      Index(name="tracardi-session",             object=None, rel='profile.id'),
            "profile":      Index(name="tracardi-profile",             object=None, rel='_id'),
            "event":        Index(name="tracardi-event",               object=None, rel=None),
            "flow":         Index(name="tracardi-flow",                object=None, rel=None),
            "rule":         Index(name="tracardi-rule",                object=None, rel=None),
            "segment":      Index(name="tracardi-segment",             object=None, rel=None),
            "consent":      Index(name="tracardi-consent",             object=None, rel=None),
            "stat-log":     Index(name="tracardi-stat-log",            object=None, rel=None),
            "debug-info":   Index(name="tracardi-debug-info",          object=None, rel=None),
            "response":     Index(name="tracardi-response",            object=None, rel=None),
        }

    def __getitem__(self, item):
        return self.resources[item]

    def __contains__(self, item):
        return item in self.resources


resources = Resource()
