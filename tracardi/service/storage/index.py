import json
import os
from datetime import datetime
from typing import Generator, Any, Tuple

from tracardi.config import tracardi, elastic
from tracardi.context import get_context
from tracardi.service.singleton import Singleton

_local_dir = os.path.dirname(__file__)


class Index:
    def __init__(self, multi_index, index, mapping, staging=False, static=False, single=False, partitioning=None):
        self.multi_index = multi_index
        self.index = index
        self._version_prefix = tracardi.version.get_version_prefix()  # eg.080
        self.mapping = mapping
        self.staging = staging
        self.static = static
        self.single = single
        self.partitioning = 'month' if partitioning is None else partitioning

    @staticmethod
    def _get_quarter(month):
        """
        Get the quarter of the year based on the month.

        Args:
        month (int): The month number (1-12).

        Returns:
        int: The quarter of the year (1-4).
        """
        if 1 <= month <= 3:
            return 1
        elif 4 <= month <= 6:
            return 2
        elif 7 <= month <= 9:
            return 3
        elif 10 <= month <= 12:
            return 4
        else:
            raise ValueError("Invalid month. Month should be between 1 and 12.")

    def _multi_index_suffix(self) -> str:
        """
        Current date suffix
        """
        date = datetime.now()
        if self.partitioning == 'month':
            return f"{date.year}-{date.month}"
        elif self.partitioning == 'year':
            return f"{date.year}-year"
        elif self.partitioning == 'day':
            return f"{date.year}-{date.month}/{date.day}"
        elif self.partitioning == 'hour':
            return f"{date.year}-{date.month}/{date.day}/{date.hour}"
        elif self.partitioning == 'minute':
            return f"{date.year}-{date.month}/{date.day}/{date.hour}/{date.minute}"
        elif self.partitioning == 'quarter':
            return f"{date.year}-q{self._get_quarter(date.month)}"
        else:
            raise ValueError("Unknown partitioning. Expected: year, month, quarter, or day")

    @staticmethod
    def _prefix_with_static(index):
        return f"static-{index}"

    @staticmethod
    def _prefix_with_production(index):
        return f"prod-{index}"

    def _prod_or_static(self, index):
        if self.static:
            return self._prefix_with_static(index)
        if get_context().is_production():
            return self._prefix_with_production(index)
        return index

    def get_mapping(self):
        if self.mapping:
            mapping_file = self.mapping
        else:
            mapping_file = 'mappings/default-dynamic-index.json'

        return os.path.join(f"{_local_dir}/../setup", mapping_file)

    def _get_prefixed_index(self) -> str:
        """
        Gets real prefixed - index
        E.g. fa73a.tracardi-event or tenant.tracardi-event
        or tracardi-event if single index
        """

        if self.single is True:
            return self.index

        return f"{get_context().tenant}.{self.index}"

    def prepare_mappings(self, mapping, index) -> dict:

        json_map = mapping.replace("%%PREFIX%%", tracardi.version.name)
        json_map = json_map.replace("%%ALIAS%%", self.get_index_alias())
        json_map = json_map.replace("%%VERSION%%", self._version_prefix)
        json_map = json_map.replace("%%REPLICAS%%", elastic.replicas)
        json_map = json_map.replace("%%SHARDS%%", elastic.shards)
        json_map = json_map.replace("%%CONF_SHARDS%%", elastic.conf_shards)
        if index.multi_index:
            template_pattern = index.get_templated_index_pattern()
            json_map = json_map.replace("%%TEMPLATE_PATTERN%%", template_pattern)

        return json.loads(json_map)

    def get_index_alias(self) -> str:
        """
        E.g. (prod|static)-fa73a.tracardi-event
        """
        prefixed_index = self._get_prefixed_index()

        if self.single is True:
            # Eg. fa73a.tracardi-license
            return f"{get_context().tenant}.{prefixed_index}"

        return self._prod_or_static(prefixed_index)

    def get_write_index(self):

        # Single index writes to alias

        if self.multi_index is True:
            # Multi index must write to month index
            prefixed_index = f"{self._get_prefixed_index()}-{self._multi_index_suffix()}"
        else:
            prefixed_index = self._get_prefixed_index()

        if self.single is True:
            # Eg. tracardi-license
            return prefixed_index

        version_prefix_index = f"{self._version_prefix}.{prefixed_index}"

        return self._prod_or_static(version_prefix_index)

    def get_templated_index_pattern(self):

        """
        Returns template pattern.
        """
        if self.static is True:
            raise AssertionError("Static index should not be a multi data index.")

        prefixed_index = self._get_prefixed_index()

        if self.multi_index is False:
            raise ValueError(f"Index {prefixed_index} is not multi index.")

        multi_index_pattern = f"{prefixed_index}-*-*"

        if self.single is True:
            # Eg. tracardi-license-*-*
            return multi_index_pattern

        # (prod|static) 070 . fa73a.tracardi-event - * - *
        index = f"{self._version_prefix}.{multi_index_pattern}"

        return self._prod_or_static(index)

    def get_prefixed_template_name(self):
        if self.multi_index is False:
            raise AssertionError("Can not get template for not multi index.")
        if self.static is True:
            raise AssertionError("Static index should not be a multi data index.")

        prefixed_index = self._get_prefixed_index()

        if self.single is True:
            # Eg. template.tracardi-license
            return f"template.{prefixed_index}"

        prefixed_template = f"template.{self._version_prefix}.{prefixed_index}"
        # (prods | static) template . 070 . fa73a . tracardi-event
        return self._prod_or_static(prefixed_template)

    def get_single_storage_index(self) -> str:
        if self.multi_index:  # not single
            raise AssertionError("Can not use single index on multi index storage. "
                                 "Use get_current_multi_storage_index or get_multi_storage_alias instead.")
        # (prod|static) 070 . fa73a.tracardi-event
        return self.get_write_index()

    # todo probably not used
    def get_current_multi_storage_index(self) -> str:
        if not self.multi_index:  # single
            raise AssertionError("Can not use multi index on single index storage. "
                                 "Use get_single_storage_index instead.")
        # (prod|static)  070 . fa73a.tracardi-event - year - month
        return self.get_write_index()

    def get_multi_storage_alias(self) -> str:
        if not self.multi_index:  # single
            raise AssertionError("Can not use multi index alias on single index storage. "
                                 "Use get_single_storage_index instead.")
        # fa73a.tracardi-event
        return self.get_index_alias()


