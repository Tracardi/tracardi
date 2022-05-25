from datetime import datetime

import tracardi.config
from tracardi.config import elastic


class Index:
    def __init__(self, multi_index, index, mapping, rel=None, aliased=True):
        self.aliased = aliased
        self.multi_index = multi_index
        self.rel = rel
        self.index = index
        if elastic.instance_prefix:
            self.prefix = "{}-".format(elastic.instance_prefix)
        else:
            self.prefix = ''
        self.mapping = mapping

    def _index(self):
        if self.aliased:
            return self.prefix + self.index
        return self.index

    def get_read_index(self):
        return self._index()

    def get_write_index(self):

        # Single index writes to alias

        if self.multi_index is False:
            return self._index()

        # Multi index must write to month index

        date = datetime.now()
        return f"{tracardi.config.tracardi.version.get_version_prefix()}.{self._index()}-{date.year}-{date.month}"

    def get_aliased_data_index(self):

        """
        Returns the data index not the alias.
        """

        version_prefix = tracardi.config.tracardi.version.get_version_prefix()

        if self.multi_index is False:
            return f"{version_prefix}.{self._index()}"

        # Multi index must write to month index

        date = datetime.now()
        return f"{version_prefix}.{self._index()}-{date.year}-{date.month}"

    def get_template_pattern(self):

        """
        Returns template pattern.
        """

        version_prefix = tracardi.config.tracardi.version.get_version_prefix()

        if self.multi_index is False:
            raise ValueError(f"Index {self._index()} is not multi index.")

        return f"{version_prefix}.{self._index()}-*-*"

    def get_prefixed_template_name(self):
        if tracardi.config.elastic.instance_prefix != '':
            return "template.{}-{}".format(tracardi.config.elastic.instance_prefix, self.index)
        return self.index


class Resource:

    def __init__(self):
        self.resources = {
            "event": Index(multi_index=True, index="tracardi-event", mapping="mappings/event-index.json", rel=None),
            "log": Index(multi_index=True,
                         index='tracardi-log',
                         mapping="mappings/log-index.json",
                         rel=None),
            "user-logs": Index(multi_index=True, index="tracardi-user-log", mapping="mappings/user-log-index.json",
                               rel=None),

            "session": Index(multi_index=True, index="tracardi-session", mapping="mappings/session-index.json",
                             rel='profile.id'),
            "profile": Index(multi_index=True, index="tracardi-profile", mapping="mappings/profile-index.json",
                             rel='_id'),
            "console-log": Index(multi_index=False, index="tracardi-console-log",
                                 mapping="mappings/console-log-index.json", rel=None),
            "user": Index(multi_index=False, index="tracardi-user", mapping="mappings/user-index.json", rel=None),
            "tracardi-pro": Index(multi_index=False, index="tracardi-pro", mapping="mappings/tracardi-pro-index.json",
                                  rel=None),
            "project": Index(multi_index=False, index="tracardi-flow-project", mapping=None, rel=None),

            "resource": Index(multi_index=False, index="tracardi-resource", mapping="mappings/resource-index.json",
                              rel=None),
            "event-source": Index(multi_index=False, index="tracardi-source",
                                  mapping="mappings/event-source-index.json",
                                  rel=None),
            "flow": Index(multi_index=False, index="tracardi-flow", mapping="mappings/flow-index.json", rel=None),
            "rule": Index(multi_index=False, index="tracardi-rule", mapping="mappings/rule-index.json", rel=None),
            "segment": Index(multi_index=False, index="tracardi-segment", mapping="mappings/segment-index.json",
                             rel=None),

            "stat-log": Index(multi_index=False, index="tracardi-stat-log", mapping=None, rel=None),
            "debug-info": Index(multi_index=False, index="tracardi-debug-info",
                                mapping="mappings/debug-info-index.json", rel=None),
            "api-instance": Index(multi_index=False, index="tracardi-api-instance",
                                  mapping="mappings/api-instance-index.json", rel=None),
            "schedule": Index(multi_index=False, index="tracardi-schedule", mapping="mappings/schedule-index.json",
                              rel=None),
            "event-tags": Index(multi_index=False, index="tracardi-events-tags", mapping="mappings/tag-index.json",
                                rel=None),
            "consent-type": Index(multi_index=False, index="tracardi-consent-type",
                                  mapping="mappings/consent-type.json",
                                  rel=None),

            "validation-schema": Index(multi_index=False, index="tracardi-validation-schema",
                                       mapping="mappings/validation-schema-index.json", rel=None),
            "value-threshold": Index(multi_index=False, index='tracardi-state-threshold',
                                     mapping="mappings/value-threshold-index.json",
                                     rel=None),
            "destination": Index(multi_index=False, index='tracardi-destination',
                                 mapping="mappings/destination-index.json",
                                 rel=None),
            "action": Index(multi_index=False, index="tracardi-flow-action-plugins",
                            mapping="mappings/plugin-index.json", rel=None),
            "import": Index(multi_index=False, index="tracardi-import", mapping="mappings/import-index.json", rel=None),
            "task": Index(multi_index=False, index="tracardi-task", mapping="mappings/task-index.json", rel=None),
            "version": Index(multi_index=False, index="tracardi-version", mapping="mappings/version-index.json",
                             aliased=False)
        }

    def list_aliases(self) -> set:
        return {index.get_read_index() for name, index in self.resources.items()}

    def get_index(self, name) -> Index:
        if name in self.resources:
            return self.resources[name]
        raise ValueError(f"Index `{name}` does not exists.")

    def add_indices(self, indices: dict):
        for name, index in indices.items():
            if not isinstance(index, Index):
                raise ValueError("Index must be Index object. {} given".format(type(index)))

            if name in self.resources:
                raise ValueError(
                    "Index `{}` already exist. Check the setup process and defined resources.".format(name))

            self.resources[name] = index

        self.resources.update(indices)

    def __getitem__(self, item):
        if item in self.resources:
            return self.resources[item]
        raise ValueError(f"Index `{item}` does not exists.")

    def __contains__(self, item):
        return item in self.resources


resources = Resource()
