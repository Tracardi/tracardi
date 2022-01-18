from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.plugin.domain.console import Console


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
    execution_graph = None
    ux = None

    async def run(self, **kwargs):
        pass

    async def close(self):
        pass

    async def on_error(self, e):
        pass

    def _get_dot_accessor(self, payload) -> DotAccessor:
        return DotAccessor(self.profile, self.session, payload, self.event, self.flow)


