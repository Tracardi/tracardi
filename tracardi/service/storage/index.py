import os
from datetime import datetime
from typing import Optional

from tracardi.config import tracardi, elastic

_local_dir = os.path.dirname(__file__)


class Index:
    def __init__(self, multi_index, index, mapping, aliased=True, staging=False):
        self.aliased = aliased
        self.multi_index = multi_index
        self.index = index
        self.prefix = "{}.".format(tracardi.version.name)
        self.mapping = mapping
        self.staging = staging

    def get_mapping(self):
        if self.mapping:
            mapping_file = self.mapping
        else:
            mapping_file = 'mappings/default-dynamic-index.json'

        return os.path.join(f"{_local_dir}/../setup", mapping_file)

    def _get_prefixed_index(self, prefix: Optional[str] = None) -> str:
        """
        Gets real prefixed - index
        E.g. fa73a.tracardi-event
        """
        if self.aliased:
            if prefix is not None:
                prefixed_index = prefix + "." + self.index
            else:
                prefixed_index = self.prefix + self.index
        else:
            prefixed_index = self.index

        return prefixed_index

    def prepare_mappings(self, mapping):
        json_map = mapping.replace("%%PREFIX%%", tracardi.version.name)
        json_map = json_map.replace("%%ALIAS%%", self.get_index_alias())
        json_map = json_map.replace("%%VERSION%%", tracardi.version.get_version_prefix())
        json_map = json_map.replace("%%REPLICAS%%", elastic.replicas)
        json_map = json_map.replace("%%SHARDS%%", elastic.shards)
        json_map = json_map.replace("%%CONF_SHARDS%%", elastic.conf_shards)
        return json_map

    def get_index_alias(self, prefix: Optional[str] = None) -> str:
        """
        E.g. prod-fa73a.tracardi-event
        """
        prefixed_index = self._get_prefixed_index(prefix)
        return tracardi.version.prefix_with_production(prefixed_index)

    def get_write_index(self):

        # Single index writes to alias

        if self.multi_index is False:
            prefixed_index = self._get_prefixed_index()
            return tracardi.version.prefix_with_production(prefixed_index)

        # Multi index must write to month index

        date = datetime.now()
        return f"{tracardi.version.get_version_prefix()}.{self._get_prefixed_index()}-{date.year}-{date.month}"

    def get_version_write_index(self) -> str:
        if self.multi_index:
            return self.get_write_index()
        elif self.aliased:
            return self.get_aliased_data_index()
        else:
            return self.index

    def get_aliased_data_index(self):

        """
        Returns the data index not the alias.
        """

        version_prefix = tracardi.version.get_version_prefix()

        if self.multi_index is False:
            # (prod-070 | 070) . fa73a.tracardi-event
            return f"{version_prefix}.{self._get_prefixed_index()}"

        # Multi index must write to month index

        date = datetime.now()
        # (prod-070 | 070) . fa73a.tracardi-event - year - month
        return f"{version_prefix}.{self._get_prefixed_index()}-{date.year}-{date.month}"

    def get_template_index_pattern(self):

        """
        Returns template pattern.
        """

        version_prefix = tracardi.version.get_version_prefix()

        if self.multi_index is False:
            raise ValueError(f"Index {self._get_prefixed_index()} is not multi index.")

        # prod-070 . fa73a.tracardi-event - * - *
        return f"{version_prefix}.{self._get_prefixed_index()}-*-*"

    def get_prefixed_template_name(self):
        prefixed_template = f"template.{tracardi.version.name}.{self.index}"
        # (prod-070 | 070) . template . fa73a . tracardi-event
        return tracardi.version.prefix_with_production(prefixed_template)

    def get_single_storage_index(self) -> str:
        if self.multi_index:  # not single
            raise AssertionError("Can not use single index on multi index storage. "
                                 "Use get_current_multi_storage_index or get_multi_storage_alias instead.")
        # (prod-070 | 070) . fa73a.tracardi-event
        return f"{tracardi.version.get_version_prefix()}.{self._get_prefixed_index()}"

    def get_current_multi_storage_index(self) -> str:
        if not self.multi_index:  # single
            raise AssertionError("Can not use multi index on single index storage. "
                                 "Use get_single_storage_index instead.")
        date = datetime.now()

        # prod-070 . fa73a.tracardi-event - year - month
        return f"{tracardi.version.get_version_prefix()}.{self._get_prefixed_index()}-{date.year}-{date.month}"

    def get_multi_storage_alias(self) -> str:
        if not self.multi_index:  # single
            raise AssertionError("Can not use multi index alias on single index storage. "
                                 "Use get_single_storage_index instead.")
        date = datetime.now()

        # prod-070 . fa73a.tracardi-event - year - month
        return f"{tracardi.version.get_version_prefix()}.{self._get_prefixed_index()}-{date.year}-{date.month}"


