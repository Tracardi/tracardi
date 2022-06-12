from datetime import datetime
import tracardi.config


class Index:
    def __init__(self, multi_index, index, mapping, aliased=True):
        self.aliased = aliased
        self.multi_index = multi_index
        self.index = index
        self.prefix = "{}.".format(tracardi.config.tracardi.version.name)
        self.mapping = mapping

    def _index(self):
        if self.aliased:
            return self.prefix + self.index
        return self.index

    def get_index_alias(self):
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
        return "template.{}.{}".format(tracardi.config.tracardi.version.name, self.index)


class Resource:

    def __init__(self):
        self.resources = {
            "event": Index(multi_index=True, index="tracardi-event", mapping="mappings/event-index.json"),
            "log": Index(multi_index=True,
                         index='tracardi-log',
                         mapping="mappings/log-index.json"),
            "user-logs": Index(multi_index=True, index="tracardi-user-log", mapping="mappings/user-log-index.json"),

            "session": Index(multi_index=True, index="tracardi-session", mapping="mappings/session-index.json"),
            "profile": Index(multi_index=True, index="tracardi-profile", mapping="mappings/profile-index.json"),
            "console-log": Index(multi_index=False, index="tracardi-console-log",
                                 mapping="mappings/console-log-index.json"),
            "user": Index(multi_index=False, index="tracardi-user", mapping="mappings/user-index.json"),
            "tracardi-pro": Index(multi_index=False, index="tracardi-pro", mapping="mappings/tracardi-pro-index.json"),

            "resource": Index(multi_index=False, index="tracardi-resource", mapping="mappings/resource-index.json"),
            "event-source": Index(multi_index=False, index="tracardi-source",
                                  mapping="mappings/event-source-index.json"),
            "flow": Index(multi_index=False, index="tracardi-flow", mapping="mappings/flow-index.json"),
            "rule": Index(multi_index=False, index="tracardi-rule", mapping="mappings/rule-index.json"),
            "segment": Index(multi_index=False, index="tracardi-segment", mapping="mappings/segment-index.json"),

            "debug-info": Index(multi_index=False, index="tracardi-debug-info",
                                mapping="mappings/debug-info-index.json"),
            "api-instance": Index(multi_index=False, index="tracardi-api-instance",
                                  mapping="mappings/api-instance-index.json"),
            "schedule": Index(multi_index=False, index="tracardi-schedule", mapping="mappings/schedule-index.json"),
            "event-tags": Index(multi_index=False, index="tracardi-events-tags", mapping="mappings/tag-index.json"),
            "consent-type": Index(multi_index=False, index="tracardi-consent-type",
                                  mapping="mappings/consent-type.json"),

            "event-management": Index(multi_index=False, index="tracardi-event-management",
                                       mapping="mappings/event-management-index.json"),
            "value-threshold": Index(multi_index=False, index='tracardi-state-threshold',
                                     mapping="mappings/value-threshold-index.json"),
            "destination": Index(multi_index=False, index='tracardi-destination',
                                 mapping="mappings/destination-index.json"),
            "action": Index(multi_index=False, index="tracardi-flow-action-plugins",
                            mapping="mappings/plugin-index.json"),
            "import": Index(multi_index=False, index="tracardi-import", mapping="mappings/import-index.json"),
            "task": Index(multi_index=False, index="tracardi-task", mapping="mappings/task-index.json"),
            "version": Index(multi_index=False, index="tracardi-version", mapping="mappings/version-index.json",
                             aliased=False)
        }

    def list_aliases(self) -> set:
        return {index.get_index_alias() for name, index in self.resources.items()}

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
