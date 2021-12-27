from tracardi.domain.profile import Profile

from tracardi.service.storage.driver import storage
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result

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

        self.execution_graph.set_profiles(profile)

        return Result(port="profile", value=result['result'][0])


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InjectProfile',
            inputs=['payload'],
            outputs=['profile', 'error'],
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
            name='Inject profile into workflow',
            desc='This node will inject profile into workflow',
            icon='profile',
            group=["Input/Output"]
        )
    )
