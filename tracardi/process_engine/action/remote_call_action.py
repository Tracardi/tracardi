import json
from datetime import datetime

import aiohttp
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class RemoteCallAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'url' not in kwargs:
            raise ValueError("Url is not set. Define it in config section.")
        self.url = kwargs['url']

        if 'payloadIn' in kwargs:
            payload_in = kwargs['payloadIn']
            if payload_in not in ['body', 'params']:
                raise ValueError("Param `payloadIn` must be either 'body' or 'params'. {} given".format(payload_in))
            self.payload_in = payload_in
        else:
            self.payload_in = "body"

        if 'timeout' in kwargs:
            self.timeout = int(kwargs['timeout'])
        else:
            self.timeout = 30

        if 'method' not in kwargs:
            self.method = 'get'
        else:
            self.method = kwargs['method']

    @staticmethod
    def _datetime_handler(date):
        if isinstance(date, datetime):
            return date.isoformat()
        raise TypeError("Unknown type")

    async def run(self, payload):

        if self.payload_in == 'params':
            if type(payload) not in [str, bool, int, float]:
                raise ValueError("Payload is not str, bool, int or float. Can not convert it URL into params.")

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:

            payload = json.dumps(payload, default=self._datetime_handler)
            payload = json.loads(payload)

            kwargs = {
                "json" if self.payload_in == 'body' else 'params': payload
            }

            async with session.request(
                    method=self.method,
                    url=self.url,
                    **kwargs
            ) as response:

                    result = {
                        "status": response.status,
                        "content": await response.json()
                    }
                    if response.status in [200, 201, 202, 203]:
                        return Result(port="response", value=result), Result(port="error", value=None)
                    else:
                        return Result(port="response", value=None), Result(port="error", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.remote_call_action',
            className='RemoteCallAction',
            inputs=['payload'],
            outputs=["response", "error"],
            init={
                "method": "undefined",
                "url": "undefined",
                "payloadIn": "body|params"
            },
            manual="remote_call_action"
        ),
        metadata=MetaData(
            name='Remote call',
            desc='Sends request to remote API endpoint.',
            type='flowNode',
            width=200,
            height=100,
            icon='cloud',
            group=["Integration"]
        )
    )
