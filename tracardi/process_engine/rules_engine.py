import asyncio
import logging
from asyncio import Task
from collections import defaultdict
from time import time
from typing import Dict, List, Tuple, Optional
from tracardi.service.license import License

from tracardi.domain.event import Event

from tracardi.service.wf.domain.debug_info import DebugInfo
from tracardi.service.wf.domain.error_debug_info import ErrorDebugInfo
from tracardi.service.wf.domain.debug_info import FlowDebugInfo
from tracardi.service.wf.domain.flow_history import FlowHistory
from tracardi.service.wf.domain.work_flow import WorkFlow
from .debugger import Debugger
from ..config import tracardi
from ..domain.console import Console
from ..domain.entity import Entity
from tracardi.service.wf.domain.entity import Entity as WfEntity
from ..domain.flow import Flow
from ..domain.flow_invoke_result import FlowInvokeResult
from ..domain.payload.tracker_payload import TrackerPayload
from ..domain.profile import Profile
from ..domain.rule_invoke_result import RuleInvokeResult
from ..domain.session import Session
from ..domain.rule import Rule
from ..exceptions.exception_service import get_traceback
from ..exceptions.log_handler import log_handler
from ..service.console_log import ConsoleLog

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class RulesEngine:

    def __init__(self,
                 session: Session,
                 profile: Optional[Profile],
                 events_rules: List[Tuple[List[Dict], Event]],
                 console_log: ConsoleLog
                 ):

        self.console_log = console_log
        self.session = session
        self.profile = profile  # Profile can be None if profile_less event
        self.events_rules = events_rules

    async def invoke(self, load_flow_callable, ux: list, tracker_payload: TrackerPayload, debug: bool) -> RuleInvokeResult:

        source_id = tracker_payload.source.id
        flow_task_store = defaultdict(list)
        debugger = Debugger()
        invoked_rules = defaultdict(list)
        invoked_flows = []

        for rules, event in self.events_rules:

            # skip invalid events
            if not event.metadata.valid:
                continue

            if len(rules) == 0:
                logger.debug(
                    f"Could not find rules for event \"{event.type}\". Check if the rule exists and is enabled.")

            for rule in rules:

                if rule is None:
                    console = Console(
                        origin="rule",
                        event_id=event.id,
                        flow_id=None,
                        node_id=None,
                        profile_id=self.profile.id,
                        module=__name__,
                        class_name=RulesEngine.__name__,
                        type="error",
                        message="Rule to workflow does not exist. This may happen when you debug a workflow that "
                                "has no routing rules set but you use `Background task` or `Pause and Resume` plugin "
                                "that gets rescheduled and it could not find the routing to the workflow. "
                                "Set a routing rule and this error will be solved automatically."
                    )
                    self.console_log.append(console)
                    continue

                # this is main roles loop
                if 'name' in rule:
                    invoked_rules[event.id].append(rule['name'])
                    rule_name = rule['name']
                else:
                    rule_name = 'Unknown'

                try:
                    rule = Rule(**rule)

                    # Can check consents only if there is profile
                    if License.has_license() and self.profile is not None:
                        # Check consents
                        if not rule.are_consents_met(self.profile.get_consent_ids()):
                            # Consents disallow to run this rule
                            continue
                    invoked_flows.append(rule.flow.id)
                except Exception as e:
                    console = Console(
                        origin="rule",
                        event_id=event.id,
                        flow_id=None,
                        node_id=None,
                        profile_id=None,
                        module=__name__,
                        class_name='RulesEngine',
                        type="error",
                        message=f"Rule '{rule_name}:{rule.id}' validation error: {str(e)}",
                        traceback=get_traceback(e)
                    )
                    self.console_log.append(console)
                    continue

                if not rule.enabled:
                    logger.info(f"Trigger rule `{rule.name}:{rule.id}` skipped. Trigger is disabled.")
                    continue

                logger.info(f"Triggering rule `{rule.name}:{rule.id}`")

                try:

                    # Loads flow for given rule

                    flow: Flow = await load_flow_callable(rule.flow.id)

                except Exception as e:
                    logger.error(str(e))
                    # This is empty DebugInfo without nodes
                    debug_info = DebugInfo(
                        timestamp=time(),
                        flow=FlowDebugInfo(
                            id=rule.flow.id,
                            name=rule.flow.name,
                            error=[ErrorDebugInfo(msg=str(e), file=__file__, line=103)]
                        ),
                        event=WfEntity(id=event.id)
                    )
                    debugger[event.type].append({rule.name: debug_info})
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
                        logger.debug(f"Invoked workflow {flow.name}:{flow.id} for event {event.type}:{event.id}")

                        # Debugging can be controlled from tracker payload.

                        flow_task = asyncio.create_task(
                            workflow.invoke(flow,
                                            event,
                                            self.profile,
                                            self.session,
                                            ux,
                                            debug=debug
                                            )
                        )

                        # Append to task store to be awaited latter

                        flow_task_store[event.type].append((rule.flow.id, event.id, rule.name, flow_task))

                    else:
                        logger.warning(f"Workflow {rule.flow.id} skipped. Event source id is not equal "
                                       f"to trigger rule source id.")
                else:
                    # todo FlowHistory is empty
                    workflow = WorkFlow(
                        FlowHistory(history=[])
                    )

                    # Creating task can cause problems. It must be thoroughly tested as
                    # concurrently running flows on the same profile may override profile data.
                    # Preliminary tests showed no issues but on heavy load we do not know if
                    # the test is still valid and every thing is ok. Solution is to remove create_task.
                    flow_task = asyncio.create_task(
                        workflow.invoke(flow, event, self.profile, self.session, ux, debug=debug)
                    )

                    # Append flows to flow_task store
                    flow_task_store[event.type].append((rule.flow.id, event.id, rule.name, flow_task))

        # Run flows and report async

        post_invoke_events = {}
        flow_responses = []
        changed_field_timestamps: List[dict] = []
        for event_type, tasks in flow_task_store.items():
            for flow_id, event_id, rule_name, task in tasks:  # type: str, str, str, Task
                try:
                    flow_invoke_result = await task  # type: FlowInvokeResult

                    self.profile = flow_invoke_result.profile
                    self.session = flow_invoke_result.session
                    debug_info = flow_invoke_result.debug_info
                    log_list = flow_invoke_result.log_list
                    post_invoke_event = flow_invoke_result.event

                    changed_field_timestamps += flow_invoke_result.flow.get_changes()

                    flow_responses.append(flow_invoke_result.flow.response)
                    post_invoke_events[post_invoke_event.id] = post_invoke_event

                    # Store logs in one console log
                    self.console_log.append_event_log_list(event_id, flow_id, log_list)

                except Exception as e:
                    # todo log error
                    console = Console(
                        origin="workflow",
                        event_id=event_id,
                        node_id=None,  # We do not know node id here as WF did not start
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
                        event=WfEntity(id=event_id),
                        flow=FlowDebugInfo(
                            id=rule.flow.name,
                            name=rule.flow.name,
                            error=[ErrorDebugInfo(msg=str(e), file=__file__, line=86)]
                        )
                    )

                debugger[event_type].append({rule_name: debug_info})

        ran_event_types = list(flow_task_store.keys())

        return RuleInvokeResult(
            debugger,
            ran_event_types,
            post_invoke_events,
            invoked_rules,
            invoked_flows,
            flow_responses,
            changed_field_timestamps
        )

    def _get_merging_keys_and_values(self):
        merge_key_values = self.profile.get_merge_key_values()

        # Add keyword
        merge_key_values = [(f"{field}.keyword", value) for field, value in merge_key_values if value is not None]

        return merge_key_values
