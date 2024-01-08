from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result

import urllib
from urllib.parse import urlparse

from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class ParseURLParameters(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)
        page_url = dot[self.config.url]

        parsed = urlparse(page_url)
        params = urllib.parse.parse_qsl(parsed.query)

        result = {
            'url': page_url,
            'scheme': parsed.scheme,
            'hostname': parsed.hostname,
            'path': parsed.path,
            'query': parsed.query,
            'params': {k: v for k, v in params},
            'fragment': parsed.fragment
        }

        return Result(port="payload", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.url_parser.plugin',
            className='ParseURLParameters',
            inputs=['payload'],
            outputs=['payload'],
            init={
                'url': 'session@context.page.url'
            },
            manual="url_parser_action",
            form=Form(groups=[
                FormGroup(
                    name="Url parser",
                    fields=[
                        FormField(
                            id="url",
                            name="Path to page URL",
                            description="Type path to page url in context or session.",
                            component=FormComponent(type="dotPath", props={
                                "defaultSourceValue": "session",
                                "defaultMode": 1
                            })
                        )
                    ]
                ),
            ]),
            license="MIT + CC",
            author="EMGE1, Risto Kowaczewski",
            version="0.6.0.1"
        ),
        metadata=MetaData(
            name='Parse URL',
            desc='Reads URL parameters form context, parses it and returns result on output.',
            type='flowNode',
            width=300,
            height=100,
            icon='url',
            group=["Parsers"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns parsed URL.")
                }
            )
        )
    )
