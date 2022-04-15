from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class FindPreviousSessionAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        result = await storage.driver.session.get_nth_last_session(
            profile_id=self.profile.id,
            n=(-1) * self.config.offset
        )
        if result is None:
            return Result(port="not_found", value=payload)
        return Result(port="found", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='FindPreviousSessionAction',
            inputs=["payload"],
            outputs=["found", "not_found"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "offset": -1
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="offset",
                                name="Offset",
                                description="Please provide an integer between -10 and 0, representing the "
                                            "number of the previous session, counting from present one. For example, "
                                            "-1 will return last session, and -2 will return the session before the "
                                            "last one.",
                                component=FormComponent(type="text", props={"label": "Offset"})
                            )
                        ]
                    )
                ]
            ),
            manual="get_prev_session_action"
        ),
        metadata=MetaData(
            name='Get previous session',
            desc='Fetches one of previous sessions for current profile, according to config, and injects it into '
                 'payload.',
            icon='plugin',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "found": PortDoc(desc="This port returns session info if the session was found."),
                    "not_found": PortDoc(desc="This port returns given payload if the session was not found.")
                }
            )
        )
    )
