from dotty_dict import dotty
from tracardi.service.plugin.domain.result import Result

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    sub_traits: str = ""


def validate(config: dict):
    return Configuration(**config)


class AutoMergePropertiesToProfileAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    def _update(self, source, value) -> dict:
        path = self.config.sub_traits.strip()
        if path:
            dotty_source = dotty(source)
            try:
                # get value to update
                dict_to_update = dotty_source[path]

                if isinstance(dict_to_update, dict):
                    # update
                    dict_to_update.update(value)
                else:
                    self.console.warning(f"Path {path} has value {dict_to_update}. It was replaced with value {value}")
                    dict_to_update = value

                # assign
                dotty_source[path] = dict_to_update
            except KeyError:
                dotty_source[path] = value

            return dotty_source.to_dict()

        else:
            source.update(value)
            return source

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.profile is not None:

            self.profile.traits = self._update(self.profile.traits, self.event.properties)
            self.update_profile()

            return Result(port="traits", value=self.profile.traits)

        return Result(port="error", value={})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=AutoMergePropertiesToProfileAction.__name__,
            inputs=["payload"],
            outputs=["traits", "error"],
            init={
                "sub_traits": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Define how to update traits",
                    fields=[
                        FormField(
                            id="sub_traits",
                            name="Sub traits path",
                            description="Leave it empty if you want to merge data to the root of your profile traits."
                                        "Type sub-path only if you want to create or merge a part of the profile "
                                        "traits. This path will be appended to the main traits path. "
                                        "e.g: profile@traits[sub.path]",
                            component=FormComponent(type="text", props={"label": "Sub path"})
                        )
                    ]
                ),
            ]),
            version='0.8.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='merge_event_properties'

        ),
        metadata=MetaData(
            name='Merge event properties',
            desc='Automatically merges all event properties to profile traits.',
            icon='merge',
            group=["Data processing"],
            tags=['traits', 'profile'],
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
