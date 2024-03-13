import asyncio
from asyncio import Task
from collections import defaultdict
from time import time
from typing import List, Tuple, Optional
from tracardi.service.license import License

from tracardi.domain.event import Event

from tracardi.service.wf.domain.debug_info import DebugInfo
from tracardi.service.wf.domain.error_debug_info import ErrorDebugInfo
from tracardi.service.wf.domain.debug_info import FlowDebugInfo
from tracardi.service.wf.domain.flow_history import FlowHistory
from tracardi.service.wf.domain.work_flow import WorkFlow
from .debugger import Debugger
from ..domain import ExtraInfo
from tracardi.service.wf.domain.entity import Entity as WfEntity
from ..domain.flow import Flow
from ..domain.flow_invoke_result import FlowInvokeResult
from ..domain.payload.tracker_payload import TrackerPayload
from ..domain.profile import Profile
from ..domain.rule_invoke_result import RuleInvokeResult
from ..domain.session import Session
from ..domain.rule import Rule
from ..exceptions.exception_service import get_traceback
from ..exceptions.log_handler import get_logger
from ..service.storage.mysql.mapping.workflow_mapping import map_to_workflow_record
from ..service.storage.mysql.service.workflow_service import WorkflowService
from ..service.utils.getters import get_entity_id

logger = get_logger(__name__)


class RulesEngine:

    def __init__(self,
                 session: Session,
                 profile: Optional[Profile],
                 events_rules: List[Tuple[List[Rule], Event]]
                 ):

        self.session = session
        self.profile = profile  # Profile can be None if profile_less event
        self.events_rules = events_rules

    async def invoke(self, ux: list, tracker_payload: TrackerPayload, debug: bool) -> RuleInvokeResult:

        source_id = tracker_payload.source.id
        flow_task_store = defaultdict(list)
        debugger = Debugger()
        invoked_rules = defaultdict(list)
        invoked_flows = []

        for rules, event in self.events_rules:

            # skip invalid events
            if not event.metadata.valid:
                continue

            for rule in rules:

                if rule is None:
                    logger.error(
                        "Rule to workflow does not exist. This may happen when you debug a workflow that "
                        "has no routing rules set but you use `Background task` or `Pause and Resume` plugin "
                        "that gets rescheduled and it could not find the routing to the workflow. "
                        "Set a routing rule and this error will be solved automatically.",
                        extra=ExtraInfo.build(
                            origin="rule",
                            event_id=event.id,
                            flow_id=None,
                            node_id=None,
                            profile_id=get_entity_id(self.profile),
                            object=self,
                            error_number="R0001"
                        )
                    )
                    continue

                # this is main roles loop
                if rule.name:
                    invoked_rules[event.id].append(rule.name)
                    rule_name = rule.name
                else:
                    rule_name = 'Unknown'

                try:
                    # Can check consents only if there is profile
                    if License.has_license() and self.profile is not None:
                        # Check consents
                        if not rule.are_consents_met(self.profile.get_consent_ids()):
                            # Consents disallow to run this rule
                            continue
                    invoked_flows.append(rule.flow.id)
                except Exception as e:
                    logger.error(
                        f"Rule '{rule_name}:{rule.id}' validation error: {str(e)}",
                        extra=ExtraInfo.build(
                            origin="rule",
                            event_id=event.id,
                            flow_id=rule.flow.id,
                            node_id=None,
                            profile_id=get_entity_id(self.profile),
                            object=self,
                            traceback=get_traceback(e),
                            error_number="R0002"
                        )
                    )
                    continue

                if not rule.enabled:
                    logger.info(f"Trigger rule `{rule.name}:{rule.id}` skipped. Trigger is disabled.")
                    continue

                logger.info(f"Triggering rule `{rule.name}:{rule.id}`")

                try:

                    # Loads flow for given rule

                    ws = WorkflowService()
                    flow_record = (await ws.load_by_id(rule.flow.id)).map_to_object(map_to_workflow_record)

                    if not flow_record:
                        raise ValueError("Could not find flow `{}`".format(rule.flow.id))

                    flow: Flow = Flow.from_workflow_record(flow_record)

                except Exception as e:
                    logger.error(str(e), e,
                                 extra=ExtraInfo.build(
                                     origin="rule",
                                     event_id=event.id,
                                     flow_id=rule.flow.id,
                                     node_id=None,
                                     profile_id=get_entity_id(self.profile),
                                     object=self,
                                     traceback=get_traceback(e),
                                     error_number="R0003"
                                 ),
                                 exc_info=True)
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
                        logger.warning(f"Workflow {rule.flow.id} skipped. Event source id (event.source.id) is not equal "
                                       f"to trigger rule source id (rule.source.id).")
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

                    # Store logs in central log
                    flow_invoke_result.register_logs_in_logger()

                except Exception as e:
                    logger.error(
                        repr(e),
                        extra=ExtraInfo.build(
                            origin="workflow",
                            event_id=event_id,
                            node_id=None,  # We do not know node id here as WF did not start
                            flow_id=flow_id,
                            profile_id=get_entity_id(self.profile),
                            object=self,
                            traceback=get_traceback(e),
                            error_number="R0003"
                        )
                    )

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
