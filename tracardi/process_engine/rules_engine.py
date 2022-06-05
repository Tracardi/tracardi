import asyncio
import logging
import traceback
from asyncio import Task
from collections import defaultdict
from time import time
from typing import Dict, List, Tuple, Optional
from pydantic import ValidationError
from tracardi.domain.event import Event, INVALID

from tracardi.service.wf.domain.debug_info import DebugInfo
from tracardi.service.wf.domain.error_debug_info import ErrorDebugInfo
from tracardi.service.wf.domain.debug_info import FlowDebugInfo
from tracardi.service.wf.domain.flow_history import FlowHistory
from tracardi.service.wf.domain.work_flow import WorkFlow
from tracardi.service.plugin.domain.console import Log
from .debugger import Debugger
from ..config import tracardi
from ..domain.console import Console
from ..domain.entity import Entity
from ..domain.payload.tracker_payload import TrackerPayload
from ..domain.profile import Profile
from ..domain.session import Session
from ..domain.rule import Rule
from ..exceptions.exception_service import get_traceback
from ..exceptions.log_handler import log_handler

logger = logging.getLogger("Routing rule")
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class RulesEngine:

    def __init__(self,
                 session: Session,
                 profile: Optional[Profile],
                 events_rules: List[Tuple[List[Dict], Event]],
                 console_log=None
                 ):

        if console_log is None:
            console_log = []

        self.console_log = console_log
        self.session = session
        self.profile = profile  # Profile can be None if profile_less event
        self.events_rules = events_rules

    async def invoke(self, load_flow_callable, ux: list, tracker_payload: TrackerPayload) -> Tuple[Debugger, list, list, dict, Dict[str, list]]:

        source_id = tracker_payload.source.id
        flow_task_store = defaultdict(list)
        debugger = Debugger()
        invoked_rules = defaultdict(list)

        for rules, event in self.events_rules:

            # skip invalid events
            if event.metadata.status == INVALID:
                continue

            if len(rules) == 0:
                logger.debug(f"Could not find rules for event \"{event.type}\". Check if the rule exists and is enabled.")

            for rule in rules:

                # this is main roles loop
                if 'name' in rule:
                    invoked_rules[event.type].append(rule['name'])

                try:
                    rule = Rule(**rule)
                except ValidationError as e:
                    console = Console(
                        origin="rule",
                        event_id=event.id,
                        flow_id=None,
                        module=__name__,
                        class_name='RulesEngine',
                        type="error",
                        message="Rule validation error: ".format(str(e)),
                        traceback=get_traceback(e)
                    )
                    self.console_log.append(console)
                    continue

                if not rule.enabled:
                    logger.info(f"Rule {rule.name} skipped. Rule is disabled.")
                    continue

                logger.info(f"Running rule {rule.name}")

                try:

                    # Loads flow for given rule

                    flow = await load_flow_callable(rule.flow.id)

                except Exception as e:
                    # This is empty DebugInfo without nodes
                    debug_info = DebugInfo(
                        timestamp=time(),
                        flow=FlowDebugInfo(
                            id=rule.flow.id,
                            name=rule.flow.name,
                            error=[ErrorDebugInfo(msg=str(e), file=__file__, line=103)]
                        ),
                        event=Entity(id=event.id)
                    )
                    debugger[event.type].append({rule.name: debug_info})
                    continue

                if not flow.enabled:
                    continue

                # Validates rule source. Type was verified before

                if source_id:
                    if source_id == event.source.id:

                        # Create workflow and pass data

                        # todo FlowHistory is empty
                        workflow = WorkFlow(
                            flow_history=FlowHistory(history=[]),
                            tracker_payload=tracker_payload
                        )

                        # Flows are run concurrently

                        flow_task = asyncio.create_task(workflow.invoke(flow, event, self.profile, self.session, ux, debug=False))
                        flow_task_store[event.type].append((rule.flow.id, event.id, rule.name, flow_task))

                    else:
                        logger.warning(f"Workflow {rule.flow.id} skipped. Event source id is not equal "
                                       f"to rule source id.")
                else:
                    # todo FlowHistory is empty
                    workflow = WorkFlow(
                        FlowHistory(history=[])
                    )

                    # Creating task can cause problems. It must be thoroughly tested as
                    # concurrently running flows on the same profile may override profile data.
                    # Preliminary tests showed no issues but on heavy load we do not know if
                    # the test is still valid and every thing is ok. Solution is to remove create_task.
                    flow_task = asyncio.create_task(workflow.invoke(flow, event, self.profile, self.session, ux, debug=False))
                    flow_task_store[event.type].append((rule.flow.id, event.id, rule.name, flow_task))

        # Run flows and report async

        post_invoke_events = {}
        for event_type, tasks in flow_task_store.items():
            for flow_id, event_id, rule_name, task in tasks:
                try:
                    debug_info, log_list, post_invoke_event, self.profile, self.session = await task  # type: DebugInfo, List[Log], Event, Profile, Session
                    post_invoke_events[post_invoke_event.id] = post_invoke_event

                    # Store logs in one console log
                    for log in log_list:  # type: Log
                        console = Console(
                            origin="node",
                            event_id=event_id,
                            flow_id=flow_id,
                            module=log.module,
                            class_name=log.class_name,
                            type=log.type,
                            message=log.message,
                            traceback=log.traceback
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
                        message=repr(e),
                        traceback=get_traceback(e)
                    )
                    self.console_log.append(console)

                    debug_info = DebugInfo(
                        timestamp=time(),
                        flow=FlowDebugInfo(
                            id=rule.flow.name,
                            name=rule.flow.name,
                            error=[ErrorDebugInfo(msg=str(e), file=__file__, line=86)]
                        ),
                        event=Entity(id=event_id)
                    )

                debugger[event_type].append({rule_name: debug_info})

        ran_event_types = list(flow_task_store.keys())

        return debugger, \
               ran_event_types, \
               self.console_log, \
               post_invoke_events, \
               invoked_rules

    @staticmethod
    def _mark_profiles_as_merged(profiles, merge_with) -> List[Profile]:
        disabled_profiles = []

        for profile in profiles:   # type: Profile
            profile.active = False
            profile.metadata.merged_with = merge_with
            disabled_profiles.append(profile)

        return disabled_profiles

    def _get_merging_keys_and_values(self):
        merge_key_values = self.profile.get_merge_key_values()

        # Add keyword
        merge_key_values = [(f"{field}.keyword", value) for field, value in merge_key_values if value is not None]

        return merge_key_values
