import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from tracardi.service.notation.dict_traverser import DictTraverser

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.configuration import Configuration
from tracardi.service.tracardi_http_client import HttpClient


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class HtmlPageFetchAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

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

            # headers['ContentType'] =

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with HttpClient(
                self.node.on_connection_error_repeat,
                [200, 201, 202, 203],
                timeout=timeout
            ) as client:

                params = self.config.get_params(dot)

                async with client.request(
                        method=self.config.method,
                        url=str(self.config.url),
                        headers=headers,
                        cookies=cookies,
                        ssl=self.config.ssl_check,
                        **params
                ) as response:

                    result = {
                        "status": response.status,
                        "content": await response.text(),
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
            module=__name__,
            className='HtmlPageFetchAction',
            inputs=['payload'],
            outputs=["response", "error"],
            init={
                "method": "get",
                "url": None,
                "timeout": 30,
                "headers": {},
                "cookies": {},
                "ssl_check": True,
                "body": ""
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
                            description="Type content to be sent. For replacing some part of content with data use "
                                        "double curly braces, e.g. {{profile@id}}.",
                            component=FormComponent(type="textarea", props={"label": "Content", "rows": 13})
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
            version="0.6.1",
            author="Risto Kowaczewski",
            license="MIT"
        ),
        metadata=MetaData(
            name='HTML fetcher',
            desc='Fetches HTML page.',
            icon='globe',
            group=["Connectors"]
        )
    )
