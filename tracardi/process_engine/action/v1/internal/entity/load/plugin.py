from tracardi.service.plugin.domain.result import Result
from .model.config import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage


def validate(config: dict):
    return Configuration(**config)


class EntityLoadAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict, in_edge=None):

        if self.profile is None:
            self.console.warning("This is profile-less event. Entity will be loaded without the profile reference.")

        result = await storage.driver.entity.load_by_id(self.config.id)
        return Result(port="result", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EntityLoadAction',
            inputs=["payload"],
            outputs=["result"],
            version='0.7.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "id": None,
                "type": ""
            }
        ),
        metadata=MetaData(
            name='Load entity',
            desc='Loads entity by its id.',
            icon='entity',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload.")
                }
            )
        )
    )
