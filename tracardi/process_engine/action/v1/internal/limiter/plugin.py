from hashlib import sha1
from typing import Optional

from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.throttle import Limiter

from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class LimiterAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Optional[Result]:
        dot = self._get_dot_accessor(payload)
        converter = DictTraverser(dot)
        keys = [sha1(key.encode('utf-8')).hexdigest()[0:12] for key in converter.reshape(self.config.keys)]

        key = ":".join(keys)

        throttle = Limiter(self.config.limit, self.config.ttl)

        result, ttl = throttle.limit(key)

        if result:
            return Result(port="pass", value=payload)
        return Result(port="block", value=payload)


def register() -> Plugin:
    return Plugin(
        spec=Spec(
            module=__name__,
            className=LimiterAction.__name__,
            inputs=["payload"],
            outputs=['pass', 'block'],
            version='0.7.3',
            license="MIT",
            author="Risto Kowaczewski",
            manual="limiter_action",
            init={
              "keys": [],
              "limit": 1,
              "ttl": 60
            },
            form=Form(groups=[
                FormGroup(
                    name="Event id",
                    fields=[
                        FormField(
                            id="limit",
                            name="Number of allowed executions",
                            description="Type the number of allowed passes through this plugin within defined time.",
                            component=FormComponent(type="text", props={"label": "Limit"})
                        ),
                        FormField(
                            id="ttl",
                            name="Time range (Time to live)",
                            description="Type the time period (in seconds) that must pass for the limit to be reset "
                                        "to 0.",
                            component=FormComponent(type="text", props={"label": "Limit"})
                        ),
                        FormField(
                            id="keys",
                            name="Throttle key identifier",
                            description="Select the throttle identifiers. This is will define what resource is "
                                        "protected by this limiter. See the documentation for more information. ",
                            component=FormComponent(type="listOfDotPaths", props={"label": "Limit keys",
                                                                                  "defaultSourceValue": "profile"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Limiter',
            desc='This node throttles the workflow execution.',
            icon='hand-stop',
            keywords=['rate', 'limiter', 'throttle'],
            group=["Flow control"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "pass": PortDoc(desc="Returns input payload if execution not throttled."),
                    "block": PortDoc(desc="Returns input payload if execution throttled.")
                }
            )
        )
    )
