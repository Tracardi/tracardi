from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.elastic.interface.collector.load.session import load_nth_last_session_for_profile
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class PreviousSessionAction(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.event.metadata.profile_less is False:

            if self.config.offset < 0:
                offset = (-1 * self.config.offset)
            else:
                offset = self.config.offset

            result = await load_nth_last_session_for_profile(
                profile_id=self.profile.id,
                offset= offset - 1
            )
            if result is not None:
                return Result(port="found", value=result)
        else:
            self.console.warning("Can not find last session for profile less event.")

        return Result(port="not_found", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=PreviousSessionAction.__name__,
            inputs=["payload"],
            outputs=["found", "not_found"],
            version='0.6.2',
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "offset": -1
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Session configuration",
                        fields=[
                            FormField(
                                id="offset",
                                name="Session offset",
                                description="Enter the session you want to get on the plugin exit. For example, "
                                            "-1 will return last session, and -2 will return 2nd last session.",
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
            desc='Loads previous sessions for current profile, according to config, and injects it into '
                 'payload.',
            icon='previous',
            group=["Sessions"],
            tags=['last', 'previous'],
            purpose=['collection', 'segmentation'],
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
