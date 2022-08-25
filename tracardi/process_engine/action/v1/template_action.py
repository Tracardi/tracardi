from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    template: str


def validate(config: dict):
    return Configuration(**config)


class TemplateAction(ActionRunner):

    dot_template: DotTemplate
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)
        self.dot_template = DotTemplate()

    async def run(self, payload: dict, in_edge=None) -> Result:
        accessor = self._get_dot_accessor(payload)
        return Result(port="template", value={
            "template": self.dot_template.render(self.config.template, accessor)
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.template_action',
            className='TemplateAction',
            inputs=["payload"],
            outputs=['template'],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk, Risto Kowaczewski",
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
                            description="Provide template with placeholders. Placeholders start with {{ and end "
                                        "with }}. Data is referenced with dot notation. Example: {{profile@pii.name}}",
                            component=FormComponent(type="textarea", props={"label": "template"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Template',
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
