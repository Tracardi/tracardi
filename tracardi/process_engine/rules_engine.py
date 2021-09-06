import asyncio
from asyncio import Task
from collections import defaultdict
from time import time
from typing import Dict, List, Tuple
from pydantic import ValidationError
from tracardi.domain.event import Event

from tracardi_graph_runner.domain.debug_info import DebugInfo
from tracardi_graph_runner.domain.error_debug_info import ErrorDebugInfo
from tracardi_graph_runner.domain.debug_info import FlowDebugInfo
from tracardi_graph_runner.domain.flow_history import FlowHistory
from tracardi_graph_runner.domain.work_flow import WorkFlow
from tracardi_plugin_sdk.domain.console import Log
from ..domain.console import Console
from ..domain.entity import Entity
from ..domain.profile import Profile
from ..domain.session import Session
from ..domain.rule import Rule


class RulesEngine:

    def __init__(self,
                 session: Session,
                 profile: Profile,
                 events_rules: List[Tuple[Task, Event]],
                 console_log=None
                 ):

        if console_log is None:
            console_log = []

        self.console_log = console_log
        self.session = session
        self.profile = profile
        self.events_rules = events_rules

    async def invoke(self, load_flow_callable, source_id=None) -> Tuple[Dict[str, List[Dict[str, DebugInfo]]], list, list]:

        flow_task_store = defaultdict(list)
        debug_info_by_event_type_and_rule_name = defaultdict(list)

        for rules_loading_task, event in self.events_rules:

            # Loads rules only for event.type
            rules = await rules_loading_task

            for rule in rules:

                try:
                    rule = Rule(**rule)
                except ValidationError as e:
                    print(str(e))
                    # todo log error and disable rule
                    continue

                if not rule.enabled:
                    continue

                try:
                    flow = await load_flow_callable(rule.flow.id)
                except Exception as e:
                    # This is empty DebugInfo without nodes
                    debug_info = DebugInfo(
                        timestamp=time(),
                        flow=FlowDebugInfo(
                            id=rule.flow.id,
                            error=[ErrorDebugInfo(msg=str(e), file=__file__, line=103)]
                        ),
                        event=Entity(id=event.id)
                    )
                    debug_info_by_event_type_and_rule_name[event.type].append({rule.name: debug_info})
                    continue

                if not flow.enabled:
                    continue

                # Validates rule source. Type was verified before

                if source_id:
                    if source_id == event.source.id:
                        # todo FlowHistory is empty
                        workflow = WorkFlow(
                            FlowHistory(history=[]),
                            self.session,
                            self.profile,
                            event
                        )
                        flow_task = asyncio.create_task(workflow.invoke(flow, debug=False))
                        flow_task_store[event.type].append((rule.flow.id, event.id, rule.name, flow_task))
                else:
                    # todo FlowHistory is empty
                    workflow = WorkFlow(
                        FlowHistory(history=[]),
                        self.session,
                        self.profile,
                        event
                    )
                    flow_task = asyncio.create_task(workflow.invoke(flow, debug=False))
                    flow_task_store[event.type].append((rule.flow.id, event.id, rule.name, flow_task))

        # Run and report async

        for event_type, tasks in flow_task_store.items():
            for flow_id, event_id, rule_name, task in tasks:
                try:
                    debug_info, log_list = await task  # type: DebugInfo, List[Log]

                    # Store logs in one console log
                    for log in log_list:  # type: Log
                        console = Console(
                            origin="node",
                            event_id=event_id,
                            flow_id=flow_id,
                            module=log.module,
                            class_name=log.class_name,
                            type=log.type,
                            message=log.message
                        )
                        self.console_log.append(console)

                except Exception as e:
                    # todo log error

                    console = Console(
                        origin="workflow",
                        event_id=event_id,
                        flow_id=flow_id,
                        module='tracardi.process_engine.rules_engine',
                        class_name="RulesEngine",
                        type="error",
                        message=str(e)
                    )
                    self.console_log.append(console)

                    debug_info = DebugInfo(
                        timestamp=time(),
                        flow=FlowDebugInfo(
                            id=flow_id,
                            error=[ErrorDebugInfo(msg=str(e), file=__file__, line=86)]
                        ),
                        event=Entity(id=event_id)
                    )

                debug_info_by_event_type_and_rule_name[event_type].append({rule_name: debug_info})

        ran_event_types = list(flow_task_store.keys())

        return debug_info_by_event_type_and_rule_name, ran_event_types, self.console_log
        # # Save profile
        #
        # segmentation_info = {"errors": [], "ids": []}
        # try:
        #     save_tasks = []
        #
        #     # Segmentation
        #     if self.profile.operation.needs_update() or self.profile.operation.needs_segmentation():
        #         # Segmentation runs only if profile was updated or flow forced it
        #         async for event_type, segment_id, error in self.profile.segment(
        #                 flow_task_store.keys(),
        #                 load_segment_by_event_type):
        #             # Segmentation triggered
        #             if error:
        #                 segmentation_info['errors'].append(error)
        #             segmentation_info['ids'].append(segment_id)
        #
        #     # Merging, schedule save only if there is an update in flow.
        #
        #     if self.profile.operation.needs_merging() and self.profile.operation.needs_update():
        #
        #         disabled_profiles = await self.profile.merge(limit=2000)
        #         if disabled_profiles is not None:
        #             save_old_profiles_task = asyncio.create_task(
        #                 StorageForBulk(disabled_profiles).index('profile').save())
        #             save_tasks.append(save_old_profiles_task)
        #
        #     # Must be the last operation
        #     if self.profile.operation.needs_update():
        #         save_tasks.append(asyncio.create_task(StorageFor(self.profile).index().save()))
        #
        #     # run save tasks
        #     await asyncio.gather(*save_tasks)
        #
        # except Exception as e:
        #     # this error is a global segmentation error
        #     # todo log it.
        #     print(str(e))
        #     pass
        #
        # finally:
        #     return debug_info_by_event_type_and_rule_name, segmentation_info, console_log

    @staticmethod
    def _mark_profiles_as_merged(profiles, merge_with) -> List[Profile]:
        disabled_profiles = []

        for profile in profiles:
            profile.active = False
            profile.mergedWith = merge_with
            disabled_profiles.append(profile)

        return disabled_profiles

    def _get_merging_keys_and_values(self):
        merge_key_values = self.profile.get_merge_key_values()

        # Add keyword
        merge_key_values = [(f"{field}.keyword", value) for field, value in merge_key_values if value is not None]

        return merge_key_values

    # async def execute(self, source_id) -> Tuple[Dict[str, List[Dict[str, DebugInfo]]], Dict[str, list], list]:
    #
    #     """ Runs rules and flow and saves debug info and console log """
    #
    #     debug_info_by_event_type_and_rule_name, segmentation_info, console_log = await self.invoke(source_id)
    #
    #     # # Save console log
    #     #
    #     # if console_log:
    #     #     await StorageForBulk(console_log).index('console-log').save()
    #     #
    #     # # Collect debug info
    #     #
    #     # record = []
    #     # for debug_info_record in EventDebugRecord.encode(
    #     #         debug_info_by_event_type_and_rule_name):  # type: EventDebugRecord
    #     #     record.append(debug_info_record)
    #     #
    #     # # Save in debug index
    #     # await StorageForBulk(record).index("debug-info").save()
    #     #
    #     # return debug_info_by_event_type_and_rule_name, segmentation_info, console_log
