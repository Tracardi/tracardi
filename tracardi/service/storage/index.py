from datetime import datetime
import os


class Index:
    def __init__(self, multi_index, index, mapping, rel):
        self.multi_index = multi_index
        self.rel = rel
        self.index = index
        self.prefix = "{}-".format(os.environ['INSTANCE_PREFIX']) if 'INSTANCE_PREFIX' in os.environ else ''
        self.mapping = mapping

    def _index(self):
        return self.prefix + self.index

    def get_read_index(self):
        if self.multi_index is False:
            return self._index()

        return self._index() + "*"

    def get_write_index(self):
        if self.multi_index is False:
            return self._index()

        date = datetime.now()
        return self._index() + f"-{date.year}-{date.month}"


class Resource:

    def __init__(self):
        self.resources = {
            "project": Index(multi_index=False, index="tracardi-flow-project", mapping=None, rel=None),
            "action": Index(multi_index=False, index="tracardi-flow-action-plugins", mapping=None, rel=None),
            "token": Index(multi_index=False, index="tracardi-token", mapping="mappings/token-index.json", rel=None),
            "resource": Index(multi_index=False, index="tracardi-resource", mapping=None, rel=None),
            "session": Index(multi_index=True, index="tracardi-session", mapping=None, rel='profile.id'),
            "profile": Index(multi_index=False, index="tracardi-profile", mapping="mappings/profile-index.json",
                             rel='_id'),
            "event": Index(multi_index=True, index="tracardi-event", mapping="mappings/event-index.json", rel=None),
            "flow": Index(multi_index=False, index="tracardi-flow", mapping=None, rel=None),
            "rule": Index(multi_index=False, index="tracardi-rule", mapping=None, rel=None),
            "segment": Index(multi_index=False, index="tracardi-segment", mapping="mappings/segment-index.json",
                             rel=None),
            "console-log": Index(multi_index=False, index="tracardi-console-log",
                                 mapping="mappings/console-log-index.json", rel=None),
            "stat-log": Index(multi_index=False, index="tracardi-stat-log", mapping=None, rel=None),
            "debug-info": Index(multi_index=False, index="tracardi-debug-info",
                                mapping="mappings/debug-info-index.json", rel=None),
            "api-instance": Index(multi_index=False, index="tracardi-api-instance",
                                  mapping="mappings/api-instance-index.json", rel=None),
            "task": Index(multi_index=False, index="tracardi-task", mapping="mappings/task-index.json", rel=None)
        }

    def __getitem__(self, item):
        return self.resources[item]

    def __contains__(self, item):
        return item in self.resources


resources = Resource()
