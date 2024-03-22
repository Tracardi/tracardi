from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.elastic.interface.event import load_nth_last_event
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class PreviousEventGetter(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        event_type = self.event.type if self.config.event_type.id == "@current" else self.config.event_type.id

        if self.event.metadata.profile_less is False:
            result = await load_nth_last_event(
                profile_id=self.profile.id,
                event_type=event_type,
                offset=(-1) * self.config.offset
            )

            if result is None:
                return Result(port="not_found", value=payload)
            return Result(port="found", value=result)

        else:
            result = await load_nth_last_event(
                event_type=event_type,
                offset=(-1) * self.config.offset
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
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "event_type": {"id": "@current", "name": "@current"},
                "offset": -1
            },
            manual="get_prev_event_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Event configuration",
                        fields=[
                            FormField(
                                name="Event type",
                                id="event_type",
                                description="Please provide event type that you want to load into payload. If you want "
                                            "current but previous event, insert @current.",
                                component=FormComponent(type="eventType", props={"label": "Event type", "props": {
                                    "defaultValueSet": [{"id": "@current",
                                                         "name": "@current"}],
                                    "onlyValueWithOptions": False
                                }})
                            ),
                            FormField(
                                name="Offset",
                                id="offset",
                                description="Please provide an integer between -10 and 0 inclusively. This integer "
                                            "is the number of the event, counting from the present one. For "
                                            "example, 0 is current event, -1 is previous one, etc. ",
                                component=FormComponent(type="text", props={"label": "Offset"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Get previous event',
            desc='Injects the previous event for current profile into payload, according to the event type '
                 'and offset value.',
            icon='previous',
            tags=['previous', 'last'],
            group=["Events"],
            purpose=['collection', 'segmentation'],
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
