from pydantic import BaseModel, validator
from tracardi.service.plugin.domain.result import Result

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner


class Configuration(BaseModel):
    traits_type: str
    sub_traits: str = ""

    @validator("traits_type")
    def must_be_private_or_public(cls, value):
        if value not in ['private', 'public']:
            raise ValueError("Only 'private', 'public' values are accepted, {} given".format(value))
        return value


def validate(config: dict):
    return Configuration(**config)


class AutoMergePropertiesToProfileAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        if self.profile is not None:
            if self.debug is not True:
                self.profile.operation.update = True
            if self.config.traits_type == 'private':
                self.profile.traits.private.update(self.event.properties)
                return Result(port="traits", value=self.profile.traits.private)
            else:
                self.profile.traits.public.update(self.event.properties)
                return Result(port="traits", value=self.profile.traits.public)

        return Result(port="error", value={})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AutoMergePropertiesToProfileAction',
            inputs=["payload"],
            outputs=["traits", "error"],
            init={
                "traits_type": "public",
                "sub_traits": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Define which traits to update",
                    fields=[
                        FormField(
                            id="traits_type",
                            name="Define traits type",
                            description="Please select which traits you would like to be updated with data form "
                                        "event properties.",
                            component=FormComponent(type="select", props={"label": "traits type", "items": {
                                "private": "Private",
                                "public": "Public"
                            }})
                        ),
                        FormField(
                            id="sub_traits",
                            name="Sub traits path",
                            description="Leave it empty if you want to merge data to the root of your profile traits."
                                        "Type sub-path only if you want to create or merge a part of the profile "
                                        "traits. This path will be appended to the main traits path. "
                                        "e.g: profile@traits.public.[sub.path]",
                            component=FormComponent(type="text", props={"label": "Sub path"})
                        )
                    ]
                ),
            ]),
            version='0.6.2',
            license="MIT",
            author="Risto Kowaczewski"

        ),
        metadata=MetaData(
            name='Auto merge event properties',
            desc='Automatically merges all event properties to profile traits.',
            icon='merge',
            group=["Traits"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "traits": PortDoc(desc="This port returns merged traits.")
                }
            )
        )
    )
