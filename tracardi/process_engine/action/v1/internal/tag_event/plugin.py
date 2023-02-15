from pydantic import BaseModel

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(BaseModel):
    tags: str


def validate(config: dict) -> Config:
    return Config(**config)


class TagEventAction(ActionRunner):
    config: Config

    async def set_up(self, init):
        config = validate(init)
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:

        tags = [tag.strip() for tag in self.config.tags.split()]
        self.event.tags.add(tags)
        self.event.operation.update = True

        return Result(port='payload', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=TagEventAction.__name__,
            inputs=["payload"],
            outputs=['payload'],
            version='0.8.0',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "tags": ""
            },
            form=None,

        ),
        metadata=MetaData(
            name='Tag event',
            desc='Ads tag to current event.',
            icon='tag',
            keywords=['new', 'event', 'add'],
            group=["Operations"],
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
