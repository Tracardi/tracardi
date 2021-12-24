from datetime import datetime
import os


class Index:
    def __init__(self, multi_index, index, mapping, rel):
        self.multi_index = multi_index
        self.rel = rel
        self.index = index
        self.prefix = "{}-".format(os.environ['INSTANCE_PREFIX']) if 'INSTANCE_PREFIX' in os.environ and os.environ['INSTANCE_PREFIX'] else ''
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
            "tracardi-pro": Index(multi_index=False, index="tracardi-pro", mapping="mappings/tracardi-pro-index.json",
                                 rel=None),
            "project": Index(multi_index=False, index="tracardi-flow-project", mapping=None, rel=None),
            "action": Index(multi_index=False, index="tracardi-flow-action-plugins",
                            mapping="mappings/plugin-index.json", rel=None),
            "token": Index(multi_index=False, index="tracardi-token", mapping="mappings/token-index.json", rel=None),
            "resource": Index(multi_index=False, index="tracardi-resource", mapping="mappings/resource-index.json",
                              rel=None),
            "event-source": Index(multi_index=False, index="tracardi-event-source",
                                  mapping="mappings/event-source-index.json",
                                  rel=None),
            "session": Index(multi_index=True, index="tracardi-session", mapping="mappings/session-index.json",
                             rel='profile.id'),
            "profile": Index(multi_index=True, index="tracardi-profile", mapping="mappings/profile-index.json",
                             rel='_id'),
            "event": Index(multi_index=True, index="tracardi-event", mapping="mappings/event-index.json", rel=None),
            "flow": Index(multi_index=False, index="tracardi-flow", mapping="mappings/flow-index.json", rel=None),
            "rule": Index(multi_index=False, index="tracardi-rule", mapping="mappings/rule-index.json", rel=None),
            "segment": Index(multi_index=False, index="tracardi-segment", mapping="mappings/segment-index.json",
                             rel=None),
            "console-log": Index(multi_index=False, index="tracardi-console-log",
                                 mapping="mappings/console-log-index.json", rel=None),
            "stat-log": Index(multi_index=False, index="tracardi-stat-log", mapping=None, rel=None),
            "debug-info": Index(multi_index=False, index="tracardi-debug-info",
                                mapping="mappings/debug-info-index.json", rel=None),
            "api-instance": Index(multi_index=False, index="tracardi-api-instance",
                                  mapping="mappings/api-instance-index.json", rel=None),
            "task": Index(multi_index=False, index="tracardi-task", mapping="mappings/task-index.json", rel=None),
            "profile-purchase": Index(multi_index=False, index="tracardi-profile-purchase",
                                      mapping="mappings/profile-purchase-index.json", rel=None),
            "event-tags": Index(multi_index=False, index="tracardi-event-tags", mapping="mappings/tag-index.json",
                                rel=None),
            "consent-type": Index(multi_index=False, index="tracardi-consent-type", mapping="mappings/consent-type.json",
                                rel=None),
            "user": Index(multi_index=False, index="tracardi-user", mapping="mappings/user-index.json", rel=None),
            "validation-schema": Index(multi_index=False, index="tracardi-validation-schema",
                                       mapping="mappings/validation-schema-index.json", rel=None)
        }

    def add_indices(self, indices: dict):
        for name, index in indices.items():
            if not isinstance(index, Index):
                raise ValueError("Index must be Index object. {} given".format(type(index)))

            if name in self.resources:
                raise ValueError("Index `{}` already exist. Check the setup process and defined resources.".format(name))

            self.resources[name] = index

        self.resources.update(indices)

    def __getitem__(self, item):
        return self.resources[item]

    def __contains__(self, item):
        return item in self.resources


resources = Resource()
