from typing import Dict

from pydantic import BaseModel

from tracardi.domain.event import Event
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.plugin.domain.console import Console


class ReshapeTemplate(BaseModel):
    template: str = ""
    default: bool = True


class JoinSettings(BaseModel):
    merge: bool = False
    reshape: Dict[str, ReshapeTemplate] = None
    type: str = 'dict'

    def has_reshape_templates(self) -> bool:
        return self.reshape is not None

    def get_reshape_template(self, port) -> ReshapeTemplate:
        return self.reshape[port]


class ActionRunner:
    id = None
    debug = True
    event = None  # type: Event
    session = None
    profile = None  # type: Profile
    flow = None
    flow_history = None
    console = None  # type: Console
    node = None
    metrics = None
    memory = None
    execution_graph = None  # GraphInvoker
    tracker_payload = None  # type: TrackerPayload
    ux = None
    join = None

    async def run(self, payload: dict, in_edge=None):
        pass

    async def close(self):
        pass

    async def on_error(self, e):
        pass

    def _get_dot_accessor(self, payload) -> DotAccessor:
        return DotAccessor(self.profile, self.session, payload, self.event, self.flow, self.memory)

    def update_profile(self):
        if self.debug is not True:
            if isinstance(self.profile, Profile):
                self.profile.operation.update = True
            else:
                if self.event.metadata.profile_less is True:
                    self.console.warning("Can not update profile when processing profile less events.")
                else:
                    self.console.error("Can not update profile. Profile is empty.")
        else:
            self.console.warning("Profile update skipped. It will not be updated when debugging.")

    def set_tracker_option(self, key, value):
        if isinstance(self.tracker_payload, TrackerPayload):
            self.tracker_payload.options[key] = value

    def join_output(self) -> bool:
        return isinstance(self.join, JoinSettings) and self.join.merge is True
