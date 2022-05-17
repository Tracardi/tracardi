from tracardi.domain.profile import Profile

from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class InjectProfile(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        result = await storage.driver.raw.index("profile").query_by_sql(self.config.query, start=0, limit=2)

        if result['total'] != 1:
            self.console.error("The profile query returned {} profiles. "
                               "Do not know which one to inject.".format(result['total']))
            return Result(port="error", value=payload)

        profile = Profile(**result['result'][0])

        self.event.profile = profile
        self.event.metadata.profile_less = False
        self.event.update = True
        self.execution_graph.set_profiles(profile)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InjectProfile',
            inputs=['payload'],
            outputs=['payload', 'error'],
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "query": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Select profile",
                    fields=[
                        FormField(
                            id="query",
                            name="Profile query",
                            description="Type the query that the profile must meet. It must return single profile "
                                        "otherwise the profile will not be injected. "
                                        "For example: pii.email EXISTS AND pii.email=\"john@email.com\"",
                            component=FormComponent(type="text", props={"label": "Condition"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Load profile',
            desc='Loads and injects profile into workflow and assigns it to current event.',
            icon='profile',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns input payload."),
                    "error": PortDoc(desc="Returns error.")
                }
            )
        )
    )
