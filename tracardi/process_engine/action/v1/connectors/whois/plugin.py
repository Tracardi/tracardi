from pydantic import validator

from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
import whois


def validate(config):
    return Configuration(**config)


class Configuration(PluginConfig):
    domain: str

    @validator("domain")
    def must_not_be_emty(cls, value):
        if value.strip() == "":
            raise ValueError("Domain must not be empty.")
        return value


class WhoisAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        try:
            result = whois.whois(self.config.domain)
            result['exists'] = bool(result.domain_name)
            return Result(value=result, port="result")
        except Exception as e:
            return Result(value={"message": str(e)}, port="error")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=WhoisAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.7.3',
            init={
                "domain": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Whois domain configuration",
                    fields=[
                        FormField(
                            id="domain",
                            name="Domain",
                            description="Type or reference domain to check in whois service.",
                            component=FormComponent(type="dotPath", props={
                                "label": "Domain",
                                "defaultSourceValue": "payload"
                            })
                        )
                    ])
            ]),
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Whois',
            desc='Checks domain in whois service.',
            icon='globe',
            group=["Connectors"],
            purpose=['collection'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns response form whois service."),
                    "error": PortDoc(desc="Returns error message if plugin fails.")
                }
            )
        )
    )
