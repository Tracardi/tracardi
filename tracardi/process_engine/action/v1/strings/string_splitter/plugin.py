from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SplitterAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        string = dot[self.config.string]
        result = [item.strip() for item in string.split(self.config.delimiter)]
        return Result(port="payload", value={"result": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.string_splitter.plugin',
            className='SplitterAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT + CC",
            author="Bartosz Dobrosielski",
            manual="string_splitter_action",
            init={
                "string": None,
                "delimiter": '.',
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="string",
                            name="String to split",
                            description="Type path to string or string itself. Default source is event. Change it if"
                                        " the data is elsewhere.",
                            component=FormComponent(type="dotPath", props={"defaultSourceValue": "event"})
                        ),
                        FormField(
                            id="delimiter",
                            name="Delimiter",
                            description="Type delimiter. It will be used to split the string into list of strings.",
                            component=FormComponent(type="text", props={"label": "delimiter"})
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='String splitter',
            desc='It splits string into list of strings by defined delimiter.',
            icon='splitter',
            group=["String"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns array with separated values.")
                }
            ),
        )
    )
