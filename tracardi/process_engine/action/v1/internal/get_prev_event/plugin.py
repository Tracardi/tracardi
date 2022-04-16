from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class PreviousEventGetter(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        if self.event.metadata.profile_less is False:
            result = await storage.driver.event.get_nth_last_event(
                profile_id=self.profile.id,
                event_type=self.config.event_type,
                n=(-1) * self.config.offset
            )

            if result is None:
                return Result(port="not_found", value=payload)
            return Result(port="found", value=result)

        else:
            result = await storage.driver.event.get_nth_last_event(
                event_type=self.config.event_type,
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
            className='PreviousEventGetter',
            inputs=["payload"],
            outputs=["found", "not_found"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            init={
                "event_type": None,
                "offset": -1
            },
            manual="get_prev_event_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                name="Event type",
                                id="event_type",
                                description="Please provide event type that you want to load into payload.",
                                component=FormComponent(type="text", props={"label": "Event type"})
                            ),
                            FormField(
                                name="Offset",
                                id="offset",
                                description="Please provide an integer between -10 and 0 inclusively. This integer "
                                            "represents the number of the event, counting from the present one. For "
                                            "example, 0 is current event, -1 is previous one, and -2 is one before the "
                                            "last one.",
                                component=FormComponent(type="text", props={"label": "Offset"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Get previous event',
            desc='Injects one of the previous events for current profile into payload, according to given event type '
                 'and offset value.',
            icon='plugin',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "found": PortDoc(desc="This port returns event data if the event was found."),
                    "not_found": PortDoc(desc="This port returns event data if the event was not found.")
                }
            )
        )
    )