class Resource(metaclass=Singleton):

    def __init__(self):
        self.resources = {
            "bridge": Index(staging=False, static=True, multi_index=False, index="tracardi-bridge",
                            mapping="mappings/bridge-index.json"),
            "event": Index(staging=False,
                           multi_index=True,
                           partitioning=tracardi.event_partitioning,
                           index="tracardi-event",
                           mapping="mappings/event-index.json"),
            "entity": Index(staging=False,
                            multi_index=True,
                            partitioning=tracardi.entity_partitioning,
                            index="tracardi-entity",
                            mapping="mappings/entity-index.json"),
            "log": Index(staging=False,
                         multi_index=True,
                         partitioning=tracardi.log_partitioning,
                         index='tracardi-log',
                         mapping="mappings/log-index.json"),
            "user-logs": Index(staging=False,
                               multi_index=True,
                               partitioning=tracardi.user_log_partitioning,
                               index="tracardi-user-log",
                               mapping="mappings/user-log-index.json"),
            "session": Index(staging=False,
                             multi_index=True,
                             partitioning=tracardi.session_partitioning,
                             index="tracardi-session",
                             mapping="mappings/session-index.json"),
            "profile": Index(staging=False,
                             multi_index=True,
                             partitioning=tracardi.profile_partitioning,
                             index="tracardi-profile",
                             mapping="mappings/profile-index.json"),
            "item": Index(staging=False,
                          multi_index=True,
                          partitioning=tracardi.item_partitioning,
                          index="tracardi-item",
                          mapping="mappings/item-index.json"),
            "console-log": Index(staging=False,
                                 multi_index=True,
                                 index="tracardi-console-log",
                                 partitioning=tracardi.console_log_partitioning,
                                 mapping="mappings/console-log-index.json"),
            "dispatch-log": Index(staging=False,
                                  multi_index=True,
                                  partitioning=tracardi.dispatch_log_partitioning,
                                  index="tracardi-dispatch-log",
                                  mapping="mappings/dispatch-log-index.json"),
            "field-update-log": Index(staging=False,
                                      multi_index=True,
                                      partitioning=tracardi.field_change_log_partitioning,
                                      index="tracardi-field-update-log",
                                      mapping="mappings/field-update-log-index.json"),
            "user": Index(staging=True,
                          multi_index=False,
                          index="tracardi-user",
                          mapping="mappings/user-index.json"),
            "tracardi-pro": Index(staging=False, multi_index=False, index="tracardi-pro",
                                  mapping="mappings/tracardi-pro-index.json"),
            "entity-list": Index(staging=True, multi_index=False, index="tracardi-entity-list",
                                 mapping="mappings/entity-list-index.json"),
            "resource": Index(staging=True, multi_index=False, index="tracardi-resource",
                              mapping="mappings/resource-index.json"),
            "event-source": Index(staging=True, multi_index=False, index="tracardi-source",
                                  mapping="mappings/event-source-index.json"),
            "event-redirect": Index(staging=True, multi_index=False, index="tracardi-event-redirect",
                                    mapping="mappings/event-redirect-index.json"),
            "flow": Index(staging=True, multi_index=False, index="tracardi-flow",
                          mapping="mappings/flow-index.json"),
            "rule": Index(staging=True, multi_index=False, index="tracardi-rule",
                          mapping="mappings/rule-index.json"),
            "segment": Index(staging=True, multi_index=False, index="tracardi-segment",
                             mapping="mappings/segment-index.json"),
            "live-segment": Index(staging=True, multi_index=False, index="tracardi-live-segment",
                                  mapping="mappings/live-segment-index.json"),
            "content": Index(staging=True,
                             multi_index=False,
                             index="tracardi-content",
                             mapping="mappings/content-index.json"),
            "setting": Index(staging=True,
                             multi_index=False,
                             index="tracardi-setting",
                             mapping="mappings/settings-index.json"),
            "event-management": Index(staging=True,
                                      multi_index=False,
                                      index="tracardi-event-management",
                                      mapping="mappings/event-management-index.json"),
            "event-to-profile": Index(staging=True,
                                      multi_index=False,
                                      index="tracardi-event_to_profile",
                                      mapping="mappings/event-to-profile-index.json"),
            "debug-info": Index(staging=False,
                                multi_index=False,
                                index="tracardi-debug-info",
                                mapping="mappings/debug-info-index.json"),
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
            "action": Index(staging=False,
                            static=True,
                            multi_index=False,
                            index="tracardi-flow-action-plugins",
                            mapping="mappings/plugin-index.json"),
            "import": Index(staging=False, multi_index=False, index="tracardi-import",
                            mapping="mappings/import-index.json"),
            "task": Index(staging=False, multi_index=False, index="tracardi-task", mapping="mappings/task-index.json"),
            "report": Index(staging=True, multi_index=False, index="tracardi-report",
                            mapping="mappings/report-index.json"),
            "identification-point": Index(staging=True, multi_index=False, index="tracardi-identification-point",
                                          mapping="mappings/identification-point-index.json"),
            "version": Index(staging=False, multi_index=False, index="tracardi-version",
                             mapping="mappings/version-index.json")
        }

    def list_aliases(self) -> set:
        return {index.get_index_alias() for name, index in self.resources.items()}

    def get_index_constant(self, name) -> Index:
        if name in self.resources:
            return self.resources[name]
        raise ValueError(f"Index `{name}` does not exists.")

    def get_index_mappings(self) -> Generator[Tuple[Index, dict], Any, None]:
        for key, index in self.resources.items():  # type: str, Index

            map_file = index.get_mapping()

            with open(map_file) as file:
                map = file.read()
                map = index.prepare_mappings(map, index)
                yield index, map

    def get_template_name(self, index) -> str:
        log_index = self[index]
        return log_index.get_prefixed_template_name()

    def __getitem__(self, item) -> Index:
        if item in self.resources:
            return self.resources[item]
        raise ValueError(f"Index `{item}` does not exists.")

    def __contains__(self, item):
        return item in self.resources