class Resource:

    def __init__(self):
        self.resources = {
            "bridge": Index(staging=True, multi_index=False, index="tracardi-bridge",
                            mapping="mappings/bridge-index.json"),
            "event": Index(staging=False, multi_index=True, index="tracardi-event",
                           mapping="mappings/event-index.json"),
            "entity": Index(staging=False, multi_index=False, index="tracardi-entity",
                            mapping="mappings/entity-index.json"),
            "log": Index(staging=False, multi_index=True,
                         index='tracardi-log',
                         mapping="mappings/log-index.json"),
            "user-logs": Index(staging=False, multi_index=True, index="tracardi-user-log",
                               mapping="mappings/user-log-index.json"),

            "session": Index(staging=False, multi_index=True, index="tracardi-session",
                             mapping="mappings/session-index.json"),
            "profile": Index(staging=False, multi_index=True, index="tracardi-profile",
                             mapping="mappings/profile-index.json"),
            "console-log": Index(staging=False, multi_index=False, index="tracardi-console-log",
                                 mapping="mappings/console-log-index.json"),
            "user": Index(staging=False, multi_index=False, index="tracardi-user", mapping="mappings/user-index.json"),
            "tracardi-pro": Index(staging=False, multi_index=False, index="tracardi-pro",
                                  mapping="mappings/tracardi-pro-index.json"),

            "resource": Index(staging=True, multi_index=False, index="tracardi-resource",
                              mapping="mappings/resource-index.json"),
            "event-source": Index(staging=True, multi_index=False, index="tracardi-source",
                                  mapping="mappings/event-source-index.json"),
            "event-redirect": Index(staging=True, multi_index=False, index="tracardi-event-redirect",
                                    mapping="mappings/event-redirect-index.json"),
            "flow": Index(staging=True, multi_index=False, index="tracardi-flow", mapping="mappings/flow-index.json"),
            "rule": Index(staging=True, multi_index=False, index="tracardi-rule", mapping="mappings/rule-index.json"),
            "segment": Index(staging=True, multi_index=False, index="tracardi-segment",
                             mapping="mappings/segment-index.json"),
            "live-segment": Index(staging=True, multi_index=False, index="tracardi-live-segment",
                                  mapping="mappings/live-segment-index.json"),
            "event-management": Index(staging=True, multi_index=False, index="tracardi-event-management",
                                      mapping="mappings/event-management-index.json"),
            "debug-info": Index(staging=False, multi_index=False, index="tracardi-debug-info",
                                mapping="mappings/debug-info-index.json"),
            "api-instance": Index(staging=False, multi_index=False, index="tracardi-api-instance",
                                  mapping="mappings/api-instance-index.json"),
            "heartbeats": Index(staging=True, multi_index=False, index="tracardi-heartbeats",
                                mapping="mappings/heartbeats-index.json"),
            "event-tags": Index(staging=True, multi_index=False, index="tracardi-events-tags",
                                mapping="mappings/tag-index.json"),
            "consent-type": Index(staging=True, multi_index=False, index="tracardi-consent-type",
                                  mapping="mappings/consent-type-index.json"),
            "consent-data-compliance": Index(staging=True, multi_index=False, index="tracardi-consent-data-compliance",
                                             mapping="mappings/consent-data-compliance-index.json"),
            "event-reshaping": Index(staging=True, multi_index=False, index="tracardi-event-reshaping",
                                     mapping="mappings/event-reshaping-index.json"),
            "event-validation": Index(staging=True, multi_index=False, index="tracardi-event-validation",
                                      mapping="mappings/event-validator-index.json"),
            "destination": Index(staging=True, multi_index=False, index='tracardi-destination',
                                 mapping="mappings/destination-index.json"),
            "action": Index(staging=True, multi_index=False, index="tracardi-flow-action-plugins",
                            mapping="mappings/plugin-index.json"),
            "import": Index(staging=False, multi_index=False, index="tracardi-import",
                            mapping="mappings/import-index.json"),
            "task": Index(staging=False, multi_index=False, index="tracardi-task", mapping="mappings/task-index.json"),
            "version": Index(staging=False, multi_index=False, index="tracardi-version",
                             mapping="mappings/version-index.json",
                             aliased=True),
            "report": Index(staging=True, multi_index=False, index="tracardi-report",
                            mapping="mappings/report-index.json"),
            "identification-point": Index(staging=True, multi_index=False, index="tracardi-identification-point",
                                          mapping="mappings/identification-point-index.json")
        }

    def list_aliases(self) -> set:
        return {index.get_index_alias() for name, index in self.resources.items()}

    def get_index_constant(self, name) -> Index:
        if name in self.resources:
            return self.resources[name]
        raise ValueError(f"Index `{name}` does not exists.")

    # def add_indices(self, indices: dict):
    #     for name, index in indices.items():
    #         if not isinstance(index, Index):
    #             raise ValueError("Index must be Index object. {} given".format(type(index)))
    #
    #         if name in self.resources:
    #             raise ValueError(
    #                 "Index `{}` already exist. Check the setup process and defined resources.".format(name))
    #
    #         self.resources[name] = index
    #
    #     self.resources.update(indices)

    def __getitem__(self, item) -> Index:
        if item in self.resources:
            return self.resources[item]
        raise ValueError(f"Index `{item}` does not exists.")

    def __contains__(self, item):
        return item in self.resources


resources = Resource()
