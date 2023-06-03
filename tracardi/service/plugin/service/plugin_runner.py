import asyncio
from typing import Type
from uuid import uuid4

from tracardi.domain.event import Event
from tracardi.domain.event_source import EventSource
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from ..domain.result import Result
from ..runner import ActionRunner
from ..domain.console import Console
from tracardi.service.wf.domain.graph_invoker import GraphInvoker


class PluginTestResult:
    def __init__(self, output, profile=None, session=None, event=None, console=None, flow=None):
        self.event: Event = event
        self.session: Session = session
        self.profile: Profile = profile
        self.output: Result = output
        self.console = console
        self.flow = flow

    def __repr__(self):
        return f"output=`{self.output}`\nprofile=`{self.profile}`\nsession=`{self.session}`\nevent=`{self.session}`" \
               f"\nconsole=`{self.console}`"


def run_plugin(plugin: Type[ActionRunner], init, payload, profile=None, session=None, event=None, flow=None,
               node=None, in_edge=None) -> PluginTestResult:
    async def main(plugin, init, payload):
        try:

            plugin = plugin()

            console = Console("Test", "test", "abc")

            plugin.id = str(uuid4())
            plugin.profile = profile
            plugin.session = session
            plugin.event = event
            plugin.console = console
            plugin.flow = flow
            plugin.node = node
            plugin.tracker_payload = TrackerPayload(
                source=EventSource(
                    id="@test-resource",
                    type=["web-page"],
                    name="Test resource",
                    bridge=NamedEntity(id="1", name="rest"),
                    description="This resource is created for test purposes.",
                    tags=['test']
                ),
                session=session
            )
            plugin.execution_graph = GraphInvoker(graph=[], start_nodes=[])

            await plugin.set_up(init)
            output = await plugin.run(payload, in_edge=in_edge)

            return PluginTestResult(
                output,
                profile,
                session,
                event,
                console,
                flow
            )

        except Exception as e:
            if isinstance(plugin, ActionRunner):
                await plugin.on_error(e)
            raise e
        finally:
            if isinstance(plugin, ActionRunner):
                await plugin.close()

    return asyncio.run(main(plugin, init, payload))
