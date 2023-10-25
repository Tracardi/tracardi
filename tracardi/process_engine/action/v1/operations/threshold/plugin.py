from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent, NodeEvents
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration
from tracardi.service.value_threshold_manager import ValueThresholdManager


def validate(config: dict):
    return Configuration(**config)


class ValueThresholdAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.event.metadata.profile_less is True and self.profile is None:
            self.console.warning(f"Could not assign value {self.config.value} to profile. The {self.event.type} "
                                 "event is profile-less. There is no profile within this event.")

        profile_id = self.profile.id if self.profile is not None else None
        vtm = ValueThresholdManager(node_id=self.node.id,
                                    debug=self.debug,
                                    profile_id=profile_id,
                                    name=self.config.name,
                                    ttl=self.config.ttl)

        dot = self._get_dot_accessor(payload)
        current_value = dot[self.config.value]
        if await vtm.pass_threshold(current_value):
            return Result(port="pass", value=payload)
        return Result(port="stop", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ValueThresholdAction',
            inputs=["payload"],
            outputs=["pass", "stop"],
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "name": None,
                "value": None,
                "ttl": 30 * 60,
                "assign_to_profile": True
            },
            node=NodeEvents(
                on_remove="path-to-endpoint"
            ),
            form=Form(groups=[
                FormGroup(
                    name="Value change threshold",
                    fields=[
                        FormField(
                            id="name",
                            name="Value name",
                            description="Type value name to identify it.",
                            component=FormComponent(type="text", props={"label": "name"})
                        ),
                        FormField(
                            id="value",
                            name="Value",
                            description="Type value or path to value that is to be monitored.",
                            component=FormComponent(type="dotPath", props={"label": "value"})
                        ),
                        FormField(
                            id="ttl",
                            name="Value time to live",
                            description="Type value time to live. After this time value will be considered invalid and "
                                        "will be changed. The plugin will trigger the pass output port.",
                            component=FormComponent(type="text", props={"label": "Time to live"})
                        ),
                        FormField(
                            id="assign_to_profile",
                            name="Value connected with profile",
                            description="Keep value assigned to profile. Most of the "
                                        "time you want this. The value should be assigned to a profile "
                                        "to keep it aligned with the customers actions. In rare cases when there are "
                                        "profile-less events value can not be assigned to profile.",
                            component=FormComponent(type="bool", props={"label": "Assign value to profile"})
                        ),
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Value change',
            desc='This plugin will stop the workflow if the defined value did not change,',
            icon='threshold',
            group=["Flow control"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "pass": PortDoc(desc="This port returns input payload if value changed."),
                    "stop": PortDoc(desc="This port returns input payload if value did NOT change.")
                }
            )
        )
    )
