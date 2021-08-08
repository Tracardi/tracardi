from datetime import datetime


class Index:
    def __init__(self, multi_index, index, mapping, rel):
        self.multi_index = multi_index
        self.rel = rel
        self.index = index
        self.mapping = mapping

    def get_read_index(self):
        if self.multi_index is False:
            return self.index

        return self.index + "*"

    def get_write_index(self):
        if self.multi_index is False:
            return self.index

        date = datetime.now()
        return self.index + f"-{date.year}-{date.month}"


class Resource:

    def __init__(self):
        self.resources = {
            # "credential":   Index(multi_index=False, index="tracardi-credential",          mapping=None, rel=None),
            "project":      Index(multi_index=False, index="tracardi-flow-project",        mapping=None, rel=None),
            "action":       Index(multi_index=False, index="tracardi-flow-action-plugins", mapping=None, rel=None),
            "token":        Index(multi_index=False, index="tracardi-token",               mapping="mappings/token-index.json", rel=None),
            "source":       Index(multi_index=False, index="tracardi-source",              mapping=None, rel=None),
            "session":      Index(multi_index=True,  index="tracardi-session",             mapping=None, rel='profile.id'),
            "profile":      Index(multi_index=False, index="tracardi-profile",             mapping="mappings/profile-index.json", rel='_id'),
            "event":        Index(multi_index=True,  index="tracardi-event",               mapping="mappings/event-index.json", rel=None),
            "flow":         Index(multi_index=False, index="tracardi-flow",                mapping=None, rel=None),
            "rule":         Index(multi_index=False, index="tracardi-rule",                mapping=None, rel=None),
            "segment":      Index(multi_index=False, index="tracardi-segment",             mapping=None, rel=None),
            # "consent":      Index(multi_index=False, index="tracardi-consent",             mapping=None, rel=None),
            "stat-log":     Index(multi_index=False, index="tracardi-stat-log",            mapping=None, rel=None),
            "debug-info":   Index(multi_index=False, index="tracardi-debug-info",          mapping="mappings/debug-info-index.json", rel=None),
            # "response":     Index(multi_index=False, index="tracardi-response",            mapping=None, rel=None),
        }

    def __getitem__(self, item):
        return self.resources[item]

    def __contains__(self, item):
        return item in self.resources


resources = Resource()
