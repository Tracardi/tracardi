import hashlib
import json

from pydantic import BaseModel
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Configuration(BaseModel):
    value: str
    func: str = 'md5'


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class GetValueHashAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):

        dot = self._get_dot_accessor(payload)
        value = dot[self.config.value]

        if not isinstance(value, str):
            value = json.dumps(value)

        self.console.log(f"Hashed value:{value}")
        if self.config.func == 'md5':
            result = hashlib.md5(value.encode())
        elif self.config.func == 'sha256':
            result = hashlib.sha256(value.encode())
        elif self.config.func == 'sha1':
            result = hashlib.sha1(value.encode())
        elif self.config.func == 'sha512':
            result = hashlib.sha512(value.encode())
        else:
            result = hashlib.md5(value.encode())
        return Result(port='uuid4', value={
            "uuid4": result.hexdigest()
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='GetValueHashAction',
            inputs=["payload"],
            outputs=['hash'],
            version='0.6.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={"value": "", "func": "md5"},
            form=Form(groups=[
                FormGroup(
                    name="Value to hash",
                    fields=[
                        FormField(
                            id="value",
                            name="Reference value to be hashed",
                            description="If this value is not a string then it will be serialized to JSON and hashed.",
                            component=FormComponent(type="dotPath",
                                                    props={"label": "value", "defaultSourceValue": "event"})
                        ),
                        FormField(
                            id="func",
                            name="Hashing function",
                            description="Select hashing method.",
                            component=FormComponent(type="select",
                                                    props={"label": "Hashing", "items": {
                                                        "md5": "MD5",
                                                        "sha1": "SHA1",
                                                        "sha256": "SHA256",
                                                        "sha512": "SHA512"
                                                    }})
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='Hash value',
            desc='Generates MD5 or SHA1 hash from value.',
            icon='hash',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "hash": PortDoc(desc="This port returns md5 hash of configured value.")
                }
            )
        )
    )
