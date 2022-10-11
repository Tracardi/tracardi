import asyncio
import aiohttp
from aiohttp import ClientConnectorError, ContentTypeError

from tracardi.service.notation.dict_traverser import DictTraverser
from json import JSONDecodeError

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.wf.domain.node import Node
from .model.configuration import RemoteCallConfiguration
from tracardi.service.storage.driver import storage
from tracardi.service.url_constructor import ApiCredentials


def validate(config: dict) -> RemoteCallConfiguration:
    return RemoteCallConfiguration(**config)


class RemoteCallAction(ActionRunner):

    credentials: ApiCredentials
    config: RemoteCallConfiguration

    async def set_up(self, init):
        config = RemoteCallConfiguration(**init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, ApiCredentials)

    @staticmethod
    def _validate_key_value(values, label):
        for name, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    "{} values must be strings, `{}` given for {} `{}`".format(label, type(value), label.lower(),
                                                                               name))

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:

            dot = self._get_dot_accessor(payload)
            traverser = DictTraverser(dot)

            cookies = traverser.reshape(reshape_template=self.config.cookies)
            headers = traverser.reshape(reshape_template=self.config.headers)

            self._validate_key_value(headers, "Header")
            self._validate_key_value(cookies, "Cookie")

            headers['ContentType'] = self.config.body.type

            node = self.node  # type: Node

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with HttpClient(timeout=timeout, retries=node.on_connection_error_repeat) as session:

                params = self.config.get_params(dot)
                url = self.credentials.get_url(dot=dot, endpoint=self.config.endpoint)

                self.console.log("Making {} request to {}".format(self.config.method.upper(), url))

                async with session.request(
                        method=self.config.method,
                        url=url,
                        headers=headers,
                        cookies=cookies,
                        ssl=self.config.ssl_check,
                        proxy=self.credentials.proxy,
                        **params
                ) as response:

                    try:
                        content = await response.json(content_type=None)

                    except JSONDecodeError:
                        content = await response.text()

                    except ContentTypeError:
                        content = await response.json(content_type='text/html')

                    result = {
                        "status": response.status,
                        "content": content,
                        "cookies": response.cookies
                    }

                    if response.status in [200, 201, 202, 203]:
                        return Result(port="response", value=result)
                    else:
                        return Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="error", value="Remote call timed out.")


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
                "source": {"name": None, "id": None},
                "endpoint": None,
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
                            id="source",
                            name="Resource",
                            description="Select your API resource containing your URL and API credentials.",
                            component=FormComponent(type="resource", props={"tag": "api"})
                        ),
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
                            id="endpoint",
                            name="Endpoint",
                            description="Type endpoint that should be called. Feel free to use dot templates, e.g. "
                                        "/some/{{payload@value}}/endpoint.",
                            component=FormComponent(type="text", props={"label": "Endpoint"})
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
