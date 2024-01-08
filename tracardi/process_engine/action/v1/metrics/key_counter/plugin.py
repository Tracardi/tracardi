from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.domain.profile import Profile

from .model.configuration import Configuration
from .service.key_counter import KeyCounter


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class KeyCounterAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)

        # If path does not exist then create empty value
        if self.config.save_in not in dot:
            dot[self.config.save_in] = {}

        counter_dict = dot[self.config.save_in]

        if counter_dict is None:
            counter_dict = {}
        else:
            if not isinstance(counter_dict, dict):
                raise ValueError(f"Path [{self.config.save_in}] for key counting must be dict, "
                                 f"{type(counter_dict)} given.")

        if isinstance(self.config.key, list):
            keys_to_count = [dot[key] for key in self.config.key]
        else:
            keys_to_count = dot[self.config.key]

        # Save counts
        counter = KeyCounter(counter_dict)
        counter.count(keys_to_count)

        dot[self.config.save_in] = counter.counts

        if isinstance(self.profile, Profile):
            self.profile.replace(Profile(**dot.profile))

        return Result(port='payload', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.metrics.key_counter.plugin',
            className='KeyCounterAction',
            inputs=['payload'],
            outputs=['payload'],
            version="0.6.0.1",
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="key_counter_action",
            init={
                "key": None,
                "save_in": None
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="key",
                            name="Key",
                            description="Type path to KEY or KEY itself. Default source is event. Change it if"
                                        " the key is elsewhere.",
                            component=FormComponent(type="dotPath", props={"defaultSourceValue": "event"})
                        ),
                        FormField(
                            id="save_in",
                            name="Place to save",
                            description="Type path to profile.",
                            component=FormComponent(type="forceDotPath", props={"defaultSourceValue": "profile"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Key counter',
            desc='Counts keys and saves it in profile.',
            type='flowNode',
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                }
            ),
            icon='bar-chart',
            group=['Stats']
        )
    )
