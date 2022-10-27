from base64 import b64decode

from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Configuration(PluginConfig):
    source: str
    target_encoding: str


def validate(config: dict):
    return Configuration(**config)


class Base64DecodeAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        base64 = dot[self.config.source]
        result = b64decode(base64 + '==').decode(self.config.target_encoding)

        return Result(port="payload", value={"text": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=Base64DecodeAction.__name__,
            inputs=['payload'],
            outputs=['payload'],
            version='0.1',
            license='MIT',
            author='knittl',
            manual='base64_decode',
            init={
                'source': '',
                'target_encoding': 'utf-8'
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id='source',
                            name='Base64 source',
                            description='Type path to string or string itself.',
                            component=FormComponent(type='dotPath', props={'defaultSourceValue': 'event'})
                        ),
                        FormField(
                            id='target_encoding',
                            name='Target Encoding',
                            description='Output text encoding. Will be used to convert output bytes to text after '
                                        'base64-decoding it. Set to "utf-8" if unsure.',
                            component=FormComponent(type='text', props={'label': 'encoding'})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Decode Base64',
            desc='Decodes a base64-encoded input to plain text',
            group=['Converters'],
            tags=['base64'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object with base64 encoded data.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns the plain text decoded from base64-encoded input.")
                }
            ),
        )
    )
