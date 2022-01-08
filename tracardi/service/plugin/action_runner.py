from tracardi.service.notation.dot_accessor import DotAccessor


class ActionRunner:
    id = None
    debug = True
    event = None
    session = None
    profile = None
    flow = None
    flow_history = None
    console = None
    node = None
    metrics = None
    execution_graph = None
    ux = None

    async def run(self, **kwargs):
        pass

    async def close(self):
        pass

    async def on_error(self):
        pass

    def _get_dot_accessor(self, payload) -> DotAccessor:
        return DotAccessor(self.profile, self.session, payload, self.event, self.flow)


