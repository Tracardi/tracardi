from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result
from tracardi_dot_notation.dot_template import DotTemplate
from pydantic import BaseModel


class Configuration(BaseModel):
    template: str


def validate(config: dict):
    return Configuration(**config)


class TemplateAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)
        self.dot_template = DotTemplate()

    async def run(self, payload):
        accessor = self._get_dot_accessor(payload)
        return Result(port="payload", value=self.dot_template.render(self.config.template, accessor))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.template_action',
            className='TemplateAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            manual="template_action",
            init={
                "template": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Payload to template",
                    fields=[
                        FormField(
                            id="template",
                            name="Template",
                            description="Provide template with placeholders.",
                            component=FormComponent(type="textarea", props={"label": "template"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Template data',
            desc='Returns a string where placeholders are replaced with given values.',
            icon='template',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns a string with placeholders replaced by values given in "
                                            "payload.")
                }
            )
        )
    )
