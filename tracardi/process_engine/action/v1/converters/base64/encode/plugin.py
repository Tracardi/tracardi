from base64 import b64encode

from tracardi.process_engine.action.v1.converters.base64.utils.text_encodings import common_encodings
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Documentation, Form, FormComponent, FormField, FormGroup, \
    MetaData, Plugin, PortDoc, Spec
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Configuration(PluginConfig):
    source: str
    source_encoding: str


def validate(config: dict):
    return Configuration(**config)


class Base64EncodeAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        text = dot[self.config.source]
        result = b64encode(text.encode(self.config.source_encoding)).decode('ascii')

        return Result(port="payload", value={"base64": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=Base64EncodeAction.__name__,
            inputs=['payload'],
            outputs=['payload'],
            version='0.7.3',
            license='MIT',
            author='knittl',
            manual='base64_encode',
            init={
                'source': '',
                'source_encoding': 'utf_8',
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id='source',
                            name='Text source',
                            description='Type path to string or string itself.',
                            component=FormComponent(type='dotPath', props={'defaultSourceValue': 'event'}),
                        ),
                        FormField(
                            id='source_encoding',
                            name='Source Encoding',
                            description='Input text encoding. Will be used to convert input text to bytes before '
                                        'base64-encoding it. If unsure, choose "UTF-8". If the required encoding is '
                                        'not listed, it must be configured in the raw JSON config (all standard Python '
                                        'text encoding keys are supported)',
                            component=FormComponent(type='select', props={
                                'label': 'encoding',
                                'items': common_encodings,
                                'initValue': 'utf_8'
                            }),
                        ),
                    ],
                ),
            ]),
        ),
        metadata=MetaData(
            name='Encode Base64',
            desc='Encodes input text to base64',
            group=['Converters'],
            icon='password',
            tags=['base64'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns base64-encoded data.")
                },
            ),
        ),
    )
