import json

import aiohttp

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.service import plugin_context
from tracardi.service.wf.domain.node import Node


class MicroserviceAction(ActionRunner):

    init: dict

    async def set_up(self, init):
        self.init = init

    async def run(self, payload: dict, in_edge=None):
        # todo remotely run
        node = self.node  # type: Node
        context = plugin_context.get_context(self, include=['node'])

        service_id = node.microservice.service.id
        action_id = node.microservice.plugin.id
        config = {
            "init": self.init,
            "context": context,
            "params": {
                "payload": payload,
                "in_edge": in_edge.dict() if in_edge else None
            }
        }
        config = json.loads(json.dumps(config, default=str))
        microservice_url = f"{node.microservice.server.credentials['url']}/plugin/run" \
                           f"?service_id={service_id}" \
                           f"&action_id={action_id}"
        async with aiohttp.ClientSession(headers={
            'X-Token': node.microservice.server.credentials['token']
        }) as client:
            async with client.post(
                    url=microservice_url,
                    json=config) as remote_response:
                print(await remote_response.json())

        plugin_context.set_context(self, context)
        return None


# todo do not need register as this is not registered.
def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MicroserviceAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.7.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={

            }
        ),
        metadata=MetaData(
            name='Microservice',
            desc='Runs remote microservice plugin.',
            icon='cloud',
            group=["Operations"],
            remote=True,
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns microservice response.")
                }
            )
        )
    )
