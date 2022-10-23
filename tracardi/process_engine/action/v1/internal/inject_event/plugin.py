from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class InjectEvent(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        event = await storage.driver.event.load(self.config.event_id)
        if event is None:
            self.console.warning("Event id `{}` does not exist.".format(self.config.event_id))
        return Result(port="payload", value=event)


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=True,
        spec=Spec(
            module=__name__,
            className='InjectEvent',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "event_id": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Event id",
                    fields=[
                        FormField(
                            id="event_id",
                            name="Event id",
                            description="Type event id you would like to add to payload.",
                            component=FormComponent(type="text", props={"label": "Event id"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Inject event into payload',
            desc='This node will inject event of given id into payload',
            icon='json',
            keywords=['load'],
            group=["Events"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns input payload.")
                }
            )
        )
    )
