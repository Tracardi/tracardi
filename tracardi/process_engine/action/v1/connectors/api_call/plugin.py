import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from tracardi_dot_notation.dict_traverser import DictTraverser

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.configuration import RemoteCallConfiguration


def validate(config: dict) -> RemoteCallConfiguration:
    return RemoteCallConfiguration(**config)


class RemoteCallAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    @staticmethod
    def _validate_key_value(values, label):
        for name, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    "{} values must be strings, `{}` given for {} `{}`".format(label, type(value), label.lower(),
                                                                               name))

    async def run(self, payload):

        try:

            dot = self._get_dot_accessor(payload)
            traverser = DictTraverser(dot)

            self.config.cookies = traverser.reshape(reshape_template=self.config.cookies)
            self.config.headers = traverser.reshape(reshape_template=self.config.headers)

            self._validate_key_value(self.config.headers, "Header")
            self._validate_key_value(self.config.cookies, "Cookie")

            self.config.headers['ContentType'] = self.config.body.type

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                params = self.config.get_params(dot)

                async with session.request(
                        method=self.config.method,
                        url=str(self.config.url),
                        headers=self.config.headers,
                        cookies=self.config.cookies,
                        ssl=self.config.ssl_check,
                        **params
                ) as response:

                    result = {
                        "status": response.status,
                        "content": await response.json(),
                        "cookies": response.cookies
                    }

                    if response.status in [200, 201, 202, 203]:
                        return Result(port="response", value=result), Result(port="error", value=None)
                    else:
                        return Result(port="response", value=None), Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="response", value=None), Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="response", value=None), Result(port="error", value="Remote call timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.api_call.plugin',
            className='RemoteCallAction',
            inputs=['payload'],
            outputs=["response", "error"],
            init={
                "method": "post",
                "url": None,
                "timeout": 30,
                "headers": {},
                "cookies": {},
                "ssl_check": True,
                "body": {"type": "application/json", "content": "{}"}
            },
            form=Form(groups=[
                FormGroup(
                    name="Remote call settings",
                    fields=[
                        FormField(
                            id="method",
                            name="Method",
                            description="Select API request method.",
                            component=FormComponent(type="select", props={
                                "label": "Method",
                                "items": {
                                    "get": "GET",
                                    "post": "POST",
                                    "put": "PUT",
                                    "delete": "DELETE"
                                }
                            })
                        ),
                        FormField(
                            id="url",
                            name="URL",
                            description="Type URL to be called.",
                            component=FormComponent(type="text", props={"label": "Url"})
                        ),
                        FormField(
                            id="body",
                            name="Content",
                            description="Type content to be sent. By selecting one of the tabs you define the request "
                                        "content-type. You can use dot notation to inject values from profile, event, "
                                        "or session. For HTML or TEXT use double curly braces, e.g. {{profile@id}}.",
                            component=FormComponent(type="contentInput", props={"label": "Content", "rows": 13})
                        ),
                    ]),
                FormGroup(
                    name="Advanced settings",
                    description="Set additional settings of remote request. Such as timeout, headers, etc.",
                    fields=[
                        FormField(
                            id="timeout",
                            name="Timeout",
                            description="Type value in seconds for call time-out.",
                            component=FormComponent(type="text", props={"label": "Time-out"})
                        ),
                        FormField(
                            id="ssl_check",
                            name="Validate SSL certificate",
                            description="Type if the SSL certificate must be checked.",
                            component=FormComponent(type="bool", props={"label": "Check and validate SSL certificate."})
                        ),
                        FormField(
                            id="headers",
                            name="Request headers",
                            description="Type key and value for request headers.",
                            component=FormComponent(type="keyValueList", props={"label": "Request headers"})
                        ),
                        FormField(
                            id="cookies",
                            name="Cookies",
                            description="Type key and value for cookies.",
                            component=FormComponent(type="keyValueList", props={"label": "Cookies"})
                        )
                    ]
                ),
            ]),
            version="0.6.0.1",
            author="Risto Kowaczewski",
            license="MIT",
            manual="remote_call_action"
        ),
        metadata=MetaData(
            name='Remote API call',
            desc='Sends request to remote API endpoint.',
            icon='globe',
            group=["Connectors"]
        )
    )
