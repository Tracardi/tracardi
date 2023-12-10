from tracardi.service.utils.date import now_in_utc

from tracardi.domain.profile import Profile
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration
from tracardi.process_engine.tql.condition import Condition


def validate(config: dict):
    return Configuration(**config)


class ProfileSegmentAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    def _update(self, profile: Profile, segment, action):
        action = action.lower()
        if action == 'add':
            if segment not in profile.segments:
                profile.segments.append(segment)
        elif action == 'remove':
            if segment in profile.segments:
                profile.segments = list(set(profile.segments))
                profile.segments.remove(segment)
        profile.metadata.time.segmentation = now_in_utc()
        self.profile.replace(profile)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.event.metadata.profile_less is False:
            dot = self._get_dot_accessor(payload)
            condition = Condition()
            profile = Profile(**dot.profile)
            try:
                if await condition.evaluate(self.config.condition, dot):
                    self._update(profile, self.config.true_segment, self.config.true_action)
                    return Result(port="true", value=payload)
                else:
                    self._update(profile, self.config.false_segment, self.config.false_action)
                    return Result(port="false", value=payload)
            except Exception as e:
                self.console.error(str(e))
                return Result(port="error", value=payload)

        self.console.warning("Can not segment profile-less event. There is no profile.")
        return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ProfileSegmentAction',
            inputs=["payload"],
            outputs=['true', "false", "error"],
            version='0.6.0.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="segmentation/profile_segment",
            init={
                "condition": "",
                "true_segment": "",
                "true_action": "add",
                "false_segment": "",
                "false_action": "remove",
            },
            form=Form(groups=[
                FormGroup(
                    name="Segment logic",
                    description="Set the conditions for profile segmentation.",
                    fields=[
                        FormField(
                            id="condition",
                            name="Condition statement",
                            description="Provide condition for segmentation. If the condition is met then the profile "
                                        "will be segmented to defined segment, if NOT then the other action can be "
                                        "performed.",
                            component=FormComponent(type="textarea", props={"label": "condition"})
                        )
                    ]
                ),
                FormGroup(
                    name="Segment when condition is met (Positive path)",
                    description="This will be triggered when the segmentation condition IS met.",
                    fields=[
                        FormField(
                            id="true_action",
                            name="What would you like to do",
                            description="Please select either to ADD, REMOVE, or do NOTHING.",
                            component=FormComponent(type="select", props={"label": "action", "items": {
                                "add": "Add segment",
                                "remove": "Remove segment",
                                "none": "Do nothing"
                            }})
                        ),
                        FormField(
                            id="true_segment",
                            name="Segment name",
                            description="Provide segment name. This name will be used to mark a profile. "
                                        "Please use dashes instead of spaces.",
                            component=FormComponent(type="text", props={"label": "segment"})
                        )
                    ]
                ),
                FormGroup(
                    name="Segment when condition is NOT met  (Negative path)",
                    description="This will be triggered when the segmentation condition IS NOT met.",
                    fields=[
                        FormField(
                            id="false_action",
                            name="What would you like to do",
                            description="Please select either to ADD, REMOVE, or do NOTHING.",
                            component=FormComponent(type="select", props={"label": "action", "items": {
                                "add": "Add segment",
                                "remove": "Remove segment",
                                "none": "Do nothing"
                            }})
                        ),
                        FormField(
                            id="false_segment",
                            name="Segment name",
                            description="Provide segment name. This name will be used to mark a profile. "
                                        "Please use dashes instead of spaces.",
                            component=FormComponent(type="text", props={"label": "segment"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Conditional segmentation',
            desc='This plugin will add/remove segment from the profile.',
            icon='segment',
            group=["Segmentation"],
            tags=['condition'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "true": PortDoc(desc="Returns input payload when segmentation was triggered."),
                    "false": PortDoc(desc="Returns input payload when segmentation was not triggered."),
                    "error": PortDoc(desc="Returns input payload when there was an error in segmentation."),
                }
            )
        )
    )
