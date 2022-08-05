import asyncio
from typing import Type
from uuid import uuid4

from ..runner import ActionRunner
from ..domain.console import Console
from tracardi.service.wf.domain.graph_invoker import GraphInvoker


class PluginTestResult:
    def __init__(self, output, profile=None, session=None, event=None, console=None, flow=None):
        self.event = event
        self.session = session
        self.profile = profile
        self.output = output
        self.console = console
        self.flow = flow

    def __repr__(self):
        return f"output=`{self.output}`\nprofile=`{self.profile}`\nsession=`{self.session}`\nevent=`{self.session}`" \
               f"\nconsole=`{self.console}`"


def run_plugin(plugin: Type[ActionRunner], init, payload, profile=None, session=None, event=None, flow=None,
               node=None, in_edge=None) -> PluginTestResult:

    async def main(plugin, init, payload):
        try:

            build_method = getattr(plugin, "build", None)
            if build_method and callable(build_method):
                plugin = await build_method(**init)
            else:
                plugin = plugin(**init)

            console = Console("Test", "test")

            plugin.id = str(uuid4())
            plugin.profile = profile
            plugin.session = session
            plugin.event = event
            plugin.console = console
            plugin.flow = flow
            plugin.node = node
            plugin.execution_graph = GraphInvoker(graph=[], start_nodes=[])

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
